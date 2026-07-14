export function AegonLogo({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg gradient-teal shadow-[0_0_20px_rgba(6,182,212,0.4)]">
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5 text-white"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
        >
          <path d="M12 2L3 7v6c0 5 4 9 9 10 5-1 9-5 9-10V7l-9-5z" strokeLinejoin="round" />
          <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      {!collapsed && (
        <div className="flex flex-col leading-none">
          <span className="text-display text-lg tracking-tight text-white">AEGON</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-slate-400">
            Asset Intelligence
          </span>
        </div>
      )}
    </div>
  );
}
