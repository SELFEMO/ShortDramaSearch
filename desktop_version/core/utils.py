import platform
import sys
import os


def get_platform_info():
    """获取平台信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version()
    }


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def is_linux():
    return platform.system() == "Linux"


def resource_path(relative_path):
    """获取资源的绝对路径，用于PyInstaller打包后定位资源文件"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    # 如果资源文件不存在，尝试在开发目录中查找
    if not os.path.exists(path):
        # 在项目根目录中查找
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(base_path, relative_path)

    return path