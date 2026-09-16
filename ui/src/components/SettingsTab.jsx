import React, { useRef, useState, useEffect } from "react";
import { Sliders, Eye, BarChart3, Palette, CheckSquare, ShieldCheck, Wind, Layout, Sparkles, Cpu, Layers, Tv, Activity } from "lucide-react";

export default function SettingsTab({ settings = {}, onUpdateSettings }) {
  const containerRef = useRef(null);
  const [isWide, setIsWide] = useState(true);

  // Local state for smooth, zero-latency slider feedback
  const [localWidth, setLocalWidth] = useState(settings.overlay_manual_width ?? 1080);
  const [localBgPct, setLocalBgPct] = useState(settings.overlay_bg_transparency_pct ?? 65);
  const [localTextPct, setLocalTextPct] = useState(settings.overlay_text_transparency_pct ?? 100);
  const isDraggingRef = useRef(false);

  useEffect(() => {
    if (!isDraggingRef.current) {
      if (settings.overlay_manual_width !== undefined) setLocalWidth(settings.overlay_manual_width);
      if (settings.overlay_bg_transparency_pct !== undefined) setLocalBgPct(settings.overlay_bg_transparency_pct);
      if (settings.overlay_text_transparency_pct !== undefined) setLocalTextPct(settings.overlay_text_transparency_pct);
    }
  }, [settings.overlay_manual_width, settings.overlay_bg_transparency_pct, settings.overlay_text_transparency_pct]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setIsWide(entry.contentRect.width >= 860);
      }
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const handleUpdate = (updates) => {
    if (onUpdateSettings) {
      onUpdateSettings({ ...settings, ...updates });
    }
  };

  // Instant IPC calls for zero-latency slider dragging
  const handleBgSliderChange = (val) => {
    setLocalBgPct(val);
    if (window.pywebview && window.pywebview.api && window.pywebview.api.set_bg_transparency) {
      window.pywebview.api.set_bg_transparency(val);
    }
  };

  const handleBgSliderCommit = (val) => {
    const bgMode = val <= 0 ? "transparent" : (val >= 95 ? "solid" : "badges");
    handleUpdate({
      overlay_bg_transparency_pct: val,
      overlay_bg_mode: bgMode
    });
  };

  const handleTextSliderChange = (val) => {
    setLocalTextPct(val);
    if (window.pywebview && window.pywebview.api && window.pywebview.api.set_text_transparency) {
      window.pywebview.api.set_text_transparency(val);
    }
  };

  const handleTextSliderCommit = (val) => {
    handleUpdate({ overlay_text_transparency_pct: val });
  };

  const handleMetricToggle = (metricKey) => {
    const currentMetrics = settings.metrics || {};
    const updated = {
      ...currentMetrics,
      [metricKey]: currentMetrics[metricKey] === false ? true : false,
    };
    handleUpdate({ metrics: updated });
  };

  const handleDeckGraphToggle = (graphKey) => {
    const currentDeck = settings.overlay_bottom_graphs || {};
    const updated = {
      ...currentDeck,
      [graphKey]: currentDeck[graphKey] === false ? true : false,
    };
    handleUpdate({ overlay_bottom_graphs: updated });
  };

  const widthMode = settings.overlay_width_mode ?? "auto";
  const layout = settings.overlay_layout ?? "horizontal";
  const theme = settings.overlay_theme ?? "apple_dark";
  const scale = settings.overlay_scale ?? "medium";
  const closeToTray = settings.close_to_tray ?? true;
  const metrics = settings.metrics || {};
  const deckGraphs = settings.overlay_bottom_graphs || {};
  const overlayFanMode = settings.overlay_fan_mode ?? "dual";
  const dashboardShowFan = settings.dashboard_show_fan ?? true;

  const metricCategories = [
    {
      name: "Hiệu năng Game (FPS & Độ trễ)",
      color: "text-[#30D158]",
      dotColor: "bg-[#30D158]",
      items: [
        { id: "app_name", label: "Tên game / ứng dụng active" },
        { id: "fps", label: "Tốc độ khung hình (FPS)" },
        { id: "one_percent_low", label: "Chỉ số 1% Low FPS" },
        { id: "frametime", label: "Độ trễ khung hình (ms)" },
      ]
    },
    {
      name: "Vi xử lý CPU (AMD Ryzen 7)",
      color: "text-[#FF9F0A]",
      dotColor: "bg-[#FF9F0A]",
      items: [
        { id: "cpu_temp", label: "Nhiệt độ CPU (°C)" },
        { id: "cpu_usage", label: "Mức tải CPU (%)" },
        { id: "cpu_clock", label: "Xung nhịp CPU (MHz)" },
      ]
    },
    {
      name: "Đồ họa GPU (NVIDIA RTX 3060)",
      color: "text-[#0A84FF]",
      dotColor: "bg-[#0A84FF]",
      items: [
        { id: "gpu_temp", label: "Nhiệt độ GPU (°C)" },
        { id: "gpu_usage", label: "Mức tải GPU (%)" },
        { id: "gpu_clock", label: "Xung nhịp GPU Core (MHz)" },
        { id: "gpu_power", label: "Công suất GPU (Watts)" },
      ]
    },
    {
      name: "Bộ nhớ & Mạng & Tản nhiệt",
      color: "text-[#BF5AF2]",
      dotColor: "bg-[#BF5AF2]",
      items: [
        { id: "ram", label: "Bộ nhớ RAM đã dùng" },
        { id: "network", label: "Tốc độ Internet (↓ Tải xuống / ↑ Tải lên)" },
        { id: "fan", label: "Vòng tua Quạt tản nhiệt (RPM)" },
      ]
    }
  ];

  return (
    <div ref={containerRef} className="w-full h-full overflow-y-auto p-2 pr-3 custom-scrollbar">
      <div className={isWide ? "grid grid-cols-2 gap-5" : "flex flex-col space-y-5"}>
        {/* ================= LEFT COLUMN ================= */}
        <div className="flex flex-col space-y-5">
          {/* Section 1: 4 Layout Modes (Apple x Gaming Visual Cards) */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2 text-white font-display font-bold text-sm">
                <Layout className="w-4 h-4 text-apple-blue" />
                <span>1. Bố cục hiển thị Overlay (Layout Modes)</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-apple-blue/15 text-apple-blue border border-apple-blue/30 font-semibold">
                Áp dụng 100% thông số
              </span>
            </div>
            <p className="text-[11px] text-[#86868b] leading-relaxed mb-4">
              Chọn kiểu bố cục thanh giám sát trên màn hình chơi game. Tất cả 4 bố cục đều áp dụng chuẩn xác danh sách thông số bạn chọn.
            </p>

            <div className="grid grid-cols-2 gap-2.5">
              {[
                {
                  id: "horizontal",
                  title: "Thanh ngang chuẩn",
                  badge: "Khuyên dùng",
                  desc: "Trải dài trên màn hình, hỗ trợ khung sóng biểu đồ dưới"
                },
                {
                  id: "compact",
                  title: "Thanh mini Pill",
                  badge: "Siêu gọn",
                  desc: "Viên thuốc bo tròn tối giản, siêu nhẹ mắt và tiết kiệm diện tích"
                },
                {
                  id: "corner",
                  title: "Khối góc OSD",
                  badge: "Gaming Card",
                  desc: "Đa hàng phong cách MSI Afterburner cao cấp, tự co giãn hàng"
                },
                {
                  id: "vertical",
                  title: "Thanh dọc Side Dock",
                  badge: "Cạnh viền",
                  desc: "Cột hiển thị dọc bên hông màn hình, số liệu xếp ngay ngắn"
                },
              ].map((l) => (
                <div
                  key={l.id}
                  onClick={() => handleUpdate({ overlay_layout: l.id })}
                  className={`p-3 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                    layout === l.id
                      ? "bg-apple-blue/15 border-apple-blue text-white shadow-lg shadow-apple-blue/10 ring-1 ring-apple-blue/40"
                      : "bg-[#18191f]/80 border-white/5 text-white/70 hover:border-white/20 hover:text-white"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-xs text-white">{l.title}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                      layout === l.id ? "bg-apple-blue text-white" : "bg-white/5 text-[#86868b]"
                    }`}>
                      {l.badge}
                    </span>
                  </div>
                  <span className="text-[10px] text-[#86868b] leading-tight">{l.desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Dual Independent Transparency Sliders */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center space-x-2 text-white font-display font-bold text-sm mb-1">
              <Eye className="w-4 h-4 text-apple-teal" />
              <span>2. Độ trong suốt Nền & Chữ (Điều chỉnh độc lập)</span>
            </div>
            <p className="text-[11px] text-[#86868b] leading-relaxed mb-4">
              Kéo 2 thanh trượt bên dưới để thay đổi độ mờ của nền và độ rõ nét của chữ/đồ thị với phản hồi tức thời.
            </p>

            <div className="space-y-5 text-xs">
              {/* Slider 1: Background Transparency */}
              <div className="p-3.5 bg-[#18191f]/80 rounded-xl border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/90 font-semibold flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-apple-blue inline-block"></span>
                    <span>Độ trong suốt nền màn hình (Background):</span>
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-[#86868b]">
                      {localBgPct === 0 ? "Trong suốt 100% (Pure HUD)" : localBgPct <= 35 ? "Kính mờ nhẹ" : localBgPct <= 70 ? "Kính mờ Apple" : "Nền tối"}
                    </span>
                    <span className="text-apple-blue font-bold font-display px-2.5 py-0.5 rounded-md bg-apple-blue/15 border border-apple-blue/30 text-xs">
                      {localBgPct}%
                    </span>
                  </div>
                </div>

                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={localBgPct}
                  onMouseDown={() => { isDraggingRef.current = true; }}
                  onMouseUp={() => { isDraggingRef.current = false; handleBgSliderCommit(localBgPct); }}
                  onTouchStart={() => { isDraggingRef.current = true; }}
                  onTouchEnd={() => { isDraggingRef.current = false; handleBgSliderCommit(localBgPct); }}
                  onChange={(e) => handleBgSliderChange(Number(e.target.value))}
                  className="w-full accent-apple-blue bg-[#25252e] rounded-lg h-2.5 cursor-pointer"
                />

                {/* Quick Presets for Background */}
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {[
                    { val: 0, label: "0% Pure HUD" },
                    { val: 35, label: "35% Kính nhẹ" },
                    { val: 65, label: "65% Chuẩn Apple" },
                    { val: 85, label: "85% Nền tối rõ" },
                    { val: 100, label: "100% Nguyên khối" },
                  ].map((p) => (
                    <button
                      key={p.val}
                      onClick={() => {
                        handleBgSliderChange(p.val);
                        handleBgSliderCommit(p.val);
                      }}
                      className={`px-2 py-1 rounded-lg text-[10px] font-semibold transition-all cursor-pointer border ${
                        Math.abs(localBgPct - p.val) <= 2
                          ? "bg-apple-blue text-white border-apple-blue shadow-sm shadow-apple-blue/20"
                          : "bg-[#1f2027] text-[#86868b] border-white/5 hover:text-white hover:border-white/15"
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Slider 2: Text Transparency */}
              <div className="p-3.5 bg-[#18191f]/80 rounded-xl border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/90 font-semibold flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#30D158] inline-block"></span>
                    <span>Độ trong suốt chữ & số liệu (Text & Metrics):</span>
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-[#86868b]">
                      {localTextPct === 100 ? "Rõ nét tối đa" : localTextPct >= 75 ? "Sắc nét" : "Mờ ảo"}
                    </span>
                    <span className="text-[#30D158] font-bold font-display px-2.5 py-0.5 rounded-md bg-[#30D158]/15 border border-[#30D158]/30 text-xs">
                      {localTextPct}%
                    </span>
                  </div>
                </div>

                <input
                  type="range"
                  min="20"
                  max="100"
                  step="1"
                  value={localTextPct}
                  onMouseDown={() => { isDraggingRef.current = true; }}
                  onMouseUp={() => { isDraggingRef.current = false; handleTextSliderCommit(localTextPct); }}
                  onTouchStart={() => { isDraggingRef.current = true; }}
                  onTouchEnd={() => { isDraggingRef.current = false; handleTextSliderCommit(localTextPct); }}
                  onChange={(e) => handleTextSliderChange(Number(e.target.value))}
                  className="w-full accent-[#30D158] bg-[#25252e] rounded-lg h-2.5 cursor-pointer"
                />

                {/* Quick Presets for Text */}
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {[
                    { val: 100, label: "100% Rõ nét nhất" },
                    { val: 85, label: "85% Tự nhiên" },
                    { val: 70, label: "70% Mờ vừa" },
                    { val: 50, label: "50% Mờ nhiều" },
                    { val: 30, label: "30% Mờ ảo" },
                  ].map((p) => (
                    <button
                      key={p.val}
                      onClick={() => {
                        handleTextSliderChange(p.val);
                        handleTextSliderCommit(p.val);
                      }}
                      className={`px-2 py-1 rounded-lg text-[10px] font-semibold transition-all cursor-pointer border ${
                        Math.abs(localTextPct - p.val) <= 2
                          ? "bg-[#30D158] text-black border-[#30D158] shadow-sm font-bold"
                          : "bg-[#1f2027] text-[#86868b] border-white/5 hover:text-white hover:border-white/15"
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Overlay Sizing & Precision Auto-Fit */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center space-x-2 text-white font-display font-bold text-sm mb-4">
              <Sliders className="w-4 h-4 text-apple-orange" />
              <span>3. Kích thước & Chế độ Auto-Fit</span>
            </div>

            <div className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <label
                  onClick={() => handleUpdate({ overlay_width_mode: "auto" })}
                  className={`p-3 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                    widthMode === "auto"
                      ? "bg-apple-orange/15 border-apple-orange text-white shadow-sm ring-1 ring-apple-orange/40"
                      : "bg-[#18191f]/80 border-white/5 text-white/70 hover:border-white/20 hover:text-white"
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <input
                      type="radio"
                      name="width_mode"
                      value="auto"
                      checked={widthMode === "auto"}
                      onChange={() => handleUpdate({ overlay_width_mode: "auto" })}
                      className="accent-apple-orange"
                    />
                    <span className="font-bold text-xs text-white">Tự động co giãn (Auto-fit)</span>
                  </div>
                  <span className="text-[10px] text-[#86868b] leading-tight">
                    Khung Overlay tự ôm sát chính xác theo số lượng thông số hiển thị
                  </span>
                </label>

                <label
                  onClick={() => handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: localWidth })}
                  className={`p-3 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                    widthMode === "manual"
                      ? "bg-apple-orange/15 border-apple-orange text-white shadow-sm ring-1 ring-apple-orange/40"
                      : "bg-[#18191f]/80 border-white/5 text-white/70 hover:border-white/20 hover:text-white"
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <input
                      type="radio"
                      name="width_mode"
                      value="manual"
                      checked={widthMode === "manual"}
                      onChange={() => handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: localWidth })}
                      className="accent-apple-orange"
                    />
                    <span className="font-bold text-xs text-white">Cố định thủ công (Manual)</span>
                  </div>
                  <span className="text-[10px] text-[#86868b] leading-tight">
                    Giữ nguyên chiều dài cố định theo giá trị bạn thiết lập
                  </span>
                </label>
              </div>

              {/* Slider for manual width */}
              <div className="p-3 bg-[#18191f]/80 rounded-xl border border-white/5 mt-2">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-[#86868b] font-medium">Chiều dài thanh (khi chọn thủ công):</span>
                  <span className="text-apple-orange font-bold font-display px-2 py-0.5 rounded bg-apple-orange/10 border border-apple-orange/20">
                    {localWidth} px {widthMode === "auto" ? "(Đang bật Auto-fit)" : ""}
                  </span>
                </div>
                <input
                  type="range"
                  min="380"
                  max="1600"
                  step="10"
                  value={localWidth}
                  onMouseDown={() => { isDraggingRef.current = true; }}
                  onMouseUp={() => { isDraggingRef.current = false; handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: localWidth }); }}
                  onTouchStart={() => { isDraggingRef.current = true; }}
                  onTouchEnd={() => { isDraggingRef.current = false; handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: localWidth }); }}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setLocalWidth(val);
                    handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: val });
                  }}
                  className="w-full accent-apple-orange bg-[#25252e] rounded-lg h-2 cursor-pointer"
                />

                <div className="flex flex-wrap gap-1.5 mt-2">
                  {[600, 800, 1000, 1200, 1450].map((w) => (
                    <button
                      key={w}
                      onClick={() => {
                        setLocalWidth(w);
                        handleUpdate({ overlay_width_mode: "manual", overlay_manual_width: w });
                      }}
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-colors cursor-pointer border ${
                        widthMode === "manual" && Math.abs(localWidth - w) < 20
                          ? "bg-apple-orange text-white border-apple-orange shadow-sm"
                          : "bg-[#1f2027] text-[#86868b] border-white/5 hover:text-white"
                      }`}
                    >
                      {w}px
                    </button>
                  ))}
                </div>
              </div>

              <p className="text-[11px] text-[#86868b] leading-relaxed pt-1">
                Tọa độ góc của Overlay luôn được neo chắc chắn trên màn hình khi bạn đổi kích thước hoặc kéo thả tay nắm [::].
              </p>
            </div>
          </div>
        </div>

        {/* ================= RIGHT COLUMN ================= */}
        <div className="flex flex-col space-y-5">
          {/* Section 4: Metrics Selection (100% Functional in ALL layouts) */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2 text-white font-display font-bold text-sm">
                <CheckSquare className="w-4 h-4 text-[#30D158]" />
                <span>4. Danh sách thông số hiển thị (Metric Toggles)</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#30D158]/15 text-[#30D158] border border-[#30D158]/30 font-semibold">
                Đồng bộ 4 bố cục
              </span>
            </div>
            <p className="text-[11px] text-[#86868b] leading-relaxed mb-4">
              Bật hoặc tắt từng thông số cụ thể. Các tùy chọn này hoạt động chuẩn xác 100% trên cả Thanh ngang, Thanh mini, Khối góc OSD và Thanh dọc.
            </p>

            <div className="space-y-3.5">
              {metricCategories.map((cat, idx) => (
                <div key={idx} className="p-3 bg-[#18191f]/80 rounded-xl border border-white/5">
                  <div className={`text-xs font-bold ${cat.color} mb-2.5 flex items-center space-x-1.5`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${cat.dotColor}`}></span>
                    <span>{cat.name}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {cat.items.map((m) => {
                      const isChecked = metrics[m.id] !== false;
                      return (
                        <label
                          key={m.id}
                          className={`flex items-center space-x-2 p-2 rounded-lg cursor-pointer transition-all border ${
                            isChecked
                              ? "bg-white/5 border-white/15 text-white"
                              : "bg-transparent border-transparent text-[#86868b] hover:text-white"
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => handleMetricToggle(m.id)}
                            className="accent-apple-blue rounded w-3.5 h-3.5"
                          />
                          <span className="truncate text-[11px] font-medium">{m.label}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 5: Dual-Fan Telemetry Controls */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center space-x-2 text-white font-display font-bold text-sm mb-4">
              <Wind className="w-4 h-4 text-apple-teal" />
              <span>5. Thiết lập Quạt tản nhiệt & Vòng tua (Dual-Fan)</span>
            </div>

            <div className="space-y-4 text-xs">
              {/* Toggle 1: Show on Dashboard */}
              <div className="flex items-center justify-between p-2.5 bg-[#18191f]/80 rounded-xl border border-white/5">
                <div>
                  <span className="text-white/90 font-medium block">Trạm Quạt ở trang Tổng quan (Dashboard)</span>
                  <span className="text-[10px] text-[#86868b]">Hiển thị 2 quạt CPU & GPU và buồng tản nhiệt tại Dashboard</span>
                </div>
                <input
                  type="checkbox"
                  checked={dashboardShowFan}
                  onChange={(e) => handleUpdate({ dashboard_show_fan: e.target.checked })}
                  className="accent-apple-teal rounded cursor-pointer w-4 h-4"
                />
              </div>

              {/* Selector: Overlay Fan Mode */}
              <div className="pt-2 border-t border-white/5">
                <span className="text-[#86868b] font-medium block mb-2">Kiểu hiển thị vòng tua trên Overlay:</span>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "dual", title: "Quạt kép (CPU & GPU)", desc: "C: 1950 · G: 2150 RPM (Khuyên dùng)" },
                    { id: "max", title: "Quạt quay nhanh nhất", desc: "Hiển thị 1 chỉ số lớn nhất (Max RPM)" },
                    { id: "cpu", title: "Chỉ Quạt CPU (Trái)", desc: "Tản nhiệt chip Ryzen 7 5800H" },
                    { id: "gpu", title: "Chỉ Quạt GPU (Phải)", desc: "Tản nhiệt đồ họa RTX 3060" },
                  ].map((fm) => (
                    <label
                      key={fm.id}
                      onClick={() => handleUpdate({ overlay_fan_mode: fm.id })}
                      className={`p-2.5 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                        overlayFanMode === fm.id
                          ? "bg-apple-teal/15 border-apple-teal text-white shadow-sm"
                          : "bg-[#18191f]/80 border-white/5 text-white/70 hover:text-white"
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="overlay_fan_mode"
                          value={fm.id}
                          checked={overlayFanMode === fm.id}
                          onChange={() => handleUpdate({ overlay_fan_mode: fm.id })}
                          className="accent-apple-teal"
                        />
                        <span className="font-semibold text-xs text-white">{fm.title}</span>
                      </div>
                      <span className="text-[10px] text-[#86868b] mt-1 pl-5 leading-tight">{fm.desc}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Section 6: Bottom Graph Deck (Only for Horizontal Bar) */}
          {layout === "horizontal" && (
            <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2 text-white font-display font-bold text-sm">
                  <BarChart3 className="w-4 h-4 text-apple-blue" />
                  <span>6. Khung biểu đồ sóng bên dưới (Bottom Deck)</span>
                </div>
                <input
                  type="checkbox"
                  checked={settings.overlay_show_bottom_graphs ?? true}
                  onChange={(e) => handleUpdate({ overlay_show_bottom_graphs: e.target.checked })}
                  className="accent-apple-blue rounded cursor-pointer w-4 h-4"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { id: "fps", label: "Sóng FPS & 1% Low" },
                  { id: "cpu", label: "Sóng Xung & Nhiệt CPU" },
                  { id: "gpu", label: "Sóng Xung & Nhiệt GPU" },
                  { id: "ram_net", label: "Sóng RAM & Mạng" },
                  { id: "fan", label: "Sóng Quạt CPU & GPU" },
                ].map((g) => (
                  <label key={g.id} className="flex items-center space-x-2 cursor-pointer text-white/80 hover:text-white p-1.5 bg-[#18191f]/60 rounded-lg">
                    <input
                      type="checkbox"
                      checked={deckGraphs[g.id] !== false}
                      onChange={() => handleDeckGraphToggle(g.id)}
                      className="accent-apple-blue rounded"
                    />
                    <span className="truncate text-[11px]">{g.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Section 7: Themes & System Behavior */}
          <div className="apple-card p-5 bg-[#14151a]/90 backdrop-blur-xl border border-white/8 rounded-2xl shadow-xl">
            <div className="flex items-center space-x-2 text-white font-display font-bold text-sm mb-4">
              <Palette className="w-4 h-4 text-apple-orange" />
              <span>7. Chủ đề màu sắc & Hành vi hệ thống</span>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <span className="text-[#86868b] font-medium block mb-2">Chủ đề màu sắc Gaming / Apple:</span>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "apple_dark", label: "Apple Dark Minimal" },
                    { id: "ice_blue", label: "Legion Ice Blue" },
                    { id: "cyberpunk", label: "Cyber Neon" },
                    { id: "blood_red", label: "Blood Red Gaming" },
                  ].map((t) => (
                    <label key={t.id} className="flex items-center space-x-2 cursor-pointer text-white/90 p-2 bg-[#18191f]/60 rounded-lg border border-white/5">
                      <input
                        type="radio"
                        name="theme"
                        value={t.id}
                        checked={theme === t.id}
                        onChange={() => handleUpdate({ overlay_theme: t.id })}
                        className="accent-apple-orange"
                      />
                      <span className="text-xs">{t.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                <div>
                  <span className="text-white/90 font-medium block">Thu nhỏ xuống khay hệ thống khi đóng</span>
                  <span className="text-[10px] text-[#86868b]">Bấm nút X để ẩn vào khay taskbar thay vì thoát hoàn toàn</span>
                </div>
                <input
                  type="checkbox"
                  checked={closeToTray}
                  onChange={(e) => handleUpdate({ close_to_tray: e.target.checked })}
                  className="accent-apple-green rounded cursor-pointer w-4 h-4"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
