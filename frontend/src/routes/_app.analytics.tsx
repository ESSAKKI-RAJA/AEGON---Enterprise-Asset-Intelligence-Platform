import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import {
  BarChart3,
  Activity,
  Target,
  Download,
  ShieldAlert,
  AlertOctagon,
  LineChart,
  PieChart as PieChartIcon,
  Factory,
} from "lucide-react";
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
  Legend,
} from "recharts";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";

export const Route = createFileRoute("/_app/analytics")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ["enterpriseAnalytics"],
    queryFn: () => apiClient.get("/analytics/"),
  });

  return (
    <PageLayout>
      <PageHeader
        title="Executive Business Intelligence Center"
        description="Cross-Functional Health, Department Performance & Strategic Intelligence"
        actions={
          <button className="flex items-center gap-2 rounded bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-lg px-4 py-2 text-xs font-semibold font-mono transition-colors">
            <Download className="h-4 w-4" />
            Export Executive Report
          </button>
        }
      />

      {isLoading ? (
        <div className="flex h-[400px] items-center justify-center space-x-2">
          <div className="h-4 w-4 animate-bounce rounded-full bg-indigo-500"></div>
          <div
            className="h-4 w-4 animate-bounce rounded-full bg-teal-400"
            style={{ animationDelay: "0.2s" }}
          ></div>
          <div
            className="h-4 w-4 animate-bounce rounded-full bg-blue-500"
            style={{ animationDelay: "0.4s" }}
          ></div>
        </div>
      ) : (
        <>
          {/* Top Level Risk Alert */}
          {data?.enterprise_risk && data.enterprise_risk.level !== "Low" && (
            <div className="rounded-xl border border-orange-500/30 bg-orange-950/20 p-5 flex gap-4 items-center mb-6 shadow-lg backdrop-blur-sm">
              <AlertOctagon className="h-8 w-8 text-orange-400 shrink-0" />
              <div>
                <h4 className="text-orange-400 font-bold font-mono text-lg">
                  Enterprise Risk: {data.enterprise_risk.level}
                </h4>
                <p className="text-sm text-orange-200/70 mt-1">
                  Primary Driver:{" "}
                  <span className="text-orange-300 font-medium">
                    {data.enterprise_risk.primary_driver}
                  </span>{" "}
                  | Impact Area:{" "}
                  <span className="text-orange-300 font-medium">
                    {data.enterprise_risk.impact_area}
                  </span>
                </p>
              </div>
            </div>
          )}

          {/* KPIs */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {data?.kpis?.map((kpi: any, idx: number) => {
              let Icon = BarChart3;
              if (kpi.label.toLowerCase().includes("health")) Icon = Activity;
              if (kpi.label.toLowerCase().includes("compliance")) Icon = Target;
              if (kpi.deltaTone === "critical") Icon = ShieldAlert;

              return (
                <MetricCard
                  key={idx}
                  label={kpi.label}
                  value={kpi.value}
                  delta={kpi.delta}
                  deltaTone={kpi.deltaTone}
                  icon={<Icon className="h-4 w-4" />}
                />
              );
            })}
          </div>

          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Asset Health Distribution (Pie Chart) */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
              <SectionHeader
                title="Asset Health Distribution"
                icon={<PieChartIcon className="h-5 w-5 text-teal-400" />}
              />
              <div className="h-[250px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data?.visual_analytics?.health_distribution || []}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {(data?.visual_analytics?.health_distribution || []).map(
                        (entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ),
                      )}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#1e293b",
                        borderRadius: "8px",
                        color: "#f8fafc",
                      }}
                      itemStyle={{ fontWeight: 600 }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Distribution (Pie Chart) */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
              <SectionHeader
                title="Enterprise Risk Heatmap"
                icon={<AlertOctagon className="h-5 w-5 text-orange-400" />}
              />
              <div className="h-[250px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data?.visual_analytics?.risk_distribution || []}
                      cx="50%"
                      cy="50%"
                      innerRadius={0}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {(data?.visual_analytics?.risk_distribution || []).map(
                        (entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ),
                      )}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#1e293b",
                        borderRadius: "8px",
                        color: "#f8fafc",
                      }}
                      itemStyle={{ fontWeight: 600 }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Maintenance & Downtime Trends */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
              <SectionHeader
                title="Maintenance & Downtime Trends"
                icon={<LineChart className="h-5 w-5 text-indigo-400" />}
              />
              <div className="h-[300px] mt-6">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={data?.metrics_history || []}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorDowntime" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                    <XAxis
                      dataKey="month"
                      stroke="#64748b"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      dy={10}
                    />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <RechartsTooltip
                      cursor={{ stroke: "#334155", strokeWidth: 1, strokeDasharray: "4 4" }}
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#1e293b",
                        borderRadius: "8px",
                        color: "#f8fafc",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="downtime"
                      name="Downtime (Hours)"
                      stroke="#6366f1"
                      strokeWidth={3}
                      fillOpacity={1}
                      fill="url(#colorDowntime)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Department Performance */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
              <SectionHeader
                title="Department Performance (Avg Health)"
                icon={<Factory className="h-5 w-5 text-sky-400" />}
              />
              <div className="h-[300px] mt-6">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data?.visual_analytics?.department_performance || []}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                    <XAxis
                      dataKey="department"
                      stroke="#64748b"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      dy={10}
                    />
                    <YAxis
                      stroke="#64748b"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      domain={[0, 100]}
                    />
                    <RechartsTooltip
                      cursor={{ fill: "#1e293b", opacity: 0.4 }}
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#1e293b",
                        borderRadius: "8px",
                        color: "#f8fafc",
                      }}
                    />
                    <Bar
                      dataKey="avg_health"
                      name="Avg Health Score"
                      fill="#38bdf8"
                      radius={[4, 4, 0, 0]}
                      barSize={40}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2 mb-8">
            {/* Top Critical Assets Table */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
              <SectionHeader
                title="Top Critical Assets"
                icon={<ShieldAlert className="h-5 w-5 text-red-400" />}
              />
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700">
                    <tr>
                      <th className="px-4 py-3 font-mono">Asset Name</th>
                      <th className="px-4 py-3 font-mono">Department</th>
                      <th className="px-4 py-3 font-mono text-right">Health</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.visual_analytics?.top_critical_assets?.map((asset: any, idx: number) => (
                      <tr
                        key={idx}
                        className="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-4 py-3 font-medium text-slate-200">{asset.name}</td>
                        <td className="px-4 py-3 text-slate-400">{asset.department}</td>
                        <td className="px-4 py-3 text-right">
                          <span className="bg-red-950/50 text-red-400 border border-red-900/50 px-2 py-1 rounded text-xs font-mono font-bold">
                            {asset.health.toFixed(1)}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {(!data?.visual_analytics?.top_critical_assets ||
                      data.visual_analytics.top_critical_assets.length === 0) && (
                      <tr>
                        <td colSpan={3} className="px-4 py-8 text-center text-slate-500 font-mono">
                          No critical assets detected.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Strategic AI Insights */}
            <div className="flex flex-col">
              <SectionHeader
                title="Strategic AI Insights"
                icon={<Activity className="h-5 w-5 text-indigo-400" />}
              />
              <div className="mt-4 flex flex-col gap-4 flex-1">
                {data?.insights?.map((insight: any, idx: number) => (
                  <AIInsightCard
                    key={idx}
                    insight={insight.insight}
                    reasoning={insight.reasoning}
                    action={insight.action}
                    domain={insight.domain}
                    priority={insight.priority?.toLowerCase() || "high"}
                  />
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </PageLayout>
  );
}
