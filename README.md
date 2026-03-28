# 🎬 [短剧/影视资源聚合搜索](https://github.com/SELFEMO/ShortDramaSearch)

一个多版本的短剧搜索应用，提供Flask、Streamlit、Desktop和在线网页（Online-Webpage）四种实现方式，可以快速搜索短剧资源并获取百度网盘链接。

$^*$***注意：2026重构版本仍处于开发阶段（目前适配最好的版本为：Web在线版本），功能可能不稳定且界面并未完善，同时存在一些暂时无法修改的问题（Bug），欢迎贡献修复代码！***

## 🌟 [项目简介](https://github.com/SELFEMO/ShortDramaSearch.git)

这是一个简单易用的短剧搜索工具，通过调用第三方API接口，帮助用户快速查找各类短剧资源。项目提供了两种技术栈的实现，满足不同开发和使用需求。

**主要特性：**

- 🔍 **智能搜索** - 输入短剧名称即可搜索相关资源
- 📊 **结果统计** - 显示搜索结果数量和详细信息
- 🔗 **直接访问** - 一键跳转到百度网盘资源页面
- 💾 **数据导出** - 支持将搜索结果导出
- 📱 **响应式设计** - 适配不同屏幕尺寸
- ⚡ **实时反馈** - 搜索状态实时提示

---

## 🚩 [Github 在线访问版本（Online-Webpage版本）](https://github.com/SELFEMO/ShortDramaSearch/tree/master/docs/index.html)

