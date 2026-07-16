/**
 * InspectionHistory — Searchable, filterable history of past inspections.
 */
import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Clock, AlertTriangle, CheckCircle2, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import type { InspectionHistoryItem, MaintenancePriority } from "@/types/vision";

interface InspectionHistoryProps {
  items: InspectionHistoryItem[];
  isLoading?: boolean;
}

const PRIORITY_CONFIG: Record<
  MaintenancePriority,
  { label: string; color: string; bg: string }
> = {
  immediate: { label: "IMMEDIATE", color: "text-red-400", bg: "bg-red-950/30 border-red-500/30" },
  within_7_days: { label: "7 DAYS", color: "text-orange-400", bg: "bg-orange-950/20 border-orange-500/30" },
  within_30_days: { label: "30 DAYS", color: "text-amber-400", bg: "bg-amber-950/20 border-amber-500/30" },
  within_90_days: { label: "90 DAYS", color: "text-blue-400", bg: "bg-blue-950/20 border-blue-500/30" },
  scheduled: { label: "SCHEDULED", color: "text-teal-400", bg: "bg-teal-950/20 border-teal-500/30" },
  none_required: { label: "OPTIMAL", color: "text-emerald-400", bg: "bg-emerald-950/20 border-emerald-500/30" },
};

function SkeletonRow() {
  return (
    <div className="grid grid-cols-7 gap-3 px-4 py-3 border-b border-slate-800/40">
      {[...Array(7)].map((_, i) => (
        <div key={i} className="h-3 rounded bg-slate-800 animate-pulse" />
      ))}
    </div>
  );
}

export function InspectionHistory({ items, isLoading }: InspectionHistoryProps) {
  const [search, setSearch] = useState("");
  const [filterPriority, setFilterPriority] = useState<MaintenancePriority | "all">("all");

  const filtered = items.filter((item) => {
    const matchSearch =
      search === "" ||
      item.asset_name.toLowerCase().includes(search.toLowerCase()) ||
      item.session_id.toLowerCase().includes(search.toLowerCase()) ||
      item.operator.toLowerCase().includes(search.toLowerCase());

    const matchPriority =
      filterPriority === "all" || item.maintenance_priority === filterPriority;

    return matchSearch && matchPriority;
  });

  return (
    <div className="space-y-3">
      {/* Controls */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search inspections..."
            className="w-full pl-8 pr-3 py-2 text-xs font-mono bg-slate-900 border border-slate-700 rounded-lg text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-teal-500/50"
          />
        </div>
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value as any)}
          className="px-3 py-2 text-xs font-mono bg-slate-900 border border-slate-700 rounded-lg text-slate-300 focus:outline-none focus:border-teal-500/50"
        >
          <option value="all">All Priorities</option>
          <option value="immediate">Immediate</option>
          <option value="within_7_days">Within 7 Days</option>
          <option value="within_30_days">Within 30 Days</option>
          <option value="within_90_days">Within 90 Days</option>
          <option value="none_required">Optimal</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-7 gap-3 px-4 py-2.5 bg-slate-950/80 border-b border-slate-800">
          {["Inspection ID", "Asset", "Operator", "Views", "Defects", "Health", "Priority"].map(
            (col) => (
              <span key={col} className="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-widest">
                {col}
              </span>
            ),
          )}
        </div>

        {/* Rows */}
        {isLoading ? (
          [...Array(5)].map((_, i) => <SkeletonRow key={i} />)
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-slate-500">
            <Activity className="h-6 w-6 mb-2 opacity-50" />
            <p className="text-xs font-mono">No inspections found</p>
            <p className="text-[10px] font-mono text-slate-600 mt-1">
              Run an inspection to see history here
            </p>
          </div>
        ) : (
          filtered.map((item, i) => {
            const pCfg = PRIORITY_CONFIG[item.maintenance_priority];
            return (
              <motion.div
                key={item.session_id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.03 }}
                className="grid grid-cols-7 gap-3 px-4 py-3 border-b border-slate-800/40 hover:bg-slate-800/30 transition-colors"
              >
                {/* ID */}
                <span className="text-[10px] font-mono text-slate-400 truncate">
                  {item.session_id.slice(0, 8).toUpperCase()}
                </span>
                {/* Asset */}
                <span className="text-[10px] font-mono text-slate-200 font-semibold truncate">
                  {item.asset_name}
                </span>
                {/* Operator */}
                <span className="text-[10px] font-mono text-slate-400 truncate">
                  {item.operator}
                </span>
                {/* Views */}
                <span className="text-[10px] font-mono text-indigo-400">
                  {item.views_inspected}
                </span>
                {/* Defects */}
                <div className="flex items-center gap-1">
                  {item.critical_defects > 0 ? (
                    <AlertTriangle className="h-3 w-3 text-red-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                  )}
                  <span className={cn("text-[10px] font-mono", item.critical_defects > 0 ? "text-red-400" : "text-slate-300")}>
                    {item.total_defects}
                  </span>
                </div>
                {/* Health */}
                <span
                  className={cn(
                    "text-[10px] font-mono font-bold",
                    item.health_score >= 75 ? "text-emerald-400" : item.health_score >= 50 ? "text-amber-400" : "text-red-400",
                  )}
                >
                  {item.health_score.toFixed(0)}%
                </span>
                {/* Priority */}
                <span
                  className={cn(
                    "text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border w-fit",
                    pCfg.bg,
                    pCfg.color,
                  )}
                >
                  {pCfg.label}
                </span>
              </motion.div>
            );
          })
        )}
      </div>

      <p className="text-[9px] font-mono text-slate-600 text-right">
        Showing {filtered.length} of {items.length} inspections
      </p>
    </div>
  );
}
