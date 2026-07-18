/**
 * SeverityAnalytics — Recharts-based data visualization for Vision Intelligence.
 */
import { useMemo } from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
} from "recharts";
import type { DefectFinding, DigitalTwinState } from "@/types/vision";

interface SeverityAnalyticsProps {
  findings: DefectFinding[];
  digitalTwin: DigitalTwinState;
}

const SEVERITY_COLORS = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#f59e0b",
  low: "#14b8a6",
  none: "#64748b",
};

export function SeverityAnalytics({ findings, digitalTwin }: SeverityAnalyticsProps) {
  // Pie chart data
  const severityData = useMemo(() => {
    const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0, none: 0 };
    findings.forEach((f) => {
      if (counts[f.severity] !== undefined) counts[f.severity]++;
    });
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .map(([name, value]) => ({
        name: name.toUpperCase(),
        value,
        fill: SEVERITY_COLORS[name as keyof typeof SEVERITY_COLORS],
      }));
  }, [findings]);

  // Bar chart data (defects by type)
  const defectTypeData = useMemo(() => {
    const counts: Record<string, number> = {};
    findings.forEach((f) => {
      counts[f.defect_type] = (counts[f.defect_type] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5); // top 5
  }, [findings]);

  // Historical Health Data
  const healthData = useMemo(() => {
    return digitalTwin.historical_health_trend.map((val, idx) => ({
      name: `T-${digitalTwin.historical_health_trend.length - 1 - idx}`,
      health: val,
    }));
  }, [digitalTwin.historical_health_trend]);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* 1. Severity Distribution Pie */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-4">
          Severity Breakdown
        </h4>
        <div className="h-48">
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "1px solid #1e293b",
                    fontSize: "12px",
                    fontFamily: "monospace",
                  }}
                  itemStyle={{ color: "#f8fafc" }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs font-mono text-slate-600">
              No defects to display
            </div>
          )}
        </div>
      </div>

      {/* 2. Top Defect Types Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-4">
          Top Defect Types
        </h4>
        <div className="h-48">
          {defectTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={defectTypeData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fill: "#64748b", fontSize: 10, fontFamily: "monospace" }}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fill: "#94a3b8", fontSize: 10, fontFamily: "monospace" }}
                  width={80}
                />
                <RechartsTooltip
                  cursor={{ fill: "#1e293b" }}
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "1px solid #1e293b",
                    fontSize: "12px",
                    fontFamily: "monospace",
                  }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs font-mono text-slate-600">
              No defects to display
            </div>
          )}
        </div>
      </div>

      {/* 3. Historical Degradation Area Chart */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 md:col-span-2">
        <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-4">
          Historical Asset Health Degradation
        </h4>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={healthData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fill: "#64748b", fontSize: 10, fontFamily: "monospace" }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: "#64748b", fontSize: 10, fontFamily: "monospace" }}
              />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "1px solid #1e293b",
                  fontSize: "12px",
                  fontFamily: "monospace",
                }}
              />
              <Area
                type="monotone"
                dataKey="health"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorHealth)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
