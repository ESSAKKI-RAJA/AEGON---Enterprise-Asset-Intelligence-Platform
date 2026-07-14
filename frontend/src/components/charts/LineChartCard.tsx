import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import { Download } from "lucide-react";

interface LineChartCardProps {
  title: string;
  data: any[];
  xKey: string;
  lines: { key: string; name: string; color: string }[];
  icon?: React.ReactNode;
  exportable?: boolean;
  className?: string;
}

export function LineChartCard({
  title,
  data,
  xKey,
  lines,
  icon,
  exportable = false,
  className,
}: LineChartCardProps) {
  return (
    <div
      className={cn("rounded border border-slate-800 bg-slate-900 p-5 flex flex-col", className)}
    >
      <div className="mb-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          {icon && <div className="text-slate-400">{icon}</div>}
          <h3 className="font-bold font-mono text-slate-200">{title}</h3>
        </div>
        {exportable && (
          <button className="text-xs font-mono text-slate-400 hover:text-white flex items-center gap-1 transition-colors">
            <Download className="h-3 w-3" /> Export
          </button>
        )}
      </div>

      <div className="flex-1 w-full min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey={xKey}
              stroke="#64748b"
              tick={{ fill: "#64748b", fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fill: "#64748b", fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#1e293b",
                color: "#f8fafc",
                fontFamily: "monospace",
                fontSize: "12px",
              }}
              itemStyle={{ color: "#e2e8f0" }}
            />
            {lines.map((l) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                name={l.name}
                stroke={l.color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
