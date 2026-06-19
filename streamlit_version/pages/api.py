from services.runtime import configure_page
from services.state import init_state
from services.pages import render_api_page
from services.ui import footer, render_page_shell


configure_page("API 生成器 · 酷乐短剧")
init_state()
render_page_shell("api")
render_api_page()
footer()
