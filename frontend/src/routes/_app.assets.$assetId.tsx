import { createFileRoute, Link, useParams, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import {
  ArrowLeft,
  Activity,
  ShieldAlert,
  DollarSign,
  Clock,
  Settings,
  Link as LinkIcon,
  FileText,
  CheckCircle2,
  ArrowUpRight,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";

export const Route = createFileRoute("/_app/assets/$assetId")({
  component: AssetDigitalTwinPage,
});

function AssetDigitalTwinPage() {
  const { assetId } = Route.useParams();
  const navigate = useNavigate();

  const {
    data: twin,
    isLoading,
    error,
  } = useQuery<any>({
    queryKey: ["assetDigitalTwin", assetId],
    queryFn: () => apiClient.get(`/assets/${assetId}`),
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="text-slate-500 font-mono animate-pulse">Loading Digital Twin...</div>
      </div>
    );
  }

  if (error || !twin) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-red-400 font-mono">
        Failed to load Asset Digital Twin.
      </div>
    );
  }

  const { identity, lifecycle, intelligence, relationships } = twin;

  const finData = [
    { name: "Current Value", value: intelligence.financial_intelligence.current_value },
    { name: "Depreciation", value: intelligence.financial_intelligence.accumulated_depreciation },
  ];
  const COLORS = ["#2dd4bf", "#1e293b"];

  return (
    <PageLayout>
      {/* HEADER & IDENTITY */}
      <div className="mb-2">
        <Link
          to="/assets"
          className="inline-flex items-center gap-2 text-xs font-mono text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          <ArrowLeft className="h-3 w-3" />
          Back to Registry
        </Link>
      </div>

      <PageHeader
        title={identity.name}
        description={`ID: ${identity.barcode} | Dept: ${identity.department} | Cat: ${identity.category}`}
        actions={
          <>
            <StatusBadge status={identity.status} type="general" />
            <button className="flex items-center gap-2 rounded bg-slate-800 px-4 py-2 text-sm font-mono text-slate-200 hover:bg-slate-700 transition-colors ml-4">
              <Settings className="h-4 w-4" />
              Manage
            </button>
            <Link
              to="/maintenance"
              className="flex items-center gap-2 rounded bg-indigo-600 px-4 py-2 text-sm font-mono text-white hover:bg-indigo-500 transition-colors"
            >
              <Activity className="h-4 w-4" />
              Schedule Maintenance
            </Link>
          </>
        }
      />

      {/* LIFECYCLE TIMELINE (Simplified horizontal) */}
      <div className="rounded border border-slate-800 bg-slate-900 p-5">
        <SectionHeader title="Lifecycle Timeline" icon={<Clock className="h-4 w-4" />} />
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 relative mt-4">
          <div className="absolute top-1/2 left-0 right-0 h-px bg-slate-800 -z-10 -translate-y-1/2"></div>

          <div className="flex flex-col items-center gap-2 bg-slate-900 px-2">
            <div className="h-3 w-3 rounded-full bg-teal-500 ring-4 ring-slate-900"></div>
            <span className="text-center">
              Procured
              <br />
              {lifecycle.purchase_date
                ? new Date(lifecycle.purchase_date).toLocaleDateString()
                : "N/A"}
            </span>
          </div>

          <div className="flex flex-col items-center gap-2 bg-slate-900 px-2">
            <div className="h-3 w-3 rounded-full bg-teal-500 ring-4 ring-slate-900"></div>
            <span>Installed</span>
          </div>

          <div className="flex flex-col items-center gap-2 bg-slate-900 px-2">
            <div className="h-3 w-3 rounded-full bg-teal-500 ring-4 ring-slate-900"></div>
            <span className="text-teal-400 font-semibold">Active</span>
          </div>

          <div className="flex flex-col items-center gap-2 bg-slate-900 px-2">
            <div className="h-3 w-3 rounded-full border border-slate-600 bg-slate-800 ring-4 ring-slate-900"></div>
            <span className="text-center">
              Next Maint
              <br />
              {lifecycle.next_maintenance
                ? new Date(lifecycle.next_maintenance).toLocaleDateString()
                : "N/A"}
            </span>
          </div>

          <div className="flex flex-col items-center gap-2 bg-slate-900 px-2 opacity-50">
            <div className="h-3 w-3 rounded-full border border-slate-600 bg-slate-800 ring-4 ring-slate-900"></div>
            <span>Disposal</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* HEALTH INTELLIGENCE */}
        <div className="rounded border border-slate-800 bg-slate-900 p-5 flex flex-col">
          <SectionHeader
            title="Health Intelligence"
            icon={<Activity className="h-4 w-4 text-teal-400" />}
          />
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            <div className="relative flex items-center justify-center">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="58"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  className="text-slate-800"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="58"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  strokeDasharray={364}
                  strokeDashoffset={364 - (364 * intelligence.health_intelligence.score) / 100}
                  className={
                    intelligence.health_intelligence.score < 50
                      ? "text-red-500"
                      : intelligence.health_intelligence.score < 75
                        ? "text-orange-500"
                        : "text-teal-500"
                  }
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-bold font-mono text-white">
                  {intelligence.health_intelligence.score.toFixed(0)}
                </span>
                <span className="text-xs font-mono text-slate-400">/ 100</span>
              </div>
            </div>
            <div className="mt-6 w-full space-y-2 text-sm font-mono text-slate-300">
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">Status</span>
                <span className="capitalize">{intelligence.health_intelligence.status}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">Asset Age</span>
                <span>{intelligence.health_intelligence.age_years} Years</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Utilization Rate</span>
                <span>{intelligence.health_intelligence.utilization_rate}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* RISK INTELLIGENCE */}
        <div className="rounded border border-indigo-900/50 bg-indigo-950/10 p-5 flex flex-col">
          <SectionHeader
            title="AI Failure Prediction"
            icon={<ShieldAlert className="h-4 w-4 text-indigo-400" />}
          />
          <div className="flex-1 flex flex-col gap-4 mt-2">
            <AIInsightCard
              insight={`${intelligence.risk_intelligence.failure_probability} Risk Level`}
              reasoning={intelligence.risk_intelligence.reason}
              action={intelligence.risk_intelligence.recommended_action}
              confidence={parseFloat(intelligence.risk_intelligence.confidence)}
              domain="Asset Reliability"
              priority={
                intelligence.risk_intelligence.failure_probability.includes("High")
                  ? "critical"
                  : "medium"
              }
              className="border-none p-0 bg-transparent"
            />
            <div className="grid grid-cols-2 gap-2 mt-auto">
              <div className="bg-slate-900/50 p-2 rounded">
                <div className="text-[10px] text-slate-500 font-mono mb-1 uppercase tracking-wider">
                  Remaining Life
                </div>
                <div className="text-sm font-bold text-slate-200">
                  {intelligence.risk_intelligence.estimated_remaining_useful_life}
                </div>
              </div>
              <div className="bg-slate-900/50 p-2 rounded">
                <div className="text-[10px] text-slate-500 font-mono mb-1 uppercase tracking-wider">
                  Est. Repair Cost
                </div>
                <div className="text-sm font-bold text-slate-200">
                  {intelligence.risk_intelligence.estimated_repair_cost}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FINANCIAL INTELLIGENCE */}
        <div className="rounded border border-slate-800 bg-slate-900 p-5 flex flex-col">
          <SectionHeader
            title="Financial Value"
            icon={<DollarSign className="h-4 w-4 text-emerald-400" />}
          />
          <div className="flex-1 flex flex-col mt-2">
            <div className="h-32 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={finData}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={50}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {finData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => `$${value.toLocaleString()}`}
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#1e293b",
                      color: "#f8fafc",
                      fontSize: "12px",
                      fontFamily: "monospace",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2 text-sm font-mono text-slate-300">
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">Current Value</span>
                <span className="font-bold text-emerald-400">
                  ${intelligence.financial_intelligence.current_value.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">Accumulated Depr.</span>
                <span className="text-red-400">
                  -${intelligence.financial_intelligence.accumulated_depreciation.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">Purchase Cost</span>
                <span>${intelligence.financial_intelligence.purchase_cost.toLocaleString()}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/50 pb-2">
                <span className="text-slate-500">YTD Maintenance Cost</span>
                <span>
                  ${intelligence.financial_intelligence.maintenance_cost_ytd.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RELATIONSHIPS & DOCUMENTS */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded border border-slate-800 bg-slate-900 p-5">
          <SectionHeader title="Enterprise Relationships" icon={<LinkIcon className="h-4 w-4" />} />
          <ul className="space-y-2 text-sm font-mono text-slate-400 mt-2">
            <Link
              to="/maintenance"
              className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 hover:bg-slate-800 transition-colors"
            >
              <span className="flex items-center gap-2">
                <Settings className="h-3 w-3" /> Work Orders
              </span>
              <span className="px-2 py-0.5 bg-slate-800 rounded text-slate-200">
                {relationships.work_orders}
              </span>
            </Link>
            <li className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
              <span className="flex items-center gap-2">
                <FileText className="h-3 w-3" /> Documents Attached
              </span>
              <span className="px-2 py-0.5 bg-slate-800 rounded text-slate-200">
                {relationships.documents}
              </span>
            </li>
          </ul>
        </div>

        <div className="rounded border border-slate-800 bg-slate-900 p-5">
          <SectionHeader title="Quick Actions" icon={<CheckCircle2 className="h-4 w-4" />} />
          <div className="grid grid-cols-2 gap-3 mt-2">
            <button className="p-3 text-left rounded bg-slate-950 border border-slate-800 hover:bg-slate-800 transition-colors text-xs font-mono text-slate-300">
              Generate AI Executive Report
            </button>
            <Link
              to="/maintenance"
              className="p-3 text-left rounded bg-slate-950 border border-slate-800 hover:bg-slate-800 transition-colors text-xs font-mono text-slate-300"
            >
              View Maintenance History
            </Link>
            <button className="p-3 text-left rounded bg-slate-950 border border-slate-800 hover:bg-slate-800 transition-colors text-xs font-mono text-slate-300">
              Create Support Ticket
            </button>
            <Link
              to="/finance"
              className="p-3 text-left rounded bg-slate-950 border border-slate-800 hover:bg-slate-800 transition-colors text-xs font-mono text-slate-300"
            >
              Export Financial Ledger
            </Link>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
