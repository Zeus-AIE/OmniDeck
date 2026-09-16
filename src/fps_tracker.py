"""
FPS Tracker using Intel PresentMon (ETW) and Windows API.
Safe with anti-cheat (No DLL injection, pure event tracing).
"""

import os
import sys
import time
import ctypes
import threading
import subprocess
import collections
from typing import Optional, Tuple, Dict, List
import psutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


SYSTEM_IGNORE_PROCESSES = {
    "explorer.exe", "searchhost.exe", "shellexperiencehost.exe",
    "taskmgr.exe", "cmd.exe", "powershell.exe", "python.exe",
    "pythonw.exe", "lockapp.exe", "startmenuexperiencehost.exe",
    "applicationframehost.exe", "textinputhost.exe", "systemsettings.exe",
    "dwm.exe", "conhost.exe", "runtimebroker.exe", "ctfmon.exe", "fontdrvhost.exe"
}


class FPSTracker:
    def __init__(self, bin_path: Optional[str] = None):
        if bin_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.bin_path = os.path.abspath(os.path.join(base_dir, "..", "bin", "PresentMon.exe"))
        else:
            self.bin_path = bin_path

        self._running = False
        self._proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Cache of PID -> process name
        self._pid_names: Dict[int, str] = {}
        
        # Per-PID frame records: deque of (timestamp, ms_between_presents)
        self._frame_history: Dict[int, collections.deque] = {}
        
        # Currently targeted game PID & name
        self.active_pid: Optional[int] = None
        self.active_name: str = "Chưa vào game"
        self.active_title: str = ""
        self.last_active_time: float = 0.0

        # Snapshot stats
        self.current_fps: float = 0.0
        self.avg_fps: float = 0.0
        self.one_percent_low: float = 0.0
        self.frametime_ms: float = 0.0
        
        # History buffers for graphs
        self.history_fps = collections.deque(maxlen=60)
        self.history_one_percent_low = collections.deque(maxlen=60)
        self.history_frametimes = collections.deque(maxlen=100)
        self._last_hist_time = 0.0


    def get_foreground_app(self) -> Tuple[Optional[int], str, str]:
        """Detect current foreground window and process name."""
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None, "", ""
        
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        p_id = pid.value
        if p_id == 0:
            return None, "", ""
        
        name = self._resolve_pid_name(p_id)
        
        title = ""
        title_len = user32.GetWindowTextLengthW(hwnd)
        if title_len > 0:
            buff = ctypes.create_unicode_buffer(title_len + 1)
            user32.GetWindowTextW(hwnd, buff, title_len + 1)
            title = buff.value
            
        return p_id, name, title

    def _resolve_pid_name(self, pid: int) -> str:
        if pid in self._pid_names:
            return self._pid_names[pid]
        try:
            p = psutil.Process(pid)
            name = p.name()
            self._pid_names[pid] = name
            return name
        except Exception:
            return f"PID:{pid}"

    def start(self):
        if self._running:
            return
        if not os.path.exists(self.bin_path):
            raise FileNotFoundError(f"PresentMon.exe not found at {self.bin_path}")

        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.kill()
            except Exception:
                pass
            self._proc = None

    def _reader_loop(self):
        cmd = [
            self.bin_path,
            "--stop_existing_session",
            "--no_console_stats",
            "--output_stdout"
        ]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

        try:
            CREATE_NO_WINDOW = 0x08000000
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"Failed to start PresentMon: {e}")
            self._running = False
            return

        header_parsed = False
        col_idx_pid = 1
        col_idx_ms = 10
        col_idx_app = 0

        while self._running and self._proc.poll() is None:
            try:
                line = self._proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line or line.startswith("warning:"):
                    continue

                parts = line.split(",")
                if not header_parsed:
                    # Parse CSV header dynamically
                    if "ProcessID" in parts:
                        header_parsed = True
                        try:
                            col_idx_app = parts.index("Application")
                            col_idx_pid = parts.index("ProcessID")
                            col_idx_ms = parts.index("MsBetweenPresents")
                        except ValueError:
                            pass
                    continue

                if len(parts) <= max(col_idx_pid, col_idx_ms):
                    continue

                try:
                    pid = int(parts[col_idx_pid])
                    app_name = parts[col_idx_app].strip()
                    ms_str = parts[col_idx_ms].strip()
                    if ms_str == "NA" or not ms_str:
                        continue
                    ms_between = float(ms_str)
                except ValueError:
                    continue

                if ms_between <= 0 or ms_between > 1000.0:
                    continue

                # Resolve application name
                if (not app_name or app_name == "<unknown>") and pid > 0:
                    app_name = self._resolve_pid_name(pid)
                else:
                    self._pid_names[pid] = app_name

                now = time.time()
                with self._lock:
                    if pid not in self._frame_history:
                        self._frame_history[pid] = collections.deque(maxlen=300)
                    self._frame_history[pid].append((now, ms_between))

            except Exception:
                pass

    def update(self):
        """Update active software selection and calculate frame statistics using 3-tier PID resolution."""
        fg_pid, fg_name, fg_title = self.get_foreground_app()
        now = time.time()

        with self._lock:
            target_pid = None
            target_name = ""

            # Check if fg_name is valid user app (not OS/shell)
            is_valid_fg_app = False
            if fg_pid and fg_name:
                low_fg = fg_name.lower()
                if low_fg not in SYSTEM_IGNORE_PROCESSES and not low_fg.startswith("antigravity"):
                    is_valid_fg_app = True

            # TIER 1: Check if the exact foreground PID has recent presents (in last 1.2s)
            if is_valid_fg_app and fg_pid in self._frame_history:
                recent_fg = [ft for (t, ft) in self._frame_history[fg_pid] if now - t <= 1.2]
                if len(recent_fg) >= 2:
                    target_pid = fg_pid
                    target_name = fg_name

            # TIER 2: If foreground PID has no presents, check ANY active process sharing the same exe name
            # (Covers Chromium GPU process, multi-process game engines, Unreal/Unity worker PIDs, launcher vs game)
            if target_pid is None and is_valid_fg_app:
                for pid, history in self._frame_history.items():
                    p_name = self._resolve_pid_name(pid)
                    if p_name.lower() == fg_name.lower():
                        recent_same = [ft for (t, ft) in history if now - t <= 1.2]
                        if len(recent_same) >= 2:
                            target_pid = pid
                            target_name = fg_name
                            break

            # TIER 3: Check any active process currently presenting frames (fallback for borderless, overlays, or launcher handoffs)
            if target_pid is None:
                best_pid = None
                best_count = 0
                for pid, history in self._frame_history.items():
                    name = self._resolve_pid_name(pid).lower()
                    if name in SYSTEM_IGNORE_PROCESSES or name.startswith("antigravity") or name.startswith("dwm"):
                        continue
                    recent = [ft for (t, ft) in history if now - t <= 1.2]
                    if len(recent) > best_count:
                        best_count = len(recent)
                        best_pid = pid

                if best_pid is not None and best_count >= 2:
                    target_pid = best_pid
                    target_name = self._resolve_pid_name(best_pid)

            # Update active targets
            if target_pid is not None:
                self.active_pid = target_pid
                self.active_name = target_name
                self.active_title = fg_title if is_valid_fg_app else ""
                self.last_active_time = now
            elif now - self.last_active_time > 5.0:
                self.active_pid = None
                self.active_name = fg_name if is_valid_fg_app else "Desktop / Tĩnh"
                self.active_title = ""


            # Calculate FPS and 1% Low for the active PID
            if self.active_pid and self.active_pid in self._frame_history:
                history = self._frame_history[self.active_pid]
                # Filter frames in last 1.0 second
                recent = [(t, ft) for (t, ft) in history if now - t <= 1.0]

                if len(recent) >= 2:
                    frame_times = [ft for (_, ft) in recent]
                    self.frametime_ms = frame_times[-1]

                    # Instantaneous FPS smoothed over recent frames
                    avg_ft = sum(frame_times) / len(frame_times)
                    self.current_fps = round(1000.0 / avg_ft, 1) if avg_ft > 0 else 0.0

                    # 1% Low calculation
                    sorted_ft = sorted(frame_times)
                    # 99th percentile frame time corresponds to 1% low FPS
                    idx_99 = min(len(sorted_ft) - 1, int(len(sorted_ft) * 0.99))
                    p99_ft = sorted_ft[idx_99]
                    self.one_percent_low = round(1000.0 / p99_ft, 1) if p99_ft > 0 else 0.0

                    # Average FPS over the window
                    time_span = recent[-1][0] - recent[0][0]
                    if time_span > 0:
                        self.avg_fps = round(len(recent) / time_span, 1)
                    else:
                        self.avg_fps = self.current_fps
                else:
                    self.current_fps = 0.0
                    self.one_percent_low = 0.0
                    self.frametime_ms = 0.0
            else:
                self.current_fps = 0.0
                self.one_percent_low = 0.0
                self.avg_fps = 0.0
                self.frametime_ms = 0.0

            # Update history buffers for graphs
            if now - self._last_hist_time >= 0.5:
                self._last_hist_time = now
                self.history_fps.append(self.current_fps)
                self.history_one_percent_low.append(self.one_percent_low)
                if self.frametime_ms > 0:
                    self.history_frametimes.append(self.frametime_ms)

    def get_stats(self) -> dict:
        self.update()
        with self._lock:
            return {
                "game_name": self.active_name,
                "game_title": self.active_title,
                "pid": self.active_pid,
                "fps": self.current_fps,
                "one_percent_low": self.one_percent_low,
                "avg_fps": self.avg_fps,
                "frametime_ms": round(self.frametime_ms, 2),
                "history_fps": list(self.history_fps),
                "history_one_percent_low": list(self.history_one_percent_low),
                "history_frametimes": list(self.history_frametimes)
            }


if __name__ == "__main__":
    tracker = FPSTracker()
    tracker.start()
    print("FPS Tracker started. Monitoring for 5 seconds...")
    for i in range(5):
        time.sleep(1)
        stats = tracker.get_stats()
        print(f"[{i+1}s] App: {stats['game_name']} | FPS: {stats['fps']} | 1% Low: {stats['one_percent_low']} | FrameTime: {stats['frametime_ms']}ms")
    tracker.stop()
    print("FPS Tracker stopped.")
