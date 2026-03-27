import requests
import json
from typing import Optional, Dict, Any, List

BASE_API = "https://api.kuleu.com/api"

API_URLS = {
    "短剧搜索": f"{BASE_API}/action",
    "百度短剧": f"{BASE_API}/bddj",
    "聚合资源搜索": f"{BASE_API}/jhsj",
    "每日影视资源": f"{BASE_API}/yingshi",
    "短剧热度榜": f"{BASE_API}/shortdramarank",
    "夸克热搜": f"{BASE_API}/vtquark",
}

RESOURCE_TYPE_MAP = {
    "夸克网盘": "quark",
    "百度网盘": "baidu",
    "阿里云盘": "aliyun",
    "天翼云盘": "tianyi",
    "UC网盘": "uc",
    "移动云盘": "yidong",
    "115网盘": "115",
    "PikPak": "pikpak",
    "迅雷网盘": "xunlei",
    "123网盘": "123",
    "磁力链接": "magnet",
    "电驴链接": "ed2k",
}


class ApiClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def _request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """统一请求处理"""
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            # 尝试解析JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"code": 500, "msg": "API返回数据格式错误"}

        except requests.exceptions.Timeout:
            return {"code": 408, "msg": "请求超时，请检查网络连接"}
        except requests.exceptions.ConnectionError:
            return {"code": 503, "msg": "网络连接失败"}
        except requests.exceptions.RequestException as e:
            return {"code": 500, "msg": f"请求失败: {str(e)}"}

    def search_drama(
        self, keyword: str, search_type: str = "短剧搜索"
    ) -> Dict[str, Any]:
        """短剧搜索 / 百度短剧"""
        if search_type not in ("短剧搜索", "百度短剧"):
            return {"code": 400, "msg": f"不支持的搜索类型: {search_type}"}

        url = API_URLS[search_type]
        params = {"text": keyword}
        result = self._request(url, params)

        # 统一成功状态码为200
        if result.get("code") == 200:
            return result
        return result

    def search_aggregate(self, keyword: str, sub_type: str = "quark") -> Dict[str, Any]:
        """聚合资源搜索"""
        url = API_URLS["聚合资源搜索"]
        params = {"type": sub_type, "name": keyword}
        result = self._request(url, params)

        # 聚合资源搜索成功码为0
        if result.get("code") == 0:
            data = result.get("data", {})

            # 提取特定类型的数据
            items = []
            if isinstance(data, dict):
                # 尝试从merged_by_type中获取
                merged = data.get("merged_by_type", {})
                items = merged.get(sub_type, [])

                # 如果没有，尝试直接从type字段获取
                if not items:
                    items = data.get(sub_type, [])

            return {"code": 200, "msg": "搜索成功", "data": items, "count": len(items)}

        return result

    def get_daily_resources(self) -> Dict[str, Any]:
        """每日影视资源（合并百度和夸克源）"""
        base_url = API_URLS["每日影视资源"]
        all_items: List[Dict] = []
        errors: List[str] = []

        sources = [("百度", f"{base_url}?baidu"), ("夸克", f"{base_url}?quark")]

        for name, url in sources:
            result = self._request(url)

            # 每日影视成功码可能是200或1
            if result.get("code") in (200, 1):
                data = result.get("data", [])
                # 添加来源标记
                for item in data:
                    item["source"] = name
                all_items.extend(data)
            else:
                errors.append(f"{name}源失败: {result.get('msg', '未知错误')}")

        if not all_items and errors:
            return {"code": 500, "msg": "; ".join(errors)}

        return {
            "code": 200,
            "msg": "获取成功",
            "data": all_items,
            "count": len(all_items),
        }

    def get_drama_rank(self) -> Dict[str, Any]:
        """短剧热度榜"""
        url = API_URLS["短剧热度榜"]
        result = self._request(url)

        if result.get("code") == 200:
            return result
        return result

    def get_quark_hot(self, tag: str = "短剧") -> Dict[str, Any]:
        """夸克热搜"""
        url = API_URLS["夸克热搜"]
        params = {"tag": tag}
        return self._request(url, params)
