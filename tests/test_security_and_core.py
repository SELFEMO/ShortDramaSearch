import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.kuleu_core import (  # noqa: E402
    SlidingWindowRateLimiter,
    ThreadSafeTTLCache,
    build_search_terms,
    normalize_keyword,
    normalize_resource_item,
    parse_api_dict_safely,
    sanitize_csv_cell,
    sanitize_ico_target,
    sanitize_url,
)


class SharedCoreTests(unittest.TestCase):
    def test_sanitize_url_allows_safe_schemes_only(self):
        self.assertEqual(sanitize_url("https://pan.quark.cn/s/abc?pwd=1234"), "https://pan.quark.cn/s/abc?pwd=1234")
        self.assertEqual(sanitize_url("magnet:?xt=urn:btih:12345"), "magnet:?xt=urn:btih:12345")
        self.assertEqual(sanitize_url("ed2k://|file|test|123|abc|/"), "ed2k://|file|test|123|abc|/")
        self.assertEqual(sanitize_url("javascript:alert(1)"), "")
        self.assertEqual(sanitize_url("file:///etc/passwd"), "")
        self.assertEqual(sanitize_url("smb://evil/share"), "")
        self.assertEqual(sanitize_url("https://"), "")

    def test_sanitize_ico_target_allowlist(self):
        self.assertEqual(sanitize_ico_target("https://pan.baidu.com/s/123"), "https://pan.baidu.com/")
        self.assertEqual(sanitize_ico_target("http://127.0.0.1:8080/admin"), "")
        self.assertEqual(sanitize_ico_target("https://169.254.169.254/latest/meta-data/"), "")

    def test_sanitize_csv_cell(self):
        self.assertEqual(sanitize_csv_cell("=CMD()"), "'=CMD()")
        self.assertEqual(sanitize_csv_cell("+1+1"), "'+1+1")
        self.assertEqual(sanitize_csv_cell("@SUM(A1)"), "'@SUM(A1)")
        self.assertEqual(sanitize_csv_cell("正常短剧标题"), "正常短剧标题")

    def test_build_search_terms_bounded(self):
        terms = build_search_terms("a b c d e f g", max_terms=3)
        self.assertEqual(len(terms), 3)
        self.assertEqual(terms[0], "a b c d e f g")
        self.assertEqual(len(normalize_keyword("x" * 120, max_length=80)), 80)

    def test_parse_api_dict_safely_and_pwd_protection(self):
        raw = '{"code": 200, "data": [{"name": "测试", "url": "https://pan.quark.cn/s/1?pwd=32e7", "pwd": 32e7}]}'
        parsed = parse_api_dict_safely(raw)
        self.assertEqual(parsed["data"][0]["pwd"], "32e7")
        with self.assertRaises(ValueError):
            parse_api_dict_safely('["not", "a", "dict"]')

    def test_ttl_cache_bounds_and_expiry(self):
        cache = ThreadSafeTTLCache(maxsize=2, ttl=0.1)
        cache.set("a", {"v": 1})
        cache.set("b", {"v": 2})
        cache.set("c", {"v": 3})
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), {"v": 2})
        time.sleep(0.12)
        self.assertIsNone(cache.get("b"))

    def test_rate_limiter(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10.0)
        self.assertTrue(limiter.allow("1.2.3.4")[0])
        self.assertTrue(limiter.allow("1.2.3.4")[0])
        allowed, retry_after = limiter.allow("1.2.3.4")
        self.assertFalse(allowed)
        self.assertGreaterEqual(retry_after, 1)


class DesktopDataManagerTests(unittest.TestCase):
    def test_atomic_write_corrupt_backup_and_cache(self):
        sys.path.insert(0, str(REPO_ROOT / "desktop_version"))
        from core.data_manager import DataManager

        with tempfile.TemporaryDirectory() as tmpdir:
            dm = DataManager()
            dm.app_data_dir = tmpdir
            dm.history_file = str(Path(tmpdir) / "history.json")
            dm.favorites_file = str(Path(tmpdir) / "favorites.json")
            dm.broken_file = str(Path(tmpdir) / "broken_links.json")
            dm.quality_file = str(Path(tmpdir) / "quality_ratings.json")
            dm.settings_file = str(Path(tmpdir) / "settings.json")
            dm.cache_file = str(Path(tmpdir) / "cache.json")
            dm._favorites_cache = None
            dm._favorites_id_set = None

            # Corrupt file should be backed up instead of silently wiped
            Path(dm.history_file).write_text("{broken json", encoding="utf-8")
            self.assertEqual(dm.load_search_history(), [])
            backups = list(Path(tmpdir).glob("history.json.corrupt.*.json"))
            self.assertEqual(len(backups), 1)

            # Toggle favorite & O(1) lookup
            res = {"name": "短剧A", "url": "https://pan.quark.cn/s/xyz", "pwd": "abcd"}
            self.assertTrue(dm.toggle_favorite(res))
            self.assertTrue(dm.is_favorited("https://pan.quark.cn/s/xyz"))
            # Import rejects javascript: URL
            dm.import_favorites([{"name": "bad", "url": "javascript:alert(1)"}, res])
            self.assertEqual(len(dm.get_favorites()), 1)


class DocsIntegrityTests(unittest.TestCase):
    def test_docs_inlined_and_hardened(self):
        for name in ("index.html", "neo.html", "console.html"):
            html = (REPO_ROOT / "docs" / name).read_text(encoding="utf-8")
            self.assertEqual(html.count("<style>"), 1, name)
            self.assertEqual(html.count("<script>"), 2, name)
            self.assertNotIn("user-scalable=no", html, name)
            self.assertNotIn("/cf-fonts/", html, name)
            self.assertNotIn("beacon.min.js", html, name)
            self.assertNotIn("openQrModal('${escapeHtml", html, name)
            self.assertIn("function sanitizeUrl(", html, name)


if __name__ == "__main__":
    unittest.main()
