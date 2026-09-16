"""
Real-time Performance Visualizer module for Legion Performance & FPS Monitor.
Renders smooth, high-performance Canvas line graphs for:
1. Full Dashboard Graphs: Clock Speed, FPS & Consistency, Temperatures, Load & Network.
2. MiniSparkline: Ultra-lightweight inline mini-graphs directly embedded in Overlay.
"""

import tkinter as tk
from typing import List, Tuple, Optional


def _get_area_color(hex_color: str) -> str:
    """Returns a rich, subtle dark tint corresponding to the line color for area fill."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            dark_r = int(r * 0.16 + 0x12 * 0.84)
            dark_g = int(g * 0.16 + 0x16 * 0.84)
            dark_b = int(b * 0.16 + 0x1f * 0.84)
            return f"#{dark_r:02x}{dark_g:02x}{dark_b:02x}"
        except Exception:
            pass
    return "#151b27"


def _get_glow_color(hex_color: str) -> str:
    """Returns a darker, saturated halo color for neon glow behind the line."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            glow_r = int(r * 0.35 + 0x12 * 0.65)
            glow_g = int(g * 0.35 + 0x16 * 0.65)
            glow_b = int(b * 0.35 + 0x1f * 0.65)
            return f"#{glow_r:02x}{glow_g:02x}{glow_b:02x}"
        except Exception:
            pass
def generate_catmull_rom_spline(
    pts: List[Tuple[float, float]],
    steps: int = 10,
    min_y: float = None,
    max_y: float = None
) -> List[float]:
    """
    Interpolates 2D points using a smooth Catmull-Rom Spline.
    Guarantees the curve passes strictly through every data point with C1 continuity,
    producing beautiful, organic, rounded curves (Apple Health / Activity Monitor style).
    """
    if not pts:
        return []
    if len(pts) == 1:
        return [pts[0][0], pts[0][1]]
    if len(pts) == 2:
        return [pts[0][0], pts[0][1], pts[1][0], pts[1][1]]

    # Pad start and end with mirrored virtual points to close interpolation
    p0 = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
    pn = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
    padded = [p0] + pts + [pn]

    curve = []
    for i in range(1, len(padded) - 2):
        p_0, p_1, p_2, p_3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
        for step in range(steps):
            t = step / float(steps)
            t2 = t * t
            t3 = t2 * t
            # Catmull-Rom formulation (tension = 0.5)
            x = 0.5 * (
                (2 * p_1[0]) +
                (-p_0[0] + p_2[0]) * t +
                (2 * p_0[0] - 5 * p_1[0] + 4 * p_2[0] - p_3[0]) * t2 +
                (-p_0[0] + 3 * p_1[0] - 3 * p_2[0] + p_3[0]) * t3
            )
            y = 0.5 * (
                (2 * p_1[1]) +
                (-p_0[1] + p_2[1]) * t +
                (2 * p_0[1] - 5 * p_1[1] + 4 * p_2[1] - p_3[1]) * t2 +
                (-p_0[1] + 3 * p_1[1] - 3 * p_2[1] + p_3[1]) * t3
            )
            if min_y is not None:
                y = max(min_y, y)
            if max_y is not None:
                y = min(max_y, y)
            curve.extend([x, y])

    # Append exact final point
    final_y = pts[-1][1]
    if min_y is not None:
        final_y = max(min_y, final_y)
    if max_y is not None:
        final_y = min(max_y, final_y)
    curve.extend([pts[-1][0], final_y])
    return curve


