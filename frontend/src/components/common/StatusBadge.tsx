import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  type?: "health" | "risk" | "sla" | "general";
  className?: string;
}

export function StatusBadge({ status, type = "general", className }: StatusBadgeProps) {
  const s = status.toUpperCase().replace("_", " ");

  let colorClass = "bg-slate-800 text-slate-300";

  // Priority / Risk mapping
  if (s === "CRITICAL" || s === "HIGH" || s === "OVERDUE" || s === "DOWN") {
    colorClass = "bg-red-950 text-red-400";
  } else if (s === "MEDIUM" || s === "WARNING" || s === "AT RISK" || s === "OVER BUDGET") {
    colorClass = "bg-orange-950 text-orange-400";
  } else if (
    s === "LOW" ||
    s === "HEALTHY" ||
    s === "ON TRACK" ||
    s === "COMPLETED" ||
    s === "OPTIMAL"
  ) {
    colorClass = "bg-emerald-950 text-emerald-400";
  } else if (s === "PENDING" || s === "SCHEDULED" || s === "IN PROGRESS") {
    colorClass = "bg-blue-950 text-blue-400";
  }

  return (
    <span
      className={cn(
        "px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider",
        colorClass,
        className,
      )}
    >
      {s}
    </span>
  );
}
