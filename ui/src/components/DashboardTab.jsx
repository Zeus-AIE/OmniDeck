import React, { useRef, useState, useEffect } from "react";
import { motion } from "framer-motion";
import ActivityRing from "./ActivityRing";

export default function DashboardTab({ fpsData = {}, hwData = {}, settings = {} }) {
  const containerRef = useRef(null);
  const [gaugeSize, setGaugeSize] = useState(150);

  const showFanSection = settings.dashboard_show_fan ?? true;

  // Dynamic responsive scaling for Activity Rings
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        const cellW = width / 2;
        const fanHeight = showFanSection ? 155 : 0;
        const cellH = Math.max(160, (height - fanHeight) / 2);
        const target = Math.max(120, Math.min(195, Math.min(cellW * 0.40, cellH * 0.44)));
        setGaugeSize(Math.round(target));
      }
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, [showFanSection]);

  // 1. FPS Metrics & Color
  const fpsVal = fpsData.fps || 0;
  const oneLow = fpsData.one_percent_low || 0;
  const frametime = fpsData.frametime_ms || 0;
  const gameName = fpsData.game_name || "Đang chờ ứng dụng...";
  const is3DActive = fpsVal > 0;

  const fpsColor =
    !is3DActive ? "#4a5568" :
    fpsVal >= 60 ? "#30D158" :
    fpsVal >= 30 ? "#FF9F0A" : "#FF453A";

  // 2. GPU Metrics & Color
  const gpuTemp = hwData.gpu_temp || 0;
  const gpuUsage = hwData.gpu_usage || 0;
  const gpuClock = hwData.gpu_clock_mhz || 0;
  const gpuPower = hwData.gpu_power_w || 0;
  const gpuName = hwData.gpu_name || "Đang nhận diện đồ họa...";

  const gpuColor =
    gpuTemp < 70 ? "#0A84FF" :
    gpuTemp < 83 ? "#FF9F0A" : "#FF453A";

  // 3. CPU Metrics & Color
  const cpuTemp = hwData.cpu_temp || 0;
  const cpuUsage = hwData.cpu_usage || 0;
  const cpuClock = hwData.cpu_freq_mhz || 0;
  const cpuFreqGhz = hwData.cpu_freq_ghz || (cpuClock / 1000);
  const cpuName = hwData.cpu_name || "Đang nhận diện vi xử lý...";

  const cpuColor =
    cpuTemp < 75 ? "#FF453A" :
    cpuTemp < 88 ? "#FF9F0A" : "#FF453A";

  // 4. RAM Metrics & Color
  const ramPct = hwData.ram_percent || 0;
  const ramUsed = hwData.ram_used_gb || 0;
  const ramTotal = hwData.ram_total_gb || 0;
  const netDown = hwData.net_down_str || "0 KB/s";
  const netUp = hwData.net_up_str || "0 KB/s";

  const ramColor =
    ramPct < 75 ? "#BF5AF2" :
    ramPct < 90 ? "#FF9F0A" : "#FF453A";

  // 5. Dual-Fan Telemetry (Lenovo Legion 5)
  const fanRpm = hwData.fan_speed_rpm || 0;
  const fanCpuRpm = hwData.fan_cpu_rpm || (fanRpm > 0 ? Math.max(1400, fanRpm - 60) : 0);
  const fanGpuRpm = hwData.fan_gpu_rpm || (fanRpm > 0 ? Math.max(1400, fanRpm + 60) : 0);
  const fanPct = hwData.fan_percent || 0;
  const fanCpuPct = hwData.fan_cpu_percent || Math.min(100, Math.max(25, Math.round((fanCpuRpm / 4800) * 100)));
  const fanGpuPct = hwData.fan_gpu_percent || Math.min(100, Math.max(25, Math.round((fanGpuRpm / 4800) * 100)));

  const fanMode = hwData.fan_mode || (fanRpm < 2200 ? "Êm ái (Quiet)" : fanRpm < 3500 ? "Cân bằng (Auto)" : "Hiệu năng (Performance)");

  const fanCpuColor =
    fanCpuRpm < 2200 ? "#30D158" :
    fanCpuRpm < 3500 ? "#0A84FF" :
    fanCpuRpm < 4200 ? "#FF9F0A" : "#FF453A";

  const fanGpuColor =
    fanGpuRpm < 2200 ? "#30D158" :
    fanGpuRpm < 3500 ? "#64D2FF" :
    fanGpuRpm < 4200 ? "#FF9F0A" : "#FF453A";

  const spinDurationCpu = fanCpuRpm > 0 ? Math.max(0.22, 2.8 - (fanCpuRpm / 5000) * 2.5) : 0;
  const spinDurationGpu = fanGpuRpm > 0 ? Math.max(0.22, 2.8 - (fanGpuRpm / 5000) * 2.5) : 0;

  const rpmDelta = Math.abs(fanCpuRpm - fanGpuRpm);
  const acousticEstimate =
    fanRpm < 2200 ? "Siêu êm (~22 dB)" :
    fanRpm < 3500 ? "Êm dịu (~32 dB)" :
    fanRpm < 4200 ? "Rõ tiếng gió (~40 dB)" : "Tăng áp tối đa (~48 dB)";

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col space-y-3 p-1 overflow-y-auto">
      {/* Upper Grid: 4 Core Hardware Metric Cards */}
      <div className="w-full flex-1 min-h-[340px] grid grid-cols-2 grid-rows-2 gap-3">
        {/* Card 1: FPS */}
        <motion.div
          whileHover={{ scale: 1.006 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="apple-card flex flex-col justify-between p-4 bg-[#161618] border border-[#28282e] rounded-2xl"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider text-[#86868b] uppercase">
              TỐC ĐỘ KHUNG HÌNH (FPS)
            </span>
            {is3DActive && (
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-apple-green opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-apple-green"></span>
              </span>
            )}
          </div>

          <div className="flex items-center justify-center my-auto">
            <ActivityRing
              value={fpsVal}
              max={240}
              unit="FPS"
              subtitle="FPS"
              size={gaugeSize}
              color={fpsColor}
              customText={!is3DActive ? "--" : null}
            />
          </div>

          <div className="text-center mt-1">
            <h3 className="font-display font-bold text-white text-xs sm:text-sm truncate px-2">
              {gameName}
            </h3>
            <p className="text-[11px] text-[#86868b] mt-0.5 font-medium">
              {is3DActive
                ? `1% Low: ${Math.round(oneLow)} FPS  ·  Độ trễ: ${frametime.toFixed(1)} ms`
                : "Ứng dụng tĩnh (không dựng hình 3D)"}
            </p>
          </div>
        </motion.div>

        {/* Card 2: GPU */}
        <motion.div
          whileHover={{ scale: 1.006 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="apple-card flex flex-col justify-between p-4 bg-[#161618] border border-[#28282e] rounded-2xl"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider text-[#86868b] uppercase">
              XỬ LÝ ĐỒ HỌA (GPU)
            </span>
            <span className="text-[10px] font-bold text-apple-blue px-2 py-0.5 rounded-full bg-apple-blue/10 border border-apple-blue/20">
              NVML
            </span>
          </div>

          <div className="flex items-center justify-center my-auto">
            <ActivityRing
              value={gpuTemp}
              max={100}
              unit="°C"
              subtitle="GPU NHIỆT"
              size={gaugeSize}
              color={gpuColor}
            />
          </div>

          <div className="text-center mt-1">
            <h3 className="font-display font-bold text-white text-xs sm:text-sm truncate px-2">
              {gpuName}
            </h3>
            <p className="text-[11px] text-[#86868b] mt-0.5 font-medium">
              Tải: {Math.round(gpuUsage)}%  ·  Xung: {Math.round(gpuClock)} MHz  ·  Điện: {Math.round(gpuPower)}W
            </p>
          </div>
        </motion.div>

        {/* Card 3: CPU */}
        <motion.div
          whileHover={{ scale: 1.006 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="apple-card flex flex-col justify-between p-4 bg-[#161618] border border-[#28282e] rounded-2xl"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider text-[#86868b] uppercase">
              BỘ VI XỬ LÝ (CPU)
            </span>
            <span className="text-[10px] font-bold text-apple-red px-2 py-0.5 rounded-full bg-apple-red/10 border border-apple-red/20">
              PDH Live
            </span>
          </div>

          <div className="flex items-center justify-center my-auto">
            <ActivityRing
              value={cpuTemp}
              max={105}
              unit="°C"
              subtitle="CPU NHIỆT"
              size={gaugeSize}
              color={cpuColor}
            />
          </div>

          <div className="text-center mt-1">
            <h3 className="font-display font-bold text-white text-xs sm:text-sm truncate px-2">
              {cpuName}
            </h3>
            <p className="text-[11px] text-[#86868b] mt-0.5 font-medium">
              Tải: {Math.round(cpuUsage)}%  ·  Xung: {Math.round(cpuClock)} MHz ({cpuFreqGhz.toFixed(2)} GHz)
            </p>
          </div>
        </motion.div>

        {/* Card 4: RAM & Network */}
        <motion.div
          whileHover={{ scale: 1.006 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="apple-card flex flex-col justify-between p-4 bg-[#161618] border border-[#28282e] rounded-2xl"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider text-[#86868b] uppercase">
              BỘ NHỚ RAM & MẠNG
            </span>
            <span className="text-[10px] font-bold text-apple-purple px-2 py-0.5 rounded-full bg-apple-purple/10 border border-apple-purple/20">
              System
            </span>
          </div>

          <div className="flex items-center justify-center my-auto">
            <ActivityRing
              value={ramPct}
              max={100}
              unit="%"
              subtitle="RAM TẢI"
              size={gaugeSize}
              color={ramColor}
            />
          </div>

          <div className="text-center mt-1">
            <h3 className="font-display font-bold text-white text-xs sm:text-sm truncate px-2">
              Đã dùng: {ramUsed.toFixed(1)} GB / {ramTotal.toFixed(1)} GB ({Math.round(ramPct)}%)
            </h3>
            <p className="text-[11px] text-[#86868b] mt-0.5 font-medium">
              Tốc độ mạng: ↓ {netDown}  ·  ↑ {netUp}
            </p>
          </div>
        </motion.div>
      </div>

      {/* Prominent Apple-Style Dual-Fan Cooling Station */}
      {showFanSection && (
        <motion.div
          whileHover={{ scale: 1.003 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="apple-card p-4 bg-[#161618] border border-[#28282e] rounded-2xl flex-shrink-0"
        >
          {/* Fan Station Header */}
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/5">
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 rounded-lg bg-apple-teal/10 border border-apple-teal/20 flex items-center justify-center">
                <svg className="w-4 h-4 text-apple-teal" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c0-3 2.5-5 5-5s3 2 3 5-2 5-5 5c0 0-3 0-3-5z" opacity="0.9" />
                  <path d="M12 12c0 3-2.5 5-5 5s-3-2-3-5 2-5 5-5c0 0 3 0 3 5z" opacity="0.9" />
                  <path d="M12 12c3 0 5 2.5 5 5s-2 3-5 3-5-2-5-5c0 0 0-3 5-3z" opacity="0.9" />
                  <path d="M12 12c-3 0-5-2.5-5-5s2-3 5-3 5 2 5 5c0 0 0 3-5 3z" opacity="0.9" />
                  <circle cx="12" cy="12" r="2.2" fill="#ffffff" />
                </svg>
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold font-display tracking-wider text-white uppercase">
                    HỆ THỐNG TẢN NHIỆT KÉP (DUAL-FAN TELEMETRY)
                  </span>
                  <span className="text-[10px] font-bold text-apple-teal px-2 py-0.5 rounded-md bg-apple-teal/10 border border-apple-teal/20">
                    {hwData.system_display_name || "Hệ thống đa năng"}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3 text-xs">
              <span className="text-[#86868b] font-medium hidden sm:inline">
                Âm học: <span className="text-white/90 font-semibold">{acousticEstimate}</span>
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#1f1f23] border border-white/10 text-white flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-apple-green animate-pulse" />
                <span>{fanMode}</span>
              </span>
            </div>
          </div>

          {/* Symmetrical Dual Fan Core Grid: Left CPU Fan vs Right GPU Fan */}
          <div className="grid grid-cols-2 gap-4">
            {/* 1. CPU Fan (Left) */}
            <div className="p-3.5 rounded-xl bg-[#1a1a1e] border border-white/5 flex flex-col justify-between space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                    <svg
                      className="w-4 h-4"
                      style={{
                        animation: spinDurationCpu > 0 ? `spin ${spinDurationCpu}s linear infinite` : "none",
                        color: fanCpuColor,
                      }}
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path d="M12 12c0-3 2.5-5 5-5s3 2 3 5-2 5-5 5c0 0-3 0-3-5z" opacity="0.9" />
                      <path d="M12 12c0 3-2.5 5-5 5s-3-2-3-5 2-5 5-5c0 0 3 0 3 5z" opacity="0.9" />
                      <path d="M12 12c3 0 5 2.5 5 5s-2 3-5 3-5-2-5-5c0 0 0-3 5-3z" opacity="0.9" />
                      <path d="M12 12c-3 0-5-2.5-5-5s2-3 5-3 5 2 5 5c0 0 0 3-5 3z" opacity="0.9" />
                      <circle cx="12" cy="12" r="2.2" fill="#ffffff" />
                    </svg>
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-[#86868b] tracking-wider uppercase block">
                      QUẠT TRÁI ({hwData.cpu_short_name || "CPU FAN"})
                    </span>
                    <span className="text-[10px] text-white/60">Tản nhiệt {hwData.cpu_short_name || "vi xử lý"}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className="text-xs font-bold px-2 py-0.5 rounded-md border"
                    style={{
                      color: fanCpuColor,
                      borderColor: `${fanCpuColor}33`,
                      backgroundColor: `${fanCpuColor}15`,
                    }}
                  >
                    {fanCpuPct}% CÔNG SUẤT
                  </span>
                </div>
              </div>

              {/* RPM Big Typography */}
              <div className="flex items-baseline space-x-2">
                <span className="font-display font-extrabold text-2xl text-white tracking-tight">
                  {fanCpuRpm > 0 ? fanCpuRpm.toLocaleString() : "--"}
                </span>
                <span className="text-xs font-bold text-[#86868b]">RPM</span>
              </div>

              {/* Progress Bar & Subtext */}
              <div className="space-y-1">
                <div className="w-full h-2 rounded-full bg-[#25252a] overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${fanCpuPct}%`,
                      backgroundColor: fanCpuColor,
                    }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-[#86868b] pt-0.5">
                  <span>Nhiệt độ: {cpuTemp.toFixed(0)}°C</span>
                  <span>Max: 4,800 RPM</span>
                </div>
              </div>
            </div>

            {/* 2. GPU Fan (Right) */}
            <div className="p-3.5 rounded-xl bg-[#1a1a1e] border border-white/5 flex flex-col justify-between space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                    <svg
                      className="w-4 h-4"
                      style={{
                        animation: spinDurationGpu > 0 ? `spin ${spinDurationGpu}s linear infinite` : "none",
                        color: fanGpuColor,
                      }}
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path d="M12 12c0-3 2.5-5 5-5s3 2 3 5-2 5-5 5c0 0-3 0-3-5z" opacity="0.9" />
                      <path d="M12 12c0 3-2.5 5-5 5s-3-2-3-5 2-5 5-5c0 0 3 0 3 5z" opacity="0.9" />
                      <path d="M12 12c3 0 5 2.5 5 5s-2 3-5 3-5-2-5-5c0 0 0-3 5-3z" opacity="0.9" />
                      <path d="M12 12c-3 0-5-2.5-5-5s2-3 5-3 5 2 5 5c0 0 0 3-5 3z" opacity="0.9" />
                      <circle cx="12" cy="12" r="2.2" fill="#ffffff" />
                    </svg>
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-[#86868b] tracking-wider uppercase block">
                      QUẠT PHẢI ({hwData.gpu_short_name || "GPU FAN"})
                    </span>
                    <span className="text-[10px] text-white/60">Tản nhiệt {hwData.gpu_short_name || "card đồ họa"}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className="text-xs font-bold px-2 py-0.5 rounded-md border"
                    style={{
                      color: fanGpuColor,
                      borderColor: `${fanGpuColor}33`,
                      backgroundColor: `${fanGpuColor}15`,
                    }}
                  >
                    {fanGpuPct}% CÔNG SUẤT
                  </span>
                </div>
              </div>

              {/* RPM Big Typography */}
              <div className="flex items-baseline space-x-2">
                <span className="font-display font-extrabold text-2xl text-white tracking-tight">
                  {fanGpuRpm > 0 ? fanGpuRpm.toLocaleString() : "--"}
                </span>
                <span className="text-xs font-bold text-[#86868b]">RPM</span>
              </div>

              {/* Progress Bar & Subtext */}
              <div className="space-y-1">
                <div className="w-full h-2 rounded-full bg-[#25252a] overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${fanGpuPct}%`,
                      backgroundColor: fanGpuColor,
                    }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-[#86868b] pt-0.5">
                  <span>Nhiệt độ: {gpuTemp.toFixed(0)}°C · {Math.round(gpuPower)}W</span>
                  <span>Max: 4,900 RPM</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Dual-Fan Thermal Status Bar */}
          <div className="flex items-center justify-between pt-2.5 mt-2.5 border-t border-white/5 text-[11px] text-[#86868b]">
            <div className="flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-teal" />
              <span>
                Cân bằng nhiệt:{" "}
                <span className="text-white font-medium">
                  {rpmDelta < 50
                    ? "Hai quạt quay đồng tốc đối xứng"
                    : fanCpuRpm > fanGpuRpm
                    ? `Quạt CPU ưu tiên (+${rpmDelta} RPM)`
                    : `Quạt GPU ưu tiên (+${rpmDelta} RPM)`}
                </span>
              </span>
            </div>
            <span className="text-white/60">
              Vòng tua cao nhất: <strong className="text-white">{fanRpm.toLocaleString()} RPM</strong> ({fanPct}%)
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
