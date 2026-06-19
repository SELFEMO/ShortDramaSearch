# 🎬 [短剧/影视资源聚合搜索](https://github.com/SELFEMO/ShortDramaSearch)

一个多版本的短剧/电视剧/电影资源搜索应用，提供Flask、Streamlit、Desktop和在线网页（Online-Webpage）四种实现方式，可以快速搜索短剧资源并获取百度网盘链接。

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

$^1$ 多个参数可以组合使用，需要使用`&`符号连接，例如：```https://selfemo.github.io/ShortDramaSearch/?q=飞驰人生3&from=netdisk&format=json```

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

Flask 版本已按 `docs/index.html` 的 GitHub Pages 页面重构：页面结构、视觉样式和交互逻辑直接对齐在线版，同时由 Flask 提供同源 API 代理与 `format=json` 直出能力，避免浏览器 CORS 或公开代理不稳定导致功能缺失。

### 主要功能

- **完整复刻 GitHub Pages 入口** - 保留聚合搜索、API 生成器、每日影视、热度榜、我的收藏、用户条例、二维码、深浅主题、搜索历史、收藏导入导出等页面能力。
- **同源接口代理** - 前端通过 `/api/kuleu/*` 调用 Flask，再由 Flask 请求酷乐 API，减少浏览器跨域限制和公开 CORS 代理失败带来的影响。
- **网页 API 模式** - 支持 `?q=关键词&from=来源&format=json` 直接返回 JSON，字段结构与在线网页 API 保持一致。
- **API 生成器可本地使用** - 生成的链接会指向当前 Flask 服务地址，可复制、打开并预览最多 5 条 JSON 结果。
- **多来源聚合搜索** - 支持 `all`、`netdisk`、`baidu`、`quark`、`aliyun`、`tianyi`、`uc`、`mobile`、`115`、`pikpak`、`xunlei`、`123`、`magnet`、`ed2k`。
- **提取码安全修正** - 服务端会优先从链接中的 `pwd` 参数恢复提取码，并保持字符串类型，避免 `32e7` 等内容被误解析为数字。
- **兼容旧接口入口** - 保留 `/search` POST 路由用于兼容旧调试页调用，但新版页面不再依赖旧版表格 UI。

### 文件结构

```text
flask_version/
├── app.py                         # Flask 服务端入口、同源代理、JSON API 模式
├── static/
│   └── index.assets/
│       ├── app.js                  # 从 docs/index.html 拆分并改为同源代理的前端逻辑
│       └── style.css               # 从 docs/index.html 拆分的完整样式
└── templates/
    └── index.html                  # GitHub Pages 版页面结构的 Flask/Jinja 模板
```

### 安装步骤

#### 前提条件

- Python 3.8 或更高版本
- pip 包管理工具
- 可以访问第三方酷乐 API 的网络环境

#### 1. 安装依赖

```bash
pip install flask requests
```

#### 2. 运行应用

```bash
python flask_version/app.py
```

#### 3. 访问应用

打开浏览器访问：

```text
http://localhost:5000
```

### 使用说明

#### 聚合搜索

1. 在首页输入短剧或影视资源关键词。
2. 选择搜索来源，例如 `全局聚合`、`网盘聚合`、`百度网盘`、`夸克网盘` 等。
3. 点击搜索按钮或按 Enter，页面会按来源分组展示结果。
4. 可对结果执行收藏、二维码分享、复制当前结果链接、标记疑似失效、质量评分等操作。

#### API 生成器

1. 进入页面顶部的 **API生成器**。
2. 输入关键词并选择来源。
3. 点击 **生成 API 链接** 或 **预览 JSON 结果**。
4. 生成链接格式如下：

```text
http://localhost:5000/?q=飞驰人生3&from=netdisk&format=json
```

#### 直接 JSON API

Flask 入口页支持与 GitHub Pages 版相同的参数：

| 参数名 | 别名 | 是否必填 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| `q` | `search`、`name`、`s`、`keyword` | 是 | 搜索关键词，支持空格拆词补召回 | 无 |
| `from` | `type` | 否 | 搜索来源，支持 `all`、`netdisk` 及单一来源 | `all` |
| `format` | 无 | 是 | 设置为 `json` 时直接返回 JSON | 网页模式 |

