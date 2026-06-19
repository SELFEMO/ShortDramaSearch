from typing import Dict, List


JHSJ_API = "https://api.kuleu.com/api/jhsj"
YINGSHI_API = "https://api.kuleu.com/api/yingshi"
SHORTDRAMA_RANK_API = "https://api.kuleu.com/api/shortdramarank"
VTQUARK_API = "https://api.kuleu.com/api/vtquark"
ICO_API = "https://api.kuleu.com/api/ico"
QRCODE_API = "https://api.kuleu.com/api/qrcode"
GITHUB_URL = "https://github.com/SELFEMO/ShortDramaSearch"
GITHUB_PAGES_URL = "https://selfemo.github.io/ShortDramaSearch/"

SEARCH_TIMEOUT = 15
RANK_TIMEOUT = 10
MAX_SEARCH_TOTAL = 200
MAX_HISTORY = 30

TYPE_LABELS: Dict[str, str] = {
    "baidu": "百度网盘",
    "aliyun": "阿里云盘",
    "quark": "夸克网盘",
    "tianyi": "天翼云盘",
    "uc": "UC网盘",
    "mobile": "移动云盘",
    "115": "115网盘",
    "pikpak": "PikPak",
    "xunlei": "迅雷网盘",
    "123": "123网盘",
    "magnet": "磁力链接",
    "ed2k": "电驴链接",
}

TYPE_PRESETS: Dict[str, List[str]] = {
    "all": ["baidu", "aliyun", "quark", "tianyi", "uc", "mobile", "115", "pikpak", "xunlei", "123", "magnet", "ed2k"],
    "netdisk": ["baidu", "aliyun", "quark", "tianyi", "uc", "mobile", "115", "pikpak", "xunlei", "123"],
    "baidu": ["baidu"],
    "quark": ["quark"],
    "aliyun": ["aliyun"],
    "tianyi": ["tianyi"],
    "uc": ["uc"],
    "mobile": ["mobile"],
    "115": ["115"],
    "pikpak": ["pikpak"],
    "xunlei": ["xunlei"],
    "123": ["123"],
    "magnet": ["magnet"],
    "ed2k": ["ed2k"],
}

PRESET_LABELS: Dict[str, str] = {
    "all": "全局聚合",
    "netdisk": "网盘聚合",
    **TYPE_LABELS,
}

SOURCE_ORDER = ["baidu", "quark", "aliyun", "tianyi", "uc", "mobile", "115", "pikpak", "xunlei", "123", "magnet", "ed2k"]

PAGE_LINKS = [
    {"id": "search", "path": "pages/search.py", "icon": "🔎", "title": "聚合搜索", "desc": "多源资源检索"},
    {"id": "api", "path": "pages/api.py", "icon": "🧩", "title": "API 生成器", "desc": "生成 JSON 查询链接"},
    {"id": "daily", "path": "pages/daily.py", "icon": "📅", "title": "每日影视", "desc": "百度与夸克每日资源"},
    {"id": "rank", "path": "pages/rank.py", "icon": "🔥", "title": "热度榜", "desc": "短剧与夸克热搜"},
    {"id": "favorites", "path": "pages/favorites.py", "icon": "⭐", "title": "我的收藏", "desc": "会话内收藏管理"},
    {"id": "policy", "path": "pages/policy.py", "icon": "📜", "title": "用户条例", "desc": "使用边界与免责说明"},
]
