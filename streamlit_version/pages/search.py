from services.runtime import configure_page
from services.state import init_state
from services.pages import render_search_page
from services.ui import footer, render_page_shell


configure_page("聚合搜索 · 酷乐短剧")
init_state()
render_page_shell("search")
render_search_page()
footer()
