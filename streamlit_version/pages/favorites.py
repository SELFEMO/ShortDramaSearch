from services.runtime import configure_page
from services.state import init_state
from services.pages import render_favorites_page
from services.ui import footer, render_page_shell


configure_page("我的收藏 · 酷乐短剧")
init_state()
render_page_shell("favorites")
render_favorites_page()
footer()
