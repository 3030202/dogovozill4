"""Autonomous PyInstaller Build Script for Desktop Application."""

import os
import sys
import subprocess
import shutil


def build():
    print("🚀 Запуск автономной сборки DocGen Desktop Distribution...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    app_script = os.path.join(base_dir, "adapters", "desktop_windows", "app.py")
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")

    # Check if pyinstaller is installed
    pyinstaller_bin = shutil.which("pyinstaller")
    if not pyinstaller_bin:
        # Check in .venv
        venv_pyinstaller = os.path.join(base_dir, ".venv", "bin", "pyinstaller")
        if os.path.exists(venv_pyinstaller):
            pyinstaller_bin = venv_pyinstaller

    if not pyinstaller_bin:
        print("⚠️ PyInstaller не найден в системе. Устанавливаем в виртуальное окружение...")
        pip_bin = os.path.join(base_dir, ".venv", "bin", "pip")
        subprocess.run([pip_bin, "install", "pyinstaller"], check=True)
        pyinstaller_bin = os.path.join(base_dir, ".venv", "bin", "pyinstaller")

    cmd = [
        pyinstaller_bin,
        "--name=DocGen_Platform",
        "--onefile",
        "--noconsole",
        f"--add-data={os.path.join(base_dir, 'core')}:core",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        app_script,
    ]

    print(f"📦 Выполнение команды: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        print(f"✅ Сборка успешно завершена! Исполняемый файл находится в: {dist_dir}")
    else:
        print("❌ Ошибка при сборке дистрибутива.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
