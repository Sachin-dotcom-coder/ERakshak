# Person B — Simulation & Algorithm Lead
## `signal-optimizer/` — Detailed Task Breakdown (ERH26_PS_08)

This is your complete build guide for the `signal-optimizer/` folder, aligned to the
team's shared contract and day-by-day plan, with the six extra features folded in.

---

## 1. Your Folder, Expanded

The original structure gets a few new files to hold the extra features cleanly —
each feature gets its own module instead of bloating `max_pressure.py`.

```
signal-optimizer/
├── max_pressure.py                # Core adaptive signal-timing algorithm
├── webster_formula.py             # Alternate/backup timing model
├── confidence.py                  # NEW — sensor confidence scoring (weather/visibility)
├── prediction.py                  # NEW — short-horizon congestion forecasting (linear regression)
├── event_modes.py                 # NEW — mode profiles (festival/school/office/weekend/rain)
├── priority.py                    # NEW — BRTS + emergency vehicle priority logic
├── explain.py                     # NEW — decision-reasoning generator
├── sumo/
│   ├── network.net.xml
│   ├── routes.rou.xml
│   ├── fixed_timer.sumocfg
│   ├── adaptive_timer.sumocfg
│   └── traci_runner.py
├── green_wave.py                  # Multi-junction coordination
└── requirements.txt
```

---

## 2. Core Responsibility Recap

You own **all signal-timing intelligence**: turning per-lane density/queue data
(from Person A) into a signal decision, validating it in SUMO before it's ever
claimed as a real improvement, and eventually coordinating multiple junctions.

Your only inputs are Person A's event JSON (the shared contract) and, later,
weather/time-of-day context. Your only output is a signal decision object that
Person C's backend consumes and forwards to Person D's dashboard.

---

## 3. Updated Output Contract

Extend the team's original decision output so Persons C and D can show the new
features without needing a second round-trip:

```json
{
  "junction_id": "junction_01",
  "timestamp": "2026-07-08T10:15:32Z",
  "recommended_cycle_time_sec": 38,
  "phase": "NS_green",
  "confidence": 0.62,
  "mode": "office_hours",
  "predicted_congestion_5min": "rising",
  "brts_priority_triggered": false,
  "emergency_priority_triggered": false,
  "reason": "NS approach queue (14 vehicles) exceeds EW (5); confidence lowered to 0.62 due to rain — held cycle change to +8s instead of full recompute."
}
```

Share this with Person C on Day 1 — it's a strict superset of the original
contract (nothing you had is removed, so nothing breaks).

---

## 4. Day-by-Day Plan (yours)

### Day 1 — Independent build against mocks
- Get SUMO network + routes running for one test junction (`network.net.xml`,
  `routes.rou.xml`). Confirm the **fixed-timer baseline** runs end-to-end via
  `fixed_timer.sumocfg` — no adaptive logic yet.
- Write a mock version of Person A's event feed (a JSON file or generator
  matching their contract) so you're not blocked waiting for real CV output.
- Stub out `confidence.py`, `prediction.py`, `event_modes.py`, `priority.py`,
  `explain.py` with function signatures and fake return values, so `max_pressure.py`
  can call them immediately and you fill in real logic Day 2.

### Day 2 — Wire in real logic
- Implement the **max-pressure algorithm** in `max_pressure.py`, consuming
  live density from Person A once ready (mock until then).
- Implement **confidence scoring** (Section 5) and **congestion prediction**
  (Section 6) for real — these directly modulate the max-pressure output.
- Implement **event modes** (Section 7) as a config-driven parameter swap.
- Run adaptive vs. fixed-timer comparison in SUMO via `traci_runner.py`.

### Day 3 — Integration + differentiators
- Integrate with Person A's real event stream directly into the TraCI loop —
  this is your "camera → simulated signal response" live demo.
- Implement **BRTS + emergency priority** (Section 8) — this is a strong
  demo moment (a bus/ambulance appears, signal reacts visibly in SUMO).
- Build `green_wave.py` — multi-junction coordination across 2–3 signals.
- Wire `explain.py` (Section 9) into every output so Person D can render it.

### Day 4+ — Polish
- Finalize the before/after SUMO chart (fixed timer vs. your adaptive system) —
  this is your team's strongest slide.
- Edge cases: sensor dropout, all-lanes-empty, conflicting priority requests
  (BRTS + emergency at the same junction at once — emergency should win).
- Be ready to explain the full chain, not just your layer.

---

## 5. Feature — Confidence Score (Weather/Visibility Awareness)

**Goal:** don't let noisy sensor input (rain, fog, glare, occlusion) cause
erratic signal swings. Person A's CV pipeline should expose some visibility/
detection-confidence signal per frame or per event — if they haven't defined
this yet, agree it with them Day 1 as an addition to their event contract, e.g.:

```json
"detection_confidence": 0.55,
"weather_flag": "rain"
```

**Logic (`confidence.py`):**
- Combine Person A's per-event detection confidence with a weather multiplier
  (rain/fog/night → lower trust) into a single `confidence` score in [0,1].
- If `confidence` is below a threshold (e.g. 0.6):
  - Cap how much the recommended cycle time can change from the current
    cycle in one step (e.g. max ±8s instead of a full recompute).
  - Blend the live density reading with a **historical average** for that
    junction/time-of-day (weight the historical average more heavily as
    confidence drops — a simple linear blend is enough: `final = conf * live + (1-conf) * historical`).
- Always pass the `confidence` value through to the output contract so the
  dashboard can show "acting cautiously" states.

**SUMO validation:** simulate a "rain" scenario (inject noise into detector
input) and confirm your system degrades gracefully — no wild cycle swings —
versus the fixed-timer baseline, which won't change at all. This contrast is
worth showing.

---

## 6. Feature — Congestion Prediction (Linear Regression)

**Goal:** forecast whether a junction is trending toward congestion in the
next few minutes, not just react to the current queue.

**Logic (`prediction.py`):**
- Maintain a short rolling window of recent queue-length readings per lane
  (e.g. last 5–10 samples, ~1 reading every 10–30s depending on Person A's
  publish rate).
- Fit a simple linear regression of `queue_length` vs. `time` over that
  window (least squares on x = timestamp offset, y = queue length — `numpy.polyfit`
  degree 1 is enough, no need for a full ML library).
- Use the slope to classify trend: `"rising"`, `"falling"`, or `"stable"`
  (threshold the slope, e.g. > +0.5 veh/min = rising).
- Optionally extrapolate the fitted line ~5 minutes forward to get a
  predicted queue length, and feed that (not just the current reading) into
  the max-pressure decision — so a junction that's clearly trending up gets
  a slightly longer green *before* it's visibly gridlocked.
- Expose `predicted_congestion_5min` in the output contract.

**SUMO validation:** compare "reacts only to current queue" vs. "reacts to
predicted trend" on a scenario with a sudden inflow — the predictive version
should show lower peak queue length. This is a clean before/after number for
`docs/sumo_results.md`.

---

## 7. Feature — Event Mode (Festival / School / Office / Weekend / Rain)

**Goal:** different traffic patterns need different algorithm parameters, not
different algorithms — keep this as a config layer, not a rewrite.

**Logic (`event_modes.py`):**
- Define a mode profile as a small config dict per mode, e.g.:

```python
MODES = {
    "office_hours":  {"max_green": 60, "min_green": 15, "pressure_weight": 1.0},
    "school_hours":  {"max_green": 45, "min_green": 20, "pressure_weight": 0.8},  # more predictable, shorter cycles, prioritize pedestrian clearance
    "weekend":       {"max_green": 50, "min_green": 15, "pressure_weight": 0.9},
    "festival":      {"max_green": 90, "min_green": 20, "pressure_weight": 1.3},  # heavier, less predictable flows
    "rain":          {"max_green": 55, "min_green": 20, "pressure_weight": 0.7},  # ties into confidence.py — more caution
}
```

- Mode selection can be: manual override (dashboard toggle Person D builds),
  scheduled (time-of-day/day-of-week rules), or flagged externally (festival
  calendar, weather API/flag from Person A). Start with manual + scheduled;
  external triggers are a stretch goal.
- `max_pressure.py` reads the active mode's parameters instead of hardcoded
  constants — this is a one-line lookup, not a branch per mode.
- Expose `mode` in the output contract so the dashboard can show which
  profile is active.

**SUMO validation:** run the same junction under `office_hours` vs. `festival`
parameters with a heavier route file for the festival scenario — show the
mode-aware system holds up better than a single fixed profile.

---

## 8. Feature — BRTS Bus Priority + Emergency Vehicle Priority

Two related but distinct priority mechanisms — implement them together in
`priority.py` since they share the same "interrupt the normal cycle" pathway,
but emergency always outranks BRTS.

**BRTS priority:**
- Person A's event contract already includes `brts_violation` — extend the
  ask to also flag **BRTS vehicle present and waiting** (not just intrusion),
  e.g. `"brts_waiting": true, "brts_wait_time_sec": 40`.
- When a BRTS bus is waiting past a short threshold (e.g. 20s), boost that
  approach's pressure score in `max_pressure.py` so its green comes sooner —
  don't hard-force an immediate change (that can strand cross-traffic), bias
  the next decision cycle toward it instead.

**Emergency vehicle priority:**
- Person A flags an emergency vehicle detection, e.g.
  `"emergency_vehicle": {"detected": true, "approach": "north", "lane_id": "lane_1"}`.
- This **overrides everything else immediately**: force the approach's
  signal to green (a genuine interrupt, not a biased score, since minutes
  matter), hold it long enough for the vehicle to clear (estimate via
  typical junction crossing time or vehicle speed if Person A provides it),
  then resume normal adaptive logic.
- For `green_wave.py`: if you have multi-junction coordination working, cascade
  the emergency green to the next 1–2 junctions along the vehicle's path —
  a real "green corridor," and a strong demo moment.
- Conflict rule: if both BRTS and emergency are triggered at the same
  junction, emergency wins; BRTS's boosted pressure is just delayed to the
  next cycle.

**SUMO validation:** inject a single high-priority vehicle into a congested
scenario, show its transit time drop dramatically vs. the fixed-timer
baseline (this is an easy, visually convincing number).

---

## 9. Feature — Explainable Decisions

**Goal:** every signal decision should carry a plain-English reason, not just
a number, so Person D can surface it in the dashboard's alerts/KPI panel.

**Logic (`explain.py`):**
- Build the reason string from the same variables that fed the decision —
  don't compute it separately, or it can drift from the real logic. Cheapest
  approach: a small template picked by which factor dominated the decision,
  filled in with the actual numbers, e.g.:
  - Normal case: `"NS approach queue ({n} vehicles) exceeds EW ({m}); cycle extended to {t}s."`
  - Low confidence: `"...; confidence lowered to {c} due to {weather}, so change capped at +{delta}s."`
  - Rising prediction: `"...; queue trend rising (predicted +{p} vehicles in 5 min), green extended pre-emptively."`
  - BRTS: `"BRTS bus waiting {w}s on {approach}; priority given next cycle."`
  - Emergency: `"Emergency vehicle detected on {approach}; forced green corridor."`
- Priority order for which reason to surface if multiple apply: emergency >
  BRTS > confidence/weather caution > prediction > baseline max-pressure —
  pick the most specific/urgent one as the headline reason, but you can
  return the full list of contributing factors too if Person D wants detail.
- This is what fills the `reason` field in the Section 3 output contract.

---

## 10. Testing Checklist Before Demo

- [ ] Fixed-timer baseline runs in SUMO, unmodified, as your control.
- [ ] Adaptive (max-pressure) beats fixed-timer on throughput/avg wait — this
      is your headline chart in `docs/sumo_results.md`.
- [ ] Confidence-capping visibly prevents wild swings under a simulated
      "rain/noisy sensor" scenario.
- [ ] Predictive mode reduces peak queue length vs. reactive-only mode on a
      sudden-inflow scenario.
- [ ] At least two event modes (e.g. `office_hours` vs `festival`) produce
      visibly different, sensible behavior on the same junction.
- [ ] A BRTS bus waiting gets green sooner than an equivalent car would.
- [ ] An emergency vehicle gets an immediate green corridor with a clear
      before/after transit-time number.
- [ ] Every decision object includes a non-empty, accurate `reason` string.
- [ ] Full output contract (Section 3) is what Person C's backend actually
      receives — confirm with them, don't assume.

---

## 11. What to Hand Off to Whom

- **Person A:** needs to add `detection_confidence`, `weather_flag`,
  `brts_waiting`/`brts_wait_time_sec`, and `emergency_vehicle` fields to
  their event contract — flag this to them Day 1, it's the one dependency
  that blocks Sections 5 and 8 if it slips.
- **Person C:** gets the extended output contract in Section 3 — confirm
  their DB schema (`timing_logs` table) has columns for `confidence`, `mode`,
  `predicted_congestion_5min`, and `reason` so nothing gets dropped.
- **Person D:** the `reason` string and `mode` are the two fields most worth
  surfacing prominently in the dashboard — they're what make the demo look
  "intelligent" rather than just "a number changed."