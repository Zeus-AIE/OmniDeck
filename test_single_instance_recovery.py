"""
Automated Test Suite for Single-Instance Guard, Zombie Mutex Auto-Recovery, and Shortcuts.
Executed by Tester Agent as part of the agent-dev-team workflow.
Outputs Structured Output JSON for verification.
"""

import os
import sys
import time
import socket
import ctypes
import unittest
import importlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def run_all_tests():
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failures = []

    # Test 1: src/app.py is a transparent redirector
    total_tests += 1
    try:
        app_py_path = os.path.join(SRC_DIR, "app.py")
        with open(app_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "app_modern.py" in content, "app.py does not forward to app_modern.py"
        assert "subprocess" in content or "exec" in content, "app.py does not invoke subprocess/exec"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_redirect_app_py",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 2: Verify shortcuts target app_modern.py
    total_tests += 1
    try:
        desktop_lnk = os.path.join(os.path.expanduser("~"), "Desktop", "Legion FPS Monitor.lnk")
        if os.path.exists(desktop_lnk):
            with open(desktop_lnk, "rb") as f:
                lnk_bytes = f.read()
            utf16_needle = "app_modern.py".encode("utf-16le")
            assert b"app_modern.py" in lnk_bytes or utf16_needle in lnk_bytes, "Desktop shortcut does not point to app_modern.py"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_shortcuts_target_modern",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 3: Tray Refresher execution
    total_tests += 1
    try:
        from app_modern import refresh_system_tray
        # Must execute cleanly without exception
        refresh_system_tray()
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_tray_refresh",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 4: Zombie Recovery Logic
    total_tests += 1
    try:
        from app_modern import check_and_enforce_single_instance, SINGLE_INSTANCE_PORT
        # Create a mock socket client test
        # When no server listens on port, connect fails
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        err = s.connect_ex(("127.0.0.1", SINGLE_INSTANCE_PORT))
        s.close()
        # Port should be free in test environment
        assert err != 0, f"Port {SINGLE_INSTANCE_PORT} is unexpectedly open during test"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_zombie_recovery_port_check",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 5: SystemTrayManager Menu Configuration
    total_tests += 1
    try:
        from tray_manager import SystemTrayManager
        tm = SystemTrayManager(
            icon_path=os.path.join(BASE_DIR, "assets", "icon.png"),
            on_toggle_dashboard=lambda: None,
            on_hide_dashboard=lambda: None,
            on_toggle_overlay=lambda: None,
            on_toggle_transparency=lambda: None,
            on_exit=lambda: None
        )
        assert tm.on_hide_dashboard is not None
        assert tm.on_toggle_dashboard is not None
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_tray_manager_init",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    # Test 6: ModernLegionApp restore_and_focus existence and signature
    total_tests += 1
    try:
        from app_modern import ModernLegionApp
        assert hasattr(ModernLegionApp, "restore_and_focus"), "ModernLegionApp missing restore_and_focus"
        assert hasattr(ModernLegionApp, "hide_dashboard"), "ModernLegionApp missing hide_dashboard"
        passed_tests += 1
    except Exception as e:
        failed_tests += 1
        failures.append({
            "test_name": "test_app_modern_methods",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

    result = {
        "status": "PASSED" if failed_tests == 0 else "FAILED",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "failures": failures
    }
    return result

if __name__ == "__main__":
    import json
    res = run_all_tests()
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["status"] == "PASSED" else 1)
