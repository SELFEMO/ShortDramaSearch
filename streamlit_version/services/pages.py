import html
import json
import time
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from services.api_client import (
    build_limited_preview_data,
    dump_json,
    fetch_and_merge_data,
    fetch_and_merge_data_stable,
    flatten_preview_links,
    load_daily_resources,
    load_shortdrama_rank,
    load_vtquark_rank,
)
from services.component_map import INDEX_FEATURES
from services.constants import GITHUB_URL, MAX_HISTORY, PRESET_LABELS, TYPE_PRESETS
from services.normalizers import make_resource_id, normalize_resource_item, normalize_search_keyword, source_label, valid_preset_name
from services.runtime import get_query_params, first_query_value, rerun, switch_page
from services.state import get_favorites, save_favorites, save_search_history, set_pending_search
from services.ui import (
    collect_current_result_links,
    footer,
    header,
    inject_page_style,
    merge_imported_favorites,
    process_imported_json,
    render_component_alignment_note,
    render_grouped_results,
    render_policy_notice,
    render_rank_tags_for_search,
    render_resource_card,
)


def render_search_page() -> None:
    header(
        "短剧 / 资源聚合搜索",
        "基于酷乐 API 聚合资源搜索接口，支持多种网盘与磁力 / 电驴链接；空格拆词、搜索历史、收藏、失效标记、质量评分与二维码均已迁移到 Streamlit 多页面结构。",
    )
    render_policy_notice()
    render_component_alignment_note("page-search")

    if st.session_state.pending_keyword:
        st.session_state.search_keyword = st.session_state.pending_keyword
        st.session_state.search_preset = st.session_state.pending_preset or "all"
        st.session_state.pending_keyword = ""
        st.session_state.pending_preset = ""

    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword = ""
    if "search_preset" not in st.session_state:
        st.session_state.search_preset = "all"

    with st.form("search_form", clear_on_submit=False):
        # 中文：搜索输入放进同一个表单后，回车会稳定触发搜索按钮，而不会误触发页面下方的导出按钮。
        # English: Keeping search inputs in one form makes Enter consistently submit search instead of accidentally triggering export buttons below.
        col1, col2 = st.columns([3, 1])
        with col1:
            keyword = st.text_input("搜索关键词", key="search_keyword", placeholder="输入短剧 / 资源名称搜索...")
        with col2:
            preset_options = list(TYPE_PRESETS.keys())
            preset = st.selectbox(
                "搜索来源",
                options=preset_options,
                index=preset_options.index(valid_preset_name(st.session_state.search_preset)),
                format_func=lambda value: PRESET_LABELS.get(value, value),
                key="search_preset",
            )
        search_clicked = st.form_submit_button("🔍 搜索", type="primary", use_container_width=True)

    with st.expander("🕘 最近搜索", expanded=bool(st.session_state.history)):
        if st.session_state.history:
            cols = st.columns(3)
            for index, term in enumerate(st.session_state.history[:12]):
                if cols[index % 3].button(term, key=f"history_{index}", use_container_width=True):
                    set_pending_search(term, preset)
                    rerun()
            export_data = {"type": "kuleu_search_history", "version": 1, "exportedAt": datetime.now().isoformat(), "data": st.session_state.history}
            st.download_button("导出搜索历史", dump_json(export_data), "kuleu-search-history.json", "application/json")
            uploaded = st.file_uploader("导入搜索历史 JSON", type=["json"], key="import_history")
            if uploaded and st.button("确认导入搜索历史"):
                imported = [normalize_search_keyword(item) for item in process_imported_json(uploaded, [])]
                st.session_state.history = [item for item in dict.fromkeys(imported) if item][:MAX_HISTORY]
                rerun()
            if st.button("清空搜索历史"):
                st.session_state.history = []
                rerun()
        else:
            st.caption("暂无搜索历史。")

    render_rank_tags_for_search()

    should_search = search_clicked or st.session_state.run_pending_search
    if should_search:
        st.session_state.run_pending_search = False
        clean_keyword = normalize_search_keyword(keyword)
        if not clean_keyword:
            st.warning("请输入搜索关键词。")
            return

        save_search_history(clean_keyword)
        with st.spinner(f"正在搜索「{clean_keyword}」..."):
            result = fetch_and_merge_data(clean_keyword, preset)
            is_rate_limited = (result.get("apiStatus") or {}).get("failedReason") == "rate_limited"
            if is_rate_limited:
                st.error("接口请求过于频繁，请稍后再试。系统不会继续自动重试，避免加重限流。")
                return
            if not result.get("total"):
                st.info("首次未命中，正在自动重试一次...")
                time.sleep(1.2)
                result = fetch_and_merge_data(clean_keyword, preset)

        st.session_state.current_results = result
        st.session_state.current_keyword = clean_keyword
        st.session_state.current_preset = preset

    current = st.session_state.get("current_results")
    if current and current.get("total"):
        render_grouped_results(current, st.session_state.current_keyword)
        links_text = collect_current_result_links()
        if links_text:
            with st.expander("复制当前结果链接", expanded=False):
                st.text_area("链接文本", value=links_text, height=260)
                st.download_button("下载当前结果链接 TXT", links_text.encode("utf-8"), "kuleu-current-links.txt", "text/plain")
    elif current:
        st.info("未找到相关结果。")
    else:
        st.info("选择“全局聚合”将一次性查询所有支持类型。")


