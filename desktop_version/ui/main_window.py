# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, QTimer, QUrl, QSize, QRectF, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QDesktopServices, QFont, QPalette, QPainter, QPainterPath, QPen, QPixmap, QRegion
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QActionGroup,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QPlainTextEdit,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.api_client import (
    ApiClient,
    ApiError,
    ONLINE_PAGE_URL,
    PRESET_LABEL,
    TYPE_LABEL,
    TYPE_PRESETS,
)
from core.data_manager import DataManager
from core.utils import build_ui_metrics, format_timestamp, get_system_theme_name, resource_path
from ui.detail_dialog import DetailDialog
from ui.scrollbar import install_auto_hide_scrollbars


class TaskThread(QThread):
    """把网络请求放到后台线程执行，避免阻塞 Qt 主线程。"""

    success = pyqtSignal(object)
    failure = pyqtSignal(str)

    def __init__(self, task: Callable[[], Any], parent=None):
        super().__init__(parent)
        self.task = task

    def run(self):
        try:
            self.success.emit(self.task())
        except Exception as exc:
            self.failure.emit(str(exc))



def combo_arrow_asset(theme: str) -> str:
    name = "chevron_down_light.svg" if theme == "light" else "chevron_down_dark.svg"
    # 中文：箭头图标使用项目内 SVG 资源，避免用 QSS 边框拼三角形时在 Windows 上渲染成难懂的小横块。
    # English: The arrow uses an in-project SVG asset because QSS border triangles can render as confusing tiny bars on Windows.
    return resource_path(os.path.join("resources", "icons", name)).replace("\\", "/")


def compact_button_policy(button: QPushButton) -> QPushButton:
    # 中文：按钮不再允许在横向布局中主动吃掉空白区域，否则“清空”等短按钮会被拉成很宽的大块。
    # English: Buttons are not allowed to consume extra horizontal space, otherwise short labels such as “清空” become unnecessarily wide blocks.
    button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    button.setMinimumWidth(0)
    button.setMinimumHeight(0)
    return button


def build_modern_combo_qss(
    selector: str,
    metrics: Dict[str, Any],
    background: str,
    text_color: str,
    border_color: str,
    hover_border: str,
    popup_background: str,
    popup_hover: str,
    selection_background: str,
    selection_text: str,
    arrow_color: str,
    arrow_background: str,
    compact: bool = False,
    arrow_image: str = "",
) -> str:
    """生成统一的现代化 QComboBox 样式。"""
    pad_v = max(2, metrics.get("compact_button_padding_v", 2) if compact else metrics.get("input_padding_v", 6))
    pad_h = max(6, metrics.get("compact_button_padding_h", 6) if compact else metrics.get("input_padding_h", 8))
    radius = max(5, metrics.get("card_radius", 10) // 2)
    popup_radius = max(5, metrics.get("combo_popup_radius", radius))
    popup_padding = max(2, metrics.get("combo_popup_padding", 4))
    arrow_area = metrics.get("combo_arrow_area_width", 24)
    arrow = metrics.get("combo_arrow_size", 10)
    item_height = metrics.get("combo_popup_item_height", 24)
    arrow_rule = f'image: url("{arrow_image}");' if arrow_image else "image: none;"

    # 中文：下拉按钮只保留右侧留白和清晰 SVG 箭头，不再绘制独立小按钮块，避免和原生控件混杂造成误读。
    # English: The drop-down keeps only right padding and a clear SVG chevron instead of a separate mini button, avoiding a mixed native/custom look.
    return f"""
        {selector} {{
            background: {background};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: {radius}px;
            padding: {pad_v}px {arrow_area + max(4, pad_h // 2)}px {pad_v}px {pad_h}px;
            min-height: 0px;
        }}
        {selector}:hover {{
            border-color: {hover_border};
        }}
        {selector}:focus, {selector}:on {{
            border-color: {hover_border};
        }}
        {selector}::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: {arrow_area}px;
            border: none;
            background: transparent;
        }}
        {selector}::drop-down:hover {{
            background: {arrow_background};
        }}
        {selector}::down-arrow {{
            {arrow_rule}
            width: {arrow}px;
            height: {arrow}px;
            margin-right: {max(4, arrow_area // 3)}px;
        }}
        {selector} QAbstractItemView, QListView#comboPopupView {{
            background: {popup_background};
            color: {text_color};
            border: 1px solid {hover_border};
            border-radius: {popup_radius}px;
            padding: {popup_padding}px;
            margin: 0px;
            outline: none;
            selection-background-color: {selection_background};
            selection-color: {selection_text};
        }}
        {selector} QAbstractItemView::item, QListView#comboPopupView::item {{
            min-height: {item_height}px;
            padding: 2px {pad_h}px;
            margin: 1px 0px;
            border-radius: {max(4, popup_radius - 3)}px;
            background: transparent;
        }}
        {selector} QAbstractItemView::item:hover, QListView#comboPopupView::item:hover {{
            background: {popup_hover};
        }}
        {selector} QAbstractItemView::item:selected, QListView#comboPopupView::item:selected {{
            background: {selection_background};
            color: {selection_text};
        }}
        QListView#comboPopupView QScrollBar:vertical {{
            background: transparent;
            width: {max(6, metrics.get("scrollbar_size", 8))}px;
            margin: {max(1, metrics.get("scrollbar_margin", 2))}px;
            border: none;
        }}
        QListView#comboPopupView QScrollBar::handle:vertical {{
            background: {hover_border};
            border-radius: {max(3, metrics.get("scrollbar_radius", 5))}px;
            min-height: {max(24, metrics.get("scrollbar_handle_min", 36) // 2)}px;
        }}
        QListView#comboPopupView QScrollBar::add-line:vertical, QListView#comboPopupView QScrollBar::sub-line:vertical {{
            height: 0px;
            width: 0px;
            border: none;
            background: transparent;
        }}
        QListView#comboPopupView QScrollBar::add-page:vertical, QListView#comboPopupView QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
    """


class StableComboBox(QComboBox):
    """避免下拉弹层原生自动滚动过度的组合框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popup_radius = 8
        self._popup_max_visible = 8
        self.setCursor(Qt.PointingHandCursor)
        self.setMaxVisibleItems(self._popup_max_visible)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        view = QListView(self)
        view.setObjectName("comboPopupView")
        view.setMouseTracking(True)
        view.setAutoScroll(False)
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setUniformItemSizes(True)
        view.setFrameShape(QFrame.NoFrame)
        view.setContentsMargins(0, 0, 0, 0)
        self.setView(view)

    def configure_popup(self, metrics: Dict[str, Any]):
        # 中文：下拉列表默认只展示少量候选项，剩余内容通过滚动查看，避免来源列表一展开就占满半个屏幕。
        # English: The popup shows only a small number of options by default and keeps the rest scrollable, preventing source lists from taking over the screen.
        self._popup_max_visible = int(metrics.get("combo_popup_max_visible", 8))
        self._popup_radius = int(metrics.get("combo_popup_radius", 8))
        self.setMaxVisibleItems(max(5, min(10, self._popup_max_visible)))
        view = self.view()
        if view is not None:
            view.setAutoScroll(False)
            view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.setUniformItemSizes(True)
            view.setSpacing(0)

    def showPopup(self):
        view = self.view()
        if view is not None:
            # 中文：关闭 QAbstractItemView 的边缘自动滚动，避免鼠标只是移到下拉框底部就一路滚到最后一项并预选。
            # English: QAbstractItemView edge auto-scroll is disabled so merely moving the cursor to the popup bottom cannot scroll to and preselect the last item.
            view.setAutoScroll(False)
            view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        super().showPopup()
        QTimer.singleShot(0, self.polish_popup_corners)

    def polish_popup_corners(self):
        view = self.view()
        if view is None:
            return
        popup = view.window()
        if popup is None or popup is self.window():
            return
        rect = popup.rect()
        if rect.isEmpty():
            return
        radius = max(4, self._popup_radius)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        # 中文：Qt5 的组合框弹层是独立原生窗口，仅靠 QSS 圆角无法稳定裁掉底部方角，因此给弹层窗口加圆角遮罩。
        # English: A Qt5 combo popup is a separate native window; QSS radius alone cannot reliably clip square bottom corners, so a rounded mask is applied to the popup window.
        popup.setMask(QRegion(path.toFillPolygon().toPolygon()))


class ResourceCard(QFrame):
    """单条资源卡片，替代窄列表格行。"""

    actionRequested = pyqtSignal(str, dict)
    qualityChanged = pyqtSignal(str, int)

    def __init__(self, record: Dict[str, Any], data_manager: DataManager, metrics: Dict[str, Any], theme: str = "dark", parent=None):
        super().__init__(parent)
        self.record = dict(record or {})
        self.data_manager = data_manager
        self.metrics = dict(metrics or {})
        self.theme = "light" if theme == "light" else "dark"
        self.link = self.record.get("url", "")
        self.setObjectName("resourceCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setCursor(Qt.ArrowCursor)
        self._card_radius = metrics.get("card_radius", 10)
        self._paint_colors = ResourceTable._build_theme_colors(self.theme)
        # 中文：卡片圆角由 paintEvent 绘制，而不是依赖 QSS 背景裁剪；Qt5 子控件继承全局背景时很容易在圆角后露出方形底色。
        # English: Card corners are painted in paintEvent instead of relying on QSS clipping; Qt5 child widgets can inherit global backgrounds and expose square corners behind rounded cards.
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.init_ui()
        self.apply_visual_theme(self.theme)

    def paintEvent(self, event):
        colors = getattr(self, "_paint_colors", ResourceTable._build_theme_colors(self.theme))
        radius = getattr(self, "_card_radius", self.metrics.get("card_radius", 10))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setBrush(QColor(colors["card_bg"]))
        painter.setPen(QPen(QColor(colors["card_border"]), 1))
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)

    @staticmethod
    def compact_text(value: Any, limit: int = 110) -> str:
        text = " ".join(str(value or "").split())
        if len(text) <= limit:
            return text
        return f"{text[:max(0, limit - 1)]}…"

    @staticmethod
    def source_label(record: Dict[str, Any]) -> str:
        source_key = record.get("type", "")
        return TYPE_LABEL.get(source_key, source_key or record.get("source", record.get("_source", "未知来源")))

    def init_ui(self):
        metrics = self.metrics
        padding = metrics.get("card_padding", 12)
        spacing = metrics.get("card_spacing", 8)

        # 中文：把原来横向表格列改成纵向信息层级，是为了让长标题和长链接拥有自然换行空间，而不是继续抢占固定列宽。
        # English: The old horizontal table columns are converted into vertical information layers so long titles and links get natural wrapping space instead of competing for fixed column widths.
        root = QVBoxLayout(self)
        root.setContentsMargins(padding, padding, padding, padding)
        root.setSpacing(spacing)

        top_row = QHBoxLayout()
        top_row.setSpacing(spacing)
        title_block = QVBoxLayout()
        title_block.setSpacing(max(3, spacing // 2))

        title = QLabel(self.compact_text(self.record.get("name", "未知资源"), metrics.get("card_title_limit", 120)))
        title.setObjectName("resourceCardTitle")
        title.setWordWrap(True)
        title.setToolTip(str(self.record.get("name", "")))
        title_block.addWidget(title)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(max(4, spacing // 2))
        chip_row.addWidget(self.create_chip(self.source_label(self.record)))
        pwd = str(self.record.get("pwd", "") or "").strip()
        if pwd:
            chip_row.addWidget(self.create_chip(f"提取码 {pwd}"))
        marker = self.record.get("_searchTerm") or self.record.get("addtime") or format_timestamp(self.record.get("timestamp"))
        if marker:
            chip_row.addWidget(self.create_chip(self.compact_text(marker, 38)))
        if self.data_manager.is_broken_marked(self.link):
            chip_row.addWidget(self.create_chip("本地标记失效", "danger"))
        chip_row.addStretch(1)
        title_block.addLayout(chip_row)
        top_row.addLayout(title_block, 1)

        side = QVBoxLayout()
        side.setSpacing(max(4, spacing // 2))
        favorite_btn = self.create_button("★ 已收藏" if self.data_manager.is_favorited(self.link) else "☆ 收藏", "favorite", "ghost")
        broken_btn = self.create_button("取消失效" if self.data_manager.is_broken_marked(self.link) else "标记失效", "broken", "danger")
        side.addWidget(favorite_btn)
        side.addWidget(broken_btn)
        top_row.addLayout(side)
        root.addLayout(top_row)

        link_text = self.compact_text(self.link, metrics.get("card_link_limit", 120)) or "无链接"
        link_label = QLabel(link_text)
        link_label.setObjectName("resourceCardLink")
        link_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        link_label.setToolTip(self.link)
        root.addWidget(link_label)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(max(5, spacing // 2))
        rating_label = QLabel("评分")
        rating_label.setObjectName("resourceCardMeta")
        bottom_row.addWidget(rating_label)
        rating = StableComboBox()
        rating.setObjectName("resourceCardRating")
        rating.setMinimumWidth(metrics.get("rating_width", 94))
        rating.addItems(["未评分", "★", "★★", "★★★", "★★★★", "★★★★★"])
        rating.setCurrentIndex(max(0, min(5, self.data_manager.get_quality(self.link))))
        rating.currentIndexChanged.connect(lambda score, current_link=self.link: self.qualityChanged.emit(current_link, score))
        bottom_row.addWidget(rating)
        bottom_row.addStretch(1)
        for text, action, role in [
            ("打开", "open", "primary"),
            ("复制链接", "copy_link", "ghost"),
            ("复制密码", "copy_pwd", "ghost"),
            ("二维码", "qr", "ghost"),
            ("详情", "detail", "ghost"),
        ]:
            bottom_row.addWidget(self.create_button(text, action, role))
        root.addLayout(bottom_row)

    def create_chip(self, text: str, role: str = "normal") -> QLabel:
        chip = QLabel(str(text or ""))
        chip.setObjectName("resourceCardChipDanger" if role == "danger" else "resourceCardChip")
        chip.setToolTip(str(text or ""))
        return chip

    def create_button(self, text: str, action: str, role: str = "ghost") -> QPushButton:
        button = compact_button_policy(QPushButton(text))
        button.setObjectName("resourceCardPrimaryButton" if role == "primary" else "resourceCardDangerButton" if role == "danger" else "resourceCardGhostButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.actionRequested.emit(action, dict(self.record)))
        return button

    def apply_visual_theme(self, theme: str):
        self.theme = "light" if theme == "light" else "dark"
        colors = ResourceTable._build_theme_colors(self.theme)
        metrics = self.metrics
        radius = metrics.get("card_radius", 10)
        self._paint_colors = colors
        self._card_radius = radius
        padding_v = max(2, metrics.get("compact_button_padding_v", 3))
        padding_h = max(6, metrics.get("compact_button_padding_h", 8))
        title_font = metrics.get("card_title_font_size", metrics.get("base_font_size", 13) + 1)
        small_font = metrics.get("small_font_size", 12)
        combo_qss = build_modern_combo_qss(
            "QComboBox#resourceCardRating",
            metrics,
            colors["combo_bg"],
            colors["text"],
            colors["card_border"],
            "#ff6b35",
            colors["combo_bg"],
            colors["chip_bg"],
            "#ff6b35",
            "#ffffff",
            colors["muted_text"],
            colors["ghost_button_bg"],
            compact=True,
            arrow_image=combo_arrow_asset(self.theme),
        )

        # 中文：卡片使用局部 QSS 覆盖全局按钮样式，避免每个内联操作都变成醒目的橙色主按钮。
        # English: Card-local QSS overrides global button styles so every inline action does not become a prominent orange primary button.
        self.setStyleSheet(f"""
            QFrame#resourceCard {{
                background: transparent;
                border: none;
            }}
            QLabel#resourceCardTitle {{
                color: {colors["text"]};
                font-size: {title_font}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
            QLabel#resourceCardMeta {{
                color: {colors["muted_text"]};
                background: transparent;
                border: none;
            }}
            QLabel#resourceCardLink {{
                color: {colors["link_text"]};
                background: transparent;
                border: none;
                font-size: {small_font}px;
            }}
            QLabel#resourceCardChip, QLabel#resourceCardChipDanger {{
                border: none;
                border-radius: {max(6, radius // 2)}px;
                padding: {max(2, padding_v // 2)}px {padding_h}px;
                font-size: {small_font}px;
            }}
            QLabel#resourceCardChip {{
                background: {colors["chip_bg"]};
                color: {colors["chip_text"]};
            }}
            QLabel#resourceCardChipDanger {{
                background: {colors["danger_bg"]};
                color: {colors["danger_text"]};
            }}
            QPushButton#resourceCardPrimaryButton,
            QPushButton#resourceCardGhostButton,
            QPushButton#resourceCardDangerButton {{
                border-radius: {max(5, radius // 2)}px;
                padding: {padding_v}px {padding_h}px;
                min-height: 0px;
            }}
            QPushButton#resourceCardPrimaryButton {{
                background: #ff6b35;
                color: #ffffff;
                border: 1px solid #ff6b35;
            }}
            QPushButton#resourceCardGhostButton {{
                background: {colors["ghost_button_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["card_border"]};
            }}
            QPushButton#resourceCardDangerButton {{
                background: {colors["danger_button_bg"]};
                color: {colors["danger_text"]};
                border: 1px solid {colors["danger_border"]};
            }}
            {combo_qss}
        """)
        self.update()


class ResourceTable(QListWidget):
    """搜索、每日影视和收藏共用的资源卡片列表。"""

    actionRequested = pyqtSignal(str, dict)
    qualityChanged = pyqtSignal(str, int)

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.records: List[Dict[str, Any]] = []
        self.show_broken = True
        self._theme_name = "dark"
        self._theme_colors = self._build_theme_colors(self._theme_name)
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        install_auto_hide_scrollbars(self, horizontal=False)
        self.setUniformItemSizes(False)
        self.setSpacing(self.ui_metrics.get("card_gap", 10))
        self.itemDoubleClicked.connect(lambda _item: self.open_current_detail())
        self.apply_adaptive_metrics()

    @staticmethod
    def _build_theme_colors(theme: str) -> Dict[str, str]:
        if theme == "light":
            return {
                "table_bg": "#f8fafc",
                "row_bg": "#ffffff",
                "row_alt": "#f8fafc",
                "broken_bg": "#fff1f2",
                "text": "#172033",
                "muted_text": "#64748b",
                "grid": "#d8e0ea",
                "selection_bg": "#dbeafe",
                "selection_text": "#0f172a",
                "card_bg": "#ffffff",
                "card_border": "#d8e0ea",
                "chip_bg": "#edf2f7",
                "chip_text": "#334155",
                "link_text": "#2563eb",
                "ghost_button_bg": "#f8fafc",
                "danger_bg": "#ffe4e6",
                "danger_text": "#be123c",
                "danger_button_bg": "#fff1f2",
                "danger_border": "#fecdd3",
                "combo_bg": "#ffffff",
            }
        return {
            "table_bg": "#101018",
            "row_bg": "#1a1a24",
            "row_alt": "#151520",
            "broken_bg": "#2a1b1d",
            "text": "#f0f0f5",
            "muted_text": "#a8a8b8",
            "grid": "#2a2a3a",
            "selection_bg": "#223047",
            "selection_text": "#ffffff",
            "card_bg": "#181824",
            "card_border": "#2d2d3d",
            "chip_bg": "#242436",
            "chip_text": "#d7d7e4",
            "link_text": "#8cc7ff",
            "ghost_button_bg": "#20202e",
            "danger_bg": "#3a2026",
            "danger_text": "#ffb4c1",
            "danger_button_bg": "#2d1c21",
            "danger_border": "#5f2c38",
            "combo_bg": "#20202e",
        }

    def set_visual_theme(self, theme: str):
        self._theme_name = "light" if theme == "light" else "dark"
        self._theme_colors = self._build_theme_colors(self._theme_name)
        colors = self._theme_colors
        metrics = self.ui_metrics

        # 中文：资源结果不再使用表格列，而是使用可换行卡片；列表容器只负责滚动和选中状态，避免列宽过窄导致按钮与文字被硬裁切。
        # English: Resource results use wrapping cards instead of table columns; the list only handles scrolling and selection to avoid hard clipping buttons and text in narrow columns.
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(colors["table_bg"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Highlight, QColor(colors["selection_bg"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["selection_text"]))
        self.setPalette(palette)
        self.viewport().setPalette(palette)
        # 中文：列表 viewport 必须显式填充当前主题背景，否则 item widget 自绘圆角外侧会露出系统默认底色。
        # English: The list viewport must explicitly fill the current theme background, otherwise the area outside custom-painted card corners can expose the system default color.
        self.viewport().setAutoFillBackground(True)
        self.viewport().setStyleSheet(f"background: {colors['table_bg']};")
        self.setStyleSheet(f"""
            QListWidget {{
                background: {colors["table_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["grid"]};
                border-radius: 8px;
                padding: {metrics.get("card_gap", 10)}px;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
            }}
        """)
        self.repaint_cards()

    def repaint_cards(self):
        for index in range(self.count()):
            item = self.item(index)
            widget = self.itemWidget(item)
            if isinstance(widget, ResourceCard):
                widget.metrics = dict(self.ui_metrics)
                widget.apply_visual_theme(self._theme_name)
                item.setSizeHint(QSize(0, widget.sizeHint().height() + self.ui_metrics.get("card_gap", 10)))

    def apply_adaptive_metrics(self):
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.setSpacing(self.ui_metrics.get("card_gap", 10))
        self.repaint_cards()

    def set_records(self, records: List[Dict[str, Any]], show_broken: bool = True):
        self.records = list(records or [])
        self.show_broken = show_broken
        visible = [item for item in self.records if show_broken or not self.data_manager.is_broken_marked(item.get("url", ""))]
        self.apply_adaptive_metrics()
        self.clear()

        for record in visible:
            self.add_record_card(record)

        if self.count() > 0:
            self.setCurrentRow(0)

    def add_record_card(self, record: Dict[str, Any]):
        # 中文：QListWidgetItem 只保存数据和高度，真实界面交给 ResourceCard 渲染，这样能同时保留列表选择能力和卡片布局自由度。
        # English: QListWidgetItem only stores data and size while ResourceCard renders the UI, preserving list selection while allowing flexible card layout.
        item = QListWidgetItem()
        item.setData(Qt.UserRole, dict(record))
        card = ResourceCard(record, self.data_manager, self.ui_metrics, self._theme_name, self)
        card.actionRequested.connect(self.actionRequested)
        card.qualityChanged.connect(self.qualityChanged)
        item.setSizeHint(QSize(0, card.sizeHint().height() + self.ui_metrics.get("card_gap", 10)))
        self.addItem(item)
        self.setItemWidget(item, card)

    def current_record(self) -> Optional[Dict[str, Any]]:
        item = self.currentItem()
        if not item:
            return None
        record = item.data(Qt.UserRole)
        return dict(record) if isinstance(record, dict) else None

    def open_current_detail(self):
        record = self.current_record()
        if record:
            self.actionRequested.emit("detail", record)


class RankCard(QFrame):
    """热度榜卡片，避免空说明列和窄操作列表造成视觉割裂。"""

    searchRequested = pyqtSignal(dict)

    def __init__(self, record: Dict[str, Any], rank: int, keyword: str, metrics: Dict[str, Any], theme: str = "dark", parent=None):
        super().__init__(parent)
        self.record = dict(record or {})
        self.rank = rank
        self.keyword = str(keyword or "").strip() or "未知关键词"
        self.metrics = dict(metrics or {})
        self.theme = "light" if theme == "light" else "dark"
        self.setObjectName("rankCard")
        self.setFrameShape(QFrame.NoFrame)
        self._card_radius = metrics.get("card_radius", 10)
        self._paint_colors = ResourceTable._build_theme_colors(self.theme)
        # 中文：热度榜卡片同样使用自绘圆角，避免 QListWidget 选中背景或全局 QWidget 背景在圆角后形成方块。
        # English: Rank cards use the same custom rounded painting to prevent QListWidget selection or global QWidget backgrounds from creating square blocks behind the corners.
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.init_ui()
        self.apply_visual_theme(self.theme)

    def paintEvent(self, event):
        colors = getattr(self, "_paint_colors", ResourceTable._build_theme_colors(self.theme))
        radius = getattr(self, "_card_radius", self.metrics.get("card_radius", 10))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setBrush(QColor(colors["card_bg"]))
        painter.setPen(QPen(QColor(colors["card_border"]), 1))
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)

    @staticmethod
    def compact_text(value: Any, limit: int = 120) -> str:
        text = " ".join(str(value or "").split())
        if len(text) <= limit:
            return text
        return f"{text[:max(0, limit - 1)]}…"

    @staticmethod
    def rank_description(record: Dict[str, Any]) -> str:
        for key in ("hot", "heat", "score", "desc", "description", "category", "subTitle", "intro"):
            value = str(record.get(key, "")).strip()
            if value:
                return value
        return ""

    def init_ui(self):
        metrics = self.metrics
        padding = metrics.get("card_padding", 12)
        spacing = metrics.get("card_spacing", 8)

        # 中文：榜单接口经常只有排名和关键词，没有说明字段；卡片布局按“有则展示、无则省略”设计，避免表格空列占据大面积空间。
        # English: Rank APIs often provide only rank and keyword without descriptions; the card layout shows optional fields only when present to avoid large empty table columns.
        root = QHBoxLayout(self)
        root.setContentsMargins(padding, padding, padding, padding)
        root.setSpacing(spacing)

        self.rank_badge = QLabel(str(self.rank))
        self.rank_badge.setObjectName("rankBadge")
        self.rank_badge.setAlignment(Qt.AlignCenter)
        self.rank_badge.setFixedWidth(metrics.get("rank_badge_width", 46))
        root.addWidget(self.rank_badge)

        content = QVBoxLayout()
        content.setSpacing(max(4, spacing // 2))
        title = QLabel(self.compact_text(self.keyword, metrics.get("rank_keyword_limit", 140)))
        title.setObjectName("rankKeyword")
        title.setWordWrap(True)
        title.setToolTip(self.keyword)
        content.addWidget(title)

        description = self.rank_description(self.record)
        self.meta = None
        if description:
            # 中文：没有说明字段时直接省略副文本，避免每张卡片重复显示操作提示并挤占榜单垂直空间。
            # English: When no description is available, the subtitle is omitted so repeated operation hints do not consume vertical space in every rank card.
            self.meta = QLabel(self.compact_text(description, metrics.get("rank_desc_limit", 160)))
            self.meta.setObjectName("rankMeta")
            self.meta.setWordWrap(True)
            self.meta.setToolTip(description)
            content.addWidget(self.meta)
        root.addLayout(content, 1)

        self.search_button = compact_button_policy(QPushButton("聚合搜索"))
        self.search_button.setObjectName("rankSearchButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(lambda: self.searchRequested.emit(dict(self.record)))
        root.addWidget(self.search_button, 0, Qt.AlignVCenter)

    def apply_visual_theme(self, theme: str):
        self.theme = "light" if theme == "light" else "dark"
        colors = ResourceTable._build_theme_colors(self.theme)
        metrics = self.metrics
        radius = metrics.get("card_radius", 10)
        self._paint_colors = colors
        self._card_radius = radius
        padding_v = max(2, metrics.get("compact_button_padding_v", 3))
        padding_h = max(6, metrics.get("compact_button_padding_h", 8))
        title_font = metrics.get("card_title_font_size", metrics.get("base_font_size", 13) + 1)
        small_font = metrics.get("small_font_size", 12)

        # 中文：榜单搜索按钮使用固定横向文本，防止窄表格单元格把“搜索”挤成逐字竖排。
        # English: The rank search button keeps a fixed horizontal label so a narrow table cell cannot squeeze “搜索” into vertical-looking characters.
        self.setStyleSheet(f"""
            QFrame#rankCard {{
                background: transparent;
                border: none;
            }}
            QLabel#rankBadge {{
                background: {colors["chip_bg"]};
                color: {colors["chip_text"]};
                border-radius: {max(8, radius // 2)}px;
                padding: {padding_v}px 0px;
                font-weight: 700;
            }}
            QLabel#rankKeyword {{
                background: transparent;
                border: none;
                color: {colors["text"]};
                font-size: {title_font}px;
                font-weight: 700;
            }}
            QLabel#rankMeta {{
                background: transparent;
                border: none;
                color: {colors["muted_text"]};
                font-size: {small_font}px;
            }}
            QPushButton#rankSearchButton {{
                background: #ff6b35;
                color: #ffffff;
                border: 1px solid #ff6b35;
                border-radius: {max(5, radius // 2)}px;
                padding: {padding_v}px {padding_h}px;
                min-height: 0px;
            }}
            QPushButton#rankSearchButton:hover {{
                background: #ff8555;
                border-color: #ff8555;
            }}
        """)
        self.update()


class RankList(QListWidget):
    """热度榜专用卡片列表。"""

    searchRequested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records: List[Dict[str, Any]] = []
        self._theme_name = "dark"
        self._theme_colors = ResourceTable._build_theme_colors(self._theme_name)
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        install_auto_hide_scrollbars(self, horizontal=False)
        self.setSpacing(self.ui_metrics.get("card_gap", 10))
        self.itemDoubleClicked.connect(lambda _item: self.search_current_record())
        self.apply_adaptive_metrics()

    @staticmethod
    def keyword_from_record(record: Dict[str, Any]) -> str:
        for key in ("keyword", "name", "title", "word", "text", "query"):
            value = str(record.get(key, "")).strip()
            if value:
                return value
        return ""

    def set_visual_theme(self, theme: str):
        self._theme_name = "light" if theme == "light" else "dark"
        self._theme_colors = ResourceTable._build_theme_colors(self._theme_name)
        colors = self._theme_colors
        metrics = self.ui_metrics

        # 中文：榜单列表只保留卡片边界和选中态，内容布局交给 RankCard，避免表头、空列和单元格按钮继续影响阅读。
        # English: The rank list keeps only card boundaries and selection state while RankCard owns content layout, avoiding headers, empty columns, and cell buttons affecting readability.
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(colors["table_bg"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Highlight, QColor(colors["selection_bg"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["selection_text"]))
        self.setPalette(palette)
        self.viewport().setPalette(palette)
        # 中文：榜单卡片同样让 viewport 接管背景，避免选中项或平台调色板在圆角外留下方形色块。
        # English: Rank cards let the viewport own the background as well, preventing selected items or platform palettes from leaving square blocks outside rounded corners.
        self.viewport().setAutoFillBackground(True)
        self.viewport().setStyleSheet(f"background: {colors['table_bg']};")
        self.setStyleSheet(f"""
            QListWidget {{
                background: {colors["table_bg"]};
                color: {colors["text"]};
                border: 1px solid {colors["grid"]};
                border-radius: 8px;
                padding: {metrics.get("card_gap", 10)}px;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
            }}
        """)
        self.repaint_cards()

    def apply_adaptive_metrics(self):
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.setSpacing(self.ui_metrics.get("card_gap", 10))
        self.repaint_cards()

    def set_records(self, records: List[Dict[str, Any]]):
        self.records = [dict(item) if isinstance(item, dict) else {"name": str(item)} for item in (records or [])]
        self.apply_adaptive_metrics()
        self.clear()
        for index, record in enumerate(self.records, 1):
            # 中文：过滤后仍优先保留接口原始排名，避免用户搜索榜单关键词时看到排名被重新编号。
            # English: The original API rank is preserved after filtering so searching inside the rank list does not renumber items unexpectedly.
            rank = record.get("rank") or record.get("index") or index
            self.add_rank_card(rank, record)
        if self.count() > 0:
            self.setCurrentRow(0)

    def add_rank_card(self, rank: int, record: Dict[str, Any]):
        keyword = self.keyword_from_record(record) or json.dumps(record, ensure_ascii=False)
        item = QListWidgetItem()
        item.setData(Qt.UserRole, dict(record))
        card = RankCard(record, rank, keyword, self.ui_metrics, self._theme_name, self)
        card.searchRequested.connect(self.searchRequested)
        item.setSizeHint(QSize(0, card.sizeHint().height() + self.ui_metrics.get("card_gap", 10)))
        self.addItem(item)
        self.setItemWidget(item, card)

    def repaint_cards(self):
        for index in range(self.count()):
            item = self.item(index)
            widget = self.itemWidget(item)
            if isinstance(widget, RankCard):
                widget.metrics = dict(self.ui_metrics)
                widget.apply_visual_theme(self._theme_name)
                item.setSizeHint(QSize(0, widget.sizeHint().height() + self.ui_metrics.get("card_gap", 10)))

    def current_record(self) -> Optional[Dict[str, Any]]:
        item = self.currentItem()
        if not item:
            return None
        record = item.data(Qt.UserRole)
        return dict(record) if isinstance(record, dict) else None

    def search_current_record(self):
        record = self.current_record()
        if record:
            self.searchRequested.emit(record)


class QrDialog(QDialog):
    """二维码预览弹窗。"""

    def __init__(self, image_bytes: bytes, link: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("扫描二维码")
        self.ui_metrics = getattr(parent, "ui_metrics", build_ui_metrics(QApplication.instance()))
        self.resize(self.ui_metrics.get("qr_dialog_width", 360), self.ui_metrics.get("qr_dialog_height", 420))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.ui_metrics.get("page_margin", 14), self.ui_metrics.get("page_margin", 14), self.ui_metrics.get("page_margin", 14), self.ui_metrics.get("page_margin", 14))
        layout.setSpacing(self.ui_metrics.get("layout_spacing", 10))
        label = QLabel("使用手机相机或微信扫一扫")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        qr_size = self.ui_metrics.get("qr_image_size", 280)
        image_label.setPixmap(pixmap.scaled(qr_size, qr_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(image_label, 1)

        link_edit = QLineEdit(link)
        link_edit.setReadOnly(True)
        layout.addWidget(link_edit)

        close_btn = compact_button_policy(QPushButton("关闭"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class FloatingStatusLabel(QLabel):
    """左下角悬浮临时状态提示，不参与主布局。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.theme = "dark"
        self.setObjectName("floatingStatus")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setWordWrap(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
        self.update_visual_theme(self.theme, self.ui_metrics)
        self.hide()

    def show_message(self, message: str, timeout: int = 5000):
        text = str(message or "").strip()
        self.hide_timer.stop()
        if not text:
            self.hide()
            return

        self.setText(text)
        self.reposition()
        self.show()
        self.raise_()
        if int(timeout) > 0:
            self.hide_timer.start(int(timeout))

    def update_visual_theme(self, theme: str, metrics: Dict[str, Any]):
        self.theme = "light" if theme == "light" else "dark"
        self.ui_metrics = dict(metrics or {})
        font_size = self.ui_metrics.get("status_font_size", self.ui_metrics.get("small_font_size", 12))
        padding_v = max(5, self.ui_metrics.get("input_padding_v", 6))
        padding_h = max(12, self.ui_metrics.get("input_padding_h", 8) + 4)
        radius = max(9, self.ui_metrics.get("card_radius", 10))
        if self.theme == "light":
            style = f"""
                QLabel#floatingStatus {{
                    background: rgba(255, 255, 255, 236);
                    color: #334155;
                    border: 1px solid #cbd5e1;
                    border-radius: {radius}px;
                    padding: {padding_v}px {padding_h}px;
                    font-size: {font_size}px;
                }}
            """
        else:
            style = f"""
                QLabel#floatingStatus {{
                    background: rgba(18, 18, 26, 238);
                    color: #e5e7eb;
                    border: 1px solid #2d2d3d;
                    border-radius: {radius}px;
                    padding: {padding_v}px {padding_h}px;
                    font-size: {font_size}px;
                }}
            """
        # 中文：Toast 使用子控件悬浮显示而不是 QStatusBar，因为 QStatusBar 会占用窗口底部布局高度。
        # English: The toast is rendered as a floating child widget instead of QStatusBar because QStatusBar consumes bottom layout height.
        self.setFont(QFont("Microsoft YaHei", font_size))
        self.setStyleSheet(style)
        self.reposition()

    def reposition(self):
        parent = self.parentWidget()
        if not parent:
            return
        margin = self.ui_metrics.get("page_margin", 14)
        max_width = max(260, int(parent.width() * 0.55))
        self.setMaximumWidth(max_width)
        self.adjustSize()
        hint = self.sizeHint()
        self.resize(min(hint.width(), max_width), hint.height())
        self.move(margin, max(margin, parent.height() - self.height() - margin))


class MainWindow(QMainWindow):
    """原生 PyQt5 桌面主窗口。"""

    def __init__(self, data_manager: DataManager, initial_keyword: str = "", initial_preset: str = "all", preview_json: bool = False):
        super().__init__()
        self.data_manager = data_manager
        self.api_client = ApiClient()
        self.current_thread: Optional[TaskThread] = None
        self.current_records: List[Dict[str, Any]] = []
        self.daily_records: List[Dict[str, Any]] = []
        self.rank_records: List[Dict[str, Any]] = []
        self.rank_source = "drama"
        self.preview_json_on_start = preview_json
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        self.theme_mode = self.data_manager.load_theme_mode()
        self.current_theme = self.resolve_effective_theme(self.theme_mode)
        self.connected_screen = None
        self.system_theme_timer = QTimer(self)
        self.system_theme_timer.timeout.connect(self.refresh_system_theme_if_needed)

        self.setWindowTitle("酷乐短剧 / 影视资源聚合搜索 - PyQt5")
        self.apply_adaptive_window_size()
        self.init_ui()
        self.setup_screen_adaptation()
        self.apply_theme_mode(self.theme_mode, persist=False)
        self.refresh_history_list()
        self.refresh_favorites()
        QTimer.singleShot(200, self.show_policy_dialog)

        if initial_keyword:
            self.search_input.setText(initial_keyword)
            self.type_select.setCurrentText(PRESET_LABEL.get(initial_preset, PRESET_LABEL["all"]))
            if preview_json:
                self.tabs.setCurrentWidget(self.api_page)
                self.api_keyword_input.setText(initial_keyword)
                self.api_from_select.setCurrentText(PRESET_LABEL.get(initial_preset, PRESET_LABEL["all"]))
                QTimer.singleShot(450, self.preview_api_json)
            else:
                QTimer.singleShot(450, self.perform_search)

    def apply_adaptive_window_size(self):
        # 中文：启动窗口不能固定 1280x820，否则低分辨率设备会被裁切，高分辨率设备又显得过小。
        # English: The launch window cannot stay fixed at 1280x820 because low-resolution screens clip it while high-resolution screens make it look too small.
        metrics = self.ui_metrics
        self.resize(metrics["window_width"], metrics["window_height"])
        self.setMinimumSize(metrics["minimum_width"], metrics["minimum_height"])

        screen = QApplication.instance().primaryScreen()
        if screen:
            available = screen.availableGeometry()
            x = available.x() + max(0, (available.width() - metrics["window_width"]) // 2)
            y = available.y() + max(0, (available.height() - metrics["window_height"]) // 2)
            self.move(x, y)

    def setup_screen_adaptation(self):
        application = QApplication.instance()
        if not application:
            return
        application.primaryScreenChanged.connect(self.on_primary_screen_changed)
        self.bind_screen_signals(application.primaryScreen())

    def on_primary_screen_changed(self, screen):
        self.bind_screen_signals(screen)
        self.refresh_ui_scale(resize_window=True)

    def bind_screen_signals(self, screen):
        if not screen or screen is self.connected_screen:
            return
        self.connected_screen = screen
        try:
            # 中文：监听分辨率和 DPI 变化，让用户切换显示器或调整系统缩放后无需重启应用。
            # English: Listening to resolution and DPI changes lets users move displays or change OS scaling without restarting the app.
            screen.geometryChanged.connect(lambda _geometry: self.refresh_ui_scale())
            screen.logicalDotsPerInchChanged.connect(lambda _dpi: self.refresh_ui_scale())
        except Exception:
            pass

    def refresh_ui_scale(self, resize_window: bool = False):
        # 中文：刷新时只更新字体和控件尺寸，默认不重置窗口位置，避免用户手动摆放窗口后被程序打断。
        # English: Refreshing updates fonts and controls by default without moving the window, so the app does not disrupt a manually placed window.
        old_scale = self.ui_metrics.get("scale", 1.0)
        self.ui_metrics = build_ui_metrics(QApplication.instance())
        new_scale = self.ui_metrics.get("scale", 1.0)
        if resize_window:
            self.apply_adaptive_window_size()
        self.apply_theme_mode(getattr(self, "theme_mode", self.data_manager.load_theme_mode()), persist=False)
        self.apply_widget_metrics()
        if abs(old_scale - new_scale) >= 0.05:
            self.set_status(f"已根据当前屏幕自动调整界面缩放：{new_scale:.2f}x")

    def apply_layout_spacing(self, layout=None):
        if layout is None:
            central = self.centralWidget()
            layout = central.layout() if central else None
        if layout is None:
            return
        # 中文：Qt 布局默认间距是固定像素，递归更新可以让输入区、按钮区和表格区在不同分辨率下保持同样的视觉密度。
        # English: Qt layout spacing defaults to fixed pixels, so recursive updates keep input rows, button rows, and tables visually balanced across resolutions.
        layout.setSpacing(self.ui_metrics["layout_spacing"])
        for index in range(layout.count()):
            child = layout.itemAt(index)
            child_layout = child.layout() if child else None
            if child_layout:
                self.apply_layout_spacing(child_layout)

    def apply_widget_metrics(self):
        metrics = self.ui_metrics
        self.setFont(QFont("Microsoft YaHei", metrics["base_font_size"]))
        if hasattr(self, "floating_status"):
            self.floating_status.update_visual_theme(getattr(self, "current_theme", "dark"), metrics)
        self.apply_layout_spacing()
        if hasattr(self, "tabs"):
            self.tabs.setStyleSheet("")
        # 中文：全局刷新时统一收紧按钮尺寸策略，防止新建控件在 QHBoxLayout 中被拉伸成过宽的块状按钮。
        # English: Global refresh keeps button size policies compact so newly created widgets are not stretched into oversized blocks in QHBoxLayout.
        for button in self.findChildren(QPushButton):
            compact_button_policy(button)
        for combo in self.findChildren(QComboBox):
            if isinstance(combo, StableComboBox):
                combo.configure_popup(metrics)
        for table_name in ("results_table", "api_preview_links_table", "daily_table", "favorites_table"):
            table = getattr(self, table_name, None)
            if table:
                table.apply_adaptive_metrics()
                table.set_visual_theme(getattr(self, "current_theme", "dark"))
        if hasattr(self, "rank_list"):
            self.rank_list.apply_adaptive_metrics()
            self.rank_list.set_visual_theme(getattr(self, "current_theme", "dark"))
        if hasattr(self, "history_list"):
            self.history_list.setSpacing(metrics.get("history_card_gap", 8))
            self.history_list.setMinimumWidth(metrics.get("history_min_width", 220))
            self.refresh_history_list()
        if hasattr(self, "search_page") and hasattr(self, "results_table"):
            # 中文：侧边历史宽度按屏幕比例调整，卡片式历史需要比旧单行列表更宽，才能避免关键词和操作按钮互相挤压。
            # English: The history sidebar scales with the screen; card-style history needs more width than the old single-line list to avoid squeezing keywords and buttons.
            splitter = self.results_table.parentWidget().parentWidget()
            if isinstance(splitter, QSplitter):
                splitter.setSizes([metrics["history_width"], max(metrics["history_width"] * 3, 1)])

    def apply_plain_table_theme(self, table: QTableWidget):
        theme = getattr(self, "current_theme", "dark")
        colors = ResourceTable._build_theme_colors(theme)
        metrics = self.ui_metrics

        # 中文：普通榜单表格也显式绑定主题色，避免只有资源表格修复而榜单仍受系统浅色调色板影响。
        # English: Plain rank tables also bind theme colors explicitly so only fixing resource tables does not leave rank tables affected by the system light palette.
        palette = table.palette()
        palette.setColor(QPalette.Base, QColor(colors["table_bg"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["row_alt"]))
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.Highlight, QColor(colors["selection_bg"]))
        palette.setColor(QPalette.HighlightedText, QColor(colors["selection_text"]))
        table.setPalette(palette)
        table.viewport().setPalette(palette)
        table.setAlternatingRowColors(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors["table_bg"]};
                color: {colors["text"]};
                gridline-color: {colors["grid"]};
                selection-background-color: {colors["selection_bg"]};
                selection-color: {colors["selection_text"]};
                border: 1px solid {colors["grid"]};
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: {max(2, metrics.get("input_padding_v", 6) // 2)}px {metrics.get("input_padding_h", 8)}px;
                border-bottom: 1px solid {colors["grid"]};
            }}
            QTableWidget::item:selected {{
                background-color: {colors["selection_bg"]};
                color: {colors["selection_text"]};
            }}
        """)
        for row in range(table.rowCount()):
            background = colors["row_alt"] if row % 2 else colors["row_bg"]
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    item.setBackground(QBrush(QColor(background)))
                    item.setForeground(QBrush(QColor(colors["text"])))

    def init_ui(self):
        self.create_actions()

        # 只保留 QTabWidget 作为页面切换入口，避免工具栏和页签同时承担导航职责导致用户误以为存在两套状态。
        # Keep QTabWidget as the only page navigation entry, because duplicated toolbar tabs make users think two independent navigation states exist.
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(self.ui_metrics["page_margin"], self.ui_metrics["page_margin"], self.ui_metrics["page_margin"], self.ui_metrics["page_margin"])
        root.setSpacing(self.ui_metrics["layout_spacing"])

        title = QLabel("酷乐短剧 / 影视资源 · PyQt5")
        title.setObjectName("appTitle")
        title.setFont(QFont("Microsoft YaHei", self.ui_metrics["title_font_size"], QFont.Bold))
        root.addWidget(title)

        # 中文：顶部标题区不再放置状态文本，避免主内容上方长期残留“正在...”这类过期提示。
        # English: The title area no longer contains status text, preventing stale messages such as "loading..." from remaining above the content.
        self.tabs = QTabWidget()
        self.search_page = self.create_search_page()
        self.api_page = self.create_api_page()
        self.daily_page = self.create_daily_page()
        self.rank_page = self.create_rank_page()
        self.favorites_page = self.create_favorites_page()
        self.tabs.addTab(self.search_page, "聚合搜索")
        self.tabs.addTab(self.api_page, "API生成器")
        self.tabs.addTab(self.daily_page, "每日影视")
        self.tabs.addTab(self.rank_page, "热度榜")
        self.tabs.addTab(self.favorites_page, "我的收藏")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        root.addWidget(self.tabs, 1)

        self.setCentralWidget(central)
        self.configure_status_overlay()

    def configure_status_overlay(self):
        # 中文：临时状态提示改为悬浮 Toast，不进入主布局，因此不会挤占结果列表或页签内容空间。
        # English: Temporary status messages now use a floating toast outside the main layout, so they do not consume space from result lists or tabs.
        self.floating_status = FloatingStatusLabel(self.centralWidget())
        self.floating_status.update_visual_theme(getattr(self, "current_theme", "dark"), self.ui_metrics)
        self.floating_status.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "floating_status"):
            # 中文：窗口尺寸变化时重新贴靠左下角，保证悬浮状态不会漂到内容中间或被裁切。
            # English: Re-anchoring on resize keeps the floating status at the bottom-left instead of drifting into content or being clipped.
            self.floating_status.reposition()

    def create_actions(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        view_menu = menubar.addMenu("视图")
        help_menu = menubar.addMenu("帮助")

        self.export_results_action = QAction("导出当前结果 JSON", self)
        self.export_results_action.triggered.connect(self.export_current_results)
        file_menu.addAction(self.export_results_action)

        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)
        self.light_theme_action = self.create_theme_action("浅色模式", "light")
        self.dark_theme_action = self.create_theme_action("深色模式", "dark")
        self.system_theme_action = self.create_theme_action("跟随系统（默认）", "system")
        for action in (self.light_theme_action, self.dark_theme_action, self.system_theme_action):
            view_menu.addAction(action)

        github_action = QAction("打开 GitHub 项目", self)
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/SELFEMO/ShortDramaSearch")))
        help_menu.addAction(github_action)

        online_action = QAction("打开在线网页", self)
        online_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(ONLINE_PAGE_URL)))
        help_menu.addAction(online_action)

        policy_action = QAction("用户使用条例", self)
        policy_action.triggered.connect(lambda: self.show_policy_dialog(force=True))
        help_menu.addAction(policy_action)

        help_api_action = QAction("API 使用说明", self)
        help_api_action.triggered.connect(self.show_api_help)
        help_menu.addAction(help_api_action)

    def create_theme_action(self, label: str, mode: str) -> QAction:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setData(mode)
        action.triggered.connect(lambda checked, selected=mode: checked and self.set_theme_mode(selected))
        self.theme_action_group.addAction(action)
        return action

    def update_theme_actions(self):
        if not hasattr(self, "theme_action_group"):
            return
        for action in self.theme_action_group.actions():
            blocked = action.blockSignals(True)
            action.setChecked(action.data() == getattr(self, "theme_mode", "system"))
            action.blockSignals(blocked)

    def create_search_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        tip = QLabel("基于酷乐 API 的聚合资源搜索。关键词空格会自动拆分并合并去重，和 GitHub Pages 版保持一致。")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入短剧 / 影视资源名称搜索...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.type_select = StableComboBox()
        self.fill_preset_combo(self.type_select)
        self.search_button = compact_button_policy(QPushButton("搜索"))
        self.search_button.clicked.connect(self.perform_search)
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(self.type_select)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)

        extra_row = QHBoxLayout()
        self.hide_broken_checkbox = QCheckBox("隐藏本地标记失效链接")
        self.hide_broken_checkbox.stateChanged.connect(self.refresh_search_table)
        copy_links_btn = compact_button_policy(QPushButton("复制当前结果链接"))
        copy_links_btn.clicked.connect(self.copy_current_result_links)
        export_history_btn = compact_button_policy(QPushButton("导出历史"))
        export_history_btn.clicked.connect(self.export_history)
        import_history_btn = compact_button_policy(QPushButton("导入历史"))
        import_history_btn.clicked.connect(self.import_history)
        extra_row.addWidget(self.hide_broken_checkbox)
        extra_row.addStretch(1)
        extra_row.addWidget(copy_links_btn)
        extra_row.addWidget(export_history_btn)
        extra_row.addWidget(import_history_btn)
        layout.addLayout(extra_row)

        splitter = QSplitter(Qt.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        history_header = QHBoxLayout()
        history_header.addWidget(QLabel("最近搜索"))
        clear_history_btn = compact_button_policy(QPushButton("清空"))
        clear_history_btn.clicked.connect(self.clear_history)
        history_header.addWidget(clear_history_btn)
        left_layout.addLayout(history_header)
        self.history_list = QListWidget()
        # 中文：历史记录改成卡片列表并关闭横向滚动，避免长关键词和时间戳挤成一行后出现底部滚动条。
        # English: Search history uses cards with horizontal scrolling disabled so long keywords and timestamps do not squeeze into one line with a bottom scrollbar.
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.history_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        install_auto_hide_scrollbars(self.history_list, horizontal=False)
        self.history_list.setSpacing(self.ui_metrics.get("history_card_gap", 8))
        self.history_list.itemDoubleClicked.connect(self.search_from_history_item)
        left_layout.addWidget(self.history_list)
        left_panel.setMinimumWidth(self.ui_metrics.get("history_min_width", 220))
        splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.search_summary = QLabel("请输入关键词开始搜索。")
        right_layout.addWidget(self.search_summary)
        self.results_table = ResourceTable(self.data_manager)
        self.bind_table(self.results_table)
        right_layout.addWidget(self.results_table, 1)
        # 中文：资源卡片内部已提供主要操作按钮，底部不再重复放置一排全局按钮，避免用户在“选中行”和“卡片按钮”之间产生困惑。
        # English: Resource cards already contain the primary action buttons, so the duplicated bottom action row is removed to avoid confusion between selected-row actions and card buttons.
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        layout.addWidget(splitter, 1)
        return page

    def create_api_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        form_box = QGroupBox("API 生成器")
        form_layout = QVBoxLayout(form_box)
        fields = QGridLayout()
        fields.addWidget(QLabel("搜索关键词："), 0, 0)
        self.api_keyword_input = QLineEdit()
        self.api_keyword_input.setPlaceholderText("例如：飞驰人生3")
        self.api_keyword_input.textChanged.connect(self.update_api_generated_url)
        fields.addWidget(self.api_keyword_input, 0, 1)
        fields.addWidget(QLabel("搜索来源："), 1, 0)
        self.api_from_select = StableComboBox()
        self.fill_preset_combo(self.api_from_select)
        self.api_from_select.currentIndexChanged.connect(self.update_api_generated_url)
        fields.addWidget(self.api_from_select, 1, 1)
        fields.addWidget(QLabel("生成链接："), 2, 0)
        self.api_url_output = QLineEdit()
        self.api_url_output.setReadOnly(True)
        fields.addWidget(self.api_url_output, 2, 1)
        form_layout.addLayout(fields)

        api_buttons = QHBoxLayout()
        generate_btn = compact_button_policy(QPushButton("生成 API 链接"))
        generate_btn.clicked.connect(self.update_api_generated_url)
        copy_btn = compact_button_policy(QPushButton("复制链接"))
        copy_btn.clicked.connect(lambda: self.copy_text(self.api_url_output.text(), "API 链接已复制。"))
        open_btn = compact_button_policy(QPushButton("打开在线 JSON"))
        open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.api_url_output.text())) if self.api_url_output.text() else None)
        preview_btn = compact_button_policy(QPushButton("预览 JSON 结果"))
        preview_btn.clicked.connect(self.preview_api_json)
        help_btn = compact_button_policy(QPushButton("API 使用说明"))
        help_btn.clicked.connect(self.show_api_help)
        api_buttons.addWidget(generate_btn)
        api_buttons.addWidget(copy_btn)
        api_buttons.addWidget(open_btn)
        api_buttons.addWidget(preview_btn)
        api_buttons.addWidget(help_btn)
        api_buttons.addStretch(1)
        form_layout.addLayout(api_buttons)
        layout.addWidget(form_box)

        preview_splitter = QSplitter(Qt.Horizontal)
        json_box = QGroupBox("JSON 预览")
        json_layout = QVBoxLayout(json_box)
        self.api_preview_status = QLabel("请输入关键词后点击“预览 JSON 结果”。")
        json_layout.addWidget(self.api_preview_status)
        self.api_preview_output = QPlainTextEdit()
        self.api_preview_output.setReadOnly(True)
        install_auto_hide_scrollbars(self.api_preview_output, horizontal=True)
        self.api_preview_output.setPlainText(json.dumps({"code": 0, "msg": "waiting", "tip": "这里会显示预览 JSON，最多 5 条搜索结果。"}, ensure_ascii=False, indent=2))
        json_layout.addWidget(self.api_preview_output, 1)
        preview_splitter.addWidget(json_box)

        links_box = QGroupBox("链接快捷操作")
        links_layout = QVBoxLayout(links_box)
        self.api_preview_links_table = ResourceTable(self.data_manager)
        self.bind_table(self.api_preview_links_table)
        links_layout.addWidget(self.api_preview_links_table, 1)
        # 中文：预览区同样使用卡片内联操作，保持和搜索结果一致的操作路径。
        # English: The preview area uses inline card actions as well, keeping the operation path consistent with search results.
        preview_splitter.addWidget(links_box)
        preview_splitter.setStretchFactor(0, 1)
        preview_splitter.setStretchFactor(1, 1)
        layout.addWidget(preview_splitter, 1)
        self.update_api_generated_url()
        return page

    def create_daily_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel("每日影视资源：合并百度与夸克源，仅展示每日最新影视资源和热门资源。")
        header.setWordWrap(True)
        layout.addWidget(header)

        row = QHBoxLayout()
        self.daily_filter_input = QLineEdit()
        self.daily_filter_input.setPlaceholderText("在今日影视资源中检索...")
        self.daily_filter_input.textChanged.connect(self.refresh_daily_table)
        refresh_btn = compact_button_policy(QPushButton("刷新"))
        refresh_btn.clicked.connect(self.load_daily_resources)
        row.addWidget(self.daily_filter_input, 1)
        row.addWidget(refresh_btn)
        layout.addLayout(row)

        self.daily_summary = QLabel("点击刷新加载每日影视资源。")
        layout.addWidget(self.daily_summary)
        self.daily_table = ResourceTable(self.data_manager)
        self.bind_table(self.daily_table)
        layout.addWidget(self.daily_table, 1)
        # 中文：每日影视列表复用卡片操作，避免窄表格按钮在高 DPI 下被压缩。
        # English: Daily resources reuse card actions to avoid cramped table buttons on high-DPI displays.
        return page

    def create_rank_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel("热度榜：支持短剧热度榜与夸克短剧热搜榜，双击榜单项可跳转聚合搜索。")
        header.setWordWrap(True)
        layout.addWidget(header)

        row = QHBoxLayout()
        self.rank_source_select = StableComboBox()
        self.rank_source_select.addItem("短剧热度榜", "drama")
        self.rank_source_select.addItem("夸克热搜榜", "vtquark")
        self.rank_source_select.currentIndexChanged.connect(self.load_rank_resources)
        self.rank_filter_input = QLineEdit()
        self.rank_filter_input.setPlaceholderText("在当前榜单中检索关键词...")
        self.rank_filter_input.textChanged.connect(self.refresh_rank_table)
        refresh_btn = compact_button_policy(QPushButton("刷新榜单"))
        refresh_btn.clicked.connect(self.load_rank_resources)
        row.addWidget(self.rank_source_select)
        row.addWidget(self.rank_filter_input, 1)
        row.addWidget(refresh_btn)
        layout.addLayout(row)

        self.rank_summary = QLabel("点击刷新榜单。")
        layout.addWidget(self.rank_summary)
        self.rank_list = RankList()
        self.rank_list.searchRequested.connect(self.search_rank_record)
        self.rank_list.set_visual_theme(getattr(self, "current_theme", "dark"))
        layout.addWidget(self.rank_list, 1)
        # 中文：热度榜改用卡片列表，原因是多数榜单没有说明字段，表格会制造大面积空列并把操作按钮挤成竖排。
        # English: The rank page uses cards because many rank APIs have no description field; a table creates huge empty columns and squeezes action buttons vertically.
        return page

    def create_favorites_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel("收藏保存在本机 ~/.short_drama_search，不会上传到服务器。")
        header.setWordWrap(True)
        layout.addWidget(header)

        row = QHBoxLayout()
        self.favorite_filter_input = QLineEdit()
        self.favorite_filter_input.setPlaceholderText("在收藏中搜索名称 / 来源 / 链接...")
        self.favorite_filter_input.textChanged.connect(self.refresh_favorites)
        export_btn = compact_button_policy(QPushButton("导出收藏"))
        export_btn.clicked.connect(self.export_favorites)
        import_btn = compact_button_policy(QPushButton("导入收藏"))
        import_btn.clicked.connect(self.import_favorites)
        clear_btn = compact_button_policy(QPushButton("清空收藏"))
        clear_btn.clicked.connect(self.clear_favorites)
        row.addWidget(self.favorite_filter_input, 1)
        row.addWidget(export_btn)
        row.addWidget(import_btn)
        row.addWidget(clear_btn)
        layout.addLayout(row)

        self.favorite_summary = QLabel("暂无收藏。")
        layout.addWidget(self.favorite_summary)
        self.favorites_table = ResourceTable(self.data_manager)
        self.bind_table(self.favorites_table)
        layout.addWidget(self.favorites_table, 1)
        # 中文：收藏页复用同一套卡片交互，用户不需要切换操作习惯。
        # English: Favorites reuse the same card interaction so users do not need to switch operation habits.
        return page

    def fill_preset_combo(self, combo: QComboBox):
        combo.clear()
        for key in ("all", "netdisk", "baidu", "quark", "aliyun", "tianyi", "uc", "mobile", "115", "pikpak", "xunlei", "123", "magnet", "ed2k"):
            combo.addItem(PRESET_LABEL.get(key, key), key)

    def bind_table(self, table: ResourceTable):
        table.actionRequested.connect(self.handle_resource_action)
        table.qualityChanged.connect(self.handle_quality_changed)

    def create_resource_action_row(self, table: ResourceTable) -> QHBoxLayout:
        row = QHBoxLayout()
        actions = [
            ("打开链接", lambda: self.handle_current_table_action(table, "open")),
            ("复制链接", lambda: self.handle_current_table_action(table, "copy_link")),
            ("复制密码", lambda: self.handle_current_table_action(table, "copy_pwd")),
            ("二维码", lambda: self.handle_current_table_action(table, "qr")),
            ("详情", lambda: self.handle_current_table_action(table, "detail")),
        ]
        for text, callback in actions:
            button = compact_button_policy(QPushButton(text))
            button.clicked.connect(callback)
            row.addWidget(button)
        row.addStretch(1)
        return row

    def set_status(self, message: str, timeout: int = 5000):
        # 中文：状态提示改为左下角悬浮 Toast；它不占用任何布局空间，普通提示会自动消失，忙碌提示由后续状态覆盖或清空。
        # English: Status messages use a bottom-left floating toast; it consumes no layout space, normal messages auto-hide, and busy messages are replaced or cleared by later states.
        if hasattr(self, "floating_status"):
            self.floating_status.show_message(str(message or ""), max(0, int(timeout)))

    def preset_from_combo(self, combo: QComboBox) -> str:
        return combo.currentData() or "all"

    def run_task(self, task: Callable[[], Any], on_success: Callable[[Any], None], busy_message: str):
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.information(self, "提示", "已有任务正在执行，请稍后。")
            return
        self.set_status(busy_message, timeout=0)
        self.current_thread = TaskThread(task, self)
        self.current_thread.success.connect(on_success)
        self.current_thread.failure.connect(self.on_task_error)
        self.current_thread.finished.connect(lambda: self.search_button.setEnabled(True))
        self.search_button.setEnabled(False)
        self.current_thread.start()

    def on_task_error(self, message: str):
        self.set_status(f"操作失败：{message}")
        QMessageBox.warning(self, "操作失败", message)

    def perform_search(self):
        keyword = self.api_client.normalize_search_keyword(self.search_input.text())
        if not keyword:
            QMessageBox.information(self, "提示", "请输入搜索关键词。")
            return
        preset = self.preset_from_combo(self.type_select)

        def task():
            result = self.api_client.fetch_and_merge_data_stable(keyword, preset, attempts=2)
            return result

        self.run_task(task, lambda result: self.on_search_success(keyword, preset, result), f"正在搜索：{keyword} ...")

    def on_search_success(self, keyword: str, preset: str, result: Dict[str, Any]):
        self.current_records = self.api_client.flatten_merged_result(result)
        total = len(self.current_records)
        self.data_manager.save_search_history(keyword, total)
        self.data_manager.cache_results(f"{preset}:{keyword}", self.current_records)
        self.refresh_history_list()
        self.refresh_search_table()
        api_status = result.get("apiStatus", {})
        self.search_summary.setText(
            f"关键词：{keyword}｜来源：{PRESET_LABEL.get(preset, preset)}｜共 {total} 条｜成功请求 {api_status.get('successCount', 0)} 次，失败 {api_status.get('failedCount', 0)} 次"
        )
        self.set_status(f"搜索完成，共 {total} 条结果。")

    def refresh_search_table(self):
        # 中文：刷新结果前先同步当前主题，避免搜索后新创建的卡片沿用列表初始化时的默认深色。
        # English: The current theme is synced before rebuilding results so newly created cards do not keep the list's default dark theme.
        self.results_table.set_visual_theme(getattr(self, "current_theme", "dark"))
        self.results_table.set_records(self.current_records, show_broken=not self.hide_broken_checkbox.isChecked())

    def refresh_history_list(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.clear()
        self.history_list.setSpacing(self.ui_metrics.get("history_card_gap", 8))
        for record in self.data_manager.load_search_history():
            keyword = str(record.get("keyword", "")).strip()
            if not keyword:
                continue
            list_item = QListWidgetItem()
            list_item.setData(Qt.UserRole, keyword)
            card = self.create_history_card(record)
            list_item.setSizeHint(QSize(0, card.sizeHint().height() + self.ui_metrics.get("history_card_gap", 8)))
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, card)

    def create_history_card(self, record: Dict[str, Any]) -> QFrame:
        keyword = str(record.get("keyword", "")).strip()
        count = int(record.get("count") or 0)
        timestamp = format_timestamp(record.get("timestamp"))
        frame = QFrame()
        frame.setObjectName("historyCard")
        layout = QVBoxLayout(frame)
        padding = self.ui_metrics.get("history_card_padding", 10)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(max(3, self.ui_metrics.get("layout_spacing", 10) // 2))

        title_row = QHBoxLayout()
        keyword_label = QLabel(keyword)
        keyword_label.setObjectName("historyKeyword")
        keyword_label.setWordWrap(True)
        keyword_label.setToolTip(keyword)
        title_row.addWidget(keyword_label, 1)
        search_btn = compact_button_policy(QPushButton("重搜"))
        search_btn.setObjectName("historySearchButton")
        search_btn.clicked.connect(lambda _checked=False, current_keyword=keyword: self.start_search_from_keyword(current_keyword))
        title_row.addWidget(search_btn)
        layout.addLayout(title_row)

        meta = QLabel(f"{count} 条结果 · {timestamp}" if timestamp else f"{count} 条结果")
        meta.setObjectName("historyMeta")
        layout.addWidget(meta)
        return frame

    def start_search_from_keyword(self, keyword: str):
        # 中文：历史卡片上的“重搜”直接复用主搜索流程，避免用户先选中历史项再去点底部按钮的二次操作。
        # English: The history card's rerun button reuses the main search flow directly, avoiding a two-step select-then-action pattern.
        keyword = str(keyword or "").strip()
        if not keyword:
            return
        self.search_input.setText(keyword)
        self.tabs.setCurrentWidget(self.search_page)
        self.perform_search()

    def search_from_history_item(self, item: QListWidgetItem):
        keyword = item.data(Qt.UserRole) or ""
        self.start_search_from_keyword(keyword)

    def clear_history(self):
        if QMessageBox.question(self, "确认", "确定清空搜索历史吗？") == QMessageBox.Yes:
            self.data_manager.clear_search_history()
            self.refresh_history_list()

    def update_api_generated_url(self):
        keyword = self.api_client.normalize_search_keyword(self.api_keyword_input.text())
        preset = self.preset_from_combo(self.api_from_select)
        self.api_url_output.setText(self.api_client.build_online_api_url(keyword, preset))

    def preview_api_json(self):
        keyword = self.api_client.normalize_search_keyword(self.api_keyword_input.text())
        if not keyword:
            QMessageBox.information(self, "提示", "请先输入搜索关键词。")
            return
        preset = self.preset_from_combo(self.api_from_select)
        self.update_api_generated_url()
        self.api_preview_status.setText("正在请求接口并生成预览...")

        def task():
            result = self.api_client.fetch_and_merge_data_stable(keyword, preset, attempts=3)
            merged = result.get("mergedByType", {})
            types = result.get("typeList", [])
            preview_data, preview_count = self.api_client.build_limited_preview_data(merged, types, limit=5)
            payload = {
                "code": 0,
                "msg": "success",
                "keyword": keyword,
                "type": result.get("effectivePreset", preset),
                "total": result.get("total", 0),
                "data": preview_data,
            }
            return payload, preview_count

        self.run_task(task, self.on_preview_success, "正在预览 JSON ...")

    def on_preview_success(self, payload_and_count):
        payload, preview_count = payload_and_count
        self.api_preview_output.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2))
        records: List[Dict[str, Any]] = []
        for resource_type, items in (payload.get("data") or {}).items():
            records.extend(self.api_client.normalize_resource_item(item, resource_type) for item in items)
        self.api_preview_links_table.set_visual_theme(getattr(self, "current_theme", "dark"))
        self.api_preview_links_table.set_records(records)
        self.api_preview_status.setText(f"预览完成：真实结果共 {payload.get('total', 0)} 条，预览区展示 {preview_count} 条。")
        self.set_status("JSON 预览完成。")

    def load_daily_resources(self):
        self.run_task(self.api_client.get_daily_resources, self.on_daily_loaded, "正在加载每日影视资源 ...")

    def on_daily_loaded(self, result: Dict[str, Any]):
        self.daily_records = result.get("data", []) or []
        self.refresh_daily_table()
        self.set_status(f"每日影视加载完成，共 {len(self.daily_records)} 条。")

    def refresh_daily_table(self):
        keyword = self.daily_filter_input.text().strip().lower()
        records = self.daily_records
        if keyword:
            records = [item for item in records if keyword in str(item.get("name", "")).lower() or keyword in str(item.get("url", "")).lower()]
        self.daily_summary.setText(f"共 {len(records)} 条影视资源。")
        self.daily_table.set_visual_theme(getattr(self, "current_theme", "dark"))
        self.daily_table.set_records(records)

    def load_rank_resources(self):
        self.rank_source = self.rank_source_select.currentData() or "drama"
        if self.rank_source == "vtquark":
            self.run_task(lambda: self.api_client.get_vtquark_rank("短剧"), self.on_rank_loaded, "正在加载夸克热搜榜 ...")
        else:
            self.run_task(self.api_client.get_short_drama_rank, self.on_rank_loaded, "正在加载短剧热度榜 ...")

    def on_rank_loaded(self, result: Dict[str, Any]):
        data = result.get("data", result)
        if isinstance(data, dict):
            for key in ("list", "items", "rank", "data"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
        if not isinstance(data, list):
            data = []
        self.rank_records = data
        self.refresh_rank_table()
        self.set_status(f"榜单加载完成，共 {len(self.rank_records)} 条。")

    def rank_keyword_from_record(self, record: Dict[str, Any]) -> str:
        for key in ("keyword", "name", "title", "word", "text", "query"):
            value = str(record.get(key, "")).strip()
            if value:
                return value
        return ""

    def refresh_rank_table(self):
        keyword = self.rank_filter_input.text().strip().lower()
        records = []
        for record in self.rank_records:
            if not isinstance(record, dict):
                record = {"name": str(record)}
            text = json.dumps(record, ensure_ascii=False).lower()
            if not keyword or keyword in text:
                records.append(record)

        # 中文：筛选后的榜单直接交给 RankList 生成卡片，避免继续维护表格列宽、表头和单元格按钮这三套容易冲突的状态。
        # English: Filtered ranks are passed directly to RankList to build cards, avoiding three conflicting states: table column widths, headers, and cell buttons.
        self.rank_list.set_visual_theme(getattr(self, "current_theme", "dark"))
        self.rank_list.set_records(records)
        self.rank_summary.setText(f"当前展示 {len(records)} 条榜单。")

    def search_selected_rank(self):
        record = self.rank_list.current_record() if hasattr(self, "rank_list") else None
        if record:
            self.search_rank_record(record)

    def search_rank_record(self, record: Dict[str, Any]):
        keyword = self.rank_keyword_from_record(record)
        if not keyword:
            return
        # 中文：榜单跳转搜索固定使用全局聚合，和网页端点击榜单后强制 forceAll 的行为一致。
        # English: Rank-to-search uses global aggregation, matching the web page's forceAll behavior when a rank item is clicked.
        self.tabs.setCurrentWidget(self.search_page)
        self.search_input.setText(keyword)
        self.type_select.setCurrentText(PRESET_LABEL["all"])
        self.perform_search()

    def refresh_favorites(self):
        if not hasattr(self, "favorites_table"):
            return
        records = self.data_manager.get_favorites()
        keyword = self.favorite_filter_input.text().strip().lower() if hasattr(self, "favorite_filter_input") else ""
        if keyword:
            records = [item for item in records if keyword in json.dumps(item, ensure_ascii=False).lower()]
        self.favorite_summary.setText(f"共 {len(records)} 条收藏。")
        self.favorites_table.set_visual_theme(getattr(self, "current_theme", "dark"))
        self.favorites_table.set_records(records)

    def clear_favorites(self):
        if QMessageBox.question(self, "确认", "确定清空全部收藏吗？") == QMessageBox.Yes:
            self.data_manager.clear_favorites()
            self.refresh_favorites()
            self.refresh_search_table()

    def handle_current_table_action(self, table: ResourceTable, action: str):
        record = table.current_record()
        if not record:
            QMessageBox.information(self, "提示", "请先选中一条资源。")
            return
        self.handle_resource_action(action, record)

    def handle_resource_action(self, action: str, record: Dict[str, Any]):
        if action == "favorite":
            is_fav = self.data_manager.toggle_favorite(record)
            self.set_status("已收藏。" if is_fav else "已取消收藏。")
            self.refresh_all_resource_tables()
        elif action == "broken":
            is_broken = self.data_manager.toggle_broken_link(record)
            self.set_status("已标记失效。" if is_broken else "已取消失效标记。")
            self.refresh_all_resource_tables()
        elif action == "open":
            self.open_resource_link(record)
        elif action == "copy_link":
            self.copy_text(record.get("url", ""), "链接已复制。")
        elif action == "copy_pwd":
            self.copy_text(record.get("pwd", ""), "密码已复制。")
        elif action == "qr":
            self.show_qrcode(record)
        elif action == "detail":
            DetailDialog(record, self).exec_()

    def handle_quality_changed(self, link: str, score: int):
        self.data_manager.set_quality(link, score)
        self.set_status("本地质量评分已更新。")

    def refresh_all_resource_tables(self):
        self.refresh_search_table()
        self.refresh_daily_table()
        self.refresh_favorites()
        if hasattr(self, "api_preview_links_table"):
            self.api_preview_links_table.set_visual_theme(getattr(self, "current_theme", "dark"))
            self.api_preview_links_table.set_records(self.api_preview_links_table.records)

    def open_resource_link(self, record: Dict[str, Any]):
        url = record.get("url", "")
        if not url:
            QMessageBox.information(self, "提示", "该资源没有链接。")
            return
        QDesktopServices.openUrl(QUrl(url))

    def copy_text(self, text: str, message: str = "已复制。"):
        if not text:
            QMessageBox.information(self, "提示", "没有可复制的内容。")
            return
        QApplication.clipboard().setText(str(text))
        self.set_status(message)

    def show_qrcode(self, record: Dict[str, Any]):
        link = record.get("url", "")
        if not link:
            QMessageBox.information(self, "提示", "该资源没有链接。")
            return

        def task():
            return self.api_client.get_qrcode_image_bytes(link, self.ui_metrics.get("qr_image_size", 260))

        def on_qrcode_ready(data: bytes):
            # 中文：二维码已经生成时必须立即覆盖忙碌提示，否则模态窗口关闭后用户会误以为后台任务仍在运行。
            # English: The busy message must be replaced as soon as the QR code is ready; otherwise users may think the background task is still running after closing the modal dialog.
            self.set_status("二维码已生成，请使用手机扫码。")
            dialog = QrDialog(data, link, self)
            # 中文：弹窗关闭时只清空二维码相关临时提示，不再额外提示“二维码窗口已关闭”，避免无意义状态打扰用户。
            # English: When the dialog closes, only clear the QR-related toast instead of showing a redundant "QR window closed" message.
            dialog.finished.connect(lambda _code: self.set_status("", 0))
            dialog.exec_()

        self.run_task(task, on_qrcode_ready, "正在生成二维码 ...")

    def copy_current_result_links(self):
        links = [item.get("url", "") for item in self.current_records if item.get("url")]
        if self.hide_broken_checkbox.isChecked():
            links = [link for link in links if not self.data_manager.is_broken_marked(link)]
        if not links:
            QMessageBox.information(self, "提示", "当前没有可复制的结果链接。")
            return
        self.copy_text("\n".join(links), f"已复制 {len(links)} 条链接。")

    def export_json(self, default_name: str, data: Any):
        path, _ = QFileDialog.getSaveFileName(self, "导出 JSON", default_name, "JSON 文件 (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        self.set_status(f"已导出：{path}")

    def import_json(self) -> Optional[Any]:
        path, _ = QFileDialog.getOpenFileName(self, "导入 JSON", "", "JSON 文件 (*.json)")
        if not path:
            return None
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def export_current_results(self):
        self.export_json("shortdrama_results.json", self.current_records)

    def export_history(self):
        self.export_json("shortdrama_history.json", self.data_manager.load_search_history())

    def import_history(self):
        data = self.import_json()
        if data is None:
            return
        if not isinstance(data, list):
            QMessageBox.warning(self, "导入失败", "历史文件必须是 JSON 数组。")
            return
        self.data_manager.import_search_history(data)
        self.refresh_history_list()

    def export_favorites(self):
        self.export_json("shortdrama_favorites.json", self.data_manager.get_favorites())

    def import_favorites(self):
        data = self.import_json()
        if data is None:
            return
        if not isinstance(data, list):
            QMessageBox.warning(self, "导入失败", "收藏文件必须是 JSON 数组。")
            return
        self.data_manager.import_favorites(data)
        self.refresh_favorites()
        self.refresh_search_table()

    def on_tab_changed(self, index: int):
        current = self.tabs.widget(index)
        if current is self.daily_page and not self.daily_records:
            self.load_daily_resources()
        elif current is self.rank_page and not self.rank_records:
            self.load_rank_resources()
        elif current is self.favorites_page:
            self.refresh_favorites()

    def show_api_help(self):
        text = (
            "网页 API 参数：\n\n"
            f"基础地址：{ONLINE_PAGE_URL}\n"
            "q / name / s / keyword：搜索关键词，支持空格拆分。\n"
            "from：all、netdisk、baidu、quark、aliyun、tianyi、uc、mobile、115、pikpak、xunlei、123、magnet、ed2k。\n"
            "format=json：返回 JSON 数据。\n\n"
            "示例：\n"
            f"{ONLINE_PAGE_URL}?q=飞驰人生3&from=netdisk&format=json\n\n"
            "桌面版不嵌入 index.html，而是使用同样的第三方接口和字段结构生成等价预览。"
        )
        QMessageBox.information(self, "API 使用说明", text)

    def show_policy_dialog(self, force: bool = False):
        dialog = QDialog(self)
        dialog.setWindowTitle("用户使用条例")
        width = self.ui_metrics.get("policy_dialog_width", 620)
        max_height = self.ui_metrics.get("policy_dialog_height", 360)
        content_height = self.ui_metrics.get("policy_dialog_content_height", 210)
        dialog.setMinimumWidth(width)

        layout = QVBoxLayout(dialog)
        margin = self.ui_metrics.get("page_margin", 14)
        spacing = self.ui_metrics.get("layout_spacing", 10)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)

        content = QTextEdit()
        content.setObjectName("policyContent")
        content.setReadOnly(True)
        content.setFrameShape(QFrame.NoFrame)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # 中文：条例内容较短，正文区按内容固定为紧凑高度，避免 QTextEdit 在垂直布局中吃掉剩余空间形成大面积留白。
        # English: The policy text is short, so the text area uses a compact fixed height instead of letting QTextEdit consume remaining vertical space and create large blanks.
        content.setFixedHeight(content_height)
        install_auto_hide_scrollbars(content, horizontal=False)
        content.setHtml(
            "<style>"
            "body{margin:0;line-height:1.55;}"
            "h2{margin:0 0 12px 0;font-size:22px;}"
            "p{margin:0 0 10px 0;}"
            "</style>"
            "<h2>用户使用条例</h2>"
            "<p>本程序仅作为第三方公开索引信息的搜索聚合工具，不存储、不上传、不托管任何影视文件，亦不提供在线播放、下载、转存等服务。</p>"
            "<p>页面中展示的资源链接均来源于互联网公开索引信息，仅作为搜索结果聚合展示用途。所有链接会跳转至第三方网盘或外部平台，相关文件的有效性、安全性、合法性与可访问性均由用户自行判断并承担风险。</p>"
            "<p>本程序为个人兴趣开源项目，不收取任何费用、不用于商业用途、不参与任何资源运营行为。</p>"
            "<p>若相关资源、接口或内容涉及侵权问题，请优先联系对应接口平台或资源提供方进行处理。</p>"
            "<p>GitHub 项目地址：https://github.com/SELFEMO/ShortDramaSearch</p>"
        )
        layout.addWidget(content)

        actions = QHBoxLayout()
        actions.setSpacing(spacing)
        reject_btn = compact_button_policy(QPushButton("拒绝并退出"))
        accept_btn = compact_button_policy(QPushButton("我已阅读并确认"))
        reject_btn.clicked.connect(dialog.reject)
        accept_btn.clicked.connect(dialog.accept)
        actions.addStretch(1)
        actions.addWidget(reject_btn)
        actions.addWidget(accept_btn)
        layout.addLayout(actions)

        dialog.adjustSize()
        # 中文：最终高度仍受屏幕自适应上限控制，保证小屏不溢出，同时不再像旧版本那样强制拉到 520px。
        # English: The final height is still capped by adaptive screen metrics so small displays are safe, while avoiding the old forced 520px height.
        dialog.resize(width, min(max_height, dialog.sizeHint().height()))

        if dialog.exec_() != QDialog.Accepted and not force:
            QApplication.instance().quit()

    @staticmethod
    def normalize_theme_mode(mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        return normalized if normalized in {"light", "dark", "system"} else "system"

    def resolve_effective_theme(self, mode: str) -> str:
        normalized = self.normalize_theme_mode(mode)
        if normalized == "system":
            # 中文：跟随系统保存的是“策略”而不是固定颜色，实际渲染时再解析系统当前偏好。
            # English: System mode stores a policy instead of a fixed color, so the current OS preference is resolved at render time.
            return get_system_theme_name(QApplication.instance())
        return normalized

    def set_theme_mode(self, mode: str):
        self.apply_theme_mode(mode, persist=True)
        labels = {"light": "浅色模式", "dark": "深色模式", "system": "跟随系统"}
        self.set_status(f"已切换为{labels.get(self.theme_mode, '跟随系统')}。")

    def toggle_theme(self):
        sequence = ["system", "light", "dark"]
        current = self.normalize_theme_mode(getattr(self, "theme_mode", "system"))
        self.set_theme_mode(sequence[(sequence.index(current) + 1) % len(sequence)])

    def apply_theme_mode(self, mode: str, persist: bool = True):
        self.theme_mode = self.normalize_theme_mode(mode)
        effective_theme = self.resolve_effective_theme(self.theme_mode)
        if persist:
            self.data_manager.save_theme_mode(self.theme_mode, effective_theme)
        self.apply_theme(effective_theme, persist=False)
        self.update_theme_actions()
        self.update_system_theme_timer()

    def update_system_theme_timer(self):
        if not hasattr(self, "system_theme_timer"):
            return
        if getattr(self, "theme_mode", "system") == "system":
            if not self.system_theme_timer.isActive():
                # 中文：Qt5 在部分平台不会主动通知系统主题变化，定时轻量检查能让“跟随系统”在运行中也保持有效。
                # English: Qt5 does not reliably notify system theme changes on every platform, so a lightweight timer keeps system mode effective while the app is running.
                self.system_theme_timer.start(6000)
        else:
            self.system_theme_timer.stop()

    def refresh_system_theme_if_needed(self):
        if getattr(self, "theme_mode", "system") != "system":
            return
        effective_theme = self.resolve_effective_theme("system")
        if effective_theme != getattr(self, "current_theme", ""):
            # 中文：只有实际主题发生变化时才重绘，避免定时检查反复刷新整个窗口造成闪烁。
            # English: Repaint only when the effective theme changes, preventing the timer from repeatedly refreshing the whole window and causing flicker.
            self.apply_theme_mode("system", persist=True)
            self.set_status("已跟随系统主题自动更新。")

    def apply_theme(self, theme: str, persist: bool = True):
        theme = "light" if theme == "light" else "dark"
        self.current_theme = theme
        if persist:
            self.theme_mode = theme
            self.data_manager.save_theme_mode(theme, theme)

        metrics = self.ui_metrics
        application = QApplication.instance()
        if application:
            # 中文：同时设置 QApplication 字体和 QSS 字体，确保原生控件、菜单和弹窗都按同一缩放基准渲染。
            # English: Setting both QApplication font and QSS font keeps native widgets, menus, and dialogs rendered from the same scaling baseline.
            application.setFont(QFont("Microsoft YaHei", metrics["base_font_size"]))

        base_font = metrics["base_font_size"]
        small_font = metrics["small_font_size"]
        title_font = metrics["title_font_size"]
        input_v = metrics["input_padding_v"]
        input_h = metrics["input_padding_h"]
        button_v = metrics.get("button_padding_v", metrics["control_padding_v"])
        button_h = metrics.get("button_padding_h", metrics["control_padding_h"])
        button_min_height = metrics.get("button_min_height", metrics["table_row_height"] - 8)
        tab_v = metrics["tab_padding_v"]
        tab_h = metrics["tab_padding_h"]
        header_h = metrics["table_header_height"]
        group_padding = metrics["group_padding"]
        group_top = metrics["group_margin_top"]
        status_font = metrics.get("status_font_size", small_font)
        scrollbar_size = metrics.get("scrollbar_size", 10)
        scrollbar_margin = metrics.get("scrollbar_margin", 2)
        scrollbar_radius = metrics.get("scrollbar_radius", 6)
        scrollbar_min = metrics.get("scrollbar_handle_min", 42)

        light_combo_qss = build_modern_combo_qss(
            "QComboBox",
            metrics,
            "#ffffff",
            "#172033",
            "#cbd5e1",
            "#ff6b35",
            "#ffffff",
            "#f1f5f9",
            "#ff6b35",
            "#ffffff",
            "#475569",
            "#f8fafc",
            arrow_image=combo_arrow_asset("light"),
        )
        dark_combo_qss = build_modern_combo_qss(
            "QComboBox",
            metrics,
            "#1a1a24",
            "#f0f0f5",
            "#2a2a3a",
            "#ff6b35",
            "#1a1a24",
            "#242436",
            "#ff6b35",
            "#ffffff",
            "#c7c7d6",
            "#20202e",
            arrow_image=combo_arrow_asset("dark"),
        )

        if theme == "light":
            qss = f"""
                QWidget {{ background: #f8fafc; color: #172033; font-family: 'Microsoft YaHei'; font-size: {base_font}px; }}
                QMainWindow, QMenuBar, QMenu {{ background: #ffffff; color: #172033; }}
                QMenuBar::item {{ padding: {max(3, button_v // 2)}px {button_h}px; }}
                QMenu::item {{ padding: {button_v}px {button_h * 2}px {button_v}px {button_h}px; }}
                #appTitle {{ color: #111827; font-size: {title_font}px; font-weight: 700; }}
                QLabel {{ font-size: {base_font}px; }}
                QLineEdit, QPlainTextEdit, QTextEdit, QTableWidget, QListWidget {{ background: #ffffff; color: #172033; border: 1px solid #cbd5e1; border-radius: 6px; padding: {input_v}px {input_h}px; }}
                QTableWidget {{ background-color: #ffffff; alternate-background-color: #f1f5f9; color: #172033; gridline-color: #d8e0ea; selection-background-color: #2563eb; selection-color: #ffffff; }}
                QTableWidget::item:selected {{ background-color: #2563eb; color: #ffffff; }}
                {light_combo_qss}
                QPlainTextEdit, QTextEdit {{ font-family: 'Consolas', 'Microsoft YaHei'; font-size: {metrics["mono_font_size"]}px; }}
                QPushButton {{ background: #ff6b35; color: white; border: none; border-radius: 6px; padding: {button_v}px {button_h}px; min-height: 0px; }}
                QPushButton:hover {{ background: #ff8555; }}
                QTabWidget::pane, QGroupBox {{ border: 1px solid #cbd5e1; border-radius: 8px; }}
                QGroupBox {{ margin-top: {group_top}px; padding: {group_padding}px; }}
                QGroupBox::title {{ subcontrol-origin: margin; left: {group_padding}px; padding: 0 {max(5, group_padding // 2)}px; }}
                QTabBar::tab {{ background: #edf2f7; color: #172033; padding: {tab_v}px {tab_h}px; border: 1px solid #cbd5e1; border-bottom: none; border-top-left-radius: 7px; border-top-right-radius: 7px; }}
                QTabBar::tab:selected {{ background: #ffffff; color: #111827; }}
                QHeaderView::section {{ background: #e2e8f0; color: #172033; padding: {input_v}px {input_h}px; min-height: {header_h}px; border: none; }}
                QScrollBar:vertical {{ background: transparent; width: {scrollbar_size}px; margin: {scrollbar_margin}px; border: none; }}
                QScrollBar::handle:vertical {{ background: #94a3b8; border-radius: {scrollbar_radius}px; min-height: {scrollbar_min}px; }}
                QScrollBar::handle:vertical:hover {{ background: #64748b; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; width: 0px; border: none; background: transparent; }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
                QScrollBar:horizontal {{ background: transparent; height: {scrollbar_size}px; margin: {scrollbar_margin}px; border: none; }}
                QScrollBar::handle:horizontal {{ background: #94a3b8; border-radius: {scrollbar_radius}px; min-width: {scrollbar_min}px; }}
                QScrollBar::handle:horizontal:hover {{ background: #64748b; }}
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0px; width: 0px; border: none; background: transparent; }}
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
                QFrame#historyCard {{ background: #ffffff; border: 1px solid #d8e0ea; border-radius: 8px; }}
                QLabel#historyKeyword {{ background: transparent; border: none; color: #172033; font-weight: 700; }}
                QLabel#historyMeta {{ background: transparent; border: none; color: #64748b; font-size: {small_font}px; }}
                QPushButton#historySearchButton {{ background: #edf2f7; color: #172033; border: 1px solid #cbd5e1; border-radius: 6px; padding: {metrics.get("compact_button_padding_v", max(3, button_v // 2))}px {metrics.get("compact_button_padding_h", max(8, button_h // 2))}px; min-height: 0px; }}
            """
        else:
            qss = f"""
                QWidget {{ background: #0a0a0f; color: #f0f0f5; font-family: 'Microsoft YaHei'; font-size: {base_font}px; }}
                QMainWindow, QMenuBar, QMenu {{ background: #12121a; color: #f0f0f5; }}
                QMenuBar::item {{ padding: {max(3, button_v // 2)}px {button_h}px; }}
                QMenu::item {{ padding: {button_v}px {button_h * 2}px {button_v}px {button_h}px; }}
                #appTitle {{ color: #ffffff; font-size: {title_font}px; font-weight: 700; }}
                QLabel {{ font-size: {base_font}px; }}
                QLineEdit, QPlainTextEdit, QTextEdit, QTableWidget, QListWidget {{ background: #1a1a24; color: #f0f0f5; border: 1px solid #2a2a3a; border-radius: 6px; padding: {input_v}px {input_h}px; }}
                QTableWidget {{ background-color: #1a1a24; alternate-background-color: #151520; color: #f0f0f5; gridline-color: #2a2a3a; selection-background-color: #0284c7; selection-color: #ffffff; }}
                QTableWidget::item:selected {{ background-color: #0284c7; color: #ffffff; }}
                {dark_combo_qss}
                QPlainTextEdit, QTextEdit {{ font-family: 'Consolas', 'Microsoft YaHei'; font-size: {metrics["mono_font_size"]}px; }}
                QPushButton {{ background: #ff6b35; color: white; border: none; border-radius: 6px; padding: {button_v}px {button_h}px; min-height: 0px; }}
                QPushButton:hover {{ background: #ff8555; }}
                QTabWidget::pane, QGroupBox {{ border: 1px solid #2a2a3a; border-radius: 8px; }}
                QGroupBox {{ margin-top: {group_top}px; padding: {group_padding}px; }}
                QGroupBox::title {{ subcontrol-origin: margin; left: {group_padding}px; padding: 0 {max(5, group_padding // 2)}px; }}
                QTabBar::tab {{ background: #151520; color: #f0f0f5; padding: {tab_v}px {tab_h}px; border: 1px solid #2a2a3a; border-bottom: none; border-top-left-radius: 7px; border-top-right-radius: 7px; }}
                QTabBar::tab:selected {{ background: #1a1a24; color: #ffffff; }}
                QHeaderView::section {{ background: #2a2a3a; color: #f0f0f5; padding: {input_v}px {input_h}px; min-height: {header_h}px; border: none; }}
                QScrollBar:vertical {{ background: transparent; width: {scrollbar_size}px; margin: {scrollbar_margin}px; border: none; }}
                QScrollBar::handle:vertical {{ background: #4f5367; border-radius: {scrollbar_radius}px; min-height: {scrollbar_min}px; }}
                QScrollBar::handle:vertical:hover {{ background: #727891; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; width: 0px; border: none; background: transparent; }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
                QScrollBar:horizontal {{ background: transparent; height: {scrollbar_size}px; margin: {scrollbar_margin}px; border: none; }}
                QScrollBar::handle:horizontal {{ background: #4f5367; border-radius: {scrollbar_radius}px; min-width: {scrollbar_min}px; }}
                QScrollBar::handle:horizontal:hover {{ background: #727891; }}
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0px; width: 0px; border: none; background: transparent; }}
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
                QFrame#historyCard {{ background: #181824; border: 1px solid #2d2d3d; border-radius: 8px; }}
                QLabel#historyKeyword {{ background: transparent; border: none; color: #f0f0f5; font-weight: 700; }}
                QLabel#historyMeta {{ background: transparent; border: none; color: #a8a8b8; font-size: {small_font}px; }}
                QPushButton#historySearchButton {{ background: #20202e; color: #f0f0f5; border: 1px solid #2d2d3d; border-radius: 6px; padding: {metrics.get("compact_button_padding_v", max(3, button_v // 2))}px {metrics.get("compact_button_padding_h", max(8, button_h // 2))}px; min-height: 0px; }}
            """
        if application:
            application.setStyleSheet(qss)
        self.apply_widget_metrics()

