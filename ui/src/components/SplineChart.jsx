import React, { useRef, useState, useEffect } from "react";

// Catmull-Rom Spline Interpolation Algorithm with smooth clamping
function generateCatmullRomSpline(pts, steps = 10, minY = null, maxY = null) {
  if (!pts || pts.length === 0) return [];
  if (pts.length === 1) return [pts[0].x, pts[0].y];
  if (pts.length === 2) return [pts[0].x, pts[0].y, pts[1].x, pts[1].y];

  const p0 = { x: 2 * pts[0].x - pts[1].x, y: 2 * pts[0].y - pts[1].y };
  const pn = { x: 2 * pts[pts.length - 1].x - pts[pts.length - 2].x, y: 2 * pts[pts.length - 1].y - pts[pts.length - 2].y };
  const padded = [p0, ...pts, pn];

  const curve = [];
  for (let i = 1; i < padded.length - 2; i++) {
    const p_0 = padded[i - 1];
    const p_1 = padded[i];
    const p_2 = padded[i + 1];
    const p_3 = padded[i + 2];

    for (let step = 0; step < steps; step++) {
      const t = step / steps;
      const t2 = t * t;
      const t3 = t2 * t;

      let x = 0.5 * (
        (2 * p_1.x) +
        (-p_0.x + p_2.x) * t +
        (2 * p_0.x - 5 * p_1.x + 4 * p_2.x - p_3.x) * t2 +
        (-p_0.x + 3 * p_1.x - 3 * p_2.x + p_3.x) * t3
      );
      let y = 0.5 * (
        (2 * p_1.y) +
        (-p_0.y + p_2.y) * t +
        (2 * p_0.y - 5 * p_1.y + 4 * p_2.y - p_3.y) * t2 +
        (-p_0.y + 3 * p_1.y - 3 * p_2.y + p_3.y) * t3
      );

      if (minY !== null) y = Math.max(minY, y);
      if (maxY !== null) y = Math.min(maxY, y);

      curve.push(x, y);
    }
  }

  const lastPt = pts[pts.length - 1];
  let finalY = lastPt.y;
  if (minY !== null) finalY = Math.max(minY, finalY);
  if (maxY !== null) finalY = Math.min(maxY, finalY);
  curve.push(lastPt.x, finalY);

  return curve;
}

