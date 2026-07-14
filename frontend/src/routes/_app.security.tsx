import { createFileRoute } from "@tanstack/react-router";
import {
  Shield,
  ShieldAlert,
  Key,
  Activity,
  Users,
  Server,
  Lock,
  FileCheck,
  Globe,
  Database,
  Network,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  User,
} from "lucide-react";
import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";

export const Route = createFileRoute("/_app/security")({
  component: SecurityDashboard,
});

function SecurityDashboard() {
  const securityData = {
    score: 94,
    complianceStatus: "Compliant",
    failedLogins: 12,
    activeSessions: 145,
    auditEventsLast24h: 342,
    apiHealth: "100%",
    suspiciousActivities: [
      {
        id: 1,
        type: "Failed Login Spike",
        user: "unknown",
        ip: "192.168.1.45",
        time: "10 mins ago",
        severity: "high",
      },
      {
        id: 2,
        type: "Permission Escalation Attempt",
        user: "jdoe@aegon.dev",
        ip: "10.0.0.12",
        time: "2 hours ago",
        severity: "medium",
      },
    ],
    recentAudits: [
      { id: 101, action: "UPDATE", entity: "UserRole", by: "admin@aegon.dev", time: "1 hour ago" },
      {
        id: 102,
        action: "DELETE",
        entity: "Asset: PMP-8902",
        by: "mmanager@aegon.dev",
        time: "3 hours ago",
      },
      {
        id: 103,
        action: "CREATE",
        entity: "APIKey (Production)",
        by: "admin@aegon.dev",
        time: "5 hours ago",
      },
      {
        id: 104,
        action: "GENERATE",
        entity: "AI Forecast (EOQ)",
        by: "supply_chain@aegon.dev",
        time: "6 hours ago",
      },
      { id: 105, action: "LOGIN", entity: "Session", by: "jdoe@aegon.dev", time: "8 hours ago" },
      {
        id: 106,
        action: "EXPORT",
        entity: "Financial Report",
        by: "cfo@aegon.dev",
        time: "10 hours ago",
      },
    ],
  };

  const complianceFrameworks = [
    { name: "ISO 27001", status: "certified", date: "Valid until 2027" },
    { name: "SOC 2 Type II", status: "certified", date: "Valid until 2027" },
    { name: "GDPR", status: "compliant", date: "Ongoing" },
    { name: "NIST CSF", status: "compliant", date: "Ongoing" },
  ];

  const permissionMatrix = [
    { module: "Executive Dashboard", read: true, write: false, delete: false },
    { module: "Asset Registry", read: true, write: true, delete: true },
    { module: "Digital Twin", read: true, write: true, delete: false },
    { module: "Maintenance", read: true, write: true, delete: true },
    { module: "Inventory", read: true, write: true, delete: false },
    { module: "Procurement", read: true, write: true, delete: false },
    { module: "Finance", read: true, write: false, delete: false },
    { module: "AI Intelligence", read: true, write: true, delete: false },
    { module: "Security & Settings", read: true, write: true, delete: true },
  ];

  return (
    <PageLayout>
      <PageHeader
        title="Enterprise Security Center"
        description="Audit, Governance, Compliance & Access Intelligence"
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

      {/* Security KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <MetricCard
          label="Enterprise Security Score"
          value={`${securityData.score}/100`}
          delta="+2 points"
          deltaTone="positive"
          icon={<Shield className="h-4 w-4" />}
        />
        <MetricCard
          label="Failed Logins (24h)"
          value={securityData.failedLogins.toString()}
          delta="-5 from yesterday"
          deltaTone="positive"
          icon={<Key className="h-4 w-4" />}
        />
        <MetricCard
          label="Active Sessions"
          value={securityData.activeSessions.toString()}
          delta="+12 peak"
          deltaTone="neutral"
          icon={<Users className="h-4 w-4" />}
        />
        <MetricCard
          label="API Health"
          value={securityData.apiHealth}
          delta="100% Uptime"
          deltaTone="positive"
          icon={<Server className="h-4 w-4" />}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3 mb-6">
        {/* Suspicious Activity & Alerts */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg">
          <SectionHeader
            title="Active Threats"
            icon={<ShieldAlert className="h-5 w-5 text-orange-400" />}
          />
          <ul className="space-y-4 flex-1 mt-2">
            {securityData.suspiciousActivities.map((alert) => (
              <li
                key={alert.id}
                className="flex flex-col p-4 bg-slate-950/80 rounded-lg border border-slate-800 shadow-inner"
              >
                <div className="flex justify-between items-center mb-2">
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded tracking-wider ${
                      alert.severity === "high"
                        ? "bg-red-950/50 border border-red-500/20 text-red-400"
                        : "bg-orange-950/50 border border-orange-500/20 text-orange-400"
                    }`}
                  >
                    {alert.severity.toUpperCase()} RISK
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {alert.time}
                  </span>
                </div>
                <div className="text-sm font-semibold font-sans text-slate-200 mt-1">
                  {alert.type}
                </div>
                <div className="text-xs text-slate-400 font-mono mt-2 bg-slate-900 p-2 rounded">
                  Target: {alert.user} <br /> IP: {alert.ip}
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Compliance Card */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg">
          <SectionHeader
            title="Enterprise Compliance"
            icon={<FileCheck className="h-5 w-5 text-teal-400" />}
          />
          <div className="flex-1 mt-2">
            <div className="bg-teal-950/20 border border-teal-500/20 rounded-lg p-3 mb-5 flex items-start gap-3">
              <Shield className="h-5 w-5 text-teal-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-teal-400">Evaluation Mode Active</h4>
                <p className="text-xs text-teal-200/70 mt-1 leading-relaxed">
                  Compliance markers below are simulated for demonstration purposes. AEGON provides
                  native audit trails to satisfy SOC 2 and ISO 27001 requirements.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {complianceFrameworks.map((fw, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-slate-950/50 rounded-lg border border-slate-800"
                >
                  <div className="flex items-center gap-3">
                    <Globe className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-200">{fw.name}</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase tracking-wider text-emerald-400 bg-emerald-400/10 border border-emerald-500/20">
                      {fw.status}
                    </span>
                    <span className="text-[10px] text-slate-500 mt-1">{fw.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Audit Trail */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col shadow-lg h-[400px]">
          <SectionHeader
            title="Audit Immutable Ledger"
            icon={<Activity className="h-5 w-5 text-indigo-400" />}
          />
          <ul className="space-y-3 flex-1 overflow-y-auto custom-scrollbar mt-2 pr-2">
            {securityData.recentAudits.map((audit) => (
              <li
                key={audit.id}
                className="flex justify-between items-center p-3 bg-slate-950/80 rounded-lg border border-slate-800"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                        audit.action === "DELETE"
                          ? "bg-red-500/10 text-red-400 border border-red-500/20"
                          : audit.action === "CREATE"
                            ? "bg-teal-500/10 text-teal-400 border border-teal-500/20"
                            : audit.action === "GENERATE"
                              ? "bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20"
                              : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                      }`}
                    >
                      {audit.action}
                    </span>
                    <span className="text-xs font-semibold text-slate-200 truncate max-w-[150px]">
                      {audit.entity}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {audit.by}
                  </div>
                </div>
                <div className="text-[10px] text-slate-500 font-mono whitespace-nowrap">
                  {audit.time}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Permission Matrix */}
      <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 backdrop-blur-sm p-6 shadow-lg">
        <SectionHeader
          title="Enterprise Permission Matrix"
          icon={<Lock className="h-5 w-5 text-fuchsia-400" />}
        />
        <div className="mt-4 bg-slate-950/50 rounded-lg border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-400 uppercase bg-slate-900 border-b border-slate-800">
                <tr>
                  <th scope="col" className="px-6 py-4 font-semibold tracking-wider">
                    Module
                  </th>
                  <th scope="col" className="px-6 py-4 font-semibold tracking-wider text-center">
                    Read Access
                  </th>
                  <th scope="col" className="px-6 py-4 font-semibold tracking-wider text-center">
                    Write Access
                  </th>
                  <th scope="col" className="px-6 py-4 font-semibold tracking-wider text-center">
                    Delete Access
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {permissionMatrix.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-200 flex items-center gap-3">
                      <Database className="h-4 w-4 text-slate-500" />
                      {row.module}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {row.read ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500 mx-auto" />
                      ) : (
                        <XCircle className="h-5 w-5 text-slate-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {row.write ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500 mx-auto" />
                      ) : (
                        <XCircle className="h-5 w-5 text-slate-600 mx-auto" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {row.delete ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-500 mx-auto" />
                      ) : (
                        <XCircle className="h-5 w-5 text-slate-600 mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
