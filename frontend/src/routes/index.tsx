import { createFileRoute } from "@tanstack/react-router";
import { CommandCentre } from "@/components/traffic/CommandCentre";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Command Centre — TrafficSense Surat" },
      {
        name: "description",
        content:
          "Real-time adaptive traffic command centre for Surat City Police: junction congestion, BRTS corridor intrusions, signal optimisation and predictive recommendations.",
      },
      { property: "og:title", content: "Command Centre — TrafficSense Surat" },
      {
        property: "og:description",
        content:
          "Mission-control dashboard monitoring Surat junctions, BRTS corridor violations and adaptive signal performance in real time.",
      },
    ],
  }),
  component: CommandCentre,
});