def render_api_page() -> None:
    header("API 生成器", "配置关键词和搜索来源，一键生成 URL 参数式 API 链接，并预览最多 5 条 JSON 结果。")
    render_policy_notice()
    render_component_alignment_note("page-api")

    st.session_state.api_base_url = st.text_input(
        "当前页面根地址",
        value=st.session_state.api_base_url,
        help="本地一般为 http://localhost:8501/；部署后可改成你的 Streamlit 应用地址。",
    )
    api_keyword = st.text_input("搜索关键词", placeholder="例如：飞驰人生3 / 庆余年 / 墨雨云间", key="api_keyword")
    api_from = st.selectbox("搜索来源", options=list(TYPE_PRESETS.keys()), format_func=lambda value: PRESET_LABELS.get(value, value), key="api_from")

    clean_keyword = normalize_search_keyword(api_keyword)
    generated_url = ""
    if clean_keyword:
        base_url = st.session_state.api_base_url.rstrip("/") + "/"
        generated_url = f"{base_url}?{urlencode({'q': clean_keyword, 'from': api_from, 'format': 'json'})}"

    st.text_input("生成后的 API 链接", value=generated_url, disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        if generated_url:
            st.link_button("打开链接", generated_url, use_container_width=True)
    with col2:
        if generated_url:
            st.download_button("保存 API 链接 TXT", generated_url.encode("utf-8"), "kuleu-api-url.txt", "text/plain", use_container_width=True)

    preview_clicked = st.button("👀 预览 JSON 结果", type="primary", use_container_width=True)

    with st.expander("API 使用说明", expanded=False):
        st.markdown(
            """
- `q` / `s` / `name` / `keyword`：搜索关键词，支持中英文和空格拆词。
- `from`：搜索来源，可用 `all`、`netdisk`、`baidu`、`quark`、`aliyun`、`tianyi`、`uc`、`mobile`、`115`、`pikpak`、`xunlei`、`123`、`magnet`、`ed2k`。
- `format=json`：在 Streamlit 版本中会渲染等价 JSON 结果页，并提供下载；GitHub Pages 版本会输出纯 JSON 文本。
"""
        )

    if preview_clicked:
        if not clean_keyword:
            st.error("请先输入搜索关键词。")
            return
        with st.spinner("正在请求接口并生成预览..."):
            result = fetch_and_merge_data_stable(clean_keyword, api_from, attempts=3, delay=0.7)
        preview_data, preview_count = build_limited_preview_data(result["mergedByType"], result["typeList"], limit=5)
        payload = {
            "code": 0,
            "msg": "success",
            "keyword": clean_keyword,
            "type": result["effectivePreset"],
            "total": result["total"],
            "data": preview_data,
        }
        if preview_count:
            st.success(f"预览完成：真实结果共 {result['total']} 条，预览区展示 {preview_count} 条。")
        else:
            st.warning("接口已自动重试，但仍未搜索到结果。")
        st.json(payload)
        st.download_button("下载预览 JSON", dump_json(payload), "kuleu-api-preview.json", "application/json")
        st.markdown("### 链接快捷操作")
        for index, entry in enumerate(flatten_preview_links(preview_data, 5)):
            render_resource_card(entry["item"], entry["type"], index, prefix="api_preview", allow_favorite=True, allow_broken=True)


def render_daily_page() -> None:
    header("每日影视", "合并展示酷乐 API 每日影视资源中的百度网盘与夸克网盘数据，并支持本页关键词过滤。")
    render_policy_notice()
    render_component_alignment_note("page-daily")

    if st.button("📥 加载 / 刷新每日影视资源", type="primary", use_container_width=True) or not st.session_state.daily_data:
        with st.spinner("正在加载今日影视资源..."):
            items, errors = load_daily_resources()
            st.session_state.daily_data = items
        if errors:
            st.warning("部分每日影视接口加载失败：" + "；".join(errors))

    keyword = normalize_search_keyword(st.text_input("在今日影视资源中检索", placeholder="输入名称或链接关键词"))
    data = st.session_state.daily_data or []
    if keyword:
        low = keyword.lower()
        data = [item for item in data if low in str(item.get("name", "")).lower() or low in str(item.get("viewlink", "")).lower()]

    if not data:
        st.info("未获取到今日影视资源。")
        return

    st.metric("每日影视资源", len(data))
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in data:
        grouped.setdefault(item.get("_source") or "baidu", []).append(item)

    for source in ["baidu", "quark"]:
        items = grouped.get(source) or []
        if not items:
            continue
        with st.expander(f"{source_label(source)} · {len(items)} 条", expanded=True):
            for index, item in enumerate(items):
                fixed = normalize_resource_item({"name": item.get("name"), "url": item.get("viewlink"), "pwd": item.get("pwd")})
                if item.get("addtime"):
                    st.caption(f"更新时间：{item.get('addtime')}")
                render_resource_card(fixed, source, index, prefix=f"daily_{source}", allow_favorite=True, allow_broken=True)

    df = pd.DataFrame(data)
    st.download_button("下载每日影视 CSV", df.to_csv(index=False).encode("utf-8-sig"), f"kuleu-daily-{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    st.download_button("下载每日影视 JSON", dump_json(data), f"kuleu-daily-{datetime.now().strftime('%Y%m%d')}.json", "application/json")


def render_rank_page() -> None:
    header("热度榜", "展示短剧热度榜与夸克短剧热搜榜，点击条目即可进入聚合搜索并用全局聚合搜索该标题。")
    render_policy_notice()
    render_component_alignment_note("page-rank")

    keyword = normalize_search_keyword(st.text_input("在当前榜单中检索关键词", placeholder="输入榜单标题关键词"))
    tab1, tab2 = st.tabs(["短剧热度榜", "夸克热搜榜"])

    with tab1:
        try:
            rank_data = load_shortdrama_rank()
        except Exception as error:
            st.error(f"短剧热度榜加载失败：{error}")
            rank_data = []
        if keyword:
            rank_data = [item for item in rank_data if keyword.lower() in normalize_search_keyword(item.get("title")).lower()]
        st.metric("榜单条目", len(rank_data))
        for index, item in enumerate(rank_data):
            title = normalize_search_keyword(item.get("title"))
            if not title:
                continue
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"**{item.get('ranking', index + 1)}. {html.escape(title)}**  \n<span class='muted'>热度：{html.escape(str(item.get('hots', '')))}</span>", unsafe_allow_html=True)
            if col2.button("搜索", key=f"rank_search_{index}", use_container_width=True):
                set_pending_search(title, "all")
                switch_page("pages/search.py")

    with tab2:
        try:
            vtquark_data = load_vtquark_rank()
        except Exception as error:
            st.error(f"夸克热搜榜加载失败：{error}")
            vtquark_data = []
        if keyword:
            vtquark_data = [item for item in vtquark_data if keyword.lower() in normalize_search_keyword(item.get("content_title")).lower()]
        st.metric("榜单条目", len(vtquark_data))
        for index, item in enumerate(vtquark_data):
            title = normalize_search_keyword(item.get("content_title"))
            if not title:
                continue
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"**{item.get('content_rank', index + 1)}. {html.escape(title)}**  \n<span class='muted'>热度：{html.escape(str(item.get('hot', '')))}</span>", unsafe_allow_html=True)
            if col2.button("搜索", key=f"vt_search_{index}", use_container_width=True):
                set_pending_search(title, "all")
                switch_page("pages/search.py")


