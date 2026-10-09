# backend-api/app/reports_analytics.py
"""
reports_analytics.py — High-Fidelity Mock & Real Telemetry Analytics Engine
===========================================================================
Implements the full Reports & Metrics Redesign Specification (Section 8).
Anchored to the system's operational timeline (October 2026 / 2026-10-10),
aligning 1-to-1 with the PDF generator date ranges and Surat Smart City data contracts.
"""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models import Junction as DBJunction, Lane, TrafficMetric, Violation, Recommendation
from app.reports.periods import IST

router = APIRouter(prefix="/api/reports", tags=["reports-analytics"])

# -----------------------------------------------------------------------------
# 1. CANONICAL JUNCTION REGISTRY (22 Intersections)
# -----------------------------------------------------------------------------
CANONICAL_JUNCTIONS = [
    {
        "id": "J001",
        "name": "Udhna Darwaja",
        "short_name": "Udhna",
        "zone": "South Zone",
        "corridor": "BRTS Corridor 1",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-U01",
        "saturation_base": 0.87,
        "free_flow_speed": 45.0,
    },
    {
        "id": "J002",
        "name": "Sahara Darwaja",
        "short_name": "Sahara",
        "zone": "Ring Road",
        "corridor": "Ring Road Arterial",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-S02",
        "saturation_base": 0.92,
        "free_flow_speed": 42.0,
    },
    {
        "id": "J003",
        "name": "Majura Gate Flyover",
        "short_name": "Majura",
        "zone": "Central Surat",
        "corridor": "Ring Road Arterial",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-M03",
        "saturation_base": 0.81,
        "free_flow_speed": 48.0,
    },
    {
        "id": "J004",
        "name": "Ring Road / Delhi Gate",
        "short_name": "Delhi Gate",
        "zone": "Ring Road",
        "corridor": "Ring Road Arterial",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-D04",
        "saturation_base": 0.89,
        "free_flow_speed": 40.0,
    },
    {
        "id": "J005",
        "name": "Adajan Gam / Patia",
        "short_name": "Adajan",
        "zone": "West Zone",
        "corridor": "Hazira Link Corridor",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-A05",
        "saturation_base": 0.74,
        "free_flow_speed": 46.0,
    },
    {
        "id": "J006",
        "name": "Piplod Junction",
        "short_name": "Piplod",
        "zone": "Dumas Road",
        "corridor": "Airport Corridor",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-P06",
        "saturation_base": 0.62,
        "free_flow_speed": 55.0,
    },
    {
        "id": "J007",
        "name": "Varachha / Sardar Chowk",
        "short_name": "Varachha",
        "zone": "East Zone",
        "corridor": "Diamond Corridor",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-V07",
        "saturation_base": 0.95,
        "free_flow_speed": 38.0,
    },
    {
        "id": "J008",
        "name": "Kharwarnagar Circle",
        "short_name": "Kharwarnagar",
        "zone": "South Zone",
        "corridor": "BRTS Corridor 1",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-K08",
        "saturation_base": 0.98,
        "free_flow_speed": 40.0,
    },
    {
        "id": "J009",
        "name": "Khatodara GIDC Cross",
        "short_name": "Khatodara",
        "zone": "Industrial Corridor",
        "corridor": "GIDC Arterial",
        "on_brts": False,
        "mode": "FIXED",
        "health": "live",
        "camera_id": "CAM-K09",
        "saturation_base": 0.78,
        "free_flow_speed": 44.0,
    },
    {
        "id": "J010",
        "name": "Katargam Darwaja",
        "short_name": "Katargam",
        "zone": "North Zone",
        "corridor": "Old City Ring",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-K10",
        "saturation_base": 0.72,
        "free_flow_speed": 42.0,
    },
    {
        "id": "J011",
        "name": "Vesu VIP Road Crossing",
        "short_name": "Vesu VIP",
        "zone": "Vesu Zone",
        "corridor": "VIP Corridor",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-V11",
        "saturation_base": 0.65,
        "free_flow_speed": 52.0,
    },
    {
        "id": "J012",
        "name": "Dindoli Bridge Approach",
        "short_name": "Dindoli",
        "zone": "South-East Zone",
        "corridor": "Suburban Link",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-D12",
        "saturation_base": 0.76,
        "free_flow_speed": 45.0,
    },
    {
        "id": "J013",
        "name": "Kamrej Highway Junction",
        "short_name": "Kamrej",
        "zone": "Outer Ring Road",
        "corridor": "NH-48 Connector",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-K13",
        "saturation_base": 0.88,
        "free_flow_speed": 60.0,
    },
    {
        "id": "J014",
        "name": "Textile Market Corridor",
        "short_name": "Textile Mkt",
        "zone": "Commercial Hub",
        "corridor": "Ring Road Arterial",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-T14",
        "saturation_base": 0.94,
        "free_flow_speed": 35.0,
    },
    {
        "id": "J015",
        "name": "Palanpur Jakatnaka",
        "short_name": "Palanpur",
        "zone": "Rander Zone",
        "corridor": "West Arterial",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-P15",
        "saturation_base": 0.69,
        "free_flow_speed": 46.0,
    },
    {
        "id": "J016",
        "name": "Sarthana Jakatnaka",
        "short_name": "Sarthana",
        "zone": "East Zone",
        "corridor": "Zoo Highway",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-S16",
        "saturation_base": 0.84,
        "free_flow_speed": 48.0,
    },
    {
        "id": "J017",
        "name": "Cable Bridge Adajan Side",
        "short_name": "Cable Bridge",
        "zone": "Tapi River Crossing",
        "corridor": "River Expressway",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-C17",
        "saturation_base": 0.82,
        "free_flow_speed": 50.0,
    },
    {
        "id": "J018",
        "name": "Gopipura Main Road",
        "short_name": "Gopipura",
        "zone": "Heritage Zone",
        "corridor": "Old City Central",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-G18",
        "saturation_base": 0.60,
        "free_flow_speed": 36.0,
    },
    {
        "id": "J019",
        "name": "Bhatar Char Rasta",
        "short_name": "Bhatar",
        "zone": "Bhatar Zone",
        "corridor": "South West Arterial",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-B19",
        "saturation_base": 0.77,
        "free_flow_speed": 44.0,
    },
    {
        "id": "J020",
        "name": "Althan Tenement",
        "short_name": "Althan",
        "zone": "South Zone",
        "corridor": "Canal Corridor",
        "on_brts": True,
        "mode": "FALLBACK",
        "health": "degraded",
        "camera_id": "CAM-A20",
        "saturation_base": 0.91,
        "free_flow_speed": 42.0,
    },
    {
        "id": "J021",
        "name": "Ichhapore GIDC Cross",
        "short_name": "Ichhapore",
        "zone": "Hazira Belt",
        "corridor": "Port Heavy Freight",
        "on_brts": False,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-I21",
        "saturation_base": 0.75,
        "free_flow_speed": 52.0,
    },
    {
        "id": "J022",
        "name": "Station Circle",
        "short_name": "Station",
        "zone": "Central Surat",
        "corridor": "Railway Terminus Link",
        "on_brts": True,
        "mode": "ADAPTIVE",
        "health": "live",
        "camera_id": "CAM-S22",
        "saturation_base": 0.93,
        "free_flow_speed": 34.0,
    },
]

