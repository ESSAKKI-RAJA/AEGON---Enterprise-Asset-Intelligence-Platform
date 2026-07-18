/**
 * ExecutiveSummaryPanel — AI-generated narrative with typing animation.
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FileText, CheckCircle2, AlertTriangle, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ExecutiveSummary, CompositeAnalysis } from "@/types/vision";

interface ExecutiveSummaryPanelProps {
  summary: ExecutiveSummary;
  composite: CompositeAnalysis;
  onGenerateReport?: () => void;
  isGeneratingReport?: boolean;
}

function AnimatedNarrative({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed("");
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        setDone(true);
      }
    }, 10); // fast type speed
    return () => clearInterval(interval);
  }, [text]);

  return (
    <p className="text-sm text-slate-300 leading-relaxed font-mono whitespace-pre-line">
      {displayed}
      {!done && (
        <span className="inline-block w-0.5 h-4 bg-teal-400 animate-pulse align-middle ml-0.5" />
      )}
    </p>
  );
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-400",
  high: "text-orange-400",
  medium: "text-amber-400",
  low: "text-teal-400",
};

export function ExecutiveSummaryPanel({
  summary,
  composite,
  onGenerateReport,
  isGeneratingReport,
}: ExecutiveSummaryPanelProps) {
  return (
    <div className="space-y-5">
      {/* Narrative */}
      <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/10 p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="h-5 w-5 rounded bg-indigo-500/20 flex items-center justify-center">
            <FileText className="h-3 w-3 text-indigo-400" />
          </div>
          <span className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider">
            AI Executive Summary
          </span>
        </div>
        <AnimatedNarrative text={summary.narrative} />
      </div>

      {/* Key Findings */}
      {summary.key_findings.length > 0 && (
        <div>
          <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-2">
            Key Findings
          </h4>
          <div className="space-y-1.5">
            {summary.key_findings.map((finding, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-2"
              >
                <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-indigo-400 shrink-0" />
                <p className="text-xs font-mono text-slate-300">{finding}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Matrix */}
      <div>
        <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-2">
          Severity Matrix
        </h4>
        <div className="grid grid-cols-4 gap-2">
          {Object.entries(summary.risk_matrix).map(([sev, cnt]) => (
            <div
              key={sev}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-2 text-center"
            >
              <div
                className={cn(
                  "text-xl font-bold font-mono",
                  SEVERITY_COLORS[sev] || "text-slate-200",
                )}
              >
                {cnt}
              </div>
              <div className="text-[9px] font-mono text-slate-500 uppercase mt-0.5">{sev}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {summary.recommendations.length > 0 && (
        <div>
          <h4 className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest mb-2">
            Recommended Actions
          </h4>
          <div className="space-y-2">
            {summary.recommendations.map((rec, i) => {
              const isUrgent = rec.toLowerCase().includes("urgent");
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className={cn(
                    "flex items-start gap-2 p-2.5 rounded-lg border",
                    isUrgent
                      ? "border-red-500/30 bg-red-950/20"
                      : "border-slate-700/50 bg-slate-900/40",
                  )}
                >
                  {isUrgent ? (
                    <AlertTriangle className="h-3.5 w-3.5 text-red-400 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="h-3.5 w-3.5 text-teal-400 shrink-0 mt-0.5" />
                  )}
                  <p
                    className={cn(
                      "text-xs font-mono",
                      isUrgent ? "text-red-300" : "text-slate-300",
                    )}
                  >
                    {rec}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Generate Report */}
      {onGenerateReport && (
        <button
          onClick={onGenerateReport}
          disabled={isGeneratingReport}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-indigo-500/30 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-300 font-mono font-semibold text-sm transition-all disabled:opacity-50"
        >
          <Download className={cn("h-4 w-4", isGeneratingReport && "animate-bounce")} />
          {isGeneratingReport ? "Generating Report..." : "Generate Enterprise Report"}
        </button>
      )}

      <p className="text-[9px] font-mono text-slate-600 text-right">
        Generated: {new Date(summary.generated_at).toLocaleString()}
      </p>
    </div>
  );
}