示例：

```bash
curl "http://localhost:5000/?q=飞驰人生3&from=netdisk&format=json"
```

返回结构示例：

```json
{
  "code": 0,
  "msg": "success",
  "keyword": "飞驰人生3",
  "type": "netdisk",
  "total": 6,
  "data": {
    "quark": [],
    "baidu": []
  }
}
```

### 同源代理接口

新版前端主要使用以下 Flask 代理接口：

| 路由 | 说明 |
| :--- | :--- |
| `/api/kuleu/jhsj?type=all&name=关键词` | 聚合资源搜索代理 |
| `/api/kuleu/yingshi?baidu` | 每日影视百度源代理 |
| `/api/kuleu/yingshi?quark` | 每日影视夸克源代理 |
| `/api/kuleu/shortdramarank` | 短剧热度榜代理 |
| `/api/kuleu/vtquark?tag=短剧` | 夸克热搜榜代理 |
| `/api/kuleu/ico?url=...` | 站点图标转发 |
| `/api/kuleu/qrcode?text=...` | 二维码图片转发 |
| `/api/search?q=关键词&from=来源` | Flask 服务端聚合后的 JSON 搜索接口 |
| `/api/daily` | Flask 服务端合并后的每日影视接口 |
| `/api/health` | 本地健康检查 |

### 自定义配置

可在 `flask_version/app.py` 顶部修改运行和请求参数：

```python
BASE_API = "https://api.kuleu.com/api"
REQUEST_TIMEOUT = 15
REQUEST_RETRIES = 2
SEARCH_RESULT_LIMIT = 200
SEARCH_RETRY_ATTEMPTS = 3
SEARCH_RETRY_DELAY = 0.7
CACHE_TTL_SECONDS = 60
```

本地端口在文件末尾调整：

```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

---

## 📊 [Streamlit 版本](https://github.com/SELFEMO/ShortDramaSearch/tree/master/streamlit_version)

### 主要功能

- **真实多页面结构** - 页面文件位于 `pages/`，不再依靠 `st.session_state.page` 在单文件内模拟切页。
- **API 层抽离** - 搜索、榜单、每日影视、二维码、JSON 解析和预览抽样统一放入 `services/api_client.py` 与 `services/normalizers.py`。
- **组件映射对齐** - `services/component_map.py` 明确记录 `docs/index.html` 的 `searchInput`、`resultsArea`、`apiGeneratedUrl`、`dailyResultsArea`、`rankListContainer`、`favoritesList` 等 DOM 组件在 Streamlit 中的对应实现。
- **不依赖 docs 路径** - Streamlit 运行时不会读取 `docs/index.html`，也不会把 HTML 文件当模板使用；所有能力均通过 Python 组件重新实现。
- **深色单主题界面** - 只保留深色模式，`.streamlit/config.toml` 固定为 dark theme，避免浅色模式造成视觉和组件尺寸不一致。
- **聚合搜索完整迁移** - 支持 `all`、`netdisk` 以及百度、夸克、阿里、天翼、UC、移动、115、PikPak、迅雷、123、磁力、电驴等单来源搜索。
- **关键词补搜策略** - 保留网页版本的“完整关键词优先 + 空格拆词补搜”策略，用于提升长标题资源召回率。
- **提取码安全处理** - `pwd` 字段始终按字符串保存，并优先从链接参数恢复，避免类似 `32e7` 被误解析为数字。
- **结果管理能力** - 支持按来源分组展示、收藏、疑似失效反馈、隐藏失效资源、本地质量评分、二维码、复制文本和 TXT 导出。
- **导入导出能力** - 搜索结果支持 CSV / JSON / TXT 下载，搜索历史和收藏支持 JSON 导入导出。
- **URL 参数兼容** - 入口页支持 `?q=关键词&from=all&format=json`；非 JSON 查询会自动带入聚合搜索页，JSON 查询会显示等价 JSON 视图并提供下载。
- **直接运行兼容** - 推荐使用 `streamlit run`；如果误用 `python streamlit_version/app.py`，程序会自动切换到 Streamlit runtime，避免 `missing ScriptRunContext` 警告刷屏。

### 安装步骤

#### 前提条件

- Python 3.8 或更高版本
- pip 或 conda 环境管理工具

#### 1. 安装依赖

```bash
pip install streamlit requests pandas
```

#### 2. 推荐运行方式

在项目根目录执行：

```bash
streamlit run streamlit_version/app.py
```

也可以使用当前 Python 环境的模块方式运行，适合多个 Python 环境并存的场景：

```bash
python -m streamlit run streamlit_version/app.py
```

如果在 IDE 中误点运行按钮，或直接执行下面命令，新版 `app.py` 会自动转交给 `python -m streamlit run`：

```bash
python streamlit_version/app.py
```

#### 3. 访问应用

当前仓库的 `streamlit_version/.streamlit/config.toml` 默认端口为 `7777`，因此通常访问：

```text
http://localhost:7777
```

如果临时指定端口运行：

```bash
streamlit run streamlit_version/app.py --server.port 8501
```

则访问：

```text
http://localhost:8501
```

当前配置文件内容如下：

```toml
[server]
port = 7777
headless = true

