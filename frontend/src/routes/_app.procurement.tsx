import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { ShoppingCart, ShieldAlert, FileSignature, Download, BadgeCheck } from "lucide-react";
import { useMemo } from "react";
import { ColumnDef } from "@tanstack/react-table";

import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { AIInsightCard } from "@/components/copilot/AIInsightCard";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { SkeletonCard, SkeletonKpis } from "@/components/common/skeleton";

export const Route = createFileRoute("/_app/procurement")({
  component: ProcurementPage,
});

function ProcurementPage() {
  const { data, isLoading } = useQuery<any>({
    queryKey: ["procurementOverview"],
    queryFn: () => apiClient.get("/procurement/"),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        accessorKey: "po_number",
        header: "PO Number",
        cell: (info) => <span className="text-indigo-400 font-semibold">{info.getValue()}</span>,
      },
      {
        accessorKey: "vendor_name",
        header: "Vendor",
        cell: (info) => <span className="font-medium text-slate-200">{info.getValue()}</span>,
      },
      {
        accessorKey: "amount",
        header: "Amount",
        cell: (info) => (
          <span className="font-bold text-emerald-400">
            ${(info.getValue() as number).toLocaleString()}
          </span>
        ),
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (info) => <StatusBadge status={info.getValue()} type="general" />,
      },
      {
        accessorKey: "delivery_risk",
        header: "Delivery Risk",
        cell: (info) => <StatusBadge status={info.getValue()} type="risk" />,
      },
    ],
    [],
  );

  return (
    <PageLayout>
      <PageHeader
        title="Procurement Operations"
        description="Vendor Ranking & Spend Analytics"
        actions={
          <button className="flex items-center gap-2 rounded bg-slate-800 px-3 py-1.5 text-xs font-mono text-slate-200 hover:bg-slate-700 transition-colors">
            <Download className="h-3.5 w-3.5" />
            Export Orders
          </button>
        }
      />

      {/* KPIs */}
      {isLoading ? (
        <SkeletonKpis count={4} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {data?.kpis?.map((kpi: any, idx: number) => {
            let Icon = ShoppingCart;
            if (kpi.label.toLowerCase().includes("vendor")) Icon = BadgeCheck;
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
      )}

      {/* AI Insights */}
      <div>
        <SectionHeader
          title="Vendor & Risk Intelligence"
          icon={<ShieldAlert className="h-5 w-5 text-indigo-400" />}
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
                domain="Procurement Control"
                priority={insight.priority?.toLowerCase() || "high"}
              />
            ))}
          </div>
        )}
      </div>

      {/* PO Table */}
      <div className="h-[500px]">
        <DataTable
          columns={columns}
          data={data?.active_purchase_orders || []}
          title="Active Purchase Orders"
          icon={<FileSignature className="h-4 w-4 text-emerald-400" />}
          exportable
          searchable
          isLoading={isLoading}
          filename="aegon_procurement_pos"
        />
      </div>
    </PageLayout>
  );
}
