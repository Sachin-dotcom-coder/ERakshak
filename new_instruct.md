# E-Rakshak — Reports & Metrics Section: Redesign Spec

**Scope:** the `REPORTS` tab of the Command Center (left-rail item 3).
**Goal:** replace "nice-looking numbers" with metrics a traffic control operator, a shift supervisor, and a city official can actually act on, while keeping the current visual language exactly.

---

## 0. How to read this document

| Part | What it covers |
| :--- | :--- |
| 1 | Audit of the current Reports page (what is weak, what is broken) |
| 2 | Design system extracted from the screenshots (the "must match" rules) |
| 3 | Information architecture and page layout |
| 4 | Widget-by-widget spec (KPIs, charts, heatmap, tables) |
| 5 | Secondary tabs (Signals, Enforcement, Incidents, System Health) |
| 6 | Metric definitions and formulas |
| 7 | Interaction, states, accessibility |
| 8 | Data contract (what the backend must expose) |
| 9 | Prioritised roadmap |

---

## 1. Audit of the current page

### 1.1 Who uses Reports, and what they need to know

| Persona | Question they bring to this page |
| :--- | :--- |
| **Control room operator** | What went wrong in the last hours, where, and did my action help? |
| **Shift supervisor** | What do I hand over to the next shift? What is still open? |
| **Traffic engineer** | Which junctions need re-timing or physical changes, and is adaptive control actually beating fixed timing? |
| **Enforcement officer** | Where and when do violations cluster, and are challans being issued correctly? |
| **City commissioner / SMC** | Is the system delivering value? What is the trend week over week? |

The Command tab answers "what is happening right now". **Reports must answer "what happened, why, compared to what, and what do we do next".** Right now it mostly shows a snapshot with no comparison.

### 1.2 Widget-by-widget verdict

| Current widget | Problem | Verdict |
| :--- | :--- | :--- |
| `JUNCTIONS 22 monitored` | A static number that never changes. | Remove (move to page subtitle). |
| `CITY CONGESTION 36 avg index` | An average hides the problem. Three junctions at 80 and nineteen at 20 average to "fine". No trend, no comparison, index is undefined to the user. | Replace with distribution-aware metric. |
| `BRTS VIOLATIONS 43 today` / `LANE VIOLATIONS 17 today` | A raw count with no rate, no baseline, no hour context. Two cards for one concept. | Merge into one Enforcement card with rate and trend. |
| `AI RECS PENDING 12` | Useful as an attention counter, but it is a navigation badge, not a metric. | Move to the section header of the recommendations table. |
| `WAIT REDUCTION 31.4% vs fixed timing` | The most important claim of the product, shown with no method, no confidence, no baseline definition. Anyone can challenge it. | Keep, but promote to an "Adaptive Benefit" panel with method and range. |
| `WAIT TIME COMPARISON` chart | **Renders empty** in the screenshot. Single junction only (J001). | Fix and redesign. |
| `THROUGHPUT COMPARISON` bars | Y-axis labels are clipped (`000`, `500`). Top 8 only. The same figures appear in the junction table. No indication which bar is adaptive vs fixed. Throughput is demand-driven, so a higher bar is not "better". | Replace. |
| `VIOLATION TREND (30 min)` | Two lines with no legend. 30-minute window is too short for a *Reports* page. The orange spike at the end dominates and is unexplained. | Redesign with a legend, longer ranges, annotations. |
| `HOURLY CONGESTION HEATMAP` | Shows only 7 of 22 junctions. Cells are almost binary (dark or red), which looks like a fixed pattern at hours 8-10 and 17-20, not measured data. Legend defines four levels but only three colours appear. Junction names do not match the other widgets. | Redesign. |
| `AI RECOMMENDATION ENGINE` table | Four near-identical rows ("Install physical concrete channelizers..."). Suggested action text is truncated. No evidence, no expected impact, no confidence, no age. **Severity colours are inverted: CRITICAL is green, HIGH is red.** | Redesign. |
| `JUNCTION PERFORMANCE REPORT` table | `IF FIXED TIMING +21%` is ambiguous (21% worse? 21% better?). No LOS grade, no trend, no violations, no health. | Redesign. |

### 1.3 Bugs and inconsistencies to fix regardless of redesign

1. Severity badge colours are wrong (`CRITICAL` rendered green). Critical must be red, High amber.
2. Wait-time chart renders no data.
3. Throughput chart Y-axis labels are cut off (`000` instead of `1,000`).
4. Junction naming is inconsistent across widgets (`Udhna`, `Udhna Darwaja`, `Kharwarnagar Circle`, `J001`). Use **one junction registry** (`id`, `display_name`, `short_name`, `zone`) and render the same name everywhere.
5. Heatmap legend lists four colours but the grid uses three; "moderate" gray and "low" dark gray are nearly indistinguishable.
6. Time axis labels are inconsistent (`00 am`, `01:12 am`). Use 24-hour `HH:mm` everywhere (this is an Indian operations room).
7. Truncated text with no way to read the rest.
8. Line chart has two series and no legend.
9. `+21%` style deltas have no sign convention. Define: green = better than baseline, red = worse, and always say "vs what".

---

## 2. Design system (must match existing UI)

> Values below are visually estimated from the screenshots. **Verify against the real CSS variables / Tailwind config** and map each to an existing token rather than hard-coding.

### 2.1 Principles observed in the current UI

