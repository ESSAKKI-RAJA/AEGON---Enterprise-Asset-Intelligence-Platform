import { Link, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard,
  ShieldAlert,
  Boxes,
  BarChart3,
  Settings as SettingsIcon,
  Menu,
  X,
  ChevronLeft,
  Bell,
  Search,
  ChevronRight,
  Wrench,
  Package,
  ShoppingCart,
  DollarSign,
  BrainCircuit,
  Shield,
  Activity,
} from "lucide-react";
import { useEffect, useState, type ReactNode, memo } from "react";
import { cn } from "@/lib/utils";
import { CopilotPanel } from "@/components/copilot/CopilotPanel";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { useUIStore } from "@/store";
import { DEMO_USER } from "@/lib/auth";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/assets", label: "Assets", icon: Boxes },
  { to: "/digital-twin", label: "Digital Twin", icon: Activity },
  { to: "/maintenance", label: "Maintenance", icon: Wrench },
  { to: "/inventory", label: "Inventory", icon: Package },
  { to: "/procurement", label: "Procurement", icon: ShoppingCart },
  { to: "/finance", label: "Finance", icon: DollarSign },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/ai-intelligence", label: "AI Intelligence", icon: BrainCircuit },
  { to: "/security", label: "Security", icon: Shield },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
] as const;

const TITLE_MAP: Record<string, string> = {
  "/dashboard": "Executive Dashboard",
  "/assets": "Asset Registry",
  "/digital-twin": "Digital Twin",
  "/maintenance": "Maintenance Intelligence",
  "/inventory": "Inventory Optimization",
  "/procurement": "Procurement",
  "/finance": "Finance Intelligence",
  "/analytics": "Analytics",
  "/ai-intelligence": "AI Intelligence",
  "/security": "Security Center",
  "/settings": "Settings",
};

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { sidebarCollapsed, toggleSidebar, setSidebarCollapsed } = useUIStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setPaletteOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setPaletteOpen(false);
        setCopilotOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const title = TITLE_MAP[pathname] ?? "AEGON";

  return (
    <div className="min-h-dvh bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-50">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden animate-fade-in"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <Sidebar
        collapsed={sidebarCollapsed}
        mobileOpen={mobileOpen}
        pathname={pathname}
        onToggle={toggleSidebar}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <div
        className={cn(
          "flex min-h-dvh flex-col transition-all duration-300 ease-in-out",
          sidebarCollapsed ? "md:pl-[72px]" : "md:pl-[240px]",
        )}
      >
        {/* Floating Header */}
        <div className="p-4 md:px-6 md:pt-6 pb-0">
          <header className="z-30 flex h-14 items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 px-4 shadow-sm backdrop-blur-md">
            <button
              className="grid h-8 w-8 place-items-center rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 md:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </button>

            {/* Breadcrumbs */}
            <div className="flex min-w-0 items-center gap-2 text-sm font-medium">
              <span className="hidden text-slate-500 dark:text-slate-400 sm:inline">AEGON</span>
              <ChevronRight className="hidden h-3.5 w-3.5 text-slate-400 sm:inline" />
              <h1 className="truncate text-slate-900 dark:text-slate-100 tracking-tight">
                {title}
              </h1>
            </div>

            <div className="ml-auto flex items-center gap-3">
              {/* Evaluation Mode Badge */}
              <div className="hidden lg:flex items-center">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-widest text-teal-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-teal-400 animate-pulse" />
                  Evaluation Mode
                </span>
              </div>

              {/* Floating Search Bar */}
              <div className="relative hidden md:block">
                <button
                  onClick={() => setPaletteOpen(true)}
                  className="flex items-center justify-between h-9 w-64 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/50 pl-3 pr-2 text-sm text-slate-500 hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors shadow-inner"
                >
                  <div className="flex items-center gap-2">
                    <Search className="h-4 w-4" />
                    <span>Search resources...</span>
                  </div>
                  <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-1.5 font-mono text-[10px] font-medium text-slate-500">
                    <span className="text-xs">⌘</span>K
                  </kbd>
                </button>
              </div>

              <div className="flex items-center gap-1 border-l border-slate-200 dark:border-slate-800 pl-3">
                <button
                  onClick={() => setCopilotOpen(true)}
                  className="relative grid h-8 w-8 place-items-center rounded-full hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 transition-colors"
                  title="AEGON AI Copilot"
                >
                  <BrainCircuit className="h-4.5 w-4.5" />
                </button>

                <button
                  className="relative grid h-8 w-8 place-items-center rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors"
                  title="Notifications"
                >
                  <Bell className="h-4.5 w-4.5" />
                  <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-slate-900" />
                </button>
              </div>

              {/* Demo User Chip */}
              <div className="ml-1 flex items-center gap-2 border-l border-slate-200 dark:border-slate-800 pl-3">
                <div className="flex items-center gap-2.5 rounded-lg border border-slate-200 dark:border-slate-700/50 bg-slate-50 dark:bg-slate-900 px-2.5 py-1.5 shadow-sm">
                  {/* Avatar */}
                  <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-teal-500 to-indigo-600 text-white text-xs font-bold shadow-sm shadow-teal-500/20 shrink-0">
                    {DEMO_USER.initials}
                  </div>
                  {/* Info */}
                  <div className="hidden lg:flex flex-col min-w-0">
                    <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[120px]">
                      {DEMO_USER.name}
                    </span>
                    <span className="text-[10px] text-teal-600 dark:text-teal-400 font-medium uppercase tracking-wide">
                      {DEMO_USER.role}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </header>
        </div>

        <main key={pathname} className="flex-1 animate-fade-in">
          <div className="mx-auto max-w-[1600px] p-4 md:p-6">{children}</div>
        </main>
      </div>

      <CopilotPanel isOpen={copilotOpen} onClose={() => setCopilotOpen(false)} />
      <CommandPalette isOpen={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </div>
  );
}

