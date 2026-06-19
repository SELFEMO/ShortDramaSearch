# -*- coding: utf-8 -*-

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import requests

BASE_API = "https://api.kuleu.com/api"
JHSJ_API = f"{BASE_API}/jhsj"
YINGSHI_API = f"{BASE_API}/yingshi"
SHORTDRAMA_RANK_API = f"{BASE_API}/shortdramarank"
VTQUARK_API = f"{BASE_API}/vtquark"
QRCODE_API = f"{BASE_API}/qrcode"
ONLINE_PAGE_URL = "https://selfemo.github.io/ShortDramaSearch/"

TYPE_LABEL = {
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

PRESET_LABEL = {
    "all": "全局聚合",
    "netdisk": "网盘聚合",
    **TYPE_LABEL,
}

PREVIEW_TYPE_ORDER = [
    "baidu",
    "quark",
    "aliyun",
    "tianyi",
    "uc",
    "mobile",
    "115",
    "pikpak",
    "xunlei",
    "123",
    "magnet",
    "ed2k",
]


class ApiError(RuntimeError):
    """业务化 API 异常，便于 UI 层展示明确状态。"""

    def __init__(self, message: str, error_type: str = "api_error"):
        super().__init__(message)
        self.error_type = error_type


class ApiClient:
    """与 docs/index.html 中使用的酷乐 API 保持同源语义的桌面端客户端。"""

    def __init__(self, timeout: int = 15, min_interval: float = 0.35):
        self.timeout = timeout
        self.min_interval = min_interval
        self._last_request_time = 0.0
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.cache_ttl = 60.0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "ShortDramaSearchDesktop/2026"
                ),
                "Accept": "application/json,text/plain,*/*",
            }
        )

    def _wait_interval(self) -> None:
        # 中文：网页端对搜索接口做了节流；桌面端同样节流，避免连续请求触发第三方接口 429。
        # English: The web page throttles search calls; the desktop client keeps the same guard to avoid third-party API 429 responses.
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request_time = time.time()

    def _cache_key(self, url: str, params: Optional[Dict[str, Any]]) -> str:
        if not params:
            return url
        return f"{url}?{urlencode(params, doseq=True)}"

    @staticmethod
    def _protect_pwd_in_json_text(text: str) -> str:
        # 中文：只在 JSON 解析前保护 pwd 字段，不能把所有数字都转成字符串，否则顶层 code 会从 0 变成 "0" 并导致成功判断失效。
        # English: Only pwd fields are protected before JSON parsing; converting every number to string would turn top-level code 0 into "0" and break success checks.
        if not isinstance(text, str):
            return text
        return re.sub(
            r'("pwd"\s*:\s*)(?!")(?!(?:null|true|false)\b)([A-Za-z0-9+\-.]{1,32})(?=\s*[,}\]])',
            lambda match: f'{match.group(1)}"{match.group(2)}"',
            text,
            flags=re.IGNORECASE,
        )

    @classmethod
    def _normalize_pwd_fields_deep(cls, value: Any) -> Any:
        # 中文：解析后再递归修正 pwd，优先从链接恢复真实提取码，避免接口把 32e7 这类提取码误写成数字。
        # English: After parsing, pwd is normalized recursively and preferably restored from links to avoid codes like 32e7 being damaged as numbers.
        if isinstance(value, list):
            return [cls._normalize_pwd_fields_deep(item) for item in value]
        if isinstance(value, dict):
            fixed = {key: cls._normalize_pwd_fields_deep(item) for key, item in value.items()}
            link = str(
                fixed.get("url")
                or fixed.get("viewlink")
                or fixed.get("link")
                or fixed.get("share_url")
                or fixed.get("shareUrl")
                or ""
            )
            pwd_from_link = cls.extract_pwd_from_link(link)
            if pwd_from_link:
                fixed["pwd"] = pwd_from_link
            elif "pwd" in fixed and fixed.get("pwd") is not None:
                fixed["pwd"] = str(fixed.get("pwd") or "").strip()
            return fixed
        return value

    @staticmethod
    def is_code(data: Dict[str, Any], *codes: int) -> bool:
        # 中文：第三方接口偶尔会把状态码返回成字符串；统一比较可避免 UI 因类型差异误判为空结果。
        # English: The third-party API may sometimes return status codes as strings, so normalized comparison prevents false empty results.
        if not isinstance(data, dict):
            return False
        actual = str(data.get("code", "")).strip()
        expected = {str(code) for code in codes}
        return actual in expected

    def _loads_json(self, text: str) -> Dict[str, Any]:
        try:
            data = json.loads(self._protect_pwd_in_json_text(text))
        except json.JSONDecodeError as exc:
            raise ApiError(f"API 返回数据不是有效 JSON: {exc}", "parse") from exc
        return self._normalize_pwd_fields_deep(data)

    def request_json(self, url: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> Dict[str, Any]:
        cache_key = self._cache_key(url, params)
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached[0] <= self.cache_ttl:
                return cached[1]

        self._wait_interval()

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.Timeout as exc:
            raise ApiError("请求超时，请稍后重试。", "timeout") from exc
        except requests.ConnectionError as exc:
            raise ApiError("网络连接失败，请检查网络。", "network") from exc
        except requests.RequestException as exc:
            raise ApiError(f"请求失败: {exc}", "network") from exc

        if response.status_code == 429:
            raise ApiError("接口请求过于频繁，请稍后再试。", "rate_limited")
        if not response.ok:
            raise ApiError(f"接口返回 HTTP {response.status_code}", "server")

        data = self._loads_json(response.text)
        if use_cache:
            self._cache[cache_key] = (time.time(), data)
        return data

    @staticmethod
    def normalize_search_keyword(keyword: str) -> str:
        return re.sub(r"\s+", " ", (keyword or "").strip())

    def build_search_terms(self, raw_input: str) -> List[str]:
        input_text = self.normalize_search_keyword(raw_input)
        if not input_text:
            return []

        parts = [p for p in re.split(r"\s+", input_text) if p]
        terms = {input_text}
        if len(parts) > 1:
            terms.update(parts)

        return sorted(terms, key=lambda item: (item != input_text, -len(item)))

    @staticmethod
    def extract_pwd_from_link(link: str) -> str:
        if not link:
            return ""
        try:
            parsed = urlparse(link)
            query = parse_qs(parsed.query)
            for key in ("pwd", "password", "pass", "code"):
                values = query.get(key)
                if values and values[0]:
                    return str(values[0]).strip()
        except Exception:
            return ""
        return ""

    @classmethod
    def normalize_pwd(cls, item: Dict[str, Any]) -> str:
        link_pwd = cls.extract_pwd_from_link(str(item.get("url") or item.get("viewlink") or ""))
        if link_pwd:
            return link_pwd

        for key in ("pwd", "password", "pass", "code"):
            value = item.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text and text.lower() not in ("none", "null", "undefined"):
                return text
        return ""

    @classmethod
    def normalize_resource_item(cls, item: Dict[str, Any], resource_type: str = "") -> Dict[str, Any]:
        # 中文：不同接口字段名不完全一致，统一字段后 UI、收藏和 JSON 预览才能复用同一套逻辑。
        # English: API fields are not fully consistent, so normalizing them lets UI, favorites and JSON preview share one logic path.
        data = dict(item or {})
        url = str(data.get("url") or data.get("viewlink") or data.get("link") or "").strip()
        name = str(data.get("name") or data.get("title") or data.get("text") or "未知资源").strip()
        return {
            **data,
            "name": name or "未知资源",
            "url": url,
            "pwd": cls.normalize_pwd({**data, "url": url}),
            "type": resource_type or str(data.get("type") or data.get("source") or "").strip(),
        }

    def fetch_and_merge_data(self, keyword: str, preset_name: str = "all", limit: int = 200) -> Dict[str, Any]:
        term = self.normalize_search_keyword(keyword)
        if not term:
            raise ApiError("请输入搜索关键词。", "missing_keyword")

        preset = preset_name if preset_name in TYPE_PRESETS else "all"
        types = TYPE_PRESETS[preset]
        type_param = ",".join(types)
        merged_by_type: Dict[str, List[Dict[str, Any]]] = {}
        url_set = set()
        success_count = 0
        failed_count = 0
        failed_terms: List[str] = []

        for search_term in self.build_search_terms(term):
            try:
                data = self.request_json(JHSJ_API, {"type": type_param, "name": search_term})
                success_count += 1
            except ApiError as exc:
                failed_count += 1
                failed_terms.append(search_term)
                if exc.error_type == "rate_limited":
                    break
                continue

            if not self.is_code(data, 0):
                failed_count += 1
                failed_terms.append(search_term)
                continue

            payload = data.get("data") or {}
            raw_merged = payload.get("merged_by_type") if isinstance(payload, dict) else {}
            if not isinstance(raw_merged, dict):
                continue

            for resource_type, items in raw_merged.items():
                if not isinstance(items, list):
                    continue
                target = merged_by_type.setdefault(resource_type, [])
                for item in items:
                    normalized = self.normalize_resource_item(item, resource_type)
                    url = normalized.get("url")
                    if not url or url in url_set:
                        continue
                    url_set.add(url)
                    normalized["_searchTerm"] = search_term
                    target.append(normalized)
                    if len(url_set) >= limit:
                        break
                if len(url_set) >= limit:
                    break
            if len(url_set) >= limit:
                break

        for resource_type, items in merged_by_type.items():
            items.sort(
                key=lambda item: (
                    item.get("_searchTerm") != term,
                    -(len(str(item.get("name") or ""))),
                )
            )

        type_list = [key for key, value in merged_by_type.items() if value]
        total = sum(len(merged_by_type[key]) for key in type_list)
        return {
            "mergedByType": merged_by_type,
            "total": total,
            "typeList": type_list,
            "apiStatus": {
                "successCount": success_count,
                "failedCount": failed_count,
                "failedTerms": failed_terms,
            },
        }

    def fetch_and_merge_data_stable(self, keyword: str, preset_name: str = "all", attempts: int = 3) -> Dict[str, Any]:
        last_result: Optional[Dict[str, Any]] = None
        last_error: Optional[Exception] = None
        safe_preset = preset_name if preset_name in TYPE_PRESETS else "all"

        for index in range(max(1, attempts)):
            try:
                result = self.fetch_and_merge_data(keyword, safe_preset)
                last_result = result
                if result.get("total", 0) > 0 and result.get("typeList"):
                    result["effectivePreset"] = safe_preset
                    result["retryCount"] = index
                    return result
            except Exception as exc:
                last_error = exc
            if index < attempts - 1:
                time.sleep(0.7 * (index + 1))

        if last_result is not None:
            last_result["effectivePreset"] = safe_preset
            last_result["retryCount"] = max(0, attempts - 1)
            return last_result
        if last_error:
            raise last_error
        return {"mergedByType": {}, "total": 0, "typeList": [], "effectivePreset": safe_preset, "retryCount": 0}

    def get_daily_resources(self) -> Dict[str, Any]:
        all_items: List[Dict[str, Any]] = []
        errors: List[str] = []
        for source in ("baidu", "quark"):
            try:
                data = self.request_json(f"{YINGSHI_API}?{source}", use_cache=False)
            except ApiError as exc:
                errors.append(f"{source}: {exc}")
                continue

            if self.is_code(data, 1, 200) and isinstance(data.get("data"), list):
                for item in data["data"]:
                    normalized = self.normalize_resource_item(
                        {
                            **item,
                            "url": item.get("viewlink") or item.get("url") or "",
                            "type": source,
                        },
                        source,
                    )
                    normalized["_source"] = source
                    normalized["addtime"] = item.get("addtime", "")
                    all_items.append(normalized)
            else:
                errors.append(f"{source}: {data.get('msg', '接口未返回有效数据')}")

        all_items.sort(key=lambda item: str(item.get("addtime") or ""), reverse=True)
        return {"code": 200 if all_items else 500, "msg": "; ".join(errors) if errors and not all_items else "success", "data": all_items, "count": len(all_items)}

    def get_short_drama_rank(self) -> Dict[str, Any]:
        return self.request_json(SHORTDRAMA_RANK_API, use_cache=False)

    def get_vtquark_rank(self, tag: str = "短剧") -> Dict[str, Any]:
        return self.request_json(VTQUARK_API, {"tag": tag}, use_cache=False)

    @staticmethod
    def flatten_merged_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        merged = result.get("mergedByType") or {}
        for resource_type in result.get("typeList") or list(merged.keys()):
            for item in merged.get(resource_type, []):
                rows.append(ApiClient.normalize_resource_item(item, resource_type))
        return rows

    @staticmethod
    def build_limited_preview_data(merged_by_type: Dict[str, List[Dict[str, Any]]], type_list: List[str], limit: int = 5) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        preview_data: Dict[str, List[Dict[str, Any]]] = {}
        cursors: Dict[str, int] = {}
        ordered_types = [item for item in PREVIEW_TYPE_ORDER if item in type_list] + [item for item in type_list if item not in PREVIEW_TYPE_ORDER]
        preview_count = 0
        has_more = True

        while preview_count < limit and has_more:
            has_more = False
            for resource_type in ordered_types:
                if preview_count >= limit:
                    break
                records = merged_by_type.get(resource_type) or []
                cursor = cursors.get(resource_type, 0)
                if cursor >= len(records):
                    continue
                cleaned = dict(ApiClient.normalize_resource_item(records[cursor], resource_type))
                cleaned.pop("_searchTerm", None)
                preview_data.setdefault(resource_type, []).append(cleaned)
                cursors[resource_type] = cursor + 1
                preview_count += 1
                has_more = True
        return preview_data, preview_count

    @staticmethod
    def build_online_api_url(keyword: str, preset_name: str = "all") -> str:
        term = ApiClient.normalize_search_keyword(keyword)
        if not term:
            return ""
        preset = preset_name if preset_name in TYPE_PRESETS else "all"
        return f"{ONLINE_PAGE_URL}?{urlencode({'q': term, 'from': preset, 'format': 'json'})}"

    @staticmethod
    def build_qrcode_url(text: str, size: int = 220) -> str:
        return f"{QRCODE_API}?{urlencode({'frame': 1, 'e': 'L', 'text': text or '', 'size': size})}"

    def get_qrcode_image_bytes(self, text: str, size: int = 260) -> bytes:
        url = self.build_qrcode_url(text, size)
        self._wait_interval()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content