def render_favorites_page() -> None:
    header("我的收藏", "管理本会话内收藏的资源，支持筛选、导出、导入、失效标记和质量评分。")
    render_policy_notice()
    render_component_alignment_note("page-favorites")

    keyword = normalize_search_keyword(st.text_input("在收藏中搜索名称 / 来源 / 链接", placeholder="输入关键词过滤收藏"))
    favorites = get_favorites()
    if keyword:
        low = keyword.lower()
        favorites = [
            item
            for item in favorites
            if low in f"{item.get('name', '')} {item.get('link', '')} {source_label(item.get('type', ''))} {item.get('pwd', '')}".lower()
        ]

    st.metric("收藏总数", len(get_favorites()))
    st.caption(f"当前筛选：{len(favorites)} 条")

    col1, col2, col3 = st.columns(3)
    export_data = {"type": "kuleu_favorites", "version": 1, "exportedAt": datetime.now().isoformat(), "data": get_favorites()}
    col1.download_button("导出收藏", dump_json(export_data), "kuleu-favorites.json", "application/json", use_container_width=True)
    uploaded = col2.file_uploader("导入收藏", type=["json"], key="import_favorites")
    if uploaded:
        imported = process_imported_json(uploaded, [])
        merge_imported_favorites(imported)
        rerun()
    if col3.button("清空收藏", use_container_width=True):
        save_favorites([])
        rerun()

    if not favorites:
        st.info("暂无匹配的收藏。你可以在搜索结果中点击“收藏”。")
        return

    st.session_state.hide_broken = st.checkbox("隐藏本地标记为疑似失效的收藏", value=st.session_state.hide_broken)
    for index, item in enumerate(favorites):
        resource = {"name": item.get("name"), "url": item.get("link"), "pwd": item.get("pwd"), "type": item.get("type")}
        render_resource_card(resource, item.get("type") or "", index, prefix="favorites", allow_favorite=True, allow_broken=True)


