/**
 * ViewInspector — Single-view upload and inspection panel.
 * Features: drag-and-drop, preview, scan animation, bounding box overlay, zoom/pan.
 */
import { useRef, useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  Camera,
  MonitorPlay,
  Smartphone,
  Layers,
  ActivitySquare
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ViewInspectionResult, ViewPanelState, DefectFinding } from "@/types/vision";

interface ViewInspectorProps {
  panel: ViewPanelState;
  isAnalyzing: boolean;
  onFileSelect: (file: File) => void;
  onAnalyze: () => void;
  compact?: boolean;
  showHeatmapGlobal?: boolean;
}

const SOURCES = [
  { id: "upload", label: "Upload", icon: Upload },
  { id: "usb", label: "USB Cam", icon: Camera },
  { id: "rtsp", label: "IP/RTSP", icon: MonitorPlay },
  { id: "mobile", label: "Mobile", icon: Smartphone },
];

const SEVERITY_COLORS = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#f59e0b",
  low: "#14b8a6",
  none: "#64748b",
};

const SEVERITY_BG = {
  critical: "border-red-500/50 bg-red-950/20",
  high: "border-orange-500/50 bg-orange-950/20",
  medium: "border-amber-500/50 bg-amber-950/20",
  low: "border-teal-500/50 bg-teal-950/20",
  none: "border-slate-700 bg-slate-900/50",
};

function BoundingBoxOverlay({ findings, showHeatmap }: { findings: DefectFinding[], showHeatmap: boolean }) {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {findings
        .filter((f) => f.bounding_box)
        .map((finding, i) => {
          const bb = finding.bounding_box!;
          const sevColor = SEVERITY_COLORS[finding.severity];
          return (
            <div key={`box-${i}`}>
              {showHeatmap ? (
                <div
                  className="absolute rounded-full opacity-60 mix-blend-screen transition-opacity duration-500"
                  style={{
                    left: `${(bb.x - bb.width/2) * 100}%`,
                    top: `${(bb.y - bb.height/2) * 100}%`,
                    width: `${bb.width * 200}%`,
                    height: `${bb.height * 200}%`,
                    background: `radial-gradient(circle, ${sevColor}ff 0%, ${sevColor}00 70%)`,
                    filter: "blur(8px)",
                  }}
                />
              ) : (
                <div
                  className="absolute border-2 rounded-sm group transition-all duration-300"
                  style={{
                    left: `${bb.x * 100}%`,
                    top: `${bb.y * 100}%`,
                    width: `${bb.width * 100}%`,
                    height: `${bb.height * 100}%`,
                    borderColor: sevColor,
                    boxShadow: `0 0 8px ${sevColor}50`,
                  }}
                >
                  {finding.mask_points && finding.mask_points.length > 0 && (
                    <svg className="absolute inset-0 w-full h-full overflow-visible opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
                       <polygon
                          points={finding.mask_points.map(p => `${p[0]*100},${p[1]*100}`).join(" ")}
                          fill={sevColor}
                       />
                    </svg>
                  )}
                  <div
                    className="absolute -top-5 left-0 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded whitespace-nowrap"
                    style={{ backgroundColor: sevColor }}
                  >
                    {finding.defect_type} {Math.round(finding.confidence * 100)}%
                  </div>
                </div>
              )}
            </div>
          );
        })}
    </div>
  );
}

function ScanAnimation() {
  const [stage, setStage] = useState(0);
  const stages = [
    "ACQUIRING IMAGE...",
    "NORMALIZING...",
    "OBJECT DETECTION...",
    "SEGMENTATION...",
    "SEVERITY CLASSIFICATION...",
    "UPDATING DIGITAL TWIN..."
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setStage(s => (s + 1) % stages.length);
    }, 600);
    return () => clearInterval(timer);
  }, [stages.length]);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-10 flex flex-col items-center justify-center bg-slate-950/40 backdrop-blur-[2px]">
      <motion.div
        className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-teal-400 to-transparent opacity-80 shadow-[0_0_8px_rgba(45,212,191,0.8)]"
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 2.0, repeat: Infinity, ease: "linear" }}
      />
      
      <div className="bg-slate-900/80 border border-teal-500/30 px-4 py-2 rounded-lg flex items-center gap-3">
         <Loader2 className="h-4 w-4 text-teal-400 animate-spin" />
         <p className="text-[10px] font-mono text-teal-400 font-bold">{stages[stage]}</p>
      </div>

      <div
        className="absolute inset-0 opacity-10 mix-blend-overlay"
        style={{
          backgroundImage: "linear-gradient(rgba(20,184,166,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(20,184,166,0.5) 1px, transparent 1px)",
          backgroundSize: "20px 20px",
        }}
      />
    </div>
  );
}

