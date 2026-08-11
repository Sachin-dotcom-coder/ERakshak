# E-Rakshak Signal Optimizer --- How to Improve It Without Adding Many New Detection Features

## 1. Objective

The current Signal Optimizer already has a strong architecture:

``` text
Camera / Vision Telemetry
        ↓
Confidence + Weather Conditioning
        ↓
Historical Blending
        ↓
Short-Horizon Prediction
        ↓
Max-Pressure Decision
        ↓
Priority Handling
        ↓
Webster Cycle Calculation
        ↓
Green-Wave Coordination
        ↓
Explainability + Actuation
```

The key improvement strategy should **not** be to make the vision system
detect dozens of new things.

Instead:

> **Keep the detection contract small and reliable, and make the
> optimizer extract much more intelligence from the same telemetry over
> time.**

The current input already contains per-lane density, queue length,
speed, detection confidence, weather, BRTS waiting information,
emergency-vehicle information, and BRTS violation information. These are
sufficient to build a considerably stronger controller if the downstream
decision logic is improved.

------------------------------------------------------------------------

# 2. Current Detection Contract

The current system receives approximately:

``` json
{
  "junction_id": "junction_01",
  "timestamp": "2026-08-11T11:30:00Z",

  "lanes": {
    "lane_NS_1": {
      "density": 14,
      "queue_length": 11,
      "speed_mps": 2.1
    },
    "lane_NS_2": {
      "density": 12,
      "queue_length": 9,
      "speed_mps": 2.4
    },
    "lane_EW_1": {
      "density": 5,
      "queue_length": 3,
      "speed_mps": 5.2
    },
    "lane_EW_2": {
      "density": 4,
      "queue_length": 2,
      "speed_mps": 5.8
    }
  },

  "detection_confidence": 0.88,
  "weather_flag": "clear",

  "brts_waiting": false,
  "brts_wait_time_sec": 0,
  "brts_approach": null,

  "emergency_vehicle": {
    "detected": false,
    "approach": null,
    "lane_id": null,
    "vehicle_speed_mps": null
  },

  "brts_violation": false
}
```

You do **not** need to dramatically expand this.

The improvements below mostly use:

-   existing queue length
-   existing density
-   existing speed
-   existing confidence
-   existing weather
-   existing timestamps
-   previous observations
-   previous signal decisions
-   historical traffic patterns

That means most improvements are **algorithmic**, not detection-heavy.

------------------------------------------------------------------------

# 3. Improvement Philosophy

There are four major ways to make the optimizer better:

## A. Better understanding of current traffic

Instead of simply using:

``` text
queue = 20
```

derive:

``` text
queue = 20
queue growth = +4
queue acceleration = +1.5
speed = falling
pressure = high
```

from the same measurements.

------------------------------------------------------------------------

## B. Better prediction

Instead of only:

``` text
Linear regression → 5-minute queue
```

use the existing time series more intelligently.

------------------------------------------------------------------------

## C. Better control decisions

Instead of:

``` text
Choose maximum pressure
```

consider:

``` text
pressure
+ queue growth
+ predicted pressure
+ starvation prevention
+ phase-switching cost
+ downstream congestion
+ priority
```

------------------------------------------------------------------------

## D. Better learning from historical data

The optimizer can learn:

``` text
Monday 8:00 AM
Tuesday 8:00 AM
Wednesday 8:00 AM
...
```

without requiring the camera to detect anything new.

This is probably the **highest-value direction**.

------------------------------------------------------------------------

# 4. Improvement #1 --- Add Queue Growth Rate

## Current system

The current predictor stores queue measurements and fits a linear
regression over a rolling window.

That is good, but the controller should also explicitly calculate:

``` text
queue growth rate
```

For example:

``` text
t0 → 10 vehicles
t1 → 12
t2 → 15
t3 → 19
```

The queue is not merely large.

It is **growing rapidly**.

Calculate:

``` text
growth_rate =
(current_queue - previous_queue) / Δt
```

For example:

``` text
19 - 15 = +4 vehicles
```

If measurements arrive every 30 seconds:

``` text
growth_rate = 4 / 30
            = 0.133 vehicles/sec
```

or:

``` text
8 vehicles/minute
```

------------------------------------------------------------------------

## Why this helps

Consider two approaches:

``` text
Approach A:
queue = 20
growth = +0.1 veh/min

Approach B:
queue = 20
growth = +8 veh/min
```

A basic max-pressure controller sees:

``` text
20 vs 20
```

But these situations are completely different.

Approach B is approaching congestion much faster.

------------------------------------------------------------------------

## Recommended metric

Add internally:

``` text
queue_growth_rate
```

You do **not** need the CV system to detect anything new.

It is calculated from previous queue observations.

------------------------------------------------------------------------

# 5. Improvement #2 --- Add Queue Acceleration

Queue growth rate tells you whether the queue is increasing.

Queue acceleration tells you whether the increase itself is becoming
faster.