[browser]
gatherUsageStats = false

[theme]
base = "dark"
primaryColor = "#ff6b35"
backgroundColor = "#0a0a0f"
secondaryBackgroundColor = "#16161f"
textColor = "#f0f0f5"
```

---

## 🖥️ [Desktop 版本 (Qt5)](https://github.com/SELFEMO/ShortDramaSearch/tree/master/desktop_version)

### 主要功能

- **PyQt5 控件实现** - 使用 `QTabWidget`、`QListWidget` 卡片列表、`QDialog` 等 PyQt5 控件实现页面。
- **分辨率与 DPI 自适应** - 启动时读取主屏幕分辨率、可用工作区和系统 DPI，自动调整窗口大小、基础字号、标题字号、按钮内边距、页签内边距、列表卡片尺寸、弹窗尺寸和二维码尺寸；切换显示器或系统缩放变化后会刷新字体与控件尺寸。
- **卡片式结果展示** - 搜索结果、每日影视、API 预览和收藏不再使用窄列表格，而是改为可换行资源卡片；标题、来源、提取码、搜索词、链接、收藏、失效标记、质量评分和快捷操作都在同一张卡片内呈现，避免列宽压缩造成按钮残缺、文字被裁切或大面积留白。
- **聚合搜索对齐网页端** - 支持 `all`、`netdisk`、`baidu`、`quark`、`aliyun`、`tianyi`、`uc`、`mobile`、`115`、`pikpak`、`xunlei`、`123`、`magnet`、`ed2k`，并按网页端逻辑拆分空格关键词、合并去重、限制频率以降低 429 风险。
- **API 生成器** - 生成 `https://selfemo.github.io/ShortDramaSearch/?q=关键词&from=来源&format=json` 链接，可复制、打开，并在桌面端预览与网页 API 字段结构一致的 JSON。
- **热度榜卡片** - 支持短剧热度榜与夸克短剧热搜榜。
- **我的收藏** - 收藏保存在本机 `~/.short_drama_search/favorites.json`，支持搜索、导入、导出和清空。
- **卡片式搜索历史** - 自动保存最近 50 条搜索记录，历史项以关键词、结果数、时间和“重搜”按钮组成卡片，关闭横向滚动，支持双击重搜、导入、导出和清空。
- **统一美化自动隐藏滚动条** - 资源列表、历史列表、JSON 预览、榜单卡片、详情弹窗和用户条例弹窗都使用细圆角滚动条；无滚动范围时自动隐藏，有滚动时按需显示，停止操作后淡出。
- **本地失效标记与质量评分** - 可对链接做本地失效标记、隐藏失效链接，并为资源设置 0-5 星本地质量评分。
- **二维码与快捷操作** - 每张资源卡片内可直接打开链接、复制链接、复制密码、查看详情或调用二维码接口生成分享二维码。
- **浅色 / 深色 / 跟随系统主题** - “视图”菜单提供“浅色模式”“深色模式”“跟随系统（默认）”三种互斥选项；首次启动默认跟随系统，后续会保存用户选择，主题样式中的字号、控件尺寸、卡片背景、历史卡片、选中状态和榜单卡片颜色会使用当前屏幕缩放指标和有效主题动态生成。

