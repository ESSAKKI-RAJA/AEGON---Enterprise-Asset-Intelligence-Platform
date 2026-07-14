import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { DollarSign, Wallet, TrendingUp, Download, PieChart } from "lucide-react";
import { useMemo } from "react";
import { ColumnDef } from "@tanstack/react-table";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { SkeletonCard, SkeletonKpis } from "@/components/common/skeleton";

export const Route = createFileRoute("/_app/finance")({
  component: FinancePage,
});

function FinancePage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ["financeOverview"],
    queryFn: () => apiClient.get("/finance/"),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        accessorKey: "department_name",
        header: "Department",
        cell: (info) => <span className="text-slate-200 font-medium">{info.getValue()}</span>,
      },
      {
        accessorKey: "allocated_budget",
        header: "Allocated",
        cell: (info) => (
          <span className="text-slate-300">${(info.getValue() as number).toLocaleString()}</span>
        ),
      },
      {
        accessorKey: "spent_ytd",
        header: "Spent YTD",
        cell: (info) => (
          <span className="text-slate-400">${(info.getValue() as number).toLocaleString()}</span>
        ),
      },
      {
        accessorKey: "variance",
        header: "Variance",
        cell: (info) => {
          const val = info.getValue() as number;
          return (
            <span className={`font-bold ${val < 0 ? "text-red-400" : "text-emerald-400"}`}>
              {val < 0 ? "-" : "+"}${Math.abs(val).toLocaleString()}
            </span>
          );
        },
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (info) => <StatusBadge status={info.getValue()} type="risk" />,
      },
    ],
    [],
  );

  return (
    <PageLayout>
      <PageHeader
        title="Financial Intelligence"
        description="CAPEX/OPEX Tracking & Asset Depreciation"
        actions={
          <button className="flex items-center gap-2 rounded bg-slate-800 px-3 py-1.5 text-xs font-mono text-slate-200 hover:bg-slate-700 transition-colors">
            <Download className="h-3.5 w-3.5" />
            Export Finance
          </button>
        }
      />

      {/* KPIs */}
      {isLoading ? (
        <SkeletonKpis count={4} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {data?.kpis?.map((kpi: any, idx: number) => {
            let Icon = DollarSign;
            if (kpi.label.toLowerCase().includes("budget")) Icon = Wallet;
            if (kpi.label.toLowerCase().includes("depreciation")) Icon = PieChart;

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
        <SectionHeader
          title="Financial & Budget Insights"
          icon={<TrendingUp className="h-5 w-5 text-indigo-400" />}
        />
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
                domain="Finance & Planning"
                priority={insight.priority?.toLowerCase() || "high"}
              />
            ))}
          </div>
        )}
      </div>

      {/* Budgets Table */}
      <div className="h-[500px]">
        <DataTable
          columns={columns}
          data={data?.department_budgets || []}
          title="Department Budgets (YTD)"
          icon={<Wallet className="h-4 w-4 text-indigo-400" />}
          exportable
          searchable
          isLoading={isLoading}
          filename="aegon_finance_budgets"
        />
      </div>
    </PageLayout>
  );
}
