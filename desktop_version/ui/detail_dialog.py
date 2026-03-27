from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
    QWidget,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QClipboard
from PyQt5.QtCore import QUrl


class DetailDialog(QDialog):
    def __init__(self, drama_data, link_field="", parent=None):
        super().__init__(parent)
        self.drama_data = drama_data
        self.link = link_field
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("详情")
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
        title = (
            self.drama_data.get("name")
            or self.drama_data.get("content_title")
            or "未知标题"
        )
        title_label = QLabel(f"<h2>{title}</h2>")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # 详细信息
        info_html = "<div style='line-height: 1.6;'>"

        # 添加所有字段
        field_mapping = {
            "name": "名称",
            "title": "标题",
            "addtime": "更新时间",
            "hot": "热度",
            "hots": "热度值",
            "source": "来源",
            "type": "类型",
            "size": "大小",
            "content_rank": "排名",
            "content_type": "内容类型",
        }

        for key, value in self.drama_data.items():
            if key in ("viewlink", "url", "link", "image_url"):
                continue

            label = field_mapping.get(key, key)
            if value:
                info_html += f"<p><b>{label}:</b> {value}</p>"

        info_html += "</div>"

        info_label = QLabel(info_html)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 添加弹性空间
        layout.addStretch()

        # 按钮区域
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)

        if self.link:
            open_btn = QPushButton("打开链接")
            open_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """
            )
            open_btn.clicked.connect(self.open_link)

            copy_btn = QPushButton("复制链接")
            copy_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """
            )
            copy_btn.clicked.connect(self.copy_link)

            btn_layout.addWidget(open_btn)
            btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addWidget(btn_widget)

    def open_link(self):
        """打开链接"""
        if self.link:
            QDesktopServices.openUrl(QUrl(self.link))

    def copy_link(self):
        """复制链接到剪贴板"""
        if self.link:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.link)
            self.accept()
