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
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ViewInspectionResult, ViewPanelState, DefectFinding } from "@/types/vision";

interface ViewInspectorProps {
  panel: ViewPanelState;
  isAnalyzing: boolean;
  onFileSelect: (file: File) => void;
  onAnalyze: () => void;
  compact?: boolean;
}

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

function BoundingBoxOverlay({ findings }: { findings: DefectFinding[] }) {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {findings
        .filter((f) => f.bounding_box)
        .map((finding, i) => {
          const bb = finding.bounding_box!;
          return (
            <div
              key={i}
              className="absolute border-2 rounded-sm group"
              style={{
                left: `${bb.x * 100}%`,
                top: `${bb.y * 100}%`,
                width: `${bb.width * 100}%`,
                height: `${bb.height * 100}%`,
                borderColor: SEVERITY_COLORS[finding.severity],
                boxShadow: `0 0 8px ${SEVERITY_COLORS[finding.severity]}50`,
              }}
            >
              <div
                className="absolute -top-5 left-0 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded whitespace-nowrap"
                style={{ backgroundColor: SEVERITY_COLORS[finding.severity] }}
              >
                {finding.defect_type} {Math.round(finding.confidence * 100)}%
              </div>
            </div>
          );
        })}
    </div>
  );
}

function ScanAnimation() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Horizontal scan line */}
      <motion.div
        className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-teal-400 to-transparent opacity-80"
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
      />
      {/* Corner brackets */}
      {[
        "top-2 left-2 border-t-2 border-l-2",
        "top-2 right-2 border-t-2 border-r-2",
        "bottom-2 left-2 border-b-2 border-l-2",
        "bottom-2 right-2 border-b-2 border-r-2",
      ].map((cls, i) => (
        <div
          key={i}
          className={cn("absolute w-4 h-4 border-teal-400 opacity-90", cls)}
        />
      ))}
      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage:
            "linear-gradient(rgba(20,184,166,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(20,184,166,0.5) 1px, transparent 1px)",
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
}: ViewInspectorProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);

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
                onClick={() => setShowBoxes((v) => !v)}
                className="p-1 rounded text-slate-500 hover:text-teal-400 transition-colors"
                title={showBoxes ? "Hide bounding boxes" : "Show bounding boxes"}
              >
                <Eye className="h-3 w-3" />
              </button>
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
          <div
            className={cn(
              "absolute inset-0 flex flex-col items-center justify-center gap-2 cursor-pointer transition-all",
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
              {panel.status === "complete" && result && showBoxes && (
                <BoundingBoxOverlay findings={result.findings} />
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
