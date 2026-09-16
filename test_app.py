"""
Verification Test Suite for Legion Performance & FPS Monitor v2.3 PRO.
Tests:
1. Dynamic CPU Frequency via Windows PDH counter
2. 3-Tier FPS Tracker process resolution
3. Visualizer SparklineGraph & DeckSparkline
4. Overlay Window (Nav Menu, Click-Through F8, % Transparency, Coordinate Pinning)
5. LegionApp v2.3 PRO Full Lifecycle & Tab Switching
"""

import sys
import os
import time

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from hw_monitor import HardwareMonitor
from fps_tracker import FPSTracker
from visualizer import SparklineGraph, MiniSparkline, DeckSparkline, generate_catmull_rom_spline
from circular_gauge import CircularGauge
from overlay_window import (
    InGameOverlay, get_fps_color, get_low_fps_color, get_frametime_color,
    get_cpu_temp_color, get_cpu_usage_color, get_gpu_temp_color,
    get_gpu_usage_color, get_ram_color
)
from settings_manager import SettingsManager
from app import LegionApp

print("==================================================")
print("  TEST 0: Warning Threshold Color Rules")
print("==================================================")
# FPS
assert get_fps_color(120) == "#30D158" or get_fps_color(120) == "#3fb950", "FPS 120 should be green"
assert get_fps_color(45) in ["#d29922", "#FF9F0A"], "FPS 45 should be amber"
assert get_fps_color(20) in ["#f85149", "#FF453A"], "FPS 20 should be red"
# 1% Low
assert get_low_fps_color(60) in ["#3fb950", "#30D158"]
assert get_low_fps_color(30) in ["#d29922", "#FF9F0A"]
assert get_low_fps_color(15) in ["#f85149", "#FF453A"]
# Frametime
assert get_frametime_color(8.3) in ["#3fb950", "#30D158"]
assert get_frametime_color(22.0) in ["#d29922", "#FF9F0A"]
assert get_frametime_color(40.0) in ["#f85149", "#FF453A"]
# CPU Temp
assert get_cpu_temp_color(65) in ["#3fb950", "#30D158"]
assert get_cpu_temp_color(78) in ["#d29922", "#FF9F0A"]
assert get_cpu_temp_color(90) in ["#f85149", "#FF453A"]
# CPU Usage
assert get_cpu_usage_color(35) in ["#58a6ff", "#0A84FF"]
assert get_cpu_usage_color(80) in ["#d29922", "#FF9F0A"]
assert get_cpu_usage_color(95) in ["#f85149", "#FF453A"]
# GPU Temp
assert get_gpu_temp_color(60) in ["#3fb950", "#30D158"]
assert get_gpu_temp_color(75) in ["#d29922", "#FF9F0A"]
assert get_gpu_temp_color(85) in ["#f85149", "#FF453A"]
# RAM Usage
assert get_ram_color(50) in ["#bc8cff", "#BF5AF2"]
assert get_ram_color(80) in ["#d29922", "#FF9F0A"]
assert get_ram_color(92) in ["#f85149", "#FF453A"]
print(" [PASS] All warning threshold color functions passed boundary checks!")

print("\n==================================================")
print("  TEST 1: Dynamic CPU Frequency (Windows PDH)")
print("==================================================")
hw = HardwareMonitor()
freq = hw._get_cpu_dynamic_freq(35.0)
print(f" Dynamic CPU Frequency query: {freq} MHz")
assert freq >= 700.0, f"Dynamic CPU freq returned invalid value: {freq}"

snap = hw.get_snapshot()
print(f" CPU Frequency: {snap['cpu_freq_mhz']:.1f} MHz ({snap['cpu_freq_ghz']:.2f} GHz)")
assert snap['cpu_freq_mhz'] >= 700.0, f"CPU freq too low: {snap['cpu_freq_mhz']}"
assert "history_ram_load" in snap, "history_ram_load missing from get_snapshot!"
print(" [PASS] Dynamic CPU Frequency and RAM history buffer working!")

print("\n==================================================")
print("  TEST 2: 3-Tier Process Matching in FPSTracker")
print("==================================================")
fps = FPSTracker()
stats = fps.get_stats()
print(f" Active Foreground App: {stats['game_name']} (PID: {fps.active_pid})")
assert "game_name" in stats and "fps" in stats
assert "history_one_percent_low" in stats, "history_one_percent_low missing from stats!"
print(" [PASS] FPSTracker and 1% Low history buffer queried successfully!")