# Map by ID
JUNCTION_MAP = {j["id"]: j for j in CANONICAL_JUNCTIONS}

# -----------------------------------------------------------------------------
# HELPER: Compute Hourly Profile for a Junction
# -----------------------------------------------------------------------------
def get_hourly_profile(j_id: str) -> List[Dict[str, Any]]:
    """Deterministic, smooth 24-hour profile with AM peak (8-10) and PM peak (17-20)."""
    seed_val = sum(ord(c) for c in j_id)
    random.seed(seed_val)
    base_factor = 0.8 + ((seed_val % 7) * 0.05)

    profile = []
    for h in range(24):
        # Base sinusoidal flow
        time_rad = (h / 24.0) * 2 * math.pi
        base = 22.0 + 8.0 * math.sin(time_rad - 1.5)

        # AM Peak: 08:00 - 10:00
        am_boost = 0.0
        if 7 <= h <= 10:
            am_dist = abs(h - 9.0)
            am_boost = max(0.0, (1.0 - am_dist / 2.0) * 48.0)

        # PM Peak: 17:00 - 20:00
        pm_boost = 0.0
        if 16 <= h <= 21:
            pm_dist = abs(h - 18.5)
            pm_boost = max(0.0, (1.0 - pm_dist / 2.5) * 56.0)

        raw_index = (base + am_boost + pm_boost) * base_factor
        # Specific hotspot elevations for realistic demo
        if j_id in ["J008", "J020", "J022", "J002", "J014"] and (h in [9, 18, 19]):
            raw_index += 12.0

        index = min(98.0, max(8.0, raw_index))

        # Measured delay vs fixed timing baseline
        adaptive_delay = 18.0 + (index * 0.42)
        fixed_delay = adaptive_delay * (1.31 + 0.05 * math.sin(h))

        # Speed (km/h) drops under congestion
        speed = max(12.0, 50.0 - (index * 0.38))
        queue_m = round(index * 0.95 + 4.0, 1)
        vehicles = int(800 + index * 42)

        # Deviation vs typical 4-week median
        typical = index * (0.95 + 0.1 * math.sin(h * 0.5))
        deviation = round(index - typical, 1)

        profile.append({
            "hour": f"{h:02d}:00",
            "hour_num": h,
            "index": round(index, 1),
            "delay_s": round(adaptive_delay, 1),
            "baseline_delay_s": round(fixed_delay, 1),
            "queue_m": queue_m,
            "speed_kmh": round(speed, 1),
            "vehicles": vehicles,
            "deviation": deviation,
        })
    return profile


