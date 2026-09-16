"""
Automated Test Suite for Overlay Layouts, Metric Toggles, Auto-Fit, and Dual Transparency.
Executed by Tester Agent as part of the agent-dev-team workflow.
Outputs Structured Output JSON for verification.
"""

import os
import sys
import json
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from settings_manager import SettingsManager
from overlay_window import InGameOverlay
from web_bridge import TelemetryAPI


def run_all_tests():
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failures = []

    # Initialize headless Tkinter root
    root = tk.Tk()
    root.withdraw()

    test_settings_path = os.path.join(BASE_DIR, "scratch_test_overlay_settings.json")
    sm = SettingsManager(filepath=test_settings_path)

    overlay = InGameOverlay(master=root, settings_mgr=sm)
    overlay.withdraw()

    # Test 1: Compact Layout Metric Toggles
    total_tests += 1
    try:
        sm.set("overlay_layout", "compact")
        sm.set("metrics", {
            "app_name": False,
            "fps": True,
            "one_percent_low": False,
            "frametime": False,
            "cpu_temp": True,
            "cpu_usage": False,
            "cpu_clock": False,
            "gpu_temp": False,
            "gpu_usage": False,
            "gpu_clock": False,
            "gpu_power": False,
            "ram": True,
            "network": False,
            "fan": False
        })
        overlay.apply_settings(force_rebuild=True)

        # fps and cpu_temp and ram_val should exist
        assert "fps_val" in overlay.labels, "fps_val missing in compact layout"
        assert "cpu_temp" in overlay.labels, "cpu_temp missing in compact layout"
        assert "ram_val" in overlay.labels, "ram_val missing in compact layout"

        # Disabled metrics must NOT exist in labels!
        assert "app" not in overlay.labels, "app label should be disabled in compact"
        assert "low_val" not in overlay.labels, "1% low label should be disabled in compact"
        assert "gpu_temp" not in overlay.labels, "gpu_temp label should be disabled in compact"
        assert "fan_val" not in overlay.labels, "fan_val label should be disabled in compact"
        assert "net_down" not in overlay.labels, "net_down label should be disabled in compact"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_compact_layout_metric_toggles",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 2: Corner Layout Metric Toggles
    total_tests += 1
    try:
        sm.set("overlay_layout", "corner")
        sm.set("metrics", {
            "app_name": True,
            "fps": False,
            "one_percent_low": False,
            "frametime": False,
            "cpu_temp": True,
            "cpu_usage": True,
            "cpu_clock": False,
            "gpu_temp": True,
            "gpu_usage": True,
            "gpu_clock": False,
            "gpu_power": True,
            "ram": False,
            "network": True,
            "fan": True
        })
        overlay.apply_settings(force_rebuild=True)

        assert "app" in overlay.labels, "app missing in corner layout"
        assert "cpu_temp" in overlay.labels, "cpu_temp missing in corner layout"
        assert "gpu_temp" in overlay.labels, "gpu_temp missing in corner layout"
        assert "gpu_power" in overlay.labels, "gpu_power missing in corner layout"
        assert "net_down" in overlay.labels, "net_down missing in corner layout"
        assert "fan_val" in overlay.labels, "fan_val missing in corner layout"

        # Disabled metrics must NOT exist
        assert "fps_val" not in overlay.labels, "fps_val should be disabled in corner layout"
        assert "ram_val" not in overlay.labels, "ram_val should be disabled in corner layout"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_corner_layout_metric_toggles",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 3: Vertical Layout Metric Toggles
    total_tests += 1
    try:
        sm.set("overlay_layout", "vertical")
        sm.set("metrics", {
            "app_name": True,
            "fps": True,
            "one_percent_low": True,
            "frametime": False,
            "cpu_temp": False,
            "cpu_usage": False,
            "cpu_clock": False,
            "gpu_temp": True,
            "gpu_usage": False,
            "gpu_clock": False,
            "gpu_power": False,
            "ram": True,
            "network": False,
            "fan": True
        })
        overlay.apply_settings(force_rebuild=True)

        assert "fps_val" in overlay.labels, "fps_val missing in vertical layout"
        assert "low_val" in overlay.labels, "low_val missing in vertical layout"
        assert "gpu_temp" in overlay.labels, "gpu_temp missing in vertical layout"
        assert "ram_val" in overlay.labels, "ram_val missing in vertical layout"
        assert "fan_val" in overlay.labels, "fan_val missing in vertical layout"

        # Disabled metrics must NOT exist
        assert "cpu_temp" not in overlay.labels, "cpu_temp should be disabled in vertical layout"
        assert "net_down" not in overlay.labels, "net_down should be disabled in vertical layout"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_vertical_layout_metric_toggles",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 4: Horizontal Layout Metric Toggles & Deck Filtering
    total_tests += 1
    try:
        sm.set("overlay_layout", "horizontal")
        sm.set("overlay_show_bottom_graphs", True)
        sm.set("overlay_bottom_graphs", {
            "fps": True,
            "cpu": False,
            "gpu": True,
            "ram_net": False,
            "fan": True
        })
        overlay.apply_settings(force_rebuild=True)

        assert "fps" in overlay.deck_graphs, "fps deck graph missing"
        assert "gpu" in overlay.deck_graphs, "gpu deck graph missing"
        assert "fan" in overlay.deck_graphs, "fan deck graph missing"
        assert "cpu" not in overlay.deck_graphs, "cpu deck graph should be disabled"
        assert "ram_net" not in overlay.deck_graphs, "ram_net deck graph should be disabled"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_horizontal_layout_and_deck_filtering",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 5: Dual Independent Transparency Setters with Real Window State Validation
    total_tests += 1
    try:
        # Deiconify overlay so it is viewable
        overlay.deiconify()
        root.update()

        # Background transparency 42%
        overlay.set_bg_transparency_pct(42)
        root.update()
        assert overlay.bg_transparency_pct == 42
        assert sm.get("overlay_bg_transparency_pct") == 42
        assert overlay.bg_win.winfo_viewable() == 1, "bg_win must be viewable at 42%"
        assert len(overlay.bg_win.winfo_children()) > 0, "bg_win must have child frames"
        assert abs(overlay.bg_win.attributes("-alpha") - 0.42) < 0.01

        # Pure HUD 0% (Background completely hidden)
        overlay.set_bg_transparency_pct(0)
        root.update()
        assert overlay.bg_win.winfo_viewable() == 0, "bg_win must be hidden at 0%"

        # Re-activate to 75%
        overlay.set_bg_transparency_pct(75)
        root.update()
        assert overlay.bg_win.winfo_viewable() == 1, "bg_win must be re-shown at 75%"
        assert abs(overlay.bg_win.attributes("-alpha") - 0.75) < 0.01

        # Text transparency
        overlay.set_text_transparency_pct(78)
        root.update()
        assert overlay.text_transparency_pct == 78
        assert sm.get("overlay_text_transparency_pct") == 78
        assert abs(overlay.attributes("-alpha") - 0.78) < 0.01

        # Boundaries
        overlay.set_bg_transparency_pct(150)
        root.update()
        assert overlay.bg_transparency_pct == 100
        assert abs(overlay.bg_win.attributes("-alpha") - 1.0) < 0.01

        overlay.set_text_transparency_pct(10)
        root.update()
        assert overlay.text_transparency_pct == 20
        assert abs(overlay.attributes("-alpha") - 0.20) < 0.01

        # Withdraw overlay when done
        overlay.withdraw()
        root.update()
        assert overlay.bg_win.winfo_viewable() == 0, "bg_win must follow overlay withdrawal"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_dual_transparency_setters",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 6: Accurate Auto-Fit Geometry on All 4 Layouts
    total_tests += 1
    try:
        for layout_name in ["horizontal", "compact", "corner", "vertical"]:
            sm.set("overlay_layout", layout_name)
            sm.set("overlay_width_mode", "auto")
            overlay.apply_settings(force_rebuild=True)

            assert overlay.current_w >= 140, f"Width too small for {layout_name}: {overlay.current_w}"
            assert overlay.current_h >= 30, f"Height too small for {layout_name}: {overlay.current_h}"

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_accurate_auto_fit_geometry_all_layouts",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 7: TelemetryAPI Bridge Transparency Methods
    total_tests += 1
    try:
        api = TelemetryAPI(
            hw_monitor=None,
            fps_tracker=None,
            settings_mgr=sm,
            overlay=overlay
        )
        assert api.set_bg_transparency(55) == True
        assert sm.get("overlay_bg_transparency_pct") == 55

        assert api.set_text_transparency(92) == True
        assert sm.get("overlay_text_transparency_pct") == 92

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_telemetry_api_bridge_transparency",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 8: Dynamic update_metrics respects all layouts without crashing
    total_tests += 1
    try:
        mock_fps = {
            "fps": 165.0,
            "one_percent_low": 120.0,
            "frametime_ms": 6.0,
            "game_name": "Cyberpunk2077.exe"
        }
        mock_hw = {
            "cpu_temp": 65.0,
            "cpu_usage": 45.0,
            "cpu_freq_mhz": 4200.0,
            "gpu_temp": 60.0,
            "gpu_usage": 88.0,
            "gpu_clock_mhz": 1850.0,
            "gpu_power_w": 115.0,
            "ram_used_gb": 12.0,
            "ram_percent": 75.0,
            "net_down_str": "15 MB/s",
            "net_up_str": "2 MB/s",
            "fan_speed_rpm": 3200,
            "fan_cpu_rpm": 3100,
            "fan_gpu_rpm": 3300,
            "fan_percent": 65
        }

        for layout_name in ["horizontal", "compact", "corner", "vertical"]:
            sm.set("overlay_layout", layout_name)
            overlay.apply_settings(force_rebuild=True)
            overlay.update_metrics(mock_fps, mock_hw)

        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_update_metrics_execution_all_layouts",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Cleanup test artifacts
    try:
        overlay.destroy()
        root.destroy()
        if os.path.exists(test_settings_path):
            os.remove(test_settings_path)
    except Exception:
        pass

    result = {
        "status": "PASSED" if failed_tests == 0 else "FAILED",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "failures": failures
    }
    return result


if __name__ == "__main__":
    res = run_all_tests()
    print("\n=== TEST_RUN_RESULT_JSON_START ===")
    print(json.dumps(res, indent=2))
    print("=== TEST_RUN_RESULT_JSON_END ===\n")
    sys.exit(0 if res["status"] == "PASSED" else 1)
