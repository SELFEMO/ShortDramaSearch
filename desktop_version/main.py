#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import (
    QIcon,
    QFontDatabase,  # 导入 QFontDatabase 以 apply_stylesheet 消除警告
)
from PyQt5.QtCore import QFile, QTextStream

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.data_manager import DataManager
from core.utils import resource_path

# # 导入 qt-material
# try:
#     from qt_material import apply_stylesheet

#     HAS_QT_MATERIAL = True
# except ImportError:
#     HAS_QT_MATERIAL = False
#     print("提示: 安装 qt-material 可获得更好的主题效果: pip install qt-material")
HAS_QT_MATERIAL = False  # 强制使用自定义主题


class ShortDramaApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("短剧搜索")
        self.app.setApplicationVersion("桌面版")
        self.app.setOrganizationName("ShortDrama")

        # 设置应用程序图标
        self.set_application_icon()

        # 应用现代化主题
        self.apply_modern_theme()

        # 初始化数据管理器
        self.data_manager = DataManager()

        # 创建主窗口
        self.main_window = MainWindow(self.data_manager)

    def set_application_icon(self):
        """设置跨平台应用程序图标"""
        # 根据平台选择图标文件
        if sys.platform == "win32":
            # icon_path = resource_path("resources/icons/app.ico")
            icon_path = resource_path("resources/icons/API.ico")
        elif sys.platform == "darwin":
            # icon_path = resource_path("resources/icons/app.icns")
            icon_path = resource_path("resources/icons/API.icns")
        else:  # Linux和其他Unix系统
            # icon_path = resource_path("resources/icons/app.png")
            icon_path = resource_path("resources/icons/API.png")

        # 设置应用程序图标
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，使用Qt内置图标
            print(f"警告: 图标文件不存在: {icon_path}")
            self.app.setWindowIcon(
                self.app.style().standardIcon(
                    self.app.style().SP_FileDialogContentsView
                )
            )

    def apply_modern_theme(self):
        """应用现代化主题"""
        if HAS_QT_MATERIAL:
            # 使用 qt-material 主题
            # 可选主题:
            # - dark_teal.xml, dark_blue.xml, dark_amber.xml, dark_pink.xml
            # - light_blue.xml, light_teal.xml, light_amber.xml, light_pink.xml
            try:
                apply_stylesheet(
                    self.app,
                    theme="dark_teal.xml",
                    invert_secondary=False,
                    font_size="18px",  # 或者更大，比如 '20px'
                )
                print("✅ 已应用 qt-material 主题: dark_teal")
            except Exception as e:
                print(f"⚠️ 应用 qt-material 主题失败: {e}")
                self.apply_custom_theme()
        else:
            # 如果没有安装 qt-material，使用自定义 QSS
            self.apply_custom_theme()

    def apply_custom_theme(self):
        """自定义现代化主题"""
        self.app.setStyle("Fusion")

        # 尝试加载自定义 QSS 文件
        qss_file = resource_path("resources/styles/custom_theme.qss")
        if os.path.exists(qss_file):
            try:
                with open(qss_file, "r", encoding="utf-8") as f:
                    self.app.setStyleSheet(f.read())
                print("✅ 已应用自定义主题")
            except Exception as e:
                print(f"⚠️ 加载自定义主题失败: {e}")
        else:
            print(f"⚠️ 未找到自定义主题文件: {qss_file}")

    def run(self):
        """运行应用程序"""
        self.main_window.show()

        # 启动事件循环
        return self.app.exec_()


def main():
    # 创建应用实例
    application = ShortDramaApp()

    # 运行应用
    sys.exit(application.run())


if __name__ == "__main__":
    main()
