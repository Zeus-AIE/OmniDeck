import React from "react";
import { motion } from "framer-motion";

export default function ActivityRing({
  value = 0,
  max = 100,
  unit = "",
  subtitle = "",
  size = 160,
  color = "#30D158",
  trackColor = "#28282e",
  customText = null,
}) {
  const strokeWidth = Math.max(9, size * 0.065);
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const ratio = Math.max(0, Math.min(1, max > 0 ? value / max : 0));
  const strokeDashoffset = circumference * (1 - ratio);

  // Dynamic font scaling
  const valFontSize = Math.max(18, Math.round(size * 0.17));
  const subFontSize = Math.max(8, Math.round(size * 0.055));
  const unitFontSize = Math.max(9, Math.round(size * 0.07));

  return (
    <div
      className="relative flex items-center justify-center select-none"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        className="rotate-[-90deg] overflow-visible"
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={trackColor}
          strokeWidth={strokeWidth}
        />
        {/* Animated Progress Arc */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{
            type: "spring",
            damping: 24,
            stiffness: 140,
            mass: 0.8,
          }}
          style={{
            filter: `drop-shadow(0px 0px ${Math.max(3, size * 0.03)}px ${color}88)`,
          }}
        />
      </svg>

      {/* Central Metrics Display */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
        <div className="flex items-baseline justify-center font-display font-bold text-white tracking-tight leading-none">
          <span style={{ fontSize: `${valFontSize}px` }}>
            {customText !== null ? customText : Math.round(value)}
          </span>
          {unit && (
            <span
              className="ml-1 font-medium text-white/70"
              style={{ fontSize: `${unitFontSize}px` }}
            >
              {unit}
            </span>
          )}
        </div>
        {subtitle && (
          <span
            className="mt-1 font-semibold tracking-wider uppercase text-[#86868b]"
            style={{ fontSize: `${subFontSize}px` }}
          >
            {subtitle}
          </span>
        )}
      </div>
    </div>
  );
}
