"""External Windows crash capture for launcher-owned Civ4 processes only."""
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time


class ExceptionRecord(ctypes.Structure):
    pass


ExceptionRecord._fields_ = [
    ('code', w.DWORD), ('flags', w.DWORD),
    ('nested', ctypes.POINTER(ExceptionRecord)), ('address', ctypes.c_void_p),
    ('count', w.DWORD), ('parameters', ctypes.c_size_t * 15)]


class ExceptionInfo(ctypes.Structure):
    _fields_ = [('record', ExceptionRecord), ('first_chance', w.DWORD)]


class EventData(ctypes.Union):
    # EXCEPTION_DEBUG_INFO is the largest DEBUG_EVENT union member.
    _fields_ = [('exception', ExceptionInfo), ('file', w.HANDLE)]


class DebugEvent(ctypes.Structure):
    _fields_ = [('kind', w.DWORD), ('pid', w.DWORD), ('tid', w.DWORD),
                ('data', EventData)]




def native_dump_writer():
    return Path(__file__).resolve().parent / 'bin' / 'observer_dump32.exe'


def capture_hang(run, pid, name):
    """Use an x86 writer so WOW64 dumps contain Civ4's actual thread stacks."""
    details = {'pid': pid, 'kind': 'stall', 'time': time.time(), 'writer_architecture': 'x86'}
    try:
        result = subprocess.run([str(native_dump_writer()), str(pid), str(run / (name + '.dmp'))],
                                timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise ctypes.WinError(result.returncode)
        details['dump'] = name + '.dmp'
        print('Stall snapshot saved: ' + str(run / (name + '.dmp')), flush=True)
    except (OSError, subprocess.TimeoutExpired) as error:
        details['dump_error'] = str(error)
        print('Could not capture stalled game: ' + str(error), flush=True)
    (run / (name + '.json')).write_text(json.dumps(details, indent=2), encoding='utf-8')


def collect_windows_dump(run, pid, executable, timeout=120):
    """WER may finish writing after process exit; preserve its per-PID fallback."""
    source = Path(os.environ['LOCALAPPDATA']) / 'CrashDumps' / ('%s.%d.dmp' % (executable.name, pid))
    print('Waiting for Windows crash evidence for PID %d (up to %d seconds).' % (pid, timeout), flush=True)
    deadline = time.monotonic() + timeout
    launched_at = (run / 'launch.json').stat().st_mtime
    last_size = None
    while time.monotonic() < deadline:
        try:
            info = source.stat()
            size = info.st_size if info.st_mtime >= launched_at else 0
            if size and size == last_size:
                destination = run / 'crash-windows.dmp'
                shutil.copy2(source, destination)
                details = {'pid': pid, 'source': str(source), 'dump': destination.name}
                (run / 'crash-windows.json').write_text(json.dumps(details, indent=2), encoding='utf-8')
                print('Windows crash dump saved: ' + str(destination), flush=True)
                return
            last_size = size
        except OSError:
            last_size = None
        time.sleep(2)
    (run / 'crash-windows.json').write_text(json.dumps({
        'pid': pid, 'expected_source': str(source),
        'dump_error': 'No readable Windows dump arrived within %d seconds' % timeout}, indent=2), encoding='utf-8')


class CrashCapture:
    def __init__(self, run):
        self.run = run
        self.initial_breakpoints = set()
        self.captured = set()
        self.exited = False
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.WaitForDebugEvent.argtypes = [ctypes.POINTER(DebugEvent), w.DWORD]
        self.kernel.WaitForDebugEvent.restype = w.BOOL
        self.kernel.ContinueDebugEvent.argtypes = [w.DWORD, w.DWORD, w.DWORD]
        self.kernel.ContinueDebugEvent.restype = w.BOOL
        self.kernel.DebugActiveProcess.argtypes = [w.DWORD]
        self.kernel.DebugActiveProcess.restype = w.BOOL
        self.kernel.CloseHandle.argtypes = [w.HANDLE]
        self.kernel.CloseHandle.restype = w.BOOL
        self.kernel.GetFinalPathNameByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
        self.kernel.GetFinalPathNameByHandleW.restype = w.DWORD
        self.modules = {}
        self.module_sizes = {}
        self.process_handle = None
        self.event_counts = {}

    def attach(self, pid):
        # Civ4's Steam startup path can exit before setup when created with
        # DEBUG_ONLY_THIS_PROCESS. Attach only after authenticated GameStart.
        if not self.kernel.DebugActiveProcess(pid):
            raise ctypes.WinError(ctypes.get_last_error())

    def _module(self, event):
        # Both CREATE_PROCESS_DEBUG_INFO and LOAD_DLL_DEBUG_INFO start with hFile.
        handle = event.data.file
        if not handle:
            return
        try:
            path = ctypes.create_unicode_buffer(32768)
            if self.kernel.GetFinalPathNameByHandleW(handle, path, len(path), 0):
                # Image base follows three handles in CREATE_PROCESS, one in LOAD_DLL.
                offset = ctypes.sizeof(w.HANDLE) * (3 if event.kind == 3 else 1)
                base = ctypes.c_void_p.from_address(ctypes.addressof(event.data) + offset).value
                self.modules[base] = path.value
                try:
                    with open(path.value, 'rb') as image:
                        image.seek(0x3C)
                        pe_offset = struct.unpack('<I', image.read(4))[0]
                        # SizeOfImage has the same offset in PE32 and PE32+.
                        image.seek(pe_offset + 24 + 56)
                        self.module_sizes[base] = struct.unpack('<I', image.read(4))[0]
                except (OSError, struct.error):
                    pass
        finally:
            self.kernel.CloseHandle(handle)

    def _capture(self, event):
        info = event.data.exception
        record = info.record
        address = record.address or 0
        key = (record.code, address)
        if key in self.captured and info.first_chance:
            return
        self.captured.add(key)
        chance = 'first' if info.first_chance else 'unhandled'
        stem = 'crash-%s-%08X-%X' % (chance, record.code, address)
        details = {'pid': event.pid, 'thread_id': event.tid,
                   'exception_code': '0x%08X' % record.code,
                   'exception_address': '0x%X' % address,
                   'first_chance': bool(info.first_chance),
                   'parameters': list(record.parameters[:min(record.count, 15)]),
                   'modules': {hex(base): path for base, path in self.modules.items()},
                   'last_heartbeat': None}
        candidates = [base for base, size in self.module_sizes.items()
                      if base <= address < base + size]
        if candidates:
            base = max(candidates)
            details.update(module=self.modules[base], module_offset=hex(address - base))
        try:
            details['last_heartbeat'] = json.loads((self.run / 'heartbeat.json').read_text())
        except (OSError, ValueError):
            pass
        details['writer_architecture'] = 'x86'
        try:
            result = subprocess.run([str(native_dump_writer()), str(event.pid), str(self.run / (stem + '.dmp'))],
                                    timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:
                raise ctypes.WinError(result.returncode)
            details['dump'] = stem + '.dmp'
        except (OSError, subprocess.TimeoutExpired) as error:
            details['dump_error'] = str(error)
        (self.run / (stem + '.json')).write_text(json.dumps(details, indent=2), encoding='utf-8')
        print('Crash evidence: ' + str(self.run / (stem + '.json')), flush=True)

    def pump(self, timeout=0):
        """Call only on the thread which attached to the launcher-owned child."""
        event = DebugEvent()
        deadline = time.monotonic() + 0.05
        while not self.exited:
            if not self.kernel.WaitForDebugEvent(ctypes.byref(event), timeout):
                error = ctypes.get_last_error()
                if error in (0, 121):  # no event before timeout
                    return
                raise ctypes.WinError(error)
            timeout = 0
            self.event_counts[event.kind] = self.event_counts.get(event.kind, 0) + 1
            if event.kind in (1, 3, 5):
                details = {'kind': event.kind, 'pid': event.pid, 'thread_id': event.tid}
                if event.kind == 1:
                    details.update(code=hex(event.data.exception.record.code),
                                   address=hex(event.data.exception.record.address or 0),
                                   first_chance=bool(event.data.exception.first_chance))
                try:
                    with (self.run / 'debug-events.jsonl').open('a', encoding='utf-8') as log:
                        log.write(json.dumps(details) + '\n')
                except OSError as error:
                    print('Could not save debug event: ' + str(error), flush=True)
            disposition = 0x00010002  # DBG_CONTINUE
            try:
                if event.kind == 3:  # CREATE_PROCESS_DEBUG_EVENT
                    offset = ctypes.sizeof(w.HANDLE)
                    self.process_handle = ctypes.c_void_p.from_address(
                        ctypes.addressof(event.data) + offset).value
                if event.kind in (3, 6):
                    self._module(event)
                elif event.kind == 7:  # UNLOAD_DLL_DEBUG_EVENT
                    self.modules.pop(event.data.file, None)
                    self.module_sizes.pop(event.data.file, None)
                elif event.kind == 5:  # EXIT_PROCESS_DEBUG_EVENT
                    self.exited = True
                elif event.kind == 1:  # EXCEPTION_DEBUG_EVENT
                    info = event.data.exception
                    # Consume only the debugger's initial loader breakpoint.
                    if (info.first_chance and info.record.code in (0x80000003, 0x4000001F)
                            and info.record.code not in self.initial_breakpoints):
                        self.initial_breakpoints.add(info.record.code)
                    else:
                        disposition = 0x80010001  # DBG_EXCEPTION_NOT_HANDLED
                        # Capture serious faults before Civ4's handler can swallow them,
                        # plus every unhandled exception. Handled language exceptions pass through.
                        if not info.first_chance or info.record.code in (0xC0000005, 0xC000001D, 0xC00000FD, 0xC0000374, 0xC0000409):
                            try:
                                self._capture(event)
                            except OSError as error:
                                print('Could not save crash evidence: ' + str(error), flush=True)
            finally:
                if not self.kernel.ContinueDebugEvent(event.pid, event.tid, disposition):
                    raise ctypes.WinError(ctypes.get_last_error())
            if time.monotonic() >= deadline:
                return
