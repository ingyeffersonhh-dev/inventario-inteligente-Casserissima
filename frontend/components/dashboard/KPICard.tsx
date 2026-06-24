"use client";
import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, DollarSign, Cake, Calendar, AlertTriangle } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  "💰": DollarSign,
  "🎂": Cake,
  "📅": Calendar,
  "⚠️": AlertTriangle,
};

interface KPICardProps {
  label:    string;
  value:    number | string;
  prefix?:  string;
  suffix?:  string;
  change?:  number | null;
  icon:     string;
  color?:   string;
  index?:   number;
  animate?: boolean;
}

function useCountUp(target: number, duration = 900, delay = 0) {
  const [value, setValue] = useState(0);
  const frame = useRef<number>(0);

  useEffect(() => {
    const t = setTimeout(() => {
      const start = performance.now();
      const tick = (now: number) => {
        const progress = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        setValue(target * ease);
        if (progress < 1) frame.current = requestAnimationFrame(tick);
        else setValue(target);
      };
      frame.current = requestAnimationFrame(tick);
    }, delay);
    return () => { clearTimeout(t); cancelAnimationFrame(frame.current); };
  }, [target, duration, delay]);

  return value;
}

export default function KPICard({
  label, value, prefix = "", suffix = "",
  change, icon, color = "var(--accent-gold)", index = 0, animate = true,
}: KPICardProps) {
  const numValue = typeof value === "number" ? value : 0;
  const animated = useCountUp(animate ? numValue : 0, 850, index * 110);
  const display  = typeof value === "string" ? value : animated;

  const formatNum = (n: number) =>
    n >= 1000
      ? n.toLocaleString("es-VE", { minimumFractionDigits: 0, maximumFractionDigits: 0 })
      : n.toLocaleString("es-VE", { minimumFractionDigits: 0, maximumFractionDigits: 1 });

  const LucideIcon = ICON_MAP[icon];

  const changePositive = (change ?? 0) > 0;
  const changeNegative = (change ?? 0) < 0;
  const changeColor = changePositive ? "var(--success)" : changeNegative ? "var(--danger)" : "var(--text-muted)";
  const changeBg    = changePositive
    ? "color-mix(in srgb, var(--success) 10%, transparent)"
    : changeNegative
    ? "color-mix(in srgb, var(--danger) 10%, transparent)"
    : "color-mix(in srgb, var(--text-muted) 10%, transparent)";

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.09, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3, boxShadow: `0 12px 36px color-mix(in srgb, ${color} 18%, transparent)` }}
      className="card relative overflow-hidden cursor-default group"
    >
      {/* Animated top border */}
      <div
        className="absolute top-0 left-0 right-0 h-[2px]"
        style={{
          background: `linear-gradient(90deg, transparent 0%, ${color} 40%, ${color} 60%, transparent 100%)`,
          opacity: 0.8,
        }}
      />

      {/* Subtle background glow on hover */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-500"
        style={{
          background: `radial-gradient(ellipse at top left, color-mix(in srgb, ${color} 6%, transparent), transparent 70%)`,
        }}
      />

      {/* Watermark icon */}
      <div className="absolute right-4 bottom-3 pointer-events-none select-none opacity-[0.04]">
        {LucideIcon
          ? <LucideIcon size={56} strokeWidth={1.2} />
          : <span className="text-5xl">{icon}</span>
        }
      </div>

      {/* Header: icon badge + change badge */}
      <div className="flex items-start justify-between mb-4 relative">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{
            background: `color-mix(in srgb, ${color} 14%, transparent)`,
            border: `1px solid color-mix(in srgb, ${color} 28%, transparent)`,
          }}
        >
          {LucideIcon
            ? <LucideIcon size={18} style={{ color }} strokeWidth={2} />
            : <span className="text-lg">{icon}</span>
          }
        </div>

        {change !== undefined && change !== null && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.09 + 0.3 }}
            className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full"
            style={{ background: changeBg, color: changeColor }}
          >
            {changePositive
              ? <TrendingUp size={10} />
              : changeNegative
              ? <TrendingDown size={10} />
              : <Minus size={10} />
            }
            {Math.abs(change).toFixed(1)}%
          </motion.div>
        )}
      </div>

      {/* Value */}
      <div className="relative">
        <p
          className="text-2xl font-bold leading-none"
          style={{ fontFamily: "var(--font-mono)", color }}
        >
          {prefix}
          {typeof display === "number" ? formatNum(display) : display}
          {suffix}
        </p>
        <p
          className="text-xs mt-2 font-medium"
          style={{ color: "var(--text-muted)" }}
        >
          {label}
        </p>
      </div>
    </motion.div>
  );
}
