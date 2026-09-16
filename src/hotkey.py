"""
Global Hotkey Listener for Windows using GetAsyncKeyState.
Works seamlessly in full-screen games, background, and any application.
No admin privileges required, 0 external dependencies.
"""

import time
import ctypes
import threading
from typing import Callable

class GlobalHotkeyListener:
    def __init__(
        self,
        on_toggle_overlay: Callable,
        on_toggle_transparency: Callable,
        on_toggle_click_through: Callable = None
    ):
        self.on_toggle_overlay = on_toggle_overlay
        self.on_toggle_transparency = on_toggle_transparency
        self.on_toggle_click_through = on_toggle_click_through
        self.running = False
        self._thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _listen_loop(self):
        user32 = ctypes.windll.user32
        
        # Virtual Key Codes
        VK_F8 = 0x77   # F8 key (Toggle Click-Through / Pin)
        VK_F9 = 0x78   # F9 key (Toggle Overlay)
        VK_F10 = 0x79  # F10 key (Toggle Transparency)
        
        f8_pressed = False
        f9_pressed = False
        f10_pressed = False

        while self.running:
            try:
                # Check F8 key state (Click-Through Pin)
                is_f8 = (user32.GetAsyncKeyState(VK_F8) & 0x8000) != 0
                if is_f8 and not f8_pressed:
                    f8_pressed = True
                    if self.on_toggle_click_through:
                        try:
                            self.on_toggle_click_through()
                        except Exception:
                            pass
                elif not is_f8:
                    f8_pressed = False

                # Check F9 key state (Toggle Overlay)
                is_f9 = (user32.GetAsyncKeyState(VK_F9) & 0x8000) != 0
                if is_f9 and not f9_pressed:
                    f9_pressed = True
                    try:
                        self.on_toggle_overlay()
                    except Exception:
                        pass
                elif not is_f9:
                    f9_pressed = False

                # Check F10 key state (Toggle Transparency)
                is_f10 = (user32.GetAsyncKeyState(VK_F10) & 0x8000) != 0
                if is_f10 and not f10_pressed:
                    f10_pressed = True
                    try:
                        self.on_toggle_transparency()
                    except Exception:
                        pass
                elif not is_f10:
                    f10_pressed = False

            except Exception:
                pass

            time.sleep(0.04)  # 25 checks per second, negligible CPU usage (<0.01%)
