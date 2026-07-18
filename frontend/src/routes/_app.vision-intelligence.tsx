import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ScanEye,
  RefreshCw,
  Cpu,
  Activity,
  ShieldAlert,
  BarChart2,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  Play,
  RotateCcw,
  Globe,
  Search,
  Database,
  Layers,
  Server,
  Wifi,
  Wrench,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { ViewInspector } from "@/components/vision/ViewInspector";
import { FindingsPanel } from "@/components/vision/FindingsPanel";
import { DigitalTwinWidget } from "@/components/vision/DigitalTwinWidget";
import { ExecutiveSummaryPanel } from "@/components/vision/ExecutiveSummaryPanel";
import { InspectionHistory } from "@/components/vision/InspectionHistory";
import { SeverityAnalytics } from "@/components/vision/SeverityAnalytics";
import {
  useUploadView,
  useGenerate360,
  useGenerateReport,
  useInspectionHistory,
  useVisionStatistics,
  useCreateMaintenanceTicket,
} from "@/services/visionService";
import { assetService } from "@/services/assets.service";
import type {
  ViewPanelState,
  VisionViewType,
  DigitalTwinState,
  CompositeAnalysis,
  ExecutiveSummary,
  DefectFinding,
  InspectionHistoryItem,
} from "@/types/vision";

export const Route = createFileRoute("/_app/vision-intelligence")({
  component: VisionIntelligencePage,
});

const VIEW_PANELS: { key: VisionViewType; label: string; description: string }[] = [
  { key: "top", label: "TOP VIEW", description: "Scratches · Paint · Wear · Rust" },
  { key: "bottom", label: "BOTTOM VIEW", description: "Cracks · Leakage · Seals" },
  { key: "front", label: "FRONT VIEW", description: "Panel · Display · Labels" },
  { key: "rear", label: "REAR VIEW", description: "Cables · Ports · Connectors" },
  { key: "left", label: "LEFT VIEW", description: "Impact · Paint · Edge" },
  { key: "right", label: "RIGHT VIEW", description: "Impact · Paint · Edge" },
];

function AnimatedKpi({
  label,
  value,
  unit = "",
  icon: Icon,
  color = "text-slate-200",
  subtext,
}: any) {
  return (
    <div className="rounded-xl border border-slate-700/40 bg-slate-900/60 backdrop-blur-sm p-4 flex flex-col gap-1">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-4 w-4" />
        <span className="text-[10px] font-mono uppercase tracking-widest">{label}</span>
      </div>
      <div className={cn("text-2xl font-bold font-mono", color)}>
        {value}
        {unit && <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>}
      </div>
      {subtext && <p className="text-[10px] font-mono text-slate-500">{subtext}</p>}
    </div>
  );
}

