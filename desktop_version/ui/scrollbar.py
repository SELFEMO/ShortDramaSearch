# -*- coding: utf-8 -*-

from PyQt5.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QTimer, Qt
from PyQt5.QtWidgets import QAbstractScrollArea, QGraphicsOpacityEffect, QScrollBar


class AutoHideScrollBar(QScrollBar):
    """视觉自动隐藏滚动条。"""

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        self.setObjectName("autoHideScrollBar")
        self.setMouseTracking(True)
        self._hide_delay = 1100
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)
        self._animation = QPropertyAnimation(self._effect, b"opacity", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)
        self.valueChanged.connect(lambda _value: self.show_temporarily())
        self.rangeChanged.connect(lambda _minimum, _maximum: self.update_auto_visibility())
        self.sliderPressed.connect(lambda: self.show_now(persistent=True))
        self.sliderReleased.connect(self.schedule_hide)
        QTimer.singleShot(300, self.update_auto_visibility)

    def has_scrollable_range(self) -> bool:
        return self.maximum() > self.minimum()

    def update_auto_visibility(self):
        # 中文：滚动条没有可滚动范围时直接隐藏，避免空白轨道占用界面注意力。
        # English: The scrollbar is hidden when there is no scrollable range, preventing an empty track from drawing attention.
        if not self.has_scrollable_range():
            self._hide_timer.stop()
            self._animation.stop()
            self._effect.setOpacity(0.0)
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
        self._animation.stop()
        self._animation.setStartValue(self._effect.opacity())
        self._animation.setEndValue(1.0)
        self._animation.start()
        if not persistent:
            self.schedule_hide()

    def show_temporarily(self):
        # 中文：滚动时短暂显示滚动条，用户停下后自动淡出，比一直显示原生滚动条更轻量。
        # English: The scrollbar appears briefly while scrolling and fades out after interaction, which is lighter than keeping native scrollbars permanently visible.
        self.show_now(persistent=False)

    def schedule_hide(self):
        if self.underMouse() or self.isSliderDown():
            return
        self._hide_timer.start(self._hide_delay)

    def fade_out(self):
        if self.underMouse() or self.isSliderDown() or not self.has_scrollable_range():
            return
        self._animation.stop()
        self._animation.setStartValue(self._effect.opacity())
        self._animation.setEndValue(0.0)
        self._animation.start()

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
        self.show_temporarily()



def install_auto_hide_scrollbars(widget, horizontal: bool = True):
    """为可滚动控件安装统一的自动隐藏滚动条。"""
    if not isinstance(widget, QAbstractScrollArea):
        return

    # 中文：只替换滚动条对象，不改变业务控件本身，便于列表、表格和文本框共享同一套滚动体验。
    # English: Only the scrollbar objects are replaced while business widgets stay unchanged, allowing lists, tables, and text editors to share one scrolling experience.
    if not isinstance(widget.verticalScrollBar(), AutoHideScrollBar):
        widget.setVerticalScrollBar(AutoHideScrollBar(Qt.Vertical, widget))
    widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    if horizontal:
        if not isinstance(widget.horizontalScrollBar(), AutoHideScrollBar):
            widget.setHorizontalScrollBar(AutoHideScrollBar(Qt.Horizontal, widget))
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    else:
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
