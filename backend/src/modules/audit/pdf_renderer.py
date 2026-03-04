"""Render an EvidencePack as a branded PDF using fpdf2.

The output is a professional compliance-grade document suitable for
board packs, customer due-diligence requests, and regulatory snapshots.
"""

from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from typing import Optional

from fpdf import FPDF

from backend.src.modules.rag.evidence import EvidencePack

log = logging.getLogger(__name__)

# ── Colour palette (CapeControl brand) ─────────────────────────────────
BRAND_DARK = (15, 23, 42)       # slate-900
BRAND_ACCENT = (16, 185, 129)   # emerald-500
WHITE = (255, 255, 255)
LIGHT_GREY = (241, 245, 249)    # slate-100
MEDIUM_GREY = (148, 163, 184)   # slate-400
DARK_TEXT = (30, 41, 59)        # slate-800
TABLE_HEADER_BG = (30, 41, 59)

# Page dimensions
PAGE_W = 210  # A4 mm
MARGIN = 15


class EvidencePackPDF(FPDF):
    """Custom PDF class with CapeControl branding."""

    def __init__(self, pack: EvidencePack) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.pack = pack
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(MARGIN, MARGIN, MARGIN)
        # Add built-in font (Helvetica, no file needed)
        self.set_font("Helvetica", "", 10)

    # ── Header / Footer ────────────────────────────────────────────────
    def header(self) -> None:
        if self.page_no() == 1:
            return  # Cover page has its own header
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*MEDIUM_GREY)
        self.cell(0, 6, "CapeControl Evidence Pack", ln=True, align="L")
        self.set_draw_color(*BRAND_ACCENT)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*MEDIUM_GREY)
        self.cell(
            0, 10,
            f"Page {self.page_no()}/{{nb}}  |  Export {self.pack.export_id[:8]}  |  "
            f"Generated {self.pack.exported_at.strftime('%Y-%m-%d %H:%M UTC')}",
            align="C",
        )

    # ── Sections ────────────────────────────────────────────────────────
    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*BRAND_DARK)
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(*BRAND_ACCENT)
        self.line(MARGIN, self.get_y(), MARGIN + 50, self.get_y())
        self.ln(4)

    def key_value(self, key: str, value: str) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MEDIUM_GREY)
        self.cell(50, 6, key)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 6, value, ln=True)


