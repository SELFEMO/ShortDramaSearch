from services.runtime import configure_page
from services.state import init_state
from services.pages import render_daily_page
from services.ui import footer, render_page_shell


configure_page("每日影视 · 酷乐短剧")
init_state()
render_page_shell("daily")
render_daily_page()
footer()
