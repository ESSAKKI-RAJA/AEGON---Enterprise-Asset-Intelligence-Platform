import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles/styles.css?url";
import { Toaster } from "@/components/ui/sonner";

function NotFoundComponent() {
  return (
    <div className="flex min-h-dvh items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-display text-7xl text-foreground font-mono">404</h1>
        <h2 className="mt-4 text-xl font-semibold font-mono">Module not found</h2>
        <p className="mt-2 text-sm text-muted-foreground font-mono">
          The requested intelligence module doesn't exist or you lack clearance.
        </p>
        <div className="mt-6">
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center rounded-md gradient-teal px-4 py-2 text-sm font-medium text-white font-mono"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: any; reset: () => void }) {
  console.error("Root Error Boundary caught:", error);
  const router = useRouter();

  useEffect(() => {
    // Error reporting removed
  }, [error]);

  const isAxiosError = error?.isAxiosError || !!error?.response;
  const status = error?.response?.status || 500;
  const endpoint = error?.config?.url || error?.request?.responseURL || "Unknown Endpoint";
  const message =
    error?.response?.data?.message || error?.message || "An unexpected error occurred.";
  const correlationId = error?.response?.headers?.["x-correlation-id"] || "N/A";
  const timestamp = new Date().toISOString();

  return (
    <div className="flex min-h-dvh items-center justify-center bg-background px-4 py-8">
      <div className="w-full max-w-2xl text-left border border-border rounded-xl bg-card shadow-sm overflow-hidden">
        <div className="bg-critical/10 p-6 border-b border-border/50 flex items-start gap-4">
          <div className="p-3 bg-critical/20 rounded-full text-critical">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <path d="M12 9v4" />
              <path d="M12 17h.01" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground font-mono">System Exception</h1>
            <p className="mt-1 text-sm text-muted-foreground font-mono">
              {isAxiosError
                ? "The intelligence backend encountered a problem processing your request."
                : "A frontend rendering exception occurred."}
            </p>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
            <h3 className="text-sm font-semibold mb-2 font-mono">Exception Details</h3>
            <div className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
              {isAxiosError && (
                <>
                  <div className="text-muted-foreground font-mono">HTTP Status:</div>
                  <div className="font-mono font-medium text-critical">{status}</div>
                  <div className="text-muted-foreground font-mono">Endpoint:</div>
                  <div className="font-mono text-xs break-all">{endpoint}</div>
                </>
              )}
              <div className="text-muted-foreground font-mono">Message:</div>
              <div className="font-medium text-foreground font-mono">{message}</div>
              <div className="text-muted-foreground font-mono">Timestamp:</div>
              <div className="font-mono text-xs text-muted-foreground">{timestamp}</div>
              <div className="text-muted-foreground font-mono">Correlation ID:</div>
              <div className="font-mono text-xs text-muted-foreground">{correlationId}</div>
            </div>
          </div>

          {process.env.NODE_ENV === "development" && (
            <details className="mt-4 border border-border/50 rounded-lg bg-muted/30">
              <summary className="p-3 text-sm font-medium cursor-pointer hover:bg-muted/50 font-mono">
                Developer Stack Trace
              </summary>
              <pre className="p-4 text-xs font-mono text-muted-foreground overflow-x-auto whitespace-pre-wrap border-t border-border/50">
                {error?.stack || "No stack trace available"}
              </pre>
            </details>
          )}

          <div className="mt-6 flex flex-wrap justify-end gap-3 pt-2">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center justify-center rounded-md border border-border bg-background px-4 py-2 text-sm font-medium hover:bg-muted transition-colors font-mono"
            >
              Hard Refresh
            </button>
            <button
              onClick={() => {
                router.invalidate();
                reset();
              }}
              className="inline-flex items-center justify-center rounded-md gradient-teal px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity font-mono"
            >
              Retry Action
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "AEGON Enterprise — Asset Management & Preventive Operations" },
      {
        name: "description",
        content:
          "AEGON Enterprise: Next-generation AI-powered enterprise asset management, preventive operations, and risk intelligence platform.",
      },
      { name: "author", content: "AEGON" },
      {
        property: "og:title",
        content: "AEGON Enterprise — Asset Management & Preventive Operations",
      },
      {
        property: "og:description",
        content: "AI-powered enterprise asset management and preventive operations.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
      </head>
      <body className="dark bg-slate-950 text-slate-50">
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
      <Toaster position="top-right" theme="dark" />
    </QueryClientProvider>
  );
}
