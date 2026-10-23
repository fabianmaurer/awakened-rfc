"""Bounded Windows setup confirmation for a launcher-owned Civ4 process."""
import ctypes
from ctypes import wintypes
import time


class SetupConfirmation:
    def __init__(self, pid, run):
        self.pid = pid
        self.run = run
        self.ready_since = None
        self.last_input = 0
        self.attempts = 0
        self.focused_since = None
        self.focused_hwnd = None
        self.last_state = None
        self.focus_requested = False
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel32.GetCurrentThreadId.argtypes = []
        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        signatures = {
            'EnumWindows': ([self.callback_type, wintypes.LPARAM], wintypes.BOOL),
            'GetWindowThreadProcessId': ([wintypes.HWND, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
            'IsWindowVisible': ([wintypes.HWND], wintypes.BOOL),
            'GetClientRect': ([wintypes.HWND, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
            'GetClassNameW': ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            'GetWindowTextW': ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            'SetForegroundWindow': ([wintypes.HWND], wintypes.BOOL),
            'GetForegroundWindow': ([], wintypes.HWND),
            'IsIconic': ([wintypes.HWND], wintypes.BOOL),
            'ShowWindowAsync': ([wintypes.HWND, ctypes.c_int], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.user32, name)
            function.argtypes = arguments
            function.restype = result

    def log_state(self, state):
        if state == self.last_state:
            return
        self.last_state = state
        with (self.run / 'setup-input.log').open('a', encoding='ascii') as handle:
            handle.write('%s: %s\n' % (time.strftime('%H:%M:%S'), state))

    def foreground(self, hwnd):
        # Never join another app's input queue or take focus back repeatedly.
        if self.focus_requested:
            return
        self.focus_requested = True
        if self.user32.IsIconic(hwnd):
            self.user32.ShowWindowAsync(hwnd, 9)  # SW_RESTORE without waiting on the game
        if self.user32.GetForegroundWindow() == hwnd:
            return
        self.user32.SetForegroundWindow(hwnd)

    def tick(self, ready):
        # The mod authenticates the activation token/PID and validates the
        # scenario before publishing readiness. Never navigate the main menu.
        if (self.run / 'game-starting.json').exists() or (self.run / 'started.json').exists():
            return
        if not ready or ready.get('pid') != self.pid or ready.get('phase') != 'scenario_setup':
            self.log_state('Waiting for authenticated scenario setup')
            return
        now = time.monotonic()
        if self.ready_since is None:
            self.ready_since = now
        # Readiness is published while the scenario is loading, before its
        # setup UI necessarily accepts DirectInput. Under parallel load a
        # short burst can exhaust every attempt before that UI is ready.
        retry_interval = min(15.0, 2.0 ** max(0, self.attempts - 1))
        if now - self.ready_since < 0.5 or now - self.last_input < retry_interval:
            return
        windows = []
        dialogs = []

        @self.callback_type
        def collect(hwnd, unused):
            owner = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value != self.pid or not self.user32.IsWindowVisible(hwnd):
                return True
            name = ctypes.create_unicode_buffer(256)
            title = ctypes.create_unicode_buffer(512)
            self.user32.GetClassNameW(hwnd, name, len(name))
            self.user32.GetWindowTextW(hwnd, title, len(title))
            if name.value == '#32770':
                dialogs.append(title.value)
            else:
                rect = wintypes.RECT()
                if self.user32.GetClientRect(hwnd, ctypes.byref(rect)):
                    area = rect.right * rect.bottom
                    if (rect.right >= 800 and rect.bottom >= 600) or self.user32.IsIconic(hwnd):
                        windows.append((area, hwnd))
            return True

        self.user32.EnumWindows(collect, 0)
        if dialogs:
            # Do not acknowledge XML errors or other native dialogs blindly.
            raise RuntimeError('Unexpected Civ4 dialog during setup: ' + repr(dialogs))
        if not windows:
            self.focused_since = None
            self.log_state('Waiting for visible child game window')
            return
        if self.attempts >= 12:
            self.log_state('Twelve confirmations sent; waiting for GameStart')
            return  # Allow slow map loading to finish until the startup timeout.
        foreground = self.user32.GetForegroundWindow()
        # The executable can expose multiple large top-level windows. Prefer
        # its actual foreground window over an inactive larger render window.
        hwnd = next((window for area, window in windows if window == foreground), max(windows)[1])
        if hwnd != self.focused_hwnd:
            self.focused_hwnd = hwnd
            self.focused_since = None
        if self.user32.GetForegroundWindow() != hwnd:
            self.focused_since = None
            self.foreground(hwnd)
            self.log_state('Waiting for child game keyboard focus (target=%s, foreground=%s)' %
                           (hwnd, self.user32.GetForegroundWindow()))
            return  # Windows may refuse focus; never send input to another app.
        if self.focused_since is None:
            self.focused_since = now
        if now - self.focused_since < 0.3:
            self.log_state('Allowing DirectInput to acquire keyboard focus')
            return

        class KeyInput(ctypes.Structure):
            _fields_ = [('vk', wintypes.WORD), ('scan', wintypes.WORD),
                        ('flags', wintypes.DWORD), ('time', wintypes.DWORD),
                        ('extra', ctypes.c_size_t)]

        class MouseInput(ctypes.Structure):
            _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG),
                        ('data', wintypes.DWORD), ('flags', wintypes.DWORD),
                        ('time', wintypes.DWORD), ('extra', ctypes.c_size_t)]

        class Payload(ctypes.Union):
            _fields_ = [('keyboard', KeyInput), ('mouse', MouseInput)]

        class Input(ctypes.Structure):
            _fields_ = [('type', wintypes.DWORD), ('payload', Payload)]

        # SendInput reaches the game's DirectInput handling. Window messages
        # alone are not reliable for this DirectX UI. No screen coordinates.
        send = self.user32.SendInput
        send.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
        send.restype = wintypes.UINT
        inputs = (Input * 2)()
        for index, flags in enumerate((0x0008, 0x0008 | 0x0002)):
            inputs[index].type = 1
            # DirectInput consumes physical scan codes. VK_RETURN with a zero
            # scan code can be accepted by SendInput but missed by the game.
            inputs[index].payload.keyboard = KeyInput(0, 0x1C, flags, 0, 0)
        # Recheck immediately before injecting input.
        if ((self.run / 'game-starting.json').exists() or
                (self.run / 'started.json').exists() or
                self.user32.GetForegroundWindow() != hwnd):
            return
        if send(1, ctypes.byref(inputs[0]), ctypes.sizeof(Input)) != 1:
            raise ctypes.WinError(ctypes.get_last_error())
        # DirectInput polls between frames; an instantaneous down/up pair can
        # otherwise disappear without the menu ever observing the held key.
        try:
            time.sleep(0.2)
        finally:
            # Always release a key we pressed, even if focus changes meanwhile.
            if send(1, ctypes.byref(inputs[1]), ctypes.sizeof(Input)) != 1:
                raise ctypes.WinError(ctypes.get_last_error())
        self.last_input = time.monotonic()
        self.attempts += 1
        self.log_state('Confirmation %d sent to child PID %d (Enter scan code)' %
                       (self.attempts, self.pid))