# -----------------------------------------------------------------------------
# 2. ENDPOINTS IMPLEMENTING SECTION 8 DATA CONTRACT
# -----------------------------------------------------------------------------

@router.get("/summary")
def get_reports_summary(
    range_type: str = Query("today", alias="range"),
    compare: str = Query("yesterday"),
    zone: str = Query("all"),
    corridor: str = Query("all"),
):
    """
    Returns the 6 KPI cards strictly adhering to Section 4.1 of new_instruct.md.
    Anchored to October 2026 / 2026-10-10.
    """
    # 24-point sparkline for each KPI
    spark_delay = [48, 42, 38, 35, 34, 38, 45, 54, 58, 52, 44, 42, 40, 41, 43, 49, 56, 62, 60, 52, 46, 44, 43, 42]
    spark_tp = [12, 10, 8, 6, 8, 15, 35, 68, 88, 82, 60, 58, 55, 59, 64, 76, 96, 114, 118, 92, 65, 48, 32, 22]
    spark_cong = [0, 0, 0, 0, 0, 1, 3, 5, 6, 4, 2, 2, 2, 2, 3, 4, 6, 7, 7, 5, 3, 2, 1, 0]
    spark_viol = [1, 0, 0, 0, 0, 1, 3, 6, 9, 8, 4, 3, 3, 4, 5, 8, 11, 14, 12, 8, 5, 3, 2, 1]

    return {
        "generated_at": "2026-10-10 18:32:14 IST",
        "data_through": "2026-10-10 18:32:02 IST",
        "freshness_seconds": 12,
        "is_stale": False,
        "period_label": "Today (10 Oct 2026)",
        "compare_label": "vs yesterday (09 Oct 2026)",
        "kpis": [
            {
                "id": "network_delay",
                "label": "NETWORK DELAY",
                "value": "42 s",
                "unit": "s/veh",
                "sub_label": "avg per vehicle",
                "delta": -6.0,
                "delta_formatted": "▼ 6% vs yesterday",
                "delta_is_good": True,
                "status_dot": None,
                "icon": "clock",
                "sparkline": spark_delay,
                "tooltip": "Network average travel delay per vehicle based on BoT-SORT trajectory tracking."
            },
            {
                "id": "throughput",
                "label": "THROUGHPUT",
                "value": "118k PCU",
                "unit": "PCU",
                "sub_label": "served today",
                "delta": 3.0,
                "delta_formatted": "▲ 3% vs last Sat",
                "delta_is_good": None,  # Neutral (demand driven)
                "status_dot": None,
                "icon": "arrow-through-gate",
                "sparkline": spark_tp,
                "tooltip": "Stop-line crossings weighted by passenger car units across 22 junctions."
            },
            {
                "id": "congested_junctions",
                "label": "CONGESTED JUNCTIONS",
                "value": "4 / 22",
                "unit": "junctions",
                "sub_label": "index ≥ 55 now · peak 7 at 18:30",
                "delta": 0.0,
                "delta_formatted": "stable vs yesterday",
                "delta_is_good": None,
                "status_dot": "red",  # red for 4+
                "icon": "alert-triangle",
                "sparkline": spark_cong,
                "tooltip": "Junctions currently operating above Level of Service D threshold."
            },
            {
                "id": "open_incidents",
                "label": "OPEN INCIDENTS",
                "value": "3",
                "unit": "incidents",
                "sub_label": "1 stalled · 1 wrong-way · 1 emergency",
                "delta": -1.0,
                "delta_formatted": "▼ 1 from morning shift",
                "delta_is_good": True,
                "status_dot": "amber",
                "icon": "siren",
                "sparkline": [2, 1, 1, 1, 0, 1, 2, 4, 3, 2, 2, 1, 2, 3, 2, 4, 5, 4, 3, 3, 3, 3, 2, 1],
                "tooltip": "Active incidents awaiting clearance by traffic control or wardens."
            },
            {
                "id": "violations",
                "label": "VIOLATIONS",
                "value": "60",
                "unit": "today",
                "sub_label": "BRTS 43 · lane 17 · 9.4/h",
                "delta": 12.0,
                "delta_formatted": "▲ 12% vs last Sat",
                "delta_is_good": False,
                "status_dot": None,
                "icon": "shield",
                "sparkline": spark_viol,
                "tooltip": "Automated vision-detected violations awaiting or issued as challans."
            },
            {
                "id": "system_health",
                "label": "SYSTEM HEALTH",
                "value": "96.4%",
                "unit": "uptime",
                "sub_label": "21/22 cameras live · 1 on fallback",
                "delta": -0.8,
                "delta_formatted": "CAM-A20 telemetry degraded",
                "delta_is_good": False,
                "status_dot": "amber",
                "icon": "activity",
                "sparkline": [98, 98, 98, 98, 98, 97, 97, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96, 96],
                "tooltip": "Edge camera uptime, inference latency, and fallback controller status."
            }
        ]
    }


