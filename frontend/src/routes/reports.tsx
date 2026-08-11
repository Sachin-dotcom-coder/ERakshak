import { createFileRoute } from "@tanstack/react-router";
import { Reports } from "@/components/traffic/Reports";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Reports — TrafficSense Surat" },
      {
        name: "description",
        content:
          "Generate and export adaptive-vs-static performance reports, BRTS enforcement logs and junction summaries for Surat City Police.",
      },
      { property: "og:title", content: "Reports — TrafficSense Surat" },
      {
        property: "og:description",
        content:
          "Junction performance summaries and exportable enforcement reporting for the TrafficSense Surat control room.",
      },
    ],
  }),
  component: Reports,
});
