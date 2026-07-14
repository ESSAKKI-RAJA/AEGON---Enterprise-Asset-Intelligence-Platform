import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface MetricCardProps {
  label: string;
  value: string | number;
  delta?: string;
  deltaPositive?: boolean;
  deltaTone?: "positive" | "critical" | "neutral" | "warning";
  icon?: ReactNode;
  className?: string;
}

export function MetricCard({
  label,
  value,
  delta,
  deltaPositive,
  deltaTone = "neutral",
  icon,
  className,
}: MetricCardProps) {
  let toneClass = "text-slate-500 dark:text-slate-400";
  let bgToneClass =
    "bg-slate-100 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700/50";

  if (deltaTone === "positive" || deltaPositive === true) {
    toneClass = "text-emerald-600 dark:text-emerald-400";
    bgToneClass =
      "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20";
  }
  if (deltaTone === "critical" || deltaPositive === false) {
    toneClass = "text-red-600 dark:text-red-400";
    bgToneClass =
      "bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-500/20";
  }
  if (deltaTone === "warning") {
    toneClass = "text-orange-600 dark:text-orange-400";
    bgToneClass =
      "bg-orange-50 dark:bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-500/20";
  }

  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className={cn(
        "rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm hover:shadow-md transition-shadow",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {label}
          </div>
          <div className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            {value}
          </div>
        </div>
        {icon && (
          <div className="rounded-lg p-2 bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 shadow-sm border border-slate-100 dark:border-slate-700">
            {icon}
          </div>
        )}
      </div>
      {delta && (
        <div className="mt-4 flex items-center">
          <span className={cn("text-[11px] font-bold px-2 py-0.5 rounded-md border", bgToneClass)}>
            {delta}
          </span>
        </div>
      )}
    </motion.div>
  );
}
