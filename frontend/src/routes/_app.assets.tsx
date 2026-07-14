import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { assetService } from "@/services/assets.service";
import { useState, useMemo } from "react";
import { Search, Filter, Activity, AlertTriangle, PieChart, Package, Download } from "lucide-react";
import { ColumnDef } from "@tanstack/react-table";

import { PageLayout, PageHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { motion } from "framer-motion";

export const Route = createFileRoute("/_app/assets")({
  component: AssetsPage,
});

function AssetsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const { data: kpisData } = useQuery<any>({
    queryKey: ["assetKpis"],
    queryFn: () => assetService.getKPIs(),
  });

  const { data: registry, isLoading } = useQuery<any>({
    queryKey: ["assets", searchQuery],
    queryFn: () => assetService.getAssets(searchQuery, 1, 50),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        accessorKey: "code",
        header: "Asset Code",
        cell: (info) => (
          <Link
            to="/assets/$assetId"
            params={{ assetId: info.row.original.id }}
            className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
          >
            {info.getValue()}
          </Link>
        ),
      },
      {
        accessorKey: "name",
        header: "Name",
        cell: (info) => (
          <span className="font-medium text-slate-800 dark:text-slate-200">{info.getValue()}</span>
        ),
      },
      {
        accessorKey: "category",
        header: "Category",
        cell: (info) => (
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            {info.getValue() || "Uncategorized"}
          </span>
        ),
      },
      {
        accessorKey: "department",
        header: "Department",
        cell: (info) => info.getValue() || "Unassigned",
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (info) => <StatusBadge status={info.getValue()} type="general" />,
      },
      {
        accessorKey: "health",
        header: "Health",
        cell: (info) => {
          const val = info.getValue() as number;
          return (
            <div className="flex items-center gap-2">
              <span
                className={`font-bold ${val < 50 ? "text-red-500" : val < 75 ? "text-amber-500" : "text-emerald-500"}`}
              >
                {val.toFixed(1)}
              </span>
              <div className="h-1.5 w-16 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${val < 50 ? "bg-red-500" : val < 75 ? "bg-amber-500" : "bg-emerald-500"}`}
                  style={{ width: `${val}%` }}
                ></div>
              </div>
            </div>
          );
        },
      },
      {
        accessorKey: "purchaseValue",
        header: "Value",
        cell: (info) =>
          info.getValue() ? (
            <span className="font-mono text-slate-600 dark:text-slate-300">
              ${(info.getValue() as number).toLocaleString()}
            </span>
          ) : (
            "—"
          ),
      },
    ],
    [],
  );

  return (
    <PageLayout>
      {/* 1. OVERVIEW & HEADER */}
      <PageHeader
        title="Asset Registry"
        description="Enterprise Single Source of Truth"
        actions={
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 text-xs font-semibold transition-colors shadow-sm"
          >
            <Download className="h-4 w-4" />
            Export Full Registry
          </motion.button>
        }
      />

      {/* 2. KPIs */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, staggerChildren: 0.1 }}
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        {kpisData?.kpis?.map((kpi: any, idx: number) => {
          let Icon = Package;
          if (kpi.label.toLowerCase().includes("health")) Icon = Activity;
          if (kpi.label.toLowerCase().includes("value")) Icon = PieChart;
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
                deltaPositive={kpi.deltaPositive}
                icon={<Icon className="h-4.5 w-4.5" />}
              />
            </motion.div>
          );
        })}
      </motion.div>

      {/* 3. ENTERPRISE SEARCH & FILTERS */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex gap-4 mt-8"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by Asset Name, ID, QR Code, Department, Serial Number..."
            className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-3 pl-11 pr-4 text-sm font-sans text-slate-900 dark:text-slate-100 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <button className="flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-5 py-3 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm">
          <Filter className="h-4 w-4" />
          Filters
        </button>
      </motion.div>

      {/* 4. ASSET REGISTRY */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="h-[600px] mt-6"
      >
        <DataTable
          columns={columns}
          data={registry?.items || []}
          title="Global Assets"
          exportable
          selectable
          virtualized
          isLoading={isLoading}
          filename="aegon_assets"
          onSelectionAction={(action, selectedRows) => {
            console.log(`Action ${action} on ${selectedRows.length} rows`);
          }}
        />
      </motion.div>
    </PageLayout>
  );
}
