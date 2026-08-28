@echo off
setlocal EnableDelayedExpansion
title DocGen — Генератор договоров

:: ── DocGen Windows Launcher ──────────────────────────────────────────
:: Этот bat-файл при первом запуске:
::   1. Проверяет наличие Python 3.10+
::   2. Создаёт venv если нет
::   3. Устанавливает зависимости
::   4. Запускает сервер и открывает браузер

set "DOCGEN_DIR=%~dp0"
set "VENV_DIR=%DOCGEN_DIR%.venv_win"
set "PORT=8001"

echo.
echo  ██████╗  ██████╗  ██████╗ ██████╗ ███████╗███╗   ██╗
echo  ██╔══██╗██╔═══██╗██╔════╝██╔════╝ ██╔════╝████╗  ██║
echo  ██║  ██║██║   ██║██║     ██║  ███╗█████╗  ██╔██╗ ██║
echo  ██║  ██║██║   ██║██║     ██║   ██║██╔══╝  ██║╚██╗██║
echo  ██████╔╝╚██████╔╝╚██████╗╚██████╔╝███████╗██║ ╚████║
echo  ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝
echo.
echo  Генератор юридических договоров РФ v1.0
echo  Zero-LLM · ГОСТ Р 7.0.97-2016
echo  ════════════════════════════════════════
echo.

:: ── Проверка Python ────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.10+ с https://python.org
    echo Убедитесь что галочка "Add to PATH" отмечена при установке.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% найден

:: ── Создание виртуального окружения ──────────────────────────────────
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Создание виртуального окружения...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать venv
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"

:: ── Установка зависимостей ────────────────────────────────────────────
if not exist "%VENV_DIR%\Scripts\uvicorn.exe" (
    echo [INFO] Установка зависимостей (первый запуск, ~2 мин)...
    pip install --quiet --upgrade pip
    pip install --quiet ^
        fastapi uvicorn[standard] ^
        python-docx lxml ^
        reportlab Pillow ^
        pydantic aiofiles ^
        python-multipart
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости
        pause
        exit /b 1
    )
    echo [OK] Зависимости установлены
)

:: ── Проверка занятости порта ──────────────────────────────────────────
netstat -an | find ":%PORT% " | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
    set /a PORT=%PORT%+1
    echo [INFO] Порт 8001 занят, используем %PORT%
)

:: ── Запуск сервера в фоне ─────────────────────────────────────────────
echo [INFO] Запуск сервера на http://127.0.0.1:%PORT%
cd /d "%DOCGEN_DIR%"
start /b "" python -m uvicorn adapters.api.server:app --host 127.0.0.1 --port %PORT% --log-level warning

:: ── Ждём запуска и открываем браузер ─────────────────────────────────
echo [INFO] Открытие браузера...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:%PORT%"

echo.
echo  ════════════════════════════════════════
echo  DocGen запущен: http://127.0.0.1:%PORT%
echo  Закройте это окно чтобы остановить сервер.
echo  ════════════════════════════════════════
echo.

:: Держим окно открытым (сервер работает пока открыто окно)
:loop
timeout /t 5 /nobreak >nul
netstat -an | find ":%PORT% " | find "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Сервер остановился. Перезапустить? (Y/N)
    choice /c YN /t 10 /d N
    if !errorlevel!==1 goto :start_server
    goto :end
)
goto :loop

:start_server
python -m uvicorn adapters.api.server:app --host 127.0.0.1 --port %PORT% --log-level warning
goto :loop

:end
deactivate
endlocal