export function ViewInspector({
  panel,
  isAnalyzing,
  onFileSelect,
  onAnalyze,
  compact = false,
  showHeatmapGlobal = false,
}: ViewInspectorProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(showHeatmapGlobal);
  const [source, setSource] = useState<string>("upload");

  useEffect(() => {
    setShowHeatmap(showHeatmapGlobal);
  }, [showHeatmapGlobal]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        onFileSelect(file);
      }
    },
    [onFileSelect],
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  const result = panel.result;
  const hasFindings = (result?.findings?.length ?? 0) > 0;
  const criticalCount = result?.critical_count ?? 0;

  const statusConfig = {
    idle: { color: "text-slate-500", border: "border-slate-700/50" },
    uploading: { color: "text-blue-400", border: "border-blue-500/40" },
    analyzing: { color: "text-teal-400", border: "border-teal-500/50" },
    complete: {
      color: criticalCount > 0 ? "text-red-400" : "text-emerald-400",
      border: criticalCount > 0 ? "border-red-500/40" : "border-emerald-500/30",
    },
    failed: { color: "text-red-400", border: "border-red-500/40" },
  };

  const cfg = statusConfig[panel.status];

  return (
    <motion.div
      layout
      className={cn(
        "relative rounded-xl border bg-slate-900/60 backdrop-blur-sm overflow-hidden flex flex-col",
        cfg.border,
        compact ? "min-h-[180px]" : "min-h-[220px]",
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-800/70 bg-slate-950/50 shrink-0">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "h-1.5 w-1.5 rounded-full",
              panel.status === "complete" && criticalCount === 0 && "bg-emerald-500",
              panel.status === "complete" && criticalCount > 0 && "bg-red-500 animate-pulse",
              panel.status === "analyzing" && "bg-teal-400 animate-pulse",
              panel.status === "idle" && "bg-slate-600",
              panel.status === "uploading" && "bg-blue-400 animate-pulse",
              panel.status === "failed" && "bg-red-500",
            )}
          />
          <span className="text-[10px] font-mono font-bold text-slate-300 uppercase tracking-widest">
            {panel.label}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {result && (
            <>
              <button
                onClick={() => setShowHeatmap((v) => !v)}
                className={cn("p-1 rounded transition-colors", showHeatmap ? "text-indigo-400 bg-indigo-950/30" : "text-slate-500 hover:text-indigo-400")}
                title="Toggle Heatmap"
              >
                <Layers className="h-3 w-3" />
              </button>
              <button
                onClick={() => setShowBoxes((v) => !v)}
                className={cn("p-1 rounded transition-colors", showBoxes ? "text-teal-400 bg-teal-950/30" : "text-slate-500 hover:text-teal-400")}
                title="Toggle Bounding Boxes"
              >
                <Eye className="h-3 w-3" />
              </button>
              <div className="w-px h-3 bg-slate-700 mx-0.5" />
              <button
                onClick={() => setZoom((z) => Math.min(z + 0.3, 3))}
                className="p-1 rounded text-slate-500 hover:text-teal-400 transition-colors"
              >
                <ZoomIn className="h-3 w-3" />
              </button>
              <button
                onClick={() => setZoom((z) => Math.max(z - 0.3, 1))}
                className="p-1 rounded text-slate-500 hover:text-teal-400 transition-colors"
              >
                <ZoomOut className="h-3 w-3" />
              </button>
              <button
                onClick={() => setZoom(1)}
                className="p-1 rounded text-slate-500 hover:text-teal-400 transition-colors"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main body */}
      <div className="flex-1 relative">
        {panel.status === "idle" && !panel.previewUrl && (
          <div className="absolute inset-0 flex flex-col">
            {/* Source Selector Header */}
            <div className="flex items-center justify-between px-2 py-1.5 bg-slate-900 border-b border-slate-800">
              {SOURCES.map(s => {
                const Icon = s.icon;
                return (
                  <button
                    key={s.id}
                    onClick={() => setSource(s.id)}
                    className={cn(
                      "flex items-center gap-1 px-1.5 py-1 rounded text-[9px] font-mono transition-colors",
                      source === s.id ? "bg-indigo-600/20 text-indigo-400" : "text-slate-500 hover:text-slate-300 hover:bg-slate-800"
                    )}
                  >
                    <Icon className="h-2.5 w-2.5" />
                    <span className="hidden sm:inline">{s.label}</span>
                  </button>
                )
              })}
            </div>

            {source === "upload" ? (
              <div
                className={cn(
                  "flex-1 flex flex-col items-center justify-center gap-2 cursor-pointer transition-all",
                  isDragging && "bg-teal-950/30 border-teal-500/50",
                )}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="p-2 rounded-lg border border-slate-700 bg-slate-800/50">
                  <Upload className="h-4 w-4 text-slate-400" />
                </div>
                <p className="text-[10px] font-mono text-slate-500 text-center px-2">
                  Drop image or click
                </p>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center bg-slate-950">
                {/* Mock Camera Feed */}
                <ActivitySquare className="h-6 w-6 text-indigo-500/50 animate-pulse mb-2" />
                <p className="text-[9px] font-mono text-indigo-400">CONNECTING TO {source.toUpperCase()} STREAM...</p>
                <button
                   onClick={() => onAnalyze()}
                   className="mt-4 px-3 py-1 text-[10px] font-mono font-bold border border-indigo-500/30 text-indigo-400 rounded hover:bg-indigo-950/50"
                >
                   CAPTURE & ANALYZE
                </button>
              </div>
            )}
          </div>
        )}

        {/* Image preview + overlays */}
        {panel.previewUrl && (
          <div className="absolute inset-0 overflow-hidden">
            <div
              className="absolute inset-0 transition-transform duration-300"
              style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}
            >
              <img
                src={panel.previewUrl}
                alt={`${panel.label} view`}
                className="w-full h-full object-cover"
              />
              {panel.status === "complete" && result && (
                <BoundingBoxOverlay findings={result.findings} showHeatmap={showHeatmap} />
              )}
            </div>
            {panel.status === "analyzing" && <ScanAnimation />}
          </div>
        )}

        {/* No image but has result (mock mode) */}
        {!panel.previewUrl && panel.status === "analyzing" && (
          <div className="absolute inset-0 bg-slate-950/80">
            <ScanAnimation />
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
              <Loader2 className="h-5 w-5 text-teal-400 animate-spin" />
              <p className="text-[9px] font-mono text-teal-400">AI SCANNING...</p>
            </div>
          </div>
        )}

        {!panel.previewUrl && panel.status === "complete" && (
          <div
            className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/60 cursor-pointer"
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            {criticalCount > 0 ? (
              <AlertTriangle className="h-6 w-6 text-red-400 mb-1" />
            ) : (
              <CheckCircle2 className="h-6 w-6 text-emerald-400 mb-1" />
            )}
            <p className="text-[10px] font-mono text-slate-400">
              {result?.defect_count ?? 0} findings
            </p>
          </div>
        )}
      </div>

      {/* Footer stats */}
      {panel.status === "complete" && result && (
        <div className="shrink-0 border-t border-slate-800/60 bg-slate-950/60 px-3 py-1.5 flex items-center justify-between">
          <span className="text-[9px] font-mono text-slate-500">
            Health: <span className={cn("font-bold", result.view_health_score > 75 ? "text-emerald-400" : result.view_health_score > 50 ? "text-amber-400" : "text-red-400")}>{result.view_health_score.toFixed(0)}%</span>
          </span>
          <span className="text-[9px] font-mono text-slate-500">
            {result.defect_count} defects
            {criticalCount > 0 && <span className="text-red-400 ml-1">({criticalCount} critical)</span>}
          </span>
          <span className="text-[9px] font-mono text-slate-600">
            {result.processing_time_ms.toFixed(0)}ms
          </span>
        </div>
      )}

      {/* Analyze button for idle with preview */}
      {panel.previewUrl && panel.status === "idle" && (
        <div className="shrink-0 p-2 border-t border-slate-800/60">
          <button
            onClick={onAnalyze}
            className="w-full py-1.5 text-[10px] font-mono font-bold text-teal-400 border border-teal-500/30 bg-teal-950/20 hover:bg-teal-950/40 rounded transition-colors"
          >
            RUN ANALYSIS
          </button>
        </div>
      )}
    </motion.div>
  );
}
