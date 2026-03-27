import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="短剧 / 影视资源聚合搜索",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== 兼容旧版本 Streamlit 的链接按钮 ====================
def create_link_button(link_text, url):
    """
    创建链接按钮（兼容旧版本 Streamlit）
    优先使用 st.link_button（Streamlit >= 1.11.0），否则用 HTML 按钮替代
    """
    try:
        import streamlit as st_test

        if hasattr(st_test, "link_button"):
            st.link_button(link_text, url)
            return
    except Exception:
        pass

    button_html = f"""
    <a href="{url}" target="_blank">
        <button style="
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
            width: 100%;
        ">
            {link_text}
        </button>
    </a>
    """
    st.markdown(button_html, unsafe_allow_html=True)


# ==================== 侧边栏使用说明 ====================
with st.sidebar:
    st.header("使用说明")
    st.markdown(
        """
- **搜索类功能**：
  - 短剧搜索 / 百度短剧 / 聚合资源搜索
  - 需输入关键词后点击「搜索」
- **榜单类功能**：
  - 短剧热度榜 / 夸克热搜 / 每日影视资源
  - 无需输入，直接点击「加载数据」即可
- **数据导出**：
  - 支持将结果导出为 CSV 文件
"""
    )


# ==================== 标题与说明 ====================
st.title("🎬 短剧 / 影视资源 · 聚合搜索")

st.markdown(
    """
**基于酷乐API聚合资源搜索接口，支持多种网盘与磁力链接**

提示：关键词之间的空格会被用于拆分搜索，以提高命中率，无需使用引号。
"""
)

# ==================== 搜索类型选择 ====================
search_type = st.radio(
    "请选择功能类型",
    (
        "短剧搜索",
        "百度短剧",
        "聚合资源搜索",
        "每日影视资源",  # 榜单类
        "短剧热度榜",  # 榜单类
        "夸克热搜",  # 榜单类
    ),
    index=0,
)

# 聚合资源搜索：二级类型选择
sub_type = None
if search_type == "聚合资源搜索":
    sub_type = st.radio(
        "请选择资源类型",
        (
            "夸克网盘",
            "百度网盘",
            "阿里云盘",
            "天翼云盘",
            "UC网盘",
            "移动云盘",
            "115网盘",
            "PikPak",
            "迅雷网盘",
            "123网盘",
            "磁力链接",
            "电驴链接",
        ),
        index=0,
    )

# ==================== 动态显示输入框或按钮 ====================
# 判断是否为榜单类（不需要搜索框）
is_rank_type = search_type in ("短剧热度榜", "夸克热搜", "每日影视资源")

search_name = None
search_clicked = False
load_data_clicked = False

if is_rank_type:
    # 榜单类：显示"加载数据"按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        load_data_clicked = st.button(
            "📥 加载数据", use_container_width=True, key="load_rank_btn"
        )