@router.get("/delay-series")
def get_delay_series(
    scope: str = Query("network"),
    range_type: str = Query("today", alias="range")
):
    """
    Hourly delay curves (Adaptive vs Baseline) with peak period bands.
    Section 4.2.
    """
    # If scope is a specific junction, load its profile; otherwise network mean
    if scope.startswith("junction:"):
        jid = scope.split(":")[1]
        raw = get_hourly_profile(jid)
    else:
        # Network average of top 10 core junctions
        all_profs = [get_hourly_profile(j["id"]) for j in CANONICAL_JUNCTIONS[:10]]
        raw = []
        for h in range(24):
            avg_adapt = sum(p[h]["delay_s"] for p in all_profs) / len(all_profs)
            avg_base = sum(p[h]["baseline_delay_s"] for p in all_profs) / len(all_profs)
            avg_veh = int(sum(p[h]["vehicles"] for p in all_profs))
            raw.append({
                "hour": f"{h:02d}:00",
                "hour_num": h,
                "delay_s": round(avg_adapt, 1),
                "baseline_delay_s": round(avg_base, 1),
                "vehicles": avg_veh,
            })

    series = []
    for r in raw:
        diff = round(r["baseline_delay_s"] - r["delay_s"], 1)
        savings_pct = round((diff / r["baseline_delay_s"]) * 100.0, 1)
        series.append({
            "t": r["hour"],
            "adaptive": r["delay_s"],
            "baseline": r["baseline_delay_s"],
            "savings_s": diff,
            "savings_pct": savings_pct,
            "vehicles_served": r["vehicles"],
            "is_peak": (8 <= r["hour_num"] <= 10) or (17 <= r["hour_num"] <= 20)
        })

    return {
        "scope": scope,
        "eyebrow": "DELAY OVER TIME",
        "title": "Adaptive vs baseline · seconds per vehicle",
        "units": "s/veh",
        "peak_bands": [
            {"name": "AM Peak", "start": "08:00", "end": "10:00"},
            {"name": "PM Peak", "start": "17:00", "end": "20:00"}
        ],
        "annotations": [
            {"time": "09:15", "junction": "J001", "event": "Emergency Preemption (+42s green)"},
            {"time": "18:20", "junction": "J008", "event": "Dynamic Queue Flush Initiated"}
        ],
        "data": series
    }


