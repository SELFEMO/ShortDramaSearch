from services.runtime import configure_page, ensure_streamlit_runtime, switch_page
from services.state import init_state
from services.pages import apply_entry_url_params


ensure_streamlit_runtime()
configure_page("酷乐短剧 / 影视资源聚合搜索")
init_state()
apply_entry_url_params()

# 中文：入口文件只负责启动与 URL 参数兼容，真实业务页面放入 pages/，以满足 Streamlit 多页面架构并降低主文件复杂度。
# English: The entry file only handles bootstrap and URL parameter compatibility; real business pages live under pages/ to satisfy the Streamlit multipage architecture and reduce main-file complexity.
switch_page("pages/1_search.py")