function AssetSelector({ onSelect }: { onSelect: (asset: any) => void }) {
  const [query, setQuery] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["assets", query],
    queryFn: () => assetService.getAssets(query, 1, 10),
  });

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8">
      <ScanEye className="h-16 w-16 text-indigo-500/50 mb-6" />
      <h2 className="text-2xl font-mono font-bold text-slate-200 mb-2">
        Select Asset for Inspection
      </h2>
      <p className="text-slate-500 font-mono text-sm mb-8 text-center max-w-md">
        Connect Vision Intelligence to a registered asset to enable Digital Twin synchronization and
        automated maintenance workflows.
      </p>

      <div className="w-full max-w-xl bg-slate-900/80 border border-slate-700 p-2 rounded-xl">
        <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-800 mb-2">
          <Search className="h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search Asset Registry..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-sm font-mono text-slate-300 placeholder:text-slate-600"
          />
        </div>

        <div className="space-y-1 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
          {isLoading ? (
            <div className="p-4 text-center text-slate-500 font-mono text-xs animate-pulse">
              Loading registry...
            </div>
          ) : data?.items?.length === 0 ? (
            <div className="p-4 text-center text-slate-500 font-mono text-xs">No assets found</div>
          ) : (
            data?.items?.map((asset: any) => (
              <button
                key={asset.id}
                onClick={() => onSelect(asset)}
                className="w-full text-left flex items-center justify-between p-3 rounded-lg hover:bg-indigo-900/30 border border-transparent hover:border-indigo-500/30 transition-all group"
              >
                <div>
                  <div className="text-sm font-bold text-slate-300 group-hover:text-indigo-400 font-mono">
                    {asset.name}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono mt-1">
                    SN: {asset.serial_number || "N/A"} • {asset.category}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-mono text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded">
                    Ready
                  </div>
                  <div className="text-[9px] font-mono text-slate-600 mt-1">{asset.department}</div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function VisionIntelligencePage() {
  const queryClient = useQueryClient();
  const [selectedAsset, setSelectedAsset] = useState<any | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  const sessionId = useRef(`session-${Date.now()}`);
  const [panels, setPanels] = useState<Record<VisionViewType, ViewPanelState>>(
    () =>
      Object.fromEntries(
        VIEW_PANELS.map(({ key, label }) => [key, { viewType: key, label, status: "idle" }]),
      ) as any,
  );
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwinState>({
    asset_name: "Asset",
    health_score: 100,
    risk_score: 0,
    temperature_celsius: 25,
    pressure_psi: 14.7,
    rotation_rpm: 0,
    maintenance_status: "Up to Date",
    inspection_progress_pct: 0,
    views_completed: [],
    historical_health_trend: [],
    historical_risk_trend: [],
    last_updated: new Date().toISOString(),
  });
  const [composite, setComposite] = useState<CompositeAnalysis | undefined>();
  const [execSummary, setExecSummary] = useState<ExecutiveSummary | undefined>();
  const [activeTab, setActiveTab] = useState<"findings" | "analytics" | "summary" | "history">(
    "findings",
  );
  const [historyItems, setHistoryItems] = useState<InspectionHistoryItem[]>([]);

  const uploadMutation = useUploadView((data) => {
    const vt = data.view_result.view_type;
    setPanels((prev) => ({
      ...prev,
      [vt]: { ...prev[vt], status: "complete", result: data.view_result },
    }));
    if (data.digital_twin) setDigitalTwin(data.digital_twin);
  });

  const generate360Mutation = useGenerate360((data) => {
    setComposite(data.composite);
    setExecSummary(data.executive_summary);
    if (data.digital_twin) setDigitalTwin(data.digital_twin);
    setActiveTab("analytics");
    toast.success("360° composite analysis complete!");
  });

  const reportMutation = useGenerateReport();
  const ticketMutation = useCreateMaintenanceTicket((data) => {
    toast.success(`Maintenance Ticket ${data.ticket_id} created successfully!`, {
      icon: <Wrench className="h-4 w-4 text-emerald-400" />,
    });
  });

  if (!selectedAsset) {
    return (
      <PageLayout>
        <AssetSelector onSelect={setSelectedAsset} />
      </PageLayout>
    );
  }

  const handleFileSelectAndAnalyze = (viewType: VisionViewType, file: File) => {
    setPanels((p) => ({
      ...p,
      [viewType]: { ...p[viewType], status: "analyzing", previewUrl: URL.createObjectURL(file) },
    }));
    uploadMutation.mutate({
      viewType,
      file,
      sessionId: sessionId.current,
      assetName: selectedAsset.name,
      operator: "Admin",
    });
  };

  const handleAnalyze = (viewType: VisionViewType) => {
    setPanels((p) => ({ ...p, [viewType]: { ...p[viewType], status: "analyzing" } }));
    uploadMutation.mutate({
      viewType,
      file: undefined,
      sessionId: sessionId.current,
      assetName: selectedAsset.name,
      operator: "Admin",
    });
  };

  const handleRunAllMock = () => {
    VIEW_PANELS.forEach(({ key }, i) => {
      setTimeout(() => {
        setPanels((p) => ({ ...p, [key]: { ...p[key], status: "analyzing" } }));
        uploadMutation.mutate({
          viewType: key,
          sessionId: sessionId.current,
          assetName: selectedAsset.name,
          operator: "Admin",
        });
      }, i * 800);
    });
  };

  const allFindings = Object.values(panels)
    .filter((p) => p.result)
    .flatMap((p) => p.result!.findings);
  const completedViews = Object.values(panels).filter((p) => p.status === "complete").length;
  const canGenerate360 = completedViews >= 2;

  // Use the last view result for global metrics if available
  const lastResult = Object.values(panels)
    .reverse()
    .find((p) => p.result)?.result;
  const modelVersion = lastResult?.model_version || "AEGON-Vision-V6.5-Enterprise";
  const gpuStatus = lastResult?.gpu_status || "A100 - Standby";
  const latency = lastResult?.processing_time_ms || 0;

  return (
    <PageLayout>
      {/* SECTION 1: Enterprise Header */}
      <div className="flex flex-col md:flex-row items-center justify-between bg-slate-900 border border-slate-800 p-3 rounded-lg mb-6 gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Server className="h-4 w-4 text-teal-400" />
            <div>
              <div className="text-[10px] font-mono text-slate-500 uppercase">Inference Engine</div>
              <div className="text-xs font-mono font-bold text-slate-200">{modelVersion}</div>
            </div>
          </div>
          <div className="w-px h-6 bg-slate-700" />
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-indigo-400" />
            <div>
              <div className="text-[10px] font-mono text-slate-500 uppercase">GPU Status</div>
              <div className="text-xs font-mono font-bold text-indigo-300">{gpuStatus}</div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Wifi className="h-4 w-4 text-emerald-400" />
            <div className="text-[10px] font-mono font-bold text-emerald-400 uppercase">
              Connected
            </div>
          </div>
          <div className="text-xs font-mono text-slate-400 border border-slate-700 px-2 py-1 rounded bg-slate-950">
            {currentTime}
          </div>
        </div>
      </div>

      <PageHeader
        title="Enterprise Vision Intelligence"
        description={`Inspecting: ${selectedAsset.name} (${selectedAsset.serial_number || "N/A"})`}
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={handleRunAllMock}
              disabled={uploadMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-[10px] font-bold"
            >
              <Play className="h-3 w-3" />
              RUN AUTOMATED PIPELINE
            </button>
          </div>
        }
      />

      {/* SECTION 2: Executive KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <AnimatedKpi
          label="Health Score"
          value={composite?.overall_health_score ?? digitalTwin.health_score}
          unit="%"
          icon={Activity}
          color="text-teal-400"
        />
        <AnimatedKpi
          label="Risk Score"
          value={composite?.risk_score ?? digitalTwin.risk_score}
          unit="%"
          icon={ShieldAlert}
          color="text-amber-400"
        />
        <AnimatedKpi
          label="Latency"
          value={latency.toFixed(0)}
          unit="ms"
          icon={Zap}
          color="text-indigo-400"
        />
        <AnimatedKpi
          label="Queue"
          value={lastResult?.queue_position || 0}
          icon={Layers}
          color="text-blue-400"
        />
        <AnimatedKpi
          label="Total Defects"
          value={allFindings.length}
          icon={AlertTriangle}
          color="text-amber-400"
        />
        <AnimatedKpi
          label="Critical"
          value={allFindings.filter((f) => f.severity === "critical").length}
          icon={AlertTriangle}
          color="text-red-400"
        />
        <AnimatedKpi
          label="Est. Cost"
          value={
            composite ? `$${(composite.maintenance_cost_estimate_usd / 1000).toFixed(0)}K` : "—"
          }
          icon={DollarSign}
          color="text-teal-400"
        />
        <AnimatedKpi
          label="RUL"
          value={composite ? composite.remaining_useful_life_years : "—"}
          unit={composite ? "yrs" : ""}
          icon={Clock}
          color="text-purple-400"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_300px] mt-6">
        {/* SECTION 6: Multi View Inspection */}
        <div className="space-y-4">
          <SectionHeader
            title="Multi-View Inspection Matrix"
            icon={<ScanEye className="h-4 w-4 text-teal-400" />}
          />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {VIEW_PANELS.map(({ key, label, description }) => (
              <div key={key} className="space-y-1">
                <ViewInspector
                  panel={{ ...panels[key], label }}
                  isAnalyzing={uploadMutation.isPending && panels[key].status === "analyzing"}
                  onFileSelect={(f) => handleFileSelectAndAnalyze(key, f)}
                  onAnalyze={() => handleAnalyze(key)}
                  showHeatmapGlobal={activeTab === "analytics"}
                />
              </div>
            ))}
            <div className="space-y-1">
              <div className="relative rounded border border-indigo-500/30 bg-slate-900 overflow-hidden flex flex-col min-h-[200px]">
                <div className="p-2 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
                  <span className="text-[10px] font-mono font-bold text-slate-300">
                    360° SYNTHESIS
                  </span>
                </div>
                <div className="flex-1 flex flex-col items-center justify-center p-4">
                  {!composite ? (
                    <div className="text-center">
                      <Globe
                        className={cn(
                          "h-12 w-12 mx-auto mb-2",
                          canGenerate360 ? "text-indigo-400 animate-pulse" : "text-slate-700",
                        )}
                      />
                      <button
                        onClick={() => generate360Mutation.mutate({ sessionId: sessionId.current })}
                        disabled={!canGenerate360 || generate360Mutation.isPending}
                        className="px-3 py-1.5 rounded bg-indigo-600/20 text-indigo-400 font-mono text-[10px] font-bold disabled:opacity-30 mt-2 hover:bg-indigo-600/30 transition-colors"
                      >
                        GENERATE COMPOSITE
                      </button>
                    </div>
                  ) : (
                    <div className="text-center w-full">
                      <div className="text-3xl font-mono text-emerald-400 font-bold">
                        {composite.overall_health_score.toFixed(0)}
                      </div>
                      <div className="text-[9px] font-mono text-slate-500">FINAL HEALTH</div>
                      <div className="text-xs font-mono text-amber-400 mt-2">
                        Risk: {composite.risk_score.toFixed(0)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 8: Digital Twin */}
        <div>
          <SectionHeader
            title="Live Digital Twin"
            icon={<Database className="h-4 w-4 text-amber-400" />}
          />
          <div className="rounded border border-slate-700 bg-slate-900 p-4 h-full min-h-[400px]">
            <DigitalTwinWidget twin={digitalTwin} />
          </div>
        </div>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900 mt-6 overflow-hidden">
        <div className="flex border-b border-slate-800 overflow-x-auto custom-scrollbar">
          {[
            { id: "findings", label: `AI Findings (${allFindings.length})` },
            { id: "analytics", label: "Severity Analytics" },
            { id: "summary", label: "Executive Summary" },
            { id: "history", label: "History" },
          ].map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={cn(
                "px-5 py-3 text-[10px] font-mono font-bold border-b-2 transition-colors uppercase whitespace-nowrap",
                activeTab === id
                  ? "border-teal-400 text-teal-400 bg-teal-950/10"
                  : "border-transparent text-slate-500 hover:text-slate-300",
              )}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="p-5 min-h-[300px]">
          {/* SECTION 9: AI Findings */}
          {activeTab === "findings" && (
            <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
              {Object.entries(panels)
                .filter(([, p]) => p.result?.findings.length)
                .map(([k, p]) => (
                  <div key={k}>
                    <p className="text-[10px] font-mono font-bold text-slate-500 uppercase mb-2">
                      {p.label}
                    </p>
                    <FindingsPanel
                      findings={p.result!.findings}
                      onCreateTicket={(f) =>
                        ticketMutation.mutate({
                          session_id: sessionId.current,
                          finding_id: f.finding_id,
                          defect_type: f.defect_type,
                          priority: "within_7_days",
                          estimated_cost: f.estimated_repair_cost,
                          asset_id: selectedAsset.id,
                        })
                      }
                      isCreatingTicket={ticketMutation.isPending}
                    />
                  </div>
                ))}
              {allFindings.length === 0 && (
                <div className="col-span-full py-12 text-center text-slate-500 font-mono text-sm">
                  No findings yet. Run an inspection to populate.
                </div>
              )}
            </div>
          )}
          {/* SECTION 10 & 11: Severity Analytics */}
          {activeTab === "analytics" && (
            <SeverityAnalytics findings={allFindings} digitalTwin={digitalTwin} />
          )}
          {/* SECTION 12: Executive Summary */}
          {activeTab === "summary" && execSummary && composite && (
            <ExecutiveSummaryPanel
              summary={execSummary}
              composite={composite}
              onGenerateReport={() => reportMutation.mutate({ sessionId: sessionId.current })}
              isGeneratingReport={reportMutation.isPending}
            />
          )}
          {activeTab === "summary" && (!execSummary || !composite) && (
            <div className="py-12 text-center text-slate-500 font-mono text-sm">
              Generate 360° Composite to view Executive Summary.
            </div>
          )}
          {/* SECTION 14: Inspection History */}
          {activeTab === "history" && <InspectionHistory items={historyItems} />}
        </div>
      </div>
    </PageLayout>
  );
}