@router.get("/los-distribution")
def get_los_distribution(range_type: str = Query("today", alias="range")):
    """
    HCM Level of Service grade distribution by hour blocks.
    Section 4.3.
    """
    blocks = [
        {"block": "00:00-06:00", "label": "Night Off-Peak", "A_C": 94, "D": 5, "E": 1, "F": 0},
        {"block": "06:00-08:00", "label": "Early Commute", "A_C": 82, "D": 14, "E": 4, "F": 0},
        {"block": "08:00-10:00", "label": "AM Peak Rush", "A_C": 52, "D": 28, "E": 14, "F": 6},
        {"block": "10:00-14:00", "label": "Midday Business", "A_C": 74, "D": 18, "E": 6, "F": 2},
        {"block": "14:00-17:00", "label": "Afternoon Shift", "A_C": 76, "D": 17, "E": 5, "F": 2},
        {"block": "17:00-20:00", "label": "PM Peak Rush", "A_C": 44, "D": 32, "E": 16, "F": 8},
        {"block": "20:00-24:00", "label": "Late Evening", "A_C": 86, "D": 11, "E": 3, "F": 0},
    ]
    return {
        "eyebrow": "LEVEL OF SERVICE",
        "title": "Junction-hours by LOS grade",
        "overall_summary": "6.8% of daily junction-hours operated at LOS E/F",
        "legend": [
            {"grade": "A-C", "desc": "Free flow", "color": "#5A5A60"},
            {"grade": "D", "desc": "Approaching unstable", "color": "#A1A1A8"},
            {"grade": "E", "desc": "Unstable", "color": "#E8A838"},
            {"grade": "F", "desc": "Breakdown", "color": "#D9534F"}
        ],
        "blocks": blocks
    }


@router.get("/violations")
def get_violations_trend(range_type: str = Query("today", alias="range")):
    """
    Stacked hourly violation data by type with the 15/h threshold line.
    Section 4.4.
    """
    hours_data = []
    for h in range(24):
        # Peak violation periods align with rush hours
        is_rush = (8 <= h <= 10) or (17 <= h <= 20)
        brts = random.randint(3, 7) if is_rush else random.randint(0, 2)
        lane = random.randint(2, 5) if is_rush else random.randint(0, 2)
        wrong = 1 if (is_rush and random.random() < 0.4) else 0
        other = 1 if random.random() < 0.3 else 0
        total = brts + lane + wrong + other

        hours_data.append({
            "t": f"{h:02d}:00",
            "brts_intrusion": brts,
            "lane_discipline": lane,
            "wrong_way": wrong,
            "other": other,
            "total": total,
            "escalated": total >= 15,
            "is_current_hour": (h == 18)
        })

    return {
        "eyebrow": "VIOLATIONS & INCIDENTS",
        "title": "By type · per hour",
        "threshold": 15,
        "threshold_label": "ESCALATED (15/h rule)",
        "total_today": sum(d["total"] for d in hours_data),
        "data": hours_data
    }


@router.get("/heatmap")
def get_congestion_heatmap(
    metric: str = Query("index"),
    range_type: str = Query("today", alias="range")
):
    """
    All 22 junctions across 24 hours with exact 4-step color calibration.
    Section 4.5.
    """
    rows = []
    for j in CANONICAL_JUNCTIONS:
        prof = get_hourly_profile(j["id"])
        hours_values = []
        for p in prof:
            if metric == "delay":
                val = p["delay_s"]
            elif metric == "queue":
                val = p["queue_m"]
            elif metric == "deviation":
                val = p["deviation"]
            else:
                val = p["index"]
            hours_values.append(val)

        rows.append({
            "id": j["id"],
            "name": j["name"],
            "short_name": j["short_name"],
            "zone": j["zone"],
            "on_brts": j["on_brts"],
            "mode": j["mode"],
            "health": j["health"],
            "peak_index": max(p["index"] for p in prof),
            "peak_hour": f"{max(prof, key=lambda x: x['index'])['hour']}",
            "hours": hours_values,
        })

    # Sort default by worst peak index
    rows.sort(key=lambda x: x["peak_index"], reverse=True)

    return {
        "eyebrow": "CONGESTION HEATMAP",
        "title": "All 22 junctions × hour · congestion index (0-100)",
        "current_hour": 18,
        "now_label": "18:30 IST",
        "metric": metric,
        "legend": [
            {"level": "Low", "range": "0-35", "color": "#1E1E22"},
            {"level": "Moderate", "range": "35-55", "color": "#5A5A60"},
            {"level": "High", "range": "55-75", "color": "#E8A838"},
            {"level": "Critical", "range": "75+", "color": "#D9534F"}
        ],
        "rows": rows
    }


