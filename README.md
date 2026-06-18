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

### 使用说明

#### 聚合搜索

1. 进入“聚合搜索”页面。
2. 输入短剧、影视或资源关键词。
3. 在“搜索来源”中选择 `全局聚合`、`网盘聚合` 或单一来源。
4. 点击“🔍 搜索”，或在搜索框中按回车，即可查看按来源分组的结果。
5. 对任意结果可执行打开链接、收藏、失效反馈、质量评分、查看二维码和复制链接文本。

#### API 生成器

1. 打开“API 生成器”。
2. 输入关键词与来源类型。
3. 复制生成的 `?q=...&from=...&format=json` 链接。
4. 点击“预览 JSON 结果”可查看最多 5 条轮询抽样预览，并下载预览 JSON。

#### 每日影视

- 打开“每日影视”页面后点击“加载 / 刷新每日影视资源”。
- 页面会合并百度和夸克每日影视接口数据。
- 支持页面内关键词过滤，以及 CSV / JSON 导出。

#### 热度榜

- “热度榜”页面包含短剧热度榜与夸克热搜榜。
- 点击榜单条目的“搜索”按钮会自动进入聚合搜索页，并使用全局聚合查询该标题。

#### 我的收藏

- 搜索结果和每日影视结果均可收藏。
- 收藏页支持关键词过滤、导出收藏、导入收藏、清空收藏、失效标记和质量评分。
- 收藏与搜索历史保存在当前 Streamlit 会话状态中，刷新或重启服务后可能丢失；需要长期保存时请及时导出 JSON。

#### 用户条例 / 组件对齐说明

- “用户条例”页展示使用边界、免责说明和功能对齐范围。
- 每个业务页面都提供“组件映射 / docs/index.html alignment”折叠区，用于查看该页面与 `docs/index.html` 中 DOM 组件的对应关系。

### URL 参数说明

Streamlit 版本支持网页版本同名参数：

```text
?q=搜索关键词&from=all&format=json
```

可用参数：

- `q` / `s` / `name` / `keyword` / `search`：搜索关键词。
- `from`：搜索来源，支持 `all`、`netdisk`、`baidu`、`quark`、`aliyun`、`tianyi`、`uc`、`mobile`、`115`、`pikpak`、`xunlei`、`123`、`magnet`、`ed2k`。
- `format=json`：进入等价 JSON 结果页并提供下载。

示例：

```text
http://localhost:7777/?q=庆余年&from=all&format=json
```

### 常见问题

#### 为什么入口 `app.py` 几乎没有业务代码？

新版采用 Streamlit 多页面架构，`app.py` 只保留启动保护、URL 参数兼容和入口跳转。这样做可以避免单文件越来越大，也让 `pages/` 与 `services/` 的职责更清晰。

#### 为什么没有直接读取 `docs/index.html`？

Streamlit 版的目标是复刻 GitHub Pages 功能，而不是把 HTML 文件当模板嵌入。运行时读取 `docs/index.html` 会让部署路径变脆弱，也会把前端 DOM 生命周期和 Streamlit 生命周期混在一起，因此新版使用 `services/component_map.py` 维护静态组件映射，并用 Python 组件重新实现对应功能。

#### 为什么现在没有浅色模式？

当前 Streamlit 版的目标是保持与 GitHub Pages 深色视觉体验一致，并减少部署环境默认主题差异带来的尺寸和对比度问题。因此本版本移除了浅色模式入口，并通过配置文件固定为 dark theme。

#### 直接运行出现 `missing ScriptRunContext` 怎么办？

Streamlit 官方推荐通过 `streamlit run your_app.py` 启动应用。当前版本已经在 `services/runtime.py` 中加入自动启动保护：如果检测到你使用 `python streamlit_version/app.py` 裸跑，会自动重新调用 `python -m streamlit run streamlit_version/app.py`。

如果仍然无法打开页面，请确认当前环境已经安装 Streamlit：

```bash
python -m pip show streamlit
```

未安装时执行：

```bash
python -m pip install streamlit requests pandas
```

#### 为什么 `format=json` 不是浏览器纯文本响应？

GitHub Pages 版本可以直接在浏览器中改写页面内容；Streamlit 运行在自己的应用框架内，不能像静态 HTML 一样直接替换 HTTP 响应体。因此 Streamlit 版本提供等价 JSON 视图和下载按钮，数据结构与 API 生成器保持一致。

### 自定义配置

常用 API 与来源配置集中在：

```text
streamlit_version/services/constants.py
```

常用配置项包括：

```python
JHSJ_API = "https://api.kuleu.com/api/jhsj"
YINGSHI_API = "https://api.kuleu.com/api/yingshi"
SHORTDRAMA_RANK_API = "https://api.kuleu.com/api/shortdramarank"
VTQUARK_API = "https://api.kuleu.com/api/vtquark"
QRCODE_API = "https://api.kuleu.com/api/qrcode"
SEARCH_TIMEOUT = 15
RANK_TIMEOUT = 10
MAX_SEARCH_TOTAL = 200
MAX_HISTORY = 30
```

---

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
│   ├── app.py                     # Streamlit入口：启动保护、URL参数与页面跳转
│   ├── .streamlit/                # Streamlit配置
│   │   └── config.toml            # 深色主题与默认端口
│   ├── pages/                     # Streamlit多页面文件
│   │   ├── 1_search.py            # 聚合搜索页
│   │   ├── 2_api.py               # API生成器页
│   │   ├── 3_daily.py             # 每日影视页
│   │   ├── 4_rank.py              # 热度榜页
│   │   ├── 5_favorites.py         # 我的收藏页
│   │   └── 6_policy.py            # 用户条例页
│   └── services/                  # 业务服务层与通用UI组件
│       ├── api_client.py          # API请求、榜单、每日影视与预览数据
│       ├── component_map.py       # docs/index.html组件静态映射
│       ├── constants.py           # 常量、来源、页面配置
│       ├── normalizers.py         # 数据清洗与提取码修复
│       ├── pages.py               # 页面渲染逻辑
│       ├── runtime.py             # 启动与URL参数工具
│       ├── state.py               # 会话状态管理
│       └── ui.py                  # 深色主题、侧边栏与结果卡片
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
    - **streamlit_version/app.py** - Streamlit入口文件，负责启动保护、URL参数兼容和跳转到多页面入口
    - **streamlit_version/pages/** - 聚合搜索、API生成器、每日影视、热度榜、我的收藏和用户条例页面
    - **streamlit_version/services/** - API层、数据清洗、状态管理、组件映射和通用UI组件
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
