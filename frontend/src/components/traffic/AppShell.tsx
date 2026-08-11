import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutGrid, Radar, FileBarChart2 } from "lucide-react";
import type { ReactNode } from "react";
import { SuratTrafficNexusLogo } from "./Logo";

const NAV = [
  { to: "/", label: "Command Centre", icon: LayoutGrid },
  { to: "/surveillance", label: "Surveillance", icon: Radar },
  { to: "/reports", label: "Reports", icon: FileBarChart2 },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="sticky top-0 z-30 flex h-screen w-14 shrink-0 flex-col items-center gap-1 border-r border-border bg-panel py-3 md:w-16">
        <div className="mb-3">
          <SuratTrafficNexusLogo showBadge />
        </div>
        {NAV.map((item) => {
          const active =
            item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              title={item.label}
              className={`group relative grid h-11 w-11 place-items-center border transition-colors ${
                active
                  ? "border-primary/50 bg-primary/15 text-primary"
                  : "border-transparent text-muted-foreground hover:border-border hover:bg-panel-raised hover:text-foreground"
              }`}
            >
              <item.icon className="h-5 w-5" />
              {active && (
                <span className="absolute left-0 top-1/2 h-6 w-0.5 -translate-y-1/2 bg-primary" />
              )}
            </Link>
          );
        })}
        <div className="mt-auto label-xs rotate-180 [writing-mode:vertical-rl]">
          E-RAKSHAK 2026
        </div>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
