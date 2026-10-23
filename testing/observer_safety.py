"""Independent emergency stop for exactly one launcher-owned Windows job."""
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time


class BasicLimits(ctypes.Structure):
    _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong),
                ('flags', w.DWORD), ('min_working_set', ctypes.c_size_t),
                ('max_working_set', ctypes.c_size_t), ('active_limit', w.DWORD),
                ('affinity', ctypes.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [('basic', BasicLimits), ('io_counters', ctypes.c_ulonglong * 6),
                ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]


def kernel_api():
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CreateJobObjectW': ([ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
        'OpenJobObjectW': ([w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        'SetInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
        'QueryInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p], w.BOOL),
        'AssignProcessToJobObject': ([w.HANDLE, w.HANDLE], w.BOOL),
        'TerminateJobObject': ([w.HANDLE, w.UINT], w.BOOL),
        'OpenProcess': ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
        'WaitForSingleObject': ([w.HANDLE, w.DWORD], w.DWORD),
        'TerminateProcess': ([w.HANDLE, w.UINT], w.BOOL),
        'CloseHandle': ([w.HANDLE], w.BOOL),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result
    return kernel


class BatchSafety:
    def __init__(self, batch):
        self.batch = batch
        self.kernel = kernel_api()
        self.name = 'Local\\AwakenedRFC-' + secrets.token_hex(24)
        self.job = self.kernel.CreateJobObjectW(None, self.name)
        if not self.job:
            raise ctypes.WinError(ctypes.get_last_error())
        self.helper = None
        try:
            limits = ExtendedLimits()
            limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.kernel.SetInformationJobObject(self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                raise ctypes.WinError(ctypes.get_last_error())
            self.helper = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), str(batch), str(os.getpid()), self.name],
                creationflags=subprocess.CREATE_NO_WINDOW)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                ready = batch / 'emergency-stop-ready.json'
                if ready.exists():
                    state = json.loads(ready.read_text(encoding='utf-8'))
                    if state.get('error'):
                        raise RuntimeError('Emergency stop unavailable: ' + state['error'])
                    return
                if self.helper.poll() is not None:
                    raise RuntimeError('Emergency stop helper exited before initialization')
                time.sleep(0.05)
            raise RuntimeError('Emergency stop helper did not initialize')
        except BaseException:
            self.close()
            raise

    def assign(self, process):
        if self.helper.poll() is not None:
            raise RuntimeError('Emergency stop helper is no longer running')
        # Popen retains the actual child process handle, avoiding PID reuse.
        if not self.kernel.AssignProcessToJobObject(self.job, int(process._handle)):
            error = ctypes.WinError(ctypes.get_last_error())
            process.terminate()
            raise error

    def arm_cleanup_timeout(self):
        # Diagnostic APIs themselves can block. The independent helper imposes
        # a hard bound once a stalled batch is already destined to stop.
        (self.batch / 'emergency-stop-deadline.json').write_text(
            json.dumps({'deadline': time.time() + 15}), encoding='utf-8')

    def close(self):
        if self.job:
            self.kernel.TerminateJobObject(self.job, 1)
            self.kernel.CloseHandle(self.job)
            self.job = None
        if self.helper is not None:
            (self.batch / 'emergency-stop-finished').touch()
            try:
                self.helper.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.helper.terminate()


def emergency_snapshot(batch, job, kernel, user):
    class JobPids(ctypes.Structure):
        _fields_ = [('assigned', w.DWORD), ('count', w.DWORD), ('pids', ctypes.c_size_t * 4096)]

    members = JobPids()
    if not kernel.QueryInformationJobObject(job, 3, ctypes.byref(members), ctypes.sizeof(members), None):
        raise ctypes.WinError(ctypes.get_last_error())
    pids = set(members.pids[:min(members.count, 4096)])
    callback_type = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    user.EnumWindows.argtypes = [callback_type, w.LPARAM]
    user.EnumWindows.restype = w.BOOL
    user.GetWindowThreadProcessId.argtypes = [w.HWND, ctypes.POINTER(w.DWORD)]
    user.GetWindowThreadProcessId.restype = w.DWORD
    user.ShowWindowAsync.argtypes = [w.HWND, ctypes.c_int]
    user.ShowWindowAsync.restype = w.BOOL

    @callback_type
    def minimize(hwnd, unused):
        pid = w.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids:
            user.ShowWindowAsync(hwnd, 11)  # SW_FORCEMINIMIZE works for hung windows
        return True

    candidates = []
    for started in batch.glob('game*/started.json'):
        try:
            pid = json.loads(started.read_text(encoding='utf-8'))['pid']
            heartbeat = started.parent / 'heartbeat.json'
            if pid in pids:
                candidates.append((heartbeat.stat().st_mtime, started.parent, pid))
        except (OSError, ValueError, KeyError):
            pass
    if not candidates:
        user.EnumWindows(minimize, 0)
        return
    _, run, pid = min(candidates)
    from observer_crashes import native_dump_writer
    details = {'pid': pid, 'kind': 'stall', 'time': time.time(), 'writer_architecture': 'x86'}
    try:
        # Capture before minimization changes the game's rendering/thread state.
        # Run the native writer directly so the three-second bound kills the
        # writer itself, rather than leaving a grandchild dump process behind.
        writer = subprocess.Popen([str(native_dump_writer()), str(pid), str(run / 'hang-emergency.dmp')],
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            code = writer.wait(timeout=3)
            if code:
                raise ctypes.WinError(code)
            details['dump'] = 'hang-emergency.dmp'
        except subprocess.TimeoutExpired:
            writer.terminate()
            details['dump_error'] = 'Emergency snapshot exceeded three seconds; shutdown continued'
    except OSError as error:
        details['dump_error'] = str(error)
    finally:
        user.EnumWindows(minimize, 0)
    (run / 'hang-emergency.json').write_text(json.dumps(details, indent=2), encoding='utf-8')


def watch(batch, parent_pid, job_name):
    kernel = kernel_api()
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.RegisterHotKey.argtypes = [w.HWND, ctypes.c_int, w.UINT, w.UINT]
    user.RegisterHotKey.restype = w.BOOL
    user.UnregisterHotKey.argtypes = [w.HWND, ctypes.c_int]
    user.UnregisterHotKey.restype = w.BOOL
    user.PeekMessageW.argtypes = [ctypes.POINTER(w.MSG), w.HWND, w.UINT, w.UINT, w.UINT]
    user.PeekMessageW.restype = w.BOOL
    parent = kernel.OpenProcess(0x100001, False, parent_pid)  # SYNCHRONIZE | TERMINATE
    job = kernel.OpenJobObjectW(0x000C, False, job_name)  # QUERY | TERMINATE
    registered = False
    ready = batch / 'emergency-stop-ready.json'
    try:
        if not parent or not job:
            raise ctypes.WinError(ctypes.get_last_error())
        # F12 is reserved for Windows debuggers; use Ctrl+Alt+Shift+F10.
        if not user.RegisterHotKey(None, 1, 0x4007, 0x79):
            raise ctypes.WinError(ctypes.get_last_error())
        registered = True
        temporary = ready.with_suffix('.tmp')
        temporary.write_text(json.dumps({'hotkey': 'Ctrl+Alt+Shift+F10', 'pid': os.getpid()}), encoding='utf-8')
        temporary.replace(ready)
        message = w.MSG()
        reason = None
        while True:
            if (batch / 'emergency-stop-finished').exists():
                break
            if kernel.WaitForSingleObject(parent, 0) == 0:
                reason = 'launcher_exited'
                break
            if (batch / 'STOP').exists():
                reason = 'stop_file'
                break
            try:
                deadline = json.loads((batch / 'emergency-stop-deadline.json').read_text(encoding='utf-8'))['deadline']
                if time.time() >= deadline:
                    reason = 'cleanup_timeout'
                    break
            except (OSError, ValueError, KeyError):
                pass
            while user.PeekMessageW(ctypes.byref(message), None, 0, 0, 1):
                if message.message == 0x0312:  # WM_HOTKEY
                    reason = 'hotkey'
            if reason:
                break
            time.sleep(0.05)
        if reason:
            if reason in ('hotkey', 'stop_file'):
                try:
                    emergency_snapshot(batch, job, kernel, user)
                except OSError as error:
                    (batch / 'emergency-snapshot-error.json').write_text(json.dumps({'error': str(error)}), encoding='utf-8')
            (batch / 'emergency-stop.json').write_text(json.dumps({'reason': reason, 'time': time.time()}), encoding='utf-8')
            kernel.TerminateJobObject(job, 1)
            # Release the debug attachment too if normal launcher cleanup cannot
            # finish. Only this launcher's exact retained handle is terminated.
            if kernel.WaitForSingleObject(parent, 5000) == 258:
                kernel.TerminateProcess(parent, 1)
    except OSError as error:
        temporary = ready.with_suffix('.tmp')
        temporary.write_text(json.dumps({'error': str(error)}), encoding='utf-8')
        temporary.replace(ready)
        if job:
            kernel.TerminateJobObject(job, 1)
    finally:
        if registered:
            user.UnregisterHotKey(None, 1)
        if parent:
            kernel.CloseHandle(parent)
        if job:
            kernel.CloseHandle(job)


if __name__ == '__main__':
    watch(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
