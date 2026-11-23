#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from core.utils import resource_path
from ui.main_window import MainWindow

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("shortdramasearch.desktop")


def _install_excepthook():
    default_hook = sys.excepthook

    def _hook(exc_type, exc_value, exc_tb):
        logger.critical("Uncaught desktop exception", exc_info=(exc_type, exc_value, exc_tb))
        default_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


class ShortDramaApp:
    """短剧搜索桌面应用入口。"""

    def __init__(self, args):
        self.args = args
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
    parser.add_argument(
        "--keyword", "--q", "--name", "--search", dest="keyword", default="", help="启动后自动搜索的关键词"
    )
    parser.add_argument(
        "--source", "--from", dest="source", default="all", help="搜索来源：all/netdisk/baidu/quark 等"
    )
    parser.add_argument("--json", action="store_true", help="启动后打开 API 生成器并预览 JSON")
    return parser.parse_args()


def main():
    _install_excepthook()
    application = ShortDramaApp(parse_args())
    sys.exit(application.run())


if __name__ == "__main__":
    main()