Example:

``` text
10
11
13
17
```

Growth:

``` text
+1
+2
+4
```

The queue is accelerating.

Calculate:

``` text
acceleration =
current_growth_rate - previous_growth_rate
```

This can be useful for detecting sudden traffic surges.

------------------------------------------------------------------------

## Example

Suppose:

``` text
Normal:
queue = 10
growth = +1/min

Sudden inflow:
queue = 15
growth = +6/min
acceleration = +5/min²
```

The controller can react before the queue becomes enormous.

------------------------------------------------------------------------

# 6. Improvement #3 --- Use Queue + Speed Together

Queue length alone is insufficient.

Speed provides additional information from the same detector.

Consider:

``` text
Case A:
queue = 20
speed = 8 m/s

Case B:
queue = 20
speed = 1 m/s
```

Case B is much more congested.

Therefore create an internal:

``` text
congestion_score
```

using existing variables.

For example:

``` text
normalized_queue
normalized_speed_reduction
queue_growth
```

Conceptually:

``` text
CongestionScore =
    w1 * QueueScore
  + w2 * SpeedCongestionScore
  + w3 * GrowthScore
```

The exact weights should be calibrated through simulation rather than
arbitrarily fixed.

------------------------------------------------------------------------

# 7. Improvement #4 --- Normalize Everything

A major improvement is to avoid comparing raw values directly.

Suppose:

``` text
queue = 20
density = 25
speed = 2
```

These quantities have different units and scales.

Normalize them.

For example:

``` text
QueueScore = queue / queue_capacity
```

and:

``` text
SpeedCongestion =
1 - (current_speed / free_flow_speed)
```

Then values become comparable.

Example:

``` text
QueueScore = 0.80
SpeedCongestion = 0.75
GrowthScore = 0.65
```

Now the optimizer can combine them safely.

------------------------------------------------------------------------

# 8. Improvement #5 --- Make Max-Pressure More Intelligent

The current controller primarily uses the differential:

``` text
upstream queue - downstream queue
```

That is a good baseline.

But you can create an enhanced pressure score:

``` text
EnhancedPressure =
    QueuePressure
  + GrowthBonus
  + PredictionBonus
  + StarvationBonus
  + PriorityBonus
  - SwitchingPenalty
```

Conceptually:

``` text
                Queue
                  │
                  ↓
             Base Pressure
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
     Growth   Prediction  Starvation
        │         │         │
        └─────────┼─────────┘
                  ↓
           Priority Bonus
                  ↓
        Switching Penalty
                  ↓
        Final Phase Score
```

This can dramatically improve behavior without changing the detection
system.

------------------------------------------------------------------------

# 9. Improvement #6 --- Add Predicted Pressure

The current predictor predicts queues.

Instead of only asking:

> "Which approach has the highest queue now?"

ask:

> "Which approach will have the highest pressure soon?"

For each approach:

``` text
CurrentQueue
PredictedQueue
```

Then calculate:

``` text
CurrentPressure
PredictedPressure
```

For example:

``` text
NS:
current pressure = 20
predicted pressure = 31

EW:
current pressure = 24
predicted pressure = 25
```

A naive controller might choose EW.

A predictive controller can recognize:

``` text
NS is about to become significantly worse.
```

Therefore:

``` text
FuturePressure =
α * CurrentPressure
+
(1-α) * PredictedPressure
```

This gives the controller a tunable balance between reactive and
proactive control.

------------------------------------------------------------------------

# 10. Improvement #7 --- Replace the Single Linear Prediction With an Ensemble

The current system uses rolling-window linear regression.

That is simple and explainable, which is good.

But traffic is not always linear.

Example:

``` text
10 → 11 → 12 → 13 → 14
```

Linear regression works well.

But:

``` text
10 → 11 → 12 → 20 → 25
```

may represent a sudden surge.

Instead of replacing linear regression completely, use multiple simple
predictors:

``` text
Predictor 1: Linear trend
Predictor 2: Moving average
Predictor 3: Exponential moving average
Predictor 4: Historical same-time value
```

Then combine them.

Example:

``` text
Prediction =
    0.35 * LinearPrediction
  + 0.20 * MovingAverage
  + 0.20 * EMA
  + 0.25 * HistoricalPrediction
```

The weights should be determined from validation data.

This remains computationally lightweight.

------------------------------------------------------------------------

# 11. Improvement #8 --- Add Historical Traffic Profiles

This is one of the biggest improvements you can make.

The camera already gives:

``` text
queue
density
speed
```

Store them over time.

You can build profiles such as:

``` text
Monday 08:00
Monday 08:05
Monday 08:10

Tuesday 08:00
Tuesday 08:05
...
```

Eventually the optimizer learns:

``` text
Monday morning → NS usually heavy
Friday evening → EW usually heavy
Festival → both directions surge
```

No new detection feature is required.

------------------------------------------------------------------------