@router.get("/bottlenecks")
def get_top_bottlenecks(limit: int = 5):
    """
    Ranked by persistence (minutes in High+Critical ≥ 75).
    Section 4.6.
    """
    bottlenecks = [
        {
            "rank": "01",
            "id": "J008",
            "name": "Kharwarnagar Circle",
            "zone": "South Zone",
            "minutes_above_75": 142,
            "peak_index": 91,
            "peak_time": "18:20",
            "flags": ["SPILLBACK"]
        },
        {
            "rank": "02",
            "id": "J020",
            "name": "Althan Tenement",
            "zone": "South Zone",
            "minutes_above_75": 96,
            "peak_index": 84,
            "peak_time": "09:05",
            "flags": ["FALLBACK MODE"]
        },
        {
            "rank": "03",
            "id": "J022",
            "name": "Station Circle",
            "zone": "Central Surat",
            "minutes_above_75": 71,
            "peak_index": 82,
            "peak_time": "18:40",
            "flags": ["STARVATION"]
        },
        {
            "rank": "04",
            "id": "J002",
            "name": "Sahara Darwaja",
            "zone": "Ring Road",
            "minutes_above_75": 64,
            "peak_index": 79,
            "peak_time": "19:10",
            "flags": []
        },
        {
            "rank": "05",
            "id": "J014",
            "name": "Textile Market Corridor",
            "zone": "Commercial Hub",
            "minutes_above_75": 58,
            "peak_index": 78,
            "peak_time": "17:45",
            "flags": ["SPILLBACK"]
        }
    ]
    return bottlenecks[:limit]


@router.get("/adaptive-benefit")
def get_adaptive_benefit():
    """
    Adaptive Benefit panel promoting the headline claim with method disclosure.
    Section 4.7.
    """
    return {
        "eyebrow": "ADAPTIVE BENEFIT",
        "method": "A/B WINDOWS + SUMO SHADOW REPLAY",
        "delay_reduction_pct": 31.4,
        "confidence_interval": "26–36%, 95% CI",
        "sample_coverage": "based on 18 junction-days logged",
        "vehicle_hours_saved": 412,
        "emissions_avoided_tonnes": 1.9,
        "zones": [
            {"zone": "South Zone", "benefit_pct": 34.2, "status": "active"},
            {"zone": "Ring Road", "benefit_pct": 32.8, "status": "active"},
            {"zone": "Central Surat", "benefit_pct": 31.5, "status": "active"},
            {"zone": "East Zone", "benefit_pct": 28.6, "status": "active"},
            {"zone": "West Zone", "benefit_pct": 26.4, "status": "active"},
            {"zone": "Outer Ring Road", "benefit_pct": None, "status": "NO BASELINE"}
        ]
    }


@router.get("/junctions-performance")
def get_junctions_performance():
    """
    Junction Performance Report table (All 22 canonical junctions).
    Section 4.9.
    """
    rows = []
    for j in CANONICAL_JUNCTIONS:
        prof = get_hourly_profile(j["id"])
        latest = prof[18]  # Current hour snapshot (18:00)

        # LOS grade HCM delay formula
        d = latest["delay_s"]
        if d <= 10:
            los = "A"
        elif d <= 20:
            los = "B"
        elif d <= 35:
            los = "C"
        elif d <= 55:
            los = "D"
        elif d <= 80:
            los = "E"
        else:
            los = "F"

        gain = round(latest["baseline_delay_s"] - latest["delay_s"], 1)
        gain_pct = round((gain / latest["baseline_delay_s"]) * 100.0)

        rows.append({
            "id": j["id"],
            "name": j["name"],
            "short_name": j["short_name"],
            "zone": j["zone"],
            "los": los,
            "congestion_index": latest["index"],
            "avg_delay_s": latest["delay_s"],
            "delay_delta_pct": -gain_pct,
            "p95_queue_m": round(latest["queue_m"] * 1.25),
            "saturation_vc": round(j["saturation_base"] + (latest["index"] - 50) * 0.002, 2),
            "throughput_pcu": latest["vehicles"],
            "cycle_failures_pct": 14 if latest["index"] > 70 else (6 if latest["index"] > 50 else 2),
            "violations_today": random.randint(2, 9) if j["on_brts"] else random.randint(0, 3),
            "mode": j["mode"],
            "on_brts": j["on_brts"],
            "adaptive_gain_pct": gain_pct,
            "health": j["health"],
            "sparkline": [p["index"] for p in prof]
        })

    # Default sort by congestion descending
    rows.sort(key=lambda x: x["congestion_index"], reverse=True)
    return rows


@router.get("/junction/{junction_id}")
def get_junction_detail(junction_id: str):
    """
    Junction Detail Drawer data.
    Section 4.10.
    """
    j = JUNCTION_MAP.get(junction_id) or CANONICAL_JUNCTIONS[0]
    prof = get_hourly_profile(j["id"])
    latest = prof[18]

    return {
        "id": j["id"],
        "name": j["name"],
        "zone": j["zone"],
        "mode": j["mode"],
        "on_brts": j["on_brts"],
        "health": j["health"],
        "camera_id": j["camera_id"],
        "last_update": "4s ago",
        "summary": {
            "delay_s": latest["delay_s"],
            "delay_delta_pct": -21,
            "p95_queue_m": round(latest["queue_m"] * 1.25),
            "saturation_vc": j["saturation_base"],
            "cycle_failure_pct": 14,
            "los": "D"
        },
        "approaches": [
            {"approach": "North", "flow_pcu": 1140, "queue_m": 42.0, "avg_speed": 34.0, "green_split": "38s", "delay_s": 44.0},
            {"approach": "East", "flow_pcu": 890, "queue_m": 28.0, "avg_speed": 38.0, "green_split": "28s", "delay_s": 36.0},
            {"approach": "South", "flow_pcu": 1280, "queue_m": 58.0, "avg_speed": 28.0, "green_split": "44s", "delay_s": 52.0},
            {"approach": "West", "flow_pcu": 760, "queue_m": 22.0, "avg_speed": 40.0, "green_split": "25s", "delay_s": 32.0},
        ],
        "index_curve_24h": [{"hour": p["hour"], "today": p["index"], "typical": round(p["index"] * 0.94, 1)} for p in prof],
        "events": [
            {"time": "18:24", "type": "VIOLATION", "desc": "BRTS lane intrusion detected (auto-rickshaw GJ-05-BX-4192)"},
            {"time": "18:12", "type": "PREEMPTION", "desc": "BRTS green extension (+8s) for Transit Bus 104"},
            {"time": "17:48", "type": "QUEUE ALERT", "desc": "Southbound queue exceeded 60m threshold"}
        ]
    }


@router.get("/recommendations-grouped")
def get_recommendations_grouped(status: Optional[str] = None):
    """
    AI Recommendation Engine with deduplication, categories, evidence, and outcome metrics.
    Section 4.8.
    """
    recs = [
        {
            "id": 101,
            "category": "INFRASTRUCTURE",
            "severity": "CRITICAL",
            "issue_title": "BRTS Lane Intrusion Heavy",
            "junction_ids": ["J001", "J008", "J014", "J020"],
            "junction_names": "Udhna Darwaja, Kharwarnagar, Textile Mkt, Althan",
            "evidence": "22 intrusions/h sustained for 3.2 h (threshold 15/h)",
            "suggested_action": "Install physical concrete channelizers and automated barrier at entry ramps to eliminate unauthorized access.",
            "expected_impact": "−60% intrusions · +4.8 km/h BRTS speed",
            "confidence": "HIGH",
            "age": "2h",
            "status": "PENDING",
            "measured_outcome": None
        },
        {
            "id": 102,
            "category": "OPERATIONAL",
            "severity": "HIGH",
            "issue_title": "Queue Spillback Gridlock",
            "junction_ids": ["J002"],
            "junction_names": "Sahara Darwaja",
            "evidence": "Southbound queue exceeded 72m for 4 consecutive cycles",
            "suggested_action": "Increase North-South phase allocation by +14 seconds and coordinate lead offset with Delhi Gate.",
            "expected_impact": "−18% delay · queue flush in 2 cycles",
            "confidence": "HIGH",
            "age": "4h",
            "status": "APPLIED",
            "measured_outcome": "Outcome: −15.4% queue at Sahara Darwaja (expected −18%)"
        },
        {
            "id": 103,
            "category": "OPERATIONAL",
            "severity": "MEDIUM",
            "issue_title": "Asymmetric Flow Imbalance",
            "junction_ids": ["J003", "J017"],
            "junction_names": "Majura Gate, Cable Bridge Adajan",
            "evidence": "Inbound flow 2.8x outbound flow during morning commute",
            "suggested_action": "Deploy dynamic green wave offset (+18s lead) across Tapi bridge arterial.",
            "expected_impact": "−12% corridor transit time",
            "confidence": "MEDIUM",
            "age": "1d",
            "status": "PENDING",
            "measured_outcome": None
        },
        {
            "id": 104,
            "category": "INFRASTRUCTURE",
            "severity": "HIGH",
            "issue_title": "Freight Loading Spillover",
            "junction_ids": ["J014"],
            "junction_names": "Textile Market Corridor",
            "evidence": "Unloading trucks occupying curb lane during 17:00–20:00 rush",
            "suggested_action": "Enforce strict loading restrictions between 17:00 and 21:00 with towing wardens.",
            "expected_impact": "+1 active lane · −24% congestion index",
            "confidence": "HIGH",
            "age": "3d",
            "status": "PENDING",
            "measured_outcome": None
        },
        {
            "id": 105,
            "category": "OPERATIONAL",
            "severity": "MEDIUM",
            "issue_title": "Cycle Length Extension",
            "junction_ids": ["J005"],
            "junction_names": "Adajan Gam / Patia",
            "evidence": "Residual queue detected at green termination in 18% of cycles",
            "suggested_action": "Extend maximum cycle length from 110s to 135s during evening peak.",
            "expected_impact": "Zero cycle failure · −14% stop-line delay",
            "confidence": "MEDIUM",
            "age": "5d",
            "status": "APPLIED",
            "measured_outcome": "Outcome: −12.1% delay at J005 (expected −14%)"
        }
    ]

    if status and status.upper() != "ALL":
        recs = [r for r in recs if r["status"] == status.upper()]
    return recs


