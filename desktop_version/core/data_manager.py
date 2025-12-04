import json
import os
from datetime import datetime

# 修改缓存过期时间（秒）
CACHE_EXPIRE_TIME = 3600  # 1小时


class DataManager:
    def __init__(self):
        self.data_dir = self.get_data_dir()
        self.history_file = os.path.join(self.data_dir, "search_history.json")
        self.cache_file = os.path.join(self.data_dir, "search_cache.json")

        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)

    def get_data_dir(self):
        """获取数据存储目录"""
        if os.name == 'nt':  # Windows
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(base_dir, 'ShortDramaSearch')
        else:  # macOS/Linux
            return os.path.join(os.path.expanduser('~'), '.shortdramasearch')

    def save_search_history(self, keyword, results):
        """保存搜索历史"""
        history = self.load_search_history()

        entry = {
            "keyword": keyword,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results.get("data", [])),
            "results": results
        }

        history.insert(0, entry)
        # 只保留最近50条记录
        history = history[:50]

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_search_history(self):
        """加载搜索历史"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def cache_results(self, keyword, results):
        """缓存搜索结果"""
        cache = self.load_cache()
        cache[keyword] = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    def load_cache(self):
        """加载缓存"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_cached_results(self, keyword):
        """获取缓存的搜索结果"""
        cache = self.load_cache()
        if keyword in cache:
            # 检查缓存是否过期（1小时）
            cached_time = datetime.fromisoformat(cache[keyword]["timestamp"])
            if (datetime.now() - cached_time).total_seconds() < 3600:
                return cache[keyword]["results"]
        return None
