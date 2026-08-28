# XML-сниппеты ГОСТ-форматирования (OOXML / python-docx)

Эталонные XML-паттерны, извлечённые из `core/rendering/docx_engine.py`.
Агент должен использовать эти паттерны при генерации нового DOCX-кода.

## 1. Привязка шрифта (`w:rFonts`)

Обязательно для **каждого** `Run` в документе.

### Python-код
```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

rPr = run._r.get_or_add_rPr()
rFonts = OxmlElement("w:rFonts")
rFonts.set(qn("w:ascii"), "Liberation Serif")    # Латиница
rFonts.set(qn("w:hAnsi"), "Liberation Serif")    # Расширенная латиница
rFonts.set(qn("w:cs"), "Liberation Serif")       # Complex scripts (арабские и т.д.)
rFonts.set(qn("w:eastAsia"), "Liberation Serif") # CJK
rPr.append(rFonts)
```

### Результирующий XML
```xml
<w:rPr>
  <w:rFonts w:ascii="Liberation Serif"
            w:hAnsi="Liberation Serif"
            w:cs="Liberation Serif"
            w:eastAsia="Liberation Serif"/>
</w:rPr>
```

---

## 2. Контроль вдов/сирот (`w:widowControl`)

Предотвращает отрыв одиночных строк на границе страницы.

### Python-код
```python
pPr = p._p.get_or_add_pPr()
widow = OxmlElement("w:widowControl")
pPr.append(widow)
```

### Результирующий XML
```xml
<w:pPr>
  <w:widowControl/>
</w:pPr>
```

---

## 3. Запрет разрыва строки таблицы (`w:cantSplit`)

Строка таблицы не будет разорвана между страницами.

### Python-код
```python
tr = row._tr
trPr = tr.get_or_add_trPr()
cantSplit = OxmlElement("w:cantSplit")
trPr.append(cantSplit)
```

### Результирующий XML
```xml
<w:trPr>
  <w:cantSplit/>
</w:trPr>
```

---

## 4. Повторяющаяся шапка таблицы (`w:tblHeader`)

При разрыве таблицы между страницами, шапка автоматически повторяется.

### Python-код
```python
tr = row._tr
trPr = tr.get_or_add_trPr()
tblHeader = OxmlElement("w:tblHeader")
trPr.append(tblHeader)
```

### Результирующий XML
```xml
<w:trPr>
  <w:tblHeader/>
</w:trPr>
```

---

## 5. Внутренние отступы ячейки (`w:tcMar`)

### Python-код
```python
def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Значения в dxa (1 мм ≈ 56.7 dxa)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)
```

### Результирующий XML
```xml
<w:tcPr>
  <w:tcMar>
    <w:top w:w="100" w:type="dxa"/>
    <w:bottom w:w="100" w:type="dxa"/>
    <w:left w:w="150" w:type="dxa"/>
    <w:right w:w="150" w:type="dxa"/>
  </w:tcMar>
</w:tcPr>
```

---

## 6. Заливка ячейки шапки (`w:shd`)

### Python-код
```python
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EFEFEF"/>')
cell._tc.get_or_add_tcPr().append(shading)
```

### Результирующий XML
```xml
<w:tcPr>
  <w:shd w:fill="EFEFEF"/>
</w:tcPr>
```

---

## 7. Полное форматирование ГОСТ-параграфа

### Python-код
```python
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def _set_paragraph_gost_format(p, indent=True, space_after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if indent:
        p.paragraph_format.first_line_indent = Mm(12.5)  # 1.25 см

    # Widow/orphan control
    pPr = p._p.get_or_add_pPr()
    widow = OxmlElement("w:widowControl")
    pPr.append(widow)
```

---

## 8. Страничная разметка (Section Properties)

### Python-код
```python
from docx.shared import Mm

section = doc.sections[0]
section.left_margin = Mm(25)
section.right_margin = Mm(15)
section.top_margin = Mm(20)
section.bottom_margin = Mm(20)
section.page_width = Mm(210)   # A4
section.page_height = Mm(297)  # A4
```
