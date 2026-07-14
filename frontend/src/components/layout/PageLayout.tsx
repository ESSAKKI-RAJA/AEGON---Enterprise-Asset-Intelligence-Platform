import { ReactNode, useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface PageLayoutProps {
  children: ReactNode;
  className?: string;
}

export function PageLayout({ children, className }: PageLayoutProps) {
  return <div className={cn("space-y-6 pb-12", className)}>{children}</div>;
}

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
}

export function PageHeader({ title, description, actions, className }: PageHeaderProps) {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    toast.info("Syncing enterprise data...");
    setTimeout(() => {
      setLastUpdated(new Date());
      setIsRefreshing(false);
      toast.success("Data synchronized successfully.");
    }, 800);
  };

  return (
    <header
      className={cn(
        "border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-end justify-between gap-4",
        className,
      )}
    >
      <div>
        <div className="flex items-center gap-3">
          <h2 className="text-display text-2xl font-bold font-mono tracking-tight text-white">
            {title}
          </h2>
          <button
            onClick={handleRefresh}
            className="text-slate-500 hover:text-teal-400 transition-colors p-1 rounded hover:bg-slate-800 group"
            title="Refresh Data"
          >
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin text-teal-400")} />
          </button>
        </div>
        {description && (
          <div className="mt-1 flex items-center gap-3">
            <p className="text-sm text-slate-400 font-mono">{description}</p>
            <span className="text-[10px] text-slate-600 font-mono hidden sm:inline-block border-l border-slate-700 pl-3">
              Last synced: {lastUpdated.toLocaleTimeString()}
            </span>
          </div>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </header>
  );
}

interface SectionHeaderProps {
  title: string;
  icon?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function SectionHeader({ title, icon, actions, className }: SectionHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between mb-4", className)}>
      <h3 className="text-lg font-bold text-slate-200 font-mono flex items-center gap-2">
        {icon && <span className="text-slate-400">{icon}</span>}
        {title}
      </h3>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