### 本次桌面列表重构说明

旧版桌面列表沿用了表格思路，把“收藏”“失效”“评分”“来源”“名称”“链接”“密码”“搜索词/时间”全部塞进同一行。这个结构在资源标题很长、DPI 缩放较大或窗口分栏较窄时天然容易出现列宽互相抢占，最终表现为按钮被裁切、评分列挤压、链接看不全、历史记录出现横向滚动条。新版改为“资源卡片 + 历史卡片”：每条资源独占一张卡片，操作按钮内联在卡片中，历史记录也用关键词、结果数、时间和“重搜”按钮分层显示。这样牺牲少量纵向密度，换取更稳定的阅读性和操作可达性。

热度榜也已经从 `QTableWidget` 改为 `RankList + RankCard`。因为短剧热度榜和夸克热搜榜经常只返回排名与关键词，没有可展示的“热度 / 说明”字段，表格会产生一整列空白；同时“操作”列在高 DPI 或窗口较窄时会把“搜索”按钮压成逐字竖排。卡片式榜单按“排名徽章 + 关键词 + 可选说明 + 聚合搜索按钮”组织信息；没有说明时直接省略副文本，不再为每条结果重复显示“点击搜索”提示，也不再保留空列。

### 本次主题模式调整说明

桌面端主题入口已从单个“切换深浅主题”动作改为三项互斥菜单：“浅色模式”“深色模式”“跟随系统（默认）”。`settings.json` 中保存的是 `theme_mode`，其中 `system` 表示跟随系统偏好；没有 `theme_mode` 时默认按 `system` 处理，旧版本自动写入的 `theme=dark` 不再被当作用户主动选择，同时仍保留实际生效的 `theme` 字段用于兼容旧版本配置。Windows 下优先读取系统应用主题注册表，macOS 下读取 `AppleInterfaceStyle`，其他平台会结合环境变量和 Qt 调色板兜底。

资源卡片、每日影视卡片、API 预览卡片、收藏卡片和热度榜卡片在重建列表前都会调用 `set_visual_theme(current_theme)`，确保新增卡片与当前主题一致。卡片外框不再用 QSS 的 `background + border-radius` 直接绘制，而是通过 `paintEvent` 自绘圆角矩形；列表项选中背景保持透明，列表 viewport 负责填充当前主题背景，从而避免浅色模式下出现“深色卡片未切换”或“圆角后面还有方角底色”的问题。

### 本次悬浮状态提示与滚动条重构说明

主标题下方的独立状态提示行已经删除，底部 `QStatusBar` 也不再使用。`MainWindow.set_status()` 现在写入左下角悬浮 Toast：它是主窗口的子控件，不参与任何布局计算，因此不会占用页面高度，也不会挤压资源列表、历史列表或页签内容。忙碌状态使用 `timeout=0` 保持到任务结束，并由后续状态覆盖或清空；普通状态默认 5 秒后自动消失。二维码弹窗关闭时只清空二维码相关 Toast，不再显示“二维码窗口已关闭”这类无意义提示。

所有主要滚动区域新增 `ui/scrollbar.py` 中的 `AutoHideScrollBar`。它只替换 Qt 滚动条对象，不改变搜索、收藏、热度榜、JSON 预览等业务控件本身；有可滚动内容时才显示，鼠标悬停、拖动或滚轮操作时淡入，停止操作后自动淡出。全局 QSS 同时重新设计了浅色/深色主题下的细圆角滚动条颜色、尺寸和轨道样式，避免系统原生滚动条破坏桌面端整体视觉。


### 本次用户使用条例弹窗调整说明

用户使用条例正文较短，旧版使用 `QTextEdit` 作为可拉伸内容区并把对话框固定到较大的自适应高度，导致正文下面出现大量空白。新版将条例正文区改为固定紧凑高度，并让对话框按 `sizeHint()` 计算最终高度，只保留必要的阅读边距和底部确认按钮区域；小屏设备仍会受自适应高度上限保护。

### 本次按钮与下拉框修正说明

上一版按钮虽然减少了部分 padding，但 `QPushButton` 仍可能在 `QHBoxLayout` 中被横向拉伸，所以“清空”等短按钮会显得过宽。新版统一给按钮设置紧凑尺寸策略，让按钮按文字和自适应 padding 计算尺寸，不再主动占据多余空白。下拉框不再用 QSS 边框拼三角形，因为该做法在 Windows / Qt5 下可能渲染成难以理解的小横块；现在改用 `resources/icons/chevron_down_light.svg` 与 `chevron_down_dark.svg` 作为深浅主题箭头。`StableComboBox` 同时将下拉列表的 `autoScroll` 关闭，并把可见项数量收敛为 8，避免来源列表过长贴到屏幕底部；弹层窗口会额外应用圆角遮罩，弥补 Qt5 仅靠 QSS 难以稳定裁剪下拉列表底部圆角的问题。

### 安装步骤

#### 前提条件

- Python 3.8 或更高版本
- pip 或 conda 包管理工具
- 可以访问第三方酷乐 API 的网络环境

#### 1. 安装依赖

```bash
cd desktop_version
pip install -r requirements.txt
```

Conda 环境推荐：

```bash
conda activate py
conda install -c conda-forge pyqt
pip install requests pyinstaller qt-material fontawesome
```

> 注意：当前PyQt5 桌面版不需要 `PyQtWebEngine`。如果运行时仍出现 `PyQt5.QtWebEngineWidgets` 相关报错，说明本地文件仍是旧的 WebEngine 壳层版本，请覆盖为最新 `desktop_version` 代码。

#### 2. 运行应用

```bash
python main.py
```

首次启动时桌面版会根据当前主屏幕自动缩放界面。缩放逻辑同时参考：

- 屏幕分辨率，例如 1366x768、1920x1080、2560x1440、3840x2160。
- 系统 DPI / 缩放比例，例如 Windows 100%、125%、150%。
- 可用工作区大小，避免任务栏占用空间后窗口被裁切。

如果应用被移动到另一块显示器，或系统 DPI/分辨率发生变化，窗口会刷新字体、紧凑按钮、下拉框箭头区域、资源卡片、历史卡片、榜单卡片和弹窗尺寸。

也可以通过启动参数复刻网页 URL 参数体验：

```bash
python main.py --q "飞驰人生3" --from netdisk
python main.py --q "飞驰人生3" --from netdisk --json
```

其中：

- `--q / --keyword / --name / --search`：启动后自动搜索关键词。
- `--from / --source`：搜索来源，取值与网页端 `from` 参数一致。
- `--json`：启动后进入“API生成器”并预览 JSON。

#### 3. PowerShell 语法检查

PowerShell 不会把 `desktop_version/core/*.py` 直接展开给 `py_compile`。请使用以下命令：

```powershell
Get-ChildItem desktop_version -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
```

跨平台写法：

```bash
python -c "import pathlib, py_compile; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('desktop_version').rglob('*.py')]"
```

#### 4. 打包为可执行文件（可选）

```bash
cd desktop_version
python build.py
```

或直接使用 PyInstaller：

```bash
# Windows
pyinstaller --name=ShortDramaSearch --windowed --onefile --icon=resources/icons/API.ico --add-data="resources;resources" main.py

# macOS
pyinstaller --name=ShortDramaSearch --windowed --onefile --icon=resources/icons/API.icns --add-data="resources:resources" main.py

# Linux
pyinstaller --name=short-drama-search --windowed --onefile --icon=resources/icons/API.png --add-data="resources:resources" main.py
```

生成的可执行文件位于 `desktop_version/dist/` 目录。

### 使用说明

#### 聚合搜索

1. 打开“聚合搜索”。
2. 输入短剧 / 影视资源关键词。
3. 选择搜索来源，例如“全局聚合”“网盘聚合”“夸克网盘”。
4. 点击“搜索”或按回车。
5. 搜索结果会以资源卡片展示，每张卡片包含名称、来源、提取码、搜索词/时间、链接、收藏、失效标记、质量评分和快捷操作。
6. 标题和链接过长时会在卡片中做适度截断并保留 tooltip；点击“详情”可查看完整原始字段。

