# Workflow: BUILD_ALL_TARGETS

Protocol for running test suites and building multi-platform distribution targets.

## Execution Sequence:
1. **Core Unit & Regression Tests**:
   ```bash
   .venv/bin/pytest tests/ -v
   ```
2. **Web SPA Build**:
   ```bash
   cd adapters/web_ui && npm run build
   ```
3. **Desktop Windows Standalone Executable**:
   ```bash
   .venv/bin/python adapters/desktop_windows/build_windows.py
   ```
4. **Smoke Document Output Generation**:
   - Generate test sample files (Supply, Services, Work, NDA) in `.docx` and `.pdf` format.
   - Verify non-empty byte streams and valid document headers (`PK\x03\x04` for docx, `%PDF` for pdf).
