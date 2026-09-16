"""
Fan Monitor module for Lenovo Legion and Windows Systems.
Tier 1: Direct Hardware Access via WMI (LENOVO_GAMEZONE_DATA / LENOVO_FAN_METHOD) when elevated.
Tier 2: High-Fidelity Legion Coldfront 3.0 Thermal Model with physical blade momentum & tachometer jitter.
"""

import time
import math
from typing import Dict, Any, Optional

try:
    import clr
    clr.AddReference('System.Management')
    from System.Management import (
        ManagementScope, ManagementObjectSearcher, ObjectQuery,
        ConnectionOptions, ImpersonationLevel
    )
    _DOTNET_AVAILABLE = True
except Exception:
    _DOTNET_AVAILABLE = False


class FanMonitor:
    def __init__(self):
        self._wmi_supported: Optional[bool] = None
        self._last_wmi_check = 0.0
        self._current_rpm = 2100.0
        self._fan1_rpm = 2050
        self._fan2_rpm = 2150
        self._fan_max_rpm = 4900
        self._is_hardware = False

    def query(self, cpu_temp: float, gpu_temp: float, gpu_power_w: float, cpu_usage: float) -> Dict[str, Any]:
        """Returns real-time fan telemetry snapshot."""
        now = time.time()

        # 1. Tier 1: Try Hardware Query if elevated or not yet failed
        if self._wmi_supported is not False or (now - self._last_wmi_check > 60.0):
            self._last_wmi_check = now
            hw_data = self._try_read_hardware_wmi()
            if hw_data is not None:
                self._wmi_supported = True
                self._is_hardware = True
                f1, f2, fmax = hw_data
                self._fan1_rpm = f1
                self._fan2_rpm = f2
                self._fan_max_rpm = max(3500, fmax) if fmax > 0 else 4900
                avg_rpm = (f1 + f2) / 2.0 if (f1 > 0 or f2 > 0) else f1
                self._current_rpm = avg_rpm
                pct = int(min(100, max(0, (self._current_rpm / self._fan_max_rpm) * 100)))
                return {
                    "fan_speed_rpm": int(self._current_rpm),
                    "fan_speed_pct": pct,
                    "fan_cpu_rpm": int(f1),
                    "fan_gpu_rpm": int(f2),
                    "fan_max_rpm": int(self._fan_max_rpm),
                    "fan_is_hardware": True
                }
            else:
                self._wmi_supported = False
                self._is_hardware = False

        # 2. Tier 2: Legion Coldfront 3.0 Thermal Model
        target_rpm = self._calc_legion_thermal_rpm(cpu_temp, gpu_temp, gpu_power_w, cpu_usage)

        # Exponential Moving Average (EMA) for physical fan blade inertia
        alpha = 0.18
        self._current_rpm = self._current_rpm * (1.0 - alpha) + target_rpm * alpha

        # Natural physical motor tachometer jitter (+- 15 RPM)
        jitter = math.sin(now * 2.7) * 12.0 + math.cos(now * 4.3) * 8.0
        final_rpm = max(0, int(self._current_rpm + jitter))

        # CPU vs GPU fan offset based on thermal source
        c_weight = max(0.0, min(1.0, (cpu_temp - 40.0) / 45.0))
        g_weight = max(0.0, min(1.0, (gpu_temp - 40.0) / 45.0 + (gpu_power_w / 130.0) * 0.25))
        diff = (g_weight - c_weight) * 180.0

        self._fan1_rpm = max(0, int(final_rpm - diff / 2))
        self._fan2_rpm = max(0, int(final_rpm + diff / 2))
        pct = int(min(100, max(0, (final_rpm / self._fan_max_rpm) * 100)))

        return {
            "fan_speed_rpm": final_rpm,
            "fan_speed_pct": pct,
            "fan_cpu_rpm": self._fan1_rpm,
            "fan_gpu_rpm": self._fan2_rpm,
            "fan_max_rpm": self._fan_max_rpm,
            "fan_is_hardware": False
        }

    def _try_read_hardware_wmi(self) -> Optional[tuple]:
        """Direct C-API / .NET query to Lenovo EC via WMI."""
        if not _DOTNET_AVAILABLE:
            return None
        try:
            options = ConnectionOptions()
            options.Impersonation = ImpersonationLevel.Impersonate
            options.EnablePrivileges = True
            scope = ManagementScope(r"root\WMI", options)
            scope.Connect()

            query = ObjectQuery("SELECT * FROM LENOVO_GAMEZONE_DATA")
            searcher = ManagementObjectSearcher(scope, query)
            for obj in searcher.Get():
                out1 = obj.InvokeMethod("GetFan1Speed", None)
                out2 = obj.InvokeMethod("GetFan2Speed", None)
                out_max = obj.InvokeMethod("GetFanMaxSpeed", None)
                f1 = int(out1["Data"]) if out1 and "Data" in out1 else 0
                f2 = int(out2["Data"]) if out2 and "Data" in out2 else 0
                fmax = int(out_max["Data"]) if out_max and "Data" in out_max else 4900
                if f1 > 0 or f2 > 0:
                    return (f1, f2, fmax)
        except Exception:
            pass
        return None

    def _calc_legion_thermal_rpm(self, c_temp: float, g_temp: float, g_watts: float, c_load: float) -> float:
        """Legion Coldfront 3.0 dual-fan curve."""
        # Effective thermal temperature combining CPU & GPU heat dissipation
        t_effective = max(c_temp, g_temp) + (min(130.0, g_watts) / 130.0) * 6.0

        if t_effective < 42.0:
            # Silent / Light Idle
            return 1400.0 + (t_effective - 30.0) * 35.0
        elif t_effective < 55.0:
            # Low Load (Web/Video)
            ratio = (t_effective - 42.0) / 13.0
            return 1820.0 + ratio * 580.0
        elif t_effective < 70.0:
            # Medium Gaming / Compilation
            ratio = (t_effective - 55.0) / 15.0
            return 2400.0 + ratio * 1050.0
        elif t_effective < 84.0:
            # Heavy Gaming / Benchmark
            ratio = (t_effective - 70.0) / 14.0
            return 3450.0 + ratio * 950.0
        else:
            # Maximum Boost / Thermal ceiling
            ratio = min(1.0, (t_effective - 84.0) / 12.0)
            return 4400.0 + ratio * 480.0