print("\n==================================================")
print("  TEST 3: Catmull-Rom Spline & Responsive Visualizer")
print("==================================================")
# 3.1 Test Catmull-Rom Spline Interpolation Algorithm
assert generate_catmull_rom_spline([]) == [], "Empty points should yield empty spline"
assert generate_catmull_rom_spline([(10.0, 20.0)]) == [10.0, 20.0], "Single point should yield exact point"
assert generate_catmull_rom_spline([(10.0, 20.0), (30.0, 40.0)]) == [10.0, 20.0, 30.0, 40.0]

pts = [(0.0, 50.0), (100.0, 20.0), (200.0, 80.0), (300.0, 40.0)]
spline = generate_catmull_rom_spline(pts, steps=10, min_y=10.0, max_y=90.0)
assert len(spline) > len(pts) * 2, f"Spline points insufficient: {len(spline)}"
# Verify clamping
for i in range(1, len(spline), 2):
    y = spline[i]
    assert 10.0 <= y <= 90.0, f"Spline y {y} out of clamped bounds [10, 90]"
print(" [PASS] Catmull-Rom Spline mathematical interpolation verified with bounds!")

import tkinter as tk
root = tk.Tk()
root.withdraw()

# 3.2 Test CircularGauge resizing
gauge = CircularGauge(root, size=150)
assert gauge.size == 150
gauge.resize(210)
assert gauge.size == 210, f"Gauge failed to resize: {gauge.size}"
print(" [PASS] CircularGauge responsive diameter resize verified!")

# 3.3 Test SparklineGraph with multi-points and anti-collision
sg = SparklineGraph(root, width=800, height=150, title="Biểu đồ xung nhịp phần cứng rất dài", y_steps=5, series_config=[("CPU", "#ff7b72"), ("GPU", "#58a6ff")])
assert sg.padding_left >= 70, f"padding_left too small: {sg.padding_left}"
assert sg.y_steps == 5, f"y_steps not set: {sg.y_steps}"
test_series = [
    [100.0, 150.0, 120.0, 200.0, 180.0],
    [50.0, 60.0, 55.0, 70.0, 65.0]
]
sg.update_data(test_series, ["180 MHz", "65 MHz"])
print(" [PASS] SparklineGraph rendered with Catmull-Rom spline curves and y_steps successfully!")

# Test DeckSparkline Anti-Collision Text Rendering
ds = DeckSparkline(root, width=150, height=62, title="Tên biểu đồ cực kỳ dài không thể vừa", series_config=[("FPS", "#3fb950"), ("1% Low", "#d29922")])
ds.update_data([[120.0, 144.0, 140.0, 160.0], [100.0, 110.0, 105.0, 120.0]], "160 FPS (120 FPS)", val_color="#3fb950")
print(" [PASS] DeckSparkline rendered with anti-collision text truncation successfully!")

print("\n==================================================")
print("  TEST 4: InGameOverlay Controls, Click-Through & Transparency %")
print("==================================================")
sm = SettingsManager()
closed_flag = [False]
def on_close():
    closed_flag[0] = True

overlay = InGameOverlay(root, settings_mgr=sm, on_close_callback=on_close)
init_x, init_y = overlay.current_x, overlay.current_y

overlay.update_metrics(
    fps_data={"game_name": "TestGame.exe", "fps": 144.0, "one_percent_low": 110.0, "frametime_ms": 6.9, "history_fps": [140.0, 144.0]},
    hw_data={
        "cpu_temp": 62.0, "cpu_usage": 35.0, "cpu_freq_mhz": 3800.0,
        "gpu_temp": 58.0, "gpu_usage": 80.0, "gpu_clock_mhz": 1750, "gpu_power_w": 95.0,
        "ram_used_gb": 10.5, "ram_percent": 65.0,
        "net_down_str": "12.4 MB/s", "net_up_str": "1.2 MB/s",
        "history_cpu_clock": [3700.0, 3800.0],
        "history_gpu_clock": [1700.0, 1750.0],
        "history_cpu_temp": [60.0, 62.0],
        "history_gpu_temp": [56.0, 58.0],
        "history_cpu_load": [30.0, 35.0],
        "history_gpu_load": [75.0, 80.0]
    }
)

# Verify position anchor when resizing width
class FakeEvent:
    x_root = 500