# 12. Historical Baseline

For each:

``` text
junction
approach
day-of-week
time-of-day
mode
```

store:

``` text
average_queue
average_speed
average_density
average_growth
```

Then compare the live value against the historical expectation.

Example:

``` text
Historical NS queue at 08:30 = 12

Current NS queue = 21
```

Calculate:

``` text
Anomaly = Current - Historical
        = 21 - 12
        = +9
```

Now the optimizer knows:

> This is not normal traffic for this time.

That can trigger stronger predictive control.

------------------------------------------------------------------------

# 13. Improvement #9 --- Detect Traffic Anomalies

Using existing measurements, calculate:

``` text
z_score =
(current_value - historical_mean)
/
historical_std
```

If:

``` text
z > 2
```

the traffic is unusually high.

You could classify:

``` text
normal
elevated
high anomaly
extreme anomaly
```

This is useful for:

-   accidents
-   unexpected events
-   road closures
-   sudden inflows
-   unusual congestion

You don't necessarily need to detect the accident itself.

The optimizer can detect:

> "Traffic behavior is abnormal."

That is already useful.

------------------------------------------------------------------------

# 14. Improvement #10 --- Add Phase Starvation Prevention

Pure max-pressure can repeatedly select the same approach.

Example:

``` text
NS → green
NS → green
NS → green
NS → green
```

Meanwhile:

``` text
EW vehicles
EW vehicles
EW vehicles
```

are waiting.

Even if EW has lower pressure, it should eventually receive service.

Add:

``` text
starvation_time
```

This is not a new detection feature.

It is simply:

``` text
time_since_last_green_for_phase
```

Then:

``` text
StarvationBonus =
f(waiting_time)
```

For example:

``` text
waiting < 20 sec → 0
20–40 sec → small bonus
40–60 sec → medium bonus
>60 sec → large bonus
```

This prevents one direction from being ignored indefinitely.

------------------------------------------------------------------------

# 15. Improvement #11 --- Add Minimum Service Guarantees

Instead of allowing a phase to potentially wait indefinitely:

``` text
Every phase must receive service within X seconds
```

For example:

``` text
max_phase_starvation = 90 sec
```

If:

``` text
EW_waiting_time > 90 sec
```

the controller forces consideration of EW.

This is especially useful for fairness.

------------------------------------------------------------------------

# 16. Improvement #12 --- Add Hysteresis

A traffic controller should not constantly switch because two pressures
are almost equal.

Suppose:

``` text
NS pressure = 21.0
EW pressure = 20.8
```

Then:

``` text
NS
```

wins.

Next measurement:

``` text
NS = 20.7
EW = 21.0
```

Now EW wins.

You can get:

``` text
NS → EW → NS → EW → NS
```

This is signal thrashing.

Instead require a meaningful advantage:

``` text
NewPhasePressure >
CurrentPhasePressure + switching_threshold
```

Example:

``` text
threshold = 3
```

Then:

``` text
NS = 21
EW = 22
```

does not immediately switch.

But:

``` text
NS = 21
EW = 28
```

does.

This creates stability.

------------------------------------------------------------------------

# 17. Improvement #13 --- Add Phase Switching Cost

Changing phases has a cost:

``` text
yellow
all-red clearance
vehicle lost time
driver confusion
```

The controller should account for this.

Define:

``` text
SwitchingPenalty
```

Then:

``` text
FinalScore =
Pressure
-
SwitchingPenalty
```

If the new phase only has slightly higher pressure, don't switch.

If the new phase has dramatically higher pressure, switch.

This works especially well together with hysteresis.

------------------------------------------------------------------------

# 18. Improvement #14 --- Use Minimum and Maximum Green Intelligently

The current system already has mode-specific minimum and maximum green
values.

Improve this by making green duration depend on demand.

Instead of:

``` text
NS → 40 sec
```

calculate:

``` text
GreenDuration =
base_green
+ queue_component
+ growth_component
+ predicted_component
```

Then clamp:

``` text
min_green ≤ GreenDuration ≤ max_green
```

For example:

``` text
Base = 25 sec
Queue bonus = 8 sec
Growth bonus = 5 sec
Prediction bonus = 4 sec

Green = 42 sec
```

This keeps the system explainable.

------------------------------------------------------------------------

# 19. Improvement #15 --- Use Saturation / Demand Instead of Only Queue

Webster's formula already uses:

``` text
v_i / s_i
```

where:

``` text
v_i = flow
s_i = saturation flow
```

You can estimate flow from existing observations.

If you have timestamps and vehicle counts:

``` text
vehicles_seen / time_interval
```

gives an approximate arrival rate.

Therefore you don't necessarily need a new detector.

Example:

``` text
30 vehicles entered in 60 seconds

flow ≈ 1800 veh/hour
```

This can make the Webster calculation more responsive.

------------------------------------------------------------------------

# 20. Improvement #16 --- Estimate Arrival Rate

