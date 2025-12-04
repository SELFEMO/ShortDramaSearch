import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="短剧搜索",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("🎬 短剧搜索系统")

# 在侧边栏添加说明
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
        - 输入短剧名称进行搜索
        - 结果会显示：
            - 短剧名称
            - 百度网盘链接
            - 更新时间
        - 点击链接可直接访问资源
    """)

    # st.header("搜索示例")
    # st.code("短命太子\n太子\n霸道总裁")

# 搜索框
search_name = st.text_input(
    "",
    # "请输入短剧名称",
    placeholder="请输入短剧名称",
    # placeholder="例如：短命太子、太子、霸道总裁...",
    key="search_input"
)

# 搜索按钮
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_clicked = st.button("🔍 搜索短剧", use_container_width=True)

# 执行搜索
if search_clicked and search_name:
    with st.spinner(f'正在搜索「{search_name}」...'):
        try:
            # 调用API
            api_url = "https://api.kuleu.com/api/bddj"
            params = {
                "text": search_name
            }

            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()

            result_data = response.json()

            if result_data.get("code") == 200:
                dramas = result_data.get("data", [])

                if dramas:
                    st.success(f"找到 {len(dramas)} 个相关结果")

                    # 转换为DataFrame以便更好展示
                    df = pd.DataFrame(dramas)

                    # 显示统计信息
                    st.subheader("📊 搜索结果概览")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总结果数", len(dramas))
                    with col2:
                        # 计算最近更新的数量（最近30天）
                        recent_count = 0
                        for drama in dramas:
                            try:
                                add_time = datetime.strptime(drama['addtime'], '%Y-%m-%d %H:%M:%S')
                                if (datetime.now() - add_time).days <= 30:
                                    recent_count += 1
                            except:
                                pass
                        st.metric("最近更新", recent_count)
                    with col3:
                        st.metric("搜索关键词", search_name)

                    # 显示详细结果
                    st.subheader("🎭 短剧列表")

                    for i, drama in enumerate(dramas, 1):
                        with st.expander(f"{i}. {drama['name']}", expanded=i <= 3):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**名称**: {drama['name']}")
                                st.write(f"**更新时间**: {drama['addtime']}")
                            with col2:
                                # st.link_button("🔗 查看资源", drama['viewlink'])  # streamlit 低版本可能不支持 link_button，使用兼容的链接按钮方法
                                link = drama['viewlink']
                                button_html = f'''
                                    <a href="{link}" target="_blank">
                                        <button style='
                                            background-color: #4CAF50;
                                            color: white;
                                            border: none;
                                            padding: 10px 20px;
                                            text-align: center;
                                            text-decoration: none;
                                            display: inline-block;
                                            font-size: 14px;
                                            margin: 4px 2px;
                                            cursor: pointer;
                                            border-radius: 5px;
                                            width: 100%;
                                        '>
                                            🔗 查看资源
                                        </button>
                                    </a>
                                    '''
                                st.markdown(button_html, unsafe_allow_html=True)

                    # 添加数据下载功能
                    st.subheader("💾 数据导出")
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="下载CSV格式数据",
                        data=csv,
                        file_name=f"短剧搜索_{search_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )

                else:
                    st.warning(f"没有找到与「{search_name}」相关的短剧")

            else:
                error_msg = result_data.get("msg", "API返回错误")
                st.error(f"搜索失败: {error_msg}")

        except requests.exceptions.RequestException as e:
            st.error(f"网络请求失败: {str(e)}")
        except Exception as e:
            st.error(f"发生错误: {str(e)}")

elif search_clicked and not search_name:
    st.warning("请输入要搜索的短剧名称")

# 添加页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>短剧搜索系统 &copy; 2025</div>",
    unsafe_allow_html=True
)