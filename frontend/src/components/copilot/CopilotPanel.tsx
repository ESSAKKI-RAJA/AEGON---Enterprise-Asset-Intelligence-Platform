import { useState, useEffect, useRef } from "react";
import { BrainCircuit, X, Send, Bot, User as UserIcon } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? "" : "http://127.0.0.1:8000/api/v1");

interface Message {
  id: string;
  sender: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

// Typing effect component
function TypewriterText({
  text,
  isStreaming,
  onComplete,
}: {
  text: string;
  isStreaming?: boolean;
  onComplete?: () => void;
}) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedText(text);
      return;
    }

    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i + 1));
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, 15);

    return () => clearInterval(interval);
  }, [text, isStreaming, onComplete]);

  return <span>{displayedText}</span>;
}

export function CopilotPanel({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      sender: "assistant",
      content:
        "Hello. I am AEGON Copilot. Ask me anything about your enterprise assets, work orders, or financial trends.",
      isStreaming: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      content: input,
      isStreaming: false,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/ai/copilot/ask`, { query: userMsg.content });

      const aiResponse = res.data.data.response.message;
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + "ai",
          sender: "assistant",
          content: aiResponse,
          isStreaming: true,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + "err",
          sender: "assistant",
          content: "Sorry, I am unable to connect to the intelligence gateway at the moment.",
          isStreaming: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: "100%", opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: "100%", opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="fixed inset-y-0 right-0 z-50 w-full max-w-[400px] border-l border-white/20 dark:border-slate-800/60 bg-white/70 dark:bg-slate-950/70 shadow-2xl backdrop-blur-2xl flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-black/5 dark:border-white/10 p-4 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
            <div className="flex items-center gap-2.5">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 shadow-sm shadow-indigo-500/20 text-white">
                <BrainCircuit className="h-4.5 w-4.5" />
              </div>
              <span className="font-semibold text-slate-800 dark:text-white tracking-tight">
                AEGON Copilot
              </span>
            </div>
            <button
              onClick={onClose}
              className="grid h-8 w-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-5 custom-scrollbar">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "flex gap-3 text-sm max-w-[90%]",
                  msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto",
                )}
              >
                <div className="shrink-0 mt-0.5">
                  {msg.sender === "user" ? (
                    <div className="h-7 w-7 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center border border-slate-300 dark:border-slate-700">
                      <UserIcon className="h-3.5 w-3.5 text-slate-600 dark:text-slate-400" />
                    </div>
                  ) : (
                    <div className="h-7 w-7 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center border border-indigo-200 dark:border-indigo-800">
                      <Bot className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                  )}
                </div>
                <div
                  className={cn(
                    "p-3.5 rounded-2xl leading-relaxed shadow-sm",
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white rounded-tr-sm"
                      : "bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 rounded-tl-sm whitespace-pre-wrap backdrop-blur-md",
                  )}
                >
                  {msg.sender === "assistant" ? (
                    <TypewriterText
                      text={msg.content}
                      isStreaming={msg.isStreaming}
                      onComplete={() => {
                        // Unset streaming state to prevent re-typing on re-render
                        setMessages((prev) =>
                          prev.map((m) => (m.id === msg.id ? { ...m, isStreaming: false } : m)),
                        );
                      }}
                    />
                  ) : (
                    msg.content
                  )}
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3 text-sm max-w-[90%] mr-auto"
              >
                <div className="shrink-0 h-7 w-7 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center border border-indigo-200 dark:border-indigo-800">
                  <Bot className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400 animate-pulse" />
                </div>
                <div className="p-3.5 rounded-2xl bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-slate-500 rounded-tl-sm backdrop-blur-md flex items-center gap-1">
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  />
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </motion.div>
            )}
            <div ref={endOfMessagesRef} className="h-4" />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-black/5 dark:border-white/10 bg-white/60 dark:bg-slate-950/60 backdrop-blur-md">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="relative flex items-center shadow-sm"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Message Copilot..."
                className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl py-3 pl-4 pr-12 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner"
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2 p-1.5 rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:bg-slate-200 dark:disabled:bg-slate-800 disabled:text-slate-400 transition-colors"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
            <div className="mt-3 text-center">
              <span className="text-[10px] text-slate-400 dark:text-slate-500">
                AEGON AI can make mistakes. Verify important information.
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
