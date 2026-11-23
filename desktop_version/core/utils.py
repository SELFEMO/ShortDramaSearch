# -*- coding: utf-8 -*-

import math
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.kuleu_core import sanitize_url  # noqa: E402


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


def get_ui_font_family() -> str:
    system = platform.system()
    if system == "Darwin":
        return "PingFang SC"
    if system == "Linux":
        return "Noto Sans CJK SC"
    return "Microsoft YaHei"


def safe_open_url(raw_url: Any) -> Tuple[bool, str]:
    """校验 URL 协议白名单后再调用系统默认处理器打开。"""
    safe = sanitize_url(raw_url)
    if not safe:
        return False, "不支持或无效的链接协议，仅允许 http/https/magnet/ed2k。"
    try:
        from PyQt5.QtCore import QUrl
        from PyQt5.QtGui import QDesktopServices

        ok = QDesktopServices.openUrl(QUrl(safe))
        if not ok:
            return False, "无法调用系统程序打开该链接。"
        return True, safe
    except Exception as exc:
        return False, f"打开链接失败: {exc}"


def get_system_theme_name(application=None) -> str:
    """返回系统当前偏好的浅色/深色主题名称。"""
    system = platform.system()

    if system == "Windows":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
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
            return "dark" if color.lightness() < 128 else "light"
        except Exception:
            pass

    return "light"


def resource_path(relative_path: str) -> str:
    """获取资源的绝对路径，用于 PyInstaller 打包后定位资源文件。"""
    base_path = getattr(sys, "_MEIPASS", None)
    if not base_path:
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
    except (TypeError, ValueError, OSError):
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


def build_ui_metrics(application=None, screen=None) -> Dict[str, Any]:
    """根据当前屏幕逻辑尺寸生成 UI 尺寸（避免与 Qt AA_EnableHighDpiScaling 双重缩放）。"""
    target_screen = screen or (application.primaryScreen() if application else None)
    width = 1920
    height = 1080
    available_width = 1280
    available_height = 820
    dpi = 96.0
    device_ratio = 1.0

    if target_screen is not None:
        geometry = target_screen.geometry()
        available = target_screen.availableGeometry()
        width = max(geometry.width(), available.width(), 1)
        height = max(geometry.height(), available.height(), 1)
        available_width = max(available.width(), 1)
        available_height = max(available.height(), 1)
        dpi = max(float(target_screen.logicalDotsPerInch() or 96.0), 72.0)
        device_ratio = max(float(target_screen.devicePixelRatio() or 1.0), 1.0)

    # AA_EnableHighDpiScaling 已在逻辑像素层面处理了系统缩放，此处仅做温和的视口自适应缩放
    resolution_scale = clamp(math.sqrt((width * height) / float(1920 * 1080)), 0.92, 1.25)
    scale = resolution_scale

    window_width = min(scaled_int(1280, scale, 980), int(available_width * 0.94))
    window_height = min(scaled_int(820, scale, 640), int(available_height * 0.90))
    minimum_width = min(scaled_int(900, scale, 820), int(available_width * 0.88))
    minimum_height = min(scaled_int(560, scale, 520), int(available_height * 0.82))

    return {
        "scale": scale,
        "dpi": dpi,
        "device_ratio": device_ratio,
        "font_family": get_ui_font_family(),
        "screen_width": width,
        "screen_height": height,
        "available_width": available_width,
        "available_height": available_height,
        "base_font_size": scaled_int(13, scale, 12, 18),
        "small_font_size": scaled_int(12, scale, 11, 16),
        "title_font_size": scaled_int(20, scale, 17, 26),
        "dialog_title_font_size": scaled_int(17, scale, 15, 22),
        "mono_font_size": scaled_int(12, scale, 11, 16),
        "status_font_size": scaled_int(12, scale, 11, 16),
        "control_padding_v": scaled_int(7, scale, 5, 12),
        "control_padding_h": scaled_int(12, scale, 9, 18),
        "button_padding_v": scaled_int(4, scale, 3, 8),
        "button_padding_h": scaled_int(10, scale, 8, 16),
        "button_min_height": scaled_int(26, scale, 24, 34),
        "compact_button_padding_v": scaled_int(3, scale, 2, 6),
        "compact_button_padding_h": scaled_int(8, scale, 6, 12),
        "combo_arrow_area_width": scaled_int(24, scale, 20, 30),
        "combo_arrow_size": scaled_int(10, scale, 8, 14),
        "combo_popup_max_visible": 8,
        "combo_popup_radius": scaled_int(8, scale, 6, 12),
        "combo_popup_padding": scaled_int(4, scale, 3, 8),
        "combo_popup_item_height": scaled_int(26, scale, 24, 32),
        "input_padding_v": scaled_int(6, scale, 5, 11),
        "input_padding_h": scaled_int(8, scale, 6, 14),
        "tab_padding_v": scaled_int(9, scale, 7, 14),
        "tab_padding_h": scaled_int(16, scale, 12, 24),
        "page_margin": scaled_int(14, scale, 10, 22),
        "layout_spacing": scaled_int(10, scale, 7, 16),
        "group_margin_top": scaled_int(18, scale, 14, 24),
        "group_padding": scaled_int(10, scale, 8, 16),
        "table_row_height": scaled_int(34, scale, 28, 48),
        "table_header_height": scaled_int(34, scale, 28, 48),
        "history_width": scaled_int(280, scale, 220, 380),
        "history_min_width": scaled_int(230, scale, 190, 320),
        "history_card_padding": scaled_int(9, scale, 7, 14),
        "history_card_gap": scaled_int(8, scale, 6, 12),
        "rating_width": scaled_int(94, scale, 80, 128),
        "card_padding": scaled_int(12, scale, 9, 18),
        "card_spacing": scaled_int(8, scale, 6, 12),
        "card_gap": scaled_int(10, scale, 7, 16),
        "card_radius": scaled_int(10, scale, 8, 16),
        "card_title_font_size": scaled_int(14, scale, 13, 20),
        "card_title_limit": scaled_int(110, scale, 86, 145),
        "card_link_limit": scaled_int(115, scale, 86, 160),
        "rank_badge_width": scaled_int(46, scale, 38, 64),
        "rank_button_width": scaled_int(88, scale, 76, 120),
        "rank_keyword_limit": scaled_int(130, scale, 96, 180),
        "rank_desc_limit": scaled_int(150, scale, 110, 200),
        "scrollbar_size": scaled_int(9, scale, 7, 12),
        "scrollbar_margin": scaled_int(2, scale, 1, 4),
        "scrollbar_radius": scaled_int(5, scale, 4, 8),
        "scrollbar_handle_min": scaled_int(42, scale, 30, 64),
        "window_width": max(760, window_width),
        "window_height": max(520, window_height),
        "minimum_width": max(720, minimum_width),
        "minimum_height": max(480, minimum_height),
        "detail_dialog_width": min(scaled_int(680, scale, 560), int(available_width * 0.82)),
        "detail_dialog_height": min(scaled_int(420, scale, 360), int(available_height * 0.78)),
        "policy_dialog_width": min(scaled_int(620, scale, 520), int(available_width * 0.70)),
        "policy_dialog_content_height": min(scaled_int(240, scale, 190), int(available_height * 0.36)),
        "policy_dialog_height": min(scaled_int(390, scale, 320), int(available_height * 0.62)),
        "qr_dialog_width": min(scaled_int(360, scale, 320), int(available_width * 0.58)),
        "qr_dialog_height": min(scaled_int(420, scale, 360), int(available_height * 0.70)),
        "qr_image_size": scaled_int(280, scale, 230, 380),
    }
