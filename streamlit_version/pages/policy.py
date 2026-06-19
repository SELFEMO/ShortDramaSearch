from services.runtime import configure_page
from services.state import init_state
from services.pages import render_policy_page
from services.ui import footer, render_page_shell


configure_page("用户条例 · 酷乐短剧")
init_state()
render_page_shell("policy")
render_policy_page()
footer()
