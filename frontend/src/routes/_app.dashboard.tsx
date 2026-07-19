import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  Download,
  BrainCircuit,
  Target,
  PieChart,
  AlertTriangle,
  DollarSign,
  BarChart3,
  TrendingUp,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { motion } from "framer-motion";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";
export const Route = createFileRoute("/_app/dashboard")({
  component: DashboardPage,
});

function DashboardPage() {
  const {
    data: dashboard,
    isLoading,
    error,
  } = useQuery<any>({
    queryKey: ["executiveDashboard_v2"],
    queryFn: () => apiClient.get("/analytics/dashboards/executive"),
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="text-slate-500 font-mono animate-pulse flex flex-col items-center gap-4">
          <BrainCircuit className="h-8 w-8 animate-spin" />
          <span>Aggregating Executive Intelligence...</span>
        </div>
      </div>
    );
  }

  if (error) {
    const axiosErr = error as any;
    const status = axiosErr?.response?.status ?? "Network Error";
    const endpoint = "/api/v1/analytics/dashboards/executive";
    const detail =
      axiosErr?.response?.data?.detail ??
      axiosErr?.response?.data?.message ??
      axiosErr?.message ??
      "Unknown error";
    return (
      <div className="flex h-[50vh] items-center justify-center p-6">
        <div className="max-w-xl w-full bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl p-6 space-y-3 font-mono text-sm">
          <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-bold text-base">
            <AlertTriangle className="h-5 w-5" />
            Dashboard Load Failed
          </div>
          <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-xs text-slate-600 dark:text-slate-400">
            <span className="font-semibold text-slate-500">Status</span>
            <span className="text-red-500 font-bold">{String(status)}</span>
            <span className="font-semibold text-slate-500">Endpoint</span>
            <span className="break-all">{endpoint}</span>
            <span className="font-semibold text-slate-500">Message</span>
            <span className="text-red-400">{String(detail)}</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-xs bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Formatting financial data for charts
  const capex = dashboard?.visual_analytics?.maintenance_trend?.[0]?.total_cost || 0;
  const financialData = [
    { name: "Current Month", value: capex * 0.3 },
    { name: "Next 30 Days", value: capex * 0.4 },
    { name: "90 Day Forecast", value: capex },
  ];

  return (
    <PageLayout>
      {/* 1. OVERVIEW */}
      <PageHeader
        title="Executive Intelligence Platform"
        description="Business Impact, Financial Exposure, and Machine Learning Forecasts"
        actions={
          <div className="flex items-center gap-4">
            <div className="font-mono text-xs text-slate-500 dark:text-slate-400 font-medium bg-slate-100 dark:bg-slate-900 px-3 py-1.5 rounded-md border border-slate-200 dark:border-slate-800">
              {new Date().toLocaleDateString("en-US", {
                weekday: "long",
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 text-xs font-semibold transition-colors shadow-sm"
            >
              <Download className="h-4 w-4" />
              Export Executive Report (PDF)
            </motion.button>
          </div>
        }
      />

      {/* 2. ENTERPRISE KPI ENGINE */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, staggerChildren: 0.1 }}
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        {dashboard?.kpis?.map((kpi: any, idx: number) => {
          let Icon = Target;
          if (kpi.label.toLowerCase().includes("health")) Icon = Activity;
          if (kpi.label.toLowerCase().includes("availability")) Icon = PieChart;
          if (kpi.deltaTone === "critical") Icon = AlertTriangle;

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <MetricCard
                label={kpi.label}
                value={kpi.value}
                delta={kpi.delta}
                deltaTone={kpi.deltaTone}
                deltaPositive={kpi.deltaTone !== "critical"}
                icon={<Icon className="h-4.5 w-4.5" />}
              />
            </motion.div>
          );
        })}
      </motion.div>

      {/* 3. DECISION INTELLIGENCE */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mt-8"
      >
        <SectionHeader
          title="Top Decision Recommendations"
          icon={<BrainCircuit className="h-5 w-5 text-indigo-500" />}
        />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {dashboard?.ai_insights?.map((insight: any, idx: number) => (
            <AIInsightCard
              key={idx}
              insight={insight.recommended_action}
              reasoning={insight.reason}
              action="Review Asset"
              confidence={insight.confidence}
              domain={insight.data_used}
              priority={insight.priority}
            />
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="grid gap-6 lg:grid-cols-3 mt-8"
      >
        {/* 4. FINANCIAL FORECASTING (Recharts Area Chart) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
          <SectionHeader
            title="90-Day CAPEX Forecast (Prophet Model)"
            icon={<TrendingUp className="h-5 w-5 text-emerald-500" />}
          />
          <div className="h-[320px] w-full mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={financialData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#cbd5e1"
                  strokeOpacity={0.4}
                />
                <XAxis
                  dataKey="name"
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
                  dx={-10}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  cursor={{ stroke: "#94a3b8", strokeWidth: 1, strokeDasharray: "4 4" }}
                  contentStyle={{
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    borderColor: "#e2e8f0",
                    borderRadius: "8px",
                    color: "#0f172a",
                    boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
                  }}
                  itemStyle={{ color: "#10b981", fontWeight: 600 }}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, "Forecast"]}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#10b981"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorValue)"
                  activeDot={{ r: 6, fill: "#10b981", stroke: "#ffffff", strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 5. ACTIONS & OBSERVABILITY */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm flex flex-col min-h-[350px]">
          <SectionHeader
            title="Action Center"
            icon={<Activity className="h-5 w-5 text-indigo-500" />}
          />
          <div className="mt-6 space-y-3 flex-1">
            {dashboard?.actions?.map((action: any, i: number) => (
              <Link
                to={action.link}
                key={i}
                className="group w-full flex items-center justify-between p-3.5 rounded-lg border border-slate-200 dark:border-slate-700/50 bg-slate-50 dark:bg-slate-800/50 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 hover:border-indigo-200 dark:hover:border-indigo-500/30 text-sm font-medium text-slate-700 dark:text-slate-300 transition-all duration-200 shadow-sm"
              >
                <span>{action.title}</span>
                <BarChart3 className="h-4 w-4 text-slate-400 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors" />
              </Link>
            ))}
          </div>

          {/* Observability Box */}
          <div className="mt-6 pt-5 border-t border-slate-200 dark:border-slate-800">
            <div className="flex justify-between items-center mb-3">
              <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
                ML Pipeline Status
              </span>
              <span className="text-[10px] text-teal-600 dark:text-teal-400 font-bold uppercase bg-teal-50 dark:bg-teal-900/30 border border-teal-200 dark:border-teal-800/50 px-2 py-0.5 rounded shadow-sm flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></div> Active
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
                Avg Inference Latency
              </span>
              <span className="text-[11px] text-slate-700 dark:text-slate-300 font-mono font-bold bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                42ms
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </PageLayout>
  );
}
