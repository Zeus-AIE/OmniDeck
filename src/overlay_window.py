"""
Customizable In-Game / Desktop Overlay Window (v2.4.2 PRO).
Features:
- Hybrid Gaming x Apple Modern Minimalist Design: Ultra-sleek, luxurious dark glassmorphism.
- 4 Responsive Layouts (Horizontal Bar, Compact Pill, Corner Gaming Card, Vertical Dock).
- 100% Full Metric Toggle Compliance across ALL layouts (FPS, 1% Low, Frametime, CPU, GPU, RAM, Net, Fan).
- Accurate Dynamic Auto-Fit with zero coordinate drifting.
- Dual Independent Transparency Sliders: Background Opacity (0% - 100%) and Text/Indicator Opacity (20% - 100%).
- Win32 Topmost Z-Order Anchoring: Background canvas pinned directly behind foreground HUD.
- Full Click-Through Passthrough (WS_EX_TRANSPARENT / F8) and Global Hotkeys (F9, F10).
"""

import ctypes
from ctypes import wintypes
import tkinter as tk
from settings_manager import THEMES, SettingsManager
from visualizer import DeckSparkline

CHROMA_KEY = "#000001"  # Invisible chroma key on Windows

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002

user32 = ctypes.windll.user32


def get_fps_color(fps: float) -> str:
    """Threshold color for FPS."""
    if fps <= 0:
        return "#8b949e"
    if fps >= 60:
        return "#30D158"  # Good (Apple Green)
    if fps >= 30:
        return "#FF9F0A"  # Warning (Amber)
    return "#FF453A"      # Critical (Red)


def get_low_fps_color(low: float) -> str:
    """Threshold color for 1% Low FPS."""
    if low <= 0:
        return "#8b949e"
    if low >= 50:
        return "#30D158"
    if low >= 25:
        return "#FF9F0A"
    return "#FF453A"


def get_frametime_color(ft: float) -> str:
    """Threshold color for Frametime in ms."""
    if ft <= 0:
        return "#8b949e"
    if ft <= 16.7:
        return "#30D158"
    if ft <= 33.3:
        return "#FF9F0A"
    return "#FF453A"


def get_cpu_temp_color(temp: float) -> str:
    """Threshold color for CPU Temperature."""
    if temp < 75:
        return "#30D158"
    if temp < 85:
        return "#FF9F0A"
    return "#FF453A"


def get_cpu_usage_color(usage: float) -> str:
    """Threshold color for CPU Usage."""
    if usage < 70:
        return "#0A84FF"
    if usage < 90:
        return "#FF9F0A"
    return "#FF453A"


def get_gpu_temp_color(temp: float) -> str:
    """Threshold color for GPU Temperature."""
    if temp < 70:
        return "#30D158"
    if temp < 81:
        return "#FF9F0A"
    return "#FF453A"


def get_gpu_usage_color(usage: float) -> str:
    """Threshold color for GPU Usage."""
    if usage < 70:
        return "#0A84FF"
    if usage < 92:
        return "#30D158"
    return "#FF9F0A"


def get_ram_color(pct: float) -> str:
    """Threshold color for RAM Usage."""
    if pct < 75:
        return "#BF5AF2"  # Apple Purple
    if pct < 88:
        return "#FF9F0A"
    return "#FF453A"


def get_fan_color(rpm: int) -> str:
    """Threshold color for Fan RPM."""
    if rpm < 2200:
        return "#30D158"  # Quiet (Apple Green)
    if rpm < 3500:
        return "#0A84FF"  # Balanced (Apple Blue)
    if rpm < 4200:
        return "#FF9F0A"  # Performance (Apple Orange)
    return "#FF453A"      # Turbo (Apple Red)


