---
name: docx_typography_rules
description: Russian GOST legal document typography rules for python-docx and OXML manipulation
version: 1.0.0
---

# Russian Legal Document Typography Rules (GOST R 7.0.97-2016)

## 1. Page Margins (ГОСТ Р 7.0.97-2016)
- **Left margin**: 2.5 cm (25 mm / 1417 dxa) - binding margin
- **Right margin**: 1.5 cm (15 mm / 850 dxa)
- **Top margin**: 2.0 cm (20 mm / 1134 dxa)
- **Bottom margin**: 2.0 cm (20 mm / 1134 dxa)

## 2. Fonts & Text Runs
- **Primary Typeface**: `Liberation Serif` / `Times New Roman`
- **Mandatory Font Binding (`w:rFonts`)**:
  Every text run style must explicitly define:
  ```xml
  <w:rFonts w:ascii="Liberation Serif" w:hAnsi="Liberation Serif" w:eastAsia="Liberation Serif" w:cs="Liberation Serif"/>
  ```
- **Font Sizes**:
  - Main Body: 11-12 pt
  - Tables: 10 pt
  - Footnotes/Details: 9-10 pt

## 3. Paragraph Formatting
- **Alignment**: `WD_ALIGN_PARAGRAPH.JUSTIFY`
- **First Line Indent (Красная строка)**: `1.25 cm` (709 dxa)
- **Line Spacing**: `1.15` line multiple (`w:line="276" w:lineRule="auto"`)
- **Spacing After Paragraph**: `Pt(4)` (80 dxa)
- **Spacing Before Paragraph**: `Pt(0)`

## 4. Pagination & Anti-Orphan Controls
- **Widow/Orphan Control**: `w:widowControl = True` on all document paragraphs
- **Keep with Next**: `keep_with_next = True` on all heading titles
- **Table Row Protection**:
  - `w:cantSplit = True` on all table rows (`<w:cantSplit/>`) to prevent rows breaking across pages
  - `w:tblHeader = True` on table header rows (`<w:tblHeader/>`) to repeat column titles on page split

## 5. Requisites & Signatures Layout
- **Two-Column Block**:
  - Left column: "ЗАКАЗЧИК" / "ПОКУПАТЕЛЬ" / "СТОРОНА 1"
  - Right column: "ИСПОЛНИТЕЛЬ" / "ПОСТАВЩИК" / "СТОРОНА 2"
  - Borderless table with equal 50% width and padding.
