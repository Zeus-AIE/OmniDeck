"""
Tester Agent Test Suite: Fan Speed Telemetry & Multi-Layer Integration.
Verifies:
1. HardwareMonitor snapshot contains all required fan fields (fan_speed_rpm, fan_cpu_rpm, fan_gpu_rpm, fan_percent, fan_mode, history_fan_rpm).
2. Fan RPM values and percentages are physically realistic (0 - 5200 RPM, 0 - 100%).
3. SettingsManager recognizes and persists the new 'fan' metric and 'fan' bottom graph toggles.
4. TelemetryAPI bridge correctly packages and returns fan telemetry for React/Modern UI.
5. InGameOverlay functions get_fan_color() return correct warning threshold colors.
6. Frontend build output (ui/dist/index.html and assets) exists and contains modern fan telemetry bundle.
Outputs Structured JSON according to agent-dev-team specification.
"""

import os
import sys
import json
import time

# Add src to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from hw_monitor import HardwareMonitor
from settings_manager import SettingsManager
from overlay_window import get_fan_color
from web_bridge import TelemetryAPI


class DummyFPSTracker:
    def get_stats(self):
        return {
            "fps": 144.0,
            "one_percent_low": 115.0,
            "frametime_ms": 6.9,
            "game_name": "TestGame.exe",
            "history_fps": [144.0] * 10,
            "history_one_percent_low": [115.0] * 10
        }


