---
name: windows_desktop_bundler
description: Specification for bundling and packaging the desktop application into standalone Windows .exe
version: 1.0.0
---

# Windows Desktop Bundler Specification

## 1. GUI Implementation
- Modern desktop UI with clean styling, typography, dark/light theme support.
- Native file dialogs for saving `.docx` and `.pdf` files.
- Real-time validation badges for INN/BIK.

## 2. PyInstaller Packaging Rules
- Use PyInstaller with custom `.spec` file.
- Flags: `--noconsole` for clean Windows execution, `--onefile` or directory bundle.
- Bundle asset directories: fonts, icons, default clauses, Typst standalone binary.
- Absolute path normalization using `sys._MEIPASS` when running in bundled frozen state.
