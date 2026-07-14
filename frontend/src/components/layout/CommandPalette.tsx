import { useState, useEffect, useRef } from "react";
import { Search, Package, Wrench, Settings } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export function CommandPalette({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    } else {
      setQuery("");
      setResults([]);
    }
  }, [isOpen]);

  useEffect(() => {
    const fetchResults = async () => {
      if (query.trim().length < 2) {
        setResults([]);
        return;
      }
      try {
        const token = localStorage.getItem("access_token");
        const res = await axios.get(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setResults(res.data.data || []);
      } catch (err) {
        console.error("Search failed", err);
      }
    };

    const timeout = setTimeout(fetchResults, 300);
    return () => clearTimeout(timeout);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-24">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Palette */}
      <div className="relative w-full max-w-2xl bg-slate-950 border border-slate-800 rounded-lg shadow-2xl overflow-hidden flex flex-col">
        <div className="flex items-center p-3 border-b border-slate-800">
          <Search className="h-5 w-5 text-slate-500 mr-3 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none focus:outline-none text-slate-200 font-mono text-lg placeholder:text-slate-600"
            placeholder="Search assets, work orders, intelligence..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <div className="text-xs text-slate-500 font-mono flex gap-2">
            <kbd className="bg-slate-900 border border-slate-800 rounded px-1.5 py-0.5">ESC</kbd> to
            close
          </div>
        </div>

        <div className="max-h-[60vh] overflow-y-auto custom-scrollbar">
          {query && results.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-mono text-sm">
              No results found for "{query}".
            </div>
          ) : (
            <ul className="p-2 space-y-1">
              {results.map((item, idx) => (
                <li key={idx}>
                  <button
                    className="w-full flex flex-col text-left p-3 hover:bg-slate-900 rounded border border-transparent hover:border-slate-800 transition-colors focus:bg-slate-900 focus:outline-none"
                    onClick={() => {
                      navigate({ to: item.link });
                      onClose();
                    }}
                  >
                    <div className="flex items-center gap-2">
                      {item.type === "ASSET" && <Package className="h-4 w-4 text-teal-400" />}
                      {item.type === "WORK_ORDER" && <Wrench className="h-4 w-4 text-orange-400" />}
                      {item.type === "USER" && <Search className="h-4 w-4 text-indigo-400" />}
                      {item.type === "DEPARTMENT" && <Search className="h-4 w-4 text-sky-400" />}
                      <span className="font-semibold text-slate-200 font-mono text-sm">
                        {item.title}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 font-mono mt-1 ml-6">
                      {item.subtitle}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {!query && (
            <div className="p-4 space-y-4">
              <div>
                <h4 className="text-xs font-semibold text-slate-600 uppercase font-mono tracking-wider mb-2 px-2">
                  Suggestions
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      navigate({ to: "/assets" });
                      onClose();
                    }}
                    className="flex items-center gap-2 p-2 rounded hover:bg-slate-900 text-slate-400 font-mono text-sm"
                  >
                    <Package className="h-4 w-4" /> Go to Assets
                  </button>
                  <button
                    onClick={() => {
                      navigate({ to: "/maintenance" });
                      onClose();
                    }}
                    className="flex items-center gap-2 p-2 rounded hover:bg-slate-900 text-slate-400 font-mono text-sm"
                  >
                    <Wrench className="h-4 w-4" /> Go to Maintenance
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
