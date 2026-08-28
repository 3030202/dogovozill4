"""ReportLab PDF Generation Engine — GOST R 7.0.97-2016 compliant.

Generates publication-ready PDF contracts with:
- DejaVu Serif font (full Cyrillic support, no external fonts required)
- GOST margins: left 30mm, right 15mm, top/bottom 20mm
- Running header/footer with page numbers
- Justified paragraph text with first-line indent
- Specification tables (supply, lease, work stages)
- Two-column signatures block with QR code
"""

from __future__ import annotations
import io
import os
import qrcode
import qrcode.image.pil

from typing import List, Dict, Any, Optional, Tuple
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, HexColor, black, white, grey
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, KeepTogether,
    Image as RLImage, HRFlowable,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from core.models.base import BaseContract
from core.models.supply import SupplyContract
from core.models.work import WorkContract
from core.models.lease import LeaseContract
from core.models.freelance import FreelanceContract
from core.models.license_sw import LicenseSWContract
from core.templates.registry import ContractRegistry
from core.num_to_words import format_rubles


# ---------------------------------------------------------------------------
# Font Registration
# ---------------------------------------------------------------------------

FONT_DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

_FONTS_REGISTERED = False


def _register_fonts() -> str:
    """Register DejaVu Serif TTF fonts and return base font name."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return "DejaVuSerif"

    if os.path.exists(FONT_DEJAVU_REGULAR):
        pdfmetrics.registerFont(TTFont("DejaVuSerif", FONT_DEJAVU_REGULAR))
        if os.path.exists(FONT_DEJAVU_BOLD):
            pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", FONT_DEJAVU_BOLD))
        _FONTS_REGISTERED = True
        return "DejaVuSerif"

    # Fallback to built-in Times (no Cyrillic) — shouldn't happen on this system
    return "Times-Roman"


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------

COLOR_TITLE = HexColor("#1A1A2E")          # deep navy
COLOR_SECTION_HEADER = HexColor("#16213E") # dark blue for section titles
COLOR_TABLE_HEADER = HexColor("#E8EAEF")   # light grey table header
COLOR_TABLE_ALT = HexColor("#F8F9FB")      # alternating row tint
COLOR_RULE = HexColor("#CBD5E1")           # divider line colour
COLOR_QR_BOX = HexColor("#F1F5F9")         # QR background


# ---------------------------------------------------------------------------
# Style Factory
# ---------------------------------------------------------------------------

def _build_styles(font_name: str) -> Dict[str, ParagraphStyle]:
    bold_name = f"{font_name}-Bold" if f"{font_name}-Bold" in pdfmetrics.getRegisteredFontNames() else font_name

    styles: Dict[str, ParagraphStyle] = {}

    styles["title"] = ParagraphStyle(
        "title",
        fontName=bold_name,
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=COLOR_TITLE,
    )

    styles["subtitle"] = ParagraphStyle(
        "subtitle",
        fontName=font_name,
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=2,
        textColor=HexColor("#64748B"),
    )

    styles["city_date"] = ParagraphStyle(
        "city_date",
        fontName=font_name,
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
    )

    styles["preamble"] = ParagraphStyle(
        "preamble",
        fontName=font_name,
        fontSize=11,
        leading=15.4,
        alignment=TA_JUSTIFY,
        firstLineIndent=12.5 * mm,
        spaceAfter=4,
    )

    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        fontName=bold_name,
        fontSize=11.5,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=4,
        textColor=COLOR_SECTION_HEADER,
    )

    styles["clause"] = ParagraphStyle(
        "clause",
        fontName=font_name,
        fontSize=11,
        leading=15.4,
        alignment=TA_JUSTIFY,
        firstLineIndent=12.5 * mm,
        spaceAfter=3,
    )

    styles["clause_num"] = ParagraphStyle(
        "clause_num",
        fontName=bold_name,
        fontSize=11,
        leading=15.4,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
    )

    styles["table_header"] = ParagraphStyle(
        "table_header",
        fontName=bold_name,
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
    )

    styles["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName=font_name,
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
    )

    styles["table_cell_center"] = ParagraphStyle(
        "table_cell_center",
        fontName=font_name,
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
    )

    styles["table_cell_right"] = ParagraphStyle(
        "table_cell_right",
        fontName=font_name,
        fontSize=9,
        leading=11,
        alignment=TA_RIGHT,
    )

    styles["sig_header"] = ParagraphStyle(
        "sig_header",
        fontName=bold_name,
        fontSize=11.5,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=6,
        textColor=COLOR_SECTION_HEADER,
    )

    styles["sig_bold"] = ParagraphStyle(
        "sig_bold",
        fontName=bold_name,
        fontSize=10,
        leading=13,
        spaceAfter=1,
    )

    styles["sig_normal"] = ParagraphStyle(
        "sig_normal",
        fontName=font_name,
        fontSize=10,
        leading=13,
        spaceAfter=1,
    )

    styles["sig_line"] = ParagraphStyle(
        "sig_line",
        fontName=font_name,
        fontSize=10,
        leading=14,
        spaceAfter=0,
    )

    styles["footer"] = ParagraphStyle(
        "footer",
        fontName=font_name,
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=HexColor("#94A3B8"),
    )

    return styles


# ---------------------------------------------------------------------------
# Header / Footer canvas callbacks
# ---------------------------------------------------------------------------

def _make_on_page(contract_title: str, contract_number: str, font_name: str):
    """Factory for ReportLab page callbacks (header + footer)."""
    bold_name = f"{font_name}-Bold" if f"{font_name}-Bold" in pdfmetrics.getRegisteredFontNames() else font_name

    def _on_page(canvas, doc):
        canvas.saveState()
        w, h = A4

        # ── Header ─────────────────────────────────────────────────────────
        header_y = h - 14 * mm
        canvas.setFont(font_name, 8)
        canvas.setFillColor(HexColor("#94A3B8"))
        canvas.drawString(30 * mm, header_y, contract_title)
        canvas.drawRightString(w - 15 * mm, header_y, f"№ {contract_number}")

        # thin rule under header
        canvas.setStrokeColor(COLOR_RULE)
        canvas.setLineWidth(0.4)
        canvas.line(30 * mm, header_y - 2 * mm, w - 15 * mm, header_y - 2 * mm)

        # ── Footer ─────────────────────────────────────────────────────────
        footer_y = 12 * mm
        canvas.setFont(font_name, 8)
        canvas.setFillColor(HexColor("#94A3B8"))
        page_num = doc.page
        canvas.drawCentredString(w / 2, footer_y, f"Стр. {page_num}")

        # thin rule above footer
        canvas.line(30 * mm, footer_y + 4 * mm, w - 15 * mm, footer_y + 4 * mm)

        canvas.restoreState()

    return _on_page


# ---------------------------------------------------------------------------
# QR Code helper
# ---------------------------------------------------------------------------

def _make_qr_image(contract: BaseContract) -> Optional[io.BytesIO]:
    """Generate QR code PNG with contract INN + number."""
    try:
        data = (
            f"ИНН:{contract.client.inn} "
            f"Договор:{contract.metadata.contract_number} "
            f"Дата:{contract.metadata.contract_date}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=3,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Specification table builder
# ---------------------------------------------------------------------------

def _build_spec_table(contract: BaseContract, styles: Dict[str, ParagraphStyle]) -> Optional[Table]:
    """Build a specification table for supply/lease/work contract types."""
    font_name_bold = "DejaVuSerif-Bold" if "DejaVuSerif-Bold" in pdfmetrics.getRegisteredFontNames() else "DejaVuSerif"

    if isinstance(contract, SupplyContract) and contract.items:
        header = [
            Paragraph("№", styles["table_header"]),
            Paragraph("Наименование товара", styles["table_header"]),
            Paragraph("Ед.", styles["table_header"]),
            Paragraph("Кол-во", styles["table_header"]),
            Paragraph("Цена (руб.)", styles["table_header"]),
            Paragraph("Сумма (руб.)", styles["table_header"]),
        ]
        data = [header]
        for i, item in enumerate(contract.items, 1):
            data.append([
                Paragraph(str(i), styles["table_cell_center"]),
                Paragraph(item.name, styles["table_cell"]),
                Paragraph(item.unit, styles["table_cell_center"]),
                Paragraph(str(item.quantity), styles["table_cell_center"]),
                Paragraph(format_rubles(item.price_per_unit), styles["table_cell_right"]),
                Paragraph(format_rubles(item.total_price), styles["table_cell_right"]),
            ])
        # Total row
        data.append([
            Paragraph("", styles["table_cell"]),
            Paragraph("", styles["table_cell"]),
            Paragraph("", styles["table_cell"]),
            Paragraph("", styles["table_cell"]),
            Paragraph("<b>ИТОГО:</b>", styles["table_header"]),
            Paragraph(format_rubles(contract.total_amount), styles["table_header"]),
        ])
        col_widths = [18*mm, None, 16*mm, 18*mm, 30*mm, 30*mm]

    elif isinstance(contract, WorkContract) and contract.stages:
        header = [
            Paragraph("Этап", styles["table_header"]),
            Paragraph("Наименование работ", styles["table_header"]),
            Paragraph("Сроки", styles["table_header"]),
            Paragraph("Стоимость (руб.)", styles["table_header"]),
        ]
        data = [header]
        for stage in contract.stages:
            data.append([
                Paragraph(f"№ {stage.stage_number}", styles["table_cell_center"]),
                Paragraph(stage.title, styles["table_cell"]),
                Paragraph(f"{stage.start_date} – {stage.end_date}", styles["table_cell_center"]),
                Paragraph(format_rubles(stage.cost), styles["table_cell_right"]),
            ])
        data.append([
            Paragraph("", styles["table_cell"]),
            Paragraph("", styles["table_cell"]),
            Paragraph("<b>ИТОГО:</b>", styles["table_header"]),
            Paragraph(format_rubles(contract.total_amount), styles["table_header"]),
        ])
        col_widths = [18*mm, None, 38*mm, 35*mm]

    elif isinstance(contract, LeaseContract):
        obj = contract.lease_object
        terms = contract.lease_terms
        header = [
            Paragraph("Параметр", styles["table_header"]),
            Paragraph("Значение", styles["table_header"]),
        ]
        rows = [
            ("Наименование", obj.name),
            ("Инв. / серийный №", obj.inventory_number or "—"),
            ("Местонахождение", obj.location),
            ("Состояние", obj.condition),
            ("Ежемесячная арендная плата", f"{format_rubles(terms.monthly_rent_rubles)} руб."),
            ("Срок аренды", f"{terms.rent_period_months} мес."),
            ("Обеспечительный платёж", f"{terms.security_deposit_months} × мес. платёж"),
        ]
        data = [header] + [
            [Paragraph(k, styles["table_cell"]), Paragraph(v, styles["table_cell"])]
            for k, v in rows
        ]
        col_widths = [55*mm, None]

    elif isinstance(contract, FreelanceContract) and contract.tasks:
        header = [
            Paragraph("№", styles["table_header"]),
            Paragraph("Задание / результат", styles["table_header"]),
            Paragraph("Срок (р.д.)", styles["table_header"]),
            Paragraph("Стоимость (руб.)", styles["table_header"]),
        ]
        data = [header]
        for i, task in enumerate(contract.tasks, 1):
            data.append([
                Paragraph(str(i), styles["table_cell_center"]),
                Paragraph(task.name, styles["table_cell"]),
                Paragraph(str(task.deadline_days) if task.deadline_days else "—", styles["table_cell_center"]),
                Paragraph(format_rubles(task.cost), styles["table_cell_right"]),
            ])
        data.append([
            Paragraph("", styles["table_cell"]),
            Paragraph("", styles["table_cell"]),
            Paragraph("<b>ИТОГО:</b>", styles["table_header"]),
            Paragraph(format_rubles(contract.total_amount), styles["table_header"]),
        ])
        col_widths = [14*mm, None, 24*mm, 35*mm]

    else:
        return None

    # Available text width: A4 width - margins
    text_width = A4[0] - 30 * mm - 15 * mm  # 165mm

    # Fill None column with remaining width
    fixed = sum(w for w in col_widths if w is not None)
    num_none = sum(1 for w in col_widths if w is None)
    if num_none > 0:
        fill_w = (text_width - fixed) / num_none
        col_widths = [fill_w if w is None else w for w in col_widths]

    tbl = Table(data, colWidths=col_widths, repeatRows=1)

    n_rows = len(data)
    n_cols = len(col_widths)
    tbl_style = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        # Borders
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, HexColor("#E2E8F0")),
        # Alternating rows
        *[("BACKGROUND", (0, row), (-1, row), COLOR_TABLE_ALT)
          for row in range(1, n_rows, 2)],
        # Total / last row bold
        ("FONTNAME", (0, n_rows - 1), (-1, n_rows - 1), font_name_bold),
        ("BACKGROUND", (0, n_rows - 1), (-1, n_rows - 1), COLOR_TABLE_HEADER),
        # Padding
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    tbl.setStyle(TableStyle(tbl_style))
    return tbl


# ---------------------------------------------------------------------------
# Signature block builder
# ---------------------------------------------------------------------------

def _build_signatures_table(
    contract: BaseContract,
    signatures: Dict[str, Any],
    styles: Dict[str, ParagraphStyle],
    qr_buf: Optional[io.BytesIO],
) -> Table:
    """Build two-column signatures block with optional QR code."""

    def _party_cell(sig: Dict[str, Any], is_client: bool) -> List[Paragraph]:
        lines = []
        lines.append(Paragraph(f"<b>{sig['role_title']}</b>", styles["sig_bold"]))
        lines.append(Paragraph(f"<b>{sig['party_name']}</b>", styles["sig_bold"]))
        for detail in sig.get("details_lines", [])[1:]:
            if detail.strip():
                lines.append(Paragraph(detail, styles["sig_normal"]))
        lines.append(Spacer(1, 5 * mm))
        lines.append(Paragraph(f"{sig['signatory_position']}:", styles["sig_normal"]))
        lines.append(Paragraph(
            "_________________ &nbsp;&nbsp; / &nbsp;" + sig["signatory_name"] + " /",
            styles["sig_line"]
        ))
        lines.append(Spacer(1, 3 * mm))
        lines.append(Paragraph("<b>М.П.</b>", styles["sig_bold"]))
        return lines

    client_content = _party_cell(signatures["client"], is_client=True)
    vendor_content = _party_cell(signatures["vendor"], is_client=False)

    client_cell = client_content
    vendor_cell = vendor_content

    # If QR code available, embed it in vendor column bottom-right
    if qr_buf:
        try:
            qr_img = RLImage(qr_buf, width=20 * mm, height=20 * mm)
            vendor_cell = vendor_content + [Spacer(1, 2 * mm), qr_img]
        except Exception:
            pass

    data = [[client_cell, vendor_cell]]
    col_w = (A4[0] - 30 * mm - 15 * mm - 10 * mm) / 2  # half with gutter

    tbl = Table(data, colWidths=[col_w, col_w], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("INNERGRID", (0, 0), (-1, -1), 0, white),  # no internal borders
        ("BOX", (0, 0), (-1, -1), 0, white),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# Main PDFEngine class
# ---------------------------------------------------------------------------

class PDFEngine:
    """ReportLab-based PDF generation engine (GOST R 7.0.97-2016)."""

    @classmethod
    def generate(cls, contract: BaseContract) -> io.BytesIO:
        """Generate GOST-compliant PDF and return as BytesIO."""
        font_name = _register_fonts()
        styles = _build_styles(font_name)

        doc_structure = ContractRegistry.assemble_document_structure(contract)
        header = doc_structure["header"]
        metadata = doc_structure["metadata"]
        signatures = doc_structure["signatures"]

        contract_title = header["title"]
        contract_number = metadata.get("contract_number", "")

        buf = io.BytesIO()

        # Page size and margins (GOST: left 30mm, right 15mm, top/bottom 20mm)
        page_w, page_h = A4
        margin_left = 30 * mm
        margin_right = 15 * mm
        margin_top = 20 * mm
        margin_bottom = 20 * mm
        # Extra space for header/footer
        header_h = 8 * mm
        footer_h = 8 * mm

        frame = Frame(
            margin_left,
            margin_bottom + footer_h,
            page_w - margin_left - margin_right,
            page_h - margin_top - margin_bottom - header_h - footer_h,
            id="main",
            showBoundary=0,
        )

        on_page = _make_on_page(contract_title, contract_number, font_name)
        page_template = PageTemplate(id="gost", frames=[frame], onPage=on_page)

        doc = BaseDocTemplate(
            buf,
            pagesize=A4,
            pageTemplates=[page_template],
            title=contract_title,
            author="DocGen Omnichannel Platform",
            subject=f"Договор № {contract_number}",
            leftMargin=margin_left,
            rightMargin=margin_right,
            topMargin=margin_top + header_h,
            bottomMargin=margin_bottom + footer_h,
        )

        story = []

        # ── Document title ──────────────────────────────────────────────────
        story.append(Paragraph(contract_title, styles["title"]))
        story.append(Spacer(1, 1 * mm))

        # City + Date side by side
        city = header.get("city", "г. Москва")
        date = header.get("date", "")
        city_date_data = [[
            Paragraph(city, styles["city_date"]),
            Paragraph(f"«{date}»", ParagraphStyle(
                "city_date_right",
                parent=styles["city_date"],
                alignment=TA_RIGHT,
            )),
        ]]
        text_width = page_w - margin_left - margin_right
        city_date_tbl = Table(city_date_data, colWidths=[text_width / 2, text_width / 2])
        city_date_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("BOX", (0, 0), (-1, -1), 0, white),
            ("INNERGRID", (0, 0), (-1, -1), 0, white),
        ]))
        story.append(city_date_tbl)
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=4))
        story.append(Spacer(1, 2 * mm))

        # ── Preamble ────────────────────────────────────────────────────────
        preamble_text = header.get("text", "")
        story.append(Paragraph(preamble_text, styles["preamble"]))
        story.append(Spacer(1, 4 * mm))

        # ── Sections ────────────────────────────────────────────────────────
        for section in doc_structure["sections"]:
            sec_block = []
            sec_block.append(Paragraph(
                f'{section["section_num"]}. {section["title"]}',
                styles["section_heading"]
            ))

            for clause in section["clauses"]:
                # Format: bold number + normal text in same paragraph
                clause_para = Paragraph(
                    f'<b>{clause["num"]}.</b>&nbsp;&nbsp;{clause["text"]}',
                    styles["clause"]
                )
                sec_block.append(clause_para)

            story.append(KeepTogether(sec_block[:3]))  # keep heading with first 3 clauses
            # Append remaining clauses individually
            for item in sec_block[3:]:
                story.append(item)

            # Specification table after Section 1
            if section["section_num"] == "1":
                spec_table = _build_spec_table(contract, styles)
                if spec_table:
                    story.append(Spacer(1, 3 * mm))
                    story.append(spec_table)
                    story.append(Spacer(1, 3 * mm))

        # ── Signatures block ────────────────────────────────────────────────
        story.append(Spacer(1, 6 * mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceBefore=2))
        story.append(Paragraph("РЕКВИЗИТЫ И ПОДПИСИ СТОРОН", styles["sig_header"]))
        story.append(Spacer(1, 3 * mm))

        qr_buf = _make_qr_image(contract)
        sig_table = _build_signatures_table(contract, signatures, styles, qr_buf)
        story.append(sig_table)

        doc.build(story)
        buf.seek(0)
        return buf