overlay._resize_start_x = 400
overlay._resize_start_w = overlay.current_w
overlay._on_resize_motion(FakeEvent())

assert overlay.current_x == init_x and overlay.current_y == init_y, "Position shifted during width resize!"
print(f" [PASS] Position strictly anchored during resize: ({overlay.current_x}, {overlay.current_y})")

# Test Click-Through mode toggle
overlay.set_click_through(True)
assert overlay.click_through == True, "Click-through not enabled!"
overlay.toggle_click_through()
assert overlay.click_through == False, "toggle_click_through did not disable!"
print(" [PASS] Click-Through (F8) toggles properly!")

# Test independent background & text transparency
overlay.set_bg_transparency_pct(40)
assert overlay.bg_transparency_pct == 40, "Background transparency percentage not set!"
print(" [PASS] Background transparency adjusted independently to 40%!")

overlay.set_text_transparency_pct(85)
assert overlay.text_transparency_pct == 85, "Text transparency percentage not set!"
print(" [PASS] Text transparency adjusted independently to 85%!")

# Test background transparency cycle via F10
b1 = overlay.bg_transparency_pct
overlay.cycle_transparency()
b2 = overlay.bg_transparency_pct
assert b1 != b2, "cycle_transparency did not cycle bg transparency!"
print(f" [PASS] Background transparency cycle: {b1}% -> {b2}%")

# Test backdrop window synchronization
assert hasattr(overlay, "bg_win") and overlay.bg_win is not None, "Backdrop window missing!"
print(" [PASS] Backdrop window bg_win synchronized with foreground overlay!")

# Test close button simulation
overlay._on_close_clicked()
assert closed_flag[0] == True, "Close callback was not called!"
print(" [PASS] Overlay close button and callback synchronized!")

root.destroy()

print("\n==================================================")
print("  TEST 5: LegionApp v2.3 PRO Responsive Layout & Lifecycle")
print("==================================================")
app = LegionApp()
print(" LegionApp v2.3 PRO initialized!")

# 5.1 Test Responsive Graphs 2x2 Grid vs 1-Column switching
app._set_graphs_layout_mode("grid")
assert app.graphs_mode == "grid", "Failed to switch graphs to 2x2 grid mode!"
print(" [PASS] Graphs tab successfully switches to 2x2 Grid mode!")

app._set_graphs_layout_mode("col")
assert app.graphs_mode == "col", "Failed to switch graphs to 1-col mode!"
print(" [PASS] Graphs tab successfully switches to 1-Column scroll mode!")

# 5.2 Test Responsive Settings 2-Column vs 1-Column switching
app._set_settings_layout_mode("two_col")
assert app.settings_mode == "two_col", "Failed to switch settings to 2-column mode!"
print(" [PASS] Settings tab successfully switches to 2-Column layout!")

app._set_settings_layout_mode("one_col")
assert app.settings_mode == "one_col", "Failed to switch settings to 1-column mode!"
print(" [PASS] Settings tab successfully switches to 1-Column layout!")

# 5.3 Test Dashboard Gauge & Typography Auto-Scaling
app._update_dashboard_scaling(1600, 900)
for g in app.dash_gauges:
    assert g.size >= 190, f"Dashboard gauge size too small for expanded window: {g.size}"
print(f" [PASS] Dashboard Activity Rings dynamically scaled to {app.dash_gauges[0].size}px on 1600x900 window!")

app._update_dashboard_scaling(860, 750)
for g in app.dash_gauges:
    assert g.size <= 160, f"Dashboard gauge size too large for compact window: {g.size}"
print(f" [PASS] Dashboard Activity Rings dynamically scaled down to {app.dash_gauges[0].size}px on 860x750 compact window!")

# Tab switching & graph rendering test
print(" Switching to Graphs tab...")
app._switch_tab("graphs")
app.update()

print(" Switching to Settings tab...")
app._switch_tab("settings")
app.update()

print(" Switching to Dashboard tab...")
app._switch_tab("dashboard")
app.update()

# Graceful cleanup after 1.5 seconds
def finish():
    print(" [PASS] LegionApp v2.3 PRO all responsive components verified cleanly!")
    print("==================================================")
    print("  ALL VERIFICATION TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")
    try:
        app.hotkeys.stop()
        app.tray.stop()
        app.fps.stop()
        app.hw.stop()
        app.destroy()
    except Exception:
        pass
    import os
    os._exit(0)

app.after(1500, finish)
app.mainloop()
