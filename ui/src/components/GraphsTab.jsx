import React, { useRef, useState, useEffect } from "react";
import SplineChart from "./SplineChart";

export default function GraphsTab({ fpsData = {}, hwData = {} }) {
  const containerRef = useRef(null);
  const [isWide, setIsWide] = useState(true);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setIsWide(entry.contentRect.width >= 880);
      }
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Extract history series
  const cpuClock = hwData.cpu_freq_mhz || 0;
  const gpuClock = hwData.gpu_clock_mhz || 0;
  const histCpuClock = hwData.history_cpu_clock || [];
  const histGpuClock = hwData.history_gpu_clock || [];

  const fps = fpsData.fps || 0;
  const low = fpsData.one_percent_low || 0;
  const histFps = fpsData.history_fps || [];
  const histLow = fpsData.history_one_percent_low || [];

  const cpuTemp = hwData.cpu_temp || 0;
  const gpuTemp = hwData.gpu_temp || 0;
  const histCpuTemp = hwData.history_cpu_temp || [];
  const histGpuTemp = hwData.history_gpu_temp || [];

  const cpuLoad = hwData.cpu_usage || 0;
  const gpuLoad = hwData.gpu_usage || 0;
  const ramLoad = hwData.ram_percent || 0;
  const histCpuLoad = hwData.history_cpu_load || [];
  const histGpuLoad = hwData.history_gpu_load || [];
  const histRamLoad = hwData.history_ram_load || [];

  // Fan RPM series (Dual Fans: CPU & GPU)
  const fanRpm = hwData.fan_speed_rpm || 0;
  const fanCpuRpm = hwData.fan_cpu_rpm || fanRpm;
  const fanGpuRpm = hwData.fan_gpu_rpm || fanRpm;
  const fanPct = hwData.fan_percent || 0;
  const fanCpuPct = hwData.fan_cpu_percent || Math.min(100, Math.max(25, Math.round((fanCpuRpm / 4800) * 100)));
  const fanGpuPct = hwData.fan_gpu_percent || Math.min(100, Math.max(25, Math.round((fanGpuRpm / 4800) * 100)));
  const histFanRpm = hwData.history_fan_rpm || [];
  const histFanCpuRpm = hwData.history_fan_cpu_rpm || [];
  const histFanGpuRpm = hwData.history_fan_gpu_rpm || [];

  return (
    <div ref={containerRef} className="w-full h-full overflow-y-auto p-1 pr-1.5">
      <div
        className={
          isWide
            ? "w-full grid grid-cols-2 gap-3.5 pb-2"
            : "w-full flex flex-col space-y-3.5 pb-2"
        }
      >
        {/* 1. Clock Speed Chart */}
        <div className={isWide ? "w-full h-[220px]" : "w-full h-[185px] flex-shrink-0"}>
          <SplineChart
            title="Xung nhịp CPU & GPU (MHz)"
            yUnit="MHz"
            yMin={0}
            yMax={5000}
            ySteps={5}
            series={[
              { name: "CPU Xung", color: "#FF453A", data: histCpuClock },
              { name: "GPU Xung", color: "#0A84FF", data: histGpuClock },
            ]}
            currentValues={[`${Math.round(cpuClock)} MHz`, `${Math.round(gpuClock)} MHz`]}
          />
        </div>

        {/* 2. FPS & 1% Low Chart */}
        <div className={isWide ? "w-full h-[220px]" : "w-full h-[185px] flex-shrink-0"}>
          <SplineChart
            title="Tốc độ khung hình (FPS & 1% Low)"
            yUnit="FPS"
            yMin={0}
            yMax={240}
            ySteps={4}
            series={[
              { name: "FPS", color: "#30D158", data: histFps },
              { name: "1% Low", color: "#FF9F0A", data: histLow },
            ]}
            currentValues={[`${Math.round(fps)} FPS`, `${Math.round(low)} FPS`]}
          />
        </div>

        {/* 3. Temperatures Chart */}
        <div className={isWide ? "w-full h-[220px]" : "w-full h-[185px] flex-shrink-0"}>
          <SplineChart
            title="Nhiệt độ phần cứng (°C)"
            yUnit="°C"
            yMin={20}
            yMax={100}
            ySteps={4}
            series={[
              { name: "CPU Nhiệt", color: "#FF453A", data: histCpuTemp },
              { name: "GPU Nhiệt", color: "#0A84FF", data: histGpuTemp },
            ]}
            currentValues={[`${Math.round(cpuTemp)}°C`, `${Math.round(gpuTemp)}°C`]}
          />
        </div>

        {/* 4. Hardware Loads Chart */}
        <div className={isWide ? "w-full h-[220px]" : "w-full h-[185px] flex-shrink-0"}>
          <SplineChart
            title="Mức tải tài nguyên hệ thống (%)"
            yUnit="%"
            yMin={0}
            yMax={100}
            ySteps={4}
            series={[
              { name: "CPU Tải", color: "#FF453A", data: histCpuLoad },
              { name: "GPU Tải", color: "#0A84FF", data: histGpuLoad },
              { name: "RAM Tải", color: "#BF5AF2", data: histRamLoad },
            ]}
            currentValues={[`${Math.round(cpuLoad)}%`, `${Math.round(gpuLoad)}%`, `${Math.round(ramLoad)}%`]}
          />
        </div>

        {/* 5. Dual-Fan Speed RPM Chart (Full Width banner) */}
        <div className={isWide ? "col-span-2 w-full h-[220px]" : "w-full h-[185px] flex-shrink-0"}>
          <SplineChart
            title="Hệ thống quạt tản nhiệt kép (Dual-Fan RPM: CPU & GPU)"
            yUnit="RPM"
            yMin={0}
            yMax={5000}
            ySteps={5}
            series={[
              { name: "Quạt CPU", color: "#0A84FF", data: histFanCpuRpm.length ? histFanCpuRpm : histFanRpm },
              { name: "Quạt GPU", color: "#30D158", data: histFanGpuRpm.length ? histFanGpuRpm : histFanRpm },
            ]}
            currentValues={[
              `CPU: ${Math.round(fanCpuRpm)} RPM (${fanCpuPct}%)`,
              `GPU: ${Math.round(fanGpuRpm)} RPM (${fanGpuPct}%)`,
            ]}
          />
        </div>
      </div>
    </div>
  );
}