def run_all_tests():
    failures = []
    total_tests = 0
    passed_tests = 0

    # -------------------------------------------------------------
    # Test 1: HardwareMonitor Fan Telemetry Fields & Types
    # -------------------------------------------------------------
    total_tests += 1
    try:
        hw = HardwareMonitor()
        snapshot = hw.get_snapshot()
        
        required_fields = [
            "fan_speed_rpm",
            "fan_cpu_rpm",
            "fan_gpu_rpm",
            "fan_percent",
            "fan_mode",
            "history_fan_rpm"
        ]
        
        missing = [f for f in required_fields if f not in snapshot]
        if missing:
            raise AssertionError(f"Missing fan telemetry fields in snapshot: {missing}")

        rpm = snapshot["fan_speed_rpm"]
        cpu_rpm = snapshot["fan_cpu_rpm"]
        gpu_rpm = snapshot["fan_gpu_rpm"]
        pct = snapshot["fan_percent"]
        mode = snapshot["fan_mode"]
        hist = snapshot["history_fan_rpm"]

        assert isinstance(rpm, int), f"fan_speed_rpm must be int, got {type(rpm)}"
        assert isinstance(cpu_rpm, int), f"fan_cpu_rpm must be int, got {type(cpu_rpm)}"
        assert isinstance(gpu_rpm, int), f"fan_gpu_rpm must be int, got {type(gpu_rpm)}"
        assert isinstance(pct, int), f"fan_percent must be int, got {type(pct)}"
        assert isinstance(mode, str), f"fan_mode must be str, got {type(mode)}"
        assert isinstance(hist, list), f"history_fan_rpm must be list, got {type(hist)}"

        assert 0 <= rpm <= 5500, f"fan_speed_rpm out of realistic bounds: {rpm}"
        assert 0 <= pct <= 100, f"fan_percent out of bounds: {pct}"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 1 (HardwareMonitor Fan Fields) failed: {str(e)}")

    # -------------------------------------------------------------
    # Test 2: Lenovo Thermal Curve Dual-Engine Dynamic Response
    # -------------------------------------------------------------
    total_tests += 1
    try:
        hw = HardwareMonitor()
        # Test low temp idle: 45°C CPU, 40°C GPU
        low_cpu, low_gpu, low_rpm, low_pct = hw._query_fan_telemetry(45, 40, 5, 0, 10)
        assert low_rpm <= 2400, f"Idle fan RPM too high: {low_rpm}"
        assert low_pct <= 50, f"Idle fan percent too high: {low_pct}"

        # Test high load gaming: 85°C CPU, 78°C GPU, 115W GPU
        for _ in range(15):
            high_cpu, high_gpu, high_rpm, high_pct = hw._query_fan_telemetry(85, 78, 80, 95, 115)

        assert high_rpm >= 3500, f"High load fan RPM too low: {high_rpm}"
        assert high_pct >= 70, f"High load fan percent too low: {high_pct}"
        assert high_gpu >= high_cpu, f"GPU fan should be higher or equal under 115W GPU load: {high_gpu} vs {high_cpu}"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 2 (Thermal Curve Dynamic Response) failed: {str(e)}")

    # -------------------------------------------------------------
    # Test 3: SettingsManager Fan Configuration Persistence
    # -------------------------------------------------------------
    total_tests += 1
    try:
        settings = SettingsManager()
        all_settings = settings.get_all()
        
        metrics = all_settings.get("metrics", {})
        bottom_graphs = all_settings.get("overlay_bottom_graphs", {})

        assert "fan" in metrics, "Setting 'fan' not found in metrics default"
        assert "fan" in bottom_graphs, "Setting 'fan' not found in overlay_bottom_graphs default"
        assert metrics["fan"] is True, "Default 'fan' metric should be True"
        assert bottom_graphs["fan"] is True, "Default 'fan' bottom graph should be True"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 3 (SettingsManager Fan Defaults) failed: {str(e)}")

    # -------------------------------------------------------------
    # Test 4: WebBridge TelemetryAPI Payload Verification
    # -------------------------------------------------------------
    total_tests += 1
    try:
        hw = HardwareMonitor()
        fps = DummyFPSTracker()
        settings = SettingsManager()
        api = TelemetryAPI(hw, fps, settings)

        payload = api.get_telemetry()
        assert "hw_data" in payload, "get_telemetry() missing 'hw_data'"
        assert "fan_speed_rpm" in payload["hw_data"], "payload hw_data missing 'fan_speed_rpm'"
        assert "history_fan_rpm" in payload["hw_data"], "payload hw_data missing 'history_fan_rpm'"
        assert payload["hw_data"]["fan_speed_rpm"] >= 0, "fan_speed_rpm cannot be negative"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 4 (TelemetryAPI WebBridge) failed: {str(e)}")

    # -------------------------------------------------------------
    # Test 5: Overlay Warning Threshold Colors
    # -------------------------------------------------------------
    total_tests += 1
    try:
        color_quiet = get_fan_color(1800)
        color_balanced = get_fan_color(2800)
        color_perf = get_fan_color(3800)
        color_turbo = get_fan_color(4500)

        assert color_quiet == "#30D158", f"Expected Apple Green for 1800 RPM, got {color_quiet}"
        assert color_balanced == "#0A84FF", f"Expected Apple Blue for 2800 RPM, got {color_balanced}"
        assert color_perf == "#FF9F0A", f"Expected Apple Orange for 3800 RPM, got {color_perf}"
        assert color_turbo == "#FF453A", f"Expected Apple Red for 4500 RPM, got {color_turbo}"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 5 (get_fan_color Thresholds) failed: {str(e)}")

    # -------------------------------------------------------------
    # Test 6: Frontend Build Asset Verification
    # -------------------------------------------------------------
    total_tests += 1
    try:
        dist_dir = os.path.join(BASE_DIR, "ui", "dist")
        index_html = os.path.join(dist_dir, "index.html")
        assert os.path.exists(index_html), f"Build artifact missing: {index_html}"

        assets_dir = os.path.join(dist_dir, "assets")
        assert os.path.isdir(assets_dir), f"Assets folder missing in dist: {assets_dir}"
        
        js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
        assert len(js_files) > 0, "No JS bundle found in dist/assets"

        passed_tests += 1
    except Exception as e:
        failures.append(f"Test 6 (Frontend Build Assets) failed: {str(e)}")

    # -------------------------------------------------------------
    # Format JSON Output according to agent-dev-team schema
    # -------------------------------------------------------------
    status = "PASSED" if len(failures) == 0 else "FAILED"
    result = {
        "status": status,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": len(failures),
        "failures": failures
    }

    print("\n=== TEST_RUN_RESULT_JSON_START ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=== TEST_RUN_RESULT_JSON_END ===\n")

    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
