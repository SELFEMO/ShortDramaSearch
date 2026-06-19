import html
import json
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from services.api_client import (
    build_qrcode_url,
    dump_json,
    flatten_preview_links,
    grouped_results_to_rows,
    load_shortdrama_rank,
    load_vtquark_rank,
)
from services.component_map import INDEX_COMPONENT_MAP
from services.constants import GITHUB_PAGES_URL, GITHUB_URL, PAGE_LINKS
from services.normalizers import get_source_class, make_resource_id, normalize_resource_item, normalize_search_keyword, ordered_types, source_label
from services.runtime import rerun
from services.state import (
    get_favorites,
    get_quality,
    is_broken_marked,
    is_favorited,
    save_favorites,
    set_pending_search,
    set_quality,
    toggle_broken,
    toggle_favorite,
)


def inject_page_style() -> None:
    palette = {
        "bg": "#0a0a0f",
        "bg2": "#12121a",
        "fg": "#f0f0f5",
        "muted": "#9ca3af",
        "card": "rgba(26,26,36,0.88)",
        "border": "rgba(255,255,255,0.12)",
        "accent": "#ff6b35",
        "accent_soft": "rgba(255,107,53,0.16)",
    }

    st.markdown(
        f"""
<style>
    div[data-testid="stSidebarNav"] {{ display: none; }}
    .stApp {{
        background:
            radial-gradient(circle at 12% 18%, {palette['accent_soft']} 0, transparent 28%),
            radial-gradient(circle at 85% 12%, rgba(99,102,241,0.16) 0, transparent 26%),
            linear-gradient(135deg, {palette['bg']} 0%, {palette['bg2']} 100%);
        color: {palette['fg']};
    }}
    .block-container {{ padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1180px; }}
    .hero-card, .kuleu-card {{
        border: 1px solid {palette['border']};
        border-radius: 22px;
        padding: 1.2rem 1.35rem;
        background: {palette['card']};
        box-shadow: 0 18px 50px rgba(0,0,0,0.18);
        margin-bottom: 1rem;
    }}
    .hero-title {{ font-size: clamp(2rem, 4vw, 3.4rem); font-weight: 800; margin: 0; }}
    .hero-subtitle {{ color: {palette['muted']}; margin-top: .45rem; line-height: 1.7; }}
    .muted {{ color: {palette['muted']}; }}
    .pill {{ display: inline-flex; align-items: center; gap: .35rem; padding: .25rem .65rem; border-radius: 999px; border: 1px solid {palette['border']}; background: {palette['accent_soft']}; margin: .15rem .25rem .15rem 0; font-size: .86rem; }}
    .result-card {{
        border: 1px solid {palette['border']};
        border-radius: 18px;
        padding: 1rem;
        margin: .75rem 0;
        background: {palette['card']};
    }}
    .result-title {{ font-weight: 800; font-size: 1.05rem; margin-bottom: .35rem; }}
    .small-line {{ font-size: .9rem; color: {palette['muted']}; word-break: break-all; }}
    .source-baidu {{ color: #06a7ff; font-weight: 700; }}
    .source-quark {{ color: #ff9500; font-weight: 700; }}
    .source-default {{ color: {palette['fg']}; font-weight: 700; }}
    .policy-box {{ font-size: .92rem; line-height: 1.85; }}
    div[data-testid="stMetric"] {{ border: 1px solid {palette['border']}; border-radius: 16px; padding: .75rem; background: {palette['card']}; }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(26,26,36,0.98), rgba(17,17,25,0.98));
        border-right: 1px solid {palette['border']};
    }}
    section[data-testid="stSidebar"] hr {{ border-color: {palette['border']}; opacity: .45; }}
    .sidebar-brand {{
        margin: .35rem 0 1.1rem 0;
        padding: .9rem .85rem;
        border: 1px solid {palette['border']};
        border-radius: 18px;
        background: rgba(255,255,255,0.045);
    }}
    .sidebar-title {{ font-size: 1.2rem; font-weight: 900; letter-spacing: .02em; }}
    .sidebar-subtitle {{ color: {palette['muted']}; font-size: .82rem; margin-top: .28rem; }}
    .nav-section-label {{
        margin: .2rem 0 .55rem 0;
        color: {palette['muted']};
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }}
    .nav-active {{
        border: 1px solid rgba(255,107,53,.45);
        border-radius: 14px;
        padding: .72rem .78rem;
        margin: .35rem 0;
        background: linear-gradient(135deg, rgba(255,107,53,.22), rgba(255,255,255,.055));
        box-shadow: inset 3px 0 0 {palette['accent']};
    }}
    .nav-active-title {{ font-weight: 900; line-height: 1.25; }}
    .nav-active-desc {{ color: {palette['muted']}; font-size: .78rem; margin-top: .2rem; }}
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {{
        min-height: 43px;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        text-align: left !important;
        border-radius: 14px;
        border: 1px solid transparent;
        background: transparent;
        color: {palette['fg']};
        font-weight: 760;
        padding-left: .75rem;
        transition: all .15s ease;
    }}
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {{
        border-color: {palette['border']};
        background: rgba(255,255,255,0.07);
        transform: translateX(2px);
    }}
    .sidebar-link-block a {{
        display: block;
        margin: .38rem 0;
        color: #7db7ff !important;
        text-decoration: none;
        font-size: .9rem;
    }}
    .compact-copy-input {{
        width: 100%;
        height: 38px;
        box-sizing: border-box;
        border-radius: 10px;
        border: 1px solid {palette['border']};
        background: rgba(17,24,39,.72);
        color: {palette['fg']};
        padding: 0 .7rem;
        font-weight: 800;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        line-height: 38px;
        outline: none;
    }}
    .compact-copy-input:focus {{ border-color: {palette['accent']}; box-shadow: 0 0 0 2px rgba(255,107,53,.18); }}
</style>
""",
        unsafe_allow_html=True,
    )


