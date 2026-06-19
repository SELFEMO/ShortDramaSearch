import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List

import streamlit as st


def ensure_streamlit_runtime() -> None:
    # 中文：Streamlit 必须在自身 runtime 中运行；自动转交能避免用户在 IDE 里点运行后看到一屏 ScriptRunContext 警告。
    # English: Streamlit must run inside its own runtime; automatic handoff prevents a wall of ScriptRunContext warnings when users click Run in an IDE.
    if os.environ.get("SHORTDRAMASEARCH_STREAMLIT_BOOTSTRAPPED") == "1":
        return

    get_script_run_ctx = None
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx as runtime_ctx

        get_script_run_ctx = runtime_ctx
    except Exception:
        try:
            from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx as runtime_ctx

            get_script_run_ctx = runtime_ctx
        except Exception:
            get_script_run_ctx = None

    if get_script_run_ctx is not None:
        try:
            if get_script_run_ctx(suppress_warning=True) is not None:
                return
        except TypeError:
            try:
                if get_script_run_ctx() is not None:
                    return
            except Exception:
                pass
        except Exception:
            pass

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    env = os.environ.copy()
    env["SHORTDRAMASEARCH_STREAMLIT_BOOTSTRAPPED"] = "1"
    command = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    if len(sys.argv) > 1:
        # 中文：保留 IDE 或命令行传入的端口参数，避免自动转交后用户自定义启动配置丢失。
        # English: Preserve port arguments from IDE or CLI so automatic handoff does not discard user launch settings.
        command.extend(sys.argv[1:])

    print("检测到当前使用 python app.py 直接启动，正在自动切换为 Streamlit 运行模式。")
    print("Detected direct python execution; relaunching with Streamlit runtime.")
    completed = subprocess.run(command, env=env, check=False)
    sys.exit(completed.returncode)


def configure_page(title: str = "酷乐短剧 / 影视资源聚合搜索") -> None:
    st.set_page_config(
        page_title=title,
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def switch_page(path: str) -> None:
    # 中文：页面跳转优先使用 Streamlit 原生多页面 API；旧版本不可用时用提示兜底，避免静默失败。
    # English: Page switching prefers Streamlit's native multipage API; when unavailable, a visible fallback avoids silent failure.
    if hasattr(st, "switch_page"):
        st.switch_page(path)
    st.info(f"请从左侧导航打开：{path}")
    st.stop()


def get_query_params() -> Dict[str, List[str]]:
    try:
        params = st.query_params
        return {key: params.get_all(key) for key in params.keys()}
    except Exception:
        try:
            return st.experimental_get_query_params()
        except Exception:
            return {}


def first_query_value(params: Dict[str, List[str]], names: Iterable[str], default: str = "") -> str:
    for name in names:
        values = params.get(name)
        if values:
            return str(values[0])
    return default