***🔗 Github Page 访问链接：[https://selfemo.github.io/ShortDramaSearch/](https://selfemo.github.io/ShortDramaSearch/)***

### 主要功能

- **零安装使用** - 无需安装任何环境，直接浏览器访问
- **跨平台兼容** - 支持所有现代浏览器，PC和移动端均可使用
- **响应式界面** - 自适应不同屏幕尺寸，移动端体验友好
- **动态视觉效果** - 渐变背景、浮动光球、入场动画等现代UI设计
- **多代理容错** - 内置多个CORS代理，提高API调用成功率
- **GitHub Pages 部署** - 支持一键部署到 GitHub Pages

#### 此外，该网站支持键入指定URL参数直接搜索（即 `https://selfemo.github.io/ShortDramaSearch/?参数=指定值` $^1$）

| 参数名 | 别名 | 是否必填 | 说明 | 默认值 | 备注                                                   |
| :--- | :--- |:-----| :--- | :--- |:-----------------------------------------------------|
| **search** | `s`、`q`、`name`、`keyword` | 否    | **搜索关键词**。支持中英文，支持空格拆分关键词以提高命中率。 | 无 | 参数值为短剧名称（需要注意的是，“短剧名称”字符串**不需要添加引号**                 |
| **from** | 无 | 否    | **搜索来源**。指定搜索的网盘类型。 | `all` | 请严格按照指定的来源名称传入参数值 $^2$，例如：`from=netdisk` |
| **format** | 无 | 否    | **输出格式**。设为 `json` 时，页面将直接输出纯 JSON 数据 $^3$，不渲染 UI 界面。 | 网页模式 (HTML) | 如果不传此参数或值不为 json，页面将渲染正常的搜索界面并自动开始搜索。                |

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

$^1$ 多个参数可以组合使用，需要使用`&`符号连接，例如：```https://selfemo.github.io/ShortDramaSearch/?q=熊出没&from=netdisk```

$^2$ 参数 `from` 指定搜索的网盘来源，如下所示：
  - **聚合类：**
    - `all`: 全局聚合（默认）
    - `netdisk`: 网盘聚合（仅包含各大网盘）
  - **网盘类：**
    - `baidu`: 百度网盘
    - `quark`: 夸克网盘
    - `aliyun`: 阿里云盘
    - `tianyi`: 天翼云盘
    - `uc`: UC网盘
    - `mobile`: 移动云盘
    - `115`: 115网盘
    - `pikpak`: PikPak
    - `xunlei`: 迅雷网盘
    - `123`: 123网盘
  - **链接类：**
    - `magnet`: 磁力链接
    - `ed2k`: 电驴链接

$^3$ 当键入网址（请求示例）类似于 ```https://selfemo.github.io/ShortDramaSearch/?q=飞驰人生3&from=netdisk&format=json``` 时，网站就变成了一个 ***API 接口***，用户能够通过该 API 接口地址获取到一个相关搜索结果的 JSON 数据，支持用户获取该 JSON 数据进行二次开发。API 接口的返回示例（JSON 数据结果示例）如下：
  ```json
  {
    "code": 0,
    "msg": "success",
    "keyword": "飞驰人生3",
    "type": "netdisk",
    "total": 6,
    "data": {
      "quark": [
        {
          "url": "https://pan.quark.cn/s/b0042dadeb1f",
          "images": [
            "https://by1.430520.xyz/t/?id=1&url=xinlangtupian.com/cover/c68667d17d70ec51a68fb4d047df6fb8.jpg"
          ],
          "pwd": "",
          "name": "飞驰人生3",
          "_searchTerm": "飞驰人生3"
        },
        {
          "url": "https://pan.quark.cn/s/9c863f8c3933",
          "images": [
            "https://image.baidu.com/search/down?url=https://img9.doubanio.com/view/photo/m_ratio_poster/public/p2929427346.jpg"
          ],
          "pwd": "",
          "name": "飞驰人生3",
          "_searchTerm": "飞驰人生3"
        }
      ],
      "baidu": [
        {
          "url": "https://pan.baidu.com/s/1j4rVw-halXSEiK_-MzXgwQ?pwd=wogg",
          "images": [
            "https://cdn5.telesco.pe/file/cFmb7wshi8Z2nkTHh8g6JGoebBtsh78ZO2DV-E0XvubBxVdRJLkXP69r1b6KJTwq4ljSIKcdvrjUIgPoCcta6dlYH3TmsaUgp7jG7CZ_iSU5ILJZ_1-_dcB4AqJkQ1t16IvvDoiIB8-Y2YBDo1a82bfEDUrgssrX87m1LuTAOrXINbRxDUGidKjK_GyGp_S9MIpBq0c4cB6Txd4NWNLe9vRbNEOTUf3IoLbHMVCH6LLGbQzK6rzjy7RA6aD_3PCB1jeCvOANTjUhSPelPcVVlzgJf5uPz6mKN-nswzXj8QzZOlhSjJ8Wpr3VX1qh6HGfKPxlShAeHpbw61vxfkQe_A.jpg"
          ],
          "pwd": "wogg",
          "name": "2026年春节档电影[镖人：风起大漠][飞驰人生3][惊蛰无声][熊出没：年年有熊]",
          "_searchTerm": "飞驰人生3"
        },
        {
          "url": "https://pan.baidu.com/s/1WOiUTWG-0KBGDI3zopQ7Zg?pwd=w594",
          "images": [
            "https://cdn1.telesco.pe/file/njiCz8lmhq3596KnCvv0AMzkIm2pLukTZ0I8s6Leemq3X3d9H-KPN7144k0zqJQu2x2KaXxxrFfu6n2ejg6nI8CZW2fZvlSONClY7QIPWbsFpBZtlqbCOFDpu-58F7_p_kBbHjCdxO1bj-SpMKB6-IkfoYvzhqPgrwRgqfFfp6ZpcisBBMoTD9ALrcZcanfy6OitusuN2CMhRYrfN97GiSPkvSLB_3bryCk8SZfIiS9pENqYLYyiUxIrfSX_iWqiQgY0AMCvtJwuClNr-4lWTvIVEyE3LvAmh70h5hRdDEy6RcPWpWOUxtQThWsElZLGqy2ChQO0KppWkg4HK1lAdQ.jpg"
          ],
          "pwd": "w594",
          "name": "2026春节档上映电影合集，《惊蛰无声》《镖人：风起大漠》《飞驰人生3》等",
          "_searchTerm": "飞驰人生3"
        },
        {
          "url": "https://pan.baidu.com/s/1aYb_zOSGHwfcBoSrLFcD5g?pwd=yyds",
          "images": [
            "https://cdn5.telesco.pe/file/KgD-ib05j1MgP2VR2MEe9e0DzOspqNSrf3ncJ70wI2Uxd8BG90Z2adMMvIPkYHr5HHRecv9aQ7UWd7l2VQtHwfUG7VqmYapTuGHLXv0F1sug-oFiTBUGV6wRg1ls-IuVeoI8SSotIgXmNbyiF2qaIi_MbmlpX6jNhiZDCvnqmpomZ1sSFo0jDxTn6OxZn9QNSxDhzwj-AFQMNLNy7JsDtTCH3tAj0msNLaEploD4kXUsHLKVzL8T7SilWd9XzvCiotVrCX61zb1XNfvBM1V5LkC_bi3C31KURbtJRtBDnOUEnr3dqNB4ML-7blRyvx0bknRf2SDAFefPAVc3UxmO5A.jpg"
          ],
          "pwd": "yyds",
          "name": "飞驰人生3 (2026)  抢先版",
          "_searchTerm": "飞驰人生3"
        },
        {
          "url": "https://pan.baidu.com/s/1Hjw6nUihfcD1ZBVzVmcBkg?pwd=8888",
          "images": [
            "https://by1.430520.xyz/t/?id=1&url=xinlangtupian.com/cover/c68667d17d70ec51a68fb4d047df6fb8.jpg"
          ],
          "pwd": "8888",
          "name": "飞驰人生3",
          "_searchTerm": "飞驰人生3"
        }
      ]
    }
  }
  ```

---

## 🚀 [Flask 版本](https://github.com/SELFEMO/ShortDramaSearch/tree/master/flask_version)

### 主要功能

- **无刷新搜索** - 使用Ajax技术实现页面无刷新搜索
- **实时状态反馈** - 搜索过程中显示加载状态
- **优雅的错误处理** - 网络错误和API错误友好提示
- **响应式界面** - 适配桌面和移动设备
- **简洁美观的UI** - 现代化的卡片式设计

### 安装步骤

#### 前提条件

- Python 3.7 或更高版本
- pip 包管理工具

#### 1. 安装依赖

```bash
pip install flask requests
```

#### 2. 运行应用

```bash
python flask_version/app.py
```

#### 3. 访问应用

打开浏览器访问 `http://localhost:5000`

### 使用说明

#### 基本搜索

1. 在搜索框中输入短剧名称
2. 页面自动发送Ajax请求，无需点击按钮
3. 搜索结果实时显示在页面下方

#### 界面功能

- **搜索框** - 输入关键词后自动搜索
- **结果统计** - 显示找到的结果数量
- **资源卡片** - 每个结果以卡片形式展示，包含：
    - 🎭 短剧完整名称
    - 📅 更新时间
    - 🔗 百度网盘链接（新标签页打开）

### 自定义配置

修改 `flask_version/app.py` 中的配置：

```python
# API接口配置 和 搜索参数
api_url = "https://api.kuleu.com/api/bddj"
params = {
    "text": search_name
}

# Flask应用配置
if __name__ == '__main__':
    app.run(
        debug=True,  # 调试模式
        host='0.0.0.0',  # 监听地址
        port=5000  # 端口号
    )
```

---

## 📊 [Streamlit 版本](https://github.com/SELFEMO/ShortDramaSearch/tree/master/streamlit_version)

### 主要功能

- **交互式界面** - Streamlit原生组件提供流畅体验
- **数据统计** - 详细的搜索结果统计信息
- **数据导出** - 支持导出CSV格式的搜索结果
- **侧边栏导航** - 清晰的功能区域划分
- **扩展功能** - 最近更新统计、批量操作等

### 安装步骤

#### 前提条件

- Python 3.7 或更高版本
- pip 包管理工具

#### 1. 安装依赖

```bash
pip install streamlit requests pandas
```

#### 2. 运行应用

```bash
streamlit run streamlit_version/app.py
```

#### 3. 访问应用

打开浏览器访问 `http://localhost:8501`or `http://localhost:7777`（根据Streamlit版本不同可能端口不同）。

或者，通过命令指定端口：
```bash
streamlit run streamlit_version/app.py --server.port 7777
```

或者，通过配置文件指定端口：
```bash
# 在 .streamlit/config.toml 中添加以下内容

[server]
port = 7777
headless = true

[browser]
gatherUsageStats = false

```

### 使用说明

#### 基本搜索

1. 在搜索框中输入短剧名称
2. 点击"🔍 搜索短剧"按钮
3. 查看搜索结果和统计信息

#### 界面功能

- **搜索区域** - 文本输入框和搜索按钮
- **统计面板** - 显示总结果数、最近更新数量等
- **可展开列表** - 点击每个结果展开查看详情
- **数据导出** - 下载CSV格式的完整结果
- **侧边栏** - 使用说明和搜索示例

#### 数据导出

- 点击"下载CSV格式数据"按钮
- 获取包含所有搜索结果的CSV文件
- 文件自动按搜索关键词和时间命名

### 自定义配置

修改 `streamlit_version/app.py` 中的配置：

```python
# 页面配置
st.set_page_config(
    page_title="短剧搜索",  # 页面标题
    page_icon="🎬",  # 页面图标
    layout="wide",  # 布局模式
    initial_sidebar_state="expanded"  # 侧边栏状态
)

# API配置
api_url = "https://api.kuleu.com/api/bddj"
params = {
    "text": search_name
}
```

## 🖥️ [Desktop 版本 (Qt5)](https://github.com/SELFEMO/ShortDramaSearch/tree/master/desktop_version)

### 主要功能

- **跨平台桌面应用** - 支持Windows、macOS和Linux系统
- **原生界面体验** - 使用Qt5框架提供流畅的桌面应用体验
- **异步搜索处理** - 搜索过程在后台线程执行，避免界面冻结
- **本地数据缓存** - 自动缓存搜索结果，提升重复搜索速度
- **一键打开链接** - 直接调用系统默认浏览器打开网盘链接
- **搜索历史记录** - 自动保存搜索历史，方便再次查看
- **现代化UI设计** - 使用表格展示结果，支持交替行颜色和悬停效果

### 安装步骤

#### 前提条件

- Python 3.7 或更高版本
- pip 包管理工具

#### 1. 安装依赖

```bash
cd desktop_version
pip install -r requirements.txt
```

#### 2. 运行应用

```bash
python main.py
```

#### 3. 打包为可执行文件（可选）

```bash
# 使用内置打包脚本
python build.py

# 或直接使用PyInstaller
# Windows 示例
pyinstaller --name=ShortDramaSearch --windowed --onefile --icon=resources/icons/app.ico --add-data="resources;resources" main.py
# macOS 示例
pyinstaller --name=ShortDramaSearch --windowed --onefile --icon=resources/icons/app.icns --add-data="resources:resources" main.py
# Linux 示例
pyinstaller --name=short-drama-search --windowed --onefile --add-data="resources:resources" main.py
```

### 使用说明

#### 基本搜索

1. 在搜索输入框中输入短剧名称
2. 点击"搜索"按钮或按回车键开始搜索
3. 查看下方表格中显示的搜索结果

#### 界面功能

- **搜索区域** - 包含搜索输入框、搜索按钮和清空按钮
- **搜索结果表格** - 显示短剧名称、更新时间和网盘链接
- **操作按钮** - 每个结果行的"打开链接"按钮可直接打开网盘页面
- **状态栏** - 实时显示搜索状态和结果数量信息
- **进度指示** - 搜索过程中显示进度条

#### 数据管理

- **自动缓存** - 搜索结果会自动缓存，相同关键词再次搜索会更快
- **搜索历史** - 自动记录搜索历史，可在历史记录中查看
- **本地存储** - 所有数据存储在用户目录下的应用数据文件夹中

### 自定义配置

修改 `desktop_version/core/api_client.py` 中的API配置：

```python
class ApiClient:
    def __init__(self):
        self.base_url = "https://api.kuleu.com/api/bddj"  # API地址
        self.timeout = 60  # 请求超时时间（秒）

    def search_drama(self, keyword):
        """搜索短剧"""
        params = {
            "text": keyword
        }  # 搜索参数配置
        # ......

    # ......
```

修改 `desktop_version/ui/main_window.py` 中的界面配置：

```python
# 窗口标题和尺寸
self.setWindowTitle("短剧搜索 - 桌面版")
self.setGeometry(50, 100, 1600, 900)  # 窗口位置和大小，位置(50,100)，大小(1600x900)

# 表格列宽调整
table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # 名称列自适应
```

修改 `desktop_version/core/data_manager.py` 中的缓存配置：

```python
# 缓存过期时间（秒）
CACHE_EXPIRE_TIME = 3600  # 1小时
```

---

## 🗂️ 项目文件结构

```
ShortDramaSearch/
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖包列表
│
├── docs                           # Online-Website版本文件夹
│   └── index.html                 # Online-Website版本网页（单文件）
│
│
├── flask_version/                 # Flask版本
│   ├── app.py                     # Flask主应用文件
│   └── templates/                 # 网页模板目录
│       └── index.html             # 主页面模板
│
├── streamlit_version/             # Streamlit版本
│   └── app.py                     # Streamlit主应用文件
│
└── desktop_version/               # 桌面应用版本
    ├── main.py                    # 应用入口点
    ├── ui/                        # 界面模块
    │   ├── main_window.py         # 主窗口类
    │   ├── details_dialog.py      # 详情对话类
    │   └── components.py          # 自定义组件
    ├── core/                      # 核心逻辑
    │   ├── api_client.py          # API客户端
    │   ├── data_manager.py        # 数据管理
    │   └── utils.py               # 工具函数
    ├── resources/                 # 资源文件
    │   ├── icons/                 # 图标资源
    │   │   ├── API.svg            # API图标（SVG格式）
    │   │   ├── API.png            # API图标（PNG格式）
    │   │   ├── API.ico            # API图标（ICO格式）
    │   │   ├── API.icns           # API图标（ICNS格式）
    │   │   └── ...                # 其他图标文件
    │   ├── images/                # 其他图片资源
    │   └── styles/                # 其他样式文件（可能包括CSS等）
    ├── build.py                   # 打包脚本（简化版本）
    ├── build.spec                 # PyInstaller构建规范文件（build.py 的打包配置）
    ├── build/                     # 构建输出
    ├── dist/                      # 分发文件
    ├── ...                        # 其他构建相关文件，或构建日志等
    └── requirements.txt           # 依赖列表
```

### 文件说明

- **flask_version** - Flask版本主目录
    - **flask_version/app.py** - Flask后端逻辑，处理API请求和路由
    - **flask_version/templates/index.html** - 前端界面，包含HTML、CSS和JavaScript
- **streamlit_version** - Streamlit版本主目录
    - **streamlit_version/app.py** - 完整的Streamlit应用，包含UI和业务逻辑
- **desktop_version** - 桌面应用主目录
    - **desktop_version/main.py** - 桌面应用入口，初始化应用和主窗口
    - **desktop_version/ui/main_window.py** - 主窗口类，定义界面布局和交互
    - **desktop_version/core/api_client.py** - 负责与第三方API通信
    - **desktop_version/core/data_manager.py** - 管理数据缓存和本地存储
    - **desktop_version/core/utils.py** - 工具函数，如时间格式化等
    - **desktop_version/resources/icons/** - 存放应用图标的目录，包含多种格式
    - **desktop_version/build.py** - 简化的打包脚本，使用PyInstaller进行打包
    - **desktop_version/build.spec** - PyInstaller的构建规范文件，定义打包配置
- **docs** - Github Pages 官方设置的除 /(root) 目录下的默认二级目录，为了避免 Github Pages 设置为 /(root) 目录时默认网页为 README.md文件
    - **index.html** - Github Pages 官方默认 html 入口文件，Online-Webpages 版本利用单文件（HTML、CSS 和 JS 内联开发）实现
- **requirements.txt** - 项目依赖包列表
- **README.md** - 项目详细说明文档

---

## 🚢 部署说明

### Flask版本部署

**本地部署：**

```bash
python flask_version/app.py
```

### Streamlit版本部署

**本地部署：**

```bash
streamlit run streamlit_version/app.py
```

### Desktop版本部署

**打包为可执行文件：**

```bash
cd desktop_version
python build.py
```

生成的可执行文件位于 `desktop_version/dist/` 目录下。

**Note:** 打包过程可能需要安装PyInstaller和相关依赖，且仅支持Windows、macOS和Linux系统。

---

## 📝 注意事项

1. **网络要求**：应用需要访问外部API，请确保网络连接正常
2. **API限制**：搜索功能依赖于第三方API服务，如遇服务不可用请联系API提供方
3. **链接时效**：百度网盘链接可能存在时效性，如遇链接失效属正常现象
4. **数据安全**：应用仅进行搜索展示，不存储用户数据和搜索结果
5. **浏览器兼容**：建议使用*Chrome、Firefox、Safari*等现代浏览器

## 🐛 常见问题

**Q: 搜索没有结果怎么办？**

- A: 尝试使用更简单的关键词，检查网络连接，或稍后重试

**Q: 如何选择使用哪个版本？**

- A:
    - **Online-Webpage版本**：适合无需安装、即时访问、分享链接或部署在 *GitHub Pages* 的场景
    -  **Flask版本**：适合需要高度自定义界面的场景
    - **Streamlit版本**：适合快速开发和数据展示场景
    - **Desktop版本**：适合需要本地运行和跨平台支持的用户🚩

**Q: 可以同时运行多个版本吗？**

- A: 可以，但需要修改端口号避免冲突（*Flask* 默认 *5000*，*Streamlit* 默认 *8501* / *7777*），*Desktop* 版本和 *Online-Webpage* 版本不受影响

## 🙏 感谢

感谢以下开源项目和资源的支持：

- **[酷乐API](https://api.kuleu.com/)** 提供的*数据接口*
- [Flask](https://flask.palletsprojects.com/)、[Streamlit](https://streamlit.io/)、[Requests](https://docs.python-requests.org/)、[Pandas](https://pandas.pydata.org/) 等*Python*库，使项目得以实现
- [菜鸟图标](https://icon.sucai999.com/) 提供的图标资源

## 📄 许可证 & 声明

- **【项目声明】** 本项目为作者本人所设计，但部分代码由[AI](https://chatglm.cn)生成，复用时请认真辨别安全性后再使用，一切后果由使用者自行承担。
- **【使用声明】** 本项目仅用于学习和演示目的，请遵守相关法律法规，合理使用搜索功能，一切后果由使用者自行承担。
- **【其他信息与声明】**
  - **【关于 酷乐API】** 酷乐API是免费提供API数据接口调用服务平台 - 我们致力于为用户提供稳定、快速的免费API数据接口服务。
    - **【酷乐API - 免责声明】** 本网站提供的 API 为个人兴趣开发，仅供学习交流使用。所有数据均来源于公开渠道， 本站不对站点内容承担任何责任。任何单位或个人因使用本 API 所引发的任何问题， 本网站均不承担任何法律责任，一切后果由使用者自行承担。
    - **【网站】**酷乐API - 免费API数据接口调用服务平台*，访问链接：[https://api.kuleu.com/](https://api.kuleu.com/)
      - **【API接口】** 酷乐API提供的API接口，见项目文件 [kuleu_API_list.txt](kuleu_API_list.txt)

---

*最后更新: 2026年*