def render_sidebar(current_page: str) -> None:
    with st.sidebar:
        st.markdown(
            """
<div class="sidebar-brand">
  <div class="sidebar-title">🎬 酷乐短剧</div>
  <div class="sidebar-subtitle">深色多页面聚合控制台</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-section-label">导航 / Navigation</div>', unsafe_allow_html=True)

        for item in PAGE_LINKS:
            title = f"{item['icon']} {item['title']}"
            if current_page == item["id"]:
                st.markdown(
                    f"""
<div class="nav-active">
  <div class="nav-active-title">{html.escape(title)}</div>
  <div class="nav-active-desc">{html.escape(item['desc'])}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                # 中文：导航改用真实 page_link 而不是自维护按钮状态，让 pages/ 架构下每次点击都直接进入目标页面。
                # English: Navigation uses real page links instead of self-managed button state so every click enters the target page directly under pages/.
                st.page_link(item["path"], label=title, use_container_width=True)

        st.markdown("---")
        st.markdown(
            f"""
<div class="sidebar-link-block">
<a href="{GITHUB_URL}" target="_blank">GitHub 项目</a>
<a href="{GITHUB_PAGES_URL}" target="_blank">GitHub Pages 版本</a>
<a href="{GITHUB_PAGES_URL}neo.html" target="_blank">Neo 新版界面</a>
<a href="{GITHUB_PAGES_URL}console.html" target="_blank">Console 控制台界面</a>
</div>
""",
            unsafe_allow_html=True,
        )


def render_page_shell(current_page: str) -> None:
    inject_page_style()
    render_sidebar(current_page)


def render_policy_notice(expanded: bool = False) -> None:
    with st.expander("用户使用条例 / User Policy", expanded=expanded):
        st.markdown(
            f"""
<div class="policy-box">
<p>欢迎使用 <strong>酷乐短剧 / 影视资源聚合搜索</strong>。本程序不存储、不上传、不传播任何网盘文件或影视资源，也不提供在线播放、下载、转存等服务。</p>
<p>页面中展示的资源链接均来源于互联网公开索引信息，仅作为搜索结果聚合展示用途。所有链接均会跳转至第三方网盘或外部平台，相关文件有效性、安全性、合法性与可访问性由用户自行判断并承担风险。</p>
<p>本程序为个人兴趣开源项目，不收费、不用于商业用途、不参与任何资源运营行为。若相关内容涉及侵权问题，请优先联系对应接口平台或资源提供方处理。</p>
<p>GitHub 项目地址：<a href="{GITHUB_URL}" target="_blank">{GITHUB_URL}</a></p>
</div>
""",
            unsafe_allow_html=True,
        )


def header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="hero-card">
  <div class="hero-title">{html.escape(title)}</div>
  <div class="hero-subtitle">{html.escape(subtitle)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown("---")
    st.markdown(
        "<div class='muted' style='text-align:center'>已适配酷乐聚合资源搜索接口所有网盘类型与磁力 / 电驴链接。短剧搜索系统 © 2026 · Streamlit 多页面重构版</div>",
        unsafe_allow_html=True,
    )


def link_button(label: str, url: str, key: str) -> None:
    if hasattr(st, "link_button"):
        st.link_button(label, url, use_container_width=True)
    else:
        st.markdown(f'<a href="{html.escape(url)}" target="_blank">{html.escape(label)}</a>', unsafe_allow_html=True)


def render_compact_copy_input(value: str, label: str = "提取码") -> None:
    # 中文：这里不用 st.code，是因为代码块默认高度和内边距较大，会破坏结果卡片按钮行的视觉平衡。
    # English: st.code is avoided here because its default height and padding break the visual balance of the result-card action row.
    safe_value = html.escape(str(value or ""), quote=True)
    safe_label = html.escape(label, quote=True)
    st.markdown(
        f'<input class="compact-copy-input" value="{safe_value}" aria-label="{safe_label}" '
        f'title="点击后 Ctrl+C 复制 / Click then press Ctrl+C to copy" readonly onclick="this.select();" />',
        unsafe_allow_html=True,
    )


def render_qr_expander(link: str, key: str) -> None:
    with st.expander("二维码 / QR Code", expanded=False):
        st.image(build_qrcode_url(link), width=220)
        st.caption("使用手机相机或微信扫一扫。")


def render_resource_card(item: Dict[str, Any], type_name: str, index: int, prefix: str, allow_favorite: bool = True, allow_broken: bool = True) -> None:
    fixed = normalize_resource_item({**item, "type": type_name})
    name = fixed.get("name") or "未知资源"
    link = fixed.get("url") or fixed.get("link") or ""
    pwd = fixed.get("pwd") or ""
    broken = is_broken_marked(link)
    if st.session_state.hide_broken and broken:
        return

    broken_tip = " · 本地已标记疑似失效" if broken else ""
    pwd_html = f'<div class="small-line">密码：<strong>{html.escape(pwd)}</strong></div>' if pwd else ""
    st.markdown(
        f"""
<div class="result-card" data-link="{html.escape(link)}">
  <div class="result-title">{html.escape(name)}</div>
  <div class="small-line">来源：<span class="{get_source_class(type_name)}">{html.escape(source_label(type_name))}</span>{broken_tip}</div>
  <div class="small-line">链接：{html.escape(link)}</div>
  {pwd_html}
</div>
""",
        unsafe_allow_html=True,
    )

    columns = st.columns([1, 1, 1, 1, 2])
    with columns[0]:
        if link:
            link_button("打开链接", link, key=f"{prefix}_open_{index}")
    with columns[1]:
        if allow_favorite and link:
            button_label = "取消收藏" if is_favorited(link) else "收藏"
            if st.button(button_label, key=f"{prefix}_fav_{make_resource_id(link)}_{index}", use_container_width=True):
                toggle_favorite(fixed)
                rerun()
    with columns[2]:
        if allow_broken and link:
            broken_label = "取消失效" if broken else "失效反馈"
            if st.button(broken_label, key=f"{prefix}_broken_{make_resource_id(link)}_{index}", use_container_width=True):
                toggle_broken(link)
                rerun()
    with columns[3]:
        if pwd:
            render_compact_copy_input(pwd, label="提取码")
        else:
            st.caption("无密码")
    with columns[4]:
        if link:
            current_score = get_quality(link)
            score = st.select_slider(
                "本地质量评分",
                options=[0, 1, 2, 3, 4, 5],
                value=current_score,
                format_func=lambda value: "未评分" if value == 0 else f"{value} 星",
                key=f"{prefix}_quality_{make_resource_id(link)}_{index}",
            )
            if score != current_score:
                set_quality(link, score)

    if link:
        with st.expander("复制链接文本 / Copyable text", expanded=False):
            pwd_line = f"\n密码：{pwd}" if pwd else ""
            st.code(f"{name}\n{link}{pwd_line}", language=None)
        render_qr_expander(link, key=f"{prefix}_qr_{index}")


def render_grouped_results(result: Dict[str, Any], keyword: str) -> None:
    merged = result.get("mergedByType") or {}
    total = result.get("total") or 0
    type_list = result.get("typeList") or []
    api_status = result.get("apiStatus") or {}

    col1, col2, col3 = st.columns(3)
    col1.metric("总结果数", total)
    col2.metric("命中来源", len(type_list))
    col3.metric("搜索关键词", keyword)

    if api_status:
        st.caption(f"搜索请求：成功 {api_status.get('successCount', 0)} 次 / 失败 {api_status.get('failedCount', 0)} 次")

    st.session_state.hide_broken = st.checkbox("隐藏本地标记为疑似失效的资源", value=st.session_state.hide_broken)

    for type_name in ordered_types(type_list):
        items = merged.get(type_name) or []
        if not items:
            continue
        with st.expander(f"{source_label(type_name)} · 共 {len(items)} 条", expanded=(type_name in ("baidu", "quark"))):
            for index, item in enumerate(items):
                render_resource_card(item, type_name, index, prefix=f"search_{type_name}")

    rows = grouped_results_to_rows(merged)
    if rows:
        df = pd.DataFrame(rows)
        clean_name = normalize_search_keyword(keyword) or "result"
        st.download_button(
            "下载 CSV 结果",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"kuleu-search-{clean_name}-{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "下载 JSON 结果",
            data=dump_json({"keyword": keyword, "total": total, "data": merged}),
            file_name=f"kuleu-search-{clean_name}-{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )


def render_rank_tags_for_search() -> None:
    with st.expander("🔥 榜单快捷搜索", expanded=True):
        col1, col2 = st.columns(2)
        try:
            rank_data = load_shortdrama_rank()
        except Exception:
            rank_data = []
        try:
            vtquark_data = load_vtquark_rank()
        except Exception:
            vtquark_data = []

        with col1:
            st.markdown("**短剧热度榜**")
            for index, item in enumerate(rank_data[:10]):
                title = normalize_search_keyword(item.get("title"))
                if title and st.button(f"{item.get('ranking', index + 1)}. {title} · 🔥 {item.get('hots', '')}", key=f"quick_rank_{index}", use_container_width=True):
                    set_pending_search(title, "all")
                    rerun()
        with col2:
            st.markdown("**夸克热搜榜**")
            for index, item in enumerate(vtquark_data[:10]):
                title = normalize_search_keyword(item.get("content_title"))
                if title and st.button(f"{item.get('content_rank', index + 1)}. {title} · 🔥 {item.get('hot', '')}", key=f"quick_vt_{index}", use_container_width=True):
                    set_pending_search(title, "all")
                    rerun()


def process_imported_json(uploaded_file: Any, fallback: List[Any]) -> List[Any]:
    if uploaded_file is None:
        return fallback
    try:
        raw = uploaded_file.read().decode("utf-8")
        data = json.loads(raw)
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            return data["data"]
        if isinstance(data, list):
            return data
        st.error("导入失败：JSON 结构不符合要求。")
    except Exception as error:
        st.error(f"导入失败：{error}")
    return fallback


def collect_current_result_links() -> str:
    current = st.session_state.get("current_results") or {}
    merged = current.get("mergedByType") or {}
    lines: List[str] = []
    for type_name in ordered_types(merged.keys()):
        for item in merged.get(type_name, []):
            fixed = normalize_resource_item(item)
            title = fixed.get("name") or "未命名资源"
            link = fixed.get("url") or ""
            pwd = fixed.get("pwd") or ""
            if not link:
                continue
            pwd_line = f"\n密码：{pwd}" if pwd else ""
            lines.append(f"{title}\n{link}{pwd_line}")
    return "\n\n".join(lines)


def render_component_alignment_note(page_key: str) -> None:
    mapping = INDEX_COMPONENT_MAP.get(page_key, {})
    if not mapping:
        return
    with st.expander("组件映射 / docs/index.html alignment", expanded=False):
        # 中文：该映射只作为实现对照说明，不读取 docs/index.html，因此打包部署到 Streamlit Cloud 时不会依赖 docs 目录路径。
        # English: This map is only an implementation reference and never reads docs/index.html, so Streamlit Cloud deployments do not depend on the docs directory path.
        st.caption("下表说明当前页面与 docs/index.html 中 DOM 组件的对应关系。")
        rows = [{"docs/index.html DOM": key, "Streamlit component": value} for key, value in mapping.items()]
        st.dataframe(rows, use_container_width=True, hide_index=True)


def merge_imported_favorites(imported: List[Any]) -> None:
    old_map = {item.get("link"): item for item in get_favorites() if item.get("link")}
    for raw_item in imported:
        if not isinstance(raw_item, dict):
            continue
        link = raw_item.get("link") or raw_item.get("url") or raw_item.get("viewlink")
        if not link:
            continue
        fixed = normalize_resource_item({"name": raw_item.get("name") or raw_item.get("title"), "url": link, "pwd": raw_item.get("pwd")})
        old_map[link] = {
            "id": raw_item.get("id") or make_resource_id(link),
            "name": fixed.get("name"),
            "link": link,
            "pwd": fixed.get("pwd"),
            "type": raw_item.get("type") or raw_item.get("source") or "",
            "savedAt": raw_item.get("savedAt") or datetime.now().isoformat(timespec="seconds"),
        }
    save_favorites(list(old_map.values()))
