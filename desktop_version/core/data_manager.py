import os
import json
from typing import Dict, List, Any


class DataManager:
    def __init__(self):
        self.app_data_dir = os.path.join(os.path.expanduser("~"), ".short_drama_search")
        os.makedirs(self.app_data_dir, exist_ok=True)

        self.history_file = os.path.join(self.app_data_dir, "history.json")
        self.cache_file = os.path.join(self.app_data_dir, "cache.json")

    def save_search_history(self, keyword: str, results: List[Dict]):
        """保存搜索历史"""
        history = self.load_search_history()

        # 去重并添加新记录
        history = [h for h in history if h["keyword"] != keyword]
        history.insert(
            0,
            {
                "keyword": keyword,
                "count": len(results),
                "timestamp": (
                    str(os.path.getmtime(self.history_file))
                    if os.path.exists(self.history_file)
                    else "0"
                ),
            },
        )

        # 只保留最近50条
        history = history[:50]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_search_history(self) -> List[Dict]:
        """加载搜索历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def cache_results(self, key: str, results: List[Dict]):
        """缓存搜索结果"""
        cache = self.load_cache()
        cache[key] = results

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)

    def get_cached_results(self, key: str) -> List[Dict]:
        """获取缓存的结果"""
        cache = self.load_cache()
        return cache.get(key, [])

    def load_cache(self) -> Dict[str, List[Dict]]:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
