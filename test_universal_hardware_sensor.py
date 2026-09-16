"""
Automated Test Suite for Universal Hardware Sensor Engine (v2.5 PRO).
Tests hardware detection, multi-vendor abstraction, dynamic registry queries,
and web bridge telemetry integration.
"""

import os
import sys
import json
import unittest

# Ensure src is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from universal_hardware import (
    get_system_identity,
    get_cpu_specs,
    get_all_gpus,
    get_gpu_short_name,
    UniversalHardwareManager
)
from hw_monitor import HardwareMonitor
from fps_tracker import FPSTracker
from settings_manager import SettingsManager
from web_bridge import TelemetryAPI


class TestUniversalHardwareSensor(unittest.TestCase):
    def test_01_system_identity_detection(self):
        """Verify dynamic detection of System Manufacturer, Model, and Family."""
        identity = get_system_identity()
        self.assertIsInstance(identity, dict)
        self.assertTrue(len(identity["manufacturer"]) > 0)
        self.assertTrue(len(identity["model"]) > 0)
        self.assertTrue(len(identity["short_brand"]) > 0)
        self.assertTrue(len(identity["display_name"]) > 0)
        self.assertIsInstance(identity["is_laptop"], bool)
        print(f"\n[PASS] Detected System: {identity['display_name']} ({identity['short_brand']}, Laptop={identity['is_laptop']})")

    def test_02_cpu_specs_detection(self):
        """Verify dynamic detection of real CPU name, base clock, cores, and threads."""
        specs = get_cpu_specs()
        self.assertIsInstance(specs, dict)
        self.assertTrue(len(specs["name"]) > 0)
        self.assertTrue(len(specs["short_name"]) > 0)
        self.assertIn(specs["vendor"], ["AMD", "Intel", "Generic"])
        self.assertGreaterEqual(specs["base_mhz"], 800.0)
        self.assertGreaterEqual(specs["cores"], 1)
        self.assertGreaterEqual(specs["threads"], specs["cores"])
        print(f"[PASS] Detected CPU: {specs['name']} | Short: {specs['short_name']} | Base: {specs['base_mhz']} MHz | Cores: {specs['cores']}C/{specs['threads']}T")

    def test_03_gpu_scanner_and_short_names(self):
        """Verify GPU scanning in Windows Registry and friendly short name generator."""
        gpus = get_all_gpus()
        self.assertIsInstance(gpus, list)
        self.assertTrue(len(gpus) > 0, "At least one GPU/Display adapter should be detected on Windows")
        
        primary_gpu = gpus[0]
        short_name = get_gpu_short_name(primary_gpu["name"])
        self.assertTrue(len(short_name) > 0)
        # Test cleaning logic
        self.assertEqual(get_gpu_short_name("NVIDIA GeForce RTX 3060 Laptop GPU"), "RTX 3060 Laptop")
        self.assertEqual(get_gpu_short_name("AMD Radeon RX 6700 XT Graphics"), "RX 6700 XT")
        self.assertEqual(get_gpu_short_name("Intel(R) Arc(TM) A770 Graphics"), "Arc A770")
        print(f"[PASS] Detected {len(gpus)} GPU(s). Primary: {primary_gpu['name']} -> Short: '{short_name}'")

    def test_04_universal_hardware_manager(self):
        """Verify UniversalHardwareManager aggregates hardware summary correctly."""
        mgr = UniversalHardwareManager()
        summary = mgr.get_summary()
        self.assertIn("system_manufacturer", summary)
        self.assertIn("system_display_name", summary)
        self.assertIn("cpu_name", summary)
        self.assertIn("cpu_short_name", summary)
        self.assertIn("cpu_base_mhz", summary)
        self.assertIn("gpu_name", summary)
        self.assertIn("gpu_short_name", summary)
        self.assertIn("all_gpus", summary)
        print(f"[PASS] Hardware Summary generated successfully: {summary['system_display_name']}")

    def test_05_hardware_monitor_snapshot_rich_metadata(self):
        """Verify HardwareMonitor incorporates real universal hardware data into snapshot."""
        hw = HardwareMonitor()
        snapshot = hw.get_snapshot()
        
        # Verify required universal fields
        required_fields = [
            "system_manufacturer", "system_model", "system_family",
            "system_display_name", "system_short_brand", "is_laptop",
            "cpu_name", "cpu_short_name", "cpu_vendor", "cpu_base_mhz",
            "cpu_cores", "cpu_threads", "gpu_name", "gpu_short_name",
            "all_gpus", "ram_total_gb", "fan_mode"
        ]
        for f in required_fields:
            self.assertIn(f, snapshot, f"Field '{f}' missing from HardwareMonitor snapshot")
            
        # RAM should be actual physical RAM > 2 GB
        self.assertGreater(snapshot["ram_total_gb"], 2.0)
        # CPU base clock should be reasonable
        self.assertGreater(snapshot["cpu_base_mhz"], 800.0)
        print(f"[PASS] HardwareMonitor Snapshot validated: RAM={snapshot['ram_total_gb']}GB, FanMode='{snapshot['fan_mode']}'")

    def test_06_web_bridge_telemetry_integration(self):
        """Verify TelemetryAPI correctly packages hardware snapshot for React UI."""
        hw = HardwareMonitor()
        fps = FPSTracker()
        settings = SettingsManager()
        api = TelemetryAPI(hw, fps, settings)
        
        payload = api.get_telemetry()
        self.assertIn("hw_data", payload)
        self.assertIn("fps_data", payload)
        self.assertIn("settings", payload)
        
        hw_data = payload["hw_data"]
        self.assertEqual(hw_data["system_display_name"], hw.system_display_name)
        self.assertEqual(hw_data["cpu_short_name"], hw.cpu_short_name)
        self.assertEqual(hw_data["gpu_short_name"], hw.gpu_short_name)
        print(f"[PASS] Web Bridge TelemetryAPI successfully delivers universal hardware to Frontend!")

    def test_07_frontend_build_artifact_exists(self):
        """Verify React production bundle was built and exists in ui/dist."""
        dist_html = os.path.join(BASE_DIR, "ui", "dist", "index.html")
        self.assertTrue(os.path.exists(dist_html), "ui/dist/index.html must exist")
        self.assertGreater(os.path.getsize(dist_html), 100)
        print("[PASS] Frontend React 18 production bundle verified in ui/dist!")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUniversalHardwareSensor)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate Agent Dev Team Structured Output JSON
    failures_list = []
    for test, trace in result.failures + result.errors:
        failures_list.append({
            "test_name": str(test),
            "error_type": "AssertionError" if result.failures else "ExecutionError",
            "location_line": 0,
            "error_message": trace.strip().split("\n")[-1],
            "reproduction_input": {},
            "suggested_fix": "Inspect sensor query fallback"
        })
        
    structured_json = {
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "total_tests": result.testsRun,
        "passed_tests": result.testsRun - len(result.failures) - len(result.errors),
        "failed_tests": len(result.failures) + len(result.errors),
        "failures": failures_list
    }
    
    print("\n=== AGENT_DEV_TEAM_TEST_RESULT ===")
    print(json.dumps(structured_json, indent=2))
    sys.exit(0 if result.wasSuccessful() else 1)
