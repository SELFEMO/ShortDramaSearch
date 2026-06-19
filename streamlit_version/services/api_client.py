import json
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
import streamlit as st

from services.constants import (
    JHSJ_API,
    MAX_SEARCH_TOTAL,
    QRCODE_API,
    RANK_TIMEOUT,
    SEARCH_TIMEOUT,
    SHORTDRAMA_RANK_API,
    TYPE_PRESETS,
    VTQUARK_API,
    YINGSHI_API,
)
from services.normalizers import (
    build_search_terms,
    normalize_resource_item,
    normalize_search_keyword,
    ordered_types,
    parse_api_json_safely,
    source_label,
    valid_preset_name,
)


@st.cache_data(show_spinner=False, ttl=300)
def request_api_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = SEARCH_TIMEOUT) -> Dict[str, Any]:
    # 中文：Streamlit 运行在服务端，不需要浏览器 CORS 代理；统一缓存可降低第三方接口压力并减少 429。
    # English: Streamlit runs server-side and does not need browser CORS proxies; shared caching reduces third-party API pressure and 429s.
    response = requests.get(url, params=params, timeout=timeout)
    if response.status_code == 429:
        raise RuntimeError("rate_limited")
    response.raise_for_status()
    return parse_api_json_safely(response.text)


def fetch_search_api(type_param: str, term: str) -> Dict[str, Any]:
    return request_api_json(JHSJ_API, params={"type": type_param, "name": term}, timeout=SEARCH_TIMEOUT)


def fetch_and_merge_data(term: str, preset_name: str) -> Dict[str, Any]:
    safe_term = normalize_search_keyword(term)
    safe_preset = valid_preset_name(preset_name)
    types = TYPE_PRESETS[safe_preset]
    type_param = ",".join(types)
    search_terms = build_search_terms(safe_term)

    merged_by_type: Dict[str, List[Dict[str, Any]]] = {}
    url_set = set()
    total = 0
    success_count = 0
    failed_count = 0
    failed_terms: List[str] = []
    failed_reason = ""

    for search_term in search_terms:
        try:
            data = fetch_search_api(type_param, search_term)
            success_count += 1
        except RuntimeError as error:
            failed_count += 1
            failed_terms.append(search_term)
            if str(error) == "rate_limited":
                failed_reason = "rate_limited"
                break
            continue
        except Exception:
            failed_count += 1
            failed_terms.append(search_term)
            continue

        payload = data.get("data", {}) if isinstance(data, dict) else {}
        grouped = payload.get("merged_by_type", {}) if isinstance(payload, dict) else {}

        if isinstance(grouped, dict):
            for type_name, items in grouped.items():
                if type_name not in merged_by_type:
                    merged_by_type[type_name] = []
                if not isinstance(items, list):
                    continue
                for raw_item in items:
                    item = normalize_resource_item(raw_item)
                    link = item.get("url") or ""
                    if not link or link in url_set:
                        continue
                    url_set.add(link)
                    item["_searchTerm"] = search_term
                    merged_by_type[type_name].append(item)
                    total += 1

        if total >= MAX_SEARCH_TOTAL:
            break

    for type_name, items in merged_by_type.items():
        # 中文：完整关键词命中的结果优先展示，拆词结果按标题长度排序，延续 docs/index.html 的排序体验。
        # English: Full-keyword hits are shown first and split-term hits are sorted by title length, matching the docs/index.html experience.
        items.sort(
            key=lambda item: (
                0 if item.get("_searchTerm") == safe_term else 1,
                -(len(str(item.get("name") or ""))),
            )
        )

    type_list = [type_name for type_name, items in merged_by_type.items() if items]
    return {
        "mergedByType": merged_by_type,
        "total": total,
        "typeList": type_list,
        "apiStatus": {
            "successCount": success_count,
            "failedCount": failed_count,
            "failedTerms": failed_terms,
            "failedReason": failed_reason,
        },
    }


def normalize_merged_search_result(result: Dict[str, Any]) -> Dict[str, Any]:
    merged = result.get("mergedByType", {}) if isinstance(result, dict) else {}
    type_list = [type_name for type_name, items in merged.items() if isinstance(items, list) and items]
    counted_total = sum(len(merged[type_name]) for type_name in type_list)
    total = max(int(result.get("total", 0) or 0), counted_total) if isinstance(result, dict) else counted_total
    return {"mergedByType": merged, "total": total, "typeList": type_list}


def is_merged_search_empty(result: Dict[str, Any]) -> bool:
    return not result or not result.get("typeList") or int(result.get("total") or 0) <= 0


