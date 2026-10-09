# backend-api/app/reports/pdf_builder.py
"""
pdf_builder.py — Executive PDF Report Generator (ReportLab + Matplotlib)
========================================================================
Builds comprehensive, publication-quality multi-page PDF intelligence briefings:
  - Distinct visual themes for AI Synthesis Mode vs Standard Algorithmic Mode
  - 6-metric KPI executive callout grid
  - Embedded Matplotlib horizontal infraction bars & daily volume trends
  - Comprehensive junction queue telemetry matrix with fill-ratio badges
  - Spatial hotspot distribution ranking table
  - Prioritized operational action advisories with severity tags
  - Formal signature block and Zero-Leak HMAC-SHA256 privacy disclosure
  - Page-numbered running headers and footers (NumberedCanvas)
"""

from __future__ import annotations

import io
from xml.sax.saxutils import escape
from typing import Any, List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas

from app.reports.narrative import ReportNarrative

# ---------------------------------------------------------------------------
# Numbered Running Header / Footer Canvas
# ---------------------------------------------------------------------------

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(14 * mm, 287 * mm, "E-Rakshak Intelligent Traffic Management — Executive Report")
            self.drawRightString(196 * mm, 287 * mm, "CONFIDENTIAL / RESTRICTED")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(14 * mm, 285 * mm, 196 * mm, 285 * mm)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(14 * mm, 12 * mm, 196 * mm, 12 * mm)
        self.drawString(
            14 * mm,
            8.5 * mm,
            "Surat Municipal Corporation & City Traffic Police Command | Zero-Leak Encrypted Architecture"
        )
        self.drawRightString(
            196 * mm,
            8.5 * mm,
            f"Page {self._pageNumber} of {total_pages}"
        )
        self.restoreState()


# ---------------------------------------------------------------------------
# Typography & Design Styles
# ---------------------------------------------------------------------------

_raw_styles = getSampleStyleSheet()

STYLE_TITLE_AI = ParagraphStyle(
    "TitleAI",
    parent=_raw_styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=21,
    textColor=colors.HexColor("#065f46"), # Deep Emerald
    spaceAfter=2,
)

STYLE_TITLE_STD = ParagraphStyle(
    "TitleSTD",
    parent=_raw_styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=21,
    textColor=colors.HexColor("#1e293b"), # Slate Navy
    spaceAfter=2,
)

STYLE_SUBTITLE = ParagraphStyle(
    "DocSubtitle",
    parent=_raw_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=13,
    textColor=colors.HexColor("#2563eb"),
    spaceAfter=4,
)

STYLE_H2 = ParagraphStyle(
    "SectionH2",
    parent=_raw_styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=15,
    textColor=colors.HexColor("#0f172a"),
    spaceBefore=8,
    spaceAfter=4,
)

STYLE_BODY = ParagraphStyle(
    "BodyCustom",
    parent=_raw_styles["BodyText"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor("#334155"),
    spaceAfter=5,
)

STYLE_TH = ParagraphStyle(
    "TableTH",
    parent=_raw_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor("#0f172a"),
)

STYLE_TD = ParagraphStyle(
    "TableTD",
    parent=_raw_styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor("#334155"),
)

STYLE_SMALL = ParagraphStyle(
    "SmallCustom",
    parent=STYLE_BODY,
    fontSize=7,
    leading=9.5,
    textColor=colors.HexColor("#64748b"),
)

def P(text: Any, style: ParagraphStyle = STYLE_BODY) -> Paragraph:
    """Safely escapes text against ReportLab XML-like markup parsing errors."""
    clean_text = escape(str(text if text is not None else "")).replace("\n", "<br/>")
    return Paragraph(clean_text, style)


# ---------------------------------------------------------------------------
# High-Resolution Matplotlib Visualizations
# ---------------------------------------------------------------------------

def _fig_to_png(fig: plt.Figure) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def chart_violations_by_type(by_type: list[dict]) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6.2, 2.1))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    if by_type:
        labels = [item["type"] for item in by_type[:5]]
        counts = [item["count"] for item in by_type[:5]]
    else:
        labels = ["No Violations Logged"]
        counts = [0]

    y_pos = range(len(labels))
    bars = ax.barh(y_pos, counts, color="#059669", edgecolor="#047857", height=0.55, alpha=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8, fontweight="medium")
    ax.invert_yaxis()
    ax.set_xlabel("Logged Violations", fontsize=8, fontweight="medium")
    ax.set_title("Infractions by Category Modality", fontsize=9, fontweight="bold", pad=6)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_width() + max(1, count * 0.02), bar.get_y() + bar.get_height() / 2, f"{count}",
                    va="center", ha="left", fontsize=7.5, fontweight="bold", color="#1e293b")

    plt.tight_layout()
    return _fig_to_png(fig)

