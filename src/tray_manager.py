"""
System Tray Manager module using pystray.
Allows Legion Performance & FPS Monitor to run cleanly in the background.
"""

import os
import threading
from typing import Callable, Optional
from PIL import Image
import pystray

class SystemTrayManager:
    def __init__(
        self,
        icon_path: str,
        on_toggle_dashboard: Callable,
        on_toggle_overlay: Callable,
        on_toggle_transparency: Callable,
        on_exit: Callable,
        on_toggle_click_through: Optional[Callable] = None,
        on_hide_dashboard: Optional[Callable] = None
    ):
        self.icon_path = icon_path
        self.on_toggle_dashboard = on_toggle_dashboard
        self.on_hide_dashboard = on_hide_dashboard
        self.on_toggle_overlay = on_toggle_overlay
        self.on_toggle_transparency = on_toggle_transparency
        self.on_exit = on_exit
        self.on_toggle_click_through = on_toggle_click_through

        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        try:
            if os.path.exists(self.icon_path):
                image = Image.open(self.icon_path)
            else:
                image = Image.new("RGBA", (64, 64), (0, 210, 255, 255))
        except Exception:
            image = Image.new("RGBA", (64, 64), (0, 210, 255, 255))

        menu_items = [
            pystray.MenuItem("Mở Dashboard", self._on_menu_dashboard, default=True),
        ]
        if self.on_hide_dashboard:
            menu_items.append(pystray.MenuItem("Ẩn Dashboard", self._on_menu_hide_dashboard))
            
        menu_items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Bật / Tắt Overlay (F9)", self._on_menu_overlay),
            pystray.MenuItem("Khóa / Xuyên thấu chuột (F8)", self._on_menu_click_through),
            pystray.MenuItem("Đổi độ trong suốt (F10)", self._on_menu_transparency),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Thoát hoàn toàn ứng dụng", self._on_menu_exit)
        ])

        menu = pystray.Menu(*menu_items)

        self._icon = pystray.Icon(
            name="LegionFPSMonitor",
            icon=image,
            title="Legion Performance & FPS Monitor (Nhấp để mở)",
            menu=menu
        )

        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def _on_menu_dashboard(self, icon, item):
        self.on_toggle_dashboard()

    def _on_menu_hide_dashboard(self, icon, item):
        if self.on_hide_dashboard:
            self.on_hide_dashboard()

    def _on_menu_overlay(self, icon, item):
        self.on_toggle_overlay()

    def _on_menu_click_through(self, icon, item):
        if self.on_toggle_click_through:
            self.on_toggle_click_through()

    def _on_menu_transparency(self, icon, item):
        self.on_toggle_transparency()

    def _on_menu_exit(self, icon, item):
        self.stop()
        self.on_exit()
