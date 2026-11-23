from __future__ import annotations

import json
import os
import re
import threading
import time
from collections import OrderedDict, deque
from copy import deepcopy
from typing import Any
from urllib.parse import parse_qs, urlparse

BASE_API = os.environ.get("KULEU_API_BASE", "https://api.kuleu.com/api").rstrip("/")

TYPE_PRESETS: dict[str, list[str]] = {
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

SOURCE_ALIASES: dict[str, str] = {
    "yidong": "mobile",
    "移动": "mobile",
    "百度": "baidu",
    "夸克": "quark",
    "阿里": "aliyun",
    "天翼": "tianyi",
    "迅雷": "xunlei",
}

KULEU_ENDPOINTS: dict[str, str] = {
    "jhsj": f"{BASE_API}/jhsj",
    "yingshi": f"{BASE_API}/yingshi",
    "shortdramarank": f"{BASE_API}/shortdramarank",
    "vtquark": f"{BASE_API}/vtquark",
    "ico": f"{BASE_API}/ico",
    "qrcode": f"{BASE_API}/qrcode",
}

ALLOWED_URL_SCHEMES: frozenset[str] = frozenset({"http", "https", "magnet", "ed2k"})

ALLOWED_ICO_HOSTS: frozenset[str] = frozenset(
    {
        "www.kuleu.com",
        "kuleu.com",
        "pan.baidu.com",
        "pan.quark.cn",
        "www.aliyundrive.com",
        "www.alipan.com",
        "cloud.189.cn",
        "drive.uc.cn",
        "yun.139.com",
        "115.com",
        "mypikpak.com",
        "pan.xunlei.com",
        "www.123pan.com",
        "www.123684.com",
        "www.123865.com",
    }
)

PWD_VALUE_RE = re.compile(
    r'("pwd"\s*:\s*)(?!")(?!(?:null|true|false)\b)([A-Za-z0-9+\-.]{1,32})(?=\s*[,}\]])',
    re.IGNORECASE,
)
HIDDEN_CHAR_RE = re.compile(r"[\u200B-\u200D\uFEFF]")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1F\x7F]")
SPACE_RE = re.compile(r"\s+")


def sanitize_url(raw_url: Any) -> str:
    """Validate URL scheme against allowlist (http/https/magnet/ed2k)."""
    if raw_url is None:
        return ""
    text = CONTROL_CHAR_RE.sub("", str(raw_url)).strip()
    if not text or len(text) > 2048:
        return ""

    try:
        parsed = urlparse(text)
    except ValueError:
        return ""

    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_URL_SCHEMES:
        return ""

    if scheme in {"http", "https"} and not parsed.netloc:
        return ""

    return text


def sanitize_ico_target(raw_url: Any) -> str:
    """Restrict /api/ico proxy target to known netdisk / site hosts."""
    safe = sanitize_url(raw_url)
    if not safe:
        return ""
    parsed = urlparse(safe)
    if parsed.scheme.lower() not in {"http", "https"}:
        return ""
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_ICO_HOSTS:
        return ""
    return f"{parsed.scheme.lower()}://{host}/"


def sanitize_csv_cell(value: Any) -> str:
    """Prevent CSV formula injection by prefixing dangerous leading characters."""
    text = "" if value is None else str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{text}"
    return text


def normalize_keyword(value: Any, max_length: int = 80) -> str:
    if value is None:
        return ""
    text = str(value).replace("\u00A0", " ")
    text = HIDDEN_CHAR_RE.sub("", text)
    text = CONTROL_CHAR_RE.sub("", text)
    normalized = SPACE_RE.sub(" ", text).strip()
    if max_length > 0 and len(normalized) > max_length:
        normalized = normalized[:max_length].strip()
    return normalized


def normalize_preset_name(value: Any) -> str:
    raw = normalize_keyword(value or "all", max_length=32)
    mapped = SOURCE_ALIASES.get(raw, raw)
    return mapped if mapped in TYPE_PRESETS else "all"


def build_search_terms(raw_input: str, max_terms: int = 3) -> list[str]:
    keyword = normalize_keyword(raw_input)
    if not keyword:
        return []

    parts = [part for part in keyword.split(" ") if part]
    terms = {keyword, *parts} if len(parts) > 1 else {keyword}
    ordered = sorted(terms, key=lambda term: (term != keyword, -len(term)))
    return ordered[: max(1, max_terms)]


def protect_pwd_in_json_text(text: str) -> str:
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
    except ValueError:
        pass

    match = re.search(r"[?&]pwd=([^&#]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def normalize_resource_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item

    fixed = dict(item)
    raw_link = (
        fixed.get("url")
        or fixed.get("viewlink")
        or fixed.get("link")
        or fixed.get("share_url")
        or fixed.get("shareUrl")
        or ""
    )
    safe_link = sanitize_url(raw_link)
    for key in ("url", "viewlink", "link", "share_url", "shareUrl"):
        if key in fixed and fixed[key]:
            fixed[key] = sanitize_url(fixed[key])

    pwd_from_link = extract_pwd_from_link(safe_link or raw_link)
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


def parse_api_dict_safely(text: str) -> dict[str, Any]:
    parsed = parse_api_text_safely(text)
    if not isinstance(parsed, dict):
        raise ValueError("API 返回格式非 JSON 对象")
    return parsed


class ThreadSafeTTLCache:
    """Bounded, thread-safe LRU+TTL cache using stdlib only."""

    def __init__(self, maxsize: int = 512, ttl: float = 60.0) -> None:
        self.maxsize = max(1, int(maxsize))
        self.ttl = max(0.0, float(ttl))
        self._lock = threading.RLock()
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, payload = entry
            if now >= expires_at:
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return deepcopy(payload)

    def set(self, key: str, payload: Any, ttl: float | None = None) -> None:
        ttl_val = self.ttl if ttl is None else max(0.0, float(ttl))
        expires_at = time.monotonic() + ttl_val
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (expires_at, deepcopy(payload))
            while len(self._store) > self.maxsize:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


class SlidingWindowRateLimiter:
    """Thread-safe per-key sliding-window rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        self.max_requests = max(1, int(max_requests))
        self.window_seconds = max(1.0, float(window_seconds))
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = {}

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = deque()
                self._buckets[key] = bucket
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                return False, retry_after
            bucket.append(now)
            # Evict stale empty/old buckets occasionally to bound memory
            if len(self._buckets) > 4096:
                stale_keys = [k for k, q in self._buckets.items() if not q or q[-1] <= cutoff]
                for stale in stale_keys:
                    self._buckets.pop(stale, None)
            return True, 0
