#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

# 中文：在导入 Qt 前启用自动缩放环境变量，避免 Windows 多显示器缩放下 Qt 读取到过期 DPI 信息。
# English: Enable auto-scaling environment variables before importing Qt so Windows multi-monitor scaling does not expose stale DPI data.
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from core.utils import resource_path
from ui.main_window import MainWindow


class ShortDramaApp:
    """短剧搜索桌面应用入口。"""

    def __init__(self, args):
        self.args = args
        # 中文：高 DPI 属性必须在 QApplication 创建前设置，否则 Qt 会先按固定像素初始化控件，后续再调字体会导致布局和字体比例不一致。
        # English: High-DPI attributes must be set before QApplication is created; otherwise Qt initializes widgets in fixed pixels and later font changes break layout proportions.
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("酷乐短剧 / 影视资源聚合搜索")
        self.app.setApplicationVersion("PyQt5 2026")
        self.app.setOrganizationName("ShortDramaSearch")
        self.set_application_icon()
        self.data_manager = DataManager()
        self.main_window = MainWindow(
            self.data_manager,
            initial_keyword=args.keyword or "",
            initial_preset=args.source or "all",
            preview_json=args.json,
        )

    def set_application_icon(self):
        if sys.platform == "win32":
            icon_path = resource_path("resources/icons/API.ico")
        elif sys.platform == "darwin":
            icon_path = resource_path("resources/icons/API.icns")
        else:
            icon_path = resource_path("resources/icons/API.png")

        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))

    def run(self):
        self.main_window.show()
        return self.app.exec_()


def parse_args():
    parser = argparse.ArgumentParser(description="ShortDramaSearch PyQt5 桌面版")
    parser.add_argument("--keyword", "--q", "--name", "--search", dest="keyword", default="", help="启动后自动搜索的关键词")
    parser.add_argument("--source", "--from", dest="source", default="all", help="搜索来源：all/netdisk/baidu/quark 等")
    parser.add_argument("--json", action="store_true", help="启动后打开 API 生成器并预览 JSON")
    return parser.parse_args()


def main():
    # 中文：desktop_version 是 PyQt5 原生控件应用，不能再依赖 QtWebEngine 嵌入网页；启动参数只用于复刻网页 URL 参数体验。
    # English: desktop_version is a PyQt5 native-widget app now, so it must not depend on QtWebEngine; startup args only mirror web URL-parameter behavior.
    application = ShortDramaApp(parse_args())
    sys.exit(application.run())


if __name__ == "__main__":
    main()
