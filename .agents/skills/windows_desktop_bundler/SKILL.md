---
name: windows_desktop_bundler
description: |
  Упаковка DocGen в автономный дистрибутив через PyInstaller.
  Активировать при: сборке, упаковке, build, exe, деплое десктопного приложения,
  PyInstaller, .spec файл, dist, --onefile, --noconsole.
---

# Windows Desktop Bundler — PyInstaller

Этот скилл описывает правила упаковки DocGen Desktop в автономный
исполняемый файл через PyInstaller.

## Ключевые файлы проекта

- GUI-приложение: `adapters/desktop_windows/app.py` (tkinter + ttk)
- Скрипт сборки: `adapters/desktop_windows/build_windows.py`
- Spec-файл (API-версия): `docgen.spec`
- Desktop spec: `adapters/desktop_windows/desktop.spec`

## 1. GUI-фреймворк

- **Используется:** tkinter + ttk (тема `clam`)
- **Тёмная палитра:**
  - Фон: `#1E1E2E`
  - Карточки: `#2A2B3C`
  - Акцент: `#6366F1`
  - Текст: `#E0E0E0`
  - Успех: `#10B981`
  - Ошибка: `#EF4444`

**НЕ мигрировать на PySide6/Qt** без явного решения. tkinter входит в stdlib
и не добавляет зависимостей к сборке.

## 2. Параметры PyInstaller

### Обязательные флаги:

```
--name=DocGen_Platform
--onefile
--noconsole
--add-data=<project_root>/core:core
--add-data=<path_to_typst_binary>:typst
--add-data=<path_to_fonts_dir>:fonts
```

### Описание:

| Флаг | Значение | Обоснование |
|---|---|---|
| `--onefile` | Один исполняемый файл | Простота распространения |
| `--noconsole` | Без окна консоли | UX для конечного пользователя |
| `--name` | `DocGen_Platform` | Единое имя бинарника |
| `--add-data core:core` | Модели, рендеринг, шаблоны | Runtime-зависимость |
| `--add-data typst:typst` | Бинарник typst(.exe) | PDF-рендеринг без внешних зависимостей |
| `--add-data fonts:fonts` | Liberation Serif и др. | ГОСТ-шрифты для DOCX и Typst |

## 3. Встраивание typst и шрифтов

### typst binary

При сборке нужно включить `typst` (или `typst.exe` на Windows) через `--add-data`.
В runtime-коде `typst_engine.py` путь к бинарнику определяется с учётом PyInstaller:

```python
import sys
import os

def _get_typst_path():
    """Определить путь к typst с учётом PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Внутри PyInstaller bundle
        base = sys._MEIPASS
        return os.path.join(base, 'typst', 'typst')
    else:
        # Разработка — typst в PATH
        return 'typst'
```

### Шрифты

Директория шрифтов встраивается аналогично:

```python
def _get_fonts_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'fonts')
    else:
        return os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
```

## 4. Логирование (без консоли)

Поскольку `--noconsole` скрывает stdout/stderr, все логи пишутся в файл:

### Windows
```
%APPDATA%/DocGen/logs/docgen.log
```

### Linux
```
~/.local/share/docgen/logs/docgen.log
```

### Реализация:

```python
import logging
import os
import sys
from pathlib import Path

def setup_logging():
    if sys.platform == 'win32':
        log_dir = Path(os.environ.get('APPDATA', '')) / 'DocGen' / 'logs'
    else:
        log_dir = Path.home() / '.local' / 'share' / 'docgen' / 'logs'

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'docgen.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )
```

## 5. Скрипт сборки (build_windows.py)

Текущий скрипт `adapters/desktop_windows/build_windows.py`:
1. Ищет `pyinstaller` в PATH или `.venv/bin/`
2. Если не найден — устанавливает через pip
3. Запускает `pyinstaller` с нужными параметрами
4. Выходной файл: `dist/DocGen_Platform`

### Что нужно добавить:
- `--add-data` для typst binary
- `--add-data` для директории шрифтов
- Определение пути к typst на текущей платформе

## 6. Spec-файл vs build_windows.py

В проекте два подхода к сборке:

| Файл | Назначение | Формат |
|---|---|---|
| `build_windows.py` | Desktop GUI (tkinter) | `--onefile --noconsole` |
| `docgen.spec` | API-сервер (FastAPI + React) | `--onedir console=True` |

**Не путать!** `docgen.spec` собирает API-версию с `docgen_launcher.py`,
а `build_windows.py` собирает десктопное приложение с `app.py`.

## 7. Чек-лист сборки

- [ ] `pyinstaller` доступен (`.venv/bin/pyinstaller`)
- [ ] `--add-data core:core` — модели и шаблоны включены
- [ ] `--add-data typst:typst` — бинарник typst включён
- [ ] `--add-data fonts:fonts` — ГОСТ-шрифты включены
- [ ] `--noconsole` — консоль скрыта
- [ ] `--onefile` — единый исполняемый файл
- [ ] Логирование настроено в `%APPDATA%/DocGen/logs/`
- [ ] `sys._MEIPASS` используется для поиска ресурсов в frozen-режиме
- [ ] Тест: запуск `dist/DocGen_Platform` на чистой системе

## 8. Кросс-платформенная сборка

PyInstaller **не поддерживает** кросс-компиляцию:
- Для `.exe` (Windows) — запускать `build_windows.py` на Windows
- Для Linux — запускать на Linux
- Для macOS — запускать на macOS

Текущий `build_windows.py` работает на любой ОС, но результат —
бинарник **для текущей платформы**.
