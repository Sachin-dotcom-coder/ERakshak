import { CLASS_COLOR } from "@/lib/mock-traffic";
import type { CameraFeed } from "@/lib/traffic-types";

const VIDEO_SOURCES: Record<string, string> = {
  "JN-01": "/videos/traffic_demo.mp4",
  "JN-02": "/videos/traffic_demo.mp4",
  "JN-03": "/videos/traffic_demo.mp4",
  "JN-04": "/videos/traffic_demo.mp4",
  "JN-05": "/videos/traffic_demo.mp4",
  "JN-07": "/videos/traffic_demo.mp4",
};

export function CameraTile({
  feed,
  overlays,
  brtsOnly,
  onClick,
  large = false,
}: {
  feed: CameraFeed;
  overlays: boolean;
  brtsOnly: boolean;
  onClick?: () => void;
  large?: boolean;
}) {
  const Wrapper = onClick ? "button" : "div";
  const videoUrl = VIDEO_SOURCES[feed.junctionId] || "/videos/traffic_demo.mp4";

  return (
    <Wrapper
      {...(onClick ? { onClick, type: "button" as const } : {})}
      className="group relative block h-fit w-full overflow-hidden border border-border bg-[oklch(0.14_0.02_264)] text-left"
    >
      <div className="relative aspect-video w-full overflow-hidden">
        {/* Real moving CCTV video background */}
        {feed.online ? (
          <video
            src={videoUrl}
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 h-full w-full object-cover opacity-80"
          />
        ) : (
          <div className="absolute inset-0 grid place-items-center bg-background/90">
            <span className="num border border-crit/50 bg-crit/10 px-2.5 py-1 text-[11px] font-semibold text-crit">
              SIGNAL LOST — CAMERA OFFLINE
            </span>
          </div>
        )}

        {/* Scan line effect overlay */}
        <div className="pointer-events-none absolute inset-0 opacity-20 [background-image:repeating-linear-gradient(0deg,transparent_0_3px,oklch(0.26_0.02_258)_3px_4px)]" />
        {feed.online && <div className="pointer-events-none absolute inset-x-0 h-10 bg-primary/[0.12] animate-scan" />}

        {/* annotation overlays */}
        {feed.online && overlays && (
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
            {/* lane polygons */}
            {!brtsOnly && (
              <>
                <polygon
                  points="4,100 30,40 42,40 26,100"
                  fill="oklch(0.8 0.14 195 / 0.08)"
                  stroke="oklch(0.8 0.14 195 / 0.4)"
                  strokeWidth="0.3"
                />
                <polygon
                  points="30,100 46,40 58,40 54,100"
                  fill="oklch(0.75 0.18 152 / 0.07)"
                  stroke="oklch(0.75 0.18 152 / 0.35)"
                  strokeWidth="0.3"
                />
              </>
            )}
            {feed.hasBrtsZone && (
              <polygon
                points="58,100 62,40 76,40 88,100"
                fill={feed.intrusionActive ? "var(--crit)" : "var(--live)"}
                fillOpacity={feed.intrusionActive ? 0.14 : 0.08}
                stroke={feed.intrusionActive ? "var(--crit)" : "var(--live)"}
                strokeWidth="0.6"
                strokeDasharray="2 1.4"
                className={feed.intrusionActive ? "animate-flash" : ""}
              />
            )}
          </svg>
        )}

        {feed.online &&
          overlays &&
          feed.boxes
            .filter((b) => !brtsOnly || b.intruding)
            .map((b) => {
              const flash = b.intruding && feed.intrusionActive;
              const color = flash ? "var(--crit)" : CLASS_COLOR[b.cls];
              return (
                <div
                  key={b.id}
                  className={`absolute border ${flash ? "animate-flash" : ""}`}
                  style={{
                    left: `${b.x}%`,
                    top: `${b.y}%`,
                    width: `${b.w}%`,
                    height: `${b.h}%`,
                    borderColor: color,
                    boxShadow: `inset 0 0 0 1px ${color}22`,
                    transition: "left .9s linear, top .9s linear",
                  }}
                >
                  <span
                    className="num absolute -top-3.5 left-0 whitespace-nowrap px-0.5 text-[8px] leading-[12px]"
                    style={{ backgroundColor: color, color: "oklch(0.15 0.02 264)" }}
                  >
                    {b.cls} {b.conf}%
                  </span>
                </div>
              );
            })}

        {/* labels */}
        <div className="absolute left-1.5 top-1.5 flex items-center gap-1.5">
          <span className="num border border-border bg-background/70 px-1.5 py-0.5 text-[9px] font-semibold">
            {feed.id}
          </span>
          <span className={`num truncate px-1 text-[9px] ${large ? "text-foreground" : "text-muted-foreground"}`}>
            {feed.junctionName}
          </span>
        </div>
        {feed.online && (
          <span className="absolute right-1.5 top-1.5 flex items-center gap-1 border border-crit/60 bg-crit/15 px-1.5 py-0.5">
            <span className="h-1.5 w-1.5 animate-blink rounded-full bg-crit" />
            <span className="num text-[9px] font-semibold text-crit">LIVE</span>
          </span>
        )}
        {feed.intrusionActive && overlays && (
          <span className="num absolute bottom-8 left-1/2 -translate-x-1/2 animate-blink border border-crit bg-crit/25 px-2 py-0.5 text-[10px] font-semibold text-crit">
            BRTS INTRUSION
          </span>
        )}
      </div>

      {/* data strip */}
      <div className="num grid grid-cols-3 divide-x divide-border border-t border-border bg-panel text-[10px]">
        <Cell label="VEH" value={String(feed.vehicleCount)} />
        <Cell label="SPD" value={`${feed.avgSpeed} km/h`} />
        <Cell label="QUEUE" value={`${feed.queueLength} m`} />
      </div>
    </Wrapper>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-2 py-1">
      <div className="text-[9px] tracking-wider text-muted-foreground">{label}</div>
      <div className="font-semibold">{value}</div>
    </div>
  );
}
