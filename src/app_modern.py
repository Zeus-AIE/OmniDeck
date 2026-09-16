"""
Legion Performance & FPS Monitor - Modern UI (v2.4 PRO)
Stack:
- Frontend: React 18 + Vite + TailwindCSS + Framer Motion (Apple Glassmorphism Design)
- Shell: Microsoft Edge WebView2 (GPU Accelerated, Low Overhead)
- Core: Zero-subprocess NVML C-API + ETW PresentMon + Windows PDH Dynamic Clock
- System: Win32 Kernel Named Mutex (Single-Instance Guard with Auto-Recovery) + Global Hotkeys (F8, F9, F10) + Tray
"""

import os
import sys
import time
import socket
import threading
import subprocess
import ctypes
import atexit
import traceback
import webview
import tkinter as tk

# Crash Logger: Prevent silent failures, display dialog and write to crash_log.txt
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    os.chdir(BASE_DIR)
except Exception:
    pass

def _global_exception_handler(exc_type, exc_value, exc_tb):
    log_path = os.path.join(BASE_DIR, "crash_log.txt")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- CRASH AT {time.ctime()} ---\n")
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
    try:
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Lỗi khởi động ứng dụng:\n\n{exc_value}\n\nXem chi tiết tại: {log_path}",
            "Legion Monitor Error",
            0x10  # MB_ICONERROR
        )
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _global_exception_handler

# Set AppUserModelID for Windows Taskbar binding
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ZeusAIE.OmniDeck.App.2.5")
except Exception:
    pass

# DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Ensure Dedicated UserDataFolder for WebView2 (Fixes Access Denied when running as Administrator)
try:
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    WEBVIEW2_DATA_DIR = os.path.join(local_app_data, "LegionFPSMonitor", "WebView2Data")
    os.makedirs(WEBVIEW2_DATA_DIR, exist_ok=True)
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = WEBVIEW2_DATA_DIR
except Exception:
    WEBVIEW2_DATA_DIR = None

# Ensure imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hw_monitor import HardwareMonitor
from fps_tracker import FPSTracker
from settings_manager import SettingsManager
from overlay_window import InGameOverlay
from hotkey import GlobalHotkeyListener
from tray_manager import SystemTrayManager
from web_bridge import TelemetryAPI

SINGLE_INSTANCE_PORT = 49152
_SINGLE_INSTANCE_MUTEX = None

