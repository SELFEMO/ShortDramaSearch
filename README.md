# 🎬 [短剧/影视资源聚合搜索](https://github.com/SELFEMO/ShortDramaSearch)

一个多版本的短剧 / 电视剧 / 电影资源聚合搜索应用，提供 **Online-Webpage、Flask、Streamlit、Desktop** 四种使用入口，可以快速检索影视资源并获取网盘或链接类结果。

> 注意：*2026 重构版本* 仍处于开发阶段（目前适配最好的版本为：Web在线版本），功能可能不稳定且界面并未完善，同时存在一些暂时无法修改的问题（Bug），欢迎贡献修复代码！

## 🌟 [项目简介](https://github.com/SELFEMO/ShortDramaSearch.git)

这是一个简单易用的影视资源聚合搜索工具。项目通过调用第三方 API 接口，将不同来源的短剧、影视、网盘和链接资源统一检索、分组展示，并提供在线网页、本地服务、数据展示和桌面客户端等多种运行方式。

**主要特性：**

- 🔍 **聚合搜索** - 输入短剧或影视名称即可检索多来源资源
- 📊 **结果统计** - 按来源分组显示结果数量和资源详情
- 🔗 **直接访问** - 支持一键打开网盘或资源链接
- 💾 **本地管理** - 支持收藏、搜索历史、导入导出等能力
- 📱 **响应式设计** - Web 页面适配 PC 与移动端浏览器
- ⚡ **API 模式** - 支持通过 URL 参数直接返回 JSON 数据

---

## 🚩 [Github 在线访问版本（Online-Webpage版本）](https://github.com/SELFEMO/ShortDramaSearch/tree/master/docs)