1. **Near-black, flat, low-chrome.** No gradients, no shadows, no glassmorphism. Depth comes from 1px borders.
2. **Neutrals carry the data; colour is reserved for attention.** White and gray for normal state. Amber and red appear only when something needs a human.
3. **Monospace for labels and numbers, sans-serif (Inter-like) for sentences.** Labels are uppercase and letter-spaced.
4. **Generous padding, large rounded cards,** consistent gutters.
5. **Every card = small mono label on top, human-readable title below, content underneath.**

### 2.2 Tokens

| Token | Approx. value | Used for |
| :--- | :--- | :--- |
| `--bg-app` | `#0A0A0B` | Page background |
| `--bg-card` | `#0E0E10` | Card surface |
| `--bg-chip` | `#1A1A1D` | Icon chips, pills, table-row hover |
| `--border` | `#1C1C20` | 1px card and row borders |
| `--text-primary` | `#FFFFFF` | Titles, big numbers |
| `--text-secondary` | `#A1A1A8` | Body, table cells |
| `--text-muted` | `#6B6B73` | Mono labels, axis ticks |
| `--series-primary` | `#FFFFFF` | Adaptive / "current" series |
| `--series-baseline` | `#2E2E33` | Fixed / baseline / comparison series |
| `--attn-amber` | `#E8A838` | High, warning, highlighted line |
| `--attn-red` | `#D9534F` | Critical, violations |
| `--good-green` | `#5CB85C` | Positive deltas (improvement) only |
| `--heat-low` | `#1E1E22` | Heatmap low |
| `--heat-moderate` | `#5A5A60` | Heatmap moderate |
| `--heat-high` | `#E8A838` | Heatmap high |
| `--heat-critical` | `#D9534F` | Heatmap critical |

### 2.3 Typography

| Role | Style |
| :--- | :--- |
| Card eyebrow label | Mono, uppercase, ~11-12px, letter-spacing ~0.14em, `--text-muted` |
| Card title | Sans, semibold, ~20px, `--text-primary` |
| KPI value | Mono, ~36px, semibold, `--text-primary` |
| KPI sub-label | Sans, ~14px, `--text-secondary` |
| Table header | Mono, uppercase, ~11px, letter-spacing ~0.14em, `--text-muted` |
| Table body | Sans 15px for names, **mono for numbers** |
| Badges | Mono, uppercase, ~11px, tinted background + 1px tinted border |
| Axis ticks | Sans/mono ~12px, `--text-muted` |

### 2.4 Component specs

**KPI card** (6 across, equal width, ~170px tall)
```
┌────────────────────────────────────────┐
│  (◉)   LABEL IN MONO CAPS              │   ◉ = 44px circular chip, --bg-chip,
│        36                              │       1px border, 20px line icon
│        sub-label  ▲ 4.2% vs last wk    │
└────────────────────────────────────────┘
```
Radius ~20px, padding ~24px, `1px solid var(--border)`.
**Addition:** a delta chip on the sub-label line (mono, 12px) and an optional 40px-high sparkline anchored bottom-right at 60% opacity.

**Chart card** radius ~24px, same border. Optional control (dropdown pill such as the existing `J001 ⌄`) sits top-right, pill radius, `--bg-chip`.

**Pill / badge**
| Variant | Text | Background | Border |
| :--- | :--- | :--- | :--- |
| Critical | `--attn-red` | red @ 12% | red @ 35% |
| High | `--attn-amber` | amber @ 12% | amber @ 35% |
| Medium | `--text-secondary` | white @ 6% | white @ 14% |
| Low | `--text-muted` | transparent | white @ 8% |
| Status solid (APPLIED, +BRTS) | `#0A0A0B` | `#FFFFFF` | none |
| Status outline (PENDING) | `--text-secondary` | transparent | white @ 18% |

**Table:** no zebra, 1px hairline row dividers, row height ~72px (compact mode ~48px), sticky mono header, hover row = `--bg-chip` @ 40%.

**Left rail:** keep as is (110px, icon over mono label, active item in rounded pill with white left indicator, `E·RAKSHAK 2026` footer).

**Sub-navigation inside Reports (new):** a row of mono-uppercase text tabs, active tab has a white 2px underline (no fill, so it does not compete with the rail).

---

## 3. Information architecture and page layout

### 3.1 Sub-tabs

```
OVERVIEW   CONGESTION   SIGNALS   ENFORCEMENT   INCIDENTS   RECOMMENDATIONS   SYSTEM HEALTH
```

`OVERVIEW` is a one-screen-plus-scroll summary in the style of the current page. The other tabs are depth views reached by clicking any widget on Overview.

### 3.2 Global filter bar (new, sticky under the page top)

```
RANGE  [ Today ][ 24h ][ 7d ][ 30d ][ Custom ]    COMPARE [ vs yesterday ⌄ ]    ZONE [ All zones ⌄ ]    CORRIDOR [ All ⌄ ]        ⟳ Live · 12s ago     ⤓ Export ⌄
```
- Styled like the existing `J001 ⌄` pill: radius full, `--bg-chip`, mono text.
- **Compare** options: `vs yesterday`, `vs same weekday last week`, `vs 7-day average`, `vs fixed-timing baseline`, `none`.
- Every widget on the page respects these filters. The filter state lives in the URL query string so views are shareable and bookmarkable.
- "Live · 12s ago" shows data freshness. If telemetry is stale (>60s) it turns amber.