export default function SplineChart({
  title = "Biểu đồ hiệu năng",
  yUnit = "",
  yMin = 0,
  yMax = 100,
  ySteps = 4,
  series = [],
  currentValues = [],
}) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const [hoverData, setHoverData] = useState(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onWheel = (e) => {
      e.preventDefault();
      setZoomLevel((prev) => {
        const delta = e.deltaY < 0 ? 0.25 : -0.25;
        const next = Math.max(1.0, Math.min(4.0, prev + delta));
        return Math.round(next * 10) / 10;
      });
    };

    canvas.addEventListener("wheel", onWheel, { passive: false });
    return () => canvas.removeEventListener("wheel", onWheel);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    let animationFrameId;

    const render = () => {
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const w = Math.floor(rect.width);
      const h = Math.floor(rect.height);

      if (w <= 0 || h <= 0) return;

      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.scale(dpr, dpr);

      ctx.fillStyle = "#161618";
      ctx.fillRect(0, 0, w, h);

      const padLeft = 70;
      const padRight = 18;
      const padTop = 26;
      const padBottom = 22;
      const plotW = Math.max(20, w - padLeft - padRight);
      const plotH = Math.max(20, h - padTop - padBottom);
      const bottomY = padTop + plotH;

      ctx.strokeStyle = "#232328";
      ctx.lineWidth = 1;
      ctx.fillStyle = "#86868b";
      ctx.font = '10px "Segoe UI Variable Text", system-ui, sans-serif';
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";

      for (let i = 0; i <= ySteps; i++) {
        const yVal = yMin + ((yMax - yMin) / ySteps) * i;
        const py = bottomY - (i / ySteps) * plotH;

        ctx.beginPath();
        ctx.moveTo(padLeft, py);
        ctx.lineTo(w - padRight, py);
        ctx.stroke();

        ctx.fillText(`${Math.round(yVal)} ${yUnit}`, padLeft - 8, py);
      }

      ctx.strokeStyle = "#2c2c34";
      ctx.beginPath();
      ctx.moveTo(padLeft, bottomY);
      ctx.lineTo(w - padRight, bottomY);
      ctx.stroke();

      const yRange = Math.max(1, yMax - yMin);

      series.forEach((s) => {
        const rawData = s.data || [];
        if (rawData.length < 2) return;

        const totalPoints = rawData.length;
        const visibleCount = Math.max(6, Math.round(totalPoints / zoomLevel));
        const slicedData = rawData.slice(-visibleCount);

        const cleanData = slicedData.map((v) => Number(v) || 0);
        const n = cleanData.length;
        const dx = plotW / Math.max(1, n - 1);

        const pts = cleanData.map((val, i) => {
          const clamped = Math.max(yMin, Math.min(yMax, val));
          return {
            x: padLeft + i * dx,
            y: bottomY - ((clamped - yMin) / yRange) * plotH,
          };
        });

        const spline = generateCatmullRomSpline(pts, 10, padTop, bottomY);
        if (spline.length < 4) return;

        const grad = ctx.createLinearGradient(0, padTop, 0, bottomY);
        grad.addColorStop(0, `${s.color}24`);
        grad.addColorStop(1, `${s.color}02`);

        ctx.beginPath();
        ctx.moveTo(spline[0], bottomY);
        ctx.lineTo(spline[0], spline[1]);
        for (let i = 2; i < spline.length; i += 2) {
          ctx.lineTo(spline[i], spline[i + 1]);
        }
        ctx.lineTo(spline[spline.length - 2], bottomY);
        ctx.closePath();
        ctx.fillStyle = grad;
        ctx.fill();

        ctx.strokeStyle = `${s.color}35`;
        ctx.lineWidth = 4.5;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        ctx.moveTo(spline[0], spline[1]);
        for (let i = 2; i < spline.length; i += 2) {
          ctx.lineTo(spline[i], spline[i + 1]);
        }
        ctx.stroke();

        ctx.strokeStyle = s.color;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(spline[0], spline[1]);
        for (let i = 2; i < spline.length; i += 2) {
          ctx.lineTo(spline[i], spline[i + 1]);
        }
        ctx.stroke();

        const lastX = spline[spline.length - 2];
        const lastY = spline[spline.length - 1];

        ctx.beginPath();
        ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
        ctx.fillStyle = `${s.color}55`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(lastX, lastY, 2, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
      });

      if (hoverData && hoverData.pixelX >= padLeft && hoverData.pixelX <= w - padRight) {
        const hx = hoverData.pixelX;
        ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(hx, padTop);
        ctx.lineTo(hx, bottomY);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    };

    const ro = new ResizeObserver(() => {
      animationFrameId = requestAnimationFrame(render);
    });
    ro.observe(container);

    render();

    return () => {
      ro.disconnect();
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [series, currentValues, yMin, yMax, ySteps, yUnit, zoomLevel, hoverData]);

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const pixelX = e.clientX - rect.left;
    const padLeft = 70;
    const padRight = 18;
    const plotW = Math.max(20, rect.width - padLeft - padRight);

    if (pixelX < padLeft || pixelX > rect.width - padRight) {
      setHoverData(null);
      return;
    }

    const firstSeries = series[0];
    if (!firstSeries || !firstSeries.data || firstSeries.data.length < 2) {
      setHoverData(null);
      return;
    }

    const totalPoints = firstSeries.data.length;
    const visibleCount = Math.max(6, Math.round(totalPoints / zoomLevel));
    const ratio = Math.max(0, Math.min(1, (pixelX - padLeft) / plotW));
    const indexInSlice = Math.round(ratio * (visibleCount - 1));

    const values = series.map((s) => {
      const sliced = (s.data || []).slice(-visibleCount);
      const val = sliced[indexInSlice] ?? 0;
      return {
        name: s.name,
        color: s.color,
        val: `${Math.round(val)} ${yUnit}`,
      };
    });

    setHoverData({ pixelX, values });
  };

  const handleMouseLeave = () => {
    setHoverData(null);
  };

  const handleDoubleClick = () => {
    setZoomLevel(1.0);
  };

  return (
    <div
      ref={containerRef}
      className="apple-card relative w-full h-full flex flex-col p-3 overflow-hidden"
      style={{ minHeight: "155px" }}
    >
      <div className="flex items-center justify-between z-10 mb-1 px-1">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-display font-bold text-white tracking-wide">
            {title}
          </span>
          {zoomLevel > 1.0 && (
            <button
              onClick={handleDoubleClick}
              title="Click đúp để đặt lại tỉ lệ 1.0x"
              className="px-2 py-0.5 rounded-md bg-apple-blue/20 text-apple-blue border border-apple-blue/30 text-[10px] font-bold cursor-pointer hover:bg-apple-blue/30 transition-colors"
            >
              Zoom {zoomLevel}x (Reset)
            </button>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {(hoverData ? hoverData.values : series).map((s, idx) => (
            <div
              key={s.name}
              className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-[#1f1f23] border border-white/5 text-[10px] font-semibold"
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: s.color }}
              />
              <span className="text-[#86868b]">{s.name}:</span>
              <span style={{ color: s.color }}>
                {hoverData ? s.val : currentValues[idx] || "--"}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div
        className="flex-1 w-full relative cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onDoubleClick={handleDoubleClick}
      >
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
      </div>

      <div className="flex items-center justify-between mt-1 px-1 text-[9px] text-[#86868b]/70 select-none">
        <span>Con lăn chuột: Phóng to / Thu nhỏ trục thời gian</span>
        <span>Click đúp: Đặt lại tỉ lệ</span>
      </div>
    </div>
  );
}
