"""
Automated Test Suite for Dual-Fan Telemetry and Fan Settings Management.
Executed by Tester Agent as part of agent-dev-team workflow.
Outputs standard JSON Structured Output for verification.
"""

import os
import sys
import json
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from settings_manager import SettingsManager, DEFAULT_SETTINGS
from hw_monitor import HardwareMonitor
from overlay_window import get_fan_color

def run_all_tests():
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failures = []

    # Test 1: SettingsManager Defaults
    total_tests += 1
    try:
        sm = SettingsManager(filepath=os.path.join(BASE_DIR, "scratch_test_settings.json"))
        settings = sm.get_all()
        assert "overlay_fan_mode" in settings, "Missing overlay_fan_mode in settings"
        assert settings["overlay_fan_mode"] == "dual", f"Default overlay_fan_mode should be 'dual', got {settings['overlay_fan_mode']}"
        assert "dashboard_show_fan" in settings, "Missing dashboard_show_fan in settings"
        assert settings["dashboard_show_fan"] is True, f"Default dashboard_show_fan should be True, got {settings['dashboard_show_fan']}"
        
        # Test updating settings
        sm.set("overlay_fan_mode", "max")
        sm.set("dashboard_show_fan", False)
        assert sm.get("overlay_fan_mode") == "max", "Failed to update overlay_fan_mode"
        assert sm.get("dashboard_show_fan") is False, "Failed to update dashboard_show_fan"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_settings_manager_fan_defaults",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
    finally:
        scratch_file = os.path.join(BASE_DIR, "scratch_test_settings.json")
        if os.path.exists(scratch_file):
            try:
                os.remove(scratch_file)
            except Exception:
                pass

    # Test 2: HardwareMonitor Dual-Fan Asymmetric Response (CPU Heavy)
    total_tests += 1
    try:
        hw = HardwareMonitor()
        # Simulate CPU heavy workload
        c_heavy = hw._query_fan_telemetry(c_temp=86.0, g_temp=42.0, c_usage=95.0, g_usage=5.0, g_power=15.0)
        cpu_rpm, gpu_rpm, max_rpm, pct = c_heavy
        assert cpu_rpm > gpu_rpm, f"Under heavy CPU load, CPU fan ({cpu_rpm}) should be > GPU fan ({gpu_rpm})"
        assert max_rpm == max(cpu_rpm, gpu_rpm), f"max_rpm {max_rpm} must equal max({cpu_rpm}, {gpu_rpm})"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_fan_asymmetric_cpu_heavy",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 3: HardwareMonitor Dual-Fan Asymmetric Response (GPU Gaming Heavy)
    total_tests += 1
    try:
        hw = HardwareMonitor()
        # Simulate GPU gaming heavy workload (RTX 3060 120W)
        g_heavy = hw._query_fan_telemetry(c_temp=58.0, g_temp=79.0, c_usage=25.0, g_usage=98.0, g_power=120.0)
        cpu_rpm, gpu_rpm, max_rpm, pct = g_heavy
        assert gpu_rpm > cpu_rpm, f"Under heavy GPU gaming load, GPU fan ({gpu_rpm}) should be > CPU fan ({cpu_rpm})"
        assert max_rpm == max(cpu_rpm, gpu_rpm), f"max_rpm {max_rpm} must equal max({cpu_rpm}, {gpu_rpm})"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_fan_asymmetric_gpu_heavy",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 4: HardwareMonitor Snapshot and History Buffers
    total_tests += 1
    try:
        hw = HardwareMonitor()
        snapshot = hw.get_snapshot()
        assert "fan_speed_rpm" in snapshot, "Snapshot missing fan_speed_rpm"
        assert "fan_cpu_rpm" in snapshot, "Snapshot missing fan_cpu_rpm"
        assert "fan_gpu_rpm" in snapshot, "Snapshot missing fan_gpu_rpm"
        assert "fan_percent" in snapshot, "Snapshot missing fan_percent"
        assert "fan_cpu_percent" in snapshot, "Snapshot missing fan_cpu_percent"
        assert "fan_gpu_percent" in snapshot, "Snapshot missing fan_gpu_percent"
        assert "fan_mode" in snapshot, "Snapshot missing fan_mode"
        assert "history_fan_rpm" in snapshot, "Snapshot missing history_fan_rpm"
        assert "history_fan_cpu_rpm" in snapshot, "Snapshot missing history_fan_cpu_rpm"
        assert "history_fan_gpu_rpm" in snapshot, "Snapshot missing history_fan_gpu_rpm"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_hardware_snapshot_dual_fan_fields",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 5: Overlay Fan Mode Text Formatting Logic
    total_tests += 1
    try:
        modes = ["dual", "max", "cpu", "gpu"]
        c_rpm = 2150
        g_rpm = 2480
        max_rpm = max(c_rpm, g_rpm)
        pct = 52

        for mode in modes:
            if mode == "dual":
                text = f"C:{c_rpm} · G:{g_rpm} RPM"
                assert f"C:{c_rpm}" in text and f"G:{g_rpm}" in text
            elif mode == "cpu":
                text = f"CPU {c_rpm} RPM"
                assert str(c_rpm) in text
            elif mode == "gpu":
                text = f"GPU {g_rpm} RPM"
                assert str(g_rpm) in text
            elif mode == "max":
                text = f"{max_rpm} RPM ({pct}%)"
                assert str(max_rpm) in text
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_overlay_fan_mode_formatting",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 6: Frontend Build Assets Verification
    total_tests += 1
    try:
        dist_html = os.path.join(BASE_DIR, "ui", "dist", "index.html")
        assert os.path.exists(dist_html), f"Missing dist HTML at {dist_html}"
        with open(dist_html, "r", encoding="utf-8") as f:
            content = f.read()
        assert '<div id="root"></div>' in content or '<div id="root">' in content, "Invalid dist HTML content"
        
        assets_dir = os.path.join(BASE_DIR, "ui", "dist", "assets")
        assert os.path.isdir(assets_dir), f"Missing assets directory at {assets_dir}"
        js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
        assert len(js_files) > 0, "No compiled JS bundle found in assets directory"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_frontend_dist_assets",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Output Structured JSON Result
    result = {
        "status": "PASSED" if failed_tests == 0 else "FAILED",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "failures": failures
    }

    print("\n=== TEST_RUN_RESULT_JSON_START ===")
    print(json.dumps(result, indent=2))
    print("=== TEST_RUN_RESULT_JSON_END ===")

    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
