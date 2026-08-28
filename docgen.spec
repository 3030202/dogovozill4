# -*- mode: python ; coding: utf-8 -*-
# DocGen PyInstaller Spec
# Собирает: FastAPI backend + встроенный React dist/ + все зависимости
# Результат: dist/DocGen/DocGen (Linux) или dist/DocGen/DocGen.exe (Windows)

import sys
from pathlib import Path

ROOT = Path(SPECPATH)  # каталог этого .spec файла = корень проекта

block_cipher = None

# ── Данные (статика, шрифты, templates) ─────────────────────────────────
added_datas = [
    # React build
    (str(ROOT / 'adapters' / 'web_ui' / 'dist'), 'web_dist'),
    # Python пакеты проекта
    (str(ROOT / 'core'),     'core'),
    (str(ROOT / 'adapters'), 'adapters'),
    # Шрифты ReportLab (могут быть в .venv)
    (str(ROOT / '.venv' / 'lib'), 'lib'),
]

# Фильтруем несуществующие пути
added_datas = [(src, dst) for src, dst in added_datas if Path(src).exists()]

# ── Hidden imports (динамически загружаемые модули) ────────────────────
hidden_imports = [
    # FastAPI / Starlette
    'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan', 'uvicorn.lifespan.on',
    'fastapi', 'starlette', 'starlette.staticfiles', 'starlette.responses',
    'anyio', 'anyio._backends._asyncio',
    # Pydantic
    'pydantic', 'pydantic.v1', 'pydantic_core',
    # python-docx
    'docx', 'docx.oxml', 'docx.oxml.ns',
    'lxml', 'lxml._elementpath',
    # ReportLab
    'reportlab', 'reportlab.pdfgen', 'reportlab.lib', 'reportlab.platypus',
    'reportlab.pdfbase', 'reportlab.pdfbase.ttfonts', 'reportlab.pdfbase.pdfmetrics',
    # PIL
    'PIL', 'PIL.Image',
    # stdlib async
    'asyncio', 'email', 'email.mime', 'email.mime.text',
    # project modules
    'adapters.api.server',
    'adapters.api.routes.contracts',
    'adapters.api.routes.drafts',
    'core.templates.registry',
    'core.rendering.pdf_engine',
    'core.rendering.docx_engine',
    'core.validator',
    'core.models.stance',
]

a = Analysis(
    [str(ROOT / 'docgen_launcher.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DocGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # True = показывает консоль (удобно для отладки)
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DocGen',
)
