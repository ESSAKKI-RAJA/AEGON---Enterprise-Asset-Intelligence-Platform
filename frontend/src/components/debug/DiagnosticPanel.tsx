import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Database, Server, Settings, Zap, X, ChevronUp, ChevronDown } from 'lucide-react';
import { apiClient } from '@/lib/api';

export function DiagnosticPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [diagnostics, setDiagnostics] = useState<any>({
    environment: 'Loading...',
    database: 'Loading...',
    cache: 'Loading...',
    routes: 0,
    apiUrl: import.meta.env.VITE_API_URL || 'https://aegon-enterprise-asset-intelligence.onrender.com',
  });

  const fetchDiagnostics = async () => {
    try {
      const [envRes, dbRes, cacheRes, routesRes] = await Promise.all([
        apiClient.get('/health/debug/environment').catch(() => ({ env: 'Error' })),
        apiClient.get('/health/debug/database').catch((e) => ({ status: 'Error', error: e.message })),
        apiClient.get('/health/debug/cache').catch((e) => ({ status: 'Error', error: e.message })),
        apiClient.get('/health/debug/routes').catch(() => ({ routes_count: 0 })),
      ]);

      setDiagnostics({
        environment: envRes.env || 'Unknown',
        database: dbRes.status || 'Unknown',
        cache: cacheRes.status || 'Unknown',
        routes: routesRes.routes_count || 0,
        apiUrl: import.meta.env.VITE_API_URL || 'https://aegon-enterprise-asset-intelligence.onrender.com',
      });
    } catch (error) {
      console.error("Failed to fetch diagnostics", error);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDiagnostics();
    }
  }, [isOpen]);

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="mb-4 w-80 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-950"
          >
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-3 dark:border-slate-800/50 dark:bg-slate-900/50">
              <div className="flex items-center gap-2 font-mono text-sm font-semibold text-slate-700 dark:text-slate-300">
                <Activity className="h-4 w-4 text-indigo-500" />
                Developer Diagnostics
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-md p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            <div className="flex flex-col gap-3 p-4 font-mono text-xs">
              <div className="flex items-center justify-between rounded-lg bg-slate-50 p-2 dark:bg-slate-900/50">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <Settings className="h-3.5 w-3.5" /> Environment
                </div>
                <div className="font-medium text-slate-700 dark:text-slate-300">
                  {diagnostics.environment}
                </div>
              </div>
              
              <div className="flex items-center justify-between rounded-lg bg-slate-50 p-2 dark:bg-slate-900/50">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <Database className="h-3.5 w-3.5" /> Database
                </div>
                <div className={`font-medium ${diagnostics.database === 'connected' ? 'text-green-500' : 'text-red-500'}`}>
                  {diagnostics.database}
                </div>
              </div>
              
              <div className="flex items-center justify-between rounded-lg bg-slate-50 p-2 dark:bg-slate-900/50">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <Zap className="h-3.5 w-3.5" /> Redis Cache
                </div>
                <div className={`font-medium ${diagnostics.cache === 'connected' ? 'text-green-500' : 'text-red-500'}`}>
                  {diagnostics.cache}
                </div>
              </div>

              <div className="flex items-center justify-between rounded-lg bg-slate-50 p-2 dark:bg-slate-900/50">
                <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <Server className="h-3.5 w-3.5" /> API URL
                </div>
                <div className="truncate font-medium text-slate-700 dark:text-slate-300 max-w-[150px]" title={diagnostics.apiUrl}>
                  {diagnostics.apiUrl}
                </div>
              </div>
              
              <button 
                onClick={fetchDiagnostics}
                className="mt-2 w-full rounded-md bg-indigo-50 py-2 text-center font-semibold text-indigo-600 hover:bg-indigo-100 transition-colors dark:bg-indigo-900/30 dark:text-indigo-400 dark:hover:bg-indigo-900/50"
              >
                Refresh Diagnostics
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-white shadow-lg transition-transform hover:scale-105 active:scale-95 dark:bg-slate-200 dark:text-slate-900"
      >
        <Activity className="h-5 w-5" />
      </button>
    </div>
  );
}
