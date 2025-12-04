#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.data_manager import DataManager
from core.utils import resource_path


class ShortDramaApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("短剧搜索")
        self.app.setApplicationVersion("桌面版")
        self.app.setOrganizationName("ShortDrama")

        # 设置应用程序图标
        self.set_application_icon()

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
            self.app.setWindowIcon(self.app.style().standardIcon(
                self.app.style().SP_FileDialogContentsView
            ))

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