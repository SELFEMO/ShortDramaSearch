from __future__ import annotations

import json
import re
import time
from copy import deepcopy
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from flask import Flask, Response, redirect, render_template, request

app = Flask(__name__, static_folder="static", template_folder="templates")

# ==================== API 配置 ====================
BASE_API = "https://api.kuleu.com/api"
REQUEST_TIMEOUT = 15
REQUEST_RETRIES = 2
SEARCH_RESULT_LIMIT = 200
SEARCH_RETRY_ATTEMPTS = 3
SEARCH_RETRY_DELAY = 0.7
CACHE_TTL_SECONDS = 60

# 中文：服务端复用 docs/index.html 的来源集合，避免 Flask API 与网页下拉选项产生语义偏差。
# English: The server reuses the same source presets as docs/index.html so the Flask API and page selector cannot drift semantically.
TYPE_PRESETS = {
    "all": [
        "baidu",
        "aliyun",
        "quark",
        "tianyi",
        "uc",
        "mobile",
        "115",
        "pikpak",
        "xunlei",
        "123",
        "magnet",
        "ed2k",
    ],
    "netdisk": [
        "baidu",
        "aliyun",
        "quark",
        "tianyi",
        "uc",
        "mobile",
        "115",
        "pikpak",
        "xunlei",
        "123",
    ],
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

SOURCE_ALIASES = {
    "yidong": "mobile",
    "移动": "mobile",
    "百度": "baidu",
    "夸克": "quark",
    "阿里": "aliyun",
    "天翼": "tianyi",
    "迅雷": "xunlei",
}

KULEU_ENDPOINTS = {
    "jhsj": f"{BASE_API}/jhsj",
    "yingshi": f"{BASE_API}/yingshi",
    "shortdramarank": f"{BASE_API}/shortdramarank",
    "vtquark": f"{BASE_API}/vtquark",
    "ico": f"{BASE_API}/ico",
    "qrcode": f"{BASE_API}/qrcode",
}

PWD_VALUE_RE = re.compile(
    r'("pwd"\s*:\s*)(?!")(?!(?:null|true|false)\b)([A-Za-z0-9+\-.]{1,32})(?=\s*[,}\]])',
    re.IGNORECASE,
)
HIDDEN_CHAR_RE = re.compile(r"[\u200B-\u200D\uFEFF]")
SPACE_RE = re.compile(r"\s+")

_session = requests.Session()
_session.headers.update(
    {
        "Accept": "application/json,text/plain,*/*",
        "User-Agent": "ShortDramaSearch-Flask/2026 (+https://github.com/SELFEMO/ShortDramaSearch)",
    }
)
_cache: dict[str, tuple[float, Any]] = {}


# ==================== 通用响应与参数工具 ====================
def json_response(payload: Any, status: int = 200) -> Response:
    # 中文：统一使用 ensure_ascii=False，保证 Flask 直接 API 与 GitHub Pages JSON 模式一样可读。
    # English: ensure_ascii=False keeps the Flask direct API as readable as the GitHub Pages JSON mode for Chinese text.
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8",
    )


def normalize_keyword(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).replace("\u00A0", " ")
    text = HIDDEN_CHAR_RE.sub("", text)
    return SPACE_RE.sub(" ", text).strip()


def get_first_arg(*names: str) -> str:
    for name in names:
        value = request.args.get(name)
        if value is not None and normalize_keyword(value):
            return normalize_keyword(value)
    return ""


def get_request_keyword(data: dict[str, Any] | None = None) -> str:
    data = data or {}
    for name in ("q", "search", "name", "s", "keyword", "text"):
        value = data.get(name)
        if value is not None and normalize_keyword(value):
            return normalize_keyword(value)

    return get_first_arg("q", "search", "name", "s", "keyword", "text")


def normalize_preset_name(value: Any) -> str:
    raw = normalize_keyword(value or "all")
    mapped = SOURCE_ALIASES.get(raw, raw)
    return mapped if mapped in TYPE_PRESETS else "all"


