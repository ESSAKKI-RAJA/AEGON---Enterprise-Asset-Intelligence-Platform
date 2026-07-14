import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import {
  Users,
  Shield,
  Building2,
  Globe,
  Clock,
  DollarSign,
  Calendar,
  Info,
  Server,
  Database,
  Cpu,
  HardDrive,
  Activity,
  Bell,
  Mail,
  FileText,
  AlertTriangle,
  BrainCircuit,
  Settings as SettingsIcon,
  ToggleLeft,
  ToggleRight,
  Eye,
  Edit2,
  Ban,
  ActivitySquare,
} from "lucide-react";
import { useMemo, useState } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "@/components/tables/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/settings")({
  component: SettingsPage,
});

// Mocked System Health Data
const SYSTEM_HEALTH = [
  { name: "Backend API", icon: Server, status: "healthy", value: "99.9% Uptime", detail: "v5.0.0" },
  {
    name: "Database (PostgreSQL)",
    icon: Database,
    status: "healthy",
    value: "12ms Latency",
    detail: "Primary Region",
  },
  {
    name: "Redis Cache",
    icon: Activity,
    status: "healthy",
    value: "3ms Latency",
    detail: "Cache Hit: 98%",
  },
  {
    name: "Worker Queue",
    icon: Cpu,
    status: "healthy",
    value: "24 Jobs/sec",
    detail: "Queue Size: 0",
  },
  {
    name: "ML Inference API",
    icon: BrainCircuit,
    status: "healthy",
    value: "145ms Avg",
    detail: "Model: AEGON-v2",
  },
  {
    name: "Blob Storage",
    icon: HardDrive,
    status: "warning",
    value: "85% Capacity",
    detail: "Auto-scale pending",
  },
];