Maintain:

``` text
arrival_rate
```

from existing queue/count telemetry.

For example:

``` text
t0 → 20
t1 → 23
t2 → 27
```

The increase can indicate incoming demand.

Use:

``` text
arrival_rate
```

to distinguish:

``` text
large queue but decreasing
```

from:

``` text
large queue and increasing rapidly
```

Those require different control decisions.

------------------------------------------------------------------------

# 21. Improvement #17 --- Estimate Queue Clearance Rate

Similarly, calculate:

``` text
clearance_rate
```

when the phase is green.

Example:

``` text
Queue:
30 → 25 → 19 → 12 → 5
```

This tells you how quickly that approach is being served.

Then the controller can estimate:

``` text
time_to_clear
```

approximately:

``` text
queue / clearance_rate
```

Example:

``` text
queue = 20
clearance = 4 veh/min

time_to_clear ≈ 5 min
```

This is useful for green duration decisions.

------------------------------------------------------------------------

# 22. Improvement #18 --- Estimate Time-To-Congestion

Using:

``` text
queue
growth_rate
capacity
```

estimate when an approach could reach a congestion threshold.

Example:

``` text
Current queue = 15
Growth = 3 vehicles/min
Critical queue = 30
```

Then:

``` text
TimeToCritical =
(30 - 15) / 3
= 5 minutes
```

Now the controller can prioritize an approach that isn't currently the
worst but is rapidly approaching a critical state.

------------------------------------------------------------------------

# 23. Improvement #19 --- Add Downstream Congestion Awareness

Max-pressure already considers downstream queues.

Make this more explicit.

Suppose:

``` text
North incoming queue = 30
North downstream queue = 28
```

Giving more green to North might simply push vehicles into a blocked
road.

Therefore define:

``` text
DownstreamPenalty
```

and reduce pressure when the receiving lane is nearly saturated.

Conceptually:

``` text
EffectivePressure =
UpstreamDemand
-
DownstreamCongestion
```

This helps prevent:

> **"Solving one queue by creating another queue."**

This is one of the strongest reasons max-pressure control is useful, and
it can be made more robust with better downstream weighting.

------------------------------------------------------------------------

# 24. Improvement #20 --- Add Spillback Protection

A particularly important extension is detecting when a queue is
approaching the physical capacity of the road segment.

You already have:

``` text
queue length
```

So define:

``` text
queue_occupancy =
current_queue / estimated_max_queue
```

Then:

``` text
queue_occupancy > 0.8
```

can be considered dangerous.

At:

``` text
queue_occupancy > 0.95
```

the controller should strongly avoid feeding more vehicles into that
downstream segment.

This can be implemented entirely from existing queue telemetry if road
capacity is configured.

------------------------------------------------------------------------

# 25. Improvement #21 --- Make Weather Affect More Than Confidence

Currently weather primarily reduces detection confidence and constrains
cycle changes.

You can also use it to modify controller behavior.

For example:

``` text
Rain:
    lower aggressiveness
    larger minimum green
    smaller cycle changes
    stronger safety margin
```

The important idea is:

> Weather should affect the control policy, not only the sensor
> confidence.

You already have the weather flag, so no new CV feature is needed.

------------------------------------------------------------------------

# 26. Improvement #22 --- Confidence-Aware Decision Making

The current system blends live and historical data based on confidence.

Take this further.

If:

``` text
confidence = 0.95
```

use:

``` text
mostly live traffic
```

If:

``` text
confidence = 0.50
```

use:

``` text
live + historical + temporal smoothing
```

If:

``` text
confidence = 0.20
```

consider freezing aggressive changes and relying more heavily on
historical values.

You can define:

``` text
confidence bands
```

such as:

``` text
0.80–1.00 → normal adaptive mode
0.60–0.80 → cautious mode
0.40–0.60 → heavily smoothed mode
<0.40 → fallback mode
```

This gives the controller graceful degradation.

------------------------------------------------------------------------

# 27. Improvement #23 --- Add Temporal Smoothing

Raw CV measurements can fluctuate:

``` text
20
23
19
24
21
25
```

A controller shouldn't interpret every fluctuation as real traffic
change.

Use:

### Moving Average

``` text
Q_smooth =
(Q_t + Q_t-1 + ... + Q_t-k) / (k+1)
```

or:

### Exponential Moving Average

``` text
EMA_t =
αQ_t + (1-α)EMA_(t-1)
```

EMA is particularly useful because it gives more importance to recent
measurements while remaining lightweight.

------------------------------------------------------------------------

# 28. Improvement #24 --- Add Confidence-Weighted Smoothing

Combine the two ideas.

If confidence is high:

``` text
α = high
```

If confidence is low:

``` text
α = low
```

Therefore:

``` text
High confidence
→ react quickly

Low confidence
→ smooth aggressively
```

This is much better than using a single fixed smoothing factor.

------------------------------------------------------------------------

