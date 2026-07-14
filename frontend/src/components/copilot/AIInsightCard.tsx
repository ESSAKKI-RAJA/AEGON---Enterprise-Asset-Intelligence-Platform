import { ReactNode } from "react";
import { ArrowRight, Activity, AlertTriangle, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface AIInsightCardProps {
  insight: string;
  reasoning: string;
  action: string;
  confidence?: number;
  domain?: string;
  priority?: "low" | "medium" | "high" | "critical";
  className?: string;
}

export function AIInsightCard({
  insight,
  reasoning,
  action,
  confidence,
  domain,
  priority = "medium",
  className,
}: AIInsightCardProps) {
  // Set theme colors based on priority
  let borderClass =
    "border-indigo-200 dark:border-indigo-800/50 hover:border-indigo-300 dark:hover:border-indigo-500/50";
  let bgClass = "bg-white dark:bg-indigo-950/20";
  let iconBgClass = "bg-indigo-50 dark:bg-indigo-900/50";
  let textClass = "text-indigo-600 dark:text-indigo-400";
  let titleClass = "text-indigo-900 dark:text-indigo-300";

  let Icon = Activity;

  if (priority === "critical" || priority === "high") {
    borderClass =
      "border-red-200 dark:border-red-900/50 hover:border-red-300 dark:hover:border-red-500/50";
    bgClass = "bg-white dark:bg-red-950/20";
    iconBgClass = "bg-red-50 dark:bg-red-900/50";
    textClass = "text-red-600 dark:text-red-400";
    titleClass = "text-red-900 dark:text-red-300";
    Icon = priority === "critical" ? ShieldAlert : AlertTriangle;
  } else if (priority === "medium") {
    borderClass =
      "border-amber-200 dark:border-amber-900/50 hover:border-amber-300 dark:hover:border-amber-500/50";
    bgClass = "bg-white dark:bg-amber-950/20";
    iconBgClass = "bg-amber-50 dark:bg-amber-900/50";
    textClass = "text-amber-600 dark:text-amber-400";
    titleClass = "text-amber-900 dark:text-amber-300";
  }

  return (
    <motion.div
      whileHover={{ scale: 1.01, transition: { duration: 0.2 } }}
      className={cn(
        "rounded-xl border p-5 flex gap-4 items-start shadow-sm hover:shadow-md transition-all",
        borderClass,
        bgClass,
        className,
      )}
    >
      <div className={cn("p-2.5 rounded-lg shrink-0", iconBgClass, textClass)}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-2">
          {domain && (
            <div
              className={cn(
                "text-[10px] font-bold uppercase tracking-widest opacity-80",
                textClass,
              )}
            >
              {domain}
            </div>
          )}
          {confidence && (
            <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Confidence:{" "}
              <span className="font-mono text-slate-700 dark:text-slate-300">
                {confidence.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
        <h3 className={cn("font-bold text-sm mb-1.5 truncate", titleClass)}>{insight}</h3>
        <p className="text-sm text-slate-600 dark:text-slate-300 mb-4 line-clamp-2 leading-relaxed">
          {reasoning}
        </p>
        <div
          className={cn(
            "inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800",
            textClass,
          )}
        >
          {action} <ArrowRight className="h-3.5 w-3.5" />
        </div>
      </div>
    </motion.div>
  );
}
