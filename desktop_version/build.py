#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import sys
from PyInstaller.__main__ import run


def add_data_arg(source: str, target: str) -> str:
    # 中文：PyInstaller 在 Windows 与类 Unix 系统使用不同分隔符，集中封装避免手写配置出错。
    # English: PyInstaller uses different data separators on Windows and Unix-like systems, so centralizing this avoids platform mistakes.
    sep = ";" if platform.system() == "Windows" else ":"
    return f"{source}{sep}{target}"


def build_app():
    system = platform.system()
    if system == "Windows":
        build_windows()
    elif system == "Darwin":
        build_macos()
    elif system == "Linux":
        build_linux()
    else:
        print(f"不支持的平台: {system}")
        sys.exit(1)


def common_opts(name: str, icon: str):
    return [
        "main.py",
        f"--name={name}",
        "--windowed",
        "--onefile",
        f"--icon={icon}",
        f"--add-data={add_data_arg('resources', 'resources')}",
        "--clean",
        "--noconfirm",
    ]


def build_windows():
    print("构建 Windows PyQt5 桌面版...")
    run(common_opts("ShortDramaSearch", "resources/icons/API.ico"))


def build_macos():
    print("构建 macOS PyQt5 桌面版...")
    run(common_opts("ShortDramaSearch", "resources/icons/API.icns"))


def build_linux():
    print("构建 Linux PyQt5 桌面版...")
    run(common_opts("short-drama-search", "resources/icons/API.png"))


if __name__ == "__main__":
    build_app()
