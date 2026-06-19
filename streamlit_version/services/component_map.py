from typing import Dict, List


# 中文：这里用静态映射记录 docs/index.html 的 DOM 组件与 Streamlit 组件关系，避免运行时读取 docs/index.html 文件导致部署路径耦合。
# English: This static map records the relationship between docs/index.html DOM components and Streamlit components, avoiding runtime reads of docs/index.html that would couple deployment paths.
INDEX_COMPONENT_MAP: Dict[str, Dict[str, str]] = {
    "page-search": {
        "searchInput": "st.text_input(key='search_keyword')",
        "typeSelect": "st.selectbox(key='search_preset')",
        "searchBtn": "st.form_submit_button('🔍 搜索')",
        "resultsArea": "render_grouped_results()",
        "searchHistoryPanel": "render_search_history_tools()",
        "toggleBrokenFilterBtn": "st.checkbox(key='hide_broken')",
        "copyCurrentLinksBtn": "st.download_button + copyable text expander",
    },
    "page-api": {
        "apiKeywordInput": "st.text_input(key='api_keyword')",
        "apiFromSelect": "st.selectbox(key='api_preset')",
        "apiGeneratedUrl": "st.text_input(readonly-like generated url)",
        "apiGenerateBtn": "form submit / generated-url refresh",
        "apiCopyBtn": "compact copy input",
        "apiOpenLink": "st.link_button",
        "apiPreviewBtn": "st.button('预览 JSON 结果')",
        "apiPreviewOutput": "st.json(payload)",
        "apiPreviewLinksList": "render_resource_card() for preview links",
    },
    "page-daily": {
        "dailyRefreshBtn": "st.button('加载 / 刷新每日影视资源')",
        "dailySearchInput": "st.text_input(key='daily_filter')",
        "dailyStats": "st.metric + caption",
        "dailyResultsArea": "render_resource_card() grouped by baidu/quark",
    },
    "page-rank": {
        "rankSearchInput": "st.text_input(key='rank_filter')",
        "rankListContainer": "st.tabs(['短剧热度榜', '夸克热搜榜'])",
    },
    "page-favorites": {
        "favoriteSearchInput": "st.text_input(key='favorite_filter')",
        "exportFavoritesBtn": "st.download_button",
        "importFavoritesBtn": "st.file_uploader",
        "clearFavoritesBtn": "st.button('清空收藏')",
        "favoritesStats": "st.metric + caption",
        "favoritesList": "render_resource_card() from session favorites",
    },
    "helpModalOverlay": {
        "helpApiTemplateUrl": "st.code(template_url)",
        "helpApiExampleUrl": "st.code(example_url)",
        "policyContent": "render_policy_notice(expanded=True)",
    },
}

INDEX_FEATURES: List[str] = [
    "Hash route pages are represented by real Streamlit pages under pages/.",
    "Search keeps full keyword first and split keyword fallback.",
    "Search supports all/netdisk/single-source presets.",
    "URL parameters q/s/name/keyword/from/format are supported on the entry app.",
    "format=json is represented as an equivalent Streamlit JSON view and download.",
    "Daily resources merge Baidu and Quark API data.",
    "Rank page contains short drama rank and Quark hot-search rank.",
    "Favorites, search history, broken marks, quality scores, imports and exports are kept in session state.",
    "QR code generation uses the same Kuleu QR API.",
]