#### API 生成器

1. 打开“API生成器”。
2. 输入关键词并选择来源。
3. 点击“生成 API 链接”可生成 GitHub Pages JSON API 链接。
4. 点击“预览 JSON 结果”会在桌面端请求同一聚合接口，并展示最多 5 条预览数据，字段结构保持：

```json
{
  "code": 0,
  "msg": "success",
  "keyword": "飞驰人生3",
  "type": "netdisk",
  "total": 6,
  "data": {
    "quark": [],
    "baidu": []
  }
}
```

#### 每日影视

1. 打开“每日影视”。
2. 首次进入会自动请求每日资源，也可以点击“刷新”。
3. 使用顶部输入框按名称或链接进行本地过滤。

#### 热度榜

1. 打开“热度榜”。
2. 在“短剧热度榜”和“夸克热搜榜”之间切换。
3. 榜单以卡片展示排名、关键词和可选说明；如果接口没有说明字段，不会再出现空白说明列。
4. 双击榜单卡片或点击“聚合搜索”，会跳转到“聚合搜索”并自动搜索该关键词。

#### 我的收藏

- 收藏、搜索历史、失效标记、质量评分和主题设置都保存在本机用户目录：`~/.short_drama_search/`。
- 收藏和历史均支持导入 / 导出 JSON，便于备份或迁移。

### 文件职责

```text
desktop_version/
├── main.py                         # PyQt5 桌面入口，处理启动参数、应用图标和主窗口初始化
├── core/
│   ├── api_client.py               # 酷乐 API 客户端、聚合搜索、每日影视、榜单、二维码、JSON 预览数据构建
│   ├── data_manager.py             # 本地历史、收藏、失效标记、质量评分、主题设置和缓存管理
│   └── utils.py                    # 资源路径、平台判断、时间格式化、分辨率/DPI、悬浮状态提示与滚动条尺寸指标
├── ui/
│   ├── main_window.py              # PyQt5 多页主窗口、资源卡片列表、历史卡片、悬浮状态提示和全部交互逻辑
│   ├── detail_dialog.py            # 资源详情弹窗
│   └── scrollbar.py                # 统一细圆角自动隐藏滚动条
├── resources/                      # 图标、字体和可选样式资源
├── build.py                        # 跨平台 PyInstaller 打包脚本
├── build.spec                      # PyInstaller 构建配置
├── ShortDramaSearch.spec           # Windows 可执行文件构建配置
└── requirements.txt                # PyQt5 桌面版依赖，不包含 PyQtWebEngine
```

### 与 Online-Webpage 版本的关系

- Online-Webpage 版本仍由 `docs/index.html` 提供。
- Desktop 版本只参考 `docs/index.html` 的功能设计、接口参数、字段结构和用户体验，不嵌入网页、不打开本地 HTML、不依赖浏览器内核；结果展示采用更适合桌面端宽屏阅读的资源卡片，而不是强行复制网页表格。
- 桌面端“API生成器”生成的是 Online-Webpage 的 JSON API 链接；桌面端“预览 JSON”则由 Python 直接调用同一酷乐 API 后构造等价 JSON。

---

## 🗂️ 项目文件结构说明

- **flask_version** - Flask版本主目录
- **streamlit_version** - Streamlit版本主目录
- **desktop_version** - PyQt5 原生桌面应用主目录
- **docs** - Github Pages 官方设置的除 /(root) 目录下的默认二级目录，为了避免 Github Pages 设置为 /(root) 目录时默认网页为 README.md文件
  - **index.html** - 在线网页版本入口文件
  - **index.assets/** - 在线网页版本静态资源目录，包含 app.js 和 style.css
- **requirements.txt** - 项目依赖包列表
- **README.md** - 项目详细说明文档

---

## 🚢 部署说明

### Flask版本部署

**本地部署：**

```bash
pip install flask requests
python flask_version/app.py
```

访问 `http://localhost:5000`。如需 JSON API，可访问：

```text
http://localhost:5000/?q=飞驰人生3&from=netdisk&format=json
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