def fetch_and_merge_data_stable(term: str, preset_name: str, attempts: int = 3, delay: float = 0.7) -> Dict[str, Any]:
    # 中文：API 生成器和 URL JSON 模式比普通搜索更需要稳定输出，因此允许空结果场景做有限重试。
    # English: API Generator and URL JSON mode need stable output more than normal search, so empty results get limited retries.
    safe_preset = valid_preset_name(preset_name)
    last_result: Optional[Dict[str, Any]] = None
    last_error: Optional[Exception] = None

    for index in range(max(1, attempts)):
        try:
            raw_result = fetch_and_merge_data(term, safe_preset)
            normalized = normalize_merged_search_result(raw_result)
            last_result = normalized
            if not is_merged_search_empty(normalized):
                return {**normalized, "effectivePreset": safe_preset, "retryCount": index}
        except Exception as error:
            last_error = error

        if index < attempts - 1:
            time.sleep(delay * (index + 1))

    if last_result is not None:
        return {**last_result, "effectivePreset": safe_preset, "retryCount": attempts - 1}
    if last_error is not None:
        raise last_error
    return {"mergedByType": {}, "total": 0, "typeList": [], "effectivePreset": safe_preset, "retryCount": attempts - 1}


@st.cache_data(show_spinner=False, ttl=1800)
def load_shortdrama_rank() -> List[Dict[str, Any]]:
    data = request_api_json(SHORTDRAMA_RANK_API, timeout=RANK_TIMEOUT)
    if data.get("code") == 200 and isinstance(data.get("data"), list):
        return data["data"]
    return []


@st.cache_data(show_spinner=False, ttl=1800)
def load_vtquark_rank() -> List[Dict[str, Any]]:
    data = request_api_json(VTQUARK_API, params={"tag": "短剧"}, timeout=RANK_TIMEOUT)
    if data.get("code") == 200 and isinstance(data.get("data"), list):
        return data["data"]
    return []


@st.cache_data(show_spinner=False, ttl=600)
def fetch_daily_api(source: str) -> List[Dict[str, Any]]:
    # 中文：每日影视接口在静态网页中使用 ?baidu / ?quark 这种裸查询参数，服务端也保持同样 URL 形态以减少接口兼容风险。
    # English: The Daily API uses bare query parameters like ?baidu / ?quark in the static page, so the server version keeps the same URL shape for compatibility.
    data = request_api_json(f"{YINGSHI_API}?{source}", timeout=SEARCH_TIMEOUT)
    if data.get("code") == 1 and isinstance(data.get("data"), list):
        return [{**item, "_source": source} for item in data["data"] if isinstance(item, dict)]
    return []


def load_daily_resources() -> Tuple[List[Dict[str, Any]], List[str]]:
    # 中文：每日影视与 docs/index.html 一样合并百度和夸克；服务端版本用顺序请求换取更简单可靠的错误收集。
    # English: Daily resources merge Baidu and Quark like docs/index.html; the server version uses sequential requests for simpler, reliable error collection.
    items: List[Dict[str, Any]] = []
    errors: List[str] = []
    for source in ("baidu", "quark"):
        try:
            items.extend(fetch_daily_api(source))
        except Exception as error:
            errors.append(f"{source_label(source)}：{error}")

    items.sort(key=lambda item: str(item.get("addtime") or ""), reverse=True)
    return items, errors


def build_qrcode_url(text: str, size: int = 220) -> str:
    params = {"frame": 1, "e": "L", "text": text or "", "size": size}
    return f"{QRCODE_API}?{urlencode(params)}"


def clean_preview_item(item: Dict[str, Any]) -> Dict[str, Any]:
    fixed = normalize_resource_item(item)
    fixed.pop("_searchTerm", None)
    return fixed


def build_limited_preview_data(merged_by_type: Dict[str, List[Dict[str, Any]]], type_list: List[str], limit: int = 5) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
    # 中文：预览按来源轮询抽样，避免前 5 条全来自同一网盘，从而更接近 docs/index.html 的对比体验。
    # English: Preview samples sources round-robin so the first five items do not all come from one drive, matching docs/index.html's comparison experience.
    preview_data: Dict[str, List[Dict[str, Any]]] = {}
    cursors: Dict[str, int] = {}
    count = 0
    has_more = True
    ordered = ordered_types(type_list)

    while count < limit and has_more:
        has_more = False
        for type_name in ordered:
            if count >= limit:
                break
            items = merged_by_type.get(type_name) or []
            cursor = cursors.get(type_name, 0)
            if cursor >= len(items):
                continue
            preview_data.setdefault(type_name, []).append(clean_preview_item(items[cursor]))
            cursors[type_name] = cursor + 1
            count += 1
            has_more = True

    return preview_data, count


def flatten_preview_links(preview_data: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []
    for type_name in ordered_types(preview_data.keys()):
        for raw_item in preview_data.get(type_name, []):
            if len(links) >= limit:
                break
            item = normalize_resource_item(raw_item)
            link = item.get("url") or ""
            if link:
                links.append({"type": type_name, "item": item, "link": link})
        if len(links) >= limit:
            break
    return links


def grouped_results_to_rows(merged_by_type: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for type_name in ordered_types(merged_by_type.keys()):
        for item in merged_by_type.get(type_name, []):
            rows.append(
                {
                    "source": source_label(type_name),
                    "type": type_name,
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "pwd": item.get("pwd"),
                    "search_term": item.get("_searchTerm"),
                }
            )
    return rows


def dump_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
