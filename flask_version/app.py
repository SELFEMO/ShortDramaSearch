from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# ==================== API 配置 ====================
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
    "quark": "quark",
    "baidu": "baidu",
    "aliyun": "aliyun",
    "tianyi": "tianyi",
    "uc": "uc",
    "yidong": "yidong",
    "115": "115",
    "pikpak": "pikpak",
    "xunlei": "xunlei",
    "123": "123",
    "magnet": "magnet",
    "ed2k": "ed2k",
}


# ==================== 路由 ====================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def unified_search():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    search_type = data.get("type", "短剧搜索")
    text = data.get("text", "").strip()
    sub_type = data.get("sub_type", "quark")

    print(f"\n=== 收到请求: {search_type} | 关键词: {text} ===")

    # 1. 搜索类
    if search_type in ("短剧搜索", "百度短剧", "聚合资源搜索"):
        return handle_search_type(search_type, text, sub_type)

    # 2. 榜单类
    elif search_type == "每日影视资源":
        return handle_daily_resources()
    elif search_type == "短剧热度榜":
        return handle_rank("短剧热度榜")
    elif search_type == "夸克热搜":
        return handle_rank("夸克热搜", tag="短剧")
    else:
        return jsonify({"code": 400, "msg": "未知的搜索类型"})


# ==================== 带重试的请求函数 ====================
def safe_api_request(url, params=None, max_retries=2, timeout=15):
    """
    安全的 API 请求函数，带重试机制
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()

            # 检查是否返回了有效内容
            if not resp.text or resp.text.strip() == "":
                raise ValueError("API 返回空内容")

            # 尝试解析 JSON
            result = resp.json()
            return result, None

        except requests.exceptions.Timeout:
            last_error = f"请求超时，已重试 {attempt + 1} 次"
            print(f"⚠️ 超时重试 ({attempt + 1}/{max_retries}): {url}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待1秒后重试
            continue

        except requests.exceptions.RequestException as e:
            last_error = f"网络请求失败: {str(e)}"
            break

        except ValueError as e:
            last_error = f"API 返回格式错误: {str(e)}"
            break

        except Exception as e:
            last_error = f"未知错误: {str(e)}"
            break

    return None, last_error


# ==================== 搜索类处理 ====================
def handle_search_type(search_type, text, sub_type):
    if not text:
        return jsonify({"code": 400, "msg": "请输入搜索关键词"})

    if search_type in ("短剧搜索", "百度短剧"):
        params = {"text": text}
        api_url = API_URLS[search_type]
        return call_kule_api(api_url, params, expect_list=True)

    elif search_type == "聚合资源搜索":
        rtype = RESOURCE_TYPE_MAP.get(sub_type, "quark")
        params = {"type": rtype, "name": text}
        api_url = API_URLS["聚合资源搜索"]
        return call_kule_api(
            api_url, params, expect_list=False, aggregate=True, rtype=rtype
        )


# ==================== 榜单类处理 ====================
def handle_daily_resources():
    """每日影视资源：合并 baidu / quark"""
    base_url = API_URLS["每日影视资源"]
    all_items = []
    errors = []

    sources = [
        ("百度", f"{base_url}?baidu"),
        ("夸克", f"{base_url}?quark"),
    ]

    for name, url in sources:
        result, error = safe_api_request(url)

        if error:
            errors.append(f"{name}源: {error}")
            continue

        if result.get("code") in (200, 1):
            data = result.get("data", [])
            for item in data:
                item["source"] = name
            all_items.extend(data)
        else:
            errors.append(f"{name}源返回错误: {result.get('msg')}")

    if not all_items and errors:
        return jsonify({"code": 500, "msg": "; ".join(errors)})

    return jsonify(
        {"code": 200, "msg": "获取成功", "data": all_items, "count": len(all_items)}
    )


def handle_rank(api_name, tag=None):
    """短剧热度榜 / 夸克热搜"""
    api_url = API_URLS[api_name]
    params = {"tag": tag} if tag else None

    result, error = safe_api_request(api_url, params)

    if error:
        return jsonify({"code": 500, "msg": error})

    code = result.get("code")
    if code not in (200, 0, 1):
        return jsonify({"code": code, "msg": result.get("msg", "API错误")})

    return jsonify(
        {
            "code": 200,
            "msg": "成功",
            "data": result.get("data", []),
            "count": len(result.get("data", [])),
        }
    )


# ==================== 统一调用酷乐 API ====================
def call_kule_api(url, params=None, expect_list=True, aggregate=False, rtype=None):
    result, error = safe_api_request(url, params, max_retries=2, timeout=15)

    if error:
        return jsonify({"code": 500, "msg": error})

    code = result.get("code")
    print(f"API响应 ({url}): Code={code}, Msg={result.get('msg', 'N/A')}")

    # 兼容多种成功码
    if code not in (200, 0, 1):
        return jsonify({"code": code, "msg": result.get("msg", "API错误")})

    # 解析数据
    raw_data = result.get("data", [])

    if aggregate and rtype:
        items = []
        if isinstance(raw_data, dict):
            merged = raw_data.get("merged_by_type", {})
            items = merged.get(rtype, [])
            if not items:
                items = raw_data.get(rtype, [])
        else:
            items = raw_data if isinstance(raw_data, list) else []
    else:
        items = raw_data if expect_list else raw_data

    return jsonify(
        {
            "code": 200,
            "msg": "成功",
            "data": items,
            "count": len(items) if isinstance(items, list) else 0,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
