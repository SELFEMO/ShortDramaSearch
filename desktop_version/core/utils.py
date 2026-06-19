# -*- coding: utf-8 -*-

import math
import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional


def get_platform_info():
    """获取平台信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def is_linux():
    return platform.system() == "Linux"



def get_system_theme_name(application=None) -> str:
    """返回系统当前偏好的浅色/深色主题名称。"""
    system = platform.system()

    if system == "Windows":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                # 中文：Windows 把 0 表示为深色应用主题、1 表示为浅色应用主题，直接读取注册表比依赖 Qt5 调色板更稳定。
                # English: Windows stores 0 as the dark app theme and 1 as the light app theme, so reading the registry is more reliable than depending on the Qt5 palette.
                return "light" if int(value) else "dark"
        except Exception:
            pass

    if system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=1,
            )
            # 中文：macOS 只在深色模式下返回 AppleInterfaceStyle=Dark，未设置时默认就是浅色。
            # English: macOS returns AppleInterfaceStyle=Dark only in dark mode, so an absent value means the default light mode.
            return "dark" if "dark" in (result.stdout or "").strip().lower() else "light"
        except Exception:
            pass

    gtk_theme = f"{os.environ.get('GTK_THEME', '')} {os.environ.get('QT_QPA_PLATFORMTHEME', '')}".lower()
    if "dark" in gtk_theme:
        return "dark"

    if application is not None:
        try:
            from PyQt5.QtGui import QPalette

            color = application.palette().color(QPalette.Window)
            # 中文：无法读取操作系统主题时，用 Qt 当前窗口背景亮度兜底，保证“跟随系统”至少能匹配平台默认外观。
            # English: When the OS theme cannot be read directly, Qt's current window background lightness is used as a fallback so system mode still matches the platform default.
            return "dark" if color.lightness() < 128 else "light"
        except Exception:
            pass

    return "light"

def resource_path(relative_path):
    """获取资源的绝对路径，用于 PyInstaller 打包后定位资源文件"""
    try:
        # 中文：PyInstaller 会把资源释放到 _MEIPASS，优先使用它才能让打包版本和源码版本路径一致。
        # English: PyInstaller extracts resources to _MEIPASS, so using it first keeps packaged and source paths consistent.
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    path = os.path.join(base_path, relative_path)
    if os.path.exists(path):
        return path

    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(project_path, relative_path)


def format_timestamp(value: Any) -> str:
    try:
        timestamp = int(value)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def scaled_int(value: float, scale: float, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    result = int(round(value * scale))
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


def build_ui_metrics(application=None) -> Dict[str, Any]:
    """根据当前主屏幕分辨率和 DPI 生成 UI 尺寸。"""
    screen = application.primaryScreen() if application else None
    width = 1920
    height = 1080
    available_width = 1280
    available_height = 820
    dpi = 96.0
    device_ratio = 1.0

    if screen is not None:
        geometry = screen.geometry()
        available = screen.availableGeometry()
        width = max(geometry.width(), available.width(), 1)
        height = max(geometry.height(), available.height(), 1)
        available_width = max(available.width(), 1)
        available_height = max(available.height(), 1)
        dpi = max(float(screen.logicalDotsPerInch() or 96.0), 72.0)
        device_ratio = max(float(screen.devicePixelRatio() or 1.0), 1.0)

    # 中文：字体缩放不能只看分辨率，高 DPI 屏幕和系统缩放会改变可读性，所以把 DPI 和像素面积一起纳入计算。
    # English: Font scaling cannot depend on resolution alone; high-DPI screens and OS scaling affect readability, so both DPI and pixel area are included.
    dpi_scale = clamp(dpi / 96.0, 0.85, 1.70)
    resolution_scale = clamp(math.sqrt((width * height) / float(1920 * 1080)), 0.88, 1.60)
    scale = clamp((dpi_scale * 0.68) + (resolution_scale * 0.32), 0.90, 1.55)

    # 中文：窗口尺寸跟随可用工作区收缩，避免 1366x768 或带任务栏的屏幕打开后被系统边缘裁切。
    # English: The window size shrinks with the available work area so 1366x768 screens or taskbars do not clip the app at launch.
    window_width = min(scaled_int(1280, scale, 980), int(available_width * 0.94))
    window_height = min(scaled_int(820, scale, 640), int(available_height * 0.90))
    minimum_width = min(scaled_int(900, scale, 820), int(available_width * 0.88))
    minimum_height = min(scaled_int(560, scale, 520), int(available_height * 0.82))

    return {
        "scale": scale,
        "dpi": dpi,
        "device_ratio": device_ratio,
        "screen_width": width,
        "screen_height": height,
        "available_width": available_width,
        "available_height": available_height,
        "base_font_size": scaled_int(13, scale, 11, 20),
        "small_font_size": scaled_int(12, scale, 10, 18),
        "title_font_size": scaled_int(20, scale, 17, 30),
        "dialog_title_font_size": scaled_int(17, scale, 15, 26),
        "mono_font_size": scaled_int(12, scale, 10, 18),
        "status_font_size": scaled_int(12, scale, 10, 18),
        "control_padding_v": scaled_int(7, scale, 5, 14),
        "control_padding_h": scaled_int(12, scale, 9, 22),
        # 中文：按钮单独使用更紧凑的内边距，避免和输入框共享尺寸后在卡片与工具行里显得过大。
        # English: Buttons use their own tighter padding so they do not look oversized in cards and action rows by sharing input-sized metrics.
        "button_padding_v": scaled_int(3, scale, 2, 7),
        "button_padding_h": scaled_int(8, scale, 6, 14),
        "button_min_height": scaled_int(22, scale, 20, 32),
        "compact_button_padding_v": scaled_int(2, scale, 1, 5),
        "compact_button_padding_h": scaled_int(6, scale, 5, 11),
        # 中文：下拉箭头区域只保留清晰的轻量箭头，不再绘制独立按钮块，避免看起来像不可理解的原生小控件。
        # English: The combo arrow area keeps only a clear lightweight chevron instead of a separate button block, avoiding a confusing native-looking control.
        "combo_arrow_area_width": scaled_int(24, scale, 20, 32),
        "combo_arrow_size": scaled_int(10, scale, 8, 14),
        # 中文：下拉弹层固定为紧凑候选数量，避免网盘来源很多时弹层过长并贴到屏幕底部。
        # English: The popup keeps a compact visible item count so long source lists do not stretch down to the screen bottom.
        "combo_popup_max_visible": 8,
        "combo_popup_radius": scaled_int(8, scale, 6, 12),
        "combo_popup_padding": scaled_int(4, scale, 3, 8),
        "combo_popup_item_height": scaled_int(24, scale, 22, 32),
        "input_padding_v": scaled_int(6, scale, 5, 12),
        "input_padding_h": scaled_int(8, scale, 6, 16),
        "tab_padding_v": scaled_int(9, scale, 7, 16),
        "tab_padding_h": scaled_int(16, scale, 12, 28),
        "page_margin": scaled_int(14, scale, 10, 26),
        "layout_spacing": scaled_int(10, scale, 7, 18),
        "group_margin_top": scaled_int(18, scale, 14, 28),
        "group_padding": scaled_int(10, scale, 8, 18),
        "table_row_height": scaled_int(34, scale, 28, 54),
        "table_header_height": scaled_int(34, scale, 28, 54),
        # 中文：结果列表已由表格改成资源卡片，历史侧栏也改为卡片，因此需要比旧单行列表更宽的默认空间。
        # English: Result lists now use resource cards and the history sidebar also uses cards, so they need more default width than the old single-line list.
        "history_width": scaled_int(280, scale, 220, 420),
        "history_min_width": scaled_int(230, scale, 190, 340),
        "history_card_padding": scaled_int(9, scale, 7, 16),
        "history_card_gap": scaled_int(8, scale, 6, 14),
        "rating_width": scaled_int(94, scale, 78, 140),
        "card_padding": scaled_int(12, scale, 9, 20),
        "card_spacing": scaled_int(8, scale, 6, 14),
        "card_gap": scaled_int(10, scale, 7, 18),
        "card_radius": scaled_int(10, scale, 8, 18),
        "card_title_font_size": scaled_int(14, scale, 12, 22),
        "card_title_limit": scaled_int(110, scale, 86, 150),
        "card_link_limit": scaled_int(115, scale, 86, 170),
        # 中文：热度榜改成卡片后，排名徽章和按钮需要独立缩放，避免再次出现表格按钮被挤成竖排的问题。
        # English: After moving ranks to cards, the rank badge and button scale independently to avoid table-like squeezed vertical buttons again.
        "rank_badge_width": scaled_int(46, scale, 38, 70),
        "rank_button_width": scaled_int(88, scale, 76, 130),
        "rank_keyword_limit": scaled_int(130, scale, 96, 190),
        "rank_desc_limit": scaled_int(150, scale, 110, 220),
        # 中文：滚动条尺寸跟随缩放但保持纤细，避免回到系统原生粗滚动条造成视觉噪声。
        # English: Scrollbar sizes follow UI scaling while staying slim, avoiding the noisy look of thick native system scrollbars.
        "scrollbar_size": scaled_int(9, scale, 7, 14),
        "scrollbar_margin": scaled_int(2, scale, 1, 4),
        "scrollbar_radius": scaled_int(5, scale, 4, 8),
        "scrollbar_handle_min": scaled_int(42, scale, 30, 70),
        "window_width": max(760, window_width),
        "window_height": max(520, window_height),
        "minimum_width": max(720, minimum_width),
        "minimum_height": max(480, minimum_height),
        "detail_dialog_width": min(scaled_int(680, scale, 560), int(available_width * 0.82)),
        "detail_dialog_height": min(scaled_int(420, scale, 360), int(available_height * 0.78)),
        # 中文：用户条例正文很短，弹窗应按内容紧凑展示，避免按普通详情弹窗高度预留大量空白。
        # English: The policy text is short, so the dialog should size to its content instead of reserving detail-dialog-like empty space.
        "policy_dialog_width": min(scaled_int(620, scale, 520), int(available_width * 0.70)),
        "policy_dialog_content_height": min(scaled_int(210, scale, 175), int(available_height * 0.32)),
        "policy_dialog_height": min(scaled_int(360, scale, 300), int(available_height * 0.58)),
        "qr_dialog_width": min(scaled_int(360, scale, 320), int(available_width * 0.58)),
        "qr_dialog_height": min(scaled_int(420, scale, 360), int(available_height * 0.70)),
        "qr_image_size": scaled_int(280, scale, 230, 420),
    }
