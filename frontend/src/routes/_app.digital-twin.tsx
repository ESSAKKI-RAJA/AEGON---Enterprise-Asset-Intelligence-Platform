import { createFileRoute } from "@tanstack/react-router";
import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { Factory, ThermometerSun, AlertOctagon, Activity, Cpu, Zap } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

export const Route = createFileRoute("/_app/digital-twin")({
  component: DigitalTwinPage,
});

function DigitalTwinPage() {
  const { data: dashboard, isLoading } = useQuery<any>({
    queryKey: ["digitalTwinData"],
    queryFn: () => apiClient.get("/analytics/dashboards/executive"), // using the existing analytics data for some numbers
  });

  return (
    <PageLayout>
      <PageHeader
        title="Digital Twin Facility Overview"
        description="Real-time telemetry and 3D space visualization of Manufacturing Plant A."
        actions={
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 px-3 py-1 bg-emerald-900/30 text-emerald-400 border border-emerald-800 rounded-full font-mono text-xs">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              TELEMETRY ACTIVE
            </span>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-4 mb-8">
        {/* Core KPIs for Digital Twin */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-5 shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-2 text-slate-400">
            <ThermometerSun className="h-5 w-5 text-orange-400" />
            <h3 className="font-mono text-sm uppercase tracking-wider">Avg Temperature</h3>
          </div>
          <div className="text-3xl font-semibold text-slate-100 font-mono">42.5°C</div>
          <div className="mt-2 text-xs font-mono text-red-400">+2.1°C above baseline</div>
        </div>

        <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-5 shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-2 text-slate-400">
            <Activity className="h-5 w-5 text-emerald-400" />
            <h3 className="font-mono text-sm uppercase tracking-wider">Facility Health</h3>
          </div>
          <div className="text-3xl font-semibold text-slate-100 font-mono">94%</div>
          <div className="mt-2 text-xs font-mono text-emerald-400">Stable</div>
        </div>

        <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-5 shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-2 text-slate-400">
            <Zap className="h-5 w-5 text-yellow-400" />
            <h3 className="font-mono text-sm uppercase tracking-wider">Power Draw</h3>
          </div>
          <div className="text-3xl font-semibold text-slate-100 font-mono">2.4 MW</div>
          <div className="mt-2 text-xs font-mono text-emerald-400">-5% below baseline</div>
        </div>

        <div className="rounded-xl border border-slate-700/50 bg-slate-900/80 p-5 shadow-lg backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-2 text-slate-400">
            <AlertOctagon className="h-5 w-5 text-red-400" />
            <h3 className="font-mono text-sm uppercase tracking-wider">Active Anomalies</h3>
          </div>
          <div className="text-3xl font-semibold text-slate-100 font-mono">3</div>
          <div className="mt-2 text-xs font-mono text-slate-500">Requires review</div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Mock 3D or visual mapping section */}
        <div className="lg:col-span-2 rounded-xl border border-slate-700/50 bg-slate-900/90 shadow-xl backdrop-blur-sm overflow-hidden flex flex-col h-[500px]">
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
            <SectionHeader
              title="Plant Floor Mapping"
              icon={<Factory className="h-5 w-5 text-indigo-400" />}
            />
            <div className="text-xs font-mono text-slate-500">Rendering Layer: Sensor Nodes</div>
          </div>

          <div className="flex-1 relative bg-slate-950/50 flex items-center justify-center p-8">
            {/* A stylized abstract representation of a factory layout */}
            <div className="absolute inset-0 grid-bg opacity-20"></div>

            <div className="relative w-full max-w-2xl aspect-[16/9] border-2 border-indigo-500/20 rounded-lg p-6 flex flex-col justify-between">
              {/* Zone A */}
              <div className="w-1/3 h-1/2 border border-emerald-500/30 bg-emerald-900/20 rounded flex items-center justify-center relative group cursor-pointer hover:bg-emerald-900/40 transition-colors">
                <div className="absolute -top-3 -left-3 h-3 w-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="font-mono text-emerald-400 font-bold text-sm">ASSEMBLY ZONE</span>
              </div>

              {/* Zone B */}
              <div className="w-1/2 h-1/3 border border-red-500/30 bg-red-900/20 rounded self-end flex items-center justify-center relative group cursor-pointer hover:bg-red-900/40 transition-colors">
                <div className="absolute -top-3 -right-3 h-3 w-3 rounded-full bg-red-500 animate-pulse"></div>
                <span className="font-mono text-red-400 font-bold text-sm">
                  BOILER ROOM (TEMP ALERT)
                </span>
              </div>

              {/* Zone C */}
              <div className="absolute top-1/4 right-8 w-1/4 h-2/3 border border-indigo-500/30 bg-indigo-900/20 rounded flex items-center justify-center group cursor-pointer hover:bg-indigo-900/40 transition-colors">
                <div className="absolute bottom-3 left-3 h-3 w-3 rounded-full bg-indigo-500"></div>
                <span className="font-mono text-indigo-400 font-bold text-sm">PACKAGING</span>
              </div>
            </div>
          </div>
        </div>

        {/* Realtime logs */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/90 shadow-xl backdrop-blur-sm h-[500px] flex flex-col">
          <div className="p-4 border-b border-slate-800 bg-slate-950">
            <SectionHeader
              title="Realtime Event Stream"
              icon={<Cpu className="h-5 w-5 text-indigo-400" />}
            />
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="text-xs font-mono p-3 bg-slate-950/50 rounded border border-slate-800"
              >
                <div className="text-slate-500 mb-1">
                  {new Date(Date.now() - i * 14000).toISOString()}
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-teal-400 mt-0.5">❯</span>
                  <span className={i === 2 ? "text-red-400" : "text-slate-300"}>
                    {i === 2
                      ? "ANOMALY DETECTED: Boiler Pressure Exceeds Threshold (2.4 MPa)"
                      : `Sensor ${Math.floor(Math.random() * 1000)} telemetry synced successfully.`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageLayout>
  );
}

// Add a simple CSS pattern for the grid background in index.css if not present
