"""Headless LibreOffice DOCX to PDF Conversion Engine (Fallback)."""

from __future__ import annotations
import os
import shutil
import tempfile
import subprocess
from typing import Optional


class LibreOfficeEngine:
    """Headless LibreOffice converter for DOCX -> PDF."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if libreoffice or soffice executable exists on system."""
        return shutil.which("soffice") is not None or shutil.which("libreoffice") is not None

    @classmethod
    def convert_docx_to_pdf(cls, docx_bytes: bytes) -> Optional[bytes]:
        """Convert in-memory DOCX byte stream to PDF byte stream."""
        bin_name = shutil.which("soffice") or shutil.which("libreoffice")
        if not bin_name:
            return None

        with tempfile.TemporaryDirectory() as tmpdir:
            in_docx = os.path.join(tmpdir, "input.docx")
            with open(in_docx, "wb") as f:
                f.write(docx_bytes)

            cmd = [
                bin_name,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", tmpdir,
                in_docx
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    check=False
                )
                out_pdf = os.path.join(tmpdir, "input.pdf")
                if proc.returncode == 0 and os.path.exists(out_pdf):
                    with open(out_pdf, "rb") as f:
                        return f.read()
            except Exception:
                return None

        return None