def build_search_terms(raw_input: str) -> list[str]:
    keyword = normalize_keyword(raw_input)
    if not keyword:
        return []

    parts = [part for part in keyword.split(" ") if part]
    terms = {keyword, *parts} if len(parts) > 1 else {keyword}

    # 中文：完整关键词必须优先搜索，拆词只作为补召回，避免短词结果冲掉精确命中。
    # English: The full keyword is searched first and split terms only improve recall, preventing short terms from outranking exact hits.
    return sorted(terms, key=lambda term: (term != keyword, -len(term)))


def make_cache_key(url: str, params: dict[str, Any] | None, raw_query: str | None) -> str:
    if raw_query is not None:
        return f"{url}?{raw_query}"

    safe_params = params or {}
    param_text = "&".join(f"{key}={safe_params[key]}" for key in sorted(safe_params))
    return f"{url}?{param_text}"


def get_cached(cache_key: str) -> Any | None:
    cached = _cache.get(cache_key)
    if not cached:
        return None

    cached_at, payload = cached
    if time.time() - cached_at > CACHE_TTL_SECONDS:
        _cache.pop(cache_key, None)
        return None

    return deepcopy(payload)


def set_cached(cache_key: str, payload: Any) -> None:
    _cache[cache_key] = (time.time(), deepcopy(payload))


# ==================== JSON 解析与字段修正 ====================
def protect_pwd_in_json_text(text: str) -> str:
    # 中文：部分接口会把类似 32e7 的提取码写成裸值，先加引号才能避免 JSON 解析失败。
    # English: Some upstream responses emit codes like 32e7 as bare values, so quoting them first prevents JSON parsing failures.
    return PWD_VALUE_RE.sub(lambda match: f'{match.group(1)}"{match.group(2)}"', text)