class MiniSparkline(tk.Canvas):
    """Ultra-compact inline sparkline canvas for Overlay HUD."""
    def __init__(
        self,
        parent,
        width=65,
        height=18,
        line_color="#58a6ff",
        bg_color="#12161f",
        border_color="#21262d",
        y_min=0.0,
        y_max=0.0,  # 0 = auto scale
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground=border_color,
            **kwargs
        )
        self.w = width
        self.h = height
        self.line_color = line_color
        self.bg_color = bg_color
        self.y_min = y_min
        self.y_max = y_max
        self.is_interactive = False  # Allows drag through in overlay

    def update_data(self, data: List[float], min_val: float = None, max_val: float = None):
        """Redraw mini sparkline with latest values."""
        self.delete("all")
        if not data or len(data) < 2:
            mid_y = self.h // 2
            self.create_line(3, mid_y, self.w - 3, mid_y, fill="#21262d", dash=(2, 2))
            return

        clean_data = [float(v) for v in data if v is not None]
        if len(clean_data) < 2:
            return

        curr_min = self.y_min if min_val is None else min_val
        curr_max = self.y_max if max_val is None else max_val

        d_min = min(clean_data)
        d_max = max(clean_data)

        if curr_max == 0 or curr_max is None:
            curr_max = max(1.0, d_max * 1.1)
            curr_min = max(0.0, d_min * 0.9)
        elif curr_max <= curr_min:
            curr_max = curr_min + 1.0

        y_range = max(1.0, curr_max - curr_min)
        pad_x = 2
        pad_y = 2
        plot_w = max(10, self.w - pad_x * 2)
        plot_h = max(6, self.h - pad_y * 2)

        n = len(clean_data)
        dx = plot_w / max(1, n - 1)

        points = []
        for i, val in enumerate(clean_data):
            px = pad_x + i * dx
            clamped_v = max(curr_min, min(curr_max, val))
            py = pad_y + plot_h - ((clamped_v - curr_min) / y_range) * plot_h
            points.extend([px, py])

        if len(points) >= 4:
            self.create_line(
                points,
                fill=self.line_color,
                width=1.5,
                smooth=True
            )
            last_x = points[-2]
            last_y = points[-1]
            self.create_oval(
                last_x - 2, last_y - 2, last_x + 2, last_y + 2,
                fill=self.line_color, outline="#ffffff", width=1
            )


class DeckSparkline(tk.Canvas):
    """Clear, legible sparkline card for the Bottom Graph Deck of the Overlay HUD."""
    def __init__(
        self,
        parent,
        width=175,
        height=62,
        title="FPS",
        y_unit="FPS",
        y_min=0.0,
        y_max=0.0,
        series_config: List[Tuple[str, str]] = None,
        bg_color="#131722",
        border_color="#242b3d",
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground=border_color,
            **kwargs
        )
        self.w = width
        self.h = height
        self.title = title
        self.y_unit = y_unit
        self.y_min = y_min
        self.y_max = y_max
        self.bg_color = bg_color
        self.border_color = border_color
        self.series_config = series_config if series_config else [("Value", "#58a6ff")]
        self.is_interactive = False

        self._last_series_data = None
        self._last_current_val_str = ""
        self._last_val_color = None
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        if event.width > 50 and event.width != self.w:
            self.w = event.width
            if self._last_series_data is not None:
                self.update_data(self._last_series_data, self._last_current_val_str, self._last_val_color)
        if event.height > 20:
            self.h = event.height

    def update_data(self, series_data: List[List[float]], current_val_str: str = "", val_color: str = None):
        self.delete("all")
        self._last_series_data = series_data
        self._last_current_val_str = current_val_str
        self._last_val_color = val_color

        curr_w = self.winfo_width()
        if curr_w > 50:
            self.w = curr_w

        # 1. Header (Title & current val with dynamic anti-collision clearance)
        v_color = val_color if val_color else self.series_config[0][1]
        max_title_x = self.w - 8

        if current_val_str:
            v_id = self.create_text(
                self.w - 6, 9,
                text=current_val_str,
                font=("Segoe UI", 8, "bold"),
                fill=v_color,
                anchor="e"
            )
            v_bbox = self.bbox(v_id)
            if v_bbox:
                max_title_x = v_bbox[0] - 8

        # Draw title with anti-collision truncation if needed
        display_title = self.title
        t_id = self.create_text(
            6, 9,
            text=display_title,
            font=("Segoe UI", 8, "bold"),
            fill="#8b949e",
            anchor="w"
        )
        t_bbox = self.bbox(t_id)

        if t_bbox and t_bbox[2] > max_title_x:
            chars = list(self.title)
            while len(chars) > 2 and t_bbox and t_bbox[2] > max_title_x:
                chars.pop()
                self.itemconfig(t_id, text="".join(chars).rstrip() + "..")
                t_bbox = self.bbox(t_id)
            if t_bbox and t_bbox[2] > max_title_x:
                self.delete(t_id)

        # 2. Dynamic Y Scale
        all_vals = []
        for s in series_data:
            all_vals.extend([float(v) for v in s if v is not None])

        curr_min = self.y_min
        curr_max = self.y_max
        if all_vals:
            data_max = max(all_vals)
            data_min = min(all_vals)
            if self.y_max == 0:
                curr_max = max(10.0, data_max * 1.15)
                curr_min = max(0.0, data_min * 0.85)
        elif curr_max == 0:
            curr_max = 100.0

        y_range = max(1.0, curr_max - curr_min)
        pad_top = 20
        pad_bot = 6
        pad_left = 6
        pad_right = 6
        plot_w = self.w - pad_left - pad_right
        plot_h = self.h - pad_top - pad_bot

        # Background midline
        mid_y = pad_top + plot_h / 2
        self.create_line(pad_left, mid_y, self.w - pad_right, mid_y, fill="#1c2333", dash=(2, 3))

        # 3. Draw each series
        for s_idx, data in enumerate(series_data):
            if s_idx >= len(self.series_config):
                break
            clean_data = [float(v) for v in data if v is not None]
            if len(clean_data) < 2:
                continue

            name, color = self.series_config[s_idx]
            n = len(clean_data)
            dx = plot_w / max(1, n - 1)

            raw_pts = []
            for i, val in enumerate(clean_data):
                px = pad_left + i * dx
                clamped_v = max(curr_min, min(curr_max, val))
                py = pad_top + plot_h - ((clamped_v - curr_min) / y_range) * plot_h
                raw_pts.append((px, py))

            if len(raw_pts) >= 2:
                curve_pts = generate_catmull_rom_spline(
                    raw_pts, steps=8,
                    min_y=pad_top - 2, max_y=pad_top + plot_h + 2
                )
                # Soft Area fill under smooth curve
                poly_pts = [curve_pts[0], pad_top + plot_h] + curve_pts + [curve_pts[-2], pad_top + plot_h]
                self.create_polygon(poly_pts, fill=_get_area_color(color), outline="")
                # Crisp smooth rounded line
                self.create_line(curve_pts, fill=color, width=2.0, joinstyle="round", capstyle="round")
                last_x = raw_pts[-1][0]
                last_y = raw_pts[-1][1]
                self.create_oval(last_x - 3, last_y - 3, last_x + 3, last_y + 3, fill=color, outline="#ffffff", width=1)


