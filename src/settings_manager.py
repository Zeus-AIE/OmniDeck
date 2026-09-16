"""
Settings Manager module for Legion Performance & FPS Monitor.
Saves and loads user preferences from settings.json.
"""

import os
import json
from typing import Dict, Any

DEFAULT_SETTINGS = {
    # Overlay Settings
    "overlay_enabled": False,
    "overlay_layout": "horizontal",  # "horizontal", "compact", "corner", "vertical"
    "overlay_theme": "apple_dark",   # "apple_dark", "ice_blue", "cyberpunk", "blood_red", "stealth"
    "overlay_scale": "medium",       # "small" (0.8), "medium" (1.0), "large" (1.25)
    "overlay_bg_mode": "badges",     # "transparent" (Pure HUD), "badges" (Dark Pills), "solid" (Full Bar)
    "overlay_transparency_pct": 90,  # Legacy fallback
    "overlay_bg_transparency_pct": 65,   # 0% (Trong suốt hoàn toàn) đến 100% (Đậm đặc)
    "overlay_text_transparency_pct": 100, # 30% đến 100% độ rõ nét chữ & số liệu
    "overlay_click_through": False,  # True = Mouse passthrough / locked
    "overlay_position": {"x": 100, "y": 20},
    "overlay_width_mode": "auto",    # "auto" or "manual"
    "overlay_manual_width": 1080,    # width in pixels when in manual mode

    # Bottom Graphs Deck (Bảng biểu đồ bên dưới thanh số liệu)
    "overlay_show_bottom_graphs": True,
    "overlay_bottom_graphs": {
        "fps": True,
        "cpu": True,
        "gpu": True,
        "ram_net": True,
        "fan": True
    },

    # Mini Graphs toggles on Overlay
    "overlay_mini_graphs": {
        "fps": False,
        "cpu": False,
        "gpu": False,
        "ram": False,
        "network": False
    },
    
    # Visible Metrics toggles in Overlay
    "metrics": {
        "app_name": True,
        "fps": True,
        "one_percent_low": True,
        "frametime": True,
        "cpu_temp": True,
        "cpu_usage": True,
        "cpu_clock": False,
        "gpu_temp": True,
        "gpu_usage": True,
        "gpu_clock": False,
        "gpu_power": False,
        "ram": True,
        "network": True,
        "fan": True
    },
    
    # Fan Cooling Settings
    "overlay_fan_mode": "dual",      # "dual" (CPU & GPU), "max" (Highest RPM), "cpu", "gpu"
    "dashboard_show_fan": True,      # Show Fan Section on Main Dashboard

    # App Behavior
    "minimize_to_tray": True,
    "close_to_tray": True,
    "start_minimized": False
}

THEMES = {
    "apple_dark": {
        "name": "Apple Dark Minimalist (Khuyên dùng)",
        "bg": "#161618",
        "border": "#2c2c30",
        "sep": "#38383e",
        "accent": "#0A84FF",
        "fps_good": "#30D158",
        "fps_warn": "#FF9F0A",
        "fps_bad": "#FF453A",
        "cpu_temp": "#FF453A",
        "gpu_temp": "#0A84FF",
        "load": "#FFD60A",
        "text": "#FFFFFF",
        "subtext": "#8E8E93",
        "net_down": "#64D2FF",
        "net_up": "#BF5AF2"
    },
    "ice_blue": {
        "name": "Legion Ice Blue",
        "bg": "#0d1117",
        "border": "#21262d",
        "sep": "#30363d",
        "accent": "#58a6ff",
        "fps_good": "#3fb950",
        "fps_warn": "#d29922",
        "fps_bad": "#f85149",
        "cpu_temp": "#ff7b72",
        "gpu_temp": "#58a6ff",
        "load": "#e3b341",
        "text": "#c9d1d9",
        "subtext": "#8b949e",
        "net_down": "#39c5cf",
        "net_up": "#bc8cff"
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "bg": "#0f081d",
        "border": "#ff007f",
        "sep": "#3a1d5a",
        "accent": "#ffe600",
        "fps_good": "#00ffcc",
        "fps_warn": "#ffe600",
        "fps_bad": "#ff0055",
        "cpu_temp": "#ff007f",
        "gpu_temp": "#00d2ff",
        "load": "#ffe600",
        "text": "#ffffff",
        "subtext": "#a78bfa",
        "net_down": "#00ffcc",
        "net_up": "#ff00aa"
    },
    "blood_red": {
        "name": "Blood Red Gaming",
        "bg": "#14090b",
        "border": "#491217",
        "sep": "#381014",
        "accent": "#ff4d4f",
        "fps_good": "#ff7875",
        "fps_warn": "#ffa940",
        "fps_bad": "#a8071a",
        "cpu_temp": "#ff4d4f",
        "gpu_temp": "#ff7a45",
        "load": "#ffc069",
        "text": "#f5f5f5",
        "subtext": "#8c8c8c",
        "net_down": "#ff7875",
        "net_up": "#ffa39e"
    },
    "stealth": {
        "name": "Stealth Monochrome",
        "bg": "#161616",
        "border": "#2c2c2c",
        "sep": "#333333",
        "accent": "#e6edf3",
        "fps_good": "#ffffff",
        "fps_warn": "#cccccc",
        "fps_bad": "#888888",
        "cpu_temp": "#e6edf3",
        "gpu_temp": "#d0d7de",
        "load": "#aaaaaa",
        "text": "#f0f6fc",
        "subtext": "#7d8590",
        "net_down": "#e6edf3",
        "net_up": "#b1bac4"
    }
}

class SettingsManager:
    def __init__(self, filepath: str = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.filepath = os.path.join(base_dir, "settings.json")
        else:
            self.filepath = filepath
            
        self.settings: Dict[str, Any] = json.loads(json.dumps(DEFAULT_SETTINGS))
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    # Merge shallowly with defaults to ensure all keys exist
                    for k, v in data.items():
                        if isinstance(v, dict) and k in self.settings:
                            self.settings[k].update(v)
                        else:
                            self.settings[k] = v
            except Exception as e:
                print(f"Failed to load settings.json: {e}")

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings.json: {e}")

    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def update(self, new_dict: Dict[str, Any]):
        for k, v in new_dict.items():
            if isinstance(v, dict) and k in self.settings and isinstance(self.settings[k], dict):
                self.settings[k].update(v)
            else:
                self.settings[k] = v
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return self.settings.copy()

    def get_theme(self) -> dict:
        t_key = self.settings.get("overlay_theme", "ice_blue")
        return THEMES.get(t_key, THEMES["ice_blue"])