else:
    # 搜索类：显示搜索框和"搜索"按钮
    search_name = st.text_input(
        "",
        placeholder="请输入关键词（多个关键词可用空格分隔）",
        key="search_input",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_clicked = st.button(
            "🔍 搜索", use_container_width=True, key="search_btn"
        )

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


# ==================== 通用 API 调用函数 ====================
@st.cache_data(show_spinner=False, ttl=300)
def call_api(url, params=None, timeout=10):
    """
    通用 API 调用函数
    返回: (ok: bool, data_or_msg: dict/str)
    """
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return True, r.json()
    except requests.exceptions.RequestException as e:
        return False, f"网络请求失败: {e}"
    except Exception as e:
        return False, f"解析返回数据失败: {e}"


# ==================== 结果展示通用函数 ====================
def show_json_as_table(data):
    """将 JSON 列表展示为表格"""
    if not data:
        st.warning("暂无数据")
        return

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def show_json_as_expandable_list(data, link_field="viewlink"):
    """
    将 JSON 列表以折叠方式逐条展示
    - link_field: 指定链接字段名（如 viewlink / url）
    """
    if not data:
        st.warning("暂无数据")
        return

    for i, item in enumerate(data, 1):
        # 尝试获取标题字段
        title = (
            item.get("name")
            or item.get("title")
            or item.get("content_title")
            or f"项目 {i}"
        )
        with st.expander(f"{i}. {title}", expanded=(i <= 3)):
            for key, value in item.items():
                if key == link_field:
                    create_link_button("🔗 查看资源", value)
                else:
                    st.write(f"**{key}**: {value}")


# ==================== 搜索与加载逻辑 ====================

# 1. 处理搜索类功能（需要输入关键词）
if not is_rank_type and search_clicked:
    if not search_name:
        st.warning("请输入要搜索的关键词")
    else:
        # 1.1 短剧搜索 / 百度短剧
        if search_type in ("短剧搜索", "百度短剧"):
            with st.spinner(f"正在搜索「{search_name}」，请稍候..."):
                url = API_URLS[search_type]
                params = {"text": search_name}
                ok, result = call_api(url, params)

                if not ok:
                    st.error(result)
                elif result.get("code") != 200:
                    st.error(f"搜索失败: {result.get('msg', 'API 返回错误')}")
                else:
                    dramas = result.get("data", [])
                    if not dramas:
                        st.warning(f"没有找到与「{search_name}」相关的短剧")
                    else:
                        st.success(f"找到 {len(dramas)} 个相关结果")

                        df = pd.DataFrame(dramas)

                        # 概览指标
                        st.subheader("📊 搜索结果概览")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("总结果数", len(dramas))
                        with col2:
                            now = datetime.now()
                            recent = 0
                            for d in dramas:
                                try:
                                    addtime = datetime.strptime(
                                        d["addtime"], "%Y-%m-%d %H:%M:%S"
                                    )
                                    if (now - addtime).days <= 30:
                                        recent += 1
                                except Exception:
                                    pass
                            st.metric("最近30天更新", recent)
                        with col3:
                            st.metric("搜索关键词", search_name)

                        # 详细列表
                        st.subheader("🎭 短剧列表")
                        show_json_as_expandable_list(dramas, link_field="viewlink")

                        # CSV 导出
                        st.subheader("💾 数据导出")
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="下载 CSV 格式数据",
                            data=csv,
                            file_name=f"{search_type}_{search_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                        )

        # 1.2 聚合资源搜索
        elif search_type == "聚合资源搜索":
            with st.spinner("正在聚合搜索资源，请稍候..."):
                url = API_URLS["聚合资源搜索"]
                rtype = RESOURCE_TYPE_MAP.get(sub_type, "quark")
                params = {
                    "type": rtype,
                    "name": search_name,
                }
                ok, result = call_api(url, params)

                if not ok:
                    st.error(result)
                elif result.get("code") != 0:
                    st.error(f"搜索失败: {result.get('message', 'API 返回错误')}")
                else:
                    data = result.get("data", {})
                    merged = data.get("merged_by_type", {})
                    items = merged.get(rtype, [])

                    if not items:
                        st.warning(f"没有找到「{sub_type}」相关的资源")
                    else:
                        st.success(f"找到 {len(items)} 条「{sub_type}」资源")

                        df = pd.DataFrame(items)
                        st.subheader("📊 聚合资源概览")
                        st.dataframe(df, use_container_width=True)

                        st.subheader("🎞️ 资源详情")
                        show_json_as_expandable_list(items, link_field="url")

                        st.subheader("💾 数据导出")
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="下载 CSV 格式数据",
                            data=csv,
                            file_name=f"聚合资源_{sub_type}_{search_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                        )

# 2. 处理榜单类功能（不需要搜索框，点击加载按钮触发）
elif is_rank_type and load_data_clicked:
    # 2.1 每日影视资源
    if search_type == "每日影视资源":
        with st.spinner("正在获取每日影视资源（百度 + 夸克），请稍候..."):
            base_url = "https://api.kuleu.com/api/yingshi"
            urls = [
                f"{base_url}?baidu",
                f"{base_url}?quark",
            ]

            all_items = []
            errors = []

            for api_url in urls:
                try:
                    r = requests.get(api_url, timeout=10)
                    r.raise_for_status()
                    result = r.json()

                    if result.get("code") != 1:
                        errors.append(
                            f"{api_url} 返回错误: {result.get('msg', '未知错误')}"
                        )
                    else:
                        data = result.get("data", [])
                        all_items.extend(data)
                except Exception as e:
                    errors.append(f"{api_url} 请求失败: {e}")

            if errors:
                for err in errors:
                    st.error(err)

            if not all_items:
                if not errors:
                    st.warning("暂无每日影视资源数据")
            else:
                st.success(f"今日共有 {len(all_items)} 条影视资源更新（百度 + 夸克）")

                df = pd.DataFrame(all_items)

                st.subheader("📅 每日影视资源")
                st.dataframe(df, use_container_width=True)

                st.subheader("📋 详细列表")
                show_json_as_expandable_list(all_items, link_field="viewlink")

                st.subheader("💾 数据导出")
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="下载 CSV 格式数据",
                    data=csv,
                    file_name=f"每日影视资源_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

    # 2.2 短剧热度榜
    elif search_type == "短剧热度榜":
        with st.spinner("正在获取短剧热度榜，请稍候..."):
            url = API_URLS["短剧热度榜"]
            ok, result = call_api(url)

            if not ok:
                st.error(result)
            elif result.get("code") != 200:
                st.error(f"获取失败: {result.get('msg', 'API 返回错误')}")
            else:
                hot_items = result.get("data", [])
                if not hot_items:
                    st.warning("暂无短剧热度榜数据")
                else:
                    st.subheader("🔥 短剧热度榜")
                    df = pd.DataFrame(hot_items)
                    st.dataframe(df, use_container_width=True)

                    st.subheader("📋 热度榜详情")
                    show_json_as_expandable_list(hot_items, link_field=None)

                    st.subheader("💾 数据导出")
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="下载 CSV 格式数据",
                        data=csv,
                        file_name=f"短剧热度榜_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )

    # 2.3 夸克热搜
    elif search_type == "夸克热搜":
        with st.spinner("正在获取夸克热搜榜，请稍候..."):
            url = API_URLS["夸克热搜"]
            params = {"tag": "短剧"}
            ok, result = call_api(url, params)

            if not ok:
                st.error(result)
            elif result.get("code") != 200:
                st.error(f"获取失败: {result.get('msg', 'API 返回错误')}")
            else:
                quark_items = result.get("data", [])
                if not quark_items:
                    st.warning("暂无夸克热搜数据")
                else:
                    st.subheader("🎬 夸克短剧热搜榜")
                    df = pd.DataFrame(quark_items)
                    st.dataframe(df, use_container_width=True)

                    st.subheader("📋 热搜详情")
                    show_json_as_expandable_list(quark_items, link_field="image_url")

                    st.subheader("💾 数据导出")
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="下载 CSV 格式数据",
                        data=csv,
                        file_name=f"夸克热搜_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )

# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray;'>
已适配酷乐聚合资源搜索接口所有网盘类型与磁力/电驴链接。<br>
短剧搜索系统 &copy; 2025 · 基于 Streamlit 构建
</div>
""",
    unsafe_allow_html=True,
)