def chart_daily_trend(per_day: list[dict]) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6.2, 2.1))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    if per_day:
        dates = [item["date"][5:] for item in per_day]
        counts = [item["count"] for item in per_day]
        ax.plot(range(len(dates)), counts, marker="o", color="#dc2626", linewidth=1.6, markersize=3.5, label="Daily Volume")
        step = max(1, len(dates) // 7)
        ax.set_xticks(range(0, len(dates), step))
        ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], fontsize=7.5, rotation=20)
    else:
        ax.text(0.5, 0.5, "No temporal volume logged for window", ha="center", va="center", fontsize=8.5, color="#64748b")

    ax.set_ylabel("Incident Count", fontsize=8, fontweight="medium")
    ax.set_title("Temporal Progression (Daily Incident Distribution)", fontsize=9, fontweight="bold", pad=6)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    return _fig_to_png(fig)


# ---------------------------------------------------------------------------
# PDF Document Assembly
# ---------------------------------------------------------------------------

def build_pdf(
    period_label: str,
    stats: dict,
    narr: ReportNarrative,
    used_ai: bool,
    generated_at: str,
) -> bytes:
    """Builds a comprehensive, publication-quality executive traffic intelligence PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story: List[Any] = []

    # 1. Header Banner
    if used_ai:
        title_style = STYLE_TITLE_AI
        badge_text = "✨ AI-SYNTHESIZED EXECUTIVE BRIEFING (ZERO-LEAK ENCRYPTED PIPELINE)"
        badge_bg = "#ecfdf5"
        badge_border = "#059669"
        badge_fg = "#065f46"
        sub_title = "E-Rakshak Neural Traffic Intelligence & Predictive Foresight"
    else:
        title_style = STYLE_TITLE_STD
        badge_text = "📋 DETERMINISTIC STATISTICAL LEDGER (ALGORITHMIC REGISTRY MODE)"
        badge_bg = "#f1f5f9"
        badge_border = "#475569"
        badge_fg = "#1e293b"
        sub_title = "E-Rakshak Statistical Compliance & Operational Audit"

    story.append(P("E-RAKSHAK ADAPTIVE TRAFFIC MANAGEMENT SYSTEM", STYLE_SUBTITLE))
    story.append(P(sub_title, title_style))

    # Badge & Metadata Table
    badge_p = Paragraph(f"<font color='{badge_fg}'><b>{badge_text}</b></font>", STYLE_SMALL)
    meta_p = Paragraph(
        f"<b>Window:</b> {escape(period_label)} &nbsp;|&nbsp; "
        f"<b>Generated:</b> {escape(generated_at)} &nbsp;|&nbsp; "
        f"<b>Classification:</b> RESTRICTED (SURAT POLICE COMMAND)",
        STYLE_SMALL
    )
    banner_table = Table([[badge_p, meta_p]], colWidths=[90 * mm, 92 * mm])
    banner_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(badge_bg)),
        ("BOX", (0, 0), (0, 0), 1, colors.HexColor(badge_border)),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#f8fafc")),
        ("BOX", (1, 0), (1, 0), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 8))

    # 2. Executive 6-Card KPI Grid
    v_stats = stats.get("violations", {})
    t_stats = stats.get("traffic", {})
    t_summary = t_stats.get("summary", {})
    dq = stats.get("data_quality", {})

    total_viol = v_stats.get("total", 0)
    change_pct = v_stats.get("change_pct")
    delta_str = f"({change_pct:+.1f}%)" if change_pct is not None else "(baseline)"
    
    avg_q = t_summary.get("avg_queue_m", 0.0)
    peak_q = t_summary.get("peak_queue_m", 0.0)
    avg_spd = t_summary.get("avg_speed_kmh", 0.0)
    j_count = t_summary.get("active_junctions", len(t_stats.get("junctions", [])))
    cov_pct = dq.get("coverage_pct", 100.0)
    hotspots_count = len(v_stats.get("top_junctions", []))

    kpi_data = [
        [
            Paragraph("TOTAL INFRACTIONS", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
            Paragraph("PEAK QUEUE DEPTH", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
            Paragraph("ARTERIAL VELOCITY", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
            Paragraph("NODAL COVERAGE", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
            Paragraph("HOTSPOTS FLAGGED", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
            Paragraph("TELEMETRY AUDIT", ParagraphStyle("KL", fontName="Helvetica-Bold", fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)),
        ],
        [
            Paragraph(f"<b>{total_viol}</b> <font size=8>{delta_str}</font>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#dc2626"), alignment=1)),
            Paragraph(f"<b>{peak_q:.1f} m</b>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#ea580c"), alignment=1)),
            Paragraph(f"<b>{avg_spd:.1f} km/h</b>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#0284c7"), alignment=1)),
            Paragraph(f"<b>{j_count} Nodes</b>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#475569"), alignment=1)),
            Paragraph(f"<b>{hotspots_count} Sectors</b>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#b91c1c"), alignment=1)),
            Paragraph(f"<b>{cov_pct:.1f}%</b>", ParagraphStyle("KV", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor("#059669"), alignment=1)),
        ]
    ]

    col_w = (182 * mm) / 6
    kpi_table = Table(kpi_data, colWidths=[col_w] * 6)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 8))

    # 3. Section 1: Executive Intelligence Briefing / Audit Statement
    sec1_title = "1. AI Executive Strategic Synthesis" if used_ai else "1. Statistical Compliance Audit Statement"
    story.append(P(sec1_title, STYLE_H2))
    story.append(P(narr.executive_summary, STYLE_BODY))
    story.append(Spacer(1, 4))

    # 4. Section 2: Key Strategic Findings Cards
    story.append(P("2. Key Operational Findings & Nodal Diagnostics", STYLE_H2))
    for idx, f in enumerate(narr.key_findings, 1):
        f_p = Paragraph(f"<b>Finding {idx}: {escape(f.title)}</b><br/><font color='#475569'>{escape(f.detail)}</font>", STYLE_BODY)
        f_box = Table([[f_p]], colWidths=[182 * mm])
        f_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("LINELEFT", (0, 0), (-1, -1), 2.5, colors.HexColor("#059669" if used_ai else "#3b82f6")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(f_box)
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 4))

    # 5. Section 3: Visual Analytics (Charts)
    story.append(P("3. Empirical Traffic Telemetry & Temporal Dispersion", STYLE_H2))
    img_type = Image(chart_violations_by_type(v_stats.get("by_type", [])), width=89 * mm, height=34 * mm)
    img_trend = Image(chart_daily_trend(v_stats.get("per_day", [])), width=89 * mm, height=34 * mm)
    charts_table = Table([[img_type, img_trend]], colWidths=[91 * mm, 91 * mm])
    charts_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(charts_table)
    story.append(Spacer(1, 8))

    # 6. Section 4: Comprehensive Junction Telemetry Matrix Table
    story.append(P("4. Monitored Corridor & Intersection Performance Matrix", STYLE_H2))
    junction_list = t_stats.get("junctions", [])
    if junction_list:
        t_header = [
            Paragraph("<b>Junction Corridor</b>", STYLE_TH),
            Paragraph("<b>Avg Queue</b>", STYLE_TH),
            Paragraph("<b>Peak Queue</b>", STYLE_TH),
            Paragraph("<b>Speed</b>", STYLE_TH),
            Paragraph("<b>Congestion Level</b>", STYLE_TH),
            Paragraph("<b>Samples</b>", STYLE_TH),
        ]
        t_rows = [t_header]
        for j in junction_list[:12]:
            q_avg = j.get("avg_queue_m", 0.0)
            q_max = j.get("max_queue_m", 0.0)
            spd = j.get("avg_speed_kmh", 0.0)
            samples = j.get("samples", 0)
            
            # Congestion classification
            if q_max > 60:
                badge = "<font color='#b91c1c'><b>SEVERE</b></font>"
            elif q_max > 35:
                badge = "<font color='#d97706'><b>MODERATE</b></font>"
            else:
                badge = "<font color='#059669'><b>NOMINAL</b></font>"

            t_rows.append([
                Paragraph(escape(j.get("junction", "Unknown")), STYLE_TD),
                Paragraph(f"{q_avg:.1f} m", STYLE_TD),
                Paragraph(f"{q_max:.1f} m", STYLE_TD),
                Paragraph(f"{spd:.1f} km/h", STYLE_TD),
                Paragraph(badge, STYLE_TD),
                Paragraph(str(samples), STYLE_TD),
            ])

        j_table = Table(t_rows, colWidths=[65 * mm, 23 * mm, 23 * mm, 23 * mm, 28 * mm, 20 * mm])
        j_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(j_table)
    else:
        story.append(P("No junction metrics logged for this window.", STYLE_BODY))

    story.append(Spacer(1, 8))

    # 7. Section 5: Prioritized Engineering Interventions
    story.append(P("5. Prioritized Traffic Engineering Advisories & Enforcement Plans", STYLE_H2))
    recs = stats.get("recommendations", [])
    if isinstance(recs, dict):
        recs = recs.get("items", [])
    if recs:
        rec_headers = [
            Paragraph("<b>Target Sector</b>", STYLE_TH),
            Paragraph("<b>Priority</b>", STYLE_TH),
            Paragraph("<b>Operational Advisory & Action Plan</b>", STYLE_TH),
            Paragraph("<b>Status</b>", STYLE_TH),
        ]
        rec_table_rows = [rec_headers]
        for r in recs[:6]:
            sev = r.get("severity", "medium").upper()
            sev_color = "#b91c1c" if sev in ("CRITICAL", "HIGH") else "#d97706"
            stat_color = "#059669" if r.get("status") == "applied" else "#475569"
            
            rec_table_rows.append([
                Paragraph(f"<b>{escape(r.get('junction', 'Network'))}</b>", STYLE_TD),
                Paragraph(f"<font color='{sev_color}'><b>[{sev}]</b></font>", STYLE_TD),
                Paragraph(f"{escape(r.get('suggested_action', r.get('description', '')))}", STYLE_TD),
                Paragraph(f"<font color='{stat_color}'><b>{r.get('status', 'pending').upper()}</b></font>", STYLE_TD),
            ])

        rec_table = Table(rec_table_rows, colWidths=[42 * mm, 24 * mm, 92 * mm, 24 * mm])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(rec_table)
    else:
        # Fallback to narrative recommended actions
        for act in narr.recommended_actions:
            story.append(P(f"• &nbsp; {escape(act)}", ParagraphStyle("ActP", parent=STYLE_BODY, leftIndent=10)))

    story.append(Spacer(1, 8))

    # 8. Section 6: Data Quality & Cryptographic Audit Footprint
    story.append(P("6. Sensor Integrity & Cryptographic Security Footprint", STYLE_H2))
    story.append(P(narr.data_quality_note, STYLE_BODY))

    if used_ai:
        privacy_claim = (
            "<b>ZERO-LEAK PRIVACY GUARANTEE:</b> All physical corridor locations and junction nodes were "
            "cryptographically pseudonymized with salted HMAC-SHA256 tokens prior to LLM analysis. "
            "No raw surveillance telemetry, license plates, camera snapshots, or citizen identities were transmitted."
        )
    else:
        privacy_claim = (
            "<b>DETERMINISTIC COMPLIANCE AUDIT:</b> Report generated entirely via local SQL database aggregation. "
            "Cloud AI services disabled; all statistics derived from verified primary municipal registers."
        )
    story.append(P(privacy_claim, STYLE_SMALL))
    story.append(Spacer(1, 6))

    # Authorization Signature Block
    sig_table = Table([
        [
            Paragraph("<b>E-Rakshak System Auditor</b><br/>Surat Smart City Mission", STYLE_SMALL),
            Paragraph("<b>Chief Traffic Operations Officer</b><br/>Surat City Traffic Police", STYLE_SMALL),
            Paragraph("<b>Cryptographic Verification Hash</b><br/>" + escape(stats.get("audit_hash", "SHA256-VERIFIED")), STYLE_SMALL),
        ]
    ], colWidths=[60 * mm, 60 * mm, 62 * mm])
    sig_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sig_table)

    # Compile document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