def _log_debug(msg):
    if os.environ.get("LEGION_DEBUG") == "1":
        try:
            with open(os.path.join(BASE_DIR, "debug_run.log"), "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        except Exception:
            pass

def refresh_system_tray():
    """Refreshes the Windows taskbar and notification overflow area to eliminate ghost/zombie icons."""
    try:
        u32 = ctypes.windll.user32
        h_tray = u32.FindWindowW("Shell_TrayWnd", None)
        if h_tray:
            h_notify = u32.FindWindowExW(h_tray, 0, "TrayNotifyWnd", None)
            if h_notify:
                h_sys = u32.FindWindowExW(h_notify, 0, "SysPager", None)
                h_tool = u32.FindWindowExW(h_sys if h_sys else h_notify, 0, "ToolbarWindow32", None)
                if h_tool:
                    u32.InvalidateRect(h_tool, None, True)
                    u32.UpdateWindow(h_tool)
        h_overflow = u32.FindWindowW("NotifyIconOverflowWindow", None)
        if h_overflow:
            h_tool2 = u32.FindWindowExW(h_overflow, 0, "ToolbarWindow32", None)
            if h_tool2:
                u32.InvalidateRect(h_tool2, None, True)
                u32.UpdateWindow(h_tool2)
    except Exception:
        pass

def _force_cleanup_old_instances(my_pid=None):
    """Proactively terminates any frozen or orphaned python processes running legion monitor."""
    if my_pid is None:
        my_pid = os.getpid()
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                if pid != my_pid and 'python' in (proc.info.get('name') or '').lower():
                    try:
                        cmdline = " ".join(proc.cmdline() or [])
                        if "app_modern.py" in cmdline or "app.py" in cmdline or "legion_fps_monitor" in cmdline:
                            _log_debug(f"Terminating orphaned process PID: {pid}")
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        _log_debug(f"Process cleanup exception: {e}")

def check_and_enforce_single_instance():
    """Atomic Windows Kernel Named Mutex check with Auto-Recovery & Admin Takeover.
    Guarantees strictly 1 instance while ensuring dead/zombie processes never block launch."""
    global _SINGLE_INSTANCE_MUTEX
    try:
        is_current_admin = False
        try:
            is_current_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            pass

        _log_debug(f"check_and_enforce_single_instance: is_current_admin={is_current_admin}")

        mutex_name = r"Local\LegionFPSMonitor_SingleInstance_Mutex_v2"
        _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
        last_err = ctypes.windll.kernel32.GetLastError()
        _log_debug(f"CreateMutexW result: handle={_SINGLE_INSTANCE_MUTEX}, last_err={last_err}")

        # 183 = ERROR_ALREADY_EXISTS: Another process is already holding the mutex!
        if last_err == 183:
            if is_current_admin:
                _log_debug("Admin instance taking over existing instance...")
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.settimeout(0.6)
                    client.connect(("127.0.0.1", SINGLE_INSTANCE_PORT))
                    client.sendall(b"TAKEOVER")
                    client.close()
                    _log_debug("TAKEOVER signal sent via socket")
                    time.sleep(0.3)
                except Exception as e:
                    _log_debug(f"TAKEOVER socket notification: {e}")

                _force_cleanup_old_instances()
                refresh_system_tray()
                time.sleep(0.3)

                # Close old handle and re-acquire
                try:
                    if _SINGLE_INSTANCE_MUTEX:
                        ctypes.windll.kernel32.CloseHandle(_SINGLE_INSTANCE_MUTEX)
                except Exception:
                    pass
                _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
                _log_debug(f"Re-acquired Mutex handle as Admin: {_SINGLE_INSTANCE_MUTEX}")
                return  # Continue running as Admin!
            else:
                _log_debug("Non-admin instance detected existing app, sending RESTORE...")
                restore_success = False
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.settimeout(0.8)
                    client.connect(("127.0.0.1", SINGLE_INSTANCE_PORT))
                    client.sendall(b"RESTORE")
                    client.close()
                    _log_debug("RESTORE signal sent successfully")
                    restore_success = True
                except Exception as e:
                    _log_debug(f"RESTORE connection failed (process may be dead/hung): {e}")

                if restore_success:
                    # Healthy instance exists and was signaled -> exit launcher immediately
                    sys.exit(0)
                else:
                    # The existing process is DEAD or HUNG (or was old app.py without socket)!
                    # Auto-recover: clean up orphaned processes and launch freshly!
                    _log_debug("Existing process is unresponsive! Initiating auto-recovery...")
                    _force_cleanup_old_instances()
                    refresh_system_tray()
                    time.sleep(0.3)
                    try:
                        if _SINGLE_INSTANCE_MUTEX:
                            ctypes.windll.kernel32.CloseHandle(_SINGLE_INSTANCE_MUTEX)
                    except Exception:
                        pass
                    _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
                    _log_debug(f"Auto-recovery: acquired Mutex handle: {_SINGLE_INSTANCE_MUTEX}")
                    return  # Continue and launch app!
        else:
            _log_debug("First instance acquired Mutex successfully")
    except Exception as e:
        _log_debug(f"check_and_enforce_single_instance exception: {e}")


class ModernLegionApp:
    def __init__(self):
        self.settings_mgr = SettingsManager()
        self.hw = HardwareMonitor()
        self.hw.start()

        self.fps = FPSTracker()
        self.fps.start()

        # Paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.png_path = os.path.join(base_dir, "assets", "icon.png")
        self.ico_path = os.path.join(base_dir, "assets", "icon.ico")
        self.html_path = os.path.join(base_dir, "ui", "dist", "index.html")

        # Subsystems initialized after main webview window creates handle
        self._secondary_initialized = False
        self.overlay = None
        self.overlay_root = None
        self.hotkeys = None
        self.tray = None

        # 1. Web Bridge API
        self.api = TelemetryAPI(
            hw_monitor=self.hw,
            fps_tracker=self.fps,
            settings_mgr=self.settings_mgr,
            overlay=None,
            on_exit_cb=self._on_full_exit
        )

        # 2. WebView2 Window (created cleanly on main thread)
        self.win = webview.create_window(
            title="OmniDeck - Universal Hardware & Game HUD v2.5 PRO",
            url=self.html_path if os.path.exists(self.html_path) else "about:blank",
            js_api=self.api,
            width=960,
            height=860,
            min_size=(860, 750),
            background_color="#0d0e12"
        )
        self.win.events.loaded += self._schedule_secondary_init
        self.win.events.closing += self._on_window_closing

    def restore_and_focus(self):
        """Restores WebView2 window from minimized or hidden and brings it to the foreground."""
        _log_debug("restore_and_focus() executing...")
        try:
            self.win.show()
        except Exception as e:
            _log_debug(f"win.show error: {e}")
        try:
            self.win.restore()
        except Exception as e:
            _log_debug(f"win.restore error: {e}")
        try:
            if hasattr(self.win, "native") and self.win.native:
                hwnd = int(self.win.native.Handle.ToInt64())
                # SW_RESTORE = 9, SW_SHOW = 5
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.BringWindowToTop(hwnd)
        except Exception as e:
            _log_debug(f"Win32 SetForegroundWindow error: {e}")

    def hide_dashboard(self):
        """Hides the dashboard window cleanly to system tray."""
        _log_debug("hide_dashboard() called")
        try:
            self.win.hide()
        except Exception as e:
            _log_debug(f"win.hide error: {e}")

    def _init_overlay_thread(self):
        """Initializes Tkinter overlay in background thread."""
        ready_event = threading.Event()

        def _run_overlay():
            self.overlay_root = tk.Tk()
            self.overlay_root.withdraw()
            self.overlay = InGameOverlay(
                master=self.overlay_root,
                settings_mgr=self.settings_mgr,
                on_close_callback=self._on_overlay_closed
            )
            if not self.settings_mgr.get("overlay_enabled", False):
                self.overlay.withdraw()
            ready_event.set()

            # Background metrics loop for overlay
            def _loop():
                try:
                    if self.overlay and self.overlay.winfo_exists():
                        if self.settings_mgr.get("overlay_enabled", False):
                            f_data = self.fps.get_stats()
                            h_data = self.hw.get_snapshot()
                            self.overlay.update_metrics(f_data, h_data)
                except Exception:
                    pass
                if self.overlay_root:
                    self.overlay_root.after(400, _loop)

            self.overlay_root.after(400, _loop)
            self.overlay_root.mainloop()

        t = threading.Thread(target=_run_overlay, daemon=True)
        t.start()
        ready_event.wait(timeout=2.0)

    def _on_overlay_closed(self):
        self.settings_mgr.set("overlay_enabled", False)

    def _on_hotkey_toggle_overlay(self):
        self.api.toggle_overlay()

    def _on_hotkey_transparency(self):
        self.api.cycle_transparency()

    def _on_hotkey_click_through(self):
        self.api.toggle_click_through()

    def _on_tray_toggle_dashboard(self):
        self.restore_and_focus()

    def _on_tray_hide_dashboard(self):
        self.hide_dashboard()

    def _on_window_closing(self):
        _log_debug("Window closing event triggered")
        if self.settings_mgr.get("close_to_tray", True):
            _log_debug("close_to_tray is True -> hiding window")
            self.hide_dashboard()
            return False  # Prevent exit, keep alive in system tray!
        _log_debug("close_to_tray is False -> full exit")
        self._on_full_exit()
        return True

    def _start_single_instance_listener(self):
        def _server():
            try:
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
                srv.listen(2)
                _log_debug(f"Single instance listener running on port {SINGLE_INSTANCE_PORT}")
                while True:
                    conn, _ = srv.accept()
                    data = conn.recv(32)
                    _log_debug(f"Single instance listener received: {data}")
                    if b"RESTORE" in data:
                        _log_debug("Handling RESTORE request: bringing dashboard to foreground")
                        self.restore_and_focus()
                    elif b"TAKEOVER" in data:
                        _log_debug("Single instance listener received TAKEOVER, shutting down old instance")
                        conn.close()
                        srv.close()
                        self._on_full_exit()
                        return
                    conn.close()
            except Exception as e:
                _log_debug(f"Single instance server error: {e}")

        t = threading.Thread(target=_server, daemon=True)
        t.start()

    def _on_full_exit(self):
        _log_debug("Executing _on_full_exit()...")
        # Hard fail-safe: Ensure process forcibly exits within 400ms no matter what
        threading.Timer(0.4, lambda: (refresh_system_tray(), os._exit(0))).start()
        try:
            if self.overlay_root:
                try:
                    self.overlay_root.quit()
                except Exception:
                    pass
            try:
                self.fps.stop()
            except Exception:
                pass
            try:
                self.hw.stop()
            except Exception:
                pass
            try:
                self.hotkeys.stop()
            except Exception:
                pass
            try:
                self.tray.stop()
            except Exception:
                pass
        except Exception as e:
            _log_debug(f"Error during cleanup: {e}")
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "PresentMon.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=0x08000000
            )
        except Exception:
            pass
        refresh_system_tray()
        _log_debug("Calling os._exit(0)")
        os._exit(0)

    def _schedule_secondary_init(self):
        if self._secondary_initialized:
            return
        self._secondary_initialized = True
        _log_debug("Main webview window ready! Initializing secondary subsystems...")
        try:
            # 1. Start Single-Instance Server
            self._start_single_instance_listener()

            # 2. Start Tkinter Overlay in dedicated thread
            self._init_overlay_thread()
            if self.api:
                self.api.overlay = self.overlay

            # 3. Start Global Hotkeys
            self.hotkeys = GlobalHotkeyListener(
                on_toggle_overlay=self._on_hotkey_toggle_overlay,
                on_toggle_transparency=self._on_hotkey_transparency,
                on_toggle_click_through=self._on_hotkey_click_through
            )
            self.hotkeys.start()

            # 4. Start System Tray
            self.tray = SystemTrayManager(
                icon_path=self.png_path if os.path.exists(self.png_path) else self.ico_path,
                on_toggle_dashboard=self._on_tray_toggle_dashboard,
                on_hide_dashboard=self._on_tray_hide_dashboard,
                on_toggle_overlay=self._on_hotkey_toggle_overlay,
                on_toggle_transparency=self._on_hotkey_transparency,
                on_exit=self._on_full_exit,
                on_toggle_click_through=self._on_hotkey_click_through
            )
            self.tray.start()
            atexit.register(self.tray.stop)
            _log_debug("All secondary subsystems initialized successfully!")
        except Exception as e:
            _log_debug(f"Error in _schedule_secondary_init: {e}")

    def _start_background_fallback(self):
        # Fallback in case loaded event doesn't fire within 2.5 seconds
        time.sleep(2.5)
        self._schedule_secondary_init()

    def run(self):
        _log_debug(f"Calling webview.start(storage_path={WEBVIEW2_DATA_DIR})...")
        try:
            if WEBVIEW2_DATA_DIR:
                webview.start(func=self._start_background_fallback, storage_path=WEBVIEW2_DATA_DIR)
            else:
                webview.start(func=self._start_background_fallback)
            _log_debug("webview.start() returned cleanly")
        except Exception as e:
            _log_debug(f"webview.start() exception: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    _log_debug("=== APP LAUNCH ===")
    refresh_system_tray()
    check_and_enforce_single_instance()
    _log_debug("Starting ModernLegionApp()...")
    app = ModernLegionApp()
    _log_debug("App initialized, starting run()...")
    app.run()
    refresh_system_tray()
    _log_debug("=== APP TERMINATED ===")
