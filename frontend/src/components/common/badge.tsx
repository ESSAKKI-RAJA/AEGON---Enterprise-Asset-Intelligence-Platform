import { cn } from "@/lib/utils";

export type StatusVariant =
  | "healthy"
  | "warning"
  | "critical"
  | "info"
  | "Excellent"
  | "Good"
  | "At Risk"
  | "Critical"
  | "Active"
  | "Maintenance"
  | "Inactive"
  | "Disposed"
  | "Scheduled"
  | "In Progress"
  | "Completed"
  | "Emergency"
  | "Preventive"
  | "Corrective";

const map: Record<string, string> = {
  healthy: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-amber-200",
  critical: "bg-red-50 text-red-700 ring-red-200",
  info: "bg-blue-50 text-blue-700 ring-blue-200",
  Excellent: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Good: "bg-blue-50 text-blue-700 ring-blue-200",
  "At Risk": "bg-amber-50 text-amber-700 ring-amber-200",
  Critical: "bg-red-50 text-red-700 ring-red-200",
  Active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Maintenance: "bg-amber-50 text-amber-700 ring-amber-200",
  Inactive: "bg-slate-100 text-slate-600 ring-slate-200",
  Disposed: "bg-slate-100 text-slate-500 ring-slate-200",
  Scheduled: "bg-blue-50 text-blue-700 ring-blue-200",
  "In Progress": "bg-amber-50 text-amber-700 ring-amber-200",
  Completed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Emergency: "bg-red-50 text-red-700 ring-red-200",
  Preventive: "bg-teal-50 text-teal-700 ring-teal-200",
  Corrective: "bg-indigo-50 text-indigo-700 ring-indigo-200",
};

export function AegonBadge({
  variant,
  children,
  className,
}: {
  variant: StatusVariant;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-[20px] px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset whitespace-nowrap",
        map[variant] ?? map.info,
        className,
      )}
    >
      <span className="size-1.5 rounded-full bg-current opacity-70" />
      {children ?? variant}
    </span>
  );
}
