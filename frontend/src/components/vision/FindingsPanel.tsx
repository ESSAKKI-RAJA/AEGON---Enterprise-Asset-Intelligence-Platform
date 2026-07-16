/**
 * FindingsPanel — AI defect findings with animated confidence bars.
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronRight, AlertTriangle, AlertOctagon, Info, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DefectFinding, DefectSeverity } from "@/types/vision";

interface FindingsPanelProps {
  findings: DefectFinding[];
  viewLabel?: string;
  onCreateTicket?: (finding: DefectFinding) => void;
  isCreatingTicket?: boolean;
}

const SEVERITY_CONFIG: Record<
  DefectSeverity,
  { label: string; color: string; bg: string; border: string; icon: any; bar: string }
> = {
  critical: {
    label: "CRITICAL",
    color: "text-red-400",
    bg: "bg-red-950/30",
    border: "border-red-500/40",
    icon: AlertOctagon,
    bar: "bg-red-500",
  },
  high: {
    label: "HIGH",
    color: "text-orange-400",
    bg: "bg-orange-950/20",
    border: "border-orange-500/30",
    icon: AlertTriangle,
    bar: "bg-orange-500",
  },
  medium: {
    label: "MEDIUM",
    color: "text-amber-400",
    bg: "bg-amber-950/20",
    border: "border-amber-500/30",
    icon: Info,
    bar: "bg-amber-500",
  },
  low: {
    label: "LOW",
    color: "text-teal-400",
    bg: "bg-teal-950/20",
    border: "border-teal-500/30",
    icon: Info,
    bar: "bg-teal-500",
  },
  none: {
    label: "NONE",
    color: "text-slate-400",
    bg: "bg-slate-900/50",
    border: "border-slate-700",
    icon: CheckCircle2,
    bar: "bg-slate-500",
  },
};

function ConfidenceBar({ value, barClass }: { value: number; barClass: string }) {
  return (
    <div className="relative h-1 rounded-full bg-slate-800/80 overflow-hidden">
      <motion.div
        className={cn("h-full rounded-full", barClass)}
        initial={{ width: 0 }}
        animate={{ width: `${value * 100}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />
    </div>
  );
}

function FindingCard({
  finding,
  index,
  onCreateTicket,
  isCreatingTicket,
}: {
  finding: DefectFinding;
  index: number;
  onCreateTicket?: (finding: DefectFinding) => void;
  isCreatingTicket?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const cfg = SEVERITY_CONFIG[finding.severity];
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className={cn(
        "rounded-lg border overflow-hidden",
        cfg.border,
        finding.severity === "critical" && "shadow-[0_0_12px_rgba(239,68,68,0.15)]",
      )}
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className={cn(
          "w-full flex items-start gap-3 p-3 text-left transition-colors",
          cfg.bg,
          "hover:brightness-110",
        )}
      >
        <Icon className={cn("h-4 w-4 shrink-0 mt-0.5", cfg.color)} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1.5 gap-2">
            <span className="text-xs font-semibold text-slate-200 font-mono truncate">
              {finding.defect_type}
            </span>
            <span
              className={cn(
                "shrink-0 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded",
                cfg.color,
                cfg.bg,
                "border",
                cfg.border,
              )}
            >
              {cfg.label}
            </span>
          </div>
          {/* Confidence bar */}
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-mono text-slate-500 shrink-0">
              Confidence
            </span>
            <div className="flex-1">
              <ConfidenceBar value={finding.confidence} barClass={cfg.bar} />
            </div>
            <span className={cn("text-[10px] font-mono font-bold shrink-0", cfg.color)}>
              {Math.round(finding.confidence * 100)}%
            </span>
          </div>
        </div>
        {expanded ? (
          <ChevronDown className="h-3 w-3 text-slate-500 shrink-0 mt-0.5" />
        ) : (
          <ChevronRight className="h-3 w-3 text-slate-500 shrink-0 mt-0.5" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden border-t border-slate-800/60"
          >
            <div className="p-3 space-y-2 bg-slate-950/50">
              <p className="text-[11px] text-slate-400 leading-relaxed">
                {finding.description}
              </p>
              <div className="flex items-start gap-1.5 mt-2">
                <div className="shrink-0 mt-0.5 h-3 w-3 rounded-full border border-indigo-500/50 flex items-center justify-center">
                  <div className="h-1 w-1 rounded-full bg-indigo-400" />
                </div>
                <p className="text-[10px] font-mono text-indigo-400">
                  {finding.recommended_action}
                </p>
              </div>
              {finding.area_affected_pct > 0 && (
                <p className="text-[9px] font-mono text-slate-600">
                  Area affected: {finding.area_affected_pct.toFixed(1)}%
                </p>
              )}
              {/* Cost and Time estimates */}
              {(finding.estimated_repair_cost > 0 || finding.estimated_repair_time_mins > 0) && (
                <div className="flex items-center gap-4 mt-2 pt-2 border-t border-slate-800/50">
                  {finding.estimated_repair_cost > 0 && (
                    <span className="text-[9px] font-mono text-amber-500/80">Est. Cost: ${finding.estimated_repair_cost.toFixed(2)}</span>
                  )}
                  {finding.estimated_repair_time_mins > 0 && (
                    <span className="text-[9px] font-mono text-blue-400/80">Est. Time: {finding.estimated_repair_time_mins} mins</span>
                  )}
                </div>
              )}
              {/* Action buttons */}
              {(finding.severity === "critical" || finding.severity === "high") && onCreateTicket && (
                <div className="mt-3">
                  <button
                    onClick={(e) => { e.stopPropagation(); onCreateTicket(finding); }}
                    disabled={isCreatingTicket}
                    className="w-full py-1.5 px-3 rounded bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-400 text-[10px] font-mono font-bold transition-colors disabled:opacity-50"
                  >
                    CREATE MAINTENANCE TICKET
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FindingsPanel({ findings, viewLabel, onCreateTicket, isCreatingTicket }: FindingsPanelProps) {
  const [filter, setFilter] = useState<DefectSeverity | "all">("all");

  const severityOrder: DefectSeverity[] = ["critical", "high", "medium", "low", "none"];
  const sorted = [...findings].sort(
    (a, b) => severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity),
  );

  const filtered = filter === "all" ? sorted : sorted.filter((f) => f.severity === filter);

  const counts = findings.reduce(
    (acc, f) => {
      acc[f.severity] = (acc[f.severity] ?? 0) + 1;
      return acc;
    },
    {} as Record<DefectSeverity, number>,
  );

  if (findings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <CheckCircle2 className="h-8 w-8 text-emerald-400 mb-2" />
        <p className="text-sm font-mono text-emerald-400 font-semibold">No Defects Detected</p>
        <p className="text-xs font-mono text-slate-500 mt-1">
          {viewLabel ? `${viewLabel} surface is in excellent condition.` : "Surface is pristine."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Filter chips */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <button
          onClick={() => setFilter("all")}
          className={cn(
            "px-2 py-0.5 rounded text-[9px] font-mono font-bold border transition-colors",
            filter === "all"
              ? "bg-slate-700 border-slate-500 text-white"
              : "border-slate-700 text-slate-500 hover:text-slate-300",
          )}
        >
          ALL ({findings.length})
        </button>
        {(["critical", "high", "medium", "low"] as DefectSeverity[]).map((sev) => {
          const cnt = counts[sev];
          if (!cnt) return null;
          const cfg = SEVERITY_CONFIG[sev];
          return (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              className={cn(
                "px-2 py-0.5 rounded text-[9px] font-mono font-bold border transition-colors",
                filter === sev ? `${cfg.bg} ${cfg.border} ${cfg.color}` : "border-slate-700 text-slate-500 hover:text-slate-300",
              )}
            >
              {cfg.label} ({cnt})
            </button>
          );
        })}
      </div>

      {/* Finding cards */}
      <div className="space-y-2">
        <AnimatePresence>
          {filtered.map((finding, i) => (
            <FindingCard
              key={finding.finding_id}
              finding={finding}
              index={i}
              onCreateTicket={onCreateTicket}
              isCreatingTicket={isCreatingTicket}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