***🔗 Github Page 访问链接：[https://selfemo.github.io/ShortDramaSearch/](https://selfemo.github.io/ShortDramaSearch/)***

Online-Webpage 版本位于 `docs/` 目录，是当前适配最好的版本。该版本无需安装 Python 环境，直接通过浏览器访问即可使用。

### 主要功能

- **零安装使用** - 无需本地部署，打开 Github Pages 即可搜索
- **多来源聚合** - 支持全局聚合、网盘聚合和单一来源搜索
- **URL 参数搜索** - 支持通过链接直接发起搜索或返回 JSON
- **API 生成器** - 可生成可复制、可打开、可预览的 JSON API 链接
- **每日影视 / 热度榜** - 提供每日影视资源与短剧热度入口
- **收藏与历史** - 使用浏览器本地存储保存收藏、搜索历史和质量评分
- **二维码分享** - 支持为资源链接生成二维码，方便移动端访问
- **深浅主题** - 支持主题切换，并尽量跟随设备显示偏好

### 页面入口

| 页面文件 | 在线地址                                                                                                                                                                                                         | 说明 |
| :--- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| :--- |
| `docs/index.html` | [https://selfemo.github.io/ShortDramaSearch/](https://selfemo.github.io/ShortDramaSearch/) or [https://selfemo.github.io/ShortDramaSearch/index.html](https://selfemo.github.io/ShortDramaSearch/index.html) | 默认稳定版入口，适合作为主访问页面 |
| `docs/neo.html` | [https://selfemo.github.io/ShortDramaSearch/neo.html](https://selfemo.github.io/ShortDramaSearch/neo.html)                                                                                                   | 功能与默认版基本一致，采用 Neo 风格的新界面设计 |
| `docs/console.html` | [https://selfemo.github.io/ShortDramaSearch/console.html](https://selfemo.github.io/ShortDramaSearch/console.html)                                                                                           | 功能与默认版基本一致，界面参考 [Nuitfanee/ClickSync](https://github.com/Nuitfanee/ClickSync) 的控制台式视觉风格 |

> `neo.html` 与 `console.html` 主要是不同视觉风格的界面入口，核心搜索、收藏、API 生成器、每日影视和热度榜能力与默认在线版（`index.html`）保持一致。

#### 此外，该网站支持键入指定URL参数直接搜索（即 `https://selfemo.github.io/ShortDramaSearch/?参数=指定值` $^1$）

| 参数名 | 别名 | 是否必填 | 说明 | 默认值 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **q** | `name`、`s` | 否 | **搜索关键词**。支持中英文，支持空格拆分关键词以提高命中率。 | 无 | 参数值为短剧或影视名称，不需要添加引号 |
| **from** | 无 | 否 | **搜索来源**。指定搜索的网盘或链接来源。 | `all` | 请严格按照指定来源名称传入参数值 $^2$，例如：`from=netdisk` |
| **format** | 无 | 否 | **输出格式**。设为 `json` 时，页面将直接输出纯 JSON 数据，不渲染 UI 界面。 | 网页模式 (HTML) | 不传此参数或值不为 `json` 时，将渲染正常搜索界面并自动开始搜索 |

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

$^1$ 多个参数可以组合使用，需要使用 `&` 符号连接，例如：

```text
https://selfemo.github.io/ShortDramaSearch/?q=飞驰人生3&from=netdisk&format=json
```

$^2$ 参数 `from` 指定搜索来源，如下所示：

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

当访问类似下面的地址时，Online-Webpage 版本会作为一个简易 **JSON API 接口** 使用：

```text
https://selfemo.github.io/ShortDramaSearch/?q=飞驰人生3&from=netdisk&format=json
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

---

## 🚀 [Flask 版本](https://github.com/SELFEMO/ShortDramaSearch/tree/master/flask_version)

Flask 版本是 Online-Webpage 默认界面的本地服务化实现。它保留 `docs/index.html` 的页面结构和交互体验，同时由 Flask 提供同源 API 代理，适合本地运行、二次开发或需要减少浏览器跨域影响的场景。

### 主要功能

- **本地 Web 服务** - 通过 `http://localhost:5000` 访问本地页面
- **同源接口代理** - 前端通过 Flask 请求酷乐 API，降低 CORS 代理不稳定影响
- **JSON API 模式** - 支持 `?q=关键词&from=来源&format=json` 直接返回 JSON
- **聚合搜索能力** - 支持 `all`、`netdisk` 以及各类单一来源搜索
- **每日影视与榜单代理** - 提供每日影视、短剧热度榜、夸克短剧榜等接口代理
- **二维码与图标转发** - 保留网页端二维码和站点图标能力

### 文件结构

```text
flask_version/
├── app.py                          # Flask 服务入口、同源代理、JSON API 模式
├── static/
│   └── index.assets/
│       ├── app.js                  # 默认在线页面对应的前端逻辑
│       └── style.css               # 默认在线页面对应的样式
└── templates/
    └── index.html                  # Flask/Jinja 页面模板
```

### 安装与运行

#### 前提条件

- Python 3.8 或更高版本
- pip 包管理工具
- 可以访问第三方酷乐 API 的网络环境

#### 1. 安装依赖

```bash
pip install flask requests
```

#### 2. 启动服务

```bash
python flask_version/app.py
```

#### 3. 访问页面

```text
http://localhost:5000
```

#### 4. JSON API 示例

```bash
curl "http://localhost:5000/?q=飞驰人生3&from=netdisk&format=json"
```

### 常用接口

| 路由 | 说明 |
| :--- | :--- |
| `/` | 本地页面入口；带 `format=json` 时返回 JSON |
| `/api/search?q=关键词&from=来源` | 本地聚合搜索接口 |
| `/api/daily` | 合并后的每日影视资源接口 |
| `/api/health` | 本地健康检查接口 |
| `/api/kuleu/jhsj` | 酷乐聚合搜索代理 |
| `/api/kuleu/yingshi` | 酷乐每日影视代理 |
| `/api/kuleu/shortdramarank` | 短剧热度榜代理 |
| `/api/kuleu/vtquark` | 夸克短剧热搜代理 |
| `/api/kuleu/qrcode` | 二维码图片转发 |

> Flask 版本的 `neo.html` 与 `console.html` 入口会跳转到 Github Pages 线上页面，默认本地服务主要维护 `index.html` 稳定界面。

---

## 📊 [Streamlit 版本](https://github.com/SELFEMO/ShortDramaSearch/tree/master/streamlit_version)

Streamlit 版本适合以数据应用的方式快速展示搜索、榜单、收藏和导出能力。其入口文件保持轻量，负责页面配置、运行时检查和 URL 参数兼容，业务页面按 Streamlit 多页面思路组织。

### 主要功能

- **数据应用形态** - 更适合快速预览、筛选和导出搜索结果
- **深色主题** - 默认使用深色界面配置，减少不同系统主题导致的视觉差异
- **URL 参数兼容** - 入口逻辑保留 `q/from/format` 参数设计，尽量与在线版 API 体验保持一致
- **模块化页面设计** - 搜索、每日影视、热度榜、收藏和 API 预览可以按页面模块拆分维护

### 文件结构

```text
streamlit_version/
├── app.py                         # Streamlit 应用入口
├── .streamlit/
│   └── config.toml                # 端口与主题配置
├── pages/                         # Streamlit 多页面目录
│   ├── search.py                  # 聚合搜索
│   ├── api.py                     # API 生成器
│   ├── daily.py                   # 每日影视
│   ├── rank.py                    # 热度榜
│   ├── favorites.py               # 我的收藏
│   └── policy.py                  # 用户条例
└── services/                      # 业务逻辑与公共能力
    ├── api_client.py              # 第三方 API 请求与结果构建
    ├── component_map.py           # 网页版组件迁移映射
    ├── constants.py               # 常量、来源类型与页面配置
    ├── normalizers.py             # 数据清洗与字段标准化
    ├── pages.py                   # 各页面主体渲染逻辑
    ├── runtime.py                 # Streamlit 运行与跳转工具
    ├── state.py                   # session_state 状态管理
    ├── ui.py                      # 通用 UI、卡片、样式与导入导出
    └── __init__.py                # 包初始化文件
```

### 安装与运行

#### 前提条件

- Python 3.8 或更高版本
- pip 或 conda 环境管理工具
- 可以访问第三方酷乐 API 的网络环境

#### 1. 安装依赖

```bash
pip install streamlit requests pandas
```

#### 2. 推荐运行方式

```bash
streamlit run streamlit_version/app.py
```

也可以使用当前 Python 环境的模块方式运行：

```bash
python -m streamlit run streamlit_version/app.py
```

#### 3. 访问应用

当前配置默认端口为 `7777`：

```text
http://localhost:7777
```

> Streamlit 版本依赖完整的 Streamlit 业务模块配合运行。若只需要稳定使用，建议优先使用 Online-Webpage 版本。

---

## 🖥️ [Desktop 版本 (Qt5)](https://github.com/SELFEMO/ShortDramaSearch/tree/master/desktop_version)

Desktop 版本是基于 PyQt5 原生控件实现的本地桌面客户端。它不嵌入网页、不依赖浏览器内核，而是参考 Online-Webpage 的接口参数、字段结构和交互逻辑，以更适合桌面端阅读和管理的方式展示资源。

### 主要功能

- **PyQt5 原生界面** - 使用桌面控件实现聚合搜索、API 生成器、每日影视、热度榜和我的收藏
- **卡片式结果展示** - 资源以卡片形式展示，适合长标题、长链接和多操作按钮的桌面布局
- **本地数据管理** - 搜索历史、收藏、失效标记、质量评分和主题设置保存在本机用户目录
- **API 生成器** - 可生成 Online-Webpage 的 JSON API 链接，并在桌面端预览等价 JSON 数据
- **二维码分享** - 支持为资源链接生成二维码弹窗
- **自适应界面** - 根据屏幕分辨率、DPI 和系统缩放调整窗口、字体和控件尺寸
- **主题模式** - 支持浅色、深色和跟随系统主题
- **跨平台打包** - 可通过 PyInstaller 打包为 Windows、macOS 或 Linux 可执行文件

### 文件结构

```text
desktop_version/
├── main.py                         # PyQt5 桌面入口、启动参数和主窗口初始化
├── core/
│   ├── api_client.py               # 酷乐 API 客户端、聚合搜索、榜单、二维码、JSON 预览
│   ├── data_manager.py             # 本地历史、收藏、失效标记、质量评分、主题设置
│   └── utils.py                    # 平台判断、资源路径、时间格式、DPI/分辨率工具
├── ui/
│   ├── main_window.py              # 多页主窗口、资源卡片、榜单卡片和交互逻辑
│   ├── detail_dialog.py            # 资源详情弹窗
│   └── scrollbar.py                # 自动隐藏滚动条
├── resources/                      # 图标、字体和样式资源
├── build.py                        # 跨平台 PyInstaller 打包脚本
└── requirements.txt                # 桌面版依赖
```

### 安装与运行

#### 前提条件

- Python 3.8 或更高版本
- pip 或 conda 包管理工具
- 可以访问第三方酷乐 API 的网络环境

#### 1. 安装依赖

```bash
cd desktop_version
pip install -r requirements.txt
```

#### 2. 运行应用

```bash
python main.py
```

也可以通过启动参数模拟网页 URL 参数体验：

```bash
python main.py --q "飞驰人生3" --from netdisk
python main.py --q "飞驰人生3" --from netdisk --json
```

#### 3. 打包为可执行文件（可选）

```bash
cd desktop_version
python build.py
```

生成文件位于：

```text
desktop_version/dist/
```

> Desktop 版本的界面和交互逻辑仍在持续完善中，由于作者本人的前端开发能力有限，目前可能存在一些界面适配问题、交互不够流畅的情况，欢迎有能力的开发者贡献代码进行优化。

---

## 🗂️ 项目文件结构说明

```text
ShortDramaSearch/
├── docs/                           # Github Pages 在线网页版本
│   ├── index.html                  # 默认稳定入口
│   ├── index.assets/               # 默认界面静态资源
│   ├── neo.html                    # Neo 新界面入口
│   ├── neo.assets/                 # Neo 界面静态资源
│   ├── console.html                # Console 控制台风格入口
│   └── console.assets/             # Console 界面静态资源
├── flask_version/                  # Flask 本地 Web 版本
├── streamlit_version/              # Streamlit 数据应用版本
├── desktop_version/                # PyQt5 原生桌面版本
├── kuleu_API_list.txt              # 酷乐 API 相关接口记录
├── requirements.txt                # 项目综合依赖列表
├── LICENSE                         # 开源许可证
└── README.md                       # 项目说明文档
```

---

## 🚢 部署说明

### Online-Webpage版本部署

Github Pages 建议选择 `docs/` 目录作为发布目录。部署后默认访问：

```text
https://selfemo.github.io/ShortDramaSearch/
```

### Flask版本部署

```bash
pip install flask requests
python flask_version/app.py
```

访问：

```text
http://localhost:5000
```

### Streamlit版本部署

```bash
pip install streamlit requests pandas
streamlit run streamlit_version/app.py
```

访问：

```text
http://localhost:7777
```

### Desktop版本部署

```bash
cd desktop_version
pip install -r requirements.txt
python main.py
```

如需打包：

```bash
python build.py
# Desktop 版本生成的可执行文件位于 `desktop_version/dist/` 目录，直接运行即可使用。
```

---

## 📝 注意事项

1. **网络要求**：应用需要访问外部 API，请确保网络连接正常。
2. **接口限制**：搜索功能依赖第三方 API 服务，如遇请求频繁、超时或服务不可用，可稍后重试。
3. **链接时效**：网盘链接可能存在时效性，资源失效属于正常情况。
4. **本地数据**：Web 端收藏与历史主要保存在浏览器本地存储；Desktop 端数据保存在本机用户目录。
5. **浏览器兼容**：Online-Webpage 版本建议使用 Chrome、Edge、Firefox、Safari 等现代浏览器。
6. **开发阶段**：2026 重构版本仍在持续完善，Web 在线版本目前优先级最高。

---

## 🐛 常见问题

**Q: 搜索没有结果怎么办？**

- A: 可以尝试更短或更准确的关键词，切换搜索来源，检查网络连接，或稍后重试。

**Q: 应该优先使用哪个版本？**

- A:
  - **Online-Webpage版本**：适合无需安装、直接访问、分享链接或部署到 Github Pages 的场景。
  - **Flask版本**：适合本地 Web 服务、接口代理和二次开发场景。
  - **Streamlit版本**：适合快速数据展示、筛选和导出场景。
  - **Desktop版本**：适合需要本地客户端、收藏管理和桌面操作体验的场景。

**Q: 可以同时运行多个版本吗？**

- A: 可以。Flask 默认端口为 `5000`，Streamlit 当前配置默认端口为 `7777`，如端口冲突可手动调整；Desktop 版本和 Online-Webpage 版本不受端口影响。

**Q: `index.html`、`neo.html`、`console.html` 有什么区别？**

- A: 三者核心功能基本一致，主要区别是视觉风格不同。`index.html` 是默认稳定入口，`neo.html` 是 Neo 新界面，`console.html` 是参考 Nuitfanee/ClickSync 控制台风格的设计入口。

---

## 🙏 感谢

感谢以下开源项目和资源的支持：

- **[酷乐API](https://api.kuleu.com/)** 提供的数据接口
- **[Flask](https://flask.palletsprojects.com/)** 提供本地 Web 服务能力
- **[Streamlit](https://streamlit.io/)** 提供数据应用展示能力
- **[PyQt5](https://riverbankcomputing.com/software/pyqt/)** 提供桌面应用界面能力
- **[Requests](https://docs.python-requests.org/)**、**[Pandas](https://pandas.pydata.org/)** 等 Python 库提供基础支持
- **[Nuitfanee/ClickSync](https://github.com/Nuitfanee/ClickSync)** 为 Console 设计版提供视觉参考
- **[菜鸟图标](https://icon.sucai999.com/)** 提供图标资源参考

---

## 📄 许可证 & 声明

- **【项目声明】** 本项目为作者本人所设计，但部分代码由 AI 辅助生成，复用时请认真辨别安全性后再使用，一切后果由使用者自行承担。
- **【使用声明】** 本项目仅用于学习和演示目的，请遵守相关法律法规，合理使用搜索功能，一切后果由使用者自行承担。
- **【其他信息与声明】**
  - **【关于 酷乐API】** 酷乐API 是免费提供 API 数据接口调用服务的平台，项目仅调用公开接口进行结果展示。
  - **【酷乐API - 免责声明】** 第三方 API 数据来源于公开渠道，本项目不对资源内容、可用性、时效性或使用后果承担责任。
  - **【API接口】** 酷乐 API 相关接口可参考项目文件 [kuleu_API_list.txt](kuleu_API_list.txt)。

---

*最后更新: 2026年*
