"""
Circular Gauge Widget - Apple Activity Ring & Minimalist Telemetry Style.
Features:
- High-resolution antialiased circular track with Apple Dark Mode aesthetics.
- Crisp typography: Prominent value with uppercase subtle subtitle.
- Pure minimalist presentation: Zero cluttered clipart/emojis.
"""

import math
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk


class CircularGauge(tk.Canvas):
    def __init__(
        self,
        parent,
        size=160,
        track_color="#28282e",
        arc_color="#30D158",
        bg_color="#1c1c1e",
        text_color="#ffffff",
        subtext_color="#86868b",
        unit="°C",
        subtitle="NHIỆT ĐỘ",
        max_val=100.0,
        icon_type=None,
        **kwargs
    ):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.track_color = track_color
        self.arc_color = arc_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.subtext_color = subtext_color
        self.unit = unit
        self.subtitle = subtitle if subtitle else unit
        self.max_val = max_val
        
        self.current_val = 0.0
        self._image_tk = None
        self._scale = 3  # 3x supersampling for high DPI antialiasing
        
        self.update_value(0.0)

    def resize(self, new_size: int):
        """Dynamically resize gauge diameter and re-render."""
        new_size = max(130, min(280, int(new_size)))
        if abs(self.size - new_size) >= 4:
            self.size = new_size
            self.config(width=new_size, height=new_size)
            self.update_value(self.current_val)

    def set_arc_color(self, color: str):
        self.arc_color = color

    def update_value(self, val: float, custom_text: str = None):
        self.current_val = val
        ratio = max(0.0, min(1.0, val / self.max_val if self.max_val > 0 else 0.0))
        
        # Canvas dimensions
        w = self.size * self._scale
        h = self.size * self._scale
        
        img = Image.new("RGBA", (w, h), self.bg_color)
        draw = ImageDraw.Draw(img)

        padding = int(14 * self._scale * (self.size / 160.0))
        stroke_width = int(9.0 * self._scale * (self.size / 160.0))
        box = [padding, padding, w - padding, h - padding]
        cx = w / 2
        cy = h / 2
        radius = (w - padding * 2) / 2

        # 1. Background Track (Apple dark track ring)
        draw.ellipse(box, outline=self.track_color, width=stroke_width)

        # 2. Progress Arc (Clockwise from top 12 o'clock)
        start_angle = -90
        extent = ratio * 360
        if extent > 0.5:
            draw.arc(box, start=start_angle, end=start_angle + extent, fill=self.arc_color, width=stroke_width)
            
            # Rounded end cap at tip of arc
            rad_end = math.radians(start_angle + extent)
            end_x = cx + radius * math.cos(rad_end)
            end_y = cy + radius * math.sin(rad_end)
            r_cap = stroke_width / 2.0
            draw.ellipse([end_x - r_cap, end_y - r_cap, end_x + r_cap, end_y + r_cap], fill=self.arc_color)

            # Rounded start cap at top
            start_x = cx
            start_y = cy - radius
            draw.ellipse([start_x - r_cap, start_y - r_cap, start_x + r_cap, start_y + r_cap], fill=self.arc_color)

        # Downsample using high quality Lanczos filter
        img_smooth = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
        self._image_tk = ImageTk.PhotoImage(img_smooth)
        self.delete("all")
        self.create_image(0, 0, anchor="nw", image=self._image_tk)

        # 3. Apple Minimalist Typography in Center (Proportionally Scaled)
        if custom_text is not None:
            num_str = custom_text
            sub_label = ""
        else:
            if self.unit == "FPS":
                num_str = f"{int(val)}" if val > 0 else "--"
                sub_label = "FPS"
            elif self.unit == "°C":
                num_str = f"{int(val)}°"
                sub_label = "CELSIUS"
            elif self.unit == "%":
                num_str = f"{int(val)}%"
                sub_label = "TẢI SỬ DỤNG"
            elif self.unit == "ms":
                num_str = f"{val:.1f}"
                sub_label = "MS LATENCY"
            else:
                num_str = f"{val:.0f}"
                sub_label = self.unit.upper()

        center_y = self.size / 2
        val_font_size = max(16, int(self.size * 0.135))
        sub_font_size = max(7, int(self.size * 0.052))
        offset_y = int(self.size * 0.04)

        if sub_label:
            # Value (Bold, prominent)
            self.create_text(
                self.size / 2,
                center_y - offset_y,
                text=num_str,
                font=("Segoe UI Variable Display", val_font_size, "bold"),
                fill=self.text_color
            )
            # Subtle uppercase label
            self.create_text(
                self.size / 2,
                center_y + int(self.size * 0.11),
                text=sub_label,
                font=("Segoe UI Variable Text", sub_font_size, "bold"),
                fill=self.subtext_color
            )
        else:
            self.create_text(
                self.size / 2,
                center_y,
                text=num_str,
                font=("Segoe UI Variable Display", int(val_font_size * 0.85), "bold"),
                fill=self.text_color
            )
