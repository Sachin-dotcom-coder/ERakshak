import { createFileRoute } from "@tanstack/react-router";
import { Surveillance } from "@/components/traffic/Surveillance";

export const Route = createFileRoute("/surveillance")({
  head: () => ({
    meta: [
      { title: "CCTV Surveillance — TrafficSense Surat" },
      {
        name: "description",
        content:
          "Operator-level multi-camera surveillance grid with live CV detection overlays, BRTS corridor zones and a raw detection event log.",
      },
      { property: "og:title", content: "CCTV Surveillance — TrafficSense Surat" },
      {
        property: "og:description",
        content:
          "Multi-camera junction monitoring with vehicle detection overlays and BRTS intrusion capture for Surat City Police.",
      },
    ],
  }),
  component: Surveillance,
});
