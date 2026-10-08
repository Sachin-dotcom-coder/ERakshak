import { Link, useRouterState } from "@tanstack/react-router";
import { Map, Camera, BarChart3, Hexagon } from "lucide-react";
import type { ReactNode } from "react";

const NAV = [
  { to: "/", label: "Command", icon: Map },
  { to: "/surveillance", label: "Cameras", icon: Camera },
  { to: "/reports", label: "Reports", icon: BarChart3 },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      {/* ── Sidebar Nav Rail ─────────────────────────────────── */}
      <nav className="nav-rail shrink-0 h-screen">
        {/* Logo */}
        <div className="mb-4 flex flex-col items-center gap-1 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
            <Hexagon className="h-5 w-5 text-primary" strokeWidth={1.5} />
          </div>
        </div>

        {/* Nav items */}
        <div className="flex flex-col items-center gap-2 px-2 flex-1">
          {NAV.map((item) => {
            const active =
              item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                title={item.label}
                className={`nav-item ${active ? "active" : ""}`}
              >
                <item.icon className="h-5 w-5" strokeWidth={1.8} />
                <span className="nav-label">{item.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Bottom branding */}
        <div className="mt-auto px-2 pb-2 flex flex-col items-center">
          <div className="label-xs text-center" style={{ fontSize: 7 }}>
            E·RAKSHAK<br />2026
          </div>
        </div>
      </nav>

      {/* ── Main Content ─────────────────────────────────────── */}
      <main className="min-w-0 flex-1 flex flex-col h-full overflow-hidden">{children}</main>
    </div>
  );
}
