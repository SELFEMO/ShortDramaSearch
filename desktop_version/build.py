#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
from PyInstaller.__main__ import run


def build_app():
    """构建应用程序"""

    # 平台特定配置
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


def build_windows():
    """构建Windows版本"""
    print("构建Windows版本...")

    opts = [
        'main.py',
        '--name=ShortDramaSearch',
        '--windowed',
        '--onefile',
        # '--icon=resources/icons/app.ico',  # Windows图标
        '--icon=resources/icons/API.ico',  # Windows图标
        '--add-data=resources;resources',  # 包含所有资源文件
        '--add-data=ui:ui',  # 包含UI模块
        '--add-data=core:core',  # 包含核心模块
        '--clean',
        '--noconfirm'
    ]

    run(opts)


def build_macos():
    """构建macOS版本"""
    print("构建macOS版本...")

    opts = [
        'main.py',
        '--name=ShortDramaSearch',
        '--windowed',
        '--onefile',
        # '--icon=resources/icons/app.icns',  # macOS图标
        '--icon=resources/icons/API.icns',  # macOS图标
        '--add-data=resources:resources',  # 包含所有资源文件
        '--add-data=ui:ui',  # 包含UI模块
        '--add-data=core:core',  # 包含核心模块
        '--clean',
        '--noconfirm'
    ]

    run(opts)


def build_linux():
    """构建Linux版本"""
    print("构建Linux版本...")

    opts = [
        'main.py',
        '--name=short-drama-search',
        '--windowed',
        '--onefile',
        # '--icon=resources/icons/app.png',  # Linux图标
        '--icon=resources/icons/API.png',  # Linux图标
        '--add-data=resources:resources',  # 包含所有资源文件
        '--add-data=ui:ui',  # 包含UI模块
        '--add-data=core:core',  # 包含核心模块
        '--clean',
        '--noconfirm'
    ]

    run(opts)


if __name__ == "__main__":
    build_app()
