from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from services.constants import MAX_HISTORY
from services.normalizers import make_resource_id, normalize_resource_item, normalize_search_keyword, valid_preset_name


def init_state() -> None:
    defaults = {
        "history": [],
        "favorites": [],
        "broken_links": [],
        "quality_map": {},
        "hide_broken": False,
        "current_results": None,
        "current_keyword": "",
        "current_preset": "all",
        "daily_data": [],
        "pending_keyword": "",
        "pending_preset": "",
        "run_pending_search": False,
        "api_base_url": "http://localhost:8501/",
        "url_params_consumed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_search_history(term: str) -> None:
    keyword = normalize_search_keyword(term)
    if not keyword:
        return
    # 中文：搜索历史去重并保留最近项，模拟 docs/index.html localStorage 的“最近搜索”行为。
    # English: Search history is de-duplicated and kept newest-first, mirroring docs/index.html localStorage history behavior.
    old = [item for item in st.session_state.history if item != keyword]
    st.session_state.history = [keyword] + old[: MAX_HISTORY - 1]


def set_pending_search(keyword: str, preset: str = "all") -> None:
    # 中文：跨页面点击榜单或历史项时先写入 pending 状态，下一次渲染搜索页再执行，避免在非搜索页直接调用搜索 UI。
    # English: Cross-page rank/history clicks write a pending state first, then the search page executes it on render, avoiding search UI calls from other pages.
    st.session_state.pending_keyword = normalize_search_keyword(keyword)
    st.session_state.pending_preset = valid_preset_name(preset)
    st.session_state.run_pending_search = True


def get_favorites() -> List[Dict[str, Any]]:
    return list(st.session_state.get("favorites") or [])


def save_favorites(items: List[Dict[str, Any]]) -> None:
    st.session_state.favorites = items


def is_favorited(link: str) -> bool:
    resource_id = make_resource_id(link)
    return any(item.get("id") == resource_id for item in get_favorites())


def toggle_favorite(resource: Dict[str, Any]) -> None:
    # 中文：收藏以链接哈希为主键，避免同一资源在不同关键词结果中重复收藏。
    # English: Favorites are keyed by link hash so the same resource is not saved twice from different keyword results.
    fixed = normalize_resource_item(resource)
    link = fixed.get("url") or fixed.get("link") or ""
    resource_id = make_resource_id(link)
    if not resource_id:
        return

    items = get_favorites()
    if any(item.get("id") == resource_id for item in items):
        save_favorites([item for item in items if item.get("id") != resource_id])
    else:
        save_favorites(
            [
                {
                    "id": resource_id,
                    "name": fixed.get("name") or "未命名资源",
                    "link": link,
                    "pwd": fixed.get("pwd") or "",
                    "type": fixed.get("type") or resource.get("type") or "",
                    "savedAt": datetime.now().isoformat(timespec="seconds"),
                }
            ]
            + items
        )


def is_broken_marked(link: str) -> bool:
    return make_resource_id(link) in set(st.session_state.get("broken_links") or [])


def toggle_broken(link: str) -> None:
    resource_id = make_resource_id(link)
    if not resource_id:
        return
    broken = list(st.session_state.get("broken_links") or [])
    if resource_id in broken:
        broken = [item for item in broken if item != resource_id]
    else:
        broken.append(resource_id)
    st.session_state.broken_links = broken


def get_quality(link: str) -> int:
    return int((st.session_state.get("quality_map") or {}).get(make_resource_id(link), 0) or 0)


def set_quality(link: str, score: int) -> None:
    resource_id = make_resource_id(link)
    if not resource_id:
        return
    score = max(0, min(5, int(score or 0)))
    data = dict(st.session_state.get("quality_map") or {})
    if score:
        data[resource_id] = score
    else:
        data.pop(resource_id, None)
    st.session_state.quality_map = data
