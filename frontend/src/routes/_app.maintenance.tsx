import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Wrench, AlertTriangle, CheckCircle2, Clock, Activity, Download } from "lucide-react";
import { useMemo } from "react";
import { ColumnDef } from "@tanstack/react-table";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { SkeletonCard, SkeletonKpis } from "@/components/common/skeleton";

export const Route = createFileRoute("/_app/maintenance")({
  component: MaintenancePage,
});

function MaintenancePage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ["maintenanceOverview"],
    queryFn: () => apiClient.get("/maintenance/"),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        accessorKey: "wo_number",
        header: "WO Number",
        cell: (info) => <span className="text-indigo-400 font-semibold">{info.getValue()}</span>,
      },
      {
        accessorKey: "asset_name",
        header: "Asset",
        cell: (info) => (
          <Link
            to="/assets/$assetId"
            params={{ assetId: info.row.original.asset_id }}
            className="font-medium text-slate-200 hover:underline"
          >
            {info.getValue()}
          </Link>
        ),
      },
      {
        accessorKey: "title",
        header: "Title",
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (info) => <StatusBadge status={info.getValue()} type="general" />,
      },
      {
        accessorKey: "priority",
        header: "AI Priority",
        cell: (info) => <StatusBadge status={info.getValue()} type="risk" />,
      },
      {
        accessorKey: "predicted_downtime_hours",
        header: "Est. Downtime",
        cell: (info) => <span className="text-slate-400 font-mono">{info.getValue()}h</span>,
      },
    ],
    [],
  );

  return (
    <PageLayout>
      <PageHeader
        title="Maintenance Operations"
        description="Intelligent Work Orders & AI Priority Scoring"
        actions={
          <button className="flex items-center gap-2 rounded bg-slate-800 px-3 py-1.5 text-xs font-mono text-slate-200 hover:bg-slate-700 transition-colors">
            <Download className="h-3.5 w-3.5" />
            Export Schedule
          </button>
        }
      />

      {/* KPIs */}
      {isLoading ? (
        <SkeletonKpis count={4} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {data?.kpis?.map((kpi: any, idx: number) => {
            let Icon = Wrench;
            if (kpi.label.toLowerCase().includes("overdue")) Icon = AlertTriangle;
            if (kpi.label.toLowerCase().includes("completed")) Icon = CheckCircle2;
            if (kpi.label.toLowerCase().includes("mttr")) Icon = Clock;

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
      )}

      {/* AI Insights */}
      <div>
        <SectionHeader title="Maintenance Intelligence" icon={<Activity className="h-5 w-5" />} />
        {isLoading ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <SkeletonCard lines={4} />
            <SkeletonCard lines={4} />
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {data?.insights?.map((insight: any, idx: number) => (
              <AIInsightCard
                key={idx}
                insight={insight.insight}
                reasoning={insight.reasoning}
                action={insight.action}
                domain="Predictive Maintenance"
                priority={insight.priority?.toLowerCase() || "high"}
              />
            ))}
          </div>
        )}
      </div>

      {/* Work Orders Table */}
      <div className="h-[500px]">
        <DataTable
          columns={columns}
          data={data?.recent_work_orders || []}
          title="Active Work Orders"
          exportable
          searchable
          isLoading={isLoading}
          filename="aegon_maintenance_wos"
        />
      </div>
    </PageLayout>
  );
}
