import hashlib
import html
import re
from typing import Any, Dict, Iterable, List
from urllib.parse import parse_qs, urlparse

import requests

from services.constants import SOURCE_ORDER, TYPE_LABELS, TYPE_PRESETS


def normalize_search_keyword(keyword: Any) -> str:
    # 中文：榜单标题和 URL 参数可能包含 HTML 实体、隐藏字符或连续空格，统一清洗能让搜索命中更稳定。
    # English: Rank titles and URL parameters may contain HTML entities, hidden characters, or repeated spaces, so normalization keeps searches stable.
    text = html.unescape(str(keyword or ""))
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    text = text.replace("\u00A0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_search_terms(raw_input: Any) -> List[str]:
    # 中文：docs/index.html 会先搜完整关键词，再用空格拆分补搜；服务端版保留这个顺序以提高长标题命中率。
    # English: docs/index.html searches the full keyword first and split terms next; the server version preserves that order to improve long-title recall.
    keyword = normalize_search_keyword(raw_input)
    if not keyword:
        return []

    parts = [part for part in keyword.split(" ") if part]
    terms = {keyword}
    if len(parts) > 1:
        terms.update(parts)

    return sorted(terms, key=lambda value: (0 if value == keyword else 1, -len(value)))


def protect_pwd_in_json_text(text: str) -> str:
    # 中文：部分接口返回裸 pwd 值（如 "pwd":32e7），先补引号才能避免 JSON 解析失败或科学计数法误转。
    # English: Some API responses expose bare pwd values (for example "pwd":32e7), so quoting them prevents JSON failures or scientific-notation conversion.
    if not isinstance(text, str):
        return text
    return re.sub(
        r'("pwd"\s*:\s*)(?!")(?!(?:null|true|false)\b)([A-Za-z0-9+\-.]{1,32})(?=\s*[,}\]])',
        lambda match: f'{match.group(1)}"{match.group(2)}"',
        text,
        flags=re.IGNORECASE,
    )


def extract_pwd_from_link(link: Any) -> str:
    # 中文：百度网盘真实提取码经常保留在链接参数中，优先从链接恢复可以规避服务端字段被误解析的问题。
    # English: BaiduNetdisk extraction codes are often preserved in URL parameters, so link-first recovery avoids server-side field parsing issues.
    if not link:
        return ""

    text = str(link).strip()
    try:
        parsed = urlparse(text)
        query = parse_qs(parsed.query)
        pwd_values = query.get("pwd") or query.get("PWD")
        if pwd_values and str(pwd_values[0]).strip():
            return str(pwd_values[0]).strip()
    except Exception:
        pass

    match = re.search(r"[?&]pwd=([^&#]+)", text, flags=re.IGNORECASE)
    if match:
        try:
            return requests.utils.unquote(match.group(1).replace("+", "%20")).strip()
        except Exception:
            return match.group(1).strip()
    return ""


def format_pwd(pwd: Any) -> str:
    # 中文：提取码必须作为字符串保存，不能 Number 化，否则 32e7 会被错误转换成 320000000。
    # English: Extraction codes must stay as strings, because numeric conversion would wrongly turn 32e7 into 320000000.
    if pwd is None:
        return ""
    return str(pwd).strip()


def normalize_resource_item(item: Dict[str, Any]) -> Dict[str, Any]:
    # 中文：统一入口字段名和提取码字段，后续搜索结果、收藏、JSON 预览都依赖同一份干净数据。
    # English: Normalizing link and password fields once lets results, favorites, and JSON preview share the same clean data.
    if not isinstance(item, dict):
        return {}

    fixed = dict(item)
    link = fixed.get("url") or fixed.get("viewlink") or fixed.get("link") or fixed.get("share_url") or fixed.get("shareUrl") or ""
    fixed["url"] = str(link or "").strip()
    pwd_from_link = extract_pwd_from_link(link)
    fixed["pwd"] = pwd_from_link if pwd_from_link else format_pwd(fixed.get("pwd") or fixed.get("password") or fixed.get("pass") or fixed.get("code"))
    fixed["name"] = html.unescape(str(fixed.get("name") or fixed.get("title") or fixed.get("content_title") or "未知资源")).strip()
    return fixed


def normalize_pwd_fields_deep(value: Any) -> Any:
    # 中文：API 模式需要输出完整嵌套 JSON，递归修正可保证所有层级的 pwd 都保持正确字符串。
    # English: API mode returns nested JSON, and recursive normalization keeps pwd fields correct at every level.
    if isinstance(value, list):
        return [normalize_pwd_fields_deep(item) for item in value]

    if isinstance(value, dict):
        fixed = {key: normalize_pwd_fields_deep(item) for key, item in value.items()}
        link = fixed.get("url") or fixed.get("viewlink") or fixed.get("link") or fixed.get("share_url") or fixed.get("shareUrl") or ""
        pwd_from_link = extract_pwd_from_link(link)
        if pwd_from_link:
            fixed["pwd"] = pwd_from_link
        elif "pwd" in fixed:
            fixed["pwd"] = format_pwd(fixed.get("pwd"))
        return fixed

    return value


def parse_api_json_safely(text: str) -> Dict[str, Any]:
    # 中文：保持与 docs/index.html 相同的“两段式解析”：先修复原始文本，再递归修复解析后的 pwd 字段。
    # English: This follows docs/index.html's two-step parsing: repair raw text first, then recursively repair pwd fields after parsing.
    import json

    safe_text = protect_pwd_in_json_text(text)
    data = json.loads(safe_text)
    return normalize_pwd_fields_deep(data)


def source_label(type_name: str) -> str:
    return TYPE_LABELS.get(type_name, type_name or "未知来源")


def get_source_class(type_name: str) -> str:
    if type_name == "baidu":
        return "source-baidu"
    if type_name == "quark":
        return "source-quark"
    return "source-default"


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def make_resource_id(link: Any) -> str:
    raw = str(link or "").strip()
    return hashlib.sha1(raw.encode("utf-8")).hexdigest() if raw else ""


def ordered_types(type_list: Iterable[str]) -> List[str]:
    safe_list = list(type_list or [])
    return [item for item in SOURCE_ORDER if item in safe_list] + [item for item in safe_list if item not in SOURCE_ORDER]


def valid_preset_name(preset_name: str) -> str:
    return preset_name if preset_name in TYPE_PRESETS else "all"
