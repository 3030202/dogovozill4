"""
DocGen — самозапускаемый дистрибутив.

Запускает встроенный FastAPI-сервер и открывает браузер.
Работает как единый исполняемый файл (PyInstaller bundle).
"""
from __future__ import annotations

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
from pathlib import Path


# ── Определяем базовый путь (внутри bundle или из исходников) ─────────
def base_path() -> Path:
    """Корневой путь для данных (dist/, storage/, ...) внутри бандла."""
    if getattr(sys, 'frozen', False):
        # PyInstaller извлекает файлы во временную папку _MEIPASS
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).parent


def storage_path() -> Path:
    """Папка storage — рядом с exe, не внутри bundle (данные сохраняются)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "storage"
    return base_path() / "storage"


# ── Настраиваем пути до запуска FastAPI ───────────────────────────────
os.environ.setdefault("DOCGEN_STORAGE_DIR", str(storage_path()))
os.environ.setdefault("DOCGEN_STATIC_DIR",  str(base_path() / "web_dist"))


def find_free_port(start: int = 8001) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start


def wait_for_server(port: int, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def open_browser(port: int) -> None:
    if wait_for_server(port):
        webbrowser.open(f"http://127.0.0.1:{port}")
    else:
        print(f"[DocGen] Сервер не ответил на порту {port} за 15 сек.")


def run_server(port: int) -> None:
    """Запускает uvicorn в текущем процессе (блокирует)."""
    import uvicorn
    # Добавляем корень проекта в sys.path если нужно
    root = str(base_path())
    if root not in sys.path:
        sys.path.insert(0, root)

    uvicorn.run(
        "adapters.api.server:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )


def main() -> None:
    port = find_free_port(8001)
    print(f"[DocGen] Запуск на http://127.0.0.1:{port}")

    # Гарантируем существование папки storage
    storage_path().mkdir(parents=True, exist_ok=True)
    (storage_path() / "drafts").mkdir(parents=True, exist_ok=True)

    # Открываем браузер в фоне — ждём пока сервер поднимется
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()

    # Запускаем сервер (блокирует до Ctrl+C / закрытия)
    run_server(port)


if __name__ == "__main__":
    main()
