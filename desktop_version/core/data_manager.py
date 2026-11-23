# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.kuleu_core import sanitize_url  # noqa: E402

logger = logging.getLogger("shortdramasearch.desktop.data")


class DataManager:
    """桌面版本地数据管理器（原子写入 + 内存索引缓存 + 线程安全）。"""

    CACHE_TTL_SECONDS = 24 * 3600
    CACHE_MAX_ENTRIES = 50

    def __init__(self):
        self._lock = threading.RLock()
        self.app_data_dir = os.path.join(os.path.expanduser("~"), ".short_drama_search")
        os.makedirs(self.app_data_dir, exist_ok=True)

        self.history_file = os.path.join(self.app_data_dir, "history.json")
        self.favorites_file = os.path.join(self.app_data_dir, "favorites.json")
        self.broken_file = os.path.join(self.app_data_dir, "broken_links.json")
        self.quality_file = os.path.join(self.app_data_dir, "quality_ratings.json")
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.cache_file = os.path.join(self.app_data_dir, "cache.json")

        # 内存缓存，避免渲染数百张卡片时重复读盘
        self._favorites_cache: Optional[List[Dict[str, Any]]] = None
        self._favorites_id_set: Optional[Set[str]] = None
        self._broken_cache: Optional[List[str]] = None
        self._broken_set: Optional[Set[str]] = None
        self._quality_cache: Optional[Dict[str, int]] = None

    def _read_json(self, path: str, default: Any) -> Any:
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            logger.warning("Corrupt JSON detected at %s: %s", path, exc)
            backup_path = f"{path}.corrupt.{int(time.time())}.json"
            try:
                os.replace(path, backup_path)
            except OSError as backup_err:
                logger.error("Failed to backup corrupt JSON %s: %s", path, backup_err)
            return default
        except OSError as exc:
            logger.warning("Failed to read %s: %s", path, exc)
            return default

    def _write_json(self, path: str, data: Any) -> None:
        parent_dir = os.path.dirname(path)
        os.makedirs(parent_dir, exist_ok=True)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=parent_dir,
                prefix=".tmp_",
                suffix=".json",
                delete=False,
            ) as tmp_file:
                tmp_path = tmp_file.name
                json.dump(data, tmp_file, ensure_ascii=False, indent=2)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp_path, path)
            tmp_path = None
        except OSError as exc:
            logger.error("Failed to atomically write %s: %s", path, exc)
            raise
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    @staticmethod
    def make_resource_id(link: str) -> str:
        return (link or "").strip()

    def load_search_history(self) -> List[Dict[str, Any]]:
        with self._lock:
            data = self._read_json(self.history_file, [])
            return data if isinstance(data, list) else []

    def save_search_history(self, keyword: str, total: int = 0) -> None:
        term = (keyword or "").strip()
        if not term:
            return
        with self._lock:
            history = [
                item
                for item in self.load_search_history()
                if isinstance(item, dict) and item.get("keyword") != term
            ]
            history.insert(
                0,
                {"keyword": term, "count": int(total or 0), "timestamp": int(time.time())},
            )
            self._write_json(self.history_file, history[:50])

    def clear_search_history(self) -> None:
        with self._lock:
            self._write_json(self.history_file, [])

    def import_search_history(self, records: List[Dict[str, Any]]) -> None:
        cleaned: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for item in records or []:
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("keyword") or "").strip()
            if not keyword or keyword in seen:
                continue
            seen.add(keyword)
            try:
                count_val = int(item.get("count") or 0)
            except (TypeError, ValueError):
                count_val = 0
            try:
                ts_val = int(item.get("timestamp") or time.time())
            except (TypeError, ValueError):
                ts_val = int(time.time())
            cleaned.append({"keyword": keyword, "count": count_val, "timestamp": ts_val})
        with self._lock:
            self._write_json(self.history_file, cleaned[:50])

    def _ensure_favorites_loaded(self) -> None:
        if self._favorites_cache is None:
            data = self._read_json(self.favorites_file, [])
            valid = [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []
            self._favorites_cache = valid
            self._favorites_id_set = {
                self.make_resource_id(item.get("url", ""))
                for item in valid
                if self.make_resource_id(item.get("url", ""))
            }

    def get_favorites(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._ensure_favorites_loaded()
            return list(self._favorites_cache or [])

    def save_favorites(self, favorites: List[Dict[str, Any]]) -> None:
        with self._lock:
            cleaned = [item for item in (favorites or []) if isinstance(item, dict)]
            self._write_json(self.favorites_file, cleaned)
            self._favorites_cache = cleaned
            self._favorites_id_set = {
                self.make_resource_id(item.get("url", ""))
                for item in cleaned
                if self.make_resource_id(item.get("url", ""))
            }

    def is_favorited(self, link: str) -> bool:
        resource_id = self.make_resource_id(link)
        if not resource_id:
            return False
        with self._lock:
            self._ensure_favorites_loaded()
            return resource_id in (self._favorites_id_set or set())

    def toggle_favorite(self, resource: Dict[str, Any]) -> bool:
        if not isinstance(resource, dict):
            return False
        raw_url = self.make_resource_id(resource.get("url", ""))
        link = sanitize_url(raw_url) or raw_url
        if not link:
            return False

        with self._lock:
            self._ensure_favorites_loaded()
            current = list(self._favorites_cache or [])
            filtered = [item for item in current if self.make_resource_id(item.get("url", "")) != link]
            is_now_favorite = len(filtered) == len(current)
            if is_now_favorite:
                filtered.insert(
                    0,
                    {
                        "name": str(resource.get("name") or "未知资源"),
                        "url": link,
                        "pwd": str(resource.get("pwd") or ""),
                        "type": str(resource.get("type") or ""),
                        "source": str(resource.get("source", resource.get("_source", "")) or ""),
                        "timestamp": int(time.time()),
                    },
                )
            self.save_favorites(filtered)
            return is_now_favorite

    def clear_favorites(self) -> None:
        self.save_favorites([])

    def import_favorites(self, records: List[Dict[str, Any]]) -> None:
        cleaned: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for item in records or []:
            if not isinstance(item, dict):
                continue
            url = sanitize_url(item.get("url") or item.get("link") or "")
            if not url or url in seen:
                continue
            seen.add(url)
            try:
                ts_val = int(item.get("timestamp") or time.time())
            except (TypeError, ValueError):
                ts_val = int(time.time())
            cleaned.append(
                {
                    "name": str(item.get("name") or "未知资源"),
                    "url": url,
                    "pwd": str(item.get("pwd") or ""),
                    "type": str(item.get("type") or ""),
                    "source": str(item.get("source") or ""),
                    "timestamp": ts_val,
                }
            )
        self.save_favorites(cleaned)

    def _ensure_broken_loaded(self) -> None:
        if self._broken_cache is None:
            data = self._read_json(self.broken_file, [])
            valid = [str(item).strip() for item in data if str(item).strip()] if isinstance(data, list) else []
            self._broken_cache = valid
            self._broken_set = set(valid)

    def get_broken_links(self) -> List[str]:
        with self._lock:
            self._ensure_broken_loaded()
            return list(self._broken_cache or [])

    def is_broken_marked(self, link: str) -> bool:
        resource_id = self.make_resource_id(link)
        if not resource_id:
            return False
        with self._lock:
            self._ensure_broken_loaded()
            return resource_id in (self._broken_set or set())

    def toggle_broken_link(self, resource: Dict[str, Any]) -> bool:
        if not isinstance(resource, dict):
            return False
        link = self.make_resource_id(resource.get("url", ""))
        if not link:
            return False
        with self._lock:
            self._ensure_broken_loaded()
            current = list(self._broken_cache or [])
            filtered = [item for item in current if item != link]
            is_now_broken = len(filtered) == len(current)
            if is_now_broken:
                filtered.insert(0, link)
            self._write_json(self.broken_file, filtered)
            self._broken_cache = filtered
            self._broken_set = set(filtered)
            return is_now_broken

    def _ensure_quality_loaded(self) -> None:
        if self._quality_cache is None:
            data = self._read_json(self.quality_file, {})
            parsed: Dict[str, int] = {}
            if isinstance(data, dict):
                for key, value in data.items():
                    try:
                        parsed[str(key)] = int(value)
                    except (TypeError, ValueError):
                        continue
            self._quality_cache = parsed

    def get_quality_map(self) -> Dict[str, int]:
        with self._lock:
            self._ensure_quality_loaded()
            return dict(self._quality_cache or {})

    def get_quality(self, link: str) -> int:
        resource_id = self.make_resource_id(link)
        if not resource_id:
            return 0
        with self._lock:
            self._ensure_quality_loaded()
            return int((self._quality_cache or {}).get(resource_id, 0) or 0)

    def set_quality(self, link: str, score: int) -> None:
        resource_id = self.make_resource_id(link)
        if not resource_id:
            return
        with self._lock:
            self._ensure_quality_loaded()
            data = dict(self._quality_cache or {})
            safe_score = max(0, min(5, int(score or 0)))
            if safe_score <= 0:
                data.pop(resource_id, None)
            else:
                data[resource_id] = safe_score
            self._write_json(self.quality_file, data)
            self._quality_cache = data

    def load_settings(self) -> Dict[str, Any]:
        with self._lock:
            data = self._read_json(self.settings_file, {})
            return data if isinstance(data, dict) else {}

    def load_theme_mode(self) -> str:
        data = self.load_settings()
        mode = str(data.get("theme_mode", "")).strip().lower()
        if mode in {"light", "dark", "system"}:
            return mode
        return "system"

    def save_theme_mode(self, mode: str, effective_theme: str) -> None:
        normalized_mode = mode if mode in {"light", "dark", "system"} else "system"
        normalized_theme = "light" if effective_theme == "light" else "dark"
        with self._lock:
            data = self.load_settings()
            data["theme_mode"] = normalized_mode
            data["theme"] = normalized_theme
            self._write_json(self.settings_file, data)

    def save_setting(self, key: str, value: Any) -> None:
        with self._lock:
            data = self.load_settings()
            data[key] = value
            self._write_json(self.settings_file, data)

    def cache_results(self, key: str, results: List[Dict[str, Any]]) -> None:
        now = int(time.time())
        with self._lock:
            cache = self._read_json(self.cache_file, {})
            if not isinstance(cache, dict):
                cache = {}
            # 清理过期并限制最大缓存条目数
            fresh = {
                k: v
                for k, v in cache.items()
                if isinstance(v, dict) and now - int(v.get("timestamp") or 0) <= self.CACHE_TTL_SECONDS
            }
            fresh[key] = {"timestamp": now, "data": (results or [])[:200]}
            if len(fresh) > self.CACHE_MAX_ENTRIES:
                sorted_keys = sorted(
                    fresh.keys(),
                    key=lambda item_k: int(fresh[item_k].get("timestamp") or 0),
                    reverse=True,
                )
                fresh = {k: fresh[k] for k in sorted_keys[: self.CACHE_MAX_ENTRIES]}
            self._write_json(self.cache_file, fresh)

    def get_cached_results(self, key: str) -> List[Dict[str, Any]]:
        now = int(time.time())
        with self._lock:
            cache = self._read_json(self.cache_file, {})
            if not isinstance(cache, dict):
                return []
            entry = cache.get(key, {})
            if not isinstance(entry, dict):
                return []
            if now - int(entry.get("timestamp") or 0) > self.CACHE_TTL_SECONDS:
                return []
            return entry.get("data", []) if isinstance(entry.get("data"), list) else []