def extract_pwd_from_link(link: Any) -> str:
    if not link:
        return ""

    text = str(link).strip()
    try:
        query = parse_qs(urlparse(text).query)
        pwd_values = query.get("pwd")
        if pwd_values and pwd_values[0].strip():
            return pwd_values[0].strip()
    except Exception:
        pass

    match = re.search(r"[?&]pwd=([^&#]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def normalize_resource_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item

    fixed = dict(item)
    link = (
        fixed.get("url")
        or fixed.get("viewlink")
        or fixed.get("link")
        or fixed.get("share_url")
        or fixed.get("shareUrl")
        or ""
    )
    pwd_from_link = extract_pwd_from_link(link)

    # 中文：提取码优先从链接恢复，因为 URL 查询参数通常比接口里的 pwd 字段更接近真实分享码。
    # English: The password is recovered from the URL first because query parameters are usually closer to the real share code than the upstream pwd field.
    if pwd_from_link:
        fixed["pwd"] = pwd_from_link
    elif "pwd" in fixed and fixed["pwd"] is not None:
        fixed["pwd"] = str(fixed["pwd"]).strip()

    return fixed


def normalize_pwd_fields_deep(value: Any) -> Any:
    if isinstance(value, list):
        return [normalize_pwd_fields_deep(item) for item in value]

    if isinstance(value, dict):
        fixed = {key: normalize_pwd_fields_deep(child) for key, child in value.items()}
        return normalize_resource_item(fixed)

    return value


def parse_api_text_safely(text: str) -> Any:
    if not text or not text.strip():
        raise ValueError("API 返回空内容")

    protected_text = protect_pwd_in_json_text(text)
    parsed = json.loads(protected_text)
    return normalize_pwd_fields_deep(parsed)


# ==================== 酷乐 API 请求代理 ====================
def request_kuleu(
    endpoint_name: str,
    params: dict[str, Any] | None = None,
    raw_query: str | None = None,
    retries: int = REQUEST_RETRIES,
    timeout: int = REQUEST_TIMEOUT,
    use_cache: bool = True,
) -> tuple[Any | None, dict[str, Any] | None]:
    api_url = KULEU_ENDPOINTS[endpoint_name]
    cache_key = make_cache_key(api_url, params, raw_query)

    if use_cache:
        cached = get_cached(cache_key)
        if cached is not None:
            return cached, None

    request_url = f"{api_url}?{raw_query}" if raw_query is not None else api_url
    last_error = "请求失败"

    for attempt in range(retries + 1):
        try:
            response = _session.get(request_url, params=params if raw_query is None else None, timeout=timeout)

            if response.status_code == 429:
                return None, {"status": 429, "message": "接口请求过于频繁，请稍后再试"}

            response.raise_for_status()
            payload = parse_api_text_safely(response.text)

            if use_cache:
                set_cached(cache_key, payload)

            return payload, None
        except requests.Timeout:
            last_error = "请求超时"
        except requests.RequestException as error:
            last_error = f"网络请求失败: {error}"
        except (ValueError, json.JSONDecodeError) as error:
            last_error = f"API 返回格式错误: {error}"

        # 中文：只在还有剩余机会时退避等待，降低第三方接口瞬时抖动对页面体验的影响。
        # English: Backoff only when another attempt remains, reducing the impact of transient upstream instability on the page experience.
        if attempt < retries:
            time.sleep(0.5 * (attempt + 1))

    return None, {"status": 502, "message": last_error}


def proxy_json_endpoint(endpoint_name: str, raw_query: str | None = None) -> Response:
    payload, error = request_kuleu(endpoint_name, raw_query=raw_query)
    if error:
        return json_response({"code": -1, "msg": error["message"]}, status=error["status"])

    return json_response(payload)


# ==================== 聚合搜索 API 模式 ====================
def merge_jhsj_payload(payload: Any, requested_types: list[str], search_term: str, merged: dict[str, list[dict[str, Any]]], url_set: set[str]) -> int:
    if not isinstance(payload, dict):
        return 0

    raw_data = payload.get("data")
    source_map: dict[str, Any] = {}

    if isinstance(raw_data, dict):
        if isinstance(raw_data.get("merged_by_type"), dict):
            source_map = raw_data["merged_by_type"]
        else:
            source_map = raw_data
    elif isinstance(raw_data, list) and len(requested_types) == 1:
        source_map = {requested_types[0]: raw_data}

    added = 0
    for type_name in requested_types:
        items = source_map.get(type_name, [])
        if not isinstance(items, list):
            continue

        bucket = merged.setdefault(type_name, [])
        for item in items:
            if not isinstance(item, dict):
                continue

            fixed = normalize_resource_item(item)
            link = str(fixed.get("url") or fixed.get("viewlink") or fixed.get("link") or "").strip()
            if not link or link in url_set:
                continue

            url_set.add(link)
            fixed["_searchTerm"] = search_term
            bucket.append(fixed)
            added += 1

            if len(url_set) >= SEARCH_RESULT_LIMIT:
                return added

    return added


def fetch_and_merge_data(keyword: str, preset_name: str) -> dict[str, Any]:
    safe_preset = normalize_preset_name(preset_name)
    requested_types = TYPE_PRESETS[safe_preset]
    type_param = ",".join(requested_types)
    search_terms = build_search_terms(keyword)

    merged_by_type: dict[str, list[dict[str, Any]]] = {}
    url_set: set[str] = set()
    success_count = 0
    failed_count = 0
    failed_terms: list[str] = []

    for search_term in search_terms:
        payload, error = request_kuleu(
            "jhsj",
            params={"type": type_param, "name": search_term},
            retries=REQUEST_RETRIES,
        )

        if error:
            failed_count += 1
            failed_terms.append(search_term)
            if error["status"] == 429:
                return {
                    "mergedByType": merged_by_type,
                    "total": sum(len(items) for items in merged_by_type.values()),
                    "typeList": [key for key, items in merged_by_type.items() if items],
                    "apiStatus": {
                        "successCount": success_count,
                        "failedCount": failed_count,
                        "failedTerms": failed_terms,
                        "failedReason": "rate_limited",
                    },
                }
            continue

        code = payload.get("code") if isinstance(payload, dict) else None
        if code not in (0, 1, 200):
            failed_count += 1
            failed_terms.append(search_term)
            continue

        success_count += 1
        merge_jhsj_payload(payload, requested_types, search_term, merged_by_type, url_set)

        if len(url_set) >= SEARCH_RESULT_LIMIT:
            break

    # 中文：排序规则保持 docs/index.html 的“完整关键词优先”体验，保证 Flask JSON 与页面结果顺序一致。
    # English: Sorting keeps docs/index.html's exact-keyword-first behavior so Flask JSON and page rendering stay consistent.
    for items in merged_by_type.values():
        items.sort(
            key=lambda item: (
                item.get("_searchTerm") != keyword,
                -(len(str(item.get("name") or ""))),
            )
        )

    type_list = [type_name for type_name in requested_types if merged_by_type.get(type_name)]
    total = sum(len(merged_by_type[type_name]) for type_name in type_list)

    return {
        "mergedByType": {type_name: merged_by_type[type_name] for type_name in type_list},
        "total": total,
        "typeList": type_list,
        "apiStatus": {
            "successCount": success_count,
            "failedCount": failed_count,
            "failedTerms": failed_terms,
        },
    }


def fetch_and_merge_data_stable(keyword: str, preset_name: str) -> dict[str, Any]:
    last_result: dict[str, Any] | None = None

    for attempt in range(SEARCH_RETRY_ATTEMPTS):
        result = fetch_and_merge_data(keyword, preset_name)
        last_result = result

        if result.get("total", 0) > 0 and result.get("typeList"):
            result["effectivePreset"] = normalize_preset_name(preset_name)
            result["retryCount"] = attempt
            return result

        api_status = result.get("apiStatus") or {}
        if api_status.get("failedReason") == "rate_limited":
            break

        if attempt < SEARCH_RETRY_ATTEMPTS - 1:
            time.sleep(SEARCH_RETRY_DELAY * (attempt + 1))

    result = last_result or {"mergedByType": {}, "total": 0, "typeList": []}
    result["effectivePreset"] = normalize_preset_name(preset_name)
    result["retryCount"] = SEARCH_RETRY_ATTEMPTS - 1
    return result


def build_search_api_payload(keyword: str, preset_name: str) -> dict[str, Any]:
    result = fetch_and_merge_data_stable(keyword, preset_name)
    effective_preset = result.get("effectivePreset") or normalize_preset_name(preset_name)

    return {
        "code": 0,
        "msg": "success",
        "keyword": keyword,
        "type": effective_preset,
        "total": result.get("total", 0),
        "data": result.get("mergedByType", {}),
    }


def flatten_merged_data(merged_data: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source_items in merged_data.values():
        if isinstance(source_items, list):
            items.extend(source_items)
    return items


# ==================== 页面路由 ====================
@app.get("/")
def index() -> Response | str:
    keyword = get_request_keyword()
    output_format = (request.args.get("format") or "").lower()

    if output_format == "json":
        if not keyword:
            return json_response({"code": -1, "msg": "missing keyword"}, status=400)

        preset = normalize_preset_name(request.args.get("from") or request.args.get("type") or "all")
        return json_response(build_search_api_payload(keyword, preset))

    return render_template("index.html")


@app.get("/api/search")
def api_search() -> Response:
    keyword = get_request_keyword()
    if not keyword:
        return json_response({"code": -1, "msg": "missing keyword"}, status=400)

    preset = normalize_preset_name(request.args.get("from") or request.args.get("type") or "all")
    return json_response(build_search_api_payload(keyword, preset))


@app.post("/search")
def legacy_search() -> Response:
    data = request.get_json(silent=True) if request.is_json else request.form.to_dict()
    data = data or {}
    search_type = data.get("type", "聚合资源搜索")
    keyword = get_request_keyword(data)

    if search_type in ("每日影视资源", "每日影视"):
        return api_daily_combined()

    if search_type in ("短剧热度榜", "夸克热搜"):
        endpoint = "shortdramarank" if search_type == "短剧热度榜" else "vtquark"
        raw_query = "tag=%E7%9F%AD%E5%89%A7" if endpoint == "vtquark" else ""
        return proxy_json_endpoint(endpoint, raw_query=raw_query)

    if not keyword:
        return json_response({"code": 400, "msg": "请输入搜索关键词"}, status=400)

    preset = normalize_preset_name(data.get("sub_type") or data.get("from") or "all")
    payload = build_search_api_payload(keyword, preset)
    items = flatten_merged_data(payload["data"])

    return json_response({"code": 200, "msg": "成功", "data": items, "count": len(items)})


@app.get("/neo.html")
def neo_page() -> Response:
    # 中文：index.html 的新版入口来自 GitHub Pages；Flask 版未重写 Neo，因此保持可点击并跳回线上稳定页面。
    # English: The new-UI entry belongs to GitHub Pages; Flask does not rewrite Neo, so the link remains usable by redirecting to the stable online page.
    return redirect("https://selfemo.github.io/ShortDramaSearch/neo.html", code=302)


@app.get("/console.html")
def console_page() -> Response:
    # 中文：Console 入口同样保持跳转而不复制第二套实验界面，避免 Flask 重构范围失控。
    # English: The Console entry redirects instead of copying a second experimental UI, keeping the Flask rewrite scoped to index.html.
    return redirect("https://selfemo.github.io/ShortDramaSearch/console.html", code=302)


# ==================== 前端同源代理路由 ====================
@app.get("/api/kuleu/jhsj")
def proxy_jhsj() -> Response:
    return proxy_json_endpoint("jhsj", raw_query=request.query_string.decode("utf-8"))


@app.get("/api/kuleu/yingshi")
def proxy_yingshi() -> Response:
    raw_query = request.query_string.decode("utf-8")
    if not raw_query and request.args.get("source"):
        raw_query = request.args.get("source", "")
    return proxy_json_endpoint("yingshi", raw_query=raw_query)


@app.get("/api/kuleu/shortdramarank")
def proxy_shortdrama_rank() -> Response:
    return proxy_json_endpoint("shortdramarank", raw_query=request.query_string.decode("utf-8"))


@app.get("/api/kuleu/vtquark")
def proxy_vtquark() -> Response:
    raw_query = request.query_string.decode("utf-8") or "tag=%E7%9F%AD%E5%89%A7"
    return proxy_json_endpoint("vtquark", raw_query=raw_query)


@app.get("/api/kuleu/ico")
def proxy_ico() -> Response:
    return redirect(f"{KULEU_ENDPOINTS['ico']}?{request.query_string.decode('utf-8')}", code=302)


@app.get("/api/kuleu/qrcode")
def proxy_qrcode() -> Response:
    return redirect(f"{KULEU_ENDPOINTS['qrcode']}?{request.query_string.decode('utf-8')}", code=302)


@app.get("/api/daily")
def api_daily_combined() -> Response:
    all_items: list[dict[str, Any]] = []
    errors: list[str] = []

    for source in ("baidu", "quark"):
        payload, error = request_kuleu("yingshi", raw_query=source)
        if error:
            errors.append(f"{source}: {error['message']}")
            continue

        data = payload.get("data", []) if isinstance(payload, dict) else []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    fixed = dict(item)
                    fixed["_source"] = source
                    all_items.append(fixed)

    if not all_items and errors:
        return json_response({"code": -1, "msg": "; ".join(errors), "data": [], "count": 0}, status=502)

    return json_response({"code": 200, "msg": "success", "data": all_items, "count": len(all_items)})


@app.get("/api/health")
def health() -> Response:
    return json_response({"code": 0, "msg": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