function ToggleSwitch({ enabled, onChange }: { enabled: boolean; onChange?: () => void }) {
  return (
    <button
      type="button"
      className={`relative inline-flex h-5 w-9 shrink-0 cursor-not-allowed items-center justify-center rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
        enabled ? "bg-indigo-500" : "bg-slate-700"
      }`}
      role="switch"
      aria-checked={enabled}
      onClick={() => {
        toast.info("Notification preferences are locked in Evaluation Mode.");
        if (onChange) onChange();
      }}
    >
      <span
        aria-hidden="true"
        className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
          enabled ? "translate-x-4" : "translate-x-0"
        }`}
      />
    </button>
  );
}

function SettingsPage() {
  const { data: usersData, isLoading } = useQuery<any>({
    queryKey: ["users"],
    queryFn: () => apiClient.get("/settings/users"),
  });

  const columns = useMemo<ColumnDef<any, any>[]>(
    () => [
      {
        id: "name",
        header: "Name",
        accessorFn: (row) => `${row.first_name} ${row.last_name}`,
        cell: (info) => (
          <div className="flex flex-col">
            <span className="font-medium text-slate-200">{info.getValue() as string}</span>
            <span className="text-xs text-slate-500">{info.row.original.email}</span>
          </div>
        ),
      },
      {
        accessorKey: "role",
        header: "Role",
        cell: (info) => {
          const role = info.getValue() as string;
          let roleColor = "text-slate-400 bg-slate-800/50";
          if (role === "Super Administrator" || role === "super_admin")
            roleColor = "text-fuchsia-400 bg-fuchsia-400/10 border border-fuchsia-500/20";
          else if (role === "Administrator" || role === "admin")
            roleColor = "text-indigo-400 bg-indigo-400/10 border border-indigo-500/20";
          else if (role === "Manager" || role === "manager")
            roleColor = "text-teal-400 bg-teal-400/10 border border-teal-500/20";

          const displayRole = role.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());

          return (
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase tracking-wider ${roleColor}`}
            >
              {displayRole}
            </span>
          );
        },
      },
      {
        accessorKey: "department",
        header: "Department",
        cell: (info) => (
          <span className="text-sm text-slate-300">{info.getValue() || "Enterprise"}</span>
        ),
      },
      {
        accessorKey: "is_active",
        header: "Status",
        cell: (info) => (
          <StatusBadge status={info.getValue() ? "active" : "inactive"} type="general" />
        ),
      },
      {
        id: "actions",
        header: "Actions",
        cell: () => (
          <div className="flex items-center gap-2">
            <button
              onClick={() => toast.info("View profile locked in Evaluation Mode.")}
              className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded transition-colors"
              title="View Profile"
            >
              <Eye className="h-4 w-4" />
            </button>
            <button
              onClick={() => toast.info("Edit user locked in Evaluation Mode.")}
              className="p-1.5 text-slate-400 hover:text-teal-400 hover:bg-slate-800 rounded transition-colors"
              title="Edit User"
            >
              <Edit2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => toast.info("Audit logs locked in Evaluation Mode.")}
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition-colors"
              title="Activity Log"
            >
              <ActivitySquare className="h-4 w-4" />
            </button>
            <button
              onClick={() => toast.error("Disable user not permitted in Evaluation Mode.")}
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
              title="Disable User"
            >
              <Ban className="h-4 w-4" />
            </button>
          </div>
        ),
      },
    ],
    [],
  );

  return (
    <PageLayout>
      <PageHeader
        title="Enterprise Control Center"
        description="Global platform configuration, infrastructure health, and administration."
        actions={
          <div className="flex items-center gap-4">
            <div className="font-mono text-xs text-slate-500 flex items-center bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <Shield className="h-4 w-4 mr-2 text-fuchsia-400" />
              Access Level:{" "}
              <span className="text-fuchsia-400 ml-1 font-semibold tracking-wider">
                SUPER ADMIN
              </span>
            </div>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3 mb-6">
        {/* Organization Profile */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
            <div className="bg-indigo-500/20 p-2.5 rounded-lg border border-indigo-500/30">
              <Building2 className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-200 text-lg">Organization Profile</h3>
              <p className="text-xs text-slate-400 font-mono">Enterprise Tenant ID: ORG-9A72B</p>
            </div>
          </div>
          <div className="space-y-4 flex-1">
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <Building2 className="h-4 w-4" /> Company
              </span>
              <span className="font-medium text-slate-200">AEGON Global Operations</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <Globe className="h-4 w-4" /> Headquarters
              </span>
              <span className="font-medium text-slate-200">New York, USA</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <Clock className="h-4 w-4" /> Timezone
              </span>
              <span className="font-medium text-slate-200 font-mono">UTC (GMT+0)</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <DollarSign className="h-4 w-4" /> Base Currency
              </span>
              <span className="font-medium text-slate-200">USD ($)</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <Calendar className="h-4 w-4" /> Fiscal Year
              </span>
              <span className="font-medium text-slate-200">Jan - Dec</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-400 flex items-center gap-2">
                <Info className="h-4 w-4" /> Version
              </span>
              <span className="font-medium text-teal-400 font-mono bg-teal-400/10 px-2 py-0.5 rounded">
                v5.0.0 Evaluation
              </span>
            </div>
          </div>
        </div>

        {/* AI Configuration */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
            <div className="bg-teal-500/20 p-2.5 rounded-lg border border-teal-500/30">
              <BrainCircuit className="h-5 w-5 text-teal-400" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-200 text-lg">AI Configuration</h3>
              <p className="text-xs text-slate-400 font-mono">Global Model Parameters</p>
            </div>
          </div>

          <div className="space-y-5">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                Prediction Horizon
              </label>
              <select
                disabled
                className="w-full bg-slate-950 border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-sm opacity-80 cursor-not-allowed"
              >
                <option>90 Days (Recommended)</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                Primary Forecast Engine
              </label>
              <select
                disabled
                className="w-full bg-slate-950 border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-sm opacity-80 cursor-not-allowed"
              >
                <option>Hybrid (Prophet + XGBoost)</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                Confidence Threshold
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  disabled
                  min="50"
                  max="99"
                  value="85"
                  className="w-full accent-teal-500 opacity-50 cursor-not-allowed"
                />
                <span className="text-sm font-mono text-teal-400 font-semibold bg-teal-400/10 px-2 py-1 rounded">
                  85%
                </span>
              </div>
            </div>
            <div className="flex justify-between items-center pt-2">
              <div>
                <div className="text-sm font-medium text-slate-200">Auto-Retraining</div>
                <div className="text-xs text-slate-500">Nightly model updates</div>
              </div>
              <ToggleSwitch enabled={true} />
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
            <div className="bg-orange-500/20 p-2.5 rounded-lg border border-orange-500/30">
              <Bell className="h-5 w-5 text-orange-400" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-200 text-lg">Alert Routing</h3>
              <p className="text-xs text-slate-400 font-mono">Enterprise Notification Center</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-4 w-4 text-red-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Critical Failure Alerts</div>
                  <div className="text-[10px] text-slate-500">Push & Email immediately</div>
                </div>
              </div>
              <ToggleSwitch enabled={true} />
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Database className="h-4 w-4 text-slate-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Inventory Stockouts</div>
                  <div className="text-[10px] text-slate-500">When stock drops below EOQ</div>
                </div>
              </div>
              <ToggleSwitch enabled={true} />
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <DollarSign className="h-4 w-4 text-emerald-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Budget Variance Warnings</div>
                  <div className="text-[10px] text-slate-500">Deviation &gt; 5%</div>
                </div>
              </div>
              <ToggleSwitch enabled={true} />
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Shield className="h-4 w-4 text-fuchsia-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Security Anomalies</div>
                  <div className="text-[10px] text-slate-500">
                    Failed logins, privilege escalation
                  </div>
                </div>
              </div>
              <ToggleSwitch enabled={true} />
            </div>

            <div className="flex justify-between items-center pt-2 border-t border-slate-800">
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-blue-400" />
                <div>
                  <div className="text-sm font-medium text-slate-200">Executive Daily Digest</div>
                  <div className="text-[10px] text-slate-500">Summary sent at 08:00 UTC</div>
                </div>
              </div>
              <ToggleSwitch enabled={false} />
            </div>
          </div>
        </div>
      </div>

      {/* System Health */}
      <SectionHeader
        title="Infrastructure Health"
        icon={<Activity className="h-5 w-5 text-indigo-400" />}
      />
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {SYSTEM_HEALTH.map((sys, idx) => (
          <div
            key={idx}
            className="bg-slate-900/40 border border-slate-700/50 rounded-xl p-4 flex flex-col justify-between hover:bg-slate-800/60 transition-colors group"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="p-2 bg-slate-800 rounded-lg group-hover:bg-slate-700 transition-colors">
                <sys.icon className="h-4 w-4 text-slate-300" />
              </div>
              <div className="flex items-center">
                <span className="relative flex h-2.5 w-2.5">
                  <span
                    className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${sys.status === "healthy" ? "bg-emerald-400" : "bg-orange-400"}`}
                  ></span>
                  <span
                    className={`relative inline-flex rounded-full h-2.5 w-2.5 ${sys.status === "healthy" ? "bg-emerald-500" : "bg-orange-500"}`}
                  ></span>
                </span>
              </div>
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-200 mb-0.5">{sys.name}</div>
              <div
                className={`text-xs font-mono font-medium ${sys.status === "healthy" ? "text-emerald-400" : "text-orange-400"}`}
              >
                {sys.value}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">{sys.detail}</div>
            </div>
          </div>
        ))}
      </div>

      {/* User Management Table */}
      <div className="h-[500px]">
        <DataTable
          columns={columns}
          data={Array.isArray(usersData) ? usersData : usersData?.data || []}
          title="Directory & Access Control"
          icon={<Users className="h-5 w-5 text-indigo-400" />}
          exportable
          searchable
          isLoading={isLoading}
          filename="aegon_users"
        />
      </div>
    </PageLayout>
  );
}