# 29. Improvement #25 --- Add Adaptive Hysteresis

Instead of using one fixed switching threshold:

``` text
threshold = 3
```

make it depend on confidence.

Example:

``` text
High confidence:
threshold = 2

Low confidence:
threshold = 5
```

Why?

When sensors are unreliable, don't allow small noisy differences to
trigger a phase switch.

------------------------------------------------------------------------

# 30. Improvement #26 --- Add Phase Lock / Minimum Green Completion

Never let the optimizer change phases too aggressively.

For example:

``` text
Current phase has been green for 5 sec
```

Even if another phase has slightly higher pressure:

``` text
DO NOT SWITCH
```

until the minimum green is completed.

After minimum green:

``` text
switch only if competing pressure is sufficiently higher
```

This combines:

``` text
minimum green
+
hysteresis
+
switching penalty
```

and creates much more stable control.

------------------------------------------------------------------------

# 31. Improvement #27 --- Improve Emergency Handling

The current system performs emergency hard preemption.

You can improve it without additional detection features.

Once:

``` text
emergency detected
approach known
speed known
```

estimate:

``` text
ETA = distance / speed
```

If distance is not currently available, use the existing emergency
approach and speed with configured approach-distance information.

Then downstream junctions can prepare based on estimated arrival.

This makes the green-wave emergency corridor more coordinated.

------------------------------------------------------------------------

# 32. Improvement #28 --- Make BRTS Priority More Intelligent

The current rule is roughly:

``` text
if BRTS waits > 20 sec:
    add pressure
```

Instead of a simple threshold, use a smooth priority function.

For example:

``` text
BRTS_Bonus = f(wait_time)
```

where:

``` text
wait = 10 sec → almost no bonus
wait = 20 sec → small bonus
wait = 40 sec → medium bonus
wait = 60 sec → strong bonus
```

This prevents a sudden discontinuity at exactly 20 seconds.

Again, no additional detection is required.

------------------------------------------------------------------------

# 33. Improvement #29 --- Learn the Best BRTS Priority Threshold

Instead of assuming:

``` text
20 sec
```

is optimal, evaluate:

``` text
10 sec
20 sec
30 sec
40 sec
```

in SUMO.

Measure:

``` text
BRTS waiting time
general traffic delay
total throughput
```

Then choose the threshold that provides the best overall tradeoff.

This is a major opportunity because you already have SUMO.

------------------------------------------------------------------------

# 34. Improvement #30 --- Build a Multi-Objective Controller

Instead of optimizing only pressure, define the system's objectives
explicitly.

For example:

``` text
Objective =
    traffic throughput
  - vehicle delay
  - queue length
  - phase switching
  - BRTS delay
  - emergency delay
```

Then assign weights:

``` text
Score =
w1 * throughput
- w2 * delay
- w3 * queue
- w4 * switching
- w5 * BRTS delay
- w6 * emergency delay
```

Emergency should not merely be another weighted term if safety requires
hard preemption. It can remain a separate override.

This creates a cleaner distinction:

``` text
Hard constraints:
    emergency safety
    minimum green
    clearance
    signal safety

Optimization objectives:
    delay
    throughput
    queues
    BRTS
    fairness
```

------------------------------------------------------------------------

# 35. Improvement #31 --- Use a Rule + Score Architecture

Don't immediately replace the entire controller with a complex neural
network.

A strong architecture is:

``` text
                ┌─────────────────────┐
                │ Hard Safety Rules   │
                └─────────┬───────────┘
                          ↓
                Emergency / Clearance
                          ↓
                ┌─────────────────────┐
                │ Optimization Score │
                └─────────┬───────────┘
                          ↓
                Pressure + Prediction
                + Fairness + Switching
                          ↓
                ┌─────────────────────┐
                │ Phase Selection     │
                └─────────────────────┘
```

This is easier to:

-   debug
-   explain
-   test
-   demonstrate to judges
-   validate in SUMO

------------------------------------------------------------------------

# 36. Improvement #32 --- Add a Safety Constraint Layer

Before sending a decision to the traffic light, validate:

``` text
Is minimum green satisfied?
Is yellow clearance satisfied?
Is all-red clearance satisfied?
Is the proposed duration within bounds?
Is the phase transition legal?
Is an emergency override active?
```

Only then:

``` text
ACTUATE
```

This creates:

``` text
Decision
   ↓
Safety Validator
   ↓
Actuator
```

The optimizer should never directly send an unsafe transition.

------------------------------------------------------------------------

# 37. Improvement #33 --- Add Decision Confidence

The current system has sensor confidence.

You can additionally calculate:

``` text
decision_confidence
```

Example:

``` text
sensor confidence = 0.90
pressure difference = very large
prediction confidence = high
historical agreement = high

decision confidence = 0.94
```

But:

``` text
sensor confidence = 0.55
NS pressure = 21
EW pressure = 20
prediction disagreement = high

decision confidence = 0.48
```

