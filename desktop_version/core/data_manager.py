# -*- coding: utf-8 -*-

import json
import os
import time
from typing import Any, Dict, List


class DataManager:
    """桌面版本地数据管理器。"""

    def __init__(self):
        self.app_data_dir = os.path.join(os.path.expanduser("~"), ".short_drama_search")
        os.makedirs(self.app_data_dir, exist_ok=True)

        self.history_file = os.path.join(self.app_data_dir, "history.json")
        self.favorites_file = os.path.join(self.app_data_dir, "favorites.json")
        self.broken_file = os.path.join(self.app_data_dir, "broken_links.json")
        self.quality_file = os.path.join(self.app_data_dir, "quality_ratings.json")
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.cache_file = os.path.join(self.app_data_dir, "cache.json")

    def _read_json(self, path: str, default: Any) -> Any:
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return default

    def _write_json(self, path: str, data: Any) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    @staticmethod
    def make_resource_id(link: str) -> str:
        return (link or "").strip()

    def load_search_history(self) -> List[Dict[str, Any]]:
        data = self._read_json(self.history_file, [])
        return data if isinstance(data, list) else []

    def save_search_history(self, keyword: str, total: int = 0) -> None:
        term = (keyword or "").strip()
        if not term:
            return

        history = [item for item in self.load_search_history() if item.get("keyword") != term]
        # 中文：和网页端一样保留最近搜索，桌面端额外记录结果数，方便用户判断历史关键词是否值得重搜。
        # English: Like the web page, recent searches are kept; the desktop client also stores result counts to help users decide what to rerun.
        history.insert(0, {"keyword": term, "count": int(total or 0), "timestamp": int(time.time())})
        self._write_json(self.history_file, history[:50])

    def clear_search_history(self) -> None:
        self._write_json(self.history_file, [])

    def import_search_history(self, records: List[Dict[str, Any]]) -> None:
        cleaned: List[Dict[str, Any]] = []
        seen = set()
        for item in records or []:
            keyword = str(item.get("keyword") or "").strip()
            if not keyword or keyword in seen:
                continue
            seen.add(keyword)
            cleaned.append(
                {
                    "keyword": keyword,
                    "count": int(item.get("count") or 0),
                    "timestamp": int(item.get("timestamp") or time.time()),
                }
            )
        self._write_json(self.history_file, cleaned[:50])

    def get_favorites(self) -> List[Dict[str, Any]]:
        data = self._read_json(self.favorites_file, [])
        return data if isinstance(data, list) else []

    def save_favorites(self, favorites: List[Dict[str, Any]]) -> None:
        self._write_json(self.favorites_file, favorites or [])

    def is_favorited(self, link: str) -> bool:
        resource_id = self.make_resource_id(link)
        return any(self.make_resource_id(item.get("url", "")) == resource_id for item in self.get_favorites())

    def toggle_favorite(self, resource: Dict[str, Any]) -> bool:
        link = self.make_resource_id(resource.get("url", ""))
        if not link:
            return False

        favorites = [item for item in self.get_favorites() if self.make_resource_id(item.get("url", "")) != link]
        is_now_favorite = len(favorites) == len(self.get_favorites())
        if is_now_favorite:
            # 中文：收藏只保存必要字段，避免接口返回的大量图片或临时字段让本地文件膨胀。
            # English: Favorites keep only essential fields so temporary API metadata or image lists do not bloat local storage.
            favorites.insert(
                0,
                {
                    "name": resource.get("name", "未知资源"),
                    "url": link,
                    "pwd": resource.get("pwd", ""),
                    "type": resource.get("type", ""),
                    "source": resource.get("source", resource.get("_source", "")),
                    "timestamp": int(time.time()),
                },
            )
        self.save_favorites(favorites)
        return is_now_favorite

    def clear_favorites(self) -> None:
        self._write_json(self.favorites_file, [])

    def import_favorites(self, records: List[Dict[str, Any]]) -> None:
        cleaned: List[Dict[str, Any]] = []
        seen = set()
        for item in records or []:
            url = self.make_resource_id(item.get("url", ""))
            if not url or url in seen:
                continue
            seen.add(url)
            cleaned.append(
                {
                    "name": item.get("name", "未知资源"),
                    "url": url,
                    "pwd": item.get("pwd", ""),
                    "type": item.get("type", ""),
                    "source": item.get("source", ""),
                    "timestamp": int(item.get("timestamp") or time.time()),
                }
            )
        self.save_favorites(cleaned)

    def get_broken_links(self) -> List[str]:
        data = self._read_json(self.broken_file, [])
        return data if isinstance(data, list) else []

    def is_broken_marked(self, link: str) -> bool:
        return self.make_resource_id(link) in set(self.get_broken_links())

    def toggle_broken_link(self, resource: Dict[str, Any]) -> bool:
        link = self.make_resource_id(resource.get("url", ""))
        if not link:
            return False
        links = [item for item in self.get_broken_links() if item != link]
        is_now_broken = len(links) == len(self.get_broken_links())
        if is_now_broken:
            # 中文：失效标记只在本地生效，避免误以为桌面端会向第三方接口提交反馈。
            # English: Broken-link marks are local only, preventing users from assuming the desktop app submits feedback upstream.
            links.insert(0, link)
        self._write_json(self.broken_file, links)
        return is_now_broken

    def get_quality_map(self) -> Dict[str, int]:
        data = self._read_json(self.quality_file, {})
        if not isinstance(data, dict):
            return {}
        return {str(key): int(value) for key, value in data.items() if str(value).isdigit() or isinstance(value, int)}

    def get_quality(self, link: str) -> int:
        return int(self.get_quality_map().get(self.make_resource_id(link), 0) or 0)

    def set_quality(self, link: str, score: int) -> None:
        resource_id = self.make_resource_id(link)
        if not resource_id:
            return
        data = self.get_quality_map()
        safe_score = max(0, min(5, int(score or 0)))
        if safe_score <= 0:
            data.pop(resource_id, None)
        else:
            data[resource_id] = safe_score
        self._write_json(self.quality_file, data)

    def load_settings(self) -> Dict[str, Any]:
        data = self._read_json(self.settings_file, {})
        return data if isinstance(data, dict) else {}

    def load_theme_mode(self) -> str:
        data = self.load_settings()
        mode = str(data.get("theme_mode", "")).strip().lower()
        if mode in {"light", "dark", "system"}:
            return mode

        # 中文：旧版本启动时会自动写入 theme=dark，它不一定代表用户主动选择；因此没有 theme_mode 时统一默认跟随系统。
        # English: Older versions wrote theme=dark during startup, which may not mean the user chose it; therefore missing theme_mode now defaults to system mode.
        return "system"

    def save_theme_mode(self, mode: str, effective_theme: str) -> None:
        normalized_mode = mode if mode in {"light", "dark", "system"} else "system"
        normalized_theme = "light" if effective_theme == "light" else "dark"
        data = self.load_settings()
        # 中文：同时保存 theme_mode 和实际 theme，是为了让新版本支持跟随系统，同时保留旧字段给可能存在的旧脚本读取。
        # English: Both theme_mode and the effective theme are saved so the new version supports system mode while the legacy field remains available for older scripts.
        data["theme_mode"] = normalized_mode
        data["theme"] = normalized_theme
        self._write_json(self.settings_file, data)

    def save_setting(self, key: str, value: Any) -> None:
        data = self.load_settings()
        data[key] = value
        self._write_json(self.settings_file, data)

    def cache_results(self, key: str, results: List[Dict[str, Any]]) -> None:
        cache = self._read_json(self.cache_file, {})
        if not isinstance(cache, dict):
            cache = {}
        cache[key] = {"timestamp": int(time.time()), "data": results}
        self._write_json(self.cache_file, cache)

    def get_cached_results(self, key: str) -> List[Dict[str, Any]]:
        cache = self._read_json(self.cache_file, {})
        if not isinstance(cache, dict):
            return []
        entry = cache.get(key, {})
        if isinstance(entry, dict):
            return entry.get("data", []) if isinstance(entry.get("data"), list) else []
        return []
