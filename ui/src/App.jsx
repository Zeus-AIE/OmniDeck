import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { LayoutDashboard, LineChart, Settings, Power, Eye, Lock } from "lucide-react";
import DashboardTab from "./components/DashboardTab";
import GraphsTab from "./components/GraphsTab";
import SettingsTab from "./components/SettingsTab";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [overlayEnabled, setOverlayEnabled] = useState(false);
  const lastUserChangeRef = useRef(0);
  const [settings, setSettings] = useState({
    overlay_enabled: false,
    overlay_layout: "horizontal",
    overlay_theme: "apple_dark",
    overlay_scale: "medium",
    overlay_width_mode: "auto",
    overlay_manual_width: 1080,
    overlay_bg_transparency_pct: 65,
    overlay_text_transparency_pct: 100,
    overlay_click_through: false,
    overlay_show_bottom_graphs: true,
    close_to_tray: true,
    metrics: {},
    overlay_bottom_graphs: {},
  });

  const [fpsData, setFpsData] = useState({
    fps: 0,
    one_percent_low: 0,
    frametime_ms: 0,
    game_name: "Đang chờ ứng dụng...",
    history_fps: [],
    history_one_percent_low: [],
  });

  const [hwData, setHwData] = useState({
    cpu_name: "AMD Ryzen 7 5800H",
    cpu_temp: 0,
    cpu_usage: 0,
    cpu_freq_mhz: 0,
    cpu_freq_ghz: 0,
    gpu_name: "NVIDIA GeForce RTX 3060",
    gpu_temp: 0,
    gpu_usage: 0,
    gpu_clock_mhz: 0,
    gpu_power_w: 0,
    ram_used_gb: 0,
    ram_total_gb: 16,
    ram_percent: 0,
    fan_speed_rpm: 0,
    fan_cpu_rpm: 0,
    fan_gpu_rpm: 0,
    fan_percent: 0,
    fan_mode: "Tự động",
    net_down_str: "0 KB/s",
    net_up_str: "0 KB/s",
    history_cpu_clock: [],
    history_gpu_clock: [],
    history_cpu_temp: [],
    history_gpu_temp: [],
    history_cpu_load: [],
    history_gpu_load: [],
    history_ram_load: [],
    history_fan_rpm: [],
  });

  // Communication with Python pywebview backend
  useEffect(() => {
    let timer;

    const poll = async () => {
      try {
        if (window.pywebview && window.pywebview.api) {
          const telemetry = await window.pywebview.api.get_telemetry();
          if (telemetry) {
            if (telemetry.fps_data) setFpsData(telemetry.fps_data);
            if (telemetry.hw_data) setHwData(telemetry.hw_data);
            if (telemetry.settings) {
              if (Date.now() - lastUserChangeRef.current > 1500) {
                setSettings(telemetry.settings);
              }
              setOverlayEnabled(telemetry.settings.overlay_enabled || false);
            }
          }
        } else {
          // Mock data fallback for standalone browser preview
          setFpsData((prev) => ({
            ...prev,
            fps: 144 + Math.sin(Date.now() / 1000) * 8,
            one_percent_low: 112 + Math.cos(Date.now() / 1000) * 6,
            frametime_ms: 6.9,
            game_name: "Valorant.exe",
            history_fps: [...(prev.history_fps || []).slice(-45), 144 + Math.random() * 8],
            history_one_percent_low: [...(prev.history_one_percent_low || []).slice(-45), 112 + Math.random() * 6],
          }));
          setHwData((prev) => ({
            ...prev,
            cpu_temp: 62 + Math.sin(Date.now() / 1500) * 4,
            cpu_usage: 35 + Math.cos(Date.now() / 1500) * 10,
            cpu_freq_mhz: 3850 + Math.sin(Date.now() / 800) * 200,
            gpu_temp: 58 + Math.cos(Date.now() / 1200) * 3,
            gpu_usage: 78 + Math.sin(Date.now() / 1200) * 12,
            gpu_clock_mhz: 1780 + Math.cos(Date.now() / 900) * 40,
            gpu_power_w: 95 + Math.random() * 5,
            ram_used_gb: 10.4,
            ram_percent: 65,
            fan_speed_rpm: Math.round(2650 + Math.sin(Date.now() / 1200) * 350),
            fan_cpu_rpm: Math.round(2580 + Math.sin(Date.now() / 1200) * 320),
            fan_gpu_rpm: Math.round(2720 + Math.sin(Date.now() / 1200) * 380),
            fan_percent: Math.round(55 + Math.sin(Date.now() / 1200) * 8),
            fan_mode: "Cân bằng",
            net_down_str: "12.4 MB/s",
            net_up_str: "1.8 MB/s",
            history_cpu_clock: [...(prev.history_cpu_clock || []).slice(-45), 3850 + Math.random() * 200],
            history_gpu_clock: [...(prev.history_gpu_clock || []).slice(-45), 1780 + Math.random() * 40],
            history_cpu_temp: [...(prev.history_cpu_temp || []).slice(-45), 62 + Math.random() * 4],
            history_gpu_temp: [...(prev.history_gpu_temp || []).slice(-45), 58 + Math.random() * 3],
            history_cpu_load: [...(prev.history_cpu_load || []).slice(-45), 35 + Math.random() * 10],
            history_gpu_load: [...(prev.history_gpu_load || []).slice(-45), 78 + Math.random() * 12],
            history_ram_load: [...(prev.history_ram_load || []).slice(-45), 65 + Math.random() * 2],
            history_fan_rpm: [...(prev.history_fan_rpm || []).slice(-45), 2650 + Math.random() * 350],
          }));
        }
      } catch (err) {
        // Ignored
      }
      timer = setTimeout(poll, 350);
    };

    poll();
    return () => clearTimeout(timer);
  }, []);

  const handleToggleOverlay = async () => {
    const nextState = !overlayEnabled;
    setOverlayEnabled(nextState);
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.toggle_overlay();
    }
  };

  const handleUpdateSettings = async (newSettings) => {
    lastUserChangeRef.current = Date.now();
    setSettings(newSettings);
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.save_settings(newSettings);
    }
  };

  const tabs = [
    { id: "dashboard", label: "Tổng quan", icon: LayoutDashboard },
    { id: "graphs", label: "Biểu đồ", icon: LineChart },
    { id: "settings", label: "Cài đặt", icon: Settings },
  ];

  return (
    <div className="flex flex-col h-screen w-screen bg-[#0d0e12] text-white overflow-hidden select-none font-text">
      {/* 1. Apple Top Header Navigation */}
      <header className="apple-glass z-20 flex items-center justify-between px-6 py-3 border-b border-white/5 flex-shrink-0">
        <div className="flex items-center space-x-3">
          <h1 className="font-display font-extrabold text-lg text-white tracking-tight flex items-center space-x-2">
            <span>Legion Monitor</span>
          </h1>
          <span className="px-2 py-0.5 text-[10px] font-bold text-apple-blue bg-apple-blue/10 border border-apple-blue/20 rounded-md">
            PRO 2.4
          </span>
        </div>

        {/* Global Hotkeys Hint & Overlay Toggle */}
        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 text-xs text-[#86868b]">
            <span className="flex items-center space-x-1">
              <Lock className="w-3 h-3 text-apple-green" />
              <span>F8 Xuyên thấu</span>
            </span>
            <span>·</span>
            <span>F9 Bật/Tắt</span>
            <span>·</span>
            <span className="flex items-center space-x-1">
              <Eye className="w-3 h-3 text-apple-blue" />
              <span>F10 Nền</span>
            </span>
          </div>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleToggleOverlay}
            className={`flex items-center space-x-1.5 px-4 py-1.5 rounded-full text-xs font-bold transition-colors cursor-pointer shadow-md ${
              overlayEnabled
                ? "bg-apple-green text-white shadow-apple-green/20"
                : "bg-apple-blue text-white shadow-apple-blue/20"
            }`}
          >
            <Power className="w-3.5 h-3.5" />
            <span>{overlayEnabled ? "Tắt Overlay (F9)" : "Bật Overlay (F9)"}</span>
          </motion.button>
        </div>
      </header>

      {/* 2. Apple Segmented Control Tab Bar */}
      <div className="px-6 py-2.5 flex-shrink-0">
        <div className="inline-flex p-1 bg-[#1f1f23] rounded-xl border border-white/5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-4 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center space-x-1.5 cursor-pointer z-10 ${
                  isActive ? "text-white" : "text-[#86868b] hover:text-white"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTabPill"
                    className="absolute inset-0 bg-[#2c2c34] rounded-lg -z-10 shadow-sm border border-white/5"
                    transition={{ type: "spring", stiffness: 450, damping: 35 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Main Content Container */}
      <main className="flex-1 w-full px-6 py-1 overflow-hidden">
        {activeTab === "dashboard" && (
          <DashboardTab fpsData={fpsData} hwData={hwData} settings={settings} />
        )}
        {activeTab === "graphs" && (
          <GraphsTab fpsData={fpsData} hwData={hwData} />
        )}
        {activeTab === "settings" && (
          <SettingsTab settings={settings} onUpdateSettings={handleUpdateSettings} />
        )}
      </main>

      {/* 4. Bottom Apple Status Bar */}
      <footer className="apple-glass px-6 py-2 flex items-center justify-between border-t border-white/5 text-[11px] text-[#86868b] flex-shrink-0">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-apple-green animate-pulse" />
          <span className="font-medium text-white/80">
            Sẵn sàng · ETW PresentMon & NVML C-API Active · Single-Instance Mutex Guard
          </span>
        </div>

        <div className="flex items-center space-x-3 font-semibold text-apple-blue">
          <span>Tải xuống: {hwData.net_down_str || "0 KB/s"}</span>
          <span>·</span>
          <span>Tải lên: {hwData.net_up_str || "0 KB/s"}</span>
        </div>
      </footer>
    </div>
  );
}