This can be shown on the dashboard.

It makes the system more transparent.

------------------------------------------------------------------------

# 38. Improvement #34 --- Detect Prediction Uncertainty

Do not output only:

``` text
predicted queue = 30
```

Also estimate:

``` text
prediction uncertainty
```

For example:

``` text
Predicted queue = 30 ± 4
```

Then:

``` text
high uncertainty
→ conservative control

low uncertainty
→ aggressive predictive control
```

With linear regression, uncertainty can be estimated from historical
residuals.

This does not require new detection features.

------------------------------------------------------------------------

# 39. Improvement #35 --- Back-Test Every Controller Change

Because SUMO is already part of the architecture, use it as your
laboratory.

For every change:

``` text
Controller A
vs
Controller B
```

run identical traffic seeds.

Compare:

``` text
Average waiting time
Average queue
Maximum queue
Throughput
Travel time
Stops
Phase switches
BRTS delay
Emergency travel time
```

Do not judge improvements from one simulation run.

Use:

``` text
multiple random seeds
multiple traffic demand levels
multiple weather/confidence conditions
```

------------------------------------------------------------------------

# 40. Improvement #36 --- Create a Scenario Matrix

Build standardized test scenarios.

## Scenario 1 --- Normal

``` text
Balanced traffic
```

## Scenario 2 --- Peak NS

``` text
NS >> EW
```

## Scenario 3 --- Peak EW

``` text
EW >> NS
```

## Scenario 4 --- Sudden Inflow

``` text
Traffic suddenly increases
```

## Scenario 5 --- Dissipating Queue

``` text
Traffic decreases
```

## Scenario 6 --- Rain / Low Confidence

``` text
confidence decreases
```

## Scenario 7 --- BRTS

``` text
BRTS waiting
```

## Scenario 8 --- Emergency

``` text
Emergency vehicle
```

## Scenario 9 --- Emergency + BRTS

``` text
Both occur simultaneously
```

## Scenario 10 --- Downstream Blockage

``` text
Receiving lane becomes congested
```

## Scenario 11 --- Repeated Oscillation

``` text
NS/EW pressure repeatedly crosses
```

## Scenario 12 --- Multi-Junction Corridor

``` text
J1 → J2 → J3
```

This lets you prove that every improvement solves a specific failure
mode.

------------------------------------------------------------------------

# 41. Improvement #37 --- Optimize the Weights Automatically

Suppose your enhanced pressure is:

``` text
Score =
w1 * Queue
+ w2 * Growth
+ w3 * Prediction
+ w4 * Starvation
- w5 * Switching
```

Don't randomly choose:

``` text
w1 = 1
w2 = 0.5
w3 = 0.3
...
```

Use SUMO to search for good values.

For example:

``` text
w_growth:
0.1
0.2
0.3
0.4
0.5
```

Run simulations and measure:

``` text
total_delay
throughput
queue
switches
```

Then choose the best configuration.

You can perform:

``` text
Grid Search
```

first.

Later:

``` text
Bayesian Optimization
```

if necessary.

------------------------------------------------------------------------

# 42. Improvement #38 --- Use Reinforcement Learning Only Later

You could eventually make the system RL-based, but it should **not** be
the first improvement.

The existing Max-Pressure controller is:

-   explainable
-   deterministic
-   easy to test
-   computationally cheap
-   easy to demonstrate

First make the rule-based controller excellent.

Then, if you have enough simulation data, use RL to learn:

``` text
phase selection
green duration
weight tuning
```

A good hybrid architecture could be:

``` text
RL
 ↓
suggest weights / parameters

Safety + Max Pressure
 ↓
validate decision

Traffic Light
```

This is safer and easier to explain than letting an RL agent directly
control everything.

------------------------------------------------------------------------

# 43. Improvement #39 --- Add Automatic Parameter Calibration

Parameters currently include things like:

``` text
minimum green
maximum green
pressure weights
BRTS threshold
cycle delta cap
prediction window
```

Put them in a configuration layer:

``` yaml
controller:
  hysteresis_threshold: 3
  max_starvation_sec: 90
  smoothing_alpha: 0.35

prediction:
  window: 10
  horizon: 10

priority:
  brts_wait_threshold: 20

safety:
  max_cycle_delta: 8
```

Then you can tune the controller without rewriting code.

------------------------------------------------------------------------

# 44. Improvement #40 --- Add Adaptive Parameter Selection

Go one step further.

The controller can select parameters based on traffic conditions.

For example:

``` text
Stable traffic:
    more smoothing
    less aggressive prediction

Rapidly changing traffic:
    less smoothing
    stronger growth weighting
    stronger prediction
```

So the controller becomes:

``` text
Traffic state
     ↓
Select controller parameters
     ↓
Run optimizer
```

This is still much simpler than full machine learning.

------------------------------------------------------------------------

# 45. Improvement #41 --- Improve Explainability