class SparklineGraph(tk.Canvas):
    def __init__(
        self,
        parent,
        width=840,
        height=150,
        title="Biểu đồ hiệu năng",
        y_unit="MHz",
        y_min=0,
        y_max=5000,
        y_steps=4,
        bg_color="#12161f",
        grid_color="#1e2533",
        text_color="#8b949e",
        series_config: List[Tuple[str, str]] = None,  # [(label, color)]
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground="#222a3a",
            **kwargs
        )
        self.w = width
        self.h = height
        self.title = title
        self.y_unit = y_unit
        self.y_min = y_min
        self.y_max = y_max
        self.y_steps = y_steps
        self.bg_color = bg_color
        self.grid_color = grid_color
        self.text_color = text_color
        self.series_config = series_config if series_config else [("Series 1", "#58a6ff")]
        
        self.padding_left = 75
        self.padding_right = 16
        self.padding_top = 26
        self.padding_bottom = 20

        self._last_series_data = None
        self._last_current_vals = None
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        changed = False
        if event.width > 100 and abs(event.width - self.w) > 2:
            self.w = event.width
            changed = True
        if event.height > 50 and abs(event.height - self.h) > 2:
            self.h = event.height
            changed = True
        if changed and self._last_series_data:
            self.update_data(self._last_series_data, self._last_current_vals)

    def update_data(self, series_data: List[List[float]], current_vals: List[str] = None):
        """Redraw graph with high-definition modern telemetry styling and smooth spline curves."""
        self.delete("all")
        self._last_series_data = series_data
        self._last_current_vals = current_vals

        curr_w = self.winfo_width()
        curr_h = self.winfo_height()
        if curr_w > 100:
            self.w = curr_w
        if curr_h > 50:
            self.h = curr_h

        plot_w = self.w - self.padding_left - self.padding_right
        plot_h = self.h - self.padding_top - self.padding_bottom
        bottom_y = self.padding_top + plot_h

        # 1. Badges & Header
        legend_x = self.w - self.padding_right
        if current_vals:
            for i in reversed(range(len(self.series_config))):
                if i < len(current_vals) and i < len(self.series_config):
                    name, color = self.series_config[i]
                    val_str = current_vals[i]
                    badge_str = f"  {name}: {val_str} "
                    
                    t_id = self.create_text(
                        legend_x - 6,
                        13,
                        text=badge_str,
                        font=("Segoe UI Variable Text", 8, "bold"),
                        fill=color,
                        anchor="e"
                    )
                    bbox = self.bbox(t_id)
                    if bbox:
                        bx1 = bbox[0] - 14
                        by1 = 4
                        bx2 = bbox[2] + 4
                        by2 = by1 + 18
                        pill_id = self.create_rectangle(
                            bx1, by1, bx2, by2,
                            fill="#25252a", outline="#323238", width=1
                        )
                        dot_id = self.create_oval(
                            bx1 + 5, by1 + 6, bx1 + 11, by1 + 12,
                            fill=color, outline=""
                        )
                        self.tag_lower(pill_id, t_id)
                        self.tag_raise(dot_id, pill_id)
                        self.tag_raise(t_id, pill_id)
                        legend_x = bx1 - 8

        # Draw Title with anti-collision check against badges
        display_title = self.title
        max_title_x = legend_x - 12
        title_id = self.create_text(
            self.padding_left,
            13,
            text=display_title,
            font=("Segoe UI Variable Display", 9, "bold"),
            fill="#ffffff",
            anchor="w"
        )
        t_bbox = self.bbox(title_id)
        if t_bbox and t_bbox[2] > max_title_x:
            while len(display_title) > 3 and t_bbox and t_bbox[2] > max_title_x:
                display_title = display_title[:-2].rstrip() + ".."
                self.itemconfig(title_id, text=display_title)
                t_bbox = self.bbox(title_id)

        # 2. Dynamic Y Scale
        all_vals = []
        for s in series_data:
            all_vals.extend([float(v) for v in s if v is not None])

        curr_min = self.y_min
        curr_max = self.y_max
        if all_vals:
            data_max = max(all_vals)
            data_min = min(all_vals)
            if self.y_max == 0:  # Auto-scale
                curr_max = max(10.0, data_max * 1.15)
                curr_min = max(0.0, data_min * 0.85)

        y_range = max(1.0, curr_max - curr_min)

        # 3. Grid lines & Time divisions (Oscilloscope grid)
        # Vertical time division marks
        for t_step in [1, 2, 3]:
            gx = self.padding_left + (plot_w / 4) * t_step
            self.create_line(gx, self.padding_top, gx, bottom_y, fill="#222226", dash=(1, 5))

        # Horizontal Grid lines & Y-axis labels
        steps = getattr(self, "y_steps", 4)
        for i in range(steps + 1):
            y_val = curr_min + (y_range / steps) * i
            py = bottom_y - (i / steps) * plot_h
            # Grid line
            self.create_line(
                self.padding_left, py, self.w - self.padding_right, py,
                fill="#242428", dash=(2, 4)
            )
            # Label
            lbl_str = f"{int(round(y_val))}" if curr_max > 10 else f"{y_val:.1f}"
            self.create_text(
                self.padding_left - 10, py,
                text=f"{lbl_str} {self.y_unit}",
                font=("Segoe UI Variable Text", 8),
                fill=self.text_color,
                anchor="e"
            )

        # 4. Plot each data series with smooth Catmull-Rom Spline curves
        prepared_series = []
        for s_idx, data in enumerate(series_data):
            if s_idx >= len(self.series_config):
                break
            clean_pts = [float(v) for v in data if v is not None]
            if len(clean_pts) < 2:
                continue

            name, color = self.series_config[s_idx]
            n_points = len(clean_pts)
            dx = plot_w / max(1, n_points - 1)

            raw_points = []
            for i, val in enumerate(clean_pts):
                px = self.padding_left + i * dx
                clamped_v = max(curr_min, min(curr_max, val))
                py = self.padding_top + plot_h - ((clamped_v - curr_min) / y_range) * plot_h
                raw_points.append((px, py))

            if len(raw_points) >= 2:
                curve_points = generate_catmull_rom_spline(
                    raw_points, steps=10,
                    min_y=self.padding_top - 2,
                    max_y=bottom_y + 2
                )
                prepared_series.append((color, curve_points, raw_points[-1]))

        # 4a. Layer 1: Soft Area Fills under smooth curves
        for color, curve, last_pt in prepared_series:
            poly_pts = [curve[0], bottom_y] + curve + [curve[-2], bottom_y]
            self.create_polygon(poly_pts, fill=_get_area_color(color), outline="")

        # 4b. Layer 2: Subtle Neon Glow Halo line
        for color, curve, last_pt in prepared_series:
            self.create_line(
                curve,
                fill=_get_glow_color(color),
                width=4.5,
                joinstyle="round",
                capstyle="round"
            )

        # 4c. Layer 3: Main Crisp High-Definition Line
        for color, curve, last_pt in prepared_series:
            self.create_line(
                curve,
                fill=color,
                width=2.2,
                joinstyle="round",
                capstyle="round"
            )

            # Live Target Marker (Oscilloscope timehead) at latest point
            last_x, last_y = last_pt
            
            # Subtle vertical scanline guide
            self.create_line(last_x, self.padding_top, last_x, bottom_y, fill=color, dash=(1, 4))

            # Outer glow ring
            self.create_oval(
                last_x - 5, last_y - 5, last_x + 5, last_y + 5,
                fill="", outline=color, width=1.5
            )
            # Inner white bright core
            self.create_oval(
                last_x - 2.5, last_y - 2.5, last_x + 2.5, last_y + 2.5,
                fill="#ffffff", outline=color, width=1
            )