def render_policy_page() -> None:
    header("用户使用条例", "使用该网页 / 程序默认遵守以下说明。")
    render_policy_notice(expanded=True)
    render_component_alignment_note("helpModalOverlay")
    st.markdown("### 与 docs/index.html 的功能对齐范围")
    for feature in INDEX_FEATURES:
        st.markdown(f"- {feature}")


def render_json_mode(query: str, preset: str) -> None:
    # 中文：Streamlit 无法像静态 HTML 那样直接改写 HTTP 响应体，因此以等价 JSON 视图和下载按钮实现 format=json 功能。
    # English: Streamlit cannot rewrite the raw HTTP response body like static HTML, so format=json is implemented as an equivalent JSON view with a download button.
    inject_page_style()
    clean_query = normalize_search_keyword(query)
    safe_preset = valid_preset_name(preset)
    if not clean_query:
        st.json({"code": -1, "msg": "missing keyword"})
        st.stop()

    with st.spinner("Loading JSON..."):
        try:
            result = fetch_and_merge_data_stable(clean_query, safe_preset, attempts=3, delay=0.7)
            payload = {
                "code": 0,
                "msg": "success",
                "keyword": clean_query,
                "type": result["effectivePreset"],
                "total": result["total"],
                "data": result["mergedByType"],
            }
        except Exception as error:
            payload = {"code": -1, "msg": str(error)}

    st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")
    st.download_button("下载 JSON", dump_json(payload), "kuleu-api-result.json", "application/json")
    st.stop()


def apply_entry_url_params() -> None:
    params = get_query_params()
    query = first_query_value(params, ["q", "s", "name", "keyword", "search"])
    preset = first_query_value(params, ["from"], default="all")
    output_format = first_query_value(params, ["format"])

    if query and output_format.lower() == "json":
        render_json_mode(query, preset)

    if query and not st.session_state.get("url_params_consumed"):
        st.session_state.url_params_consumed = True
        set_pending_search(query, preset)
