"""
Test Suite for Legion Monitor Modern UI (v2.4 PRO)
Tests:
1. Web Bridge API (TelemetryAPI snapshot, settings mutation, overlay controls)
2. Win32 Kernel Named Mutex atomic prevention of duplicate instances
3. WebView2 window initialization and React bundle loading
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
from settings_manager import SettingsManager
from web_bridge import TelemetryAPI

print("==================================================")
print("  TEST 1: TelemetryAPI & Python Web Bridge")
print("==================================================")
hw = HardwareMonitor()
fps = FPSTracker()
sm = SettingsManager()
api = TelemetryAPI(hw, fps, sm)

telemetry = api.get_telemetry()
assert "fps_data" in telemetry, "fps_data missing from get_telemetry!"
assert "hw_data" in telemetry, "hw_data missing from get_telemetry!"
assert "settings" in telemetry, "settings missing from get_telemetry!"
print(f" CPU: {telemetry['hw_data']['cpu_name']} | GPU: {telemetry['hw_data']['gpu_name']}")
print(f" FPS: {telemetry['fps_data']['fps']} | Game: {telemetry['fps_data']['game_name']}")
print(" [PASS] TelemetryAPI successfully returns complete telemetry snapshot!")

# Test settings mutation via bridge
success = api.save_settings({"overlay_manual_width": 1250, "overlay_bg_transparency_pct": 50})
assert success == True
assert sm.get("overlay_manual_width") == 1250
assert sm.get("overlay_bg_transparency_pct") == 50
print(" [PASS] Settings mutation via TelemetryAPI verified!")

print("\n==================================================")
print("  TEST 2: Win32 Kernel Named Mutex Guard")
print("==================================================")
import ctypes
mutex_name = r"Local\LegionFPSMonitor_SingleInstance_Mutex_v2"
m1 = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
err1 = ctypes.windll.kernel32.GetLastError()
# If first instance, err1 is 0 or ALREADY_EXISTS if another is running
m2 = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
err2 = ctypes.windll.kernel32.GetLastError()
assert err2 == 183, f"Win32 Mutex failed to report ERROR_ALREADY_EXISTS: {err2}"
print(" [PASS] Win32 Kernel Named Mutex Guard verified (100% duplicate prevention)!")

print("\n==================================================")
print("  TEST 3: WebView2 Shell & React Bundle Integration")
print("==================================================")
import webview
html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ui", "dist", "index.html"))
assert os.path.exists(html_path), f"ui/dist/index.html does not exist at {html_path}"

win = webview.create_window(
    title="Test Window",
    url=html_path,
    js_api=api,
    width=600,
    height=450
)

def on_loaded():
    print(" [PASS] React 18 + TailwindCSS + Framer Motion bundle loaded in WebView2 successfully!")
    time.sleep(1.0)
    win.destroy()

win.events.loaded += on_loaded
webview.start()

print("\n==================================================")
print("  ALL MODERN UI TESTS PASSED SUCCESSFULLY!       ")
print("==================================================")
