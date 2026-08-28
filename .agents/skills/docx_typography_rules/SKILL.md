---
name: docx_typography_rules
description: |
  Правила типографики ГОСТ Р 7.0.97-2016 для DOCX-вёрстки юридических документов.
  Активировать при явном упоминании: ГОСТ, типографика, вёрстка, docx, шрифты документа,
  поля документа, форматирование договора, python-docx.
---

# DOCX Typography Rules — ГОСТ Р 7.0.97-2016

Этот скилл описывает **обязательные инварианты** форматирования `.docx` документов
по ГОСТ Р 7.0.97-2016, которые агент ОБЯЗАН соблюдать при генерации или редактировании
кода в `core/rendering/docx_engine.py` и связанных модулях.

## Ключевые файлы проекта

- Основной движок: `core/rendering/docx_engine.py`
- Pydantic-модели: `core/models/base.py`, `core/models/supply.py`, и др.
- Шаблоны: `core/templates/`

## 1. Поля документа (Page Margins)

| Параметр | Значение | python-docx |
|---|---|---|
| Левое поле | 25 мм | `section.left_margin = Mm(25)` |
| Правое поле | 15 мм | `section.right_margin = Mm(15)` |
| Верхнее поле | 20 мм | `section.top_margin = Mm(20)` |
| Нижнее поле | 20 мм | `section.bottom_margin = Mm(20)` |
| Формат листа | A4 (210 × 297 мм) | `Mm(210)` / `Mm(297)` |

**НИКОГДА** не используй другие значения полей — это прямое нарушение ГОСТа.

## 2. Шрифтовая гарнитура

- **Основной шрифт:** Times New Roman
- **Fallback (Linux):** Liberation Serif (метрически идентичен TNR)
- **Константа в коде:** `DocxEngine.FONT_NAME = "Liberation Serif"`

### Обязательная XML-фиксация шрифтов

Каждый `Run` ОБЯЗАН иметь явный `w:rFonts` для **всех четырёх** Unicode-скриптов:

```python
def _apply_rfonts(run, font_name="Liberation Serif"):
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)
    rPr.append(rFonts)
```

**Почему это важно:** Без явной фиксации `w:rFonts` Microsoft Word и LibreOffice
могут подставлять шрифт по умолчанию (Calibri), ломая визуальное соответствие ГОСТу.

## 3. Параметры параграфа

| Параметр | Значение | Код |
|---|---|---|
| Выравнивание | JUSTIFY (по ширине) | `WD_ALIGN_PARAGRAPH.JUSTIFY` |
| Абзацный отступ | 1.25 см (красная строка) | `first_line_indent = Mm(12.5)` |
| Межстрочный интервал | 1.15 | `line_spacing = 1.15` |
| Отступ после параграфа | 4 pt | `space_after = Pt(4)` |
| Отступ перед параграфом | 0 pt | `space_before = Pt(0)` |

### Исключения:
- **Заголовки разделов:** `align=CENTER`, `indent=False`, `space_after=Pt(6)`, `keep_with_next=True`
- **Заголовок документа:** `align=CENTER`, `indent=False`, `font.size=Pt(13)`, `bold=True`
- **Ячейки таблиц:** `indent=False`, `space_after=Pt(0)`

## 4. Защита разметки (Anti-orphan Controls)

### Widow/Orphan Control
КАЖДЫЙ параграф обязан иметь `w:widowControl`:

```python
pPr = p._p.get_or_add_pPr()
widow = OxmlElement("w:widowControl")
pPr.append(widow)
```

### Запрет разрыва строк таблицы (cantSplit)
КАЖДАЯ строка таблицы обязана иметь `w:cantSplit`:

```python
def _set_row_cant_split(row):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    cantSplit = OxmlElement("w:cantSplit")
    trPr.append(cantSplit)
```

### Повторяющаяся шапка таблицы (tblHeader)
ПЕРВАЯ строка (шапка) таблицы обязана иметь `w:tblHeader`:

```python
def _set_row_header(row):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    trPr.append(tblHeader)
```

## 5. Таблицы

- Выравнивание: `WD_TABLE_ALIGNMENT.CENTER`
- Шапка: фон `#EFEFEF` через `w:shd`, шрифт `Pt(10)`, `bold=True`
- Данные: шрифт `Pt(9.5)`
- Внутренние отступы ячеек (`w:tcMar`): через функцию `_set_cell_margins`

## 6. Чек-лист для ревью

При создании или модификации DOCX-генерации, проверь:

- [ ] Поля 25/15/20/20 мм
- [ ] `_apply_rfonts()` вызван для КАЖДОГО `add_run()`
- [ ] `_set_paragraph_gost_format()` вызван для КАЖДОГО параграфа
- [ ] `_set_row_cant_split()` вызван для КАЖДОЙ строки таблицы
- [ ] `_set_row_header()` вызван для шапки таблицы
- [ ] `widowControl` присутствует на уровне XML
- [ ] Размер основного шрифта — `Pt(11.5)`, заголовков — `Pt(12–13)`

## Ссылки

- Подробные XML-сниппеты: `references/xml_snippets.md`
- Эталонная реализация: `core/rendering/docx_engine.py`
