import os
import webbrowser
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QScrollArea,
                             QApplication, QMessageBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QClipboard
from core.utils import resource_path


class DetailDialog(QDialog):
    def __init__(self, drama_data, parent=None):
        super().__init__(parent)
        self.drama_data = drama_data
        self.init_ui()

    def init_ui(self):
        """初始化详情对话框界面"""
        self.setWindowTitle("短剧详情")
        self.setMinimumSize(960, 640)  # 设置最小尺寸
        self.setGeometry(200, 200, 960, 640)  # 设置初始位置和大小

        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))

        main_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)  # 设置滚动区域最小高度
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)  # 增加内部间距
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # 短剧名称
        name_group = self.create_info_group("🎬 短剧名称", self.drama_data.get("name", ""))
        scroll_layout.addWidget(name_group)

        # 更新时间
        time_group = self.create_info_group("📅 更新时间", self.drama_data.get("addtime", ""))
        scroll_layout.addWidget(time_group)

        # 网盘链接
        link_group = self.create_link_group("🔗 网盘链接", self.drama_data.get("viewlink", ""))
        scroll_layout.addWidget(link_group)

        # 添加弹性空间
        scroll_layout.addStretch(1)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 复制链接按钮
        self.copy_button = QPushButton("📋 复制链接")
        self.copy_button.setMinimumHeight(40)
        self.copy_button.setFont(QFont("Microsoft YaHei", 16))
        self.copy_button.clicked.connect(self.copy_link)

        # 打开链接按钮
        self.open_button = QPushButton("🌐 打开链接")
        self.open_button.setMinimumHeight(40)
        self.open_button.setFont(QFont("Microsoft YaHei", 16))
        self.open_button.clicked.connect(self.open_link)

        # 关闭按钮
        self.close_button = QPushButton("❌ 关闭")
        self.close_button.setMinimumHeight(40)
        self.close_button.setFont(QFont("Microsoft YaHei", 16))
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        # 设置样式
        self.apply_styles()

    def create_info_group(self, title, content):
        """创建信息显示组"""
        group = QFrame()
        group.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(group)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")

        # 内容
        content_label = QLabel(content)
        content_label.setFont(QFont("Microsoft YaHei", 11))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0px;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(content_label)

        return group

    def create_link_group(self, title, link):
        """创建链接显示组"""
        group = QFrame()
        group.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(group)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")

        # 链接内容 - 使用QTextEdit以便选择和复制
        link_text = QTextEdit()
        link_text.setPlainText(link)
        link_text.setFont(QFont("Microsoft YaHei", 11))
        link_text.setMaximumHeight(100)
        link_text.setReadOnly(True)
        link_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e1e1e1;
                border-radius: 5px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(link_text)

        return group

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: Microsoft YaHei;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#copy_button {
                background-color: #2ecc71;
            }
            QPushButton#copy_button:hover {
                background-color: #27ae60;
            }
            QPushButton#open_button {
                background-color: #e67e22;
            }
            QPushButton#open_button:hover {
                background-color: #d35400;
            }
            QPushButton#close_button {
                background-color: #e74c3c;
            }
            QPushButton#close_button:hover {
                background-color: #c0392b;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdfe6;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c4cc;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #909399;
            }
        """)

        # 为按钮设置对象名称以便样式选择
        self.copy_button.setObjectName("copy_button")
        self.open_button.setObjectName("open_button")
        self.close_button.setObjectName("close_button")

    def copy_link(self):
        """复制链接到剪贴板"""
        link = self.drama_data.get("viewlink", "")
        if link:
            clipboard = QApplication.clipboard()
            clipboard.setText(link)
            QMessageBox.information(self, "复制成功", "链接已复制到剪贴板！")
        else:
            QMessageBox.warning(self, "复制失败", "没有可复制的链接")

    def open_link(self):
        """打开链接"""
        link = self.drama_data.get("viewlink", "")
        if link:
            try:
                webbrowser.open(link)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开链接:\n{str(e)}")
        else:
            QMessageBox.warning(self, "打开失败", "没有有效的链接")