# -*- coding: utf-8 -*-

from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtWidgets import QAbstractScrollArea, QScrollBar


class AutoHideScrollBar(QScrollBar):
    """轻量自动隐藏滚动条（移除 QGraphicsOpacityEffect 避免 Qt5 HiDPI 重绘闪烁）。"""

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        self.setObjectName("autoHideScrollBar")
        self.setMouseTracking(True)
        self._hide_delay = 1400
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

        self._init_timer = QTimer(self)
        self._init_timer.setSingleShot(True)
        self._init_timer.timeout.connect(self.update_auto_visibility)

        self.valueChanged.connect(lambda _value: self.show_temporarily())
        self.rangeChanged.connect(lambda _minimum, _maximum: self.update_auto_visibility())
        self.sliderPressed.connect(lambda: self.show_now(persistent=True))
        self.sliderReleased.connect(self.schedule_hide)
        self._init_timer.start(200)

    def has_scrollable_range(self) -> bool:
        return self.maximum() > self.minimum()

    def update_auto_visibility(self):
        if not self.has_scrollable_range():
            self._hide_timer.stop()
            self.setVisible(False)
            return
        self.setVisible(True)
        self.show_temporarily()

    def show_now(self, persistent: bool = False):
        if not self.has_scrollable_range():
            self.setVisible(False)
            return
        self.setVisible(True)
        self._hide_timer.stop()
        if not persistent:
            self.schedule_hide()

    def show_temporarily(self):
        self.show_now(persistent=False)

    def schedule_hide(self):
        if self.underMouse() or self.isSliderDown():
            return
        self._hide_timer.start(self._hide_delay)

    def fade_out(self):
        if self.underMouse() or self.isSliderDown() or not self.has_scrollable_range():
            return
        # 仅在静态且鼠标不在滚动条区域时隐藏，保持可用性
        self.setVisible(False)

    def enterEvent(self, event: QEvent):
        self.show_now(persistent=True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.schedule_hide()
        super().leaveEvent(event)

    def wheelEvent(self, event: QEvent):
        self.show_temporarily()
        super().wheelEvent(event)

    def showEvent(self, event: QEvent):
        super().showEvent(event)
        if self.has_scrollable_range():
            self.schedule_hide()


def install_auto_hide_scrollbars(widget, horizontal: bool = True):
    """为可滚动控件安装统一的自动隐藏滚动条。"""
    if not isinstance(widget, QAbstractScrollArea):
        return

    if not isinstance(widget.verticalScrollBar(), AutoHideScrollBar):
        widget.setVerticalScrollBar(AutoHideScrollBar(Qt.Vertical, widget))
    widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    if horizontal:
        if not isinstance(widget.horizontalScrollBar(), AutoHideScrollBar):
            widget.setHorizontalScrollBar(AutoHideScrollBar(Qt.Horizontal, widget))
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    else:
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
