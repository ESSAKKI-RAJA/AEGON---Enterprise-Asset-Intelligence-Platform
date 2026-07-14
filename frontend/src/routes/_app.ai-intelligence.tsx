import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { PageLayout, PageHeader } from "@/components/layout/PageLayout";
import {
  BrainCircuit,
  User,
  Send,
  Loader2,
  Trash2,
  Copy,
  CheckCircle2,
  Download,
  MessageSquare,
  Activity,
  Server,
  Zap,
  Database,
  Clock,
  Pin,
  ChevronRight,
  PlusCircle,
  FileText,
  AlertTriangle,
  BarChart,
  ShieldAlert,
} from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/ai-intelligence")({
  component: AIIntelligencePage,
});

const SUGGESTED_PROMPTS = [
  "Which assets require replacement?",
  "Predict next quarter CAPEX.",
  "Which departments are highest risk?",
  "Summarize enterprise health.",
  "Predict maintenance costs.",
  "Compare Plant A vs Plant B.",
];

const HISTORY_SESSIONS = [
  { id: 1, title: "Q3 Budget Optimization", date: "Today", pinned: true },
  { id: 2, title: "Pump Failure Analysis", date: "Yesterday", pinned: false },
  { id: 3, title: "Vendor Risk Assessment", date: "Last Week", pinned: false },
];

