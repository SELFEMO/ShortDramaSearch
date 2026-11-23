# -*- coding: utf-8 -*-

from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.api_client import TYPE_LABEL
from core.utils import build_ui_metrics, get_ui_font_family, safe_open_url
from ui.scrollbar import install_auto_hide_scrollbars


class DetailDialog(QDialog):
    """资源详情弹窗。"""

    def __init__(self, resource: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.resource = resource or {}
        self.ui_metrics = getattr(parent, "ui_metrics", build_ui_metrics(QApplication.instance()))
        self.setWindowTitle("资源详情")
        self.resize(
            self.ui_metrics.get("detail_dialog_width", 680),
            self.ui_metrics.get("detail_dialog_height", 420),
        )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        margin = self.ui_metrics.get("page_margin", 14)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(self.ui_metrics.get("layout_spacing", 10))

        title = QLabel(str(self.resource.get("name", "未知资源")))
        title.setWordWrap(True)
        title.setObjectName("dialogTitle")
        font_family = self.ui_metrics.get("font_family") or get_ui_font_family()
        title.setFont(
            QFont(font_family, self.ui_metrics.get("dialog_title_font_size", 17), QFont.Bold)
        )
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.name_edit = self._readonly_line(self.resource.get("name", ""))
        self.type_edit = self._readonly_line(
            TYPE_LABEL.get(self.resource.get("type", ""), self.resource.get("type", ""))
        )
        self.url_edit = self._readonly_line(self.resource.get("url", ""))
        self.pwd_edit = self._readonly_line(self.resource.get("pwd", ""))
        self.time_edit = self._readonly_line(self.resource.get("addtime", ""))

        form.addRow("名称：", self.name_edit)
        form.addRow("来源：", self.type_edit)
        form.addRow("链接：", self.url_edit)
        form.addRow("密码：", self.pwd_edit)
        form.addRow("更新：", self.time_edit)
        layout.addLayout(form)

        raw_label = QLabel("原始数据：")
        layout.addWidget(raw_label)
        raw_text = QTextEdit()
        raw_text.setReadOnly(True)
        install_auto_hide_scrollbars(raw_text, horizontal=False)
        raw_text.setPlainText("\n".join(f"{key}: {value}" for key, value in self.resource.items()))
        layout.addWidget(raw_text, 1)

        actions = QHBoxLayout()
        copy_link_btn = QPushButton("复制链接")
        copy_link_btn.setProperty("variant", "secondary")
        copy_pwd_btn = QPushButton("复制密码")
        copy_pwd_btn.setProperty("variant", "secondary")
        open_btn = QPushButton("打开链接")
        open_btn.setProperty("variant", "primary")
        copy_link_btn.clicked.connect(
            lambda: self.copy_text(self.resource.get("url", ""), "链接已复制")
        )
        copy_pwd_btn.clicked.connect(
            lambda: self.copy_text(self.resource.get("pwd", ""), "密码已复制")
        )
        open_btn.clicked.connect(self.open_link)
        actions.addWidget(copy_link_btn)
        actions.addWidget(copy_pwd_btn)
        actions.addWidget(open_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_btn = buttons.button(QDialogButtonBox.Close)
        if close_btn is not None:
            close_btn.setText("关闭")
            close_btn.setProperty("variant", "ghost")
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _readonly_line(self, text: str) -> QLineEdit:
        widget = QLineEdit(str(text or ""))
        widget.setReadOnly(True)
        return widget

    def copy_text(self, text: str, message: str):
        if not text:
            QMessageBox.information(self, "提示", "没有可复制的内容。")
            return
        QApplication.clipboard().setText(str(text))
        QMessageBox.information(self, "提示", message)

    def open_link(self):
        url = self.resource.get("url", "")
        if not url:
            QMessageBox.information(self, "提示", "没有可打开的链接。")
            return
        ok, err_msg = safe_open_url(url)
        if not ok:
            QMessageBox.warning(self, "安全提示", err_msg)