The current explainability module already gives reasons such as:

``` text
Queue trend rising
Emergency detected
BRTS priority
Rain reduced confidence
```

Make the explanation more quantitative.

Instead of:

> "NS has high pressure."

produce:

> "NS selected because pressure is 31.4 versus EW 14.2. NS queue is
> rising at 4.2 vehicles/min and predicted to reach 29 vehicles in 5
> minutes."

This is much stronger for:

-   dashboards
-   judges
-   debugging
-   audit trails

------------------------------------------------------------------------

# 46. Improvement #42 --- Add a Decision Trace

Store every decision:

``` json
{
  "timestamp": "...",
  "selected_phase": "NS_green",

  "pressure": {
    "NS": 31.4,
    "EW": 14.2
  },

  "queue": {
    "NS": 22,
    "EW": 8
  },

  "growth_rate": {
    "NS": 4.2,
    "EW": 0.4
  },

  "prediction": {
    "NS": 29,
    "EW": 10
  },

  "starvation": {
    "NS": 5,
    "EW": 42
  },

  "confidence": 0.91,

  "switching_penalty": 2.0,

  "final_scores": {
    "NS": 36.1,
    "EW": 17.4
  },

  "reason": "..."
}
```

This makes the optimizer much easier to inspect.

------------------------------------------------------------------------

# 47. Improvement #43 --- Add Controller Health Metrics

The optimizer itself should be monitored.

Track:

``` text
decision frequency
average decision latency
prediction error
sensor confidence
phase switches/minute
fallback count
emergency override count
BRTS priority count
```

This answers:

> Is the optimizer itself behaving correctly?

rather than only:

> Is traffic moving?

------------------------------------------------------------------------

# 48. Improvement #44 --- Measure Prediction Error

Every prediction should eventually be compared with reality.

If:

``` text
predicted queue = 30
actual queue = 34
```

then:

``` text
error = +4
```

Track:

``` text
MAE
RMSE
MAPE
```

where appropriate.

For example:

``` text
MAE = mean(|prediction - actual|)
```

Then compare:

``` text
Linear Regression
vs
EMA
vs
Historical Profile
vs
Ensemble
```

This tells you whether the prediction module is actually helping.

------------------------------------------------------------------------

# 49. Improvement #45 --- Make the Optimizer Self-Evaluating

Every decision should eventually answer:

``` text
Did my decision improve traffic?
```

For example:

``` text
Decision:
NS green for 42 sec

Before:
NS queue = 25

After:
NS queue = 10

Result:
queue reduced by 15
```

Or:

``` text
Decision:
NS green for 42 sec

Before:
NS queue = 25

After:
NS queue = 31

Result:
decision was ineffective
```

This historical feedback can later be used to tune the controller.

------------------------------------------------------------------------

# 50. Recommended Final Architecture

A stronger version of your current system could be:

``` text
                 ┌─────────────────────┐
                 │ Vision Telemetry    │
                 │                     │
                 │ Queue               │
                 │ Density             │
                 │ Speed               │
                 │ Confidence          │
                 │ Emergency           │
                 │ BRTS                │
                 │ Weather             │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Data Conditioning   │
                 │                     │
                 │ Smoothing           │
                 │ Confidence Blend    │
                 │ Normalization       │
                 └──────────┬──────────┘
                            ↓
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
       Trend Engine    Historical      Anomaly Engine
             │           Profile             │
             ↓              ↓                ↓
             └──────────────┼────────────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Traffic State       │
                 │                     │
                 │ Queue Growth        │
                 │ Queue Acceleration  │
                 │ Congestion          │
                 │ Arrival Rate        │
                 │ Clearance Rate      │
                 │ Time-to-Congestion  │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Enhanced Pressure   │
                 │                     │
                 │ Base Pressure       │
                 │ + Growth            │
                 │ + Prediction        │
                 │ + Fairness          │
                 │ + Priority          │
                 │ - Switching Cost    │
                 │ - Downstream Risk   │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Safety Layer        │
                 │                     │
                 │ Emergency           │
                 │ Min Green           │
                 │ Yellow              │
                 │ All-Red             │
                 │ Max Green           │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Phase Selection     │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Green Duration      │
                 │ Webster + Demand    │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Green Wave          │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Explainability      │
                 │ + Decision Trace     │
                 └──────────┬──────────┘
                            ↓
                    SUMO / Controller
```

------------------------------------------------------------------------

# 51. What I Would Implement First

Do **not** implement all 45 improvements at once.

A practical roadmap is:

## Phase 1 --- Make the existing controller smarter

Implement:

1.  Queue growth rate
2.  Queue acceleration
3.  Temporal smoothing
4.  Predicted pressure
5.  Hysteresis
6.  Switching penalty
7.  Starvation prevention
8.  Downstream congestion penalty

These require almost no additional detection.

------------------------------------------------------------------------

## Phase 2 --- Add historical intelligence

