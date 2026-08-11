# Surat Command Hub

Build a real-time traffic command-centre dashboard for "TrafficSense Surat" — 

an adaptive traffic management system for Surat City Police, built for a 

smart-city hackathon (E-Rakshak 2026). This is a mission-control style 

interface used by traffic control room operators to monitor junctions, 

signal timing, BRTS corridor violations, and infrastructure bottlenecks 

across the city in real time.

## VISUAL DIRECTION

Dark, high-contrast "control room" aesthetic — think air traffic control 

or a city-ops center, not a generic SaaS dashboard. Deep charcoal/navy 

background (#0B1120 or similar), NOT pure black. Use a restrained accent 

palette: electric cyan/teal for live/active data, amber for warnings, 

red for critical alerts (BRTS intrusions, gridlock), green for optimized/

healthy status. Data should feel alive — subtle pulse animations on live 

indicators, smooth number transitions on KPI counters, not static cards. 

Typography: a technical monospace or semi-condensed sans (like JetBrains 

Mono or Inter) for data/numbers to reinforce the "instrumentation" feel, 

paired with a clean sans for labels. Avoid rounded, soft, consumer-app 

styling — this should feel precise, dense with information, and 

authoritative, like software a police control room would actually trust.

## LAYOUT — Single-page command centre with these zones:

1. **Top bar**: System status strip — total junctions online, active 

   BRTS violations count (red badge, pulses if >0), current city-wide 

   average congestion index, live clock, connection status indicator.

2. **Left panel — City Map** (largest zone, ~55% width):

   - Interactive map (Leaflet-style) of Surat with junction markers

   - Markers color-coded by congestion level (green/amber/red) with 

     size/glow indicating severity

   - BRTS corridor drawn as a distinct highlighted lane/route overlay 

     (dashed cyan line) running through the city, with intrusion 

     incidents shown as red pulsing markers directly on the corridor

   - Clicking a junction opens a detail drawer (see #4)

   - Toggle for heatmap overlay mode showing recurring bottleneck zones

3. **Right panel — Live KPI stack** (~25% width):

   - Cards for: Avg wait time reduction (%), Vehicles processed/hour, 

     Active signal-optimizer interventions, Lane-discipline violations 

     today, BRTS intrusion count today

   - Each KPI shows a small sparkline trend (Recharts) and a "vs static 

     timer baseline" comparison badge (e.g. "+28% throughput vs fixed 

     timing" in green) — this baseline comparison is core to the pitch, 

     make it prominent

   - Recharts line chart: real-time queue length per major junction, 

     multi-line, last 30 min, auto-scrolling

4. **Junction detail drawer** (slides in from right when a map marker 

   is clicked):

   - Live camera feed placeholder (video element or static frame with 

     "LIVE" badge)

   - Per-lane density bars with queue length + arrival rate numbers

   - Before/after signal cycle comparison: current adaptive cycle vs 

     what a static timer would be running, shown as two mini timeline 

     bars

   - "What-if" toggle: simulate switching this junction back to fixed 

     timing, showing projected congestion increase (pulls from your 

     SUMO simulation results)

5. **Bottom panel — Alerts & Predictive Recommendations feed**:

   - Scrolling timestamped feed, two visually distinct alert types:

     - Real-time alerts (red/amber): BRTS intrusions, lane violations, 

       sudden congestion spikes — each with junction name, timestamp, 

       severity

     - Predictive recommendations (distinct teal/purple card style, 

       clearly separated from reactive alerts): "Junction X shows 

       recurring PM bottleneck — recommend dynamic lane reallocation" 

       with confidence score and supporting mini-chart. This section 

       should look analytically distinct from the reactive alerts — 

       it's your key differentiator, don't bury it in the same list style.

   - Filter tabs: All / Violations / BRTS / Predictions

6. **Header action**: "Export Report" button opening a modal with 

   PDF/CSV/JSON export options and a date-range picker.

## TECHNICAL REQUIREMENTS

- React with functional components and hooks

- Structure data flow assuming WebSocket live updates — build with mock 

  data now but structure state management (useState/useReducer or a 

  simple store) so real WebSocket events can slot in cleanly later, 

  e.g. a single `useTrafficData()` hook that currently returns mocked 

  streaming data but is the single integration point

- Use Recharts for all charts/sparklines

- Component structure should be modular: MapPanel, KPIPanel, 

  JunctionDrawer, AlertsFeed, ExportModal, TopStatusBar — separate files

- Fully responsive down to tablet width (control rooms often use 

  large tablets); can degrade gracefully below that

- Include realistic mock data for 6-8 Surat junctions (use real-sounding 

  names like Udhna Darwaja, Ring Road, Adajan, Piplod, Varachha) with 

  varying congestion states, at least one active BRTS intrusion, and 

  2-3 predictive recommendations already populated so the UI doesn't 

  look empty on first load

## TONE

This is a serious public-infrastructure tool being pitched to police and 

municipal officials, not a consumer product. Prioritize clarity, 

information density, and trustworthiness over playfulness. Every number 

on screen should look like it means something.

## ADDITIONAL PAGE — CCTV Surveillance View

Add a second page/route: "Surveillance" accessible via a sidebar or top-nav 

tab alongside the main Command Centre dashboard (introduce a left sidebar 

with icons for: Command Centre, Surveillance, Reports if one doesn't 

already exist from the main layout).

### Layout — Multi-camera grid with live annotation overlay:

1. **Camera grid** (main content area):

   - Grid of camera feed tiles (start with 6-9 tiles, responsive grid — 

     3x3 on desktop, 2x2 on tablet), one per junction

   - Each tile shows: junction name label, LIVE badge with pulsing red 

     dot, feed placeholder (static frame/video element is fine for mock)

   - Overlaid on each feed (as absolutely-positioned SVG/div elements 

     over the frame, simulating CV annotation output):

     - Bounding boxes around detected vehicles, color-coded by type 

       (car/bus/two-wheeler/truck) — thin, technical-looking boxes with 

       small confidence % labels, like real YOLO output overlays

     - Lane polygons drawn as semi-transparent colored zones

     - BRTS corridor zone highlighted distinctly (cyan/dashed outline) 

       — if a vehicle bounding box overlaps this zone, both the box AND 

       the zone outline flash red to simulate an intrusion being caught 

       live

     - Small data strip at bottom of each tile: vehicle count, avg 

       speed estimate, queue length — updating numbers (mocked)

   - Clicking a tile expands it to a focused single-camera view (modal 

     or full-width panel) with a larger feed, full lane-by-lane 

     breakdown, and a mini event log specific to that camera 

     ("14:32:07 — BRTS intrusion detected, 2-wheeler, 4.2s duration")

2. **Right sidebar in Surveillance view — Detection Event Log**:

   - Real-time scrolling log of raw detection events across all cameras, 

     more granular/technical than the main dashboard's alert feed — 

     this is the "under the hood" view. Format like a technical log: 

     timestamp, camera ID, event type (vehicle entry/exit, violation, 

     intrusion), object class, confidence score

   - Filter by camera and event type

3. **Top bar within this page**: 

   - Camera health status (X/Y cameras online, color-coded dots)

   - Toggle: "Show detection overlays" on/off (so operator can see raw 

     clean feed vs annotated feed)

   - Toggle: "Show BRTS zones only" — dims all other overlays to focus 

     purely on corridor monitoring

### Visual/technical notes:

- This page should feel more raw and technical than the Command Centre 

  — it's the operator-level "ground truth" view, while Command Centre 

  is the executive/summary view. Slightly more monospace, slightly more 

  data-dense, less polished chart styling, more terminal/log aesthetic 

  in the event feed.

- Keep the same dark base theme and color language (cyan=live/normal, 

  amber=warning, red=violation/intrusion) for visual consistency with 

  the main dashboard — an operator should never be confused about what 

  a color means across pages.

- Mock the same 6-8 Surat junctions used in the Command Centre page so 

  data feels connected across both views, not like two disconnected demos.

- Structure this page's mock data through the same `useTrafficData()` 

  hook pattern (or a sibling `useCameraFeeds()` hook) so it's a clean 

  integration point for real vision-service WebSocket events later.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/aa990517-c209-431f-963c-22cf20e86d4f).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