### 3.3 Overview wireframe

```
┌ FILTER BAR ───────────────────────────────────────────────────────────────────────────┐
├───────────┬───────────┬───────────┬───────────┬───────────┬───────────┤
│ NETWORK   │ THROUGHPUT│ CONGESTED │ OPEN      │ ENFORCE-  │ SYSTEM    │   Row 1: 6 KPI cards
│ DELAY     │           │ JUNCTIONS │ INCIDENTS │ MENT      │ HEALTH    │
├───────────┴─────┬─────┴───────────┼─────────────────────────────────────┤
│ DELAY OVER TIME │ LEVEL OF SERVICE│ VIOLATIONS & INCIDENTS TREND        │   Row 2: 3 chart cards (equal)
│ adaptive/fixed  │ distribution    │ stacked by type, annotated          │
├─────────────────┴─────────────────┴──────────────────┬──────────────────┤
│ CONGESTION HEATMAP  (all 22 junctions × 24h)         │ TOP BOTTLENECKS  │   Row 3: 2/3 + 1/3
│                                                      │ ranked list      │
├──────────────────────────────────────────────────────┴──────────────────┤
│ ADAPTIVE BENEFIT (method, range, per-zone)                              │   Row 4: full width, short
├─────────────────────────────────────────────────────────────────────────┤
│ NEEDS ATTENTION · RECOMMENDATIONS (grouped)                             │   Row 5: table
├─────────────────────────────────────────────────────────────────────────┤
│ JUNCTION PERFORMANCE REPORT                                             │   Row 6: table
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Overview: widget specifications

Each widget lists: **purpose, data, visual, interactions, thresholds.**

### 4.1 KPI row (6 cards)

| # | Label (mono caps) | Value | Sub-label | Icon (line) | Why it matters |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `NETWORK DELAY` | `42 s` | `avg per vehicle ▼ 6% vs yesterday` | clock | The single best summary of how the network feels to a driver. |
| 2 | `THROUGHPUT` | `118k PCU` | `served today ▲ 3% vs last Sat` | arrow-through-gate | Volume actually moved, PCU-weighted so a bus is not counted as a scooter. |
| 3 | `CONGESTED JUNCTIONS` | `4 / 22` | `index ≥ 55 now · peak 7 at 18:30` | alert-triangle | Replaces the averaged "city congestion". Counts junctions that need eyes. |
| 4 | `OPEN INCIDENTS` | `3` | `1 stalled · 1 wrong-way · 1 emergency` | siren | What a supervisor must hand over. Clicking opens the Incidents tab filtered to open. |
| 5 | `VIOLATIONS` | `60` | `BRTS 43 · lane 17 · 9.4/h ▲ 12%` | shield | One enforcement number with rate and mix, instead of two separate counts. |
| 6 | `SYSTEM HEALTH` | `96.4%` | `21/22 cameras live · 1 on fallback` | activity | Operators must know whether the numbers above can be trusted. |

**Colour rules**
- Value text stays white. Colour only on the delta chip and an optional 6px status dot beside the label.
- Delta chip: green = better than the compare baseline, red = worse, gray = within ±2%.
- "Better" is metric-specific: lower delay is better, higher throughput is better (but **gray** when demand changed, since throughput is demand-driven).
- Card 3 dot: gray 0 junctions, amber 1-3, red 4+. Card 4 dot: gray 0, amber 1-2, red any critical. Card 6 dot: green ≥99%, amber 95-99%, red <95%.

**Click-through:** every card opens the relevant tab with the same filters.

**Moved out of this row:** `JUNCTIONS 22` (becomes page subtitle "22 junctions · 6 zones"), `AI RECS PENDING` (becomes the badge on the Recommendations table header and on its sub-tab), `WAIT REDUCTION` (promoted to section 4.5).

---

### 4.2 Delay Over Time (replaces the empty Wait Time chart)

- **Eyebrow:** `DELAY OVER TIME`
- **Title:** `Adaptive vs baseline · seconds per vehicle`
- **Control:** scope dropdown `All junctions ⌄` (also `Zone: South`, or a single junction). Default is the **network**, not J001.
- **Visual:** line chart, x = time (hourly buckets for 24h, daily for 7d/30d), y = seconds/vehicle.
  - White solid line = measured (adaptive).
  - Dark-gray dashed line = baseline (fixed-timing estimate, or the compare period).
  - Light fill between the lines: white @ 6% where adaptive is better, red @ 8% where worse.
  - Shaded vertical bands for AM peak (08-10) and PM peak (17-20), using `--border` colour.
- **Interactions:** hover crosshair with tooltip (adaptive, baseline, delta, vehicles served in that bucket). Click-drag to zoom range. Click a point to open the Congestion tab at that hour.
- **Empty state:** `NO DATA FOR THIS RANGE` in mono caps, with the reason (e.g. "no telemetry from J001 since 14:02").
- **Annotation markers:** small ticks on the x-axis for events (preemption, mode change, incident), hover to reveal.

### 4.3 Level of Service Distribution (replaces Throughput Comparison)

- **Eyebrow:** `LEVEL OF SERVICE`
- **Title:** `Junction-hours by LOS grade`
- **Visual:** horizontal 100% stacked bar per hour block (or a single stacked bar per day for 7d/30d). Segments A to F, with A-C in neutral grays, D in light gray, E in amber, F in red.
- **Why:** shows *how much of the day* the network spent in bad conditions, which an average cannot. "6.2% of junction-hours at LOS E/F" is a statement a commissioner can quote.
- **Interactions:** click a segment to filter the heatmap and junction table to those junction-hours.
- **Legend:** inline under the chart: `A-C Free flow · D Approaching unstable · E Unstable · F Breakdown`.

### 4.4 Violations & Incidents Trend (replaces the 30-minute violation chart)

- **Eyebrow:** `VIOLATIONS & INCIDENTS`
- **Title:** `By type · per hour`
- **Visual:** stacked bar by hour (24h) or day (7d/30d).
  - BRTS intrusion = red, lane discipline = amber, wrong-way = white, others = gray.
  - Overlay a dashed horizontal threshold line at **15/hour** (the engine's BRTS-encroachment rule). Hours above it are annotated `ESCALATED`.
  - Incident markers (stall, emergency) as small diamonds above the bars.
- **Legend is mandatory** (the current chart has none).
- **Interactions:** hover tooltip breaks the hour down by junction (top 3). Click a bar to open the Enforcement tab at that hour.
- **Rule:** if the right-most bucket is incomplete (current hour), draw it hatched so a partial bar is not read as a drop.

---

### 4.5 Congestion Heatmap (redesigned)

- **Eyebrow:** `CONGESTION HEATMAP`
- **Title:** `All junctions × hour · congestion index (0-100)`
- **Rows:** **all 22 junctions**, grouped by zone with a small zone label divider, sorted by worst peak by default (toggle: alphabetical / zone / current).
- **Columns:** 0-23 in `HH` format. Current hour has a white 1px outline and a small mono `NOW` marker. Future hours are hatched/empty (not dark, so empty is distinguishable from "low").
- **Cell colour (4 steps, must match legend and be visibly distinct):**

| Level | Range | Colour |
| :--- | :--- | :--- |
| Low | 0-35 | `--heat-low` |
| Moderate | 35-55 | `--heat-moderate` |
| High | 55-75 | `--heat-high` (amber) |
| Critical | 75+ | `--heat-critical` (red) |

- **No-data cells:** dashed outline, no fill. Never silently render missing data as "low".
- **Tooltip:** junction, hour, index, avg queue (m), avg speed (km/h), vehicles, minutes above 75 in that hour.
- **Toggle (top-right pill):** `Index` / `Delay` / `Queue` / `Deviation vs typical`. **Deviation vs typical** colours cells by how much worse than that junction's own 4-week median for that hour. This surfaces abnormal congestion, which is far more actionable than "8am is busy everywhere".
- **Interactions:** click a row label to open the junction detail drawer; click a cell to open that junction at that hour.
- **Row sparkline (optional):** 7-day trend of daily peak index at the row end.

### 4.6 Top Bottlenecks (new, right of heatmap)

Ranked list of the worst junctions for the selected range.

```
TOP BOTTLENECKS · TODAY
01  Kharwarnagar Circle     South       ● 142 min ≥ 75    peak 91 @ 18:20
02  Althan Tenement         South       ●  96 min ≥ 75    peak 84 @ 09:05
03  Station Circle          Central     ●  71 min ≥ 75    peak 82 @ 18:40
```
- Rank by **minutes spent in High+Critical** (persistence), not peak, because a 5-minute spike matters less than 2 hours of gridlock.
- Row = mono rank, junction name, zone, mini bar of minutes, peak time.
- Flags: `SPILLBACK`, `STARVATION`, `FALLBACK MODE` pills when applicable.
- Click opens junction detail.

### 4.7 Adaptive Benefit Panel (promotes `WAIT REDUCTION 31.4%`)

Because this is the headline value claim, it needs to survive scrutiny.

```
ADAPTIVE BENEFIT                                          METHOD: A/B WINDOWS + SUMO SHADOW
Delay reduction vs fixed timing         ▼ 31.4%   (range 26-36%, 95% CI)   based on 18 junction-days
Vehicle-hours saved today               412 h
Estimated idling emissions avoided      ≈ 1.9 t CO₂   (factor configurable in Settings)
```
- Per-zone bars underneath (South / East / Central / Outer / South West ...).
- **Required honesty features:**
  - A visible `ESTIMATED` pill.
  - Method disclosure link: how the baseline is obtained (see 6.6).
  - A confidence range, never a lone decimal.
  - Junctions with insufficient baseline coverage are labelled `NO BASELINE`, not given a made-up number.

---

### 4.8 Needs Attention: Recommendations (redesigned table)

**Header:** eyebrow `AI RECOMMENDATION ENGINE`, title `12 pending · 15 total`, filter pills `All · Operational · Infrastructure · Applied` and a sort control.

**Key changes**
1. **Group duplicates.** The four "Install bollards at BRTS entry" rows become one row: `BRTS intrusion heavy · 4 junctions (J014, J016, J017, J020)` with a chevron to expand.
2. **Two categories**, because they have different owners and time scales:
   - `OPERATIONAL` (signal timing, green wave, cycle length): can be applied in one click by the operator.
   - `INFRASTRUCTURE` (bollards, turn pockets, channelizers): creates a work request for engineering, cannot be "applied" instantly.
3. **Show the evidence.** A short trigger line makes the recommendation trustworthy.
4. **Never truncate silently.** Wrap to two lines, and open a right-side drawer for the full text.

**Columns**

| Column | Content |
| :--- | :--- |
| `SEVERITY` | Badge. **Critical = red, High = amber, Medium = neutral.** |
| `ISSUE` | Issue type (title case, not `brts intrusion heavy`). |
| `WHERE` | Junction chip(s) with display name, e.g. `J001 · Udhna Darwaja`. |
| `EVIDENCE` | One mono line: `22 intrusions/h for 3 h · threshold 15/h`. |
| `SUGGESTED ACTION` | Two-line wrapped text. |
| `EXPECTED IMPACT` | `−18% delay` / `−60% intrusions` with an `EST.` pill. |
| `CONFIDENCE` | 3-segment bar (low / med / high) plus tooltip. |
| `AGE` | `2h`, `3d`. Amber after 24h unanswered, red after 72h for Critical. |
| `STATUS` | `PENDING` (outline), `APPLIED` (solid white), `DEFERRED`, `REJECTED`. |
| `ACTIONS` | ✓ Approve, ✕ Reject (existing icons). Reject opens a one-line **reason** picker (feeds model improvement). Add `⋯` for Defer, Assign, Open junction. |

**Closing the loop (new).** Once a recommendation is `APPLIED`, the row shows a **measured outcome** after a configurable window (e.g. 7 days): `Outcome: −12% delay at J005 (expected −15%)`. This is the strongest evidence the AI engine is worth trusting, and the best data for tuning it.

**Bulk actions:** select-multiple checkbox column appears on hover; bulk approve / reject / assign.

---

### 4.9 Junction Performance Report (redesigned table)

**Eyebrow:** `JUNCTION PERFORMANCE REPORT`, **title:** `Adaptive vs baseline · 22 junctions`. Controls: search, zone filter, column chooser, CSV export.

| Column | Content | Notes |
| :--- | :--- | :--- |
| `JUNCTION` | Display name + mono `J001` underneath | Sticky first column. |
| `ZONE` | Zone | Filterable. |
| `LOS` | Letter grade badge A-F | New. Neutral for A-D, amber E, red F. |
| `CONGESTION` | Bar + index (existing style) + 24h sparkline | Keep the existing bar. |
| `AVG DELAY` | Seconds per vehicle (replaces `AVG WAIT`) | Mono. Delta vs compare beneath in 12px. |
| `P95 QUEUE` | Metres | New. Averages hide the bad cycles, the 95th percentile shows them. |
| `SATURATION` | v/c ratio, e.g. `0.87` | New. Above 0.9 turns amber, above 1.0 red. This predicts failure before it happens. |
| `THROUGHPUT` | veh/h and PCU/h (measured stop-line crossings) | Must be real counts. |
| `CYCLE FAILURES` | % of cycles where the queue did not clear on green | New. Strong sign a junction needs re-timing. |
| `VIOLATIONS` | Count today | New. |
| `MODE` | `ADAPTIVE` / `FIXED` / `FLASH` / `FALLBACK` / `MANUAL` pill | New. Operators must see which junctions are *not* adaptive right now. |
| `BRTS` | `+ BRTS` pill (existing) | Keep. |
| `ADAPTIVE GAIN` | `−21% delay` in green, with `EST.` | Replaces the ambiguous `IF FIXED TIMING +21%`. |
| `HEALTH` | 8px dot: green live, amber degraded, red offline | New. |

**Row interactions**
- Click row: opens the **Junction Detail Drawer** (section 4.10).
- Default sort: congestion descending (existing sort arrow stays).
- Sticky header, virtualised if more than 30 rows.
- Pagination not needed at 22, but must scale to 100+.

### 4.10 Junction Detail Drawer (new)

Right-side drawer, 520px, same card styling, opened from any junction reference.

```
J001 · UDHNA DARWAJA              [ADAPTIVE]  [+BRTS]  ● live          ✕
South Zone · last update 4s ago
────────────────────────────────────────────────────────────────────
 DELAY 58s ▼8%   P95 QUEUE 71m   v/c 0.87   CYCLE FAIL 14%   LOS D