def render_evidence_pdf(pack: EvidencePack) -> bytes:
    """Generate a complete PDF from an EvidencePack and return raw bytes."""

    pdf = EvidencePackPDF(pack)
    pdf.alias_nb_pages()

    # ━━━━━━━━━━━━━━━━  COVER PAGE  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.add_page()
    # Dark background block
    pdf.set_fill_color(*BRAND_DARK)
    pdf.rect(0, 0, PAGE_W, 120, "F")

    # Brand bar
    pdf.set_fill_color(*BRAND_ACCENT)
    pdf.rect(0, 120, PAGE_W, 3, "F")

    # Title
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, "Evidence Pack", ln=True, align="C")
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*BRAND_ACCENT)
    pdf.cell(0, 8, "CapeControl Compliance Export", ln=True, align="C")

    # Meta block
    pdf.set_y(75)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(200, 210, 225)
    meta_lines = [
        f"Export ID: {pack.export_id}",
        f"Generated: {pack.exported_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Exported by: {pack.exported_by_email}",
    ]
    if pack.period_start or pack.period_end:
        ps = pack.period_start.strftime("%Y-%m-%d") if pack.period_start else "unbounded"
        pe = pack.period_end.strftime("%Y-%m-%d") if pack.period_end else "unbounded"
        meta_lines.append(f"Period: {ps} to {pe}")
    for line in meta_lines:
        pdf.cell(0, 7, line, ln=True, align="C")

    # Summary stats below cover
    pdf.set_y(135)
    pdf.section_title("Executive Summary")

    summary = pack.summary
    pdf.key_value("Total Documents", str(summary.get("total_documents", 0)))
    pdf.key_value("Approved Documents", str(summary.get("approved_documents", 0)))
    pdf.key_value("Total RAG Queries", str(pack.total_queries))
    pdf.key_value("Grounded Queries", f"{pack.grounded_queries}  ({summary.get('grounded_percentage', 0)}%)")
    pdf.key_value("Refused Queries", f"{pack.refused_queries}  ({summary.get('refused_percentage', 0)}%)")
    pdf.key_value("Avg Processing Time", f"{summary.get('avg_processing_time_ms', 0)} ms")

    doc_types = summary.get("document_types", [])
    if doc_types:
        pdf.key_value("Document Types", ", ".join(doc_types))

    # ━━━━━━━━━━━━━━━━  DOCUMENT INVENTORY  ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if pack.documents:
        pdf.add_page()
        pdf.section_title("Document Inventory")

        col_widths = [70, 30, 25, 25, 30]
        headers = ["Title", "Type", "Status", "Chunks", "Created"]

        # Header row
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(*TABLE_HEADER_BG)
        pdf.set_text_color(*WHITE)
        for w, h in zip(col_widths, headers):
            pdf.cell(w, 7, h, border=1, fill=True, align="C")
        pdf.ln()

        # Data rows
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*DARK_TEXT)
        for i, doc in enumerate(pack.documents):
            bg = LIGHT_GREY if i % 2 == 0 else WHITE
            pdf.set_fill_color(*bg)
            title = doc.title[:35] + "..." if len(doc.title) > 38 else doc.title
            created = doc.created_at.strftime("%Y-%m-%d") if doc.created_at else "—"
            cells = [title, doc.doc_type, doc.status, str(doc.chunk_count), created]
            for w, c in zip(col_widths, cells):
                pdf.cell(w, 6, c, border=1, fill=True, align="C")
            pdf.ln()

    # ━━━━━━━━━━━━━━━━  QUERY LOG  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if pack.queries:
        pdf.add_page()
        pdf.section_title("RAG Query Log")

        for idx, q in enumerate(pack.queries, 1):
            # Check if we need a new page (leave room for the entry)
            if pdf.get_y() > 250:
                pdf.add_page()

            # Query header
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*BRAND_DARK)
            status = "GROUNDED" if q.grounded else ("REFUSED" if q.refused else "UNGROUNDED")
            pdf.cell(0, 6, f"Query #{idx}  [{status}]", ln=True)

            # Query text
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*DARK_TEXT)
            query_text = q.query_text[:200] + "..." if len(q.query_text) > 200 else q.query_text
            pdf.multi_cell(0, 4, f"Q: {query_text}")
            pdf.ln(1)

            # Metadata line
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(*MEDIUM_GREY)
            ts = q.timestamp.strftime("%Y-%m-%d %H:%M") if q.timestamp else "—"
            model = q.model_used or "—"
            proc = f"{q.processing_time_ms}ms" if q.processing_time_ms else "—"
            pdf.cell(0, 4, f"Time: {ts}  |  Model: {model}  |  Processing: {proc}", ln=True)

            # Response excerpt
            if q.response_text:
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(*DARK_TEXT)
                excerpt = q.response_text[:300] + "..." if len(q.response_text) > 300 else q.response_text
                pdf.multi_cell(0, 4, f"A: {excerpt}")

            # Cited docs
            if q.cited_document_ids:
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_text_color(*BRAND_ACCENT)
                pdf.cell(0, 4, f"Citations: {', '.join(str(c) for c in q.cited_document_ids)}", ln=True)

            pdf.ln(3)

    # ━━━━━━━━━━━━━━━━  CERTIFICATION PAGE  ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.add_page()
    pdf.section_title("Certification & Integrity")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK_TEXT)
    certification_text = (
        "This evidence pack was generated automatically by the CapeControl platform. "
        "It contains a complete record of RAG (Retrieval-Augmented Generation) queries, "
        "document metadata, and provenance data for the specified period.\n\n"
        "All data in this pack is sourced directly from the platform's audit trail "
        "and has not been manually altered. The export ID and timestamp provide a "
        "verifiable reference for this specific export.\n\n"
        "This document is intended for compliance review, regulatory submission, "
        "and internal governance purposes."
    )
    pdf.multi_cell(0, 5, certification_text)
    pdf.ln(8)

    pdf.key_value("Export ID", pack.export_id)
    pdf.key_value("Generated At", pack.exported_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
    pdf.key_value("Exported By", pack.exported_by_email)
    pdf.key_value("Total Queries", str(pack.total_queries))
    pdf.key_value("Total Documents", str(len(pack.documents)))

    # Convert to bytes
    return bytes(pdf.output())
