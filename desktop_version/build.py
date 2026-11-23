#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import platform
import sys
from PyInstaller.__main__ import run

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent


def add_data_arg(source: Path, target: str) -> str:
    sep = ";" if platform.system() == "Windows" else ":"
    return f"{source}{sep}{target}"


def common_opts(name: str, icon_rel: str, onefile: bool = True):
    opts = [
        str(BASE_DIR / "main.py"),
        f"--name={name}",
        "--windowed",
        "--onefile" if onefile else "--onedir",
        f"--icon={BASE_DIR / icon_rel}",
        f"--add-data={add_data_arg(BASE_DIR / 'resources', 'resources')}",
        f"--add-data={add_data_arg(REPO_ROOT / 'shared', 'shared')}",
        f"--paths={BASE_DIR}",
        f"--paths={REPO_ROOT}",
        "--hidden-import=PyQt5.QtSvg",
        "--exclude-module=tkinter",
        "--exclude-module=PyQt5.QtWebEngineWidgets",
        "--clean",
        "--noconfirm",
    ]
    return opts


def build_app():
    system = platform.system()
    if system == "Windows":
        print("构建 Windows PyQt5 桌面版...")
        run(common_opts("ShortDramaSearch", "resources/icons/API.ico", onefile=True))
    elif system == "Darwin":
        print("构建 macOS PyQt5 桌面版...")
        opts = common_opts("ShortDramaSearch", "resources/icons/API.icns", onefile=False)
        opts.append("--osx-bundle-identifier=com.shortdramasearch.desktop")
        run(opts)
    elif system == "Linux":
        print("构建 Linux PyQt5 桌面版...")
        run(common_opts("short-drama-search", "resources/icons/API.png", onefile=True))
    else:
        print(f"不支持的平台: {system}")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
