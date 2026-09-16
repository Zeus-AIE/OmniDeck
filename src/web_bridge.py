"""
Web Bridge API for Legion Performance & FPS Monitor Modern UI.
Exposes real-time telemetry and control methods to the React frontend via window.pywebview.api.
"""

from typing import Dict, Any


class TelemetryAPI:
    def __init__(self, hw_monitor, fps_tracker, settings_mgr, overlay=None, on_exit_cb=None):
        self.hw = hw_monitor
        self.fps = fps_tracker
        self.settings_mgr = settings_mgr
        self.overlay = overlay
        self.on_exit_cb = on_exit_cb

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns instantaneous snapshot of hardware and game telemetry."""
        try:
            fps_data = self.fps.get_stats()
            hw_data = self.hw.get_snapshot()
            settings = self.settings_mgr.get_all()
            return {
                "fps_data": fps_data,
                "hw_data": hw_data,
                "settings": settings
            }
        except Exception as e:
            return {"error": str(e)}

    def save_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Saves user settings and applies live to Overlay."""
        try:
            if hasattr(self.settings_mgr, "update"):
                self.settings_mgr.update(new_settings)
            else:
                for k, v in new_settings.items():
                    self.settings_mgr.set(k, v)

            if self.overlay:
                if hasattr(self.overlay, "winfo_exists") and hasattr(self.overlay, "after"):
                    try:
                        if self.overlay.winfo_exists():
                            self.overlay.after(0, self.overlay.apply_settings)
                    except Exception:
                        pass
                elif hasattr(self.overlay, "apply_settings"):
                    self.overlay.apply_settings()
            return True
        except Exception:
            return False

    def toggle_overlay(self) -> bool:
        """Toggles Overlay visibility."""
        if not self.overlay:
            return False
        current_state = self.settings_mgr.get("overlay_enabled", False)
        next_state = not current_state
        self.settings_mgr.set("overlay_enabled", next_state)
        if next_state:
            self.overlay.deiconify()
            self.overlay.lift()
        else:
            self.overlay.withdraw()
        return next_state

    def toggle_click_through(self) -> bool:
        """Toggles Click-Through Passthrough [F8]."""
        if self.overlay and hasattr(self.overlay, "toggle_click_through"):
            return self.overlay.toggle_click_through()
        return False

    def cycle_transparency(self) -> int:
        """Cycles background transparency [F10]."""
        if self.overlay and hasattr(self.overlay, "cycle_transparency"):
            return self.overlay.cycle_transparency()
        return 65

    def set_bg_transparency(self, pct: int) -> bool:
        """Sets background transparency percentage (0% - 100%) live with zero lag."""
        pct = max(0, min(100, int(pct)))
        self.settings_mgr.set("overlay_bg_transparency_pct", pct)
        self.settings_mgr.set("overlay_transparency_pct", pct)
        bg_mode = "transparent" if pct <= 0 else ("solid" if pct >= 95 else "badges")
        self.settings_mgr.set("overlay_bg_mode", bg_mode)
        if self.overlay and hasattr(self.overlay, "set_bg_transparency_pct"):
            try:
                if hasattr(self.overlay, "after"):
                    self.overlay.after(0, lambda: self.overlay.set_bg_transparency_pct(pct))
                else:
                    self.overlay.set_bg_transparency_pct(pct)
            except Exception:
                pass
        return True

    def set_text_transparency(self, pct: int) -> bool:
        """Sets text/indicator transparency percentage (20% - 100%) live with zero lag."""
        pct = max(20, min(100, int(pct)))
        self.settings_mgr.set("overlay_text_transparency_pct", pct)
        if self.overlay and hasattr(self.overlay, "set_text_transparency_pct"):
            try:
                if hasattr(self.overlay, "after"):
                    self.overlay.after(0, lambda: self.overlay.set_text_transparency_pct(pct))
                else:
                    self.overlay.set_text_transparency_pct(pct)
            except Exception:
                pass
        return True

    def exit_app(self):
        """Clean application shutdown."""
        if self.on_exit_cb:
            self.on_exit_cb()