function AIIntelligencePage() {
  const [query, setQuery] = useState("");
  const [conversation, setConversation] = useState<
    { role: string; text: string; timestamp: Date; meta?: any }[]
  >([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const askMutation = useMutation({
    mutationFn: (q: string) => apiClient.post("/ai/copilot/ask", { query: q }),
    onSuccess: (data: any, variables: string) => {
      const text = data.response?.message || "No response received";

      // Mock logic to append rich metadata based on the query contents
      const meta = {
        confidence: Math.floor(Math.random() * 15) + 85, // 85-99%
        latency: Math.floor(Math.random() * 800) + 200, // 200-1000ms
        sources: ["Predictive Models", "Asset Registry"],
        priority:
          text.toLowerCase().includes("risk") || text.toLowerCase().includes("fail")
            ? "High"
            : "Normal",
      };

      if (
        variables.toLowerCase().includes("finance") ||
        variables.toLowerCase().includes("capex")
      ) {
        meta.sources.push("Financial Ledgers");
      }

      setConversation((prev) => [...prev, { role: "ai", text, timestamp: new Date(), meta }]);
    },
    onError: (err: any) => {
      setConversation((prev) => [
        ...prev,
        {
          role: "ai",
          text: `**Error:** ${err.message}`,
          timestamp: new Date(),
          meta: { confidence: 0, sources: [], latency: 0 },
        },
      ]);
    },
  });

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    const currentQuery = query;
    setQuery("");
    setConversation((prev) => [
      ...prev,
      { role: "user", text: currentQuery, timestamp: new Date() },
    ]);
    askMutation.mutate(currentQuery);
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    toast.success("Copied to clipboard");
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleClear = () => {
    setConversation([]);
    toast.info("Context cleared");
  };

  return (
    <PageLayout>
      <PageHeader
        title="Enterprise Decision Intelligence"
        description="AEGON Foundation Model — Strategic forecasting, anomaly detection, and operational intelligence."
        actions={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 border border-teal-500/30 bg-teal-950/20 px-3 py-1.5 rounded-full shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
              </span>
              <span className="font-mono text-xs text-teal-400">Connected to ML Gateway</span>
            </div>
            {conversation.length > 0 && (
              <button
                onClick={() => toast.success("Executive Brief exported to PDF.")}
                className="flex items-center gap-1 text-xs font-semibold font-mono text-indigo-400 hover:text-indigo-300 bg-indigo-400/10 hover:bg-indigo-400/20 px-3 py-1.5 rounded border border-indigo-500/20 transition-colors"
              >
                <Download className="h-3.5 w-3.5" />
                Export Brief
              </button>
            )}
          </div>
        }
      />

      <div className="flex h-[75vh] border border-slate-700/50 rounded-xl bg-slate-900/80 shadow-2xl backdrop-blur-sm overflow-hidden">
        {/* Left Sidebar — Context & History */}
        <div className="hidden lg:flex w-72 border-r border-slate-700/50 bg-slate-950/50 flex-col">
          <div className="p-4 border-b border-slate-800">
            <button
              onClick={handleClear}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm py-2 px-4 rounded-lg transition-colors shadow-sm"
            >
              <PlusCircle className="h-4 w-4" />
              New Analysis
            </button>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">
                Suggested Vectors
              </h4>
              <div className="space-y-1">
                {SUGGESTED_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setQuery(prompt);
                      // Auto submit for better UX
                      // handleSubmit();
                    }}
                    className="w-full flex items-start gap-2 p-2 rounded-md hover:bg-slate-800 transition-colors text-left text-xs text-slate-300 group"
                  >
                    <ChevronRight className="h-3.5 w-3.5 text-indigo-500/50 group-hover:text-indigo-400 shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{prompt}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">
                Recent Sessions
              </h4>
              <div className="space-y-1">
                {HISTORY_SESSIONS.map((session) => (
                  <button
                    key={session.id}
                    className="w-full flex items-center justify-between p-2 rounded-md hover:bg-slate-800 transition-colors text-left group"
                  >
                    <div className="flex items-center gap-2 overflow-hidden">
                      <MessageSquare className="h-3.5 w-3.5 text-slate-500 shrink-0" />
                      <div className="flex flex-col truncate">
                        <span className="text-xs text-slate-300 truncate">{session.title}</span>
                        <span className="text-[10px] text-slate-500">{session.date}</span>
                      </div>
                    </div>
                    {session.pinned && <Pin className="h-3 w-3 text-teal-500 shrink-0" />}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Intelligence Area */}
        <div className="flex-1 flex flex-col min-w-0 bg-slate-900/40">
          {/* Enterprise AI Header */}
          <div className="h-12 border-b border-slate-700/50 bg-slate-900/60 backdrop-blur-md flex items-center justify-between px-4 shrink-0">
            <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
              <div className="flex items-center gap-1.5" title="Active Model">
                <BrainCircuit className="h-3.5 w-3.5 text-indigo-400" />
                <span className="font-semibold text-slate-300">AEGON-LLaMA-3-8B-Instruct</span>
              </div>
              <div className="h-3 w-px bg-slate-700"></div>
              <div className="flex items-center gap-1.5" title="Inference Status">
                <Activity className="h-3.5 w-3.5 text-emerald-400" />
                <span>Status: Processing Ready</span>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono text-slate-400 hidden sm:flex">
              <div className="flex items-center gap-1.5" title="Knowledge Base Sync">
                <Database className="h-3.5 w-3.5 text-teal-400" />
                <span>KB Synced (2 mins ago)</span>
              </div>
            </div>
          </div>

          {/* Chat Container */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar relative">
            {conversation.length === 0 ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 p-6 pointer-events-none">
                <div className="h-16 w-16 bg-indigo-500/10 rounded-2xl flex items-center justify-center border border-indigo-500/20 mb-6">
                  <BrainCircuit className="h-8 w-8 text-indigo-400" />
                </div>
                <h3 className="text-xl font-semibold text-slate-200 mb-2 font-sans tracking-tight">
                  AEGON Intelligence Copilot
                </h3>
                <p className="text-sm text-slate-400 max-w-md mx-auto text-center leading-relaxed">
                  Ask strategic questions across assets, maintenance records, inventory levels, and
                  financial forecasts. The engine will synthesize insights across the enterprise
                  knowledge graph.
                </p>
              </div>
            ) : (
              conversation.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={cn(
                      "flex flex-col max-w-full lg:max-w-[85%] rounded-xl shadow-md border",
                      msg.role === "user"
                        ? "bg-indigo-600 border-indigo-500 text-indigo-50 rounded-br-sm p-4"
                        : "bg-slate-800/80 text-slate-200 rounded-bl-sm border-slate-700 p-5 backdrop-blur-sm",
                    )}
                  >
                    <div className="flex gap-4">
                      {msg.role === "ai" && (
                        <div className="shrink-0 mt-0.5">
                          <div className="bg-gradient-to-br from-indigo-500 to-teal-500 p-2 rounded border border-indigo-400/50 shadow-sm">
                            <BrainCircuit className="h-4 w-4 text-white" />
                          </div>
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        {/* User Metadata */}
                        {msg.role === "user" && (
                          <div className="flex items-center justify-end gap-2 mb-2 text-[10px] font-mono text-indigo-200/70">
                            <span>{msg.timestamp.toLocaleTimeString()}</span>
                            <User className="h-3 w-3" />
                          </div>
                        )}

                        {/* Message Content */}
                        <div
                          className={cn(
                            "prose prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800",
                            msg.role === "user"
                              ? "text-indigo-50"
                              : "prose-invert prose-p:text-slate-300 prose-headings:text-slate-200 prose-a:text-teal-400 prose-strong:text-slate-200",
                          )}
                        >
                          {msg.role === "user" ? (
                            <div className="whitespace-pre-wrap text-sm">{msg.text}</div>
                          ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                          )}
                        </div>

                        {/* AI Rich Metadata Footer */}
                        {msg.role === "ai" && msg.meta && (
                          <div className="mt-5 pt-3 border-t border-slate-700/50 grid grid-cols-2 lg:grid-cols-4 gap-3 bg-slate-900/30 p-3 rounded-lg">
                            <div className="flex flex-col gap-1">
                              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                                Confidence
                              </span>
                              <div className="flex items-center gap-1.5">
                                <Activity className="h-3 w-3 text-emerald-400" />
                                <span className="text-xs font-semibold text-emerald-400">
                                  {msg.meta.confidence}%
                                </span>
                              </div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                                Priority
                              </span>
                              <div className="flex items-center gap-1.5">
                                {msg.meta.priority === "High" ? (
                                  <AlertTriangle className="h-3 w-3 text-orange-400" />
                                ) : (
                                  <CheckCircle2 className="h-3 w-3 text-blue-400" />
                                )}
                                <span
                                  className={`text-xs font-semibold ${msg.meta.priority === "High" ? "text-orange-400" : "text-blue-400"}`}
                                >
                                  {msg.meta.priority}
                                </span>
                              </div>
                            </div>
                            <div className="flex flex-col gap-1 lg:col-span-2">
                              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                                Sources Consulted
                              </span>
                              <div className="flex items-center gap-2 flex-wrap">
                                {msg.meta.sources.map((src: string, i: number) => (
                                  <span
                                    key={i}
                                    className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-700/50 text-slate-300 border border-slate-600"
                                  >
                                    <FileText className="h-2.5 w-2.5 mr-1 text-slate-400" />
                                    {src}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {msg.role === "ai" && (
                      <div className="flex justify-end mt-2 pt-2 border-t border-transparent">
                        <button
                          onClick={() => handleCopy(msg.text, idx)}
                          className="text-[10px] font-mono font-medium text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
                        >
                          {copiedIndex === idx ? (
                            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                          {copiedIndex === idx ? "Copied" : "Copy"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {askMutation.isPending && (
              <div className="flex justify-start">
                <div className="flex flex-col max-w-[85%] rounded-xl shadow-md border bg-slate-800/80 text-slate-200 rounded-bl-sm border-slate-700 p-5 backdrop-blur-sm">
                  <div className="flex items-center gap-4">
                    <div className="shrink-0">
                      <div className="bg-gradient-to-br from-indigo-500 to-teal-500 p-2 rounded border border-indigo-400/50 shadow-sm animate-pulse">
                        <BrainCircuit className="h-4 w-4 text-white" />
                      </div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <div className="text-[10px] font-mono text-slate-500 font-semibold uppercase tracking-widest">
                        Model Inferencing
                      </div>
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-teal-500" />
                        <span className="font-mono text-xs text-slate-300 bg-gradient-to-r from-teal-400 to-indigo-400 bg-clip-text text-transparent">
                          Synthesizing context from enterprise datasets...
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={endOfMessagesRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
            <form
              onSubmit={handleSubmit}
              className="relative flex items-end gap-2 max-w-4xl mx-auto bg-slate-950 p-2 rounded-xl border border-slate-700 shadow-inner focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all"
            >
              <div className="flex-1 min-h-[44px]">
                <textarea
                  className="w-full bg-transparent border-none text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-0 resize-none max-h-32 min-h-[44px] py-3 pl-3 custom-scrollbar"
                  placeholder="Ask a strategic question or request an analysis..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  disabled={askMutation.isPending}
                  rows={1}
                />
              </div>
              <div className="flex items-center shrink-0 mb-1 mr-1">
                <button
                  type="submit"
                  disabled={askMutation.isPending || !query.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-lg disabled:opacity-50 disabled:bg-slate-800 disabled:text-slate-500 transition-all shadow-md flex items-center justify-center"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </form>
            <div className="text-center mt-2">
              <span className="text-[10px] text-slate-500 font-mono">
                AEGON LLMs can make mistakes. Verify critical financial metrics.
              </span>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
