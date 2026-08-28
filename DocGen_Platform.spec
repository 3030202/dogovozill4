# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['//wsl.localhost/Ubuntu/home/mx/dogovozill4/adapters/desktop_windows/app.py'],
    pathex=[],
    binaries=[],
    datas=[('//wsl.localhost/Ubuntu/home/mx/dogovozill4/core', 'core')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DocGen_Platform',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