────────────────────────────────────────────────────────────────────
 PER-APPROACH TABLE   (North / East / South / West)
   approach │ flow PCU/h │ queue m │ avg speed │ green split │ delay s
────────────────────────────────────────────────────────────────────
 24H INDEX LINE   (today vs typical band)
────────────────────────────────────────────────────────────────────
 SIGNAL TIMELINE  (phase bars, mode changes, preemptions)
────────────────────────────────────────────────────────────────────
 EVENTS (last 24h): violations, stalls, overrides, recommendations
────────────────────────────────────────────────────────────────────
 [ Open in Command map ]   [ Export junction report ]
```

---

## 5. Secondary tabs

### 5.1 CONGESTION

- Full heatmap with every metric toggle, 7d / 30d "typical day" mode (median per hour), and weekday vs weekend split.
- **Queue spillback log:** table of events where downstream occupancy exceeded 85% (junction, start, duration, blocked upstream junction).
- **Peak analysis cards:** peak hour, peak duration, peak-to-off-peak ratio, per zone.
- **Vehicle composition:** stacked bar by class (two-wheeler, auto, car, bus, BRTS, truck, cycle) by hour. Useful for engineers designing lane allocation, since the Indian mix is the key local factor.
- **Speed profile:** average speed by corridor by hour, with the posted limit as a reference line.

### 5.2 SIGNALS

Answers "is the controller doing its job".

| Widget | Content |
| :--- | :--- |
| **Mode timeline** | One row per junction, horizontal bar across the day coloured by mode (Adaptive white, Fixed gray, Fallback amber, Manual override red, Flash hatched). Instantly reveals who was on fallback and when. |
| **Green split utilisation** | Per junction per phase: allocated green vs used green (seconds of saturated discharge). Wasted green is a quantified retiming opportunity. |
| **Cycle length distribution** | Histogram of cycle lengths per junction vs Webster optimum. |
| **Cycle failure and starvation** | Cycles that ended with residual queue; minor phases that waited longer than the starvation limit. |
| **Priority actions** | Emergency preemptions, BRTS extensions and truncations: count, success rate, cross-street cost. |
| **Safety validator log** | Count of blocked switches (min-green lock), clamped durations, and all-red enforcement. A rising count signals an optimizer misbehaving. |
| **Manual overrides** | Operator, junction, from-mode, to-mode, duration, reason. Required for accountability. |
| **Arrival on green** (BRTS arterials) | Percentage of buses and vehicles arriving at the stop line on green. Show as a time-space diagram for the corridor (advanced, P2). |

### 5.3 ENFORCEMENT

| Widget | Content |
| :--- | :--- |
| **Violation map and ranking** | Top junctions and corridors by violations per hour, with the 15/h escalation line. |
| **By type, class, and hour** | Which vehicle classes intrude BRTS lanes and when (e.g. two-wheelers at 08:00, cars at 18:00) to plan patrols. |
| **Challan funnel** | `Detected → Auto-validated → Officer-reviewed → Issued → Paid`, with counts and drop-off percentages. |
| **Review queue** | Violations awaiting officer validation, with snapshot thumbnails and age. |
| **False-positive rate** | % of detections rejected by officers, per violation type and per camera. This is the most useful signal for retraining the model. |
| **Repeat offenders** | Plates (from ANPR) with 3+ violations in the range. Restrict visibility by role. |
| **Intrusion impact** | BRTS bus average speed during intrusion minutes vs clear minutes. Turns "43 violations" into "intrusions cost buses 4.1 km/h on this stretch". |
| **Patrol effectiveness** | Violations per hour before and after a warden assignment at a junction. |

### 5.4 INCIDENTS

| Widget | Content |
| :--- | :--- |
| **Incident log** | Time, type (stall, wrong-way, emergency, congestion event), junction, duration, status, handler. |
| **Time to clear (MTTR)** | Mean and p90 duration of stalled-vehicle incidents. |
| **Throughput lost** | From `stall_alert.throughput_loss`, summed per day and per junction. |
| **Emergency response** | Count, **detection-to-green latency** (target set in config), hold duration, recovery time to normal queue, cross-street delay cost. |
| **Incident hotspots** | Junctions with repeated stalls (road surface, bus stop placement, etc.). |
| **Shift handover summary** | Auto-generated list of open items, applied recommendations, overrides, and anomalies since shift start, with an `Export PDF` button. |

### 5.5 RECOMMENDATIONS

The full-size version of 4.8 with lifecycle filters (`Pending / Applied / Deferred / Rejected / Measured`), outcome tracking, acceptance rate by recommendation type, and a "model accuracy" chart (expected vs measured impact).

### 5.6 SYSTEM HEALTH

Operators and engineers must be able to tell "traffic is fine" from "sensor is dead".

| Widget | Content |
| :--- | :--- |
| **Camera status grid** | 22 junctions × cameras, dot per camera (live / degraded / offline), last heartbeat. |
| **Uptime** | Per camera and network, over the range. |
| **Detection confidence by lighting** | Mean confidence for `DAYLIGHT` / `NIGHT` / `RAIN` / `GLARE`. Flags junctions where night confidence collapses. |
| **Pipeline latency** | p50 / p95 for inference, event ingestion, and event-to-dashboard (target <50ms), plotted over time. |
| **Telemetry freshness** | Junctions with no event for >10s, with duration. |
| **Fallback usage** | Minutes spent on Historical-Profile or Webster-fixed fallback per junction. |
| **Calibration drift** | Homography re-projection error per camera; flag cameras that were bumped or re-aimed. |
| **Queue and bus health** | Kafka lag, Redis connectivity, DB write latency, WebSocket client count. |

---

## 6. Metric definitions

Every number on this page needs a one-line definition available on hover (`ⓘ`), and the exact formula in a docs link.

### 6.1 Delay per vehicle
Using BoT-SORT trajectories in world metres:
```
delay_i = dwell_time_in_approach_zone_i − (zone_length_m / free_flow_speed_mps)
network_delay = Σ delay_i · pcu_i  /  Σ pcu_i      (PCU-weighted mean)
```
Free-flow speed is calibrated per approach from the 90th-percentile speed of vehicles at night.

### 6.2 Congestion index (0-100)
The index must be documented and decomposable. Suggested composition:
```
index = 100 · ( 0.40·occupancy + 0.30·(1 − speed_ratio) + 0.20·delay_norm + 0.10·spillback_flag )
occupancy    = min(1, Q_m / 120)           (same constant as the TrafficMetric table)
speed_ratio  = avg_speed / free_flow_speed
delay_norm   = min(1, delay_s / 120)
```
Weights are configurable. The tooltip shows the four contributions as a mini bar, so operators learn what drives it. Bands: 0-35 Low, 35-55 Moderate, 55-75 High, 75+ Critical (existing).

### 6.3 Level of Service (signalised, HCM-style by average control delay)

| LOS | Delay (s/veh) |
| :-: | :--- |
| A | ≤ 10 |
| B | 10-20 |
| C | 20-35 |
| D | 35-55 |
| E | 55-80 |
| F | > 80 |

### 6.4 Throughput
Count of unique `track_id`s crossing a **virtual stop-line gate** per interval, weighted by PCU. This is a *measured* number. (The current `veh/h` figures such as `4,960` repeating across junctions look like capacity values; verify they are actual counts.)

### 6.5 Other core formulas

| Metric | Definition |
| :--- | :--- |
| P95 queue | 95th percentile of `queue_length_m` samples in the range. |
| Saturation (v/c) | `demand_pcu_per_h / (saturation_flow · g/C)` per approach; junction value = max approach. |
| Cycle failure | Cycle ends with ≥1 stationary vehicle (`v < 5 km/h`) in the approach at green termination. |
| Spillback minutes | Minutes where downstream lane occupancy >85%. |
| Persistence | Minutes with index ≥ 55 (High) or ≥ 75 (Critical). |
| Violation rate | Violations per hour, rolling, per junction and per corridor. |
| Intrusion impact | `bus_speed(no intrusion) − bus_speed(intrusion present)` on the corridor segment. |
| Detection-to-green latency | `t(green granted) − t(emergency_vehicle.detected = true)`. |
| MTTR | Mean `t(stall cleared) − t(stall_alert raised)`. |
| False-positive rate | `rejected_by_officer / (rejected + issued)` per violation type. |

### 6.6 Baseline for "vs fixed timing"
A comparison against fixed timing is only credible if the baseline is measured, not assumed. Use, in order of strength:
1. **A/B time windows:** run selected junctions on fixed timing for short, scheduled, matched windows (same weekday and hour), and compare.
2. **SUMO shadow replay:** replay logged demand through the fixed-timing plan in the digital twin.
3. **Historical fixed-timing data** from before deployment, normalised for demand.

Show the method on the panel. Where no valid baseline exists, show `NO BASELINE`, never a number.

---

## 7. Interaction, states, accessibility

### 7.1 Refresh model
| Data | Cadence |
| :--- | :--- |
| KPI cards, Top bottlenecks, open incidents | WebSocket push, throttled to 5s |
| Charts and heatmap | Re-query every 60s for `Today`, no refresh for historical ranges |
| Tables | Manual refresh + 60s soft refresh without losing scroll or selection |

A subtle "Live · Ns ago" indicator replaces the need for a spinner.

### 7.2 States (every widget must define all four)

| State | Presentation |
| :--- | :--- |
| Loading | Skeleton blocks in `--bg-chip`, never layout shift |
| Empty | Mono caps `NO DATA FOR THIS RANGE` + one line of cause |
| Error | Mono caps `COULD NOT LOAD` + `Retry` pill, widget-local (one failure never blanks the page) |
| Partial/stale | Amber `STALE · 3 junctions missing` pill in the card header |

### 7.3 Drill-down map
KPI → tab → widget → junction drawer → Command map. Every junction name is a link, and the filter state travels with the user.

### 7.4 Accessibility
- Never encode meaning in colour alone. Severity badges carry text; heatmap cells show the value on hover and via keyboard focus; LOS has letters.
- Keyboard: tabbing through tabs, filters, table rows; `Enter` opens drawer; `Esc` closes.
- Contrast: `--text-muted` on `--bg-card` must still reach 4.5:1 for text above 12px; adjust if the sampled grays fall short.
- Charts expose a "view as table" toggle.
- Numbers use tabular figures (mono already satisfies this).

### 7.5 Exports and scheduled reports
`⤓ Export` menu: `Current view (PDF)`, `Table (CSV)`, `Chart (PNG)`, `Raw data (CSV/JSON)`.

**Report templates** (generated by `report_generator.py`, also schedulable by email/WhatsApp):

| Template | Audience | Cadence | Contents |
| :--- | :--- | :--- | :--- |
| Shift handover | Supervisor | Each shift end | Open incidents, overrides, applied/pending recommendations, anomalies |
| Daily operations | Control room head | Daily 06:00 | KPIs, top bottlenecks, violations, system health |
| Weekly engineering | Traffic engineers | Monday | Delay trends, cycle failures, retiming candidates, recommendation outcomes |
| Enforcement | Police | Daily/weekly | Violations by junction/class/hour, challan funnel, repeat offenders |
| Executive monthly | Commissioner | Monthly | Adaptive benefit with method, trends, incidents, uptime |

---

## 8. Data contract

### 8.1 Gaps vs the current design

The detection spec already emits per-lane `vehicle_count`, `pcu_count`, `queue_length_m`, `avg_speed_kmph`, violations, emergency and stall events. The new Reports page additionally needs:

| Need | Where it comes from | Status |
| :--- | :--- | :--- |
| Per-vehicle dwell time and delay | `tracker.py` trajectories | Add `delay_s` aggregate to lane payload |
| Stop-line crossing counts | Virtual gate in `zone_utils.py` | **New** |
| Per-approach (not just per-lane) roll-up | Lane to approach mapping | New config |
| Signal phase and mode history | `signal-optimizer` | **New** `signal_phase_log`, `signal_mode_log` |
| Green used vs allocated, cycle failure | Phase log + queue at green end | New derived |
| Preemption events with timestamps | `priority.py` | New `preemption_event` |
| Incident lifecycle (raised, acknowledged, cleared) | Stall/emergency events | New `incident` |
| Challan lifecycle and officer decisions | `report_generator.py` | New `challan` |
| Recommendation evidence, expected impact, outcome | `recommendations.py` | Extend `recommendation` |
| Baseline estimates | A/B scheduler or SUMO shadow | **New** `baseline_estimate` |
| System health samples | `health.py` heartbeats | New `system_health_sample` |
| BRTS bus speed on corridor segments | Tracker, `brts_bus` class | Aggregate |
| Bus headway / schedule adherence | External AVL or GTFS feed | Optional, external dependency |

### 8.2 Aggregation tables
Raw events stay in `TrafficMetric`. Reports should never scan raw rows for ranges beyond a few hours.

```
traffic_metric_1m     (junction_id, lane_id, ts_minute, vehicles, pcu, q_p50, q_p95, speed_avg, delay_avg, crossings, index)
traffic_metric_1h     (rollup of the above, plus los_grade, v_c, cycle_failures)
violation_hourly      (junction_id, hour, type, vehicle_class, count)
signal_mode_log       (junction_id, from_ts, to_ts, mode, source[auto|operator|fallback], operator_id?)
preemption_event      (id, junction_id, kind[emergency|brts], detected_ts, green_ts, released_ts, cross_street_delay_s)
incident              (id, junction_id, lane_id, type, raised_ts, acked_ts, cleared_ts, handler, throughput_loss)
recommendation        (id, junction_id, severity, category, issue_type, evidence_json, action, expected_impact, confidence, status, created_ts, decided_ts, decided_by, reject_reason, outcome_json)
baseline_estimate     (junction_id, window, method, delay_baseline, delay_actual, ci_low, ci_high, n_samples)
system_health_sample  (camera_id, ts, online, fps, latency_ms, mean_conf, lighting, reproj_err_px)
```

### 8.3 API endpoints

```
GET  /api/reports/summary?range=today&compare=yesterday&zone=all
GET  /api/reports/delay-series?scope=network|zone:South|junction:J001&range=...
GET  /api/reports/los-distribution?range=...
GET  /api/reports/violations?range=...&group=hour|junction|type|class
GET  /api/reports/heatmap?metric=index|delay|queue|deviation&range=...
GET  /api/reports/bottlenecks?range=...&limit=10
GET  /api/reports/adaptive-benefit?range=...
GET  /api/reports/junctions?range=...                    (table, all columns in 4.9)
GET  /api/reports/junctions/{id}                         (drawer)
GET  /api/recommendations?status=&category=&group=true
POST /api/recommendations/{id}/decision                  {action, reason?}
GET  /api/incidents?status=open|all&range=...
GET  /api/signals/mode-timeline?range=...
GET  /api/system/health?range=...
POST /api/reports/export                                 {template, range, format, recipients?}
```
All list endpoints return `generated_at` and `data_through` timestamps so the UI can show freshness honestly.

---

## 9. Prioritised roadmap

### P0: fix what is broken (days)
- Correct severity colours (Critical red, High amber, Medium neutral).
- Make the wait-time chart render, and default it to the network.
- Fix throughput axis labels, or replace the widget.
- Unify junction names via a single registry.
- Add legend to the violation chart; show 24-hour time format.
- Heatmap: show all 22 junctions, make legend match colours, distinguish no-data from low.
- Rename `IF FIXED TIMING` to `ADAPTIVE GAIN` and state the sign convention.
- Wrap instead of truncate recommendation text.

### P1: make it useful (1-3 weeks)
- Global filter bar with range, compare, zone.
- New KPI row (Network Delay, Throughput, Congested Junctions, Open Incidents, Violations, System Health).
- Delay-over-time chart with baseline; LOS distribution; stacked violations with threshold line.
- Top Bottlenecks by persistence.
- Junction table with LOS, P95 queue, saturation, cycle failures, mode, health.
- Recommendation grouping, evidence, expected impact, age, reject reasons.
- Junction detail drawer.
- Incidents tab and shift-handover export.

### P2: make it trustworthy and strategic (1-2 months)
- Adaptive Benefit panel with A/B windows and SUMO shadow baselines.
- Recommendation outcome tracking and model-accuracy chart.
- Signals tab (mode timeline, green utilisation, safety validator log).
- Enforcement funnel, false-positive tracking, intrusion impact.
- System Health tab (uptime, latency, calibration drift, confidence by lighting).
- Scheduled reports, role-based visibility.

### P3: advanced
- Time-space diagrams and arrival-on-green for BRTS corridors.
- Bus headway and schedule adherence (needs AVL/GTFS feed).
- Emissions panel with configurable factors.
- Anomaly detection ("today is 30% worse than typical for this hour") surfaced as auto-generated insight cards in the same card style.

---

## Appendix: "Is this metric worth a pixel?" checklist

Before adding any widget, it must pass all five:

1. **Decision:** Can a named persona take a specific action because of it?
2. **Comparison:** Is it shown against a baseline (time, peer, target) so it can be judged?
3. **Distribution:** Does it expose the worst cases, not just the average?
4. **Trust:** Is its definition one hover away, and does it show when data is stale or missing?
5. **Drill-down:** Does clicking it take the user closer to the cause?

*E-Rakshak Reports Section Spec, 2026*