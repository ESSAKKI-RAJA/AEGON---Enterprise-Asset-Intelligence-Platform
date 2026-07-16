import { createFileRoute } from "@tanstack/react-router";
import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  ScanEye,
  RefreshCw,
  Cpu,
  Activity,
  ShieldAlert,
  BarChart2,
  Clock,
  DollarSign,
  Zap,
  AlertTriangle,
  CheckCircle2,
  Play,
  RotateCcw,
  Globe,
  ArrowUpDown,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageLayout, PageHeader, SectionHeader } from "@/components/layout/PageLayout";
import { ViewInspector } from "@/components/vision/ViewInspector";
import { FindingsPanel } from "@/components/vision/FindingsPanel";
import { DigitalTwinWidget } from "@/components/vision/DigitalTwinWidget";
import { ExecutiveSummaryPanel } from "@/components/vision/ExecutiveSummaryPanel";
import { InspectionHistory } from "@/components/vision/InspectionHistory";
import { useUploadView, useGenerate360, useGenerateReport, useInspectionHistory } from "@/services/visionService";
import type {
  ViewPanelState,
  VisionViewType,
  DigitalTwinState,
  CompositeAnalysis,
  ExecutiveSummary,
  DefectFinding,
  InspectionHistoryItem,
} from "@/types/vision";
import { useQueryClient } from "@tanstack/react-query";

export const Route = createFileRoute("/_app/vision-intelligence")({
  component: VisionIntelligencePage,
});

// ---------------------------------------------------------------------------
// View panel definitions
// ---------------------------------------------------------------------------

const VIEW_PANELS: { key: VisionViewType; label: string; description: string }[] = [
  { key: "top", label: "TOP VIEW", description: "Scratches · Paint · Wear · Rust · Heat" },
  { key: "left", label: "LEFT VIEW", description: "Impact · Paint · Edge · Alignment" },
  { key: "right", label: "RIGHT VIEW", description: "Impact · Paint · Edge · Alignment" },
  { key: "front", label: "FRONT VIEW", description: "Panel · Display · Labels · Cracks" },
  { key: "rear", label: "REAR VIEW", description: "Cables · Ports · Connectors · Heat" },
  { key: "bottom", label: "BOTTOM VIEW", description: "Cracks · Leakage · Seals · Welds" },
];

// ---------------------------------------------------------------------------
// Animated KPI counter
// ---------------------------------------------------------------------------

function AnimatedKpi({
  label,
  value,
  unit = "",
  icon: Icon,
  color = "text-slate-200",
  subtext,
}: {
  label: string;
  value: string | number;
  unit?: string;
  icon: any;
  color?: string;
  subtext?: string;
}) {
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

// ---------------------------------------------------------------------------
// 360° view placeholder panel
// ---------------------------------------------------------------------------

function CompositeViewPanel({
  composite,
  onGenerate,
  isGenerating,
  canGenerate,
}: {
  composite?: CompositeAnalysis;
  onGenerate: () => void;
  isGenerating: boolean;
  canGenerate: boolean;
}) {
  return (
    <div className="relative rounded-xl border border-indigo-500/30 bg-slate-900/60 backdrop-blur-sm overflow-hidden flex flex-col min-h-[220px]">
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-800/70 bg-slate-950/50 shrink-0">
        <div className="flex items-center gap-2">
          <div className={cn("h-1.5 w-1.5 rounded-full", composite ? "bg-indigo-400" : "bg-slate-600")} />
          <span className="text-[10px] font-mono font-bold text-slate-300 uppercase tracking-widest">
            360° MODEL
          </span>
        </div>
        {!composite && canGenerate && (
          <span className="text-[9px] font-mono text-teal-400 animate-pulse">READY</span>
        )}
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-4">
        {composite ? (
          <div className="space-y-3 w-full">
            <div className="text-center">
              <div
                className={cn(
                  "text-3xl font-bold font-mono",
                  composite.overall_health_score >= 75 ? "text-emerald-400"
                  : composite.overall_health_score >= 50 ? "text-amber-400"
                  : "text-red-400",
                )}
              >
                {composite.overall_health_score.toFixed(0)}
                <span className="text-base text-slate-500">/100</span>
              </div>
              <p className="text-[9px] font-mono text-slate-500 mt-0.5">OVERALL HEALTH</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-2 text-center">
                <div className="text-sm font-bold font-mono text-orange-400">{composite.risk_score.toFixed(0)}%</div>
                <div className="text-[9px] font-mono text-slate-500">RISK</div>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-2 text-center">
                <div className="text-sm font-bold font-mono text-blue-400">{composite.remaining_useful_life_years}y</div>
                <div className="text-[9px] font-mono text-slate-500">RUL</div>
              </div>
            </div>
            <div className={cn(
              "px-2 py-1.5 rounded-lg border text-center",
              composite.critical_defects > 0
                ? "border-red-500/30 bg-red-950/20 text-red-400"
                : "border-emerald-500/30 bg-emerald-950/20 text-emerald-400",
            )}>
              <p className="text-[10px] font-mono font-bold">{composite.deployment_status}</p>
            </div>
          </div>
        ) : (
          <div className="text-center space-y-3">
            {/* Animated 3D-style globe */}
            <div className="relative mx-auto h-16 w-16">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0"
              >
                <Globe className="h-16 w-16 text-indigo-500/40" />
              </motion.div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-6 w-6 rounded-full border-2 border-indigo-400/30 flex items-center justify-center">
                  <div className="h-2 w-2 rounded-full bg-indigo-400/50 animate-pulse" />
                </div>
              </div>
            </div>
            <p className="text-[10px] font-mono text-slate-500 text-center px-2">
              {canGenerate ? "All views ready" : "Upload views to activate"}
            </p>
            {canGenerate && (
              <button
                onClick={onGenerate}
                disabled={isGenerating}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold text-[10px] hover:bg-indigo-600/30 transition-colors disabled:opacity-50"
              >
                {isGenerating ? <RefreshCw className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3" />}
                {isGenerating ? "Fusing..." : "GENERATE 360°"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------

function VisionIntelligencePage() {
  const queryClient = useQueryClient();
  const sessionId = useRef(`session-${Date.now()}-${Math.random().toString(36).slice(2)}`);

  const [panels, setPanels] = useState<Record<VisionViewType, ViewPanelState>>(
    Object.fromEntries(
      VIEW_PANELS.map(({ key, label }) => [
        key,
        { viewType: key, label, status: "idle" },
      ]),
    ) as Record<VisionViewType, ViewPanelState>,
  );

  const [digitalTwin, setDigitalTwin] = useState<DigitalTwinState>({
    asset_name: "Enterprise Asset",
    health_score: 100,
    risk_score: 0,
    temperature_celsius: 25,
    maintenance_status: "Up to Date",
    inspection_progress_pct: 0,
    views_completed: [],
    last_updated: new Date().toISOString(),
  });

  const [composite, setComposite] = useState<CompositeAnalysis | undefined>();
  const [execSummary, setExecSummary] = useState<ExecutiveSummary | undefined>();
  const [activeTab, setActiveTab] = useState<"findings" | "history" | "summary">("findings");
  const [historyItems, setHistoryItems] = useState<InspectionHistoryItem[]>([]);
  const [assetName, setAssetName] = useState("Enterprise Asset");
  const [isEditingName, setIsEditingName] = useState(false);

  // Collect all findings across all views
  const allFindings: DefectFinding[] = Object.values(panels)
    .filter((p) => p.result)
    .flatMap((p) => p.result!.findings);

  const completedViews = Object.values(panels).filter((p) => p.status === "complete").length;
  const totalViews = VIEW_PANELS.length;
  const canGenerate360 = completedViews >= 2;

  // ---- Mutations ----

  const uploadMutation = useUploadView((data) => {
    const vt = data.view_result.view_type;
    setPanels((prev) => ({
      ...prev,
      [vt]: {
        ...prev[vt],
        status: "complete",
        result: data.view_result,
      },
    }));
    if (data.digital_twin) setDigitalTwin(data.digital_twin);
    toast.success(`${vt.toUpperCase()} view analysis complete — ${data.view_result.defect_count} findings`);
  });

  const generate360Mutation = useGenerate360((data) => {
    setComposite(data.composite);
    setExecSummary(data.executive_summary);
    if (data.digital_twin) setDigitalTwin(data.digital_twin);
    setActiveTab("summary");

    // Add to local history
    const histItem: InspectionHistoryItem = {
      session_id: sessionId.current,
      asset_name: assetName,
      operator: "System",
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      views_inspected: data.composite.views_inspected,
      total_defects: data.composite.total_defects,
      critical_defects: data.composite.critical_defects,
      health_score: data.composite.overall_health_score,
      risk_score: data.composite.risk_score,
      maintenance_priority: data.composite.maintenance_priority,
      status: "complete",
    };
    setHistoryItems((prev) => [histItem, ...prev]);

    toast.success("360° composite analysis complete!");
  });

  const reportMutation = useGenerateReport();

  // ---- Handlers ----

  const handleFileSelect = useCallback(
    (viewType: VisionViewType, file: File) => {
      const url = URL.createObjectURL(file);
      setPanels((prev) => ({
        ...prev,
        [viewType]: { ...prev[viewType], status: "idle", previewUrl: url, result: undefined },
      }));
    },
    [],
  );

  const handleAnalyze = useCallback(
    (viewType: VisionViewType) => {
      const panel = panels[viewType];
      setPanels((prev) => ({ ...prev, [viewType]: { ...prev[viewType], status: "analyzing" } }));

      const file = panel.previewUrl
        ? (() => {
            // Convert blob url back - just send null for now
            return undefined;
          })()
        : undefined;

      uploadMutation.mutate({
        viewType,
        file: undefined,
        sessionId: sessionId.current,
        assetName,
        operator: "System",
      });
    },
    [panels, assetName, uploadMutation],
  );

  // Auto-analyze when file is selected
  const handleFileSelectAndAnalyze = useCallback(
    (viewType: VisionViewType, file: File) => {
      const url = URL.createObjectURL(file);
      setPanels((prev) => ({
        ...prev,
        [viewType]: { ...prev[viewType], status: "analyzing", previewUrl: url, result: undefined },
      }));
      uploadMutation.mutate({
        viewType,
        file,
        sessionId: sessionId.current,
        assetName,
        operator: "System",
      });
    },
    [assetName, uploadMutation],
  );

  const handleGenerate360 = () => {
    generate360Mutation.mutate({ sessionId: sessionId.current });
  };

  const handleGenerateReport = () => {
    reportMutation.mutate({ sessionId: sessionId.current });
    toast.success("Enterprise report queued — downloading shortly...");
  };

  const handleReset = () => {
    sessionId.current = `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setPanels(
      Object.fromEntries(
        VIEW_PANELS.map(({ key, label }) => [key, { viewType: key, label, status: "idle" }]),
      ) as Record<VisionViewType, ViewPanelState>,
    );
    setDigitalTwin({
      asset_name: assetName,
      health_score: 100,
      risk_score: 0,
      temperature_celsius: 25,
      maintenance_status: "Up to Date",
      inspection_progress_pct: 0,
      views_completed: [],
      last_updated: new Date().toISOString(),
    });
    setComposite(undefined);
    setExecSummary(undefined);
    setActiveTab("findings");
    toast.info("New inspection session started");
  };

  const handleRunAllMock = () => {
    VIEW_PANELS.forEach(({ key }, i) => {
      setTimeout(() => {
        setPanels((prev) => ({ ...prev, [key]: { ...prev[key], status: "analyzing" } }));
        uploadMutation.mutate({
          viewType: key,
          sessionId: sessionId.current,
          assetName,
          operator: "System",
        });
      }, i * 600);
    });
    toast.info("Running AI inspection on all 6 views...");
  };

  // KPI values
  const healthScore = composite?.overall_health_score ?? digitalTwin.health_score;
  const riskScore = composite?.risk_score ?? digitalTwin.risk_score;
  const totalDefects = allFindings.length;
  const criticalCount = allFindings.filter((f) => f.severity === "critical").length;
  const inspectionProgress = completedViews > 0 ? Math.round((completedViews / totalViews) * 100) : 0;
  const avgConfidence =
    allFindings.length > 0
      ? Math.round((allFindings.reduce((s, f) => s + f.confidence, 0) / allFindings.length) * 100)
      : 0;

  return (
    <PageLayout>
      <PageHeader
        title="Enterprise Vision Intelligence"
        description="Multi-angle AI inspection system — Computer Vision · Defect Detection · Asset Health Analysis"
        actions={
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 border border-teal-500/30 bg-teal-950/20 px-3 py-1.5 rounded-full">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500" />
              </span>
              <span className="font-mono text-xs text-teal-400">CV Engine Ready</span>
            </div>
            <button
              onClick={handleRunAllMock}
              disabled={uploadMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold transition-colors disabled:opacity-50"
            >
              <Play className="h-3.5 w-3.5" />
              Run Full Inspection
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600 text-slate-400 hover:text-slate-300 font-mono text-xs transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              New Session
            </button>
          </div>
        }
      />

      {/* Asset name editor */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Inspecting:</span>
        {isEditingName ? (
          <input
            autoFocus
            value={assetName}
            onChange={(e) => setAssetName(e.target.value)}
            onBlur={() => setIsEditingName(false)}
            onKeyDown={(e) => e.key === "Enter" && setIsEditingName(false)}
            className="px-2 py-0.5 text-sm font-mono bg-slate-900 border border-teal-500/50 rounded text-slate-200 focus:outline-none"
          />
        ) : (
          <button
            onClick={() => setIsEditingName(true)}
            className="text-sm font-mono font-semibold text-slate-200 hover:text-teal-400 transition-colors"
          >
            {assetName} ✎
          </button>
        )}
      </div>

      {/* ── KPI Bar ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <AnimatedKpi
          label="Health Score"
          value={healthScore.toFixed(0)}
          unit="%"
          icon={Activity}
          color={healthScore >= 75 ? "text-emerald-400" : healthScore >= 50 ? "text-amber-400" : "text-red-400"}
        />
        <AnimatedKpi
          label="Risk Score"
          value={riskScore.toFixed(0)}
          unit="%"
          icon={ShieldAlert}
          color={riskScore <= 20 ? "text-emerald-400" : riskScore <= 50 ? "text-amber-400" : "text-red-400"}
        />
        <AnimatedKpi
          label="AI Confidence"
          value={avgConfidence || "—"}
          unit={avgConfidence ? "%" : ""}
          icon={Cpu}
          color="text-indigo-400"
        />
        <AnimatedKpi
          label="Progress"
          value={inspectionProgress}
          unit="%"
          icon={BarChart2}
          color="text-blue-400"
          subtext={`${completedViews}/${totalViews} views`}
        />
        <AnimatedKpi
          label="Total Defects"
          value={totalDefects}
          icon={AlertTriangle}
          color={totalDefects === 0 ? "text-emerald-400" : "text-amber-400"}
        />
        <AnimatedKpi
          label="Critical Issues"
          value={criticalCount}
          icon={AlertTriangle}
          color={criticalCount === 0 ? "text-emerald-400" : "text-red-400"}
        />
        <AnimatedKpi
          label="Est. Repair Cost"
          value={composite ? `$${(composite.maintenance_cost_estimate_usd / 1000).toFixed(0)}K` : "—"}
          icon={DollarSign}
          color="text-teal-400"
        />
        <AnimatedKpi
          label="RUL"
          value={composite ? `${composite.remaining_useful_life_years}` : "—"}
          unit={composite ? "yrs" : ""}
          icon={Clock}
          color="text-purple-400"
        />
      </div>

      {/* ── Main Layout: View Grid + Sidebar ── */}
      <div className="grid gap-6 xl:grid-cols-[1fr_300px]">
        {/* Left: View panels grid */}
        <div className="space-y-4">
          <SectionHeader
            title="Multi-View Inspection"
            icon={<ScanEye className="h-4 w-4 text-teal-400" />}
            actions={
              <span className="text-[10px] font-mono text-slate-500">
                {completedViews}/{totalViews} views complete
              </span>
            }
          />

          {/* 3×2 grid for 6 side views + 360 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {VIEW_PANELS.map(({ key, label, description }) => (
              <div key={key} className="space-y-1">
                <ViewInspector
                  panel={{ ...panels[key], label }}
                  isAnalyzing={
                    uploadMutation.isPending && panels[key].status === "analyzing"
                  }
                  onFileSelect={(file) => handleFileSelectAndAnalyze(key, file)}
                  onAnalyze={() => handleAnalyze(key)}
                />
                <p className="text-[9px] font-mono text-slate-600 px-1 truncate">{description}</p>
              </div>
            ))}
            {/* 360° composite panel */}
            <div className="space-y-1">
              <CompositeViewPanel
                composite={composite}
                onGenerate={handleGenerate360}
                isGenerating={generate360Mutation.isPending}
                canGenerate={canGenerate360}
              />
              <p className="text-[9px] font-mono text-slate-600 px-1">
                Health · Risk · RUL · Executive Summary
              </p>
            </div>
          </div>
        </div>

        {/* Right: Digital Twin */}
        <div>
          <SectionHeader
            title="Asset Digital Twin"
            icon={<Zap className="h-4 w-4 text-amber-400" />}
          />
          <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 backdrop-blur-sm p-4">
            <DigitalTwinWidget twin={digitalTwin} />
          </div>
        </div>
      </div>

      {/* ── Tabbed Panel: Findings / Summary / History ── */}
      <div className="rounded-xl border border-slate-700/50 bg-slate-900/60 backdrop-blur-sm overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-slate-800">
          {[
            { id: "findings", label: `AI Findings (${allFindings.length})`, icon: AlertTriangle },
            { id: "summary", label: "Executive Summary", icon: CheckCircle2, disabled: !execSummary },
            { id: "history", label: "Inspection History", icon: Clock },
          ].map(({ id, label, icon: Icon, disabled }) => (
            <button
              key={id}
              onClick={() => !disabled && setActiveTab(id as any)}
              disabled={disabled}
              className={cn(
                "flex items-center gap-2 px-5 py-3 text-xs font-mono font-semibold border-b-2 transition-colors",
                activeTab === id
                  ? "border-teal-400 text-teal-400 bg-teal-950/10"
                  : "border-transparent text-slate-500 hover:text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed",
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>

        <div className="p-5">
          <AnimatePresence mode="wait">
            {activeTab === "findings" && (
              <motion.div
                key="findings"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                {allFindings.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                    <ScanEye className="h-10 w-10 mb-3 opacity-40" />
                    <p className="text-sm font-mono">No findings yet</p>
                    <p className="text-xs font-mono text-slate-600 mt-1">
                      Upload images or click "Run Full Inspection" to start
                    </p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {Object.entries(panels)
                      .filter(([, p]) => p.result && p.result.findings.length > 0)
                      .map(([key, panel]) => (
                        <div key={key}>
                          <p className="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-2">
                            {panel.label}
                          </p>
                          <FindingsPanel findings={panel.result!.findings} viewLabel={panel.label} />
                        </div>
                      ))}
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === "summary" && execSummary && composite && (
              <motion.div
                key="summary"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <ExecutiveSummaryPanel
                  summary={execSummary}
                  composite={composite}
                  onGenerateReport={handleGenerateReport}
                  isGeneratingReport={reportMutation.isPending}
                />
              </motion.div>
            )}

            {activeTab === "history" && (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <InspectionHistory items={historyItems} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </PageLayout>
  );
}