@router.post("/recommendations/{rec_id}/decision")
def post_recommendation_decision(
    rec_id: int,
    action: str = Query("approve"),
    reason: Optional[str] = None
):
    """Approve, reject, or defer a recommendation."""
    return {
        "id": rec_id,
        "action": action,
        "status": "APPLIED" if action == "approve" else ("REJECTED" if action == "reject" else "DEFERRED"),
        "reason": reason,
        "timestamp": datetime.now(IST).isoformat()
    }


@router.get("/incidents")
def get_incidents_log():
    """Incidents log & MTTR statistics. Section 5.4."""
    return {
        "mttr_mean_min": 18.4,
        "mttr_p90_min": 32.0,
        "emergency_avg_latency_s": 9.4,
        "throughput_lost_pcu_h": 4820,
        "active_incidents": [
            {
                "id": "INC-842",
                "type": "STALLED VEHICLE",
                "junction_id": "J008",
                "junction_name": "Kharwarnagar Circle",
                "lane": "Southbound Lane 2",
                "duration_min": 16,
                "status": "CRITICAL",
                "handler": "Warden Assigned",
                "throughput_loss": "320 veh/h"
            },
            {
                "id": "INC-843",
                "type": "WRONG-WAY ENTRY",
                "junction_id": "J014",
                "junction_name": "Textile Market Corridor",
                "lane": "BRTS Approach",
                "duration_min": 8,
                "status": "HIGH",
                "handler": "Police Intercepting",
                "throughput_loss": "140 veh/h"
            },
            {
                "id": "INC-844",
                "type": "EMERGENCY VEHICLE",
                "junction_id": "J001",
                "junction_name": "Udhna Darwaja",
                "lane": "Eastbound Corridor",
                "duration_min": 3,
                "status": "ACTIVE PREEMPTION",
                "handler": "Auto Green Corridor Active",
                "throughput_loss": "0 veh/h"
            }
        ]
    }


@router.get("/signals")
def get_signals_log():
    """Signal mode timeline, green utilization, preemptions. Section 5.2."""
    return {
        "preemptions_today": 14,
        "preemption_success_rate": 98.2,
        "avg_cross_street_cost_s": 18.5,
        "adaptive_junctions_count": 20,
        "fixed_junctions_count": 1,
        "fallback_junctions_count": 1,
        "mode_timeline": [
            {"id": "J001", "name": "Udhna Darwaja", "mode": "ADAPTIVE", "green_utilization": "92%"},
            {"id": "J002", "name": "Sahara Darwaja", "mode": "ADAPTIVE", "green_utilization": "94%"},
            {"id": "J008", "name": "Kharwarnagar Circle", "mode": "ADAPTIVE", "green_utilization": "97%"},
            {"id": "J009", "name": "Khatodara GIDC Cross", "mode": "FIXED", "green_utilization": "68%"},
            {"id": "J020", "name": "Althan Tenement", "mode": "FALLBACK", "green_utilization": "74%"}
        ]
    }


@router.get("/system-health")
def get_system_health():
    """Camera status grid, pipeline latency, uptime. Section 5.6."""
    return {
        "network_uptime_pct": 98.4,
        "cameras_online": 21,
        "cameras_total": 22,
        "pipeline_latency_p50_ms": 18,
        "pipeline_latency_p95_ms": 38,
        "confidence_by_lighting": {
            "DAYLIGHT": 94.2,
            "NIGHT": 89.1,
            "RAIN": 86.4,
            "GLARE": 84.0
        },
        "cameras": [
            {"id": j["camera_id"], "junction": j["name"], "status": "online" if j["health"] == "live" else "degraded", "fps": 29.8, "latency_ms": 22}
            for j in CANONICAL_JUNCTIONS
        ]
    }
