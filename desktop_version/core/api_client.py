import requests
import json
from urllib.parse import urlencode


class ApiClient:
    def __init__(self):
        self.base_url = "https://api.kuleu.com/api/bddj"  # 短剧搜索API地址
        self.timeout = 60  # 请求超时时间，单位秒

    def search_drama(self, keyword):
        """搜索短剧"""
        params = {
            "text": keyword
        }  # 使用字典构建搜索参数

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "code": 500,
                "msg": f"网络请求失败: {str(e)}",
                "data": []
            }
        except json.JSONDecodeError:
            return {
                "code": 500,
                "msg": "API返回数据格式错误",
                "data": []
            }