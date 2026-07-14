import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import {
  PackageSearch,
  AlertTriangle,
  PackageOpen,
  Download,
  TrendingDown,
  Info,
} from "lucide-react";
import { useMemo } from "react";
import { ColumnDef } from "@tanstack/react-table";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { SkeletonCard, SkeletonKpis } from "@/components/common/skeleton";

export const Route = createFileRoute("/_app/inventory")({
  component: InventoryPage,
});

function InventoryPage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ["inventoryOverview"],
    queryFn: () => apiClient.get("/inventory/"),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        accessorKey: "part_number",
        header: "Part #",
        cell: (info) => <span className="text-indigo-400 font-semibold">{info.getValue()}</span>,
      },
      {
        accessorKey: "name",
        header: "Name",
        cell: (info) => <span className="text-slate-200">{info.getValue()}</span>,
      },
      {
        accessorKey: "current_stock",
        header: "Current Stock",
        cell: (info) => (
          <span className="font-bold">
            {info.getValue()}{" "}
            <span className="text-slate-500 font-normal text-xs">{info.row.original.unit}</span>
          </span>
        ),
      },
      {
        accessorKey: "reorder_point",
        header: "Reorder Point",
      },
      {
        accessorKey: "eoq",
        header: "EOQ",
        cell: (info) => (
          <span className="text-teal-400 font-semibold flex items-center gap-1">
            {info.getValue()}
            <span title="Economic Order Quantity">
              <Info className="h-3 w-3 text-slate-500 cursor-help" />
            </span>
          </span>
        ),
      },
      {
        accessorKey: "stock_risk",
        header: "Risk Level",
        cell: (info) => <StatusBadge status={info.getValue()} type="risk" />,
      },
    ],
    [],
  );

  return (
    <PageLayout>
      <PageHeader
        title="Inventory Intelligence"
        description="Warehouse Operations & AI Stock Optimization"
        actions={
          <button className="flex items-center gap-2 rounded bg-slate-800 px-3 py-1.5 text-xs font-mono text-slate-200 hover:bg-slate-700 transition-colors">
            <Download className="h-3.5 w-3.5" />
            Export Inventory
          </button>
        }
      />

      {/* KPIs */}
      {isLoading ? (
        <SkeletonKpis count={4} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {data?.kpis?.map((kpi: any, idx: number) => {
            let Icon = PackageSearch;
            if (kpi.deltaTone === "critical") Icon = AlertTriangle;

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
          title="AI Optimization Insights"
          icon={<TrendingDown className="h-5 w-5" />}
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
                domain="Inventory Control"
                priority={insight.priority?.toLowerCase() || "high"}
              />
            ))}
          </div>
        )}
      </div>

      {/* Low Stock Inventory Table */}
      <div className="h-[500px]">
        <DataTable
          columns={columns}
          data={data?.low_stock_items || []}
          title="Stock Risk Register"
          icon={<AlertTriangle className="h-4 w-4 text-orange-400" />}
          exportable
          searchable
          isLoading={isLoading}
          filename="aegon_inventory_risk"
        />
      </div>
    </PageLayout>
  );
}