class InGameOverlay(tk.Toplevel):
    def __init__(
        self,
        master=None,
        settings_mgr: SettingsManager = None,
        on_close_callback=None,
        on_open_dashboard_callback=None
    ):
        super().__init__(master)

        self.master_app = master
        self.settings_mgr = settings_mgr
        self.on_close_callback = on_close_callback
        self.on_open_dashboard_callback = on_open_dashboard_callback

        self.title("Legion Monitor Overlay")
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Pinned Coordinates & Dimensions
        saved_pos = self.settings_mgr.get("overlay_position", {"x": 100, "y": 20}) if self.settings_mgr else {"x": 100, "y": 20}
        self.current_x = saved_pos.get("x", 100)
        self.current_y = saved_pos.get("y", 20)
        self.current_w = self.settings_mgr.get("overlay_manual_width", 1080) if self.settings_mgr else 1080
        self.current_h = 38

        self._drag_x = 0
        self._drag_y = 0
        self._resize_start_x = 0
        self._resize_start_w = 0

        # Backdrop Layer Window for Independent Background Opacity
        self.bg_win = tk.Toplevel(master)
        self.bg_win.title("Legion Overlay Backdrop")
        self.bg_win.overrideredirect(True)
        self.bg_win.attributes("-topmost", True)
        self.bg_win.attributes("-transparentcolor", CHROMA_KEY)
        self.bg_win.config(bg=CHROMA_KEY)
        self._setup_bg_win_styles()

        # Transparency Settings
        self.bg_modes = ["badges", "transparent", "solid"]
        self.bg_mode = self.settings_mgr.get("overlay_bg_mode", "badges") if self.settings_mgr else "badges"
        if self.bg_mode not in self.bg_modes:
            self.bg_mode = "badges"

        self.bg_transparency_pct = self.settings_mgr.get("overlay_bg_transparency_pct", 65) if self.settings_mgr else 65
        self.text_transparency_pct = self.settings_mgr.get("overlay_text_transparency_pct", 100) if self.settings_mgr else 100
        self.transparency_pct = self.bg_transparency_pct

        # Click-Through (Mouse Passthrough) State
        self.click_through = self.settings_mgr.get("overlay_click_through", False) if self.settings_mgr else False

        # Bottom Graph Deck
        self.show_deck = self.settings_mgr.get("overlay_show_bottom_graphs", True) if self.settings_mgr else True

        # UI elements cache
        self.labels = {}
        self.deck_graphs = {}

        self.apply_settings()

    def _setup_bg_win_styles(self):
        try:
            self.update_idletasks()
            hwnd_bg = ctypes.windll.user32.GetParent(self.bg_win.winfo_id())
            target = hwnd_bg if hwnd_bg else self.bg_win.winfo_id()
            style = user32.GetWindowLongW(target, GWL_EXSTYLE)
            user32.SetWindowLongW(target, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED | 0x00000080)
        except Exception:
            pass

    def _sync_bg_win(self):
        """Positions and sizes the backdrop window strictly behind the foreground window."""
        if not hasattr(self, "bg_win") or not self.bg_win or not self.bg_win.winfo_exists():
            return
        if self.bg_transparency_pct <= 0:
            self.bg_win.withdraw()
            return

        # Ensure background UI frames exist
        if len(self.bg_win.winfo_children()) == 0:
            self._build_bg_ui()

        geo = f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}"
        self.bg_win.geometry(geo)
        bg_alpha = max(0.05, min(1.0, self.bg_transparency_pct / 100.0))
        self.bg_win.attributes("-alpha", bg_alpha)

        if self.winfo_viewable():
            self.bg_win.deiconify()
            try:
                hwnd_fg = user32.GetParent(self.winfo_id()) or self.winfo_id()
                hwnd_bg = user32.GetParent(self.bg_win.winfo_id()) or self.bg_win.winfo_id()
                # Pin hwnd_bg directly behind hwnd_fg without taking focus
                user32.SetWindowPos(
                    hwnd_bg, hwnd_fg,
                    self.current_x, self.current_y, self.current_w, self.current_h,
                    SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
            except Exception:
                self.bg_win.lower(self)

    def withdraw(self):
        super().withdraw()
        if hasattr(self, "bg_win") and self.bg_win and self.bg_win.winfo_exists():
            self.bg_win.withdraw()

    def deiconify(self):
        super().deiconify()
        self._sync_bg_win()
        self.lift()

    def lift(self, aboveThis=None):
        if hasattr(self, "bg_win") and self.bg_win and self.bg_win.winfo_exists():
            if self.bg_transparency_pct > 0:
                self.bg_win.lift()
        super().lift(aboveThis)

    def destroy(self):
        if hasattr(self, "bg_win") and self.bg_win and self.bg_win.winfo_exists():
            try:
                self.bg_win.destroy()
            except Exception:
                pass
        super().destroy()

    def apply_settings(self, force_rebuild=False):
        """Rebuild or reconfigure overlay according to latest settings."""
        settings = self.settings_mgr.settings if self.settings_mgr else {}
        new_layout_mode = settings.get("overlay_layout", "horizontal")
        new_theme_key = settings.get("overlay_theme", "apple_dark")
        new_scale_mode = settings.get("overlay_scale", "medium")
        new_bg_mode = settings.get("overlay_bg_mode", "badges")
        new_show_deck = settings.get("overlay_show_bottom_graphs", True)
        new_metrics = settings.get("metrics", {})
        new_deck_cfg = settings.get("overlay_bottom_graphs", {})
        new_width_mode = settings.get("overlay_width_mode", "auto")
        new_manual_w = settings.get("overlay_manual_width", 1080)
        new_fan_mode = settings.get("overlay_fan_mode", "dual")

        # Check structural rebuild need
        needs_rebuild = force_rebuild or (
            new_layout_mode != getattr(self, "layout_mode", None) or
            new_theme_key != getattr(self, "theme_key", None) or
            new_scale_mode != getattr(self, "scale_mode", None) or
            new_bg_mode != getattr(self, "bg_mode", None) or
            new_show_deck != getattr(self, "show_deck", None) or
            new_metrics != getattr(self, "_last_metrics", None) or
            new_deck_cfg != getattr(self, "_last_deck_cfg", None) or
            new_width_mode != getattr(self, "_last_width_mode", None) or
            new_fan_mode != getattr(self, "_last_fan_mode", None)
        )
        self._last_fan_mode = new_fan_mode

        self.layout_mode = new_layout_mode
        self.theme_key = new_theme_key
        self.scale_mode = new_scale_mode
        self.theme = THEMES.get(self.theme_key, THEMES["apple_dark"])
        self.bg_mode = new_bg_mode
        self.show_deck = new_show_deck
        self._last_metrics = new_metrics.copy()
        self._last_deck_cfg = new_deck_cfg.copy()
        self._last_width_mode = new_width_mode

        self.bg_transparency_pct = settings.get("overlay_bg_transparency_pct", 65)
        self.text_transparency_pct = settings.get("overlay_text_transparency_pct", 100)
        self.transparency_pct = self.bg_transparency_pct
        self.click_through = settings.get("overlay_click_through", self.click_through)

        # Harmonize bg_mode with bg_transparency_pct (0% is transparent, >=95% is solid, in-between is glass/badges)
        if self.bg_transparency_pct <= 0:
            self.bg_mode = "transparent"
        elif self.bg_transparency_pct >= 95:
            self.bg_mode = "solid"
        else:
            self.bg_mode = "badges"

        # Configure foreground window transparency (text, numbers, charts)
        self.attributes("-transparentcolor", CHROMA_KEY)
        self.config(bg=CHROMA_KEY)
        text_alpha = max(0.20, min(1.0, self.text_transparency_pct / 100.0))
        self.attributes("-alpha", text_alpha)

        if needs_rebuild:
            if self.scale_mode == "small":
                self.scale = 0.85
                self.base_font_size = 8
                self.big_font_size = 10
            elif self.scale_mode == "large":
                self.scale = 1.2
                self.base_font_size = 10
                self.big_font_size = 13
            else:
                self.scale = 1.0
                self.base_font_size = 9
                self.big_font_size = 11

            self._build_ui()
            self._build_bg_ui()
            self._bind_mouse()
        else:
            if new_width_mode == "manual" and self.layout_mode == "horizontal":
                self.current_w = max(380, new_manual_w)
                self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")

        self._sync_bg_win()
        self.set_click_through(self.click_through, update_settings=False)

    def _get_bg_colors(self):
        """Return (window_bg, bar_bg, badge_bg, border_color) for foreground overlay."""
        border_color = self.theme.get("border", "#323238")
        return CHROMA_KEY, CHROMA_KEY, CHROMA_KEY, border_color

    def _build_bg_ui(self):
        """Build backdrop layer frames matching overlay geometry."""
        if not hasattr(self, "bg_win") or not self.bg_win or not self.bg_win.winfo_exists():
            return
        for w in list(self.bg_win.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass
        self.bg_bar = None
        self.bg_deck = None

        bar_bg_color = self.theme.get("bg", "#14151a")

        bg_main = tk.Frame(self.bg_win, bg=CHROMA_KEY)
        bg_main.pack(fill="both", expand=True)

        if self.layout_mode == "horizontal":
            bar_w = getattr(self, "bar_frame", None)
            top_h = max(int(34 * self.scale), bar_w.winfo_reqheight() if (bar_w and bar_w.winfo_exists()) else int(34 * self.scale))
            if not self.show_deck:
                self.bg_bar = tk.Frame(
                    bg_main,
                    bg=bar_bg_color,
                    padx=int(6 * self.scale),
                    pady=int(3 * self.scale)
                )
                self.bg_bar.pack(fill="both", expand=True)
            else:
                self.bg_bar = tk.Frame(
                    bg_main,
                    bg=bar_bg_color,
                    padx=int(6 * self.scale),
                    pady=int(3 * self.scale),
                    height=top_h
                )
                self.bg_bar.pack_propagate(False)
                self.bg_bar.pack(fill="x", side="top")

                deck_cfg = self.settings_mgr.get("overlay_bottom_graphs", {}) if self.settings_mgr else {}
                active_count = sum(1 for k in ['fps', 'cpu', 'gpu', 'ram_net', 'fan'] if deck_cfg.get(k, True))
                if active_count > 0:
                    deck_h = int(62 * self.scale) + int(8 * self.scale)
                    self.bg_deck = tk.Frame(
                        bg_main,
                        bg=CHROMA_KEY,
                        pady=int(3 * self.scale),
                        height=deck_h
                    )
                    self.bg_deck.pack_propagate(False)
                    self.bg_deck.pack(fill="x", side="top")

                    target_w = max(380, self.current_w)
                    card_w = max(int(140 * self.scale), int((target_w - 24) / max(1, active_count)))
                    card_h = int(62 * self.scale)

                    for k in ['fps', 'cpu', 'gpu', 'ram_net', 'fan']:
                        if deck_cfg.get(k, True):
                            card_bg = tk.Frame(
                                self.bg_deck,
                                bg=bar_bg_color,
                                height=card_h,
                                width=card_w
                            )
                            card_bg.pack_propagate(False)
                            card_bg.pack(side="left", padx=int(3 * self.scale), fill="both", expand=True)
        else:
            # Compact / Corner / Vertical: Backdrop covers container exactly
            bg_container = tk.Frame(bg_main, bg=bar_bg_color)
            bg_container.pack(fill="both", expand=True)

        if self.bg_transparency_pct <= 0:
            self.bg_win.withdraw()
        else:
            self._sync_bg_win()

    def _build_ui(self):
        for w in list(self.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass
        self.labels.clear()
        self.deck_graphs.clear()
        self.lbl_lock = None
        self.btn_menu = None
        self.bar_frame = None
        self.deck_frame = None
        self.main_frame = None
        self.container = None

        metrics = self.settings_mgr.get("metrics", {}) if self.settings_mgr else {}
        deck_cfg = self.settings_mgr.get("overlay_bottom_graphs", {}) if self.settings_mgr else {}

        if self.layout_mode == "horizontal":
            self._build_horizontal_layout(metrics, deck_cfg)
        elif self.layout_mode == "compact":
            self._build_compact_layout(metrics, deck_cfg)
        elif self.layout_mode == "corner":
            self._build_corner_layout(metrics, deck_cfg)
        elif self.layout_mode == "vertical":
            self._build_vertical_layout(metrics, deck_cfg)
        else:
            self._build_horizontal_layout(metrics, deck_cfg)

    def _on_close_clicked(self, event=None):
        self.withdraw()
        if self.on_close_callback and callable(self.on_close_callback):
            self.on_close_callback()

    def _open_main_dashboard(self, event=None):
        if self.on_open_dashboard_callback and callable(self.on_open_dashboard_callback):
            self.on_open_dashboard_callback()
        elif self.master_app:
            self.master_app.deiconify()
            self.master_app.state("normal")
            self.master_app.lift()
            self.master_app.focus_force()

    def _toggle_bottom_deck(self, event=None):
        self.show_deck = not self.show_deck
        if self.settings_mgr:
            self.settings_mgr.set("overlay_show_bottom_graphs", self.show_deck)
        self.apply_settings()

    def cycle_transparency(self, event=None):
        """Cycle through background transparency levels [F10]: 0% -> 35% -> 65% -> 90%."""
        levels = [0, 35, 65, 90]
        curr = self.bg_transparency_pct
        next_lvl = levels[0]
        for idx, lvl in enumerate(levels):
            if curr <= lvl:
                next_lvl = levels[(idx + 1) % len(levels)]
                break
        else:
            next_lvl = levels[0]
        self.set_bg_transparency_pct(next_lvl)

    def set_bg_mode(self, mode: str):
        if mode in self.bg_modes:
            self.bg_mode = mode
            if self.settings_mgr:
                self.settings_mgr.set("overlay_bg_mode", mode)
            if mode == "transparent":
                self.set_bg_transparency_pct(0)
            elif mode == "solid":
                self.set_bg_transparency_pct(100)
            else:
                self.set_bg_transparency_pct(65)
            self.apply_settings()

    def set_bg_transparency_pct(self, pct: int):
        """Thread-safe background transparency update."""
        self.bg_transparency_pct = max(0, min(100, int(pct)))
        self.transparency_pct = self.bg_transparency_pct
        self.bg_mode = "transparent" if self.bg_transparency_pct <= 0 else ("solid" if self.bg_transparency_pct >= 95 else "badges")
        if self.settings_mgr:
            self.settings_mgr.set("overlay_bg_transparency_pct", self.bg_transparency_pct)
            self.settings_mgr.set("overlay_transparency_pct", self.bg_transparency_pct)
            self.settings_mgr.set("overlay_bg_mode", self.bg_mode)

        def _do_sync():
            if hasattr(self, "bg_win") and self.bg_win and self.bg_win.winfo_exists():
                if self.bg_transparency_pct > 0 and len(self.bg_win.winfo_children()) == 0:
                    self._build_bg_ui()
                self._sync_bg_win()

        if hasattr(self, "after") and hasattr(self, "winfo_exists"):
            try:
                self.after(0, _do_sync)
            except Exception:
                _do_sync()
        else:
            _do_sync()

    def set_text_transparency_pct(self, pct: int):
        """Thread-safe text / indicator transparency update."""
        self.text_transparency_pct = max(20, min(100, int(pct)))
        if self.settings_mgr:
            self.settings_mgr.set("overlay_text_transparency_pct", self.text_transparency_pct)

        def _apply_alpha():
            alpha_val = max(0.20, min(1.0, self.text_transparency_pct / 100.0))
            self.attributes("-alpha", alpha_val)

        if hasattr(self, "after") and hasattr(self, "winfo_exists"):
            try:
                self.after(0, _apply_alpha)
            except Exception:
                _apply_alpha()
        else:
            _apply_alpha()

    def set_transparency_pct(self, pct: int):
        self.set_bg_transparency_pct(pct)

    def set_fan_mode(self, mode: str):
        """Set fan display mode: dual, max, cpu, or gpu."""
        if self.settings_mgr:
            self.settings_mgr.set("overlay_fan_mode", mode)
        self.apply_settings(force_rebuild=True)

    def set_click_through(self, enabled: bool, update_settings=True):
        """Enable or disable mouse passthrough (WS_EX_TRANSPARENT)."""
        self.click_through = enabled
        if update_settings and self.settings_mgr:
            self.settings_mgr.set("overlay_click_through", enabled)

        try:
            self.update_idletasks()
            hwnd = self.winfo_id()
            parent = user32.GetParent(hwnd)
            target_hwnd = parent if parent else hwnd

            style = user32.GetWindowLongW(target_hwnd, GWL_EXSTYLE)
            if enabled:
                user32.SetWindowLongW(target_hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
            else:
                user32.SetWindowLongW(target_hwnd, GWL_EXSTYLE, (style & ~WS_EX_TRANSPARENT) | WS_EX_LAYERED)
        except Exception:
            pass

        lbl = getattr(self, "lbl_lock", None)
        if lbl is not None:
            try:
                if lbl.winfo_exists():
                    lbl.config(text="KHÓA" if enabled else "")
            except Exception:
                pass

    def toggle_click_through(self):
        """Toggle mouse passthrough with hotkey F8 or menu."""
        self.set_click_through(not self.click_through)

    def set_width_mode(self, mode: str):
        if self.settings_mgr:
            self.settings_mgr.set("overlay_width_mode", mode)
        self.apply_settings(force_rebuild=True)

    def set_manual_width(self, w: int):
        self.current_w = max(380, w)
        if self.settings_mgr:
            self.settings_mgr.set("overlay_width_mode", "manual")
            self.settings_mgr.set("overlay_manual_width", self.current_w)
        self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")
        self._sync_bg_win()

    def _show_nav_menu(self, event):
        """Display sleek Apple macOS popup menu at button position."""
        menu = tk.Menu(
            self,
            tearoff=0,
            bg="#1c1c1e",
            fg="#f5f5f7",
            activebackground="#0A84FF",
            activeforeground="#ffffff",
            relief="flat",
            bd=1,
            font=("Segoe UI Variable Text", 9)
        )

        # 1. Deck Toggle (only available in horizontal layout)
        if self.layout_mode == "horizontal":
            deck_text = "• Khung biểu đồ dưới" if self.show_deck else "  Khung biểu đồ dưới"
            menu.add_command(label=deck_text, command=self._toggle_bottom_deck)

        # 2. Click-Through Toggle
        lock_text = "• Xuyên thấu chuột (F8)" if self.click_through else "  Xuyên thấu chuột (F8)"
        menu.add_command(label=lock_text, command=self.toggle_click_through)

        menu.add_separator()

        # 3. Background Transparency Submenu
        sub_bg = tk.Menu(menu, tearoff=0, bg="#1c1c1e", fg="#f5f5f7", activebackground="#0A84FF", activeforeground="#ffffff", relief="flat", font=("Segoe UI Variable Text", 9))
        for m_id, m_name in [("badges", "Thẻ nổi bật (Floating Pills)"), ("transparent", "Trong suốt 100% (Pure HUD)"), ("solid", "Thanh tối nguyên khối")]:
            pre = "• " if self.bg_mode == m_id else "  "
            sub_bg.add_command(label=f"{pre}{m_name}", command=lambda m=m_id: self.set_bg_mode(m))
        sub_bg.add_separator()
        for p, p_txt in [
            (0, "0% (Trong suốt hoàn toàn - Pure HUD)"),
            (35, "35% (Kính mờ nhẹ)"),
            (65, "65% (Kính mờ tiêu chuẩn)"),
            (90, "90% (Nền tối rõ)"),
            (100, "100% (Nền tối nguyên khối)")
        ]:
            pre = "• " if self.bg_transparency_pct == p else "  "
            sub_bg.add_command(label=f"{pre}{p_txt}", command=lambda pct=p: self.set_bg_transparency_pct(pct))
        menu.add_cascade(label="Độ trong suốt nền...", menu=sub_bg)

        # 4. Text / Indicator Transparency Submenu
        sub_txt = tk.Menu(menu, tearoff=0, bg="#1c1c1e", fg="#f5f5f7", activebackground="#0A84FF", activeforeground="#ffffff", relief="flat", font=("Segoe UI Variable Text", 9))
        for p, p_txt in [
            (100, "100% (Rõ nét tối đa - Mặc định)"),
            (85, "85% (Hơi mờ nhẹ)"),
            (70, "70% (Mờ vừa)"),
            (50, "50% (Mờ nhiều)"),
            (30, "30% (Rất mờ)")
        ]:
            pre = "• " if self.text_transparency_pct == p else "  "
            sub_txt.add_command(label=f"{pre}{p_txt}", command=lambda pct=p: self.set_text_transparency_pct(pct))
        menu.add_cascade(label="Độ trong suốt chữ & đồ thị...", menu=sub_txt)

        # 5. Length Submenu (only for horizontal)
        if self.layout_mode == "horizontal":
            sub_w = tk.Menu(menu, tearoff=0, bg="#1c1c1e", fg="#f5f5f7", activebackground="#0A84FF", activeforeground="#ffffff", relief="flat", font=("Segoe UI Variable Text", 9))
            is_auto = self.settings_mgr.get("overlay_width_mode", "auto") == "auto" if self.settings_mgr else True
            sub_w.add_command(label="• Tự động co giãn" if is_auto else "  Tự động co giãn", command=lambda: self.set_width_mode("auto"))
            sub_w.add_separator()
            for w_cand in [750, 900, 1080, 1250, 1450]:
                pre = "• " if not is_auto and abs(self.current_w - w_cand) < 40 else "  "
                sub_w.add_command(label=f"{pre}{w_cand} px", command=lambda w=w_cand: self.set_manual_width(w))
            menu.add_cascade(label="Chiều dài thanh...", menu=sub_w)

        # 6. Fan Mode Submenu
        sub_fan = tk.Menu(menu, tearoff=0, bg="#1c1c1e", fg="#f5f5f7", activebackground="#0A84FF", activeforeground="#ffffff", relief="flat", font=("Segoe UI Variable Text", 9))
        curr_fan_mode = self.settings_mgr.get("overlay_fan_mode", "dual") if self.settings_mgr else "dual"
        fan_modes = [
            ("dual", "Quạt kép (C: CPU · G: GPU)"),
            ("max", "Quạt quay nhanh nhất (Max RPM)"),
            ("cpu", "Chỉ hiển thị Quạt CPU"),
            ("gpu", "Chỉ hiển thị Quạt GPU")
        ]
        for f_key, f_label in fan_modes:
            pre = "• " if curr_fan_mode == f_key else "  "
            sub_fan.add_command(label=f"{pre}{f_label}", command=lambda m=f_key: self.set_fan_mode(m))
        menu.add_cascade(label="Chế độ hiển thị Quạt...", menu=sub_fan)

        menu.add_separator()
        menu.add_command(label="Mở Bảng điều khiển chính", command=self._open_main_dashboard)
        menu.add_command(label="Tắt Overlay (F9)", command=self._on_close_clicked)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_resize_start(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_w = self.winfo_width()

    def _on_resize_motion(self, event):
        dx = event.x_root - self._resize_start_x
        min_w = 380
        new_w = max(min_w, self._resize_start_w + dx)
        self.current_w = new_w
        self.geometry(f"{new_w}x{self.current_h}+{self.current_x}+{self.current_y}")
        self._sync_bg_win()
        if self.settings_mgr:
            self.settings_mgr.set("overlay_width_mode", "manual")
            self.settings_mgr.set("overlay_manual_width", new_w)

    # -------------------------------------------------------------
    # 1. HORIZONTAL LAYOUT (Thanh dài ngang chuẩn Apple x Gaming)
    # -------------------------------------------------------------
    def _build_horizontal_layout(self, metrics: dict, deck_cfg: dict):
        win_bg, bar_bg, badge_bg, border_color = self._get_bg_colors()

        self.main_frame = tk.Frame(self, bg=win_bg)
        self.main_frame.pack(fill="both", expand=True)

        self.bar_frame = tk.Frame(
            self.main_frame,
            bg=bar_bg,
            highlightbackground=border_color if self.bg_mode == "solid" else CHROMA_KEY,
            highlightthickness=1 if self.bg_mode == "solid" else 0,
            padx=int(6 * self.scale),
            pady=int(3 * self.scale)
        )
        self.bar_frame.pack(fill="x", side="top")

        def make_badge():
            f = tk.Frame(
                self.bar_frame,
                bg=badge_bg,
                highlightbackground=border_color,
                highlightthickness=1 if self.bg_mode != "transparent" else 0,
                padx=int(8 * self.scale),
                pady=int(2 * self.scale)
            )
            f.pack(side="left", padx=int(3 * self.scale))
            return f

        # A. App Name Badge
        if metrics.get("app_name", True):
            b_app = make_badge()
            self.labels["app"] = tk.Label(
                b_app,
                text="Sẵn sàng",
                font=("Segoe UI Variable Text", self.base_font_size, "bold"),
                fg=self.theme["accent"],
                bg=badge_bg
            )
            self.labels["app"].pack(side="left")

        # B. FPS Badge
        if metrics.get("fps", True):
            b_fps = make_badge()
            tk.Label(b_fps, text="FPS", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            self.labels["fps_val"] = tk.Label(b_fps, text="--", font=("Segoe UI Variable Display", self.big_font_size, "bold"), fg=self.theme["fps_good"], bg=badge_bg)
            self.labels["fps_val"].pack(side="left", padx=(4, 4))

            if metrics.get("one_percent_low", True):
                tk.Label(b_fps, text="1%", font=("Segoe UI Variable Text", max(7, self.base_font_size - 2), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
                self.labels["low_val"] = tk.Label(b_fps, text="--", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["low_val"].pack(side="left", padx=(2, 4))

            if metrics.get("frametime", True):
                self.labels["ft_val"] = tk.Label(b_fps, text="-- ms", font=("Segoe UI Variable Text", max(7, self.base_font_size - 2)), fg=self.theme["subtext"], bg=badge_bg)
                self.labels["ft_val"].pack(side="left")

        # C. CPU Badge
        show_c_temp = metrics.get("cpu_temp", True)
        show_c_usage = metrics.get("cpu_usage", True)
        show_c_clock = metrics.get("cpu_clock", False)
        if show_c_temp or show_c_usage or show_c_clock:
            b_cpu = make_badge()
            tk.Label(b_cpu, text="CPU", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            if show_c_temp:
                self.labels["cpu_temp"] = tk.Label(b_cpu, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["cpu_temp"], bg=badge_bg)
                self.labels["cpu_temp"].pack(side="left", padx=(3, 2))
            if show_c_usage:
                self.labels["cpu_usage"] = tk.Label(b_cpu, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["cpu_usage"].pack(side="left", padx=(1, 2))
            if show_c_clock:
                self.labels["cpu_clock"] = tk.Label(b_cpu, text="--MHz", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["cpu_clock"].pack(side="left", padx=(1, 2))

        # D. GPU Badge
        show_g_temp = metrics.get("gpu_temp", True)
        show_g_usage = metrics.get("gpu_usage", True)
        show_g_clock = metrics.get("gpu_clock", False)
        show_g_power = metrics.get("gpu_power", False)
        if show_g_temp or show_g_usage or show_g_clock or show_g_power:
            b_gpu = make_badge()
            tk.Label(b_gpu, text="GPU", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            if show_g_temp:
                self.labels["gpu_temp"] = tk.Label(b_gpu, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["gpu_temp"], bg=badge_bg)
                self.labels["gpu_temp"].pack(side="left", padx=(3, 2))
            if show_g_usage:
                self.labels["gpu_usage"] = tk.Label(b_gpu, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["gpu_usage"].pack(side="left", padx=(1, 2))
            if show_g_clock:
                self.labels["gpu_clock"] = tk.Label(b_gpu, text="--MHz", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["gpu_clock"].pack(side="left", padx=(1, 2))
            if show_g_power:
                self.labels["gpu_power"] = tk.Label(b_gpu, text="--W", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["accent"], bg=badge_bg)
                self.labels["gpu_power"].pack(side="left", padx=(1, 2))

        # E. RAM Badge
        if metrics.get("ram", True):
            b_ram = make_badge()
            tk.Label(b_ram, text="RAM", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            self.labels["ram_val"] = tk.Label(b_ram, text="-- GB", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
            self.labels["ram_val"].pack(side="left", padx=(3, 2))

        # F. Network Badge
        if metrics.get("network", True):
            b_net = make_badge()
            tk.Label(b_net, text="NET", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            self.labels["net_down"] = tk.Label(b_net, text="↓ 0KB/s", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["net_down"], bg=badge_bg)
            self.labels["net_down"].pack(side="left", padx=(3, 3))
            self.labels["net_up"] = tk.Label(b_net, text="↑ 0KB/s", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["net_up"], bg=badge_bg)
            self.labels["net_up"].pack(side="left")

        # G. Fan Badge
        if metrics.get("fan", True):
            b_fan = make_badge()
            tk.Label(b_fan, text="FAN", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            self.labels["fan_val"] = tk.Label(b_fan, text="-- RPM", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg="#0A84FF", bg=badge_bg)
            self.labels["fan_val"].pack(side="left", padx=(3, 2))

        # Right Controls: [ ••• ] + [ KHÓA ] + [ :: ]
        self.btn_menu = tk.Label(
            self.bar_frame,
            text="•••",
            font=("Segoe UI Variable Text", max(9, self.base_font_size + 1), "bold"),
            fg=self.theme["accent"],
            bg=badge_bg,
            cursor="hand2",
            padx=7, pady=2
        )
        self.btn_menu.is_interactive = True
        self.btn_menu.pack(side="right", padx=(2, 0))
        self.btn_menu.bind("<Button-1>", self._show_nav_menu)

        lock_str = "KHÓA" if self.click_through else ""
        self.lbl_lock = tk.Label(
            self.bar_frame,
            text=lock_str,
            font=("Segoe UI Variable Text", max(7, self.base_font_size - 2), "bold"),
            fg="#30D158",
            bg=badge_bg,
            padx=3, pady=2
        )
        self.lbl_lock.is_interactive = True
        self.lbl_lock.pack(side="right", padx=1)

        btn_resize = tk.Label(
            self.bar_frame,
            text="::",
            font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"),
            fg=self.theme["subtext"],
            bg=badge_bg,
            cursor="sb_h_double_arrow",
            padx=4, pady=2
        )
        btn_resize.is_interactive = True
        btn_resize.pack(side="right", padx=2)
        btn_resize.bind("<Button-1>", self._on_resize_start)
        btn_resize.bind("<B1-Motion>", self._on_resize_motion)

        # Bottom Graph Deck
        deck_h = 0
        if self.show_deck:
            self.deck_frame = tk.Frame(self.main_frame, bg=win_bg, pady=int(3 * self.scale))
            self.deck_frame.pack(fill="x", side="top")

            active_deck_count = sum(1 for k in ['fps', 'cpu', 'gpu', 'ram_net', 'fan'] if deck_cfg.get(k, True))
            target_w = max(380, self.current_w)
            card_w = max(int(140 * self.scale), int((target_w - 24) / max(1, active_deck_count)))
            card_h = int(62 * self.scale)
            graph_bg = badge_bg if self.bg_mode != "transparent" else CHROMA_KEY

            if deck_cfg.get("fps", True):
                g_fps = DeckSparkline(
                    self.deck_frame, width=card_w, height=card_h,
                    title="FPS & 1% Low", y_unit="FPS", y_min=0, y_max=240,
                    series_config=[("FPS", self.theme["fps_good"]), ("1% Low", "#d29922")],
                    bg_color=graph_bg, border_color=border_color
                )
                g_fps.pack(side="left", fill="both", expand=True, padx=int(3 * self.scale))
                self.deck_graphs["fps"] = g_fps

            if deck_cfg.get("cpu", True):
                g_cpu = DeckSparkline(
                    self.deck_frame, width=card_w, height=card_h,
                    title="CPU Xung & Nhiệt", y_unit="MHz", y_min=0, y_max=5000,
                    series_config=[("CPU", self.theme["cpu_temp"])],
                    bg_color=graph_bg, border_color=border_color
                )
                g_cpu.pack(side="left", fill="both", expand=True, padx=int(3 * self.scale))
                self.deck_graphs["cpu"] = g_cpu

            if deck_cfg.get("gpu", True):
                g_gpu = DeckSparkline(
                    self.deck_frame, width=card_w, height=card_h,
                    title="GPU Xung & Điện", y_unit="MHz", y_min=0, y_max=2100,
                    series_config=[("GPU", self.theme["gpu_temp"])],
                    bg_color=graph_bg, border_color=border_color
                )
                g_gpu.pack(side="left", fill="both", expand=True, padx=int(3 * self.scale))
                self.deck_graphs["gpu"] = g_gpu

            if deck_cfg.get("ram_net", True):
                g_net = DeckSparkline(
                    self.deck_frame, width=card_w, height=card_h,
                    title="RAM & Mạng", y_unit="%", y_min=0, y_max=100,
                    series_config=[("RAM", "#bc8cff")],
                    bg_color=graph_bg, border_color=border_color
                )
                g_net.pack(side="left", fill="both", expand=True, padx=int(3 * self.scale))
                self.deck_graphs["ram_net"] = g_net

            if deck_cfg.get("fan", True):
                g_fan = DeckSparkline(
                    self.deck_frame, width=card_w, height=card_h,
                    title="Quạt CPU & GPU", y_unit="RPM", y_min=0, y_max=5000,
                    series_config=[("CPU", "#0A84FF"), ("GPU", "#30D158")],
                    bg_color=graph_bg, border_color=border_color
                )
                g_fan.pack(side="left", fill="both", expand=True, padx=int(3 * self.scale))
                self.deck_graphs["fan"] = g_fan

            deck_h = card_h + int(8 * self.scale)

        self.update_idletasks()
        bar_req_w = self.bar_frame.winfo_reqwidth() + int(12 * self.scale)
        top_h = max(int(36 * self.scale), self.bar_frame.winfo_reqheight() + 4)
        total_h = top_h + deck_h

        width_mode = self.settings_mgr.get("overlay_width_mode", "auto") if self.settings_mgr else "auto"
        manual_w = self.settings_mgr.get("overlay_manual_width", 1080) if self.settings_mgr else 1080

        if width_mode == "auto":
            final_w = max(bar_req_w, 380)
            if self.show_deck:
                active_count = len(self.deck_graphs)
                if active_count > 0:
                    deck_natural_w = active_count * int(160 * self.scale) + int(16 * self.scale)
                    final_w = max(final_w, deck_natural_w)
        else:
            final_w = max(bar_req_w, manual_w)

        self.current_w = final_w
        self.current_h = total_h
        self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")

    # -------------------------------------------------------------
    # 2. COMPACT LAYOUT (Thanh Mini Apple Pill HUD - Tối giản)
    # -------------------------------------------------------------
    def _build_compact_layout(self, metrics: dict, deck_cfg: dict):
        win_bg, bar_bg, badge_bg, border_color = self._get_bg_colors()

        self.container = tk.Frame(
            self,
            bg=badge_bg,
            highlightbackground=border_color if self.bg_mode != "transparent" else CHROMA_KEY,
            highlightthickness=1 if self.bg_mode != "transparent" else 0,
            padx=int(8 * self.scale),
            pady=int(3 * self.scale)
        )
        self.container.pack(fill="both", expand=True)

        # A. App Name
        if metrics.get("app_name", True):
            self.labels["app"] = tk.Label(
                self.container,
                text="App",
                font=("Segoe UI Variable Text", self.base_font_size, "bold"),
                fg=self.theme["accent"],
                bg=badge_bg
            )
            self.labels["app"].pack(side="left", padx=(0, 4))

        # B. FPS
        if metrics.get("fps", True):
            self.labels["fps_val"] = tk.Label(
                self.container,
                text="-- FPS",
                font=("Segoe UI Variable Display", self.big_font_size, "bold"),
                fg=self.theme["fps_good"],
                bg=badge_bg
            )
            self.labels["fps_val"].pack(side="left", padx=3)

            if metrics.get("one_percent_low", True):
                self.labels["low_val"] = tk.Label(
                    self.container,
                    text="1% --",
                    font=("Segoe UI Variable Text", self.base_font_size),
                    fg=self.theme["text"],
                    bg=badge_bg
                )
                self.labels["low_val"].pack(side="left", padx=2)

            if metrics.get("frametime", True):
                self.labels["ft_val"] = tk.Label(
                    self.container,
                    text="--ms",
                    font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)),
                    fg=self.theme["subtext"],
                    bg=badge_bg
                )
                self.labels["ft_val"].pack(side="left", padx=2)

        # C. CPU
        show_c_temp = metrics.get("cpu_temp", True)
        show_c_usage = metrics.get("cpu_usage", True)
        show_c_clock = metrics.get("cpu_clock", False)
        if show_c_temp or show_c_usage or show_c_clock:
            c_box = tk.Frame(self.container, bg=badge_bg)
            c_box.pack(side="left", padx=3)
            tk.Label(c_box, text="C:", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            if show_c_temp:
                self.labels["cpu_temp"] = tk.Label(c_box, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["cpu_temp"], bg=badge_bg)
                self.labels["cpu_temp"].pack(side="left", padx=1)
            if show_c_usage:
                self.labels["cpu_usage"] = tk.Label(c_box, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["cpu_usage"].pack(side="left", padx=1)
            if show_c_clock:
                self.labels["cpu_clock"] = tk.Label(c_box, text="--MHz", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)), fg=self.theme["text"], bg=badge_bg)
                self.labels["cpu_clock"].pack(side="left", padx=1)

        # D. GPU
        show_g_temp = metrics.get("gpu_temp", True)
        show_g_usage = metrics.get("gpu_usage", True)
        show_g_clock = metrics.get("gpu_clock", False)
        show_g_power = metrics.get("gpu_power", False)
        if show_g_temp or show_g_usage or show_g_clock or show_g_power:
            g_box = tk.Frame(self.container, bg=badge_bg)
            g_box.pack(side="left", padx=3)
            tk.Label(g_box, text="G:", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left")
            if show_g_temp:
                self.labels["gpu_temp"] = tk.Label(g_box, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["gpu_temp"], bg=badge_bg)
                self.labels["gpu_temp"].pack(side="left", padx=1)
            if show_g_usage:
                self.labels["gpu_usage"] = tk.Label(g_box, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["gpu_usage"].pack(side="left", padx=1)
            if show_g_power:
                self.labels["gpu_power"] = tk.Label(g_box, text="--W", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)), fg=self.theme["accent"], bg=badge_bg)
                self.labels["gpu_power"].pack(side="left", padx=1)
            if show_g_clock:
                self.labels["gpu_clock"] = tk.Label(g_box, text="--MHz", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)), fg=self.theme["text"], bg=badge_bg)
                self.labels["gpu_clock"].pack(side="left", padx=1)

        # E. RAM
        if metrics.get("ram", True):
            self.labels["ram_val"] = tk.Label(
                self.container,
                text="RAM --",
                font=("Segoe UI Variable Text", self.base_font_size),
                fg=self.theme["text"],
                bg=badge_bg
            )
            self.labels["ram_val"].pack(side="left", padx=3)

        # F. Network
        if metrics.get("network", True):
            self.labels["net_down"] = tk.Label(
                self.container,
                text="↓0K",
                font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)),
                fg=self.theme["net_down"],
                bg=badge_bg
            )
            self.labels["net_down"].pack(side="left", padx=2)

        # G. Fan
        if metrics.get("fan", True):
            self.labels["fan_val"] = tk.Label(
                self.container,
                text="FAN --",
                font=("Segoe UI Variable Text", self.base_font_size, "bold"),
                fg="#0A84FF",
                bg=badge_bg
            )
            self.labels["fan_val"].pack(side="left", padx=3)

        # Action Menu Button & Lock Indicator
        self.btn_menu = tk.Label(
            self.container,
            text="•••",
            font=("Segoe UI Variable Text", self.base_font_size, "bold"),
            fg=self.theme["accent"],
            bg=badge_bg,
            cursor="hand2",
            padx=4
        )
        self.btn_menu.is_interactive = True
        self.btn_menu.pack(side="right", padx=(2, 0))
        self.btn_menu.bind("<Button-1>", self._show_nav_menu)

        lock_str = "KHÓA" if self.click_through else ""
        self.lbl_lock = tk.Label(
            self.container,
            text=lock_str,
            font=("Segoe UI Variable Text", max(7, self.base_font_size - 2), "bold"),
            fg="#30D158",
            bg=badge_bg,
            padx=2
        )
        self.lbl_lock.is_interactive = True
        self.lbl_lock.pack(side="right", padx=1)

        self.update_idletasks()
        req_w = self.container.winfo_reqwidth() + int(14 * self.scale)
        self.current_w = max(int(240 * self.scale), req_w)
        self.current_h = max(int(32 * self.scale), self.container.winfo_reqheight() + 4)
        self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")

    # -------------------------------------------------------------
    # 3. CORNER LAYOUT (Khối góc Gaming OSD Card - Đa Hàng Đỉnh Cao)
    # -------------------------------------------------------------
    def _build_corner_layout(self, metrics: dict, deck_cfg: dict):
        win_bg, bar_bg, badge_bg, border_color = self._get_bg_colors()

        self.container = tk.Frame(
            self,
            bg=badge_bg,
            highlightbackground=border_color if self.bg_mode != "transparent" else CHROMA_KEY,
            highlightthickness=1 if self.bg_mode != "transparent" else 0,
            padx=int(12 * self.scale),
            pady=int(8 * self.scale)
        )
        self.container.pack(fill="both", expand=True)

        # Row 1: Header (App Name + Menu)
        r1 = tk.Frame(self.container, bg=badge_bg)
        r1.pack(fill="x", pady=(0, 3))
        app_text = "Đang chờ ứng dụng..." if metrics.get("app_name", True) else "Legion OSD"
        self.labels["app"] = tk.Label(
            r1,
            text=app_text,
            font=("Segoe UI Variable Text", self.base_font_size, "bold"),
            fg=self.theme["accent"],
            bg=badge_bg
        )
        self.labels["app"].pack(side="left")

        self.btn_menu = tk.Label(r1, text="•••", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["accent"], bg=badge_bg, cursor="hand2")
        self.btn_menu.is_interactive = True
        self.btn_menu.pack(side="right")
        self.btn_menu.bind("<Button-1>", self._show_nav_menu)

        lock_str = "KHÓA" if self.click_through else ""
        self.lbl_lock = tk.Label(
            r1,
            text=lock_str,
            font=("Segoe UI Variable Text", max(7, self.base_font_size - 2), "bold"),
            fg="#30D158",
            bg=badge_bg,
            padx=2
        )
        self.lbl_lock.is_interactive = True
        self.lbl_lock.pack(side="right", padx=(0, 2))

        # Row 2: FPS Group
        if metrics.get("fps", True):
            r2 = tk.Frame(self.container, bg=badge_bg)
            r2.pack(fill="x", pady=2)
            self.labels["fps_val"] = tk.Label(r2, text="-- FPS", font=("Segoe UI Variable Display", self.big_font_size, "bold"), fg=self.theme["fps_good"], bg=badge_bg)
            self.labels["fps_val"].pack(side="left", padx=(0, 6))

            if metrics.get("one_percent_low", True):
                self.labels["low_val"] = tk.Label(r2, text="1%: --", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["low_val"].pack(side="left", padx=(0, 6))

            if metrics.get("frametime", True):
                self.labels["ft_val"] = tk.Label(r2, text="-- ms", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["subtext"], bg=badge_bg)
                self.labels["ft_val"].pack(side="left")

        # Row 3: CPU Group
        show_c_temp = metrics.get("cpu_temp", True)
        show_c_usage = metrics.get("cpu_usage", True)
        show_c_clock = metrics.get("cpu_clock", False)
        if show_c_temp or show_c_usage or show_c_clock:
            r3 = tk.Frame(self.container, bg=badge_bg)
            r3.pack(fill="x", pady=2)
            tk.Label(r3, text="CPU", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left", padx=(0, 4))
            if show_c_temp:
                self.labels["cpu_temp"] = tk.Label(r3, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["cpu_temp"], bg=badge_bg)
                self.labels["cpu_temp"].pack(side="left", padx=(0, 6))
            if show_c_usage:
                self.labels["cpu_usage"] = tk.Label(r3, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["cpu_usage"].pack(side="left", padx=(0, 6))
            if show_c_clock:
                self.labels["cpu_clock"] = tk.Label(r3, text="--MHz", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["cpu_clock"].pack(side="left")

        # Row 4: GPU Group
        show_g_temp = metrics.get("gpu_temp", True)
        show_g_usage = metrics.get("gpu_usage", True)
        show_g_clock = metrics.get("gpu_clock", False)
        show_g_power = metrics.get("gpu_power", False)
        if show_g_temp or show_g_usage or show_g_clock or show_g_power:
            r4 = tk.Frame(self.container, bg=badge_bg)
            r4.pack(fill="x", pady=2)
            tk.Label(r4, text="GPU", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["subtext"], bg=badge_bg).pack(side="left", padx=(0, 4))
            if show_g_temp:
                self.labels["gpu_temp"] = tk.Label(r4, text="--°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["gpu_temp"], bg=badge_bg)
                self.labels["gpu_temp"].pack(side="left", padx=(0, 6))
            if show_g_usage:
                self.labels["gpu_usage"] = tk.Label(r4, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["gpu_usage"].pack(side="left", padx=(0, 6))
            if show_g_power:
                self.labels["gpu_power"] = tk.Label(r4, text="--W", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["accent"], bg=badge_bg)
                self.labels["gpu_power"].pack(side="left", padx=(0, 6))
            if show_g_clock:
                self.labels["gpu_clock"] = tk.Label(r4, text="--MHz", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["gpu_clock"].pack(side="left")

        # Row 5: RAM, Network & Fan Group
        show_ram = metrics.get("ram", True)
        show_net = metrics.get("network", True)
        show_fan = metrics.get("fan", True)
        if show_ram or show_net or show_fan:
            r5 = tk.Frame(self.container, bg=badge_bg)
            r5.pack(fill="x", pady=(2, 0))
            if show_ram:
                self.labels["ram_val"] = tk.Label(r5, text="RAM: --%", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["ram_val"].pack(side="left", padx=(0, 6))
            if show_net:
                self.labels["net_down"] = tk.Label(r5, text="↓0K", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1)), fg=self.theme["net_down"], bg=badge_bg)
                self.labels["net_down"].pack(side="left", padx=(0, 6))
            if show_fan:
                self.labels["fan_val"] = tk.Label(r5, text="FAN: --", font=("Segoe UI Variable Text", self.base_font_size), fg="#0A84FF", bg=badge_bg)
                self.labels["fan_val"].pack(side="left")

        self.update_idletasks()
        self.current_w = max(int(260 * self.scale), self.container.winfo_reqwidth() + int(16 * self.scale))
        self.current_h = max(int(70 * self.scale), self.container.winfo_reqheight() + int(10 * self.scale))
        self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")

    # -------------------------------------------------------------
    # 4. VERTICAL LAYOUT (Thanh Dọc Cạnh Màn Hình - Side Dock)
    # -------------------------------------------------------------
    def _build_vertical_layout(self, metrics: dict, deck_cfg: dict):
        win_bg, bar_bg, badge_bg, border_color = self._get_bg_colors()

        self.container = tk.Frame(
            self,
            bg=badge_bg,
            highlightbackground=border_color if self.bg_mode != "transparent" else CHROMA_KEY,
            highlightthickness=1 if self.bg_mode != "transparent" else 0,
            padx=int(10 * self.scale),
            pady=int(8 * self.scale)
        )
        self.container.pack(fill="both", expand=True)

        # Header: App Title + Menu
        hdr = tk.Frame(self.container, bg=badge_bg)
        hdr.pack(fill="x", pady=(0, 4))
        self.labels["app"] = tk.Label(
            hdr,
            text="App" if metrics.get("app_name", True) else "Legion",
            font=("Segoe UI Variable Text", self.base_font_size, "bold"),
            fg=self.theme["accent"],
            bg=badge_bg
        )
        self.labels["app"].pack(side="left")

        self.btn_menu = tk.Label(hdr, text="•••", font=("Segoe UI Variable Text", max(7, self.base_font_size - 1), "bold"), fg=self.theme["accent"], bg=badge_bg, cursor="hand2")
        self.btn_menu.is_interactive = True
        self.btn_menu.pack(side="right")
        self.btn_menu.bind("<Button-1>", self._show_nav_menu)

        lock_str = "KHÓA" if self.click_through else ""
        self.lbl_lock = tk.Label(
            hdr,
            text=lock_str,
            font=("Segoe UI Variable Text", max(7, self.base_font_size - 2), "bold"),
            fg="#30D158",
            bg=badge_bg,
            padx=2
        )
        self.lbl_lock.is_interactive = True
        self.lbl_lock.pack(side="right", padx=(0, 2))

        # 1. FPS
        if metrics.get("fps", True):
            self.labels["fps_val"] = tk.Label(self.container, text="FPS: --", font=("Segoe UI Variable Display", self.big_font_size, "bold"), fg=self.theme["fps_good"], bg=badge_bg)
            self.labels["fps_val"].pack(anchor="w", pady=2)
            if metrics.get("one_percent_low", True):
                self.labels["low_val"] = tk.Label(self.container, text="1% Low: --", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
                self.labels["low_val"].pack(anchor="w", pady=1)

        # 2. CPU
        show_c_temp = metrics.get("cpu_temp", True)
        show_c_usage = metrics.get("cpu_usage", True)
        if show_c_temp or show_c_usage:
            c_row = tk.Frame(self.container, bg=badge_bg)
            c_row.pack(anchor="w", pady=2)
            if show_c_temp:
                self.labels["cpu_temp"] = tk.Label(c_row, text="CPU: --°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["cpu_temp"], bg=badge_bg)
                self.labels["cpu_temp"].pack(side="left")
            if show_c_usage:
                self.labels["cpu_usage"] = tk.Label(c_row, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["cpu_usage"].pack(side="left", padx=(2, 0))

        # 3. GPU
        show_g_temp = metrics.get("gpu_temp", True)
        show_g_usage = metrics.get("gpu_usage", True)
        if show_g_temp or show_g_usage:
            g_row = tk.Frame(self.container, bg=badge_bg)
            g_row.pack(anchor="w", pady=2)
            if show_g_temp:
                self.labels["gpu_temp"] = tk.Label(g_row, text="GPU: --°C", font=("Segoe UI Variable Text", self.base_font_size, "bold"), fg=self.theme["gpu_temp"], bg=badge_bg)
                self.labels["gpu_temp"].pack(side="left")
            if show_g_usage:
                self.labels["gpu_usage"] = tk.Label(g_row, text="(--%)", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["load"], bg=badge_bg)
                self.labels["gpu_usage"].pack(side="left", padx=(2, 0))

        if metrics.get("gpu_power", False):
            self.labels["gpu_power"] = tk.Label(self.container, text="PWR: --W", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["accent"], bg=badge_bg)
            self.labels["gpu_power"].pack(anchor="w", pady=1)

        # 4. RAM
        if metrics.get("ram", True):
            self.labels["ram_val"] = tk.Label(self.container, text="RAM: --%", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["text"], bg=badge_bg)
            self.labels["ram_val"].pack(anchor="w", pady=2)

        # 5. Network
        if metrics.get("network", True):
            self.labels["net_down"] = tk.Label(self.container, text="NET: ↓ 0KB/s", font=("Segoe UI Variable Text", self.base_font_size), fg=self.theme["net_down"], bg=badge_bg)
            self.labels["net_down"].pack(anchor="w", pady=2)

        # 6. Fan
        if metrics.get("fan", True):
            self.labels["fan_val"] = tk.Label(self.container, text="FAN: --", font=("Segoe UI Variable Text", self.base_font_size), fg="#0A84FF", bg=badge_bg)
            self.labels["fan_val"].pack(anchor="w", pady=2)

        self.update_idletasks()
        self.current_w = max(int(150 * self.scale), self.container.winfo_reqwidth() + int(12 * self.scale))
        self.current_h = max(int(120 * self.scale), self.container.winfo_reqheight() + int(12 * self.scale))
        self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")

    def _bind_mouse(self):
        for widget in [self] + self.winfo_children():
            self._recursive_bind(widget)

    def _recursive_bind(self, w):
        if getattr(w, "is_interactive", False):
            return
        w.bind("<Button-1>", self._on_drag_start)
        w.bind("<B1-Motion>", self._on_drag_motion)
        w.bind("<ButtonRelease-1>", self._on_drag_release)
        for child in w.winfo_children():
            self._recursive_bind(child)

    def _on_drag_start(self, event):
        if self.click_through:
            return
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _on_drag_motion(self, event):
        if self.click_through:
            return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.current_x = x
        self.current_y = y
        self.geometry(f"{self.current_w}x{self.current_h}+{x}+{y}")
        self._sync_bg_win()

    def _on_drag_release(self, event):
        if self.settings_mgr:
            self.settings_mgr.set("overlay_position", {"x": self.current_x, "y": self.current_y})
        self._sync_bg_win()

    # -------------------------------------------------------------
    # 5. DYNAMIC TELEMETRY UPDATE (Polled every 400ms)
    # -------------------------------------------------------------
    def update_metrics(self, fps_data: dict, hw_data: dict):
        # 1. App Title
        if "app" in self.labels:
            name = fps_data.get("game_name", "")
            if name and not name.startswith("Desktop"):
                limit = 14 if self.layout_mode in ["corner", "vertical", "compact"] else 20
                display_name = name[:limit] + ".." if len(name) > limit else name
                self.labels["app"].config(text=display_name)
            else:
                self.labels["app"].config(text="Desktop" if self.layout_mode != "vertical" else "Dsk")

        # 2. FPS & 1% Low & Frametime
        fps = fps_data.get("fps", 0.0)
        low = fps_data.get("one_percent_low", 0.0)
        ft = fps_data.get("frametime_ms", 0.0)

        fps_color = get_fps_color(fps)
        low_color = get_low_fps_color(low)
        ft_color = get_frametime_color(ft)

        if "fps_val" in self.labels:
            if fps > 0:
                if self.layout_mode == "compact":
                    self.labels["fps_val"].config(text=f"{int(fps)} FPS", fg=fps_color)
                elif self.layout_mode == "vertical":
                    self.labels["fps_val"].config(text=f"FPS: {int(fps)}", fg=fps_color)
                elif self.layout_mode == "corner":
                    self.labels["fps_val"].config(text=f"{int(fps)} FPS", fg=fps_color)
                else:
                    self.labels["fps_val"].config(text=f"{int(fps)}", fg=fps_color)
            else:
                self.labels["fps_val"].config(text="--", fg=self.theme["subtext"])

        if "low_val" in self.labels:
            if self.layout_mode == "vertical":
                self.labels["low_val"].config(text=f"1% Low: {int(low)}" if fps > 0 else "1% Low: --", fg=low_color if fps > 0 else self.theme["subtext"])
            elif self.layout_mode == "corner":
                self.labels["low_val"].config(text=f"1%: {int(low)}" if fps > 0 else "1%: --", fg=low_color if fps > 0 else self.theme["subtext"])
            else:
                self.labels["low_val"].config(text=f"{int(low)}" if fps > 0 else "--", fg=low_color if fps > 0 else self.theme["subtext"])

        if "ft_val" in self.labels:
            self.labels["ft_val"].config(text=f"{ft:.1f}ms" if fps > 0 else "-- ms", fg=ft_color if fps > 0 else self.theme["subtext"])

        # 3. CPU
        cpu_temp = hw_data.get("cpu_temp", 50.0)
        cpu_usage = hw_data.get("cpu_usage", 0.0)
        cpu_clock = hw_data.get("cpu_freq_mhz", 3201.0)

        c_temp_color = get_cpu_temp_color(cpu_temp)
        c_usage_color = get_cpu_usage_color(cpu_usage)

        if "cpu_temp" in self.labels:
            prefix = "CPU: " if self.layout_mode == "vertical" else ""
            self.labels["cpu_temp"].config(text=f"{prefix}{cpu_temp:.0f}°C", fg=c_temp_color)
        if "cpu_usage" in self.labels:
            self.labels["cpu_usage"].config(text=f"({cpu_usage:.0f}%)", fg=c_usage_color)
        if "cpu_clock" in self.labels:
            self.labels["cpu_clock"].config(text=f"{int(cpu_clock)}MHz")

        # 4. GPU
        gpu_temp = hw_data.get("gpu_temp", 42)
        gpu_usage = hw_data.get("gpu_usage", 0)
        gpu_clock = hw_data.get("gpu_clock_mhz", 0)
        gpu_power = hw_data.get("gpu_power_w", 0.0)

        g_temp_color = get_gpu_temp_color(gpu_temp)
        g_usage_color = get_gpu_usage_color(gpu_usage)

        if "gpu_temp" in self.labels:
            prefix = "GPU: " if self.layout_mode == "vertical" else ""
            self.labels["gpu_temp"].config(text=f"{prefix}{gpu_temp}°C", fg=g_temp_color)
        if "gpu_usage" in self.labels:
            self.labels["gpu_usage"].config(text=f"({gpu_usage}%)", fg=g_usage_color)
        if "gpu_clock" in self.labels:
            self.labels["gpu_clock"].config(text=f"{gpu_clock}MHz")
        if "gpu_power" in self.labels:
            self.labels["gpu_power"].config(text=f"{gpu_power:.0f}W")

        # 5. RAM
        ram_used = hw_data.get("ram_used_gb", 0.0)
        ram_pct = hw_data.get("ram_percent", 0.0)
        ram_color = get_ram_color(ram_pct)

        if "ram_val" in self.labels:
            if self.layout_mode in ["corner", "vertical"]:
                self.labels["ram_val"].config(text=f"RAM: {ram_pct:.0f}%", fg=ram_color)
            elif self.layout_mode == "compact":
                self.labels["ram_val"].config(text=f"RAM {ram_pct:.0f}%", fg=ram_color)
            else:
                self.labels["ram_val"].config(text=f"{ram_used:.1f}GB ({ram_pct:.0f}%)", fg=ram_color)

        # 6. Network
        down_str = hw_data.get("net_down_str", "0 KB/s")
        up_str = hw_data.get("net_up_str", "0 KB/s")
        if "net_down" in self.labels:
            if self.layout_mode in ["corner", "compact"]:
                self.labels["net_down"].config(text=f"↓{down_str}")
            else:
                self.labels["net_down"].config(text=f"↓ {down_str}")
        if "net_up" in self.labels:
            self.labels["net_up"].config(text=f"↑ {up_str}")

        # 7. Fan RPM
        fan_rpm = hw_data.get("fan_speed_rpm", 0)
        fan_cpu_rpm = hw_data.get("fan_cpu_rpm", 0)
        fan_gpu_rpm = hw_data.get("fan_gpu_rpm", 0)
        fan_pct = hw_data.get("fan_percent", 0)
        fan_color = get_fan_color(fan_rpm)
        fan_mode_opt = self.settings_mgr.get("overlay_fan_mode", "dual") if self.settings_mgr else "dual"

        if "fan_val" in self.labels:
            if fan_mode_opt == "dual":
                if self.layout_mode in ["corner", "vertical"]:
                    self.labels["fan_val"].config(text=f"C:{fan_cpu_rpm} G:{fan_gpu_rpm}", fg=fan_color)
                elif self.layout_mode == "compact":
                    self.labels["fan_val"].config(text=f"F {fan_cpu_rpm}/{fan_gpu_rpm}", fg=fan_color)
                else:
                    self.labels["fan_val"].config(text=f"C:{fan_cpu_rpm} · G:{fan_gpu_rpm} RPM", fg=fan_color)
            elif fan_mode_opt == "cpu":
                c_color = get_fan_color(fan_cpu_rpm)
                self.labels["fan_val"].config(text=f"CPU {fan_cpu_rpm} RPM" if self.layout_mode == "horizontal" else f"CPU: {fan_cpu_rpm}", fg=c_color)
            elif fan_mode_opt == "gpu":
                g_color = get_fan_color(fan_gpu_rpm)
                self.labels["fan_val"].config(text=f"GPU {fan_gpu_rpm} RPM" if self.layout_mode == "horizontal" else f"GPU: {fan_gpu_rpm}", fg=g_color)
            else:  # "max"
                self.labels["fan_val"].config(text=f"{fan_rpm} RPM ({fan_pct}%)" if self.layout_mode == "horizontal" else f"FAN: {fan_rpm}", fg=fan_color)

        # 8. Bottom Graph Deck Updates
        if "fps" in self.deck_graphs:
            fps_val_str = f"{int(fps)} FPS" if fps > 0 else "-- FPS"
            self.deck_graphs["fps"].update_data(
                [fps_data.get("history_fps", []), fps_data.get("history_one_percent_low", [])],
                fps_val_str,
                val_color=fps_color
            )

        if "cpu" in self.deck_graphs:
            cpu_val_str = f"{int(cpu_clock)} MHz ({cpu_temp:.0f}°C)"
            self.deck_graphs["cpu"].update_data(
                [hw_data.get("history_cpu_clock", [])],
                cpu_val_str,
                val_color=c_temp_color
            )

        if "gpu" in self.deck_graphs:
            gpu_val_str = f"{gpu_clock} MHz ({gpu_power:.0f}W)"
            self.deck_graphs["gpu"].update_data(
                [hw_data.get("history_gpu_clock", [])],
                gpu_val_str,
                val_color=g_temp_color
            )

        if "ram_net" in self.deck_graphs:
            ram_val_str = f"{ram_pct:.0f}% ({down_str})"
            self.deck_graphs["ram_net"].update_data(
                [hw_data.get("history_ram_load", [])],
                ram_val_str,
                val_color=ram_color
            )

        if "fan" in self.deck_graphs:
            fan_val_str = f"C:{fan_cpu_rpm} · G:{fan_gpu_rpm}"
            hist_cpu = hw_data.get("history_fan_cpu_rpm", [])
            hist_gpu = hw_data.get("history_fan_gpu_rpm", [])
            if not hist_cpu and not hist_gpu:
                hist_cpu = hw_data.get("history_fan_rpm", [])
                hist_gpu = hist_cpu
            self.deck_graphs["fan"].update_data(
                [hist_cpu, hist_gpu],
                fan_val_str,
                val_color=fan_color
            )

        # 9. Dynamic Auto-Fit Sync (for ALL layouts)
        width_mode = self.settings_mgr.get("overlay_width_mode", "auto") if self.settings_mgr else "auto"
        if width_mode == "auto":
            if self.layout_mode == "horizontal" and hasattr(self, "bar_frame"):
                bar_req_w = self.bar_frame.winfo_reqwidth() + int(12 * self.scale)
                final_w = max(bar_req_w, 380)
                if self.show_deck and len(self.deck_graphs) > 0:
                    deck_natural_w = len(self.deck_graphs) * int(160 * self.scale) + int(16 * self.scale)
                    final_w = max(final_w, deck_natural_w)
                if abs(final_w - self.current_w) > 20:
                    self.current_w = final_w
                    self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")
                    self._sync_bg_win()
            elif hasattr(self, "container"):
                req_w = self.container.winfo_reqwidth() + int(14 * self.scale)
                req_h = self.container.winfo_reqheight() + int(8 * self.scale)
                if abs(req_w - self.current_w) > 15 or abs(req_h - self.current_h) > 10:
                    self.current_w = max(int(150 * self.scale), req_w)
                    self.current_h = max(int(32 * self.scale), req_h)
                    self.geometry(f"{self.current_w}x{self.current_h}+{self.current_x}+{self.current_y}")
                    self._sync_bg_win()