const Sidebar = memo(function Sidebar({
  collapsed,
  mobileOpen,
  pathname,
  onToggle,
  onCloseMobile,
}: {
  collapsed: boolean;
  mobileOpen: boolean;
  pathname: string;
  onToggle: () => void;
  onCloseMobile: () => void;
}) {
  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex flex-col bg-white dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 transition-all duration-300 ease-in-out shadow-sm",
        collapsed ? "md:w-[72px]" : "md:w-[240px]",
        "w-[280px]",
        mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
      )}
      aria-label="Enterprise navigation"
    >
      {/* Premium Logo Area */}
      <div className="flex h-20 shrink-0 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-white shadow-md shadow-indigo-600/20">
            <ShieldAlert className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold tracking-tight text-slate-900 dark:text-white text-lg leading-none">
                AEGON
              </span>
              <span className="text-[9px] text-slate-400 uppercase tracking-widest font-medium leading-tight mt-0.5">
                Enterprise Platform
              </span>
            </div>
          )}
        </div>
        <button
          className="grid h-7 w-7 place-items-center rounded-md text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white md:hidden"
          onClick={onCloseMobile}
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-2 custom-scrollbar">
        <ul className="space-y-1">
          {NAV.map((item) => {
            const active = pathname.startsWith(item.to);
            const Icon = item.icon;
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={cn(
                    "group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
                    active
                      ? "bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200",
                    collapsed && "md:justify-center md:px-2",
                  )}
                  aria-current={active ? "page" : undefined}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 shrink-0 transition-colors",
                      active ? "text-indigo-600 dark:text-indigo-400" : "",
                    )}
                  />
                  <span className={cn("truncate", collapsed && "md:hidden")}>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Collapse Toggle at Bottom */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={onToggle}
          className="hidden md:flex w-full items-center justify-center rounded-md p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-300 transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <ChevronLeft
            className={cn("h-4 w-4 transition-transform duration-300", collapsed && "rotate-180")}
          />
        </button>
      </div>
    </aside>
  );
});
