/**
 * DigitalTwinWidget — Live asset twin state panel updated per inspection.
 */
import { motion } from "framer-motion";
import {
  Activity,
  ThermometerSun,
  ShieldAlert,
  Wrench,
  CheckCircle2,
  Wind,
  RotateCcw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { DigitalTwinState, VisionViewType } from "@/types/vision";

interface DigitalTwinWidgetProps {
  twin: DigitalTwinState;
}

const ALL_VIEWS: { key: VisionViewType; label: string }[] = [
  { key: "top", label: "Top" },
  { key: "front", label: "Front" },
  { key: "rear", label: "Rear" },
  { key: "left", label: "Left" },
  { key: "right", label: "Right" },
  { key: "bottom", label: "Bottom" },
];

function HealthRing({ score }: { score: number }) {
  const radius = 42;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (circ * score) / 100;
  const color = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative flex items-center justify-center w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#1e293b" strokeWidth="10" />
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-xl font-bold font-mono text-white leading-none">
          {score.toFixed(0)}
        </span>
        <span className="text-[9px] font-mono text-slate-500">/ 100</span>
      </div>
    </div>
  );
}

function MetricRow({
  icon: Icon,
  label,
  value,
  valueClass = "text-slate-200",
}: {
  icon: any;
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-slate-800/60 last:border-0">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        <span className="text-[10px] font-mono uppercase tracking-wider">{label}</span>
      </div>
      <span className={cn("text-[11px] font-mono font-semibold", valueClass)}>{value}</span>
    </div>
  );
}

export function DigitalTwinWidget({ twin }: DigitalTwinWidgetProps) {
  const healthColor =
    twin.health_score >= 75
      ? "text-emerald-400"
      : twin.health_score >= 50
        ? "text-amber-400"
        : "text-red-400";

  const riskColor =
    twin.risk_score <= 20
      ? "text-emerald-400"
      : twin.risk_score <= 50
        ? "text-amber-400"
        : "text-red-400";

  const maintColor =
    twin.maintenance_status === "Up to Date"
      ? "text-emerald-400"
      : twin.maintenance_status.includes("Immediate")
        ? "text-red-400"
        : "text-amber-400";

  return (
    <div className="space-y-4">
      {/* Title & health ring */}
      <div className="flex items-center gap-4">
        <HealthRing score={twin.health_score} />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-mono font-bold text-slate-200 truncate">{twin.asset_name}</p>
          <p className="text-[9px] font-mono text-slate-500 mt-0.5">DIGITAL TWIN</p>
          <p className={cn("text-sm font-mono font-bold mt-1", healthColor)}>
            Health: {twin.health_score.toFixed(0)}/100
          </p>
        </div>
      </div>

      {/* Metrics */}
      <div className="rounded-lg border border-slate-800 bg-slate-950/50 px-3 py-1">
        <MetricRow
          icon={ShieldAlert}
          label="Risk Score"
          value={`${twin.risk_score.toFixed(0)}%`}
          valueClass={riskColor}
        />
        <MetricRow
          icon={ThermometerSun}
          label="Temperature"
          value={`${twin.temperature_celsius.toFixed(1)}°C`}
          valueClass={
            twin.temperature_celsius > 55
              ? "text-red-400"
              : twin.temperature_celsius > 40
                ? "text-amber-400"
                : "text-teal-400"
          }
        />
        <MetricRow
          icon={Wind}
          label="Pressure"
          value={`${twin.pressure_psi.toFixed(1)} PSI`}
          valueClass={twin.pressure_psi > 20 ? "text-red-400" : "text-slate-200"}
        />
        <MetricRow
          icon={RotateCcw}
          label="Rotation"
          value={`${twin.rotation_rpm.toFixed(0)} RPM`}
          valueClass={twin.rotation_rpm < 1000 ? "text-red-400" : "text-emerald-400"}
        />
        <MetricRow
          icon={Wrench}
          label="Maintenance"
          value={twin.maintenance_status}
          valueClass={maintColor}
        />
        <MetricRow
          icon={Activity}
          label="Inspection"
          value={`${twin.inspection_progress_pct.toFixed(0)}%`}
          valueClass="text-indigo-400"
        />
      </div>

      {/* View completion */}
      <div>
        <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest mb-2">
          View Progress
        </p>
        <div className="grid grid-cols-3 gap-1.5">
          {ALL_VIEWS.map(({ key, label }) => {
            const done = twin.views_completed.includes(key);
            return (
              <div
                key={key}
                className={cn(
                  "flex items-center gap-1 px-2 py-1 rounded text-[9px] font-mono font-bold border transition-colors",
                  done
                    ? "border-teal-500/40 bg-teal-950/30 text-teal-400"
                    : "border-slate-700/50 bg-slate-900/50 text-slate-600",
                )}
              >
                {done && <CheckCircle2 className="h-2.5 w-2.5 shrink-0" />}
                {label}
              </div>
            );
          })}
        </div>
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-[9px] font-mono text-slate-500 mb-1.5">
          <span>Overall Progress</span>
          <span className="text-indigo-400">{twin.inspection_progress_pct.toFixed(0)}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-teal-400"
            initial={{ width: 0 }}
            animate={{ width: `${twin.inspection_progress_pct}%` }}
            transition={{ duration: 0.8 }}
          />
        </div>
      </div>

      <p className="text-[8px] font-mono text-slate-600 text-right">
        Last updated: {new Date(twin.last_updated).toLocaleTimeString()}
      </p>
    </div>
  );
}