Implement:

9.  Historical traffic profiles
10. Historical anomaly detection
11. Time-of-day traffic baseline
12. Prediction error tracking
13. Adaptive confidence handling

Still no significant new detection requirements.

------------------------------------------------------------------------

## Phase 3 --- Improve optimization

Implement:

14. Multi-objective scoring
15. Automatic weight tuning
16. Adaptive BRTS threshold
17. Adaptive green duration
18. Spillback protection

Use SUMO heavily here.

------------------------------------------------------------------------

## Phase 4 --- Multi-junction intelligence

Implement:

19. Better green-wave offsets
20. Traffic-aware offsets
21. Emergency corridor ETA
22. Downstream coordination
23. Corridor-level pressure

------------------------------------------------------------------------

## Phase 5 --- Advanced ML

Only after the above works:

24. Prediction ensemble
25. Bayesian parameter optimization
26. RL-assisted parameter tuning
27. Learned traffic-state representation

Do not jump to RL before you have a strong baseline.

------------------------------------------------------------------------

# 52. The Most Important 10 Improvements

If you only have limited development time, prioritize these:

  Rank   Improvement                         New Detection Needed?
  ------ ----------------------------------- -----------------------
  1      Queue growth rate                   **No**
  2      Predicted pressure                  **No**
  3      Historical traffic profiles         **No**
  4      Hysteresis                          **No**
  5      Starvation prevention               **No**
  6      Downstream congestion penalty       **No**
  7      Temporal smoothing                  **No**
  8      Anomaly detection                   **No**
  9      Adaptive green duration             **No**
  10     SUMO-based parameter optimization   **No**

This is the key takeaway:

> **You can make the Signal Optimizer significantly more sophisticated
> without making the Computer Vision pipeline significantly more
> complicated.**

The biggest untapped source of intelligence is **time**.

You already have:

``` text
queue(t)
density(t)
speed(t)
confidence(t)
phase(t)
timestamp(t)
```

From these, you can derive:

``` text
queue growth
queue acceleration
arrival rate
clearance rate
congestion score
predicted queue
predicted pressure
time-to-congestion
historical deviation
phase starvation
phase stability
switching cost
prediction error
```

So instead of asking the camera to detect 30 additional things, make the
optimizer **remember, compare, predict, and learn from the same small
set of measurements**.

------------------------------------------------------------------------

# 53. Recommended Final KPI Dashboard

For demonstrating the improved optimizer, show:

## Traffic

``` text
Average Waiting Time
Average Queue Length
Maximum Queue Length
Average Travel Time
Throughput
Number of Stops
Queue Clearance Time
```

## Controller

``` text
Phase Switches / Hour
Average Green Duration
Prediction MAE
Decision Confidence
Fallback Count
Average Decision Latency
```

## Priority

``` text
BRTS Average Wait
BRTS Maximum Wait
Emergency Corridor Travel Time
Emergency Stops
```

## Network

``` text
Junction Throughput
Corridor Travel Time
Green-Wave Progression Rate
Downstream Spillback Events
```

Then compare:

``` text
Fixed Timer
        vs
Current Max Pressure
        vs
Improved Signal Optimizer
```

That gives you a much stronger experimental story than simply saying
that the optimizer "uses AI."

------------------------------------------------------------------------

# 54. Final Recommended Version

The ideal E-Rakshak Signal Optimizer should therefore remain based on
the existing small telemetry contract:

``` text
               SMALL CV CONTRACT
                      ↓
       ┌───────────────────────────┐
       │ Queue                     │
       │ Density                   │
       │ Speed                     │
       │ Confidence                │
       │ Weather                   │
       │ BRTS                      │
       │ Emergency                 │
       └─────────────┬─────────────┘
                     ↓
             TEMPORAL INTELLIGENCE
                     ↓
       ┌───────────────────────────┐
       │ Trends                    │
       │ Growth                    │
       │ Acceleration              │
       │ Historical patterns       │
       │ Anomalies                 │
       │ Predictions               │
       └─────────────┬─────────────┘
                     ↓
             SMART CONTROL
                     ↓
       ┌───────────────────────────┐
       │ Max Pressure              │
       │ Predicted Pressure        │
       │ Fairness                  │
       │ Hysteresis                │
       │ Switching Cost            │
       │ Spillback Protection      │
       │ Priority                  │
       └─────────────┬─────────────┘
                     ↓
             SAFETY CONSTRAINTS
                     ↓
              SIGNAL DECISION
                     ↓
             GREEN-WAVE CONTROL
                     ↓
             SUMO VALIDATION
                     ↓
            AUTOMATIC CALIBRATION
```

**The main architectural change is therefore not "detect more." It is
"derive more."**

That is the direction I would recommend for E-Rakshak: keep the vision
system lightweight and make the Signal Optimizer increasingly
**temporal, predictive, adaptive, fair, safety-constrained, and
self-evaluating**.
