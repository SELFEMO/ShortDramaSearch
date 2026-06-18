(function () {
    const currentScript = document.currentScript;
    const phase = currentScript ? currentScript.getAttribute('data-kuleu-script-phase') : 'main';

    if (phase === 'bootstrap') {
        // 中文：首屏主题与路由必须在 CSS 和主体渲染前执行，因此同一个外部脚本通过 bootstrap 阶段先完成关键状态写入。
        // English: First-paint theme and route state must run before CSS and body rendering, so the shared external script uses a bootstrap phase for critical state writes.
    // ---- bootstrap block 1 ----
    (function () {
                const MANUAL_THEME_KEY = 'kuleu_theme_manual';
                const THEME_MODE_KEY = 'kuleu_theme_mode';
                const LEGACY_THEME_KEY = 'kuleu_theme';

                function safeStorageGet(key) {
                    try {
                        return window.localStorage.getItem(key);
                    } catch (error) {
                        return null;
                    }
                }

                function safeStorageRemove(key) {
                    try {
                        window.localStorage.removeItem(key);
                    } catch (error) {}
                }

                function getSystemThemeEarly() {
                    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                        return 'light';
                    }
                    return 'dark';
                }

                safeStorageRemove(LEGACY_THEME_KEY);

                const themeMode = safeStorageGet(THEME_MODE_KEY);
                const manualTheme = safeStorageGet(MANUAL_THEME_KEY);
                const hasManualTheme = themeMode === 'manual' && (manualTheme === 'light' || manualTheme === 'dark');

                if (!hasManualTheme) {
                    safeStorageRemove(MANUAL_THEME_KEY);
                }

                // 中文：只有新版显式写入手动模式时才使用缓存主题，否则首屏始终跟随当前设备系统主题。
                // English: Cached themes are honored only after the new explicit manual mode is set; otherwise first paint follows the current device theme.
                const theme = hasManualTheme ? manualTheme : getSystemThemeEarly();
                const root = document.documentElement;
                root.setAttribute('data-theme', theme);
                root.setAttribute('data-theme-source', hasManualTheme ? 'manual' : 'system');
                root.classList.toggle('theme-light', theme === 'light');
                root.style.colorScheme = theme;
            })();

    // ---- bootstrap block 2 ----
    (function () {
                function getInitialNeoPageFromHash() {
                    const hash = window.location.hash || '#/';
                    const routePath = hash.split('?')[0];

                    // 中文：hash 可能带有 ?from=baidu 这类可分享状态，首屏判断只使用路径部分，避免把搜索页误判成默认页。
                    // English: The hash may carry shareable state such as ?from=baidu, so first-paint routing uses only the path portion to avoid misclassifying the search page.
                    if (routePath === '#/api') return 'api';
                    if (routePath === '#/daily') return 'daily';
                    if (routePath === '#/rank') return 'rank';
                    if (routePath === '#/favorites') return 'favorites';
                    return 'search';
                }

                const page = getInitialNeoPageFromHash();
                const root = document.documentElement;

                // 中文：首屏渲染前先把当前 hash 对应页面写到 html，避免默认搜索页先闪出后再被路由脚本二次切换。
                // English: The initial hash route is written before first paint so the default search page does not flash before the router syncs.
                root.classList.add(`neo-route-${page}`);
                root.setAttribute('data-neo-route', page);
            })();
        return;
    }

    // 中文：主逻辑仍在页面底部阶段执行，使用闭包隔离拆分后的资源，同时显式导出 HTML 内联事件需要的入口。
    // English: Main logic still runs at the original bottom-of-page phase; a closure isolates the split asset while explicitly exporting entries used by inline HTML handlers.
    (function () {
        // ==================== 公共配置 ====================
            const JHSJ_API = 'https://api.kuleu.com/api/jhsj';
            const YINGSHI_API = 'https://api.kuleu.com/api/yingshi';
            const SHORTDRAMA_RANK_API = 'https://api.kuleu.com/api/shortdramarank';
            const VTQUARK_API = 'https://api.kuleu.com/api/vtquark?tag=短剧';
            const ICO_API = 'https://api.kuleu.com/api/ico';
            const QRCODE_API = 'https://api.kuleu.com/api/qrcode';
            const CORS_PROXIES = ['https://cors.sh/', 'https://api.allorigins.win/raw?url=', 'https://corsproxy.io/?'];
            const SEARCH_TIMEOUT = 15000;
            const TYPE_LABEL = { baidu: '百度网盘', aliyun: '阿里云盘', quark: '夸克网盘', tianyi: '天翼云盘', uc: 'UC网盘', mobile: '移动云盘', '115': '115网盘', pikpak: 'PikPak', xunlei: '迅雷网盘', '123': '123网盘', magnet: '磁力链接', ed2k: '电驴链接' };
            const TYPE_PRESETS = { all: ['baidu','aliyun','quark','tianyi','uc','mobile','115','pikpak','xunlei','123','magnet','ed2k'], netdisk: ['baidu','aliyun','quark','tianyi','uc','mobile','115','pikpak','xunlei','123'], baidu: ['baidu'], quark: ['quark'], aliyun: ['aliyun'], tianyi: ['tianyi'], uc: ['uc'], mobile: ['mobile'], '115': ['115'], pikpak: ['pikpak'], xunlei: ['xunlei'], '123': ['123'], magnet: ['magnet'], ed2k: ['ed2k'] };

            // ==================== DOM ====================
            const searchInput = document.getElementById('searchInput');
            const searchBtn = document.getElementById('searchBtn');
            const resultsArea = document.getElementById('resultsArea');
            const titleLogo = document.getElementById('titleLogo');
            const searchStatus = document.getElementById('searchStatus');
            const typeSelect = document.getElementById('typeSelect');

            function setResultsAreaMode(mode) {
                if (!resultsArea) return;

                // 中文：结果区按状态切换外框样式，避免初始空状态出现上下比例失衡的“大下巴”。
                // English: Result-area framing is state-based so the initial idle hint never inherits an oversized search-result shell.
                resultsArea.classList.remove('is-idle', 'is-busy', 'has-results', 'is-feedback');

                if (mode) {
                    resultsArea.classList.add(mode);
                }
            }
            const dailySearchInput = document.getElementById('dailySearchInput');
            const dailyRefreshBtn = document.getElementById('dailyRefreshBtn');
            const dailyStats = document.getElementById('dailyStats');
            const dailyResultsArea = document.getElementById('dailyResultsArea');
            const rankSearchInput = document.getElementById('rankSearchInput');
            const rankListContainer = document.getElementById('rankListContainer');
            const appTitleEl = document.getElementById('appTitle');

            const apiKeywordInput = document.getElementById('apiKeywordInput');
            const apiFromSelect = document.getElementById('apiFromSelect');
            const apiGeneratedUrl = document.getElementById('apiGeneratedUrl');
            const apiGenerateBtn = document.getElementById('apiGenerateBtn');
            const apiCopyBtn = document.getElementById('apiCopyBtn');
            const apiOpenLink = document.getElementById('apiOpenLink');
            const apiPreviewBtn = document.getElementById('apiPreviewBtn');

            const apiPreviewStatus = document.getElementById('apiPreviewStatus');
            const apiPreviewOutput = document.getElementById('apiPreviewOutput');
            const apiPreviewLinksStatus = document.getElementById('apiPreviewLinksStatus');
            const apiPreviewLinksList = document.getElementById('apiPreviewLinksList');

            const helpApiTemplateUrl = document.getElementById('helpApiTemplateUrl');
            const helpApiExampleUrl = document.getElementById('helpApiExampleUrl');

            const searchHistoryPanel = document.getElementById('searchHistoryPanel');
            const searchHistoryList = document.getElementById('searchHistoryList');
            const clearHistoryBtn = document.getElementById('clearHistoryBtn');

            const favoriteSearchInput = document.getElementById('favoriteSearchInput');
            const clearFavoritesBtn = document.getElementById('clearFavoritesBtn');
            const favoritesStats = document.getElementById('favoritesStats');
            const favoritesList = document.getElementById('favoritesList');

            // ==================== 路由与工具函数 ====================
            const pages = {
                search: document.getElementById('page-search'),
                api: document.getElementById('page-api'),
                daily: document.getElementById('page-daily'),
                rank: document.getElementById('page-rank'),
                favorites: document.getElementById('page-favorites')
            };

            const titles = {
                search: '酷乐短剧 / 影视资源 Neo · <span>聚合搜索</span>',
                api: '酷乐短剧 / 影视资源 Neo · <span>API生成器</span>',
                daily: '酷乐短剧 / 影视资源 Neo · <span>每日影视</span>',
                rank: '酷乐短剧 / 影视资源 Neo · <span>热度榜</span>',
                favorites: '酷乐短剧 / 影视资源 Neo · <span>我的收藏</span>'
            };

            function parseNeoHashRoute(rawHash = window.location.hash) {
                const hash = rawHash || '#/';
                const [routePathRaw, queryString = ''] = hash.split('?');
                const routePath = routePathRaw || '#/';

                let page = 'search';
                if (routePath === '#/api') page = 'api';
                if (routePath === '#/daily') page = 'daily';
                if (routePath === '#/rank') page = 'rank';
                if (routePath === '#/favorites') page = 'favorites';

                // 中文：把 hash 路径和参数集中解析，后续来源筛选、路由高亮和浏览器前进后退都能使用同一份状态。
                // English: Hash path and parameters are parsed in one place so source filters, route highlighting, and browser history all share the same state.
                return {
                    page,
                    params: new URLSearchParams(queryString)
                };
            }

            function getPageFromHash() {
                return parseNeoHashRoute().page;
            }

            function getHashSourcePreset(rawHash = window.location.hash) {
                const { params } = parseNeoHashRoute(rawHash);
                const source = (params.get('from') || 'all').toLowerCase();

                return TYPE_PRESETS[source] ? source : 'all';
            }

            function getSearchHashForSource(sourceName = currentPreset) {
                const source = TYPE_PRESETS[sourceName] ? sourceName : 'all';

                if (source === 'all') return '#/';
                return `#/search?from=${encodeURIComponent(source)}`;
            }

            function getHashFromPage(pageName, options = {}) {
                if (pageName === 'api') return '#/api';
                if (pageName === 'daily') return '#/daily';
                if (pageName === 'rank') return '#/rank';
                if (pageName === 'favorites') return '#/favorites';

                const sourceName = options.sourceName || currentPreset || getHashSourcePreset();
                return getSearchHashForSource(sourceName);
            }

            function syncNeoRouteClass(pageName) {
                const finalPage = pages[pageName] ? pageName : 'search';
                const root = document.documentElement;
                const routeNames = ['search', 'api', 'daily', 'rank', 'favorites'];

                routeNames.forEach(key => {
                    root.classList.toggle(`neo-route-${key}`, key === finalPage);
                });

                // 中文：路由类与实际页面状态保持同步，CSS 首屏兜底和 JS 路由不会互相打架。
                // English: The route class stays aligned with the actual page so first-paint CSS and the JS router never fight each other.
                root.setAttribute('data-neo-route', finalPage);
            }

            function navigateTo(pageName, options = {}) {
                const finalPage = pages[pageName] ? pageName : 'search';
                const currentPage = document.body ? document.body.dataset.neoPage : '';
                const isSamePage = currentPage === finalPage;

                if (isSamePage && options.force !== true) {
                    syncNeoRouteClass(finalPage);
                    if (finalPage === 'search') {
                        applySearchSourceFromHash();
                    }
                    document.documentElement.classList.add('neo-router-ready');
                    updatePageScrollbar();
                    if (typeof window.neoRequestCondensedNavSync === 'function') {
                        // 中文：同页同步也可能发生在移动端短页面上，重新评估可避免保留不该出现的菜单收缩态。
                        // English: Same-page sync can also happen on short mobile pages, so re-evaluation prevents keeping an invalid condensed menu state.
                        window.requestAnimationFrame(window.neoRequestCondensedNavSync);
                    }
                    return;
                }

                /*
                     * 中文：这里关闭页面路由的整页 View Transition，因为移动端下拉菜单收起、页面显隐和 active 状态同时变化时会出现明显卡顿与形变。
                     * English: Full-page route View Transitions are disabled here because mobile dropdown closing, page visibility changes, and active-state updates can otherwise combine into visible jank and morphing.
                     */
                const shouldAnimate = false;

                const applyNavigationState = () => {
                    Object.keys(pages).forEach(key => {
                        pages[key].classList.toggle('active', key === finalPage);
                    });

                    /*
                         * 关键修复：
                         * 这里只处理真正的页面导航按钮。
                         * GitHub / 帮助 没有 data-page，不参与 active 状态。
                         */
                    document.querySelectorAll('.nav-link[data-page]').forEach(link => {
                        link.classList.toggle('active', link.dataset.page === finalPage);
                    });

                    appTitleEl.innerHTML = titles[finalPage] || titles.search;
                    syncNeoRouteClass(finalPage);
                    document.documentElement.classList.add('neo-router-ready');

                    if (document.body) {
                        document.body.dataset.neoPage = finalPage;
                    }

                    if (finalPage === 'search') {
                        applySearchSourceFromHash();
                    }

                    if (finalPage === 'api') {
                        setTimeout(() => {
                            updateApiGeneratedUrl();
                        }, 50);
                    }

                    if (finalPage === 'daily') loadDailyResources();
                    if (finalPage === 'rank') initRankPage();

                    /*
                         * 移动端某些浏览器会残留 hover / focus 状态，
                         * 主动 blur 可以避免两个按钮看起来同时被选中。
                         */
                    if (document.activeElement && document.activeElement.blur) {
                        document.activeElement.blur();
                    }
                };

                if (shouldAnimate && document.startViewTransition) {
                    document.documentElement.classList.add('route-switching');

                    // 中文：只在真实页面切换时启用 View Transition，避免同一路由或初始化阶段重复播放动画。
                    // English: View Transition is used only for real route changes so same-route and initial sync never replay animations.
                    const transition = document.startViewTransition(applyNavigationState);

                    transition.finished.finally(() => {
                        document.documentElement.classList.remove('route-switching');
                        updatePageScrollbar();
                    });

                    return;
                }

                if (shouldAnimate) {
                    document.documentElement.classList.add('neo-fallback-route');
                    applyNavigationState();

                    window.setTimeout(() => {
                        document.documentElement.classList.remove('neo-fallback-route');
                        updatePageScrollbar();
                    }, 640);

                    return;
                }

                applyNavigationState();
                updatePageScrollbar();
                if (typeof window.neoRequestCondensedNavSync === 'function') {
                    // 中文：页面切换后内容高度会变化，下一帧再判断导航是否仍有足够空间进入收缩态。
                    // English: Page content height changes after navigation, so the next frame checks whether there is still enough room for condensed nav.
                    window.requestAnimationFrame(window.neoRequestCondensedNavSync);
                }
            }

            let lastHandledHash = window.location.hash || '#/';
            let lastTouchNavTime = 0;

            function pushNeoRouteHash(targetHash) {
                if (window.location.hash === targetHash) return;

                if (window.history && window.history.pushState) {
                    // 中文：使用 pushState 更新 hash，避免 hashchange 立即再次触发 navigateTo，造成页面像加载了两遍。
                    // English: pushState updates the hash without firing hashchange immediately, preventing the route from rendering twice.
                    window.history.pushState(null, '', targetHash);
                    lastHandledHash = targetHash;
                    return;
                }

                lastHandledHash = targetHash;
                window.location.hash = targetHash;
            }

            function closeCondensedNavBeforeRoute() {
                const root = document.documentElement;
                const menuBtn = document.getElementById('neoNavMenuBtn');
                const isCondensed = document.body && document.body.classList.contains('neo-nav-condensed');
                const isMenuOpen = document.body && document.body.classList.contains('neo-nav-menu-open');

                if (!isCondensed && !isMenuOpen) return;

                /*
                     * 中文：路由切换只进入瞬时隐藏状态，不再给菜单容器写入行内 display 样式，避免恢复时出现一帧宽面板或半屏遮挡。
                     * English: Routing only enters instant-hidden mode and no longer writes inline display styles to the menu container, preventing a one-frame wide panel or half-screen mask when it is restored.
                     */
                root.classList.add('neo-route-instant');

                if (document.body) {
                    document.body.classList.remove('neo-nav-menu-open');
                }

                if (menuBtn) {
                    menuBtn.setAttribute('aria-expanded', 'false');
                }
            }

            function switchPageByNav(pageName) {
                if (!pages[pageName]) return;

                const targetHash = getHashFromPage(pageName);
                const root = document.documentElement;

                /*
                     * 中文：先关闭并瞬时隐藏下拉菜单，再同步切换页面；整个过程不触发菜单宽度动画、页面快照或额外重绘遮罩。
                     * English: The dropdown is closed and instantly hidden before the page changes synchronously, so no menu-width animation, page snapshot, or extra repaint mask is produced.
                     */
                closeCondensedNavBeforeRoute();
                navigateTo(pageName, { animate: false });
                pushNeoRouteHash(targetHash);

                window.requestAnimationFrame(() => {
                    root.classList.remove('neo-route-instant');
                    updatePageScrollbar();
                    if (typeof window.neoRequestCondensedNavSync === 'function') {
                        // 中文：从收缩下拉菜单切到短页面时，要在菜单隐藏后重新计算，否则会残留收缩态并触发回弹闪屏。
                        // English: When switching from the condensed dropdown to a short page, re-compute after the menu hides or the condensed state can linger and cause bounce flicker.
                        window.neoRequestCondensedNavSync();
                    }
                });
            }

            function bindNeoNavPointerMotion() {
                const navLinks = document.querySelectorAll('.neo-ui .nav-link[data-page]');

                navLinks.forEach(link => {
                    if (link.dataset.neoPointerBound === '1') return;
                    link.dataset.neoPointerBound = '1';

                    link.addEventListener('pointermove', event => {
                        const rect = link.getBoundingClientRect();
                        const x = ((event.clientX - rect.left) / rect.width) * 100;
                        const y = ((event.clientY - rect.top) / rect.height) * 100;

                        // 中文：让导航高光跟随指针移动，增加现代交互感，同时只写 CSS 变量避免重排。
                        // English: The nav highlight follows the pointer through CSS variables, adding polish without forcing layout recalculation.
                        link.style.setProperty('--neo-pointer-x', `${x.toFixed(2)}%`);
                        link.style.setProperty('--neo-pointer-y', `${y.toFixed(2)}%`);
                    });
                });
            }

            function initRouter() {
                navigateTo(getPageFromHash(), { animate: false });

                const handleHistoryRouteChange = () => {
                    const currentHash = window.location.hash || '#/';
                    if (currentHash === lastHandledHash && document.body && document.body.dataset.neoPage === getPageFromHash()) {
                        return;
                    }

                    lastHandledHash = currentHash;
                    navigateTo(getPageFromHash());
                };

                window.addEventListener('hashchange', handleHistoryRouteChange);
                window.addEventListener('popstate', handleHistoryRouteChange);

                bindNeoNavPointerMotion();

                const navLinksContainer = document.querySelector('.app-nav-links');
                if (!navLinksContainer) return;

                /*
                     * 移动端优先用 pointerup，避免部分浏览器第一次 tap 只触发 hover。
                     */
                navLinksContainer.addEventListener('pointerup', e => {
                    if (e.pointerType === 'mouse') return;

                    const link = e.target.closest('.nav-link[data-page]');
                    if (!link) return;

                    e.preventDefault();
                    lastTouchNavTime = Date.now();

                    switchPageByNav(link.dataset.page);
                }, { passive: false });

                /*
                     * 桌面端 / 不支持 PointerEvent 的浏览器走 click。
                     * 如果刚刚已经由 pointerup 处理过，则忽略这次 click，避免重复切换。
                     */
                navLinksContainer.addEventListener('click', e => {
                    const link = e.target.closest('.nav-link[data-page]');
                    if (!link) return;

                    if (Date.now() - lastTouchNavTime < 500) {
                        e.preventDefault();
                        return;
                    }

                    e.preventDefault();
                    switchPageByNav(link.dataset.page);
                });
            }

            /**
             * 点击顶部“酷乐短剧 / 影视资源”标题刷新网页。
             */
            function bindAppTitleRefresh() {
                if (!appTitleEl) return;

                appTitleEl.title = '点击刷新网页';
                appTitleEl.setAttribute('role', 'button');
                appTitleEl.setAttribute('tabindex', '0');

                appTitleEl.addEventListener('click', () => {
                    window.location.reload();
                });

                appTitleEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        window.location.reload();
                    }
                });
            }

            function showStatus(message, duration = 2000) { searchStatus.textContent = message; searchStatus.classList.add('show'); setTimeout(() => searchStatus.classList.remove('show'), duration); }
            function escapeHtml(text) { if (!text) return ''; return String(text).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[s])); }

            function safeJsonParse(text, fallback) {
                try {
                    return JSON.parse(text);
                } catch (e) {
                    return fallback;
                }
            }

            const LOCAL_KEYS = {
                history: 'kuleu_search_history_v1',
                favorites: 'kuleu_favorites_v1',
                broken: 'kuleu_broken_links_v1',
                quality: 'kuleu_resource_quality_v1',
                hideBroken: 'kuleu_hide_broken_v1'
            };

            function readLocalList(key) {
                const data = safeJsonParse(localStorage.getItem(key), []);
                return Array.isArray(data) ? data : [];
            }

            function writeLocalList(key, list) {
                localStorage.setItem(key, JSON.stringify(list));
            }

            function makeResourceId(link) {
                return encodeURIComponent(String(link || '').trim());
            }

            function getSearchHistory() {
                return readLocalList(LOCAL_KEYS.history);
            }

            function saveSearchHistory(term) {
                const keyword = normalizeSearchKeyword(term);
                if (!keyword) return;

                const oldList = getSearchHistory();
                const nextList = [
                    keyword,
                    ...oldList.filter(item => item !== keyword)
                ].slice(0, 12);

                writeLocalList(LOCAL_KEYS.history, nextList);
                renderSearchHistory();
            }

            function clearSearchHistory() {
                writeLocalList(LOCAL_KEYS.history, []);
                renderSearchHistory();
            }

            function getFavorites() {
                return readLocalList(LOCAL_KEYS.favorites);
            }

            function saveFavorites(list) {
                writeLocalList(LOCAL_KEYS.favorites, list);
            }

            function isFavorited(link) {
                const id = makeResourceId(link);
                return getFavorites().some(item => item.id === id);
            }

            function toggleFavoriteResource(resource) {
                if (!resource || !resource.link) {
                    showStatus('收藏失败：链接为空');
                    return;
                }

                const id = makeResourceId(resource.link);
                const list = getFavorites();
                const exists = list.some(item => item.id === id);

                let nextList;

                if (exists) {
                    nextList = list.filter(item => item.id !== id);
                    showStatus('已取消收藏');
                } else {
                    nextList = [{
                        id,
                        name: resource.name || '未知资源',
                        link: resource.link,
                        pwd: resource.pwd || '',
                        type: resource.type || '',
                        source: resource.source || '',
                        createdAt: Date.now()
                    }, ...list].slice(0, 200);

                    showStatus('已加入收藏');
                }

                saveFavorites(nextList);
                updateFavoriteButtons();
                renderFavorites();
            }

            function clearFavorites() {
                if (!confirm('确定要清空全部收藏吗？')) return;
                saveFavorites([]);
                updateFavoriteButtons();
                renderFavorites();
                showStatus('收藏已清空');
            }

            function getBrokenLinks() {
                return readLocalList(LOCAL_KEYS.broken);
            }

            function saveBrokenLinks(list) {
                writeLocalList(LOCAL_KEYS.broken, list);
            }

            function isBrokenMarked(link) {
                const id = makeResourceId(link);
                return getBrokenLinks().some(item => item.id === id);
            }

            function toggleBrokenLink(resource) {
                if (!resource || !resource.link) {
                    showStatus('反馈失败：链接为空');
                    return;
                }

                const id = makeResourceId(resource.link);
                const list = getBrokenLinks();
                const exists = list.some(item => item.id === id);

                let nextList;

                if (exists) {
                    nextList = list.filter(item => item.id !== id);
                    showStatus('已取消失效标记');
                } else {
                    nextList = [{
                        id,
                        name: resource.name || '未知资源',
                        link: resource.link,
                        type: resource.type || '',
                        createdAt: Date.now()
                    }, ...list].slice(0, 300);

                    showStatus('已标记为疑似失效');
                }

                saveBrokenLinks(nextList);
                updateBrokenButtons();
                updateBrokenVisibility();
                renderFavorites();
            }

            function getResourceQualityMap() {
                const data = safeJsonParse(localStorage.getItem(LOCAL_KEYS.quality), {});
                return data && typeof data === 'object' && !Array.isArray(data) ? data : {};
            }

            function saveResourceQualityMap(map) {
                localStorage.setItem(LOCAL_KEYS.quality, JSON.stringify(map || {}));
            }

            function getResourceQuality(link) {
                const id = makeResourceId(link);
                const map = getResourceQualityMap();
                const score = Number(map[id] || 0);
                return Number.isFinite(score) ? Math.max(0, Math.min(5, score)) : 0;
            }

            function setResourceQuality(link, score) {
                if (!link) {
                    showStatus('评分失败：链接为空');
                    return;
                }

                const id = makeResourceId(link);
                const map = getResourceQualityMap();
                const cleanScore = Math.max(0, Math.min(5, Number(score) || 0));

                if (cleanScore <= 0) {
                    delete map[id];
                } else {
                    map[id] = cleanScore;
                }

                saveResourceQualityMap(map);
                updateQualityRatings(link);
                renderFavorites();

                showStatus(cleanScore ? `已评分 ${cleanScore} 星` : '已清除评分');
            }

            function isHideBrokenEnabled() {
                return localStorage.getItem(LOCAL_KEYS.hideBroken) === '1';
            }

            function setHideBrokenEnabled(enabled) {
                localStorage.setItem(LOCAL_KEYS.hideBroken, enabled ? '1' : '0');
                updateBrokenVisibility();
            }

            function updateBrokenVisibility() {
                const hide = isHideBrokenEnabled();
                let brokenCount = 0;

                document.querySelectorAll('.result-item[data-link]').forEach(item => {
                    const link = item.dataset.link || '';
                    const broken = isBrokenMarked(link);

                    item.classList.toggle('is-local-broken', broken);
                    item.classList.toggle('is-broken-hidden', hide && broken);

                    if (broken) brokenCount++;
                });

                const btn = document.getElementById('toggleBrokenFilterBtn');
                const tip = document.getElementById('brokenFilterTip');

                if (btn) {
                    btn.textContent = hide ? '显示疑似失效资源' : '隐藏疑似失效资源';
                }

                if (tip) {
                    tip.textContent = brokenCount
                        ? `当前结果中有 ${brokenCount} 条疑似失效资源`
                        : '当前结果暂无本地失效标记';
                }
            }

            function updateQualityRatings(targetLink = '') {
                const selector = targetLink
                    ? `.quality-rating[data-link="${CSS.escape(targetLink)}"]`
                    : '.quality-rating[data-link]';

                document.querySelectorAll(selector).forEach(box => {
                    const link = box.dataset.link || '';
                    const score = getResourceQuality(link);

                    box.querySelectorAll('.quality-star').forEach(star => {
                        const value = Number(star.dataset.score || 0);
                        star.classList.toggle('is-active', value <= score);
                    });

                    const text = box.querySelector('.quality-text');
                    if (text) {
                        text.textContent = score ? `${score}星` : '未评分';
                    }
                });
            }

            function createQualityRatingHtml(link) {
                const score = getResourceQuality(link);

                return `
                <span class="quality-rating" data-link="${escapeHtml(link)}" title="本地资源质量评分">
                    ${[1, 2, 3, 4, 5].map(value => `
                        <button
                            type="button"
                            class="quality-star ${value <= score ? 'is-active' : ''}"
                            data-action="quality"
                            data-score="${value}"
                            data-link="${escapeHtml(link)}"
                            aria-label="${value}星"
                        >★</button>
                    `).join('')}
                    <span class="quality-text">${score ? `${score}星` : '未评分'}</span>
                </span>
            `;
            }

            function renderSearchHistory() {
                if (!searchHistoryPanel || !searchHistoryList) return;

                const list = getSearchHistory();

                if (!list.length) {
                    searchHistoryPanel.classList.remove('show');
                    searchHistoryList.innerHTML = '';
                    return;
                }

                searchHistoryPanel.classList.add('show');
                searchHistoryList.innerHTML = list.map(item => {
                    return `<button type="button" class="history-chip" data-history-keyword="${escapeHtml(item)}">${escapeHtml(item)}</button>`;
                }).join('');
            }

            function renderFavorites() {
                if (!favoritesList || !favoritesStats) return;

                const keyword = normalizeSearchKeyword(favoriteSearchInput ? favoriteSearchInput.value : '');
                const list = getFavorites();

                const filtered = keyword
                    ? list.filter(item => {
                        const text = `${item.name || ''} ${item.link || ''} ${TYPE_LABEL[item.type] || item.type || ''} ${item.pwd || ''}`.toLowerCase();
                        return text.includes(keyword.toLowerCase());
                    })
                    : list;

                favoritesStats.textContent = `共收藏 ${list.length} 条${keyword ? `，当前筛选 ${filtered.length} 条` : ''}`;

                if (!filtered.length) {
                    favoritesList.innerHTML = `<div class="favorite-empty">${keyword ? '没有匹配的收藏。' : '暂无收藏。你可以在搜索结果中点击“收藏”。'}</div>`;
                    if (typeof window.neoRequestCondensedNavSync === 'function') {
                        // 中文：空收藏会显著缩短页面高度，渲染后立即重新评估导航，避免下滑时在阈值附近反复收缩和展开。
                        // English: Empty Favorites greatly shortens page height, so the nav is re-evaluated immediately after rendering to avoid repeated condense/expand near the threshold.
                        window.requestAnimationFrame(window.neoRequestCondensedNavSync);
                    }
                    return;
                }

                favoritesList.innerHTML = filtered.map((item, index) => {
                    const typeName = TYPE_LABEL[item.type] || item.type || '未知来源';
                    const pwd = item.pwd || '';
                    return `
                    <div class="result-item ${isBrokenMarked(item.link) ? 'is-local-broken' : ''}" style="animation-delay: ${index * 0.03}s" data-link="${escapeHtml(item.link)}">
                        <button class="qr-toggle-btn" title="分享二维码" onclick="event.stopPropagation(); openQrModal('${escapeHtml(item.link)}')">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                            </svg>
                        </button>
                        <div class="drama-title">
                            ${escapeHtml(item.name || '未知资源')}
                            ${createQualityRatingHtml(item.link)}
                        </div>
                        <div class="info-list">
                            <div class="info-item">
                                <span class="info-label">来源:</span>
                                <span>${escapeHtml(typeName)}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">链接:</span>
                                <a href="${escapeHtml(item.link)}" target="_blank" class="info-link">${escapeHtml(item.link)}</a>
                            </div>
                            ${pwd ? `<div class="info-item">
                                <span class="info-label">密码:</span>
                                <span style="color: #f59e0b;">${escapeHtml(pwd)}</span>
                            </div>` : ''}
                        </div>
                        <div class="favorite-actions">
                            <button type="button" class="resource-action-btn" data-action="copy-link" data-link="${escapeHtml(item.link)}">复制链接</button>
                            ${pwd ? `<button type="button" class="resource-action-btn" data-action="copy-pwd" data-pwd="${escapeHtml(pwd)}">复制密码</button>` : ''}
                            <button type="button" class="resource-action-btn is-favorited" data-action="favorite" data-name="${escapeHtml(item.name || '')}" data-link="${escapeHtml(item.link)}" data-pwd="${escapeHtml(pwd)}" data-type="${escapeHtml(item.type || '')}">取消收藏</button>
                            <button type="button" class="resource-action-btn ${isBrokenMarked(item.link) ? 'is-broken' : ''}" data-action="broken" data-name="${escapeHtml(item.name || '')}" data-link="${escapeHtml(item.link)}" data-type="${escapeHtml(item.type || '')}">
                                ${isBrokenMarked(item.link) ? '已标记失效' : '失效反馈'}
                            </button>
                        </div>
                    </div>
                `;
                }).join('');

                bindResourceActionEvents();
                if (typeof window.neoRequestCondensedNavSync === 'function') {
                    // 中文：收藏数量变化会改变列表高度，重新评估后才能决定移动端是否适合使用收缩导航。
                    // English: Favorite count changes alter list height, so re-evaluation decides whether condensed nav is suitable on mobile.
                    window.requestAnimationFrame(window.neoRequestCondensedNavSync);
                }
            }

            function updateFavoriteButtons() {
                document.querySelectorAll('.resource-action-btn[data-action="favorite"]').forEach(btn => {
                    const link = btn.dataset.link || '';
                    const yes = isFavorited(link);
                    btn.classList.toggle('is-favorited', yes);
                    btn.textContent = yes ? '取消收藏' : '收藏';
                });
            }

            function updateBrokenButtons() {
                document.querySelectorAll('.resource-action-btn[data-action="broken"]').forEach(btn => {
                    const link = btn.dataset.link || '';
                    const yes = isBrokenMarked(link);
                    btn.classList.toggle('is-broken', yes);
                    btn.textContent = yes ? '已标记失效' : '失效反馈';
                });
            }

            function bindResourceActionEvents() {
                document.querySelectorAll('.resource-action-btn, .quality-star').forEach(btn => {
                    if (btn.dataset.bound === '1') return;
                    btn.dataset.bound = '1';

                    btn.addEventListener('click', async (e) => {
                        e.preventDefault();
                        e.stopPropagation();

                        const action = btn.dataset.action;

                        if (action === 'copy-link') {
                            await copyTextToClipboard(btn.dataset.link || '');
                            showStatus('链接已复制');
                            return;
                        }

                        if (action === 'copy-pwd') {
                            await copyTextToClipboard(btn.dataset.pwd || '');
                            showStatus('密码已复制');
                            return;
                        }

                        if (action === 'favorite') {
                            toggleFavoriteResource({
                                name: btn.dataset.name || '',
                                link: btn.dataset.link || '',
                                pwd: btn.dataset.pwd || '',
                                type: btn.dataset.type || '',
                                source: btn.dataset.source || ''
                            });
                            return;
                        }

                        if (action === 'broken') {
                            toggleBrokenLink({
                                name: btn.dataset.name || '',
                                link: btn.dataset.link || '',
                                type: btn.dataset.type || ''
                            });
                            return;
                        }

                        if (action === 'quality') {
                            setResourceQuality(btn.dataset.link || '', btn.dataset.score || 0);
                        }
                    });
                });
            }

            /**
             * 在 JSON.parse 之前保护网盘提取码。
             *
             * 处理接口返回这种情况：
             * "pwd":32e7  =>  "pwd":"32e7"
             */
            function protectPwdInJsonText(text) {
                if (typeof text !== 'string') return text;

                return text.replace(
                    /("pwd"\s*:\s*)(?!")(?!(?:null|true|false)\b)([A-Za-z0-9+\-.]{1,32})(?=\s*[,}\]])/gi,
                    (match, prefix, value) => `${prefix}"${value}"`
                );
            }

            /**
             * 从百度网盘链接中提取真实 pwd。
             *
             * 例如：
             * https://pan.baidu.com/s/xxx?pwd=32e7
             * 返回：
             * 32e7
             *
             * 这是本次修复的关键。
             * 因为有些接口返回的 item.pwd 已经被服务端或解析过程变成了 320000000，
             * 但 item.url 里的 ?pwd=32e7 仍然是正确的。
             */
            function extractPwdFromLink(link) {
                if (!link) return '';

                const text = String(link).trim();

                try {
                    const url = new URL(text, window.location.origin);
                    const pwd = url.searchParams.get('pwd');
                    if (pwd !== null && pwd !== undefined && String(pwd).trim() !== '') {
                        return String(pwd).trim();
                    }
                } catch (e) {}

                const match = text.match(/[?&]pwd=([^&#]+)/i);
                if (match && match[1]) {
                    try {
                        return decodeURIComponent(match[1].replace(/\+/g, '%20')).trim();
                    } catch (e) {
                        return match[1].trim();
                    }
                }

                return '';
            }

            /**
             * 统一格式化提取码。
             * 注意：这里绝对不能 Number()，否则 32e7 会再次变成 320000000。
             */
            function formatPwd(pwd) {
                if (pwd === null || pwd === undefined) return '';
                return String(pwd).trim();
            }

            /**
             * 解码 HTML 实体，避免榜单标题里出现 &amp;、&#039; 等内容影响搜索。
             */
            function decodeHtmlEntities(text) {
                const textarea = document.createElement('textarea');
                textarea.innerHTML = String(text || '');
                return textarea.value;
            }

            /**
             * 统一清洗搜索关键词。
             * 解决榜单标题中可能存在的隐藏字符、换行、HTML实体、连续空格等问题。
             */
            function normalizeSearchKeyword(keyword) {
                return decodeHtmlEntities(keyword)
                    .replace(/[\u200B-\u200D\uFEFF]/g, '')
                    .replace(/\u00A0/g, ' ')
                    .replace(/\s+/g, ' ')
                    .trim();
            }

            /**
             * 对单条资源做密码修正。
             * 优先级：
             * 1. 链接 url / viewlink / link 里的 ?pwd=xxxx
             * 2. 接口返回的 item.pwd
             */
            function normalizeResourceItem(item) {
                if (!item || typeof item !== 'object') return item;

                const fixed = { ...item };
                const link = fixed.url || fixed.viewlink || fixed.link || fixed.share_url || fixed.shareUrl || '';
                const pwdFromLink = extractPwdFromLink(link);

                if (pwdFromLink) {
                    fixed.pwd = pwdFromLink;
                } else {
                    fixed.pwd = formatPwd(fixed.pwd);
                }

                return fixed;
            }

            /**
             * 深度修正接口返回数据。
             * 这样不仅页面显示正确，format=json 模式输出的数据也会被修正。
             */
            function normalizePwdFieldsDeep(value) {
                if (Array.isArray(value)) {
                    return value.map(normalizePwdFieldsDeep);
                }

                if (value && typeof value === 'object') {
                    Object.keys(value).forEach(key => {
                        value[key] = normalizePwdFieldsDeep(value[key]);
                    });

                    const link = value.url || value.viewlink || value.link || value.share_url || value.shareUrl || '';
                    const pwdFromLink = extractPwdFromLink(link);

                    if (pwdFromLink) {
                        value.pwd = pwdFromLink;
                    } else if (Object.prototype.hasOwnProperty.call(value, 'pwd')) {
                        value.pwd = formatPwd(value.pwd);
                    }
                }

                return value;
            }

            /**
             * 安全解析接口 JSON。
             * 第一步：在 JSON.parse 之前保护裸 pwd。
             * 第二步：JSON.parse 后再从链接中恢复真实 pwd。
             */
            function parseApiJsonSafely(text) {
                const safeText = protectPwdInJsonText(text);

                const parsed = JSON.parse(safeText, (key, value) => {
                    if (key === 'pwd' && value !== null && value !== undefined) {
                        return String(value);
                    }
                    return value;
                });

                return normalizePwdFieldsDeep(parsed);
            }

            function extractDomain(url) { if (!url) return ''; try { return new URL(url).hostname; } catch (e) { return ''; } }
            if (titleLogo) titleLogo.onerror = function () { this.style.display = 'none'; };
            let timeoutId = null;
            function clearTimeouts() { if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; } }
            function buildQrCodeUrl(text, size) { const params = new URLSearchParams({ frame: 1, e: 'L', text: text || '', size: size || 200 }); return `${QRCODE_API}?${params.toString()}`; }

            // ==================== 折叠动画通用工具 ====================
            const collapseMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            const hotListMotionTimers = new WeakMap();

            function shouldReduceMotion() {
                return collapseMotionQuery && collapseMotionQuery.matches;
            }

            function setListTagIndexes(list) {
                if (!list) return;

                list.querySelectorAll('.tag').forEach((tag, index) => {
                    tag.style.setProperty('--tag-index', index);
                });
            }

            function setSoftElementVisible(el, visible) {
                if (!el) return;

                const currentlyHidden =
                    el.style.display === 'none' ||
                    el.classList.contains('is-hidden');

                if (shouldReduceMotion()) {
                    el.style.display = visible ? 'block' : 'none';
                    el.classList.toggle('is-hidden', !visible);
                    el.style.height = visible ? '' : '0px';
                    return;
                }

                /*
                     * 关键修复：
                     * 提示文案不能只做 opacity，否则 display:block / none 会造成下面内容瞬间回流。
                     * 这里同步动画 height，让“仅展示前 10 条...”这行也参与平滑布局变化。
                     */
                if (visible) {
                    if (!currentlyHidden && el.style.display !== 'none') return;

                    el.style.display = 'block';
                    el.style.overflow = 'hidden';
                    el.style.height = '0px';
                    el.classList.add('is-hidden');

                    const targetHeight = Math.ceil(el.scrollHeight);

                    el.getBoundingClientRect();

                    requestAnimationFrame(() => {
                        el.classList.remove('is-hidden');
                        el.style.height = `${targetHeight}px`;
                    });

                    setTimeout(() => {
                        if (!el.classList.contains('is-hidden')) {
                            el.style.height = '';
                            el.style.overflow = '';
                        }
                    }, 300);

                    return;
                }

                if (currentlyHidden) return;

                const startHeight = Math.ceil(el.getBoundingClientRect().height);

                el.style.overflow = 'hidden';
                el.style.height = `${startHeight}px`;

                el.getBoundingClientRect();

                requestAnimationFrame(() => {
                    el.classList.add('is-hidden');
                    el.style.height = '0px';
                });

                setTimeout(() => {
                    if (el.classList.contains('is-hidden')) {
                        el.style.display = 'none';
                        el.style.height = '0px';
                        el.style.overflow = 'hidden';
                    }
                }, 300);
            }

            function smoothRenderCollapsibleList(list, html, collapsed, options = {}) {
                if (!list) return;

                const animated = options.animated !== false &&
                    !shouldReduceMotion() &&
                    list.dataset.motionReady === '1';

                const oldTimer = hotListMotionTimers.get(list);
                if (oldTimer) {
                    clearTimeout(oldTimer);
                    hotListMotionTimers.delete(list);
                }

                if (!animated) {
                    list.innerHTML = html || '';
                    setListTagIndexes(list);

                    list.classList.toggle('is-collapsed', !!collapsed);
                    list.classList.remove('is-animating', 'list-opening');

                    list.style.height = collapsed ? '0px' : '';
                    list.style.overflow = collapsed ? 'hidden' : '';

                    list.setAttribute('aria-hidden', collapsed ? 'true' : 'false');
                    list.dataset.motionReady = '1';

                    updatePageScrollbar();
                    return;
                }

                const startHeight = Math.ceil(list.getBoundingClientRect().height);
                const wasCollapsed = list.classList.contains('is-collapsed');

                list.classList.add('is-animating');
                list.classList.remove('list-opening');
                list.style.overflow = 'hidden';
                list.style.height = `${startHeight}px`;

                /*
                     * 先替换内容。
                     * 比如从 20 条收回 10 条时，DOM 必须先变成 10 条，
                     * 然后再测量 10 条的真实自然高度。
                     */
                list.innerHTML = html || '';
                setListTagIndexes(list);

                let targetHeight = 0;

                if (collapsed) {
                    targetHeight = 0;
                    list.classList.add('is-collapsed');
                } else {
                    /*
                         * 关键修复：
                         * 不能直接用 list.scrollHeight。
                         * 因为此时 list 还锁着旧高度，scrollHeight 在部分浏览器里会返回旧高度，
                         * 这会导致动画结束释放 height:auto 时突然闪变。
                         *
                         * 正确做法：
                         * 1. 临时关闭 transition
                         * 2. 临时 height:auto
                         * 3. 测量新内容真实高度
                         * 4. 恢复旧高度作为动画起点
                         * 5. 下一帧再动画到真实目标高度
                         */
                    list.classList.remove('is-collapsed');

                    const oldTransition = list.style.transition;

                    list.style.transition = 'none';
                    list.style.height = 'auto';

                    targetHeight = Math.ceil(list.getBoundingClientRect().height);

                    list.style.height = `${startHeight}px`;
                    list.style.transition = oldTransition;

                    /*
                         * 从完全收起状态展开时，先保持视觉上的折叠状态，
                         * 下一帧再移除，保证 opacity / transform 也能平滑进入。
                         */
                    if (wasCollapsed) {
                        list.classList.add('is-collapsed');
                    }
                }

                list.getBoundingClientRect();

                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        if (collapsed) {
                            list.classList.add('is-collapsed');
                            list.classList.remove('list-opening');
                        } else {
                            list.classList.remove('is-collapsed');
                            list.classList.add('list-opening');
                        }

                        list.style.height = `${targetHeight}px`;
                    });
                });

                const timer = setTimeout(() => {
                    list.classList.remove('is-animating', 'list-opening');

                    if (collapsed) {
                        list.style.height = '0px';
                        list.style.overflow = 'hidden';
                        list.setAttribute('aria-hidden', 'true');
                    } else {
                        /*
                             * 关键修复：
                             * 先锁定最终高度一帧，再释放成 auto。
                             * 避免浏览器在 transitionend 同一帧重新计算布局时，
                             * 把下面的“夸克热搜榜”突然顶上来。
                             */
                        list.style.height = `${targetHeight}px`;
                        list.style.overflow = 'hidden';
                        list.setAttribute('aria-hidden', 'false');

                        requestAnimationFrame(() => {
                            requestAnimationFrame(() => {
                                list.style.height = '';
                                list.style.overflow = '';
                                updatePageScrollbar();
                            });
                        });
                    }

                    hotListMotionTimers.delete(list);
                    updatePageScrollbar();
                }, 540);

                hotListMotionTimers.set(list, timer);
            }

            // ==================== 弹窗通用开关动画与页面锁定 ====================
            let activeModalCount = 0;

            function lockPageForModal() {
                activeModalCount++;

                hidePageScrollbarImmediately();
                document.body.classList.add('modal-open');
                document.body.classList.add('scrollbar-locked');
                document.body.style.overflow = 'hidden';
            }

            function unlockPageForModal() {
                activeModalCount = Math.max(0, activeModalCount - 1);

                if (activeModalCount === 0) {
                    document.body.classList.remove('modal-open');
                    document.body.classList.remove('scrollbar-locked');
                    document.body.style.overflow = '';

                    setTimeout(updatePageScrollbar, 320);
                }
            }

            // function showModalAnimated(overlay) {
            //     if (!overlay || overlay.classList.contains('show')) return;
            //
            //     lockPageForModal();
            //
            //     overlay.classList.add('show');
            // }
            // function hideModalAnimated(overlay, afterClose) {
            //     if (!overlay || !overlay.classList.contains('show')) return;
            //
            //     overlay.classList.remove('show');
            //
            //     setTimeout(() => {
            //         if (typeof afterClose === 'function') {
            //             afterClose();
            //         }
            //
            //         unlockPageForModal();
            //     }, 320);
            // }
            const modalTimers = new WeakMap();
            function showModalAnimated(overlay) {
                if (!overlay || overlay.classList.contains('show')) return;

                const oldTimer = modalTimers.get(overlay);
                if (oldTimer) {
                    clearTimeout(oldTimer);
                    modalTimers.delete(overlay);
                }

                lockPageForModal();

                /*
                     * 关键修复：
                     * 先锁定页面，让浏览器完成一帧布局，
                     * 再添加 show，避免移动端在同一帧里同时处理 overflow / fixed / opacity / backdrop。
                     */
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        overlay.classList.add('show');
                    });
                });
            }
            function hideModalAnimated(overlay, afterClose) {
                if (!overlay || !overlay.classList.contains('show')) return;

                overlay.classList.remove('show');

                const timer = setTimeout(() => {
                    if (typeof afterClose === 'function') {
                        afterClose();
                    }

                    unlockPageForModal();
                    modalTimers.delete(overlay);
                }, 360);

                modalTimers.set(overlay, timer);
            }

            function switchModalAnimated(fromOverlay, toOverlay, beforeShow) {
                if (!toOverlay) {
                    hideModalAnimated(fromOverlay);
                    return;
                }

                const fromTimer = fromOverlay ? modalTimers.get(fromOverlay) : null;
                const toTimer = modalTimers.get(toOverlay);

                if (fromTimer) {
                    clearTimeout(fromTimer);
                    modalTimers.delete(fromOverlay);
                }

                if (toTimer) {
                    clearTimeout(toTimer);
                    modalTimers.delete(toOverlay);
                }

                if (typeof beforeShow === 'function') {
                    beforeShow();
                }

                if (activeModalCount === 0) {
                    lockPageForModal();
                } else {
                    // 中文：弹窗切换时沿用已有页面锁，不重复累加 activeModalCount，避免最终关闭后 body 仍保持 overflow:hidden 导致页面无法滚动。
                    // English: Modal handoff reuses the existing page lock without incrementing activeModalCount again, preventing body overflow:hidden from surviving after the final close.
                    hidePageScrollbarImmediately();
                    document.body.classList.add('modal-open');
                    document.body.classList.add('scrollbar-locked');
                    document.body.style.overflow = 'hidden';
                }

                if (fromOverlay) {
                    fromOverlay.classList.remove('show');
                }

                // 中文：两个启动弹窗共用一次页面锁定并在下一帧切换，避免关闭第一个后再等待第二个定时器造成明显空档。
                // English: The two startup dialogs share one page lock and switch on the next frame, avoiding the visible gap caused by waiting for a second timer after the first dialog closes.
                requestAnimationFrame(() => {
                    toOverlay.classList.add('show');
                });
            }

            // ==================== Neo 新版稳定性提醒弹窗逻辑 ====================
            const neoNoticeModalOverlay = document.getElementById('neoNoticeModalOverlay');
            const neoNoticeLegacyLink = document.getElementById('neoNoticeLegacyLink');
            const neoNoticeLegacyBtn = document.getElementById('neoNoticeLegacyBtn');
            let neoNoticeClosedForThisPageLoad = false;

            function getLegacyPageUrl() {
                const legacyUrl = new URL('./index.html', window.location.href);

                // 中文：保留当前查询参数和 hash，用户从新版返回旧版时不丢失正在访问的入口状态。
                // English: Preserve the current query and hash so returning to the old UI keeps the current entry state.
                legacyUrl.search = window.location.search;
                legacyUrl.hash = window.location.hash;

                return legacyUrl.href;
            }

            function syncNeoNoticeLegacyUrl() {
                const legacyUrl = getLegacyPageUrl();

                if (neoNoticeLegacyLink) {
                    neoNoticeLegacyLink.href = legacyUrl;
                    neoNoticeLegacyLink.textContent = legacyUrl;
                }

                if (neoNoticeLegacyBtn) {
                    neoNoticeLegacyBtn.href = legacyUrl;
                }
            }

            function openNeoNoticeModal() {
                syncNeoNoticeLegacyUrl();
                showModalAnimated(neoNoticeModalOverlay);
            }

            function closeNeoNoticeModal() {
                neoNoticeClosedForThisPageLoad = true;

                if (shouldAutoOpenPolicyModal() && !policyAutoOpenedForThisPageLoad) {
                    policyAutoOpenedForThisPageLoad = true;

                    // 中文：启动流程仍保持“新版提醒 -> 用户条例”的阅读顺序，但直接切换到条例弹窗，减少静态页首屏等待。
                    // English: The startup flow keeps the required "Neo notice -> policy" reading order, but switches directly to the policy dialog to reduce static-page startup waiting.
                    switchModalAnimated(neoNoticeModalOverlay, policyModalOverlay, hydrateReusableModalTemplates);
                    return;
                }

                hideModalAnimated(neoNoticeModalOverlay);
            }

            function shouldAutoOpenNeoNoticeModal() {
                return shouldAutoOpenPolicyModal();
            }

            function showNeoNoticeModalOnPageLoad() {
                if (!shouldAutoOpenNeoNoticeModal()) return;
                if (neoNoticeClosedForThisPageLoad) return;

                // 中文：初始化脚本已完成路由、榜单和 URL 参数处理，这里只保留短延迟给浏览器完成首帧绘制，避免旧的 420ms 等待拖慢弹窗流程。
                // English: Routing, ranking, and URL parameter initialization have already run, so only a short delay is kept for first paint instead of the old 420ms wait.
                setTimeout(() => {
                    openNeoNoticeModal();
                }, 120);
            }

            // ==================== 用户条例弹窗逻辑 ====================
            const policyModalOverlay = document.getElementById('policyModalOverlay');
            const policyModalContent = document.getElementById('policyModalContent');
            const policyModalContentTemplate = document.getElementById('policyModalContentTemplate');
            let policyModalContentHydrated = false;

            function hydrateReusableModalTemplates() {
                if (policyModalContentHydrated || !policyModalContent || !policyModalContentTemplate) return;

                policyModalContent.innerHTML = '';
                policyModalContent.appendChild(policyModalContentTemplate.content.cloneNode(true));
                policyModalContentHydrated = true;

                // 中文：条例正文从 template 克隆到弹窗，未来同一模板可复用于其它入口，避免多处手工同步法律说明。
                // English: The policy body is cloned from a template, so future entry points can reuse it without manually synchronizing legal text in several places.
            }

            function openPolicyModal() {
                hydrateReusableModalTemplates();
                showModalAnimated(policyModalOverlay);
            }

            function closePolicyModal() {
                hideModalAnimated(policyModalOverlay);
            }

            function rejectPolicy() {
                window.location.href = 'about:blank';
            }

            /*
                 * 用户条例弹窗自动弹出规则：
                 * 1. 每次正常打开网页都弹。
                 * 2. 每次刷新网页都弹。
                 * 3. 不再使用 localStorage 记忆用户是否确认。
                 * 4. 支持 #/、#/daily、#/rank 三个页面刷新后都弹。
                 * 5. 如果是 ?format=json 的 API 输出模式，不弹窗，避免破坏 JSON 返回。
                 */
            let policyAutoOpenedForThisPageLoad = false;

            function shouldAutoOpenPolicyModal() {
                const params = new URLSearchParams(window.location.search);
                const format = (params.get('format') || '').toLowerCase();

                return format !== 'json';
            }

            function showPolicyModalOnEveryPageLoad() {
                if (!shouldAutoOpenPolicyModal()) return;
                if (policyAutoOpenedForThisPageLoad) return;

                policyAutoOpenedForThisPageLoad = true;

                // 中文：条例弹窗可能由页面恢复或手动入口触发，此处只做下一帧打开，启动链路则由 switchModalAnimated 直接切换。
                // English: The policy dialog may be triggered by page restore or manual entry, so it opens on the next frame while startup uses switchModalAnimated for an immediate handoff.
                requestAnimationFrame(() => {
                    openPolicyModal();
                });
            }

            /*
                 * 处理部分手机浏览器 / Safari 的 bfcache 场景：
                 * 用户从别的页面返回时，如果页面是从缓存恢复，也重新弹出。
                 */
            window.addEventListener('pageshow', event => {
                if (event.persisted) {
                    policyAutoOpenedForThisPageLoad = false;
                    neoNoticeClosedForThisPageLoad = false;
                    showNeoNoticeModalOnPageLoad();
                }
            });

            // if (policyModalOverlay) {
            //     policyModalOverlay.addEventListener('click', (e) => {
            //         if (e.target === policyModalOverlay) {
            //             closePolicyModal();
            //         }
            //     });
            // }

            // ==================== 二维码弹窗逻辑 ====================
            const qrModalOverlay = document.getElementById('qrModalOverlay');
            const qrModalImage = document.getElementById('qrModalImage');
            const qrModalError = document.getElementById('qrModalError');
            // function openQrModal(link) { if (!link) return; qrModalImage.style.display = 'none'; qrModalError.style.display = 'none'; qrModalImage.src = buildQrCodeUrl(link, 260); qrModalImage.onload = () => { qrModalImage.style.display = 'block'; }; qrModalImage.onerror = () => { qrModalError.style.display = 'flex'; }; qrModalOverlay.classList.add('show'); }
            // function closeQrModal() { qrModalOverlay.classList.remove('show'); }
            function openQrModal(link) {
                if (!link || !qrModalOverlay) return;

                qrModalImage.style.display = 'none';
                qrModalError.style.display = 'none';
                qrModalImage.src = buildQrCodeUrl(link, 260);

                qrModalImage.onload = () => {
                    qrModalImage.style.display = 'block';
                };

                qrModalImage.onerror = () => {
                    qrModalError.style.display = 'flex';
                };

                showModalAnimated(qrModalOverlay);
            }
            function closeQrModal() {
                hideModalAnimated(qrModalOverlay);
            }
            qrModalOverlay.addEventListener('click', (e) => { if (e.target === qrModalOverlay) closeQrModal(); });

            // ==================== 核心搜索逻辑 ====================
            let searchTimer = null;
            let isSearching = false;
            let currentPreset = 'all';

            function updateNeoSourceGridActive(sourceName = currentPreset) {
                document.querySelectorAll('.neo-source-chip[data-neo-source]').forEach(chip => {
                    const isActive = chip.getAttribute('data-neo-source') === sourceName;
                    chip.classList.toggle('is-active', isActive);
                    chip.setAttribute('aria-pressed', isActive ? 'true' : 'false');
                });
            }

            function applySearchSourceFromHash() {
                const sourceFromHash = getHashSourcePreset();
                const safeSource = TYPE_PRESETS[sourceFromHash] ? sourceFromHash : 'all';

                if (typeSelect && typeSelect.value !== safeSource) {
                    typeSelect.value = safeSource;
                }

                currentPreset = safeSource;

                // 中文：hash 是可分享状态的来源，进入搜索页时优先按 hash 恢复下拉框和快捷按钮高亮。
                // English: The hash is the shareable source of truth, so entering the search page restores both the select value and shortcut highlight from it.
                updateNeoSourceGridActive(safeSource);
            }

            function syncSearchSourceHash(sourceName = currentPreset) {
                const uiIsSearchPage = document.body && document.body.dataset.neoPage === 'search';
                if (getPageFromHash() !== 'search' && !uiIsSearchPage) return;

                // 中文：快捷入口可能先切换 UI 再写 hash，因此允许“当前界面已是搜索页”作为同步条件。
                // English: A shortcut may switch the UI before writing the hash, so the current UI being on Search is also accepted as a sync condition.
                const targetHash = getSearchHashForSource(sourceName);
                pushNeoRouteHash(targetHash);
            }

            /**
             * 搜索序号。
             * 用来避免旧搜索结果覆盖新搜索结果。
             */
            let searchSequence = 0;

            /* ==================== 搜索接口防 429：缓存 / 合并请求 / 冷却 ==================== */
            const SEARCH_CACHE_TTL = 60 * 1000;
            const SEARCH_MIN_INTERVAL = 900;

            const searchApiCache = new Map();
            const searchApiInflight = new Map();

            let lastSearchApiTime = 0;

            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }

            function makeSearchApiCacheKey(url) {
                return String(url || '').trim();
            }

            function getCachedSearchApiResult(url) {
                const key = makeSearchApiCacheKey(url);
                const cached = searchApiCache.get(key);

                if (!cached) return null;

                if (Date.now() - cached.time > SEARCH_CACHE_TTL) {
                    searchApiCache.delete(key);
                    return null;
                }

                return cached.data;
            }

            function setCachedSearchApiResult(url, data) {
                const key = makeSearchApiCacheKey(url);

                searchApiCache.set(key, {
                    time: Date.now(),
                    data
                });
            }

            async function waitSearchApiInterval() {
                const now = Date.now();
                const diff = now - lastSearchApiTime;

                if (diff < SEARCH_MIN_INTERVAL) {
                    await sleep(SEARCH_MIN_INTERVAL - diff);
                }

                lastSearchApiTime = Date.now();
            }

            typeSelect.addEventListener('change', () => {
                currentPreset = TYPE_PRESETS[typeSelect.value] ? typeSelect.value : 'all';

                // 中文：用户手动切换来源时同步写入 hash，让当前来源可以被复制、收藏或分享给别人。
                // English: Manual source changes are written into the hash so the current source can be copied, bookmarked, or shared.
                syncSearchSourceHash(currentPreset);
                updateNeoSourceGridActive(currentPreset);

                const keyword = normalizeSearchKeyword(searchInput.value);
                if (keyword) performSearch(keyword, { immediate: true });
            });

            searchBtn.addEventListener('click', () => {
                performSearch(searchInput.value, { immediate: true });
            });

            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    performSearch(searchInput.value, { immediate: true });
                }
            });

            function buildSearchTerms(rawInput) {
                const input = normalizeSearchKeyword(rawInput);
                if (!input) return [];

                const parts = input.split(/\s+/).filter(Boolean);
                const terms = new Set([input]);

                if (parts.length > 1) {
                    parts.forEach(p => terms.add(p));
                }

                return Array.from(terms).sort((a, b) => {
                    if (a === input) return -1;
                    if (b === input) return 1;
                    return b.length - a.length;
                });
            }

            /**
             * 统一搜索入口。
             *
             * options.immediate:
             * - true：立即搜索，适合榜单点击、按钮点击、回车。
             * - false：防抖搜索。
             *
             * options.forceAll:
             * - true：强制使用全局聚合，适合热度榜跳转搜索。
             *
             * options.retryIfEmpty:
             * - true：如果第一次返回空结果，自动重试一次，解决接口偶发空返回。
             */
            async function performSearch(keyword, options = {}) {
                const term = normalizeSearchKeyword(keyword);

                if (!term) {
                    showStatus('请输入搜索关键词');
                    return;
                }

                if (options.forceAll) {
                    typeSelect.value = 'all';
                    currentPreset = 'all';
                }

                searchInput.value = term;
                saveSearchHistory(term);

                clearTimeout(searchTimer);

                const currentSearchId = ++searchSequence;
                const delay = options.immediate ? 0 : 300;

                searchTimer = setTimeout(() => {
                    executeSearchUI(term, {
                        searchId: currentSearchId,
                        retryIfEmpty: !!options.retryIfEmpty
                    });
                }, delay);
            }

            async function executeSearchUI(term, options = {}) {
                const searchId = options.searchId || ++searchSequence;

                isSearching = true;
                searchBtn.disabled = true;

                document.querySelectorAll('.tag').forEach(tag => tag.classList.add('disabled'));

                clearTimeouts();
                showLoading();
                showStatus(`正在搜索: ${term}...`);

                try {
                    let result = await fetchAndMergeData(term, currentPreset);

                    if (searchId !== searchSequence) return;

                    /*
                         * 只有“真正空结果”才允许重试。
                         * 如果是 429 / 限流，不重试。
                         */
                    const isRateLimited =
                        result &&
                        result.apiStatus &&
                        result.apiStatus.failedReason === 'rate_limited';

                    if (
                        options.retryIfEmpty &&
                        !isRateLimited &&
                        (!result || result.total === 0 || result.typeList.length === 0)
                    ) {
                        showStatus('首次未命中，正在自动重试...');
                        await sleep(1200);

                        result = await fetchAndMergeData(term, currentPreset);

                        if (searchId !== searchSequence) return;
                    }

                    const { mergedByType, total, typeList, apiStatus } = result;

                    if (apiStatus && apiStatus.failedReason === 'rate_limited') {
                        setResultsAreaMode('is-feedback');
                        resultsArea.innerHTML = `
                        <div class="status-message">
                            <p style="color: var(--error);">接口请求过于频繁</p>
                            <p style="margin-top: 8px;">请稍后再搜索，系统已停止自动重复请求，避免继续触发 429。</p>
                        </div>
                    `;
                        showStatus('接口请求过于频繁，请稍后再试');
                        return;
                    }

                    if (typeList.length === 0 || total === 0) {
                        setResultsAreaMode('is-feedback');
                        resultsArea.innerHTML = `<div class="status-message"><p>未找到相关结果。</p></div>`;
                        showStatus('未找到相关结果');
                        return;
                    }

                    renderGroupedResults(mergedByType, typeList, term, total, apiStatus);

                    // 中文：Neo 新版把热度榜视为持续可用的搜索入口，搜索成功后不自动收起，避免用户需要反复手动展开。
                    // English: Neo treats the ranking list as a persistent search entry, so it is not auto-collapsed after a successful search to avoid repeated manual expansion.
                    showStatus(`共找到 ${total} 条结果`);
                } catch (error) {
                    if (searchId !== searchSequence) return;

                    console.error(error);

                    if (error && error.errorType === 'rate_limited') {
                        setResultsAreaMode('is-feedback');
                        resultsArea.innerHTML = `
                        <div class="status-message">
                            <p style="color: var(--error);">接口请求过于频繁</p>
                            <p style="margin-top: 8px;">请稍后再试。系统不会继续自动重试，避免加重限流。</p>
                        </div>
                    `;
                        showStatus('接口请求过于频繁，请稍后再试');
                        return;
                    }

                    setResultsAreaMode('is-feedback');
                    resultsArea.innerHTML = `<div class="status-message"><p style="color: var(--error);">发生错误</p></div>`;
                } finally {
                    if (searchId === searchSequence) {
                        clearTimeouts();
                        isSearching = false;
                        searchBtn.disabled = false;
                        document.querySelectorAll('.tag').forEach(tag => tag.classList.remove('disabled'));
                    }
                }
            }

            async function fetchAndMergeData(term, presetName) {
                const types = TYPE_PRESETS[presetName] || TYPE_PRESETS.all;
                const typeParam = types.join(',');
                const searchTerms = buildSearchTerms(term);

                const mergedByType = {};
                const urlSet = new Set();

                let total = 0;
                let successCount = 0;
                let failedCount = 0;
                const failedTerms = [];

                for (const st of searchTerms) {
                    let data;

                    try {
                        data = await fetchSearchApi(`${JHSJ_API}?type=${encodeURIComponent(typeParam)}&name=${encodeURIComponent(st)}`);
                        successCount++;
                    } catch (e) {
                        failedCount++;
                        failedTerms.push(st);

                        if (e && e.errorType === 'rate_limited') {
                            return {
                                mergedByType,
                                total,
                                typeList: Object.keys(mergedByType),
                                apiStatus: {
                                    successCount,
                                    failedCount,
                                    failedTerms,
                                    failedReason: 'rate_limited'
                                }
                            };
                        }

                        continue;
                    }

                    if (data && data.code === 0 && data.data && data.data.merged_by_type) {
                        Object.keys(data.data.merged_by_type).forEach(type => {
                            if (!mergedByType[type]) mergedByType[type] = [];

                            data.data.merged_by_type[type].forEach(item => {
                                if (!item.url || urlSet.has(item.url)) return;

                                urlSet.add(item.url);
                                mergedByType[type].push({
                                    ...normalizeResourceItem(item),
                                    _searchTerm: st
                                });
                                total++;
                            });
                        });
                    }

                    if (total >= 200) break;
                }

                Object.keys(mergedByType).forEach(type => {
                    mergedByType[type].sort((a, b) => {
                        const aIsWhole = a._searchTerm === term ? 1 : 0;
                        const bIsWhole = b._searchTerm === term ? 1 : 0;

                        if (aIsWhole !== bIsWhole) return bIsWhole - aIsWhole;

                        return (b.name?.length || 0) - (a.name?.length || 0);
                    });
                });

                return {
                    mergedByType,
                    total,
                    typeList: Object.keys(mergedByType),
                    apiStatus: {
                        successCount,
                        failedCount,
                        failedTerms
                    }
                };
            }

            async function fetchSearchApi(fullUrl) {
                const cacheKey = makeSearchApiCacheKey(fullUrl);

                const cached = getCachedSearchApiResult(cacheKey);
                if (cached) return cached;

                if (searchApiInflight.has(cacheKey)) {
                    return searchApiInflight.get(cacheKey);
                }

                const task = (async () => {
                    try {
                        await waitSearchApiInterval();

                        let data = await tryFetchDirect(fullUrl);

                        /*
                             * 429 是接口限流，不要再走代理重试。
                             * 否则同一个接口会被继续打，429 更严重。
                             */
                        if (!data) {
                            data = await tryFetchWithProxies(fullUrl);
                        }

                        if (!data) throw { errorType: 'network' };

                        setCachedSearchApiResult(cacheKey, data);
                        return data;
                    } catch (error) {
                        if (error && error.errorType) throw error;
                        throw { errorType: 'unknown' };
                    } finally {
                        searchApiInflight.delete(cacheKey);
                    }
                })();

                searchApiInflight.set(cacheKey, task);
                return task;
            }

            async function tryFetchDirect(url) {
                const controller = new AbortController();

                const localTimeoutId = setTimeout(() => {
                    controller.abort();
                }, SEARCH_TIMEOUT);

                try {
                    const response = await fetch(url, { signal: controller.signal });

                    if (response.status === 429) {
                        throw {
                            errorType: 'rate_limited',
                            message: '接口请求过于频繁，请稍后再试'
                        };
                    }

                    if (!response.ok) {
                        throw {
                            errorType: 'server',
                            status: response.status
                        };
                    }

                    const text = await response.text();
                    return parseApiJsonSafely(text);
                } catch (error) {
                    if (error.name === 'AbortError') {
                        throw { errorType: 'timeout' };
                    }

                    if (error.errorType) throw error;

                    return null;
                } finally {
                    clearTimeout(localTimeoutId);
                }
            }

            async function tryFetchWithProxies(url) {
                let lastError = null;

                for (let proxy of CORS_PROXIES) {
                    const controller = new AbortController();

                    const timeoutPromise = new Promise((_, reject) => {
                        timeoutId = setTimeout(() => {
                            controller.abort();
                            reject({ errorType: 'timeout' });
                        }, SEARCH_TIMEOUT);
                    });

                    try {
                        const res = await Promise.race([
                            fetch(`${proxy}${encodeURIComponent(url)}`, { signal: controller.signal }),
                            timeoutPromise
                        ]);

                        if (!res.ok) throw { errorType: 'server' };

                        // 关键修改：不能用 res.json()
                        // 代理返回的数据也要先按文本处理，防止 pwd 被科学计数法解析
                        const text = await res.text();
                        const json = parseApiJsonSafely(text);

                        if (json && (json.code !== undefined || json.data)) return json;

                        throw { errorType: 'parse' };
                    } catch (error) {
                        if (error.name === 'AbortError') {
                            lastError = { errorType: 'timeout' };
                        } else {
                            lastError = error;
                        }
                        continue;
                    } finally {
                        clearTimeouts();
                    }
                }

                if (lastError) throw lastError;
                throw { errorType: 'cors' };
            }

            // // 公共分块折叠逻辑
            // function bindSectionToggleEvents() {
            //     document.querySelectorAll('.result-section .section-header').forEach(header => {
            //         header.onclick = () => {
            //             const section = header.closest('.result-section');
            //             section.classList.toggle('collapsed');
            //             if (!section.classList.contains('collapsed') && section.id) {
            //                 setTimeout(() => section.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
            //             }
            //         };
            //     });
            // }

            // ==================== 公共分块折叠逻辑：平滑高度动画版 ====================
            const resultSectionMotionTimers = new WeakMap();

            function getDirectResultList(section) {
                if (!section) return null;

                return Array.from(section.children).find(child => {
                    return child.classList && child.classList.contains('result-list');
                }) || section.querySelector('.result-list');
            }

            function syncResultSectionA11y(section) {
                if (!section) return;

                const header = section.querySelector('.section-header');
                const list = getDirectResultList(section);
                const isCollapsed = section.classList.contains('collapsed');

                if (header) {
                    header.setAttribute('role', 'button');
                    header.setAttribute('tabindex', '0');
                    header.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
                }

                if (list) {
                    list.setAttribute('aria-hidden', isCollapsed ? 'true' : 'false');
                }
            }

            function prepareResultSectionState(section) {
                if (!section) return;

                const list = getDirectResultList(section);
                if (!list) return;

                const isCollapsed = section.classList.contains('collapsed');

                if (isCollapsed) {
                    list.style.height = '0px';
                    list.style.overflow = 'hidden';
                } else {
                    list.style.height = '';
                    list.style.overflow = '';
                }

                list.querySelectorAll('.result-item').forEach((item, index) => {
                    item.style.setProperty('--item-index', index);
                });

                syncResultSectionA11y(section);
            }

            function restartSectionItemReveal(section) {
                const list = getDirectResultList(section);
                if (!list || shouldReduceMotion()) return;

                list.querySelectorAll('.result-item').forEach((item, index) => {
                    item.style.setProperty('--item-index', index);
                    item.style.animation = 'none';
                });

                list.offsetHeight;

                list.querySelectorAll('.result-item').forEach(item => {
                    item.style.animation = '';
                });

                section.classList.add('section-opening');

                setTimeout(() => {
                    section.classList.remove('section-opening');
                }, 460);
            }

            function setResultSectionCollapsed(section, shouldCollapse, options = {}) {
                if (!section) return;

                const list = getDirectResultList(section);
                if (!list) return;

                const animated = options.animated !== false && !shouldReduceMotion();

                const oldTimer = resultSectionMotionTimers.get(section);
                if (oldTimer) {
                    clearTimeout(oldTimer);
                    resultSectionMotionTimers.delete(section);
                }

                if (!animated) {
                    section.classList.toggle('collapsed', shouldCollapse);

                    list.style.height = shouldCollapse ? '0px' : '';
                    list.style.overflow = shouldCollapse ? 'hidden' : '';

                    syncResultSectionA11y(section);
                    updatePageScrollbar();
                    return;
                }

                const startHeight = list.getBoundingClientRect().height;

                section.classList.add('section-animating');
                list.style.overflow = 'hidden';
                list.style.height = `${startHeight}px`;

                list.getBoundingClientRect();

                if (shouldCollapse) {
                    section.classList.add('collapsed');
                    syncResultSectionA11y(section);

                    requestAnimationFrame(() => {
                        list.style.height = '0px';
                    });
                } else {
                    section.classList.remove('collapsed');
                    syncResultSectionA11y(section);

                    const targetHeight = list.scrollHeight;

                    requestAnimationFrame(() => {
                        list.style.height = `${targetHeight}px`;
                        restartSectionItemReveal(section);
                    });
                }

                const timer = setTimeout(() => {
                    section.classList.remove('section-animating');

                    if (shouldCollapse) {
                        list.style.height = '0px';
                        list.style.overflow = 'hidden';
                    } else {
                        list.style.height = '';
                        list.style.overflow = '';

                        if (options.scrollIntoView !== false && section.id) {
                            section.scrollIntoView({
                                behavior: shouldReduceMotion() ? 'auto' : 'smooth',
                                block: 'start'
                            });
                        }
                    }

                    resultSectionMotionTimers.delete(section);
                    updatePageScrollbar();
                }, 520);

                resultSectionMotionTimers.set(section, timer);
            }

            function bindSectionToggleEvents() {
                document.querySelectorAll('.result-section').forEach(section => {
                    prepareResultSectionState(section);
                });

                document.querySelectorAll('.result-section .section-header').forEach(header => {
                    header.onclick = () => {
                        const section = header.closest('.result-section');
                        if (!section) return;

                        const shouldCollapse = !section.classList.contains('collapsed');

                        setResultSectionCollapsed(section, shouldCollapse, {
                            animated: true,
                            scrollIntoView: !shouldCollapse
                        });
                    };

                    header.onkeydown = (e) => {
                        if (e.key !== 'Enter' && e.key !== ' ') return;

                        e.preventDefault();
                        header.click();
                    };
                });
            }

            function shouldCollapseSearchResultSection(type) {
                /*
                     * 全局聚合 / 网盘聚合：
                     * 只默认展开百度网盘和夸克网盘，其它来源默认收起。
                     */
                if (currentPreset === 'all' || currentPreset === 'netdisk') {
                    return type !== 'baidu' && type !== 'quark';
                }

                /*
                     * 单一搜索模式：
                     * 百度、夸克、阿里云盘、天翼、UC、115、磁力、电驴等全部默认展开。
                     */
                return false;
            }

            function renderGroupedResults(mergedByType, typeList, term, total, apiStatus = null) {
                const typeNames = typeList.map(type => TYPE_LABEL[type] || type).join('、');

                let html = `
                <div class="result-stats">
                    <span>关键词：${escapeHtml(term)}</span>
                    <span>共 ${total} 条</span>
                    <div class="search-health">
                        <span class="search-health-chip ok">已命中来源：${escapeHtml(typeNames || '无')}</span>
                        ${apiStatus ? `<span class="search-health-chip ${apiStatus.failedCount ? 'warn' : 'ok'}">
                            搜索请求：成功 ${apiStatus.successCount} 次 / 失败 ${apiStatus.failedCount} 次
                        </span>` : ''}
                    </div>
                </div>

                <div class="broken-filter-bar">
                    <button type="button" id="toggleBrokenFilterBtn" class="broken-filter-btn">
                        ${isHideBrokenEnabled() ? '显示疑似失效资源' : '隐藏疑似失效资源'}
                    </button>
                    <span id="brokenFilterTip" class="broken-filter-tip"></span>
                </div>
            `;

                let sortedTypes = [];

                ['baidu', 'quark'].forEach(p => {
                    if (typeList.includes(p)) sortedTypes.push(p);
                });

                typeList.forEach(t => {
                    if (!sortedTypes.includes(t)) sortedTypes.push(t);
                });

                sortedTypes.forEach(type => {
                    const items = mergedByType[type];
                    if (!items || items.length === 0) return;

                    const safeType = type.replace(/\s+/g, '_');
                    const isCollapsed = shouldCollapseSearchResultSection(type);

                    html += `
                    <div class="result-section ${isCollapsed ? 'collapsed' : ''}" id="search-${safeType}">
                        <div class="section-header">
                            <div>
                                <span class="toggle-icon">▼</span>
                                <span class="section-label ${safeType}">${escapeHtml(TYPE_LABEL[type] || type)}</span>
                                <span style="margin-left: 6px; font-size: 13px; color: #888;">共 ${items.length} 条</span>
                            </div>
                        </div>
                        <div class="result-list">
                `;

                    items.forEach((item, index) => {
                        html += createResultItem(item, type, index);
                    });

                    html += `</div></div>`;
                });

                setResultsAreaMode('has-results');
                resultsArea.innerHTML = html;

                bindSectionToggleEvents();
                bindResourceActionEvents();
                updateFavoriteButtons();
                updateBrokenButtons();
                updateQualityRatings();
                updateBrokenVisibility();

                const toggleBrokenFilterBtn = document.getElementById('toggleBrokenFilterBtn');
                if (toggleBrokenFilterBtn) {
                    toggleBrokenFilterBtn.addEventListener('click', () => {
                        setHideBrokenEnabled(!isHideBrokenEnabled());
                    });
                }
            }

            function createResultItem(item, type, index) {
                const name = item.name || '未知资源';
                const link = item.url || '#';
                const pwd = extractPwdFromLink(link) || formatPwd(item.pwd);
                const domain = extractDomain(link);
                const iconUrl = domain ? `${ICO_API}?url=https://${domain}` : '';
                const fav = isFavorited(link);
                const broken = isBrokenMarked(link);

                return `
                <div class="result-item ${broken ? 'is-local-broken' : ''} ${isHideBrokenEnabled() && broken ? 'is-broken-hidden' : ''}" style="animation-delay: ${index * 0.05}s" data-link="${escapeHtml(link)}">
                    <button class="qr-toggle-btn" title="分享二维码" onclick="event.stopPropagation(); openQrModal('${escapeHtml(link)}')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="7" height="7"/>
                            <rect x="14" y="3" width="7" height="7"/>
                            <rect x="3" y="14" width="7" height="7"/>
                            <rect x="14" y="14" width="7" height="7"/>
                        </svg>
                    </button>

                    <div class="drama-title">
                        ${escapeHtml(name)}
                        ${createQualityRatingHtml(link)}
                    </div>

                    <div class="info-list">
                        <div class="info-item">
                            <span class="info-label">来源:</span>
                            <span style="color: ${type === 'baidu' ? '#06a7ff' : type === 'quark' ? '#ff9500' : '#aaa'};">
                                ${escapeHtml(TYPE_LABEL[type] || type)}
                            </span>
                        </div>

                        <div class="info-item">
                            <span class="info-label">链接:</span>
                            <a href="${escapeHtml(link)}" target="_blank" class="info-link">
                                ${iconUrl ? `<img src="${iconUrl}" class="source-icon" onerror="this.style.display='none'">` : ''}
                                ${escapeHtml(link)}
                            </a>
                        </div>

                        ${pwd ? `<div class="info-item">
                            <span class="info-label">密码:</span>
                            <span style="color: #f59e0b;">${escapeHtml(pwd)}</span>
                        </div>` : ''}
                    </div>

                    <div class="result-actions">
                        <button type="button" class="resource-action-btn" data-action="copy-link" data-link="${escapeHtml(link)}">复制链接</button>

                        ${pwd ? `<button type="button" class="resource-action-btn" data-action="copy-pwd" data-pwd="${escapeHtml(pwd)}">复制密码</button>` : ''}

                        <button
                            type="button"
                            class="resource-action-btn ${fav ? 'is-favorited' : ''}"
                            data-action="favorite"
                            data-name="${escapeHtml(name)}"
                            data-link="${escapeHtml(link)}"
                            data-pwd="${escapeHtml(pwd)}"
                            data-type="${escapeHtml(type)}"
                        >${fav ? '取消收藏' : '收藏'}</button>

                        <button
                            type="button"
                            class="resource-action-btn ${broken ? 'is-broken' : ''}"
                            data-action="broken"
                            data-name="${escapeHtml(name)}"
                            data-link="${escapeHtml(link)}"
                            data-type="${escapeHtml(type)}"
                        >${broken ? '已标记失效' : '失效反馈'}</button>
                    </div>
                </div>
            `;
            }

            function showLoading() {
                setResultsAreaMode('is-busy');
                resultsArea.innerHTML = `<div class="status-message"><div class="spinner"></div><p>正在搜索...</p></div>`;
            }

            // ==================== 主页热度榜逻辑 ====================
            let rankData = [];
            let vtquarkData = [];

            /**
             * 短剧热度榜状态：
             * - 首次打开网页：默认展开前 10 条
             * - Neo 新版搜索成功后保持当前展开状态，不再沿用旧版自动折叠机制
             */
            let showAllRank = false;
            let rankTagsCollapsed = false;

            let showVtquark = false;

            const VTQUARK_CACHE_KEY = 'kuleu_vtquark_cache_v1';
            const RANK_API_TIMEOUT = 10000;

            const collapseArrowSvg = `
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6"/>
                    </svg>
                `;

            async function fetchJsonWithTimeout(url, timeout = RANK_API_TIMEOUT) {
                const controller = new AbortController();

                const timer = setTimeout(() => {
                    controller.abort();
                }, timeout);

                try {
                    const res = await fetch(url, {
                        signal: controller.signal,
                        cache: 'no-store'
                    });

                    if (!res.ok) {
                        throw new Error(`HTTP ${res.status}`);
                    }

                    return await res.json();
                } finally {
                    clearTimeout(timer);
                }
            }

            async function fetchJsonWithRetry(url, options = {}) {
                const retries = options.retries ?? 2;
                const delay = options.delay ?? 600;
                let lastError = null;

                for (let i = 0; i <= retries; i++) {
                    try {
                        return await fetchJsonWithTimeout(url, options.timeout || RANK_API_TIMEOUT);
                    } catch (error) {
                        lastError = error;

                        if (i < retries) {
                            await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
                        }
                    }
                }

                throw lastError;
            }

            function saveVtquarkCache(data) {
                try {
                    if (!Array.isArray(data) || data.length === 0) return;

                    localStorage.setItem(VTQUARK_CACHE_KEY, JSON.stringify({
                        time: Date.now(),
                        data
                    }));
                } catch (e) {}
            }

            function readVtquarkCache() {
                try {
                    const raw = localStorage.getItem(VTQUARK_CACHE_KEY);
                    if (!raw) return [];

                    const cache = JSON.parse(raw);
                    if (!cache || !Array.isArray(cache.data)) return [];

                    const maxAge = 24 * 60 * 60 * 1000;
                    if (Date.now() - Number(cache.time || 0) > maxAge) return [];

                    return cache.data;
                } catch (e) {
                    return [];
                }
            }

            function getVtquarkDisplayCount(data) {
                if (!Array.isArray(data)) return 0;
                return Math.min(data.length, 10);
            }

            function setVtquarkStatus(text, type = 'ready') {
                const status = document.getElementById('vtquarkStatus');
                if (!status) return;

                const finalText = String(text || '').trim();

                status.textContent = finalText;
                status.className = `vtquark-status is-${type}`;
                status.style.display = finalText ? 'inline-flex' : 'none';
            }

            function getVtquarkLoadedStatusText(data) {
                const displayCount = getVtquarkDisplayCount(data);
                return displayCount > 0 ? `已加载 ${displayCount} 条` : '';
            }

            function setRankToggleText(text, direction = 'down') {
                const toggle = document.getElementById('toggleMoreRank');
                if (!toggle) return;

                toggle.innerHTML = `${text} ${collapseArrowSvg}`;
                toggle.classList.toggle('is-open', direction === 'up');
            }

            function setVtquarkToggleText(text, direction = 'down') {
                const toggle = document.getElementById('toggleVtquark');
                if (!toggle) return;

                toggle.innerHTML = `${text} ${collapseArrowSvg}`;
                toggle.classList.toggle('is-open', direction === 'up');
            }

            async function loadRankTags() {
                try {
                    const json = await fetchJsonWithRetry(SHORTDRAMA_RANK_API, {
                        retries: 2,
                        timeout: RANK_API_TIMEOUT
                    });

                    if (json && json.code === 200 && Array.isArray(json.data)) {
                        rankData = json.data;
                        renderRankTags(false);
                    }
                } catch (e) {
                    console.warn('短剧热度榜加载失败:', e);
                }
            }

            async function loadVtquarkTags() {
                const section = document.getElementById('vtquarkSection');

                if (section) {
                    section.style.display = 'block';
                }

                setVtquarkToggleText(showVtquark ? '收起' : '展开查看', showVtquark ? 'up' : 'down');
                setVtquarkStatus('加载中...', 'loading');
                renderVtquarkTags(false);

                try {
                    const json = await fetchJsonWithRetry(VTQUARK_API, {
                        retries: 3,
                        delay: 700,
                        timeout: RANK_API_TIMEOUT
                    });

                    if (json && json.code === 200 && Array.isArray(json.data) && json.data.length > 0) {
                        vtquarkData = json.data;
                        saveVtquarkCache(vtquarkData);

                        setVtquarkStatus(getVtquarkLoadedStatusText(vtquarkData), 'ready');
                        renderVtquarkTags(false);

                        return;
                    }

                    throw new Error('接口返回为空或格式异常');
                } catch (e) {
                    console.warn('夸克热搜榜加载失败，尝试读取缓存:', e);

                    const cached = readVtquarkCache();

                    if (cached.length > 0) {
                        vtquarkData = cached;

                        const displayCount = getVtquarkDisplayCount(cached);
                        setVtquarkStatus(`缓存 ${displayCount} 条`, 'cache');
                        renderVtquarkTags(false);

                        return;
                    }

                    vtquarkData = [];

                    setVtquarkStatus('加载失败，重试中', 'error');
                    renderVtquarkTags(false);

                    setTimeout(() => {
                        loadVtquarkTags();
                    }, 5000);
                }
            }

            function buildRankTagsHtml() {
                let html = '';

                const limit = showAllRank ? 20 : 10;

                rankData.slice(0, limit).forEach((item, idx) => {
                    const title = normalizeSearchKeyword(item.title || '');

                    if (!title) return;

                    html += `<span class="tag" data-keyword="${escapeHtml(title)}">
                            <span class="tag-rank">${item.ranking || idx + 1}</span>
                            ${escapeHtml(title)}
                            <span class="tag-hot">🔥 ${escapeHtml(item.hots)}</span>
                        </span>`;
                });

                return html;
            }

            function renderRankTags(animated = false) {
                const list = document.getElementById('rankTagsList');
                const hint = document.getElementById('rankMoreHint');

                if (!list || !hint) return;

                const html = buildRankTagsHtml();

                smoothRenderCollapsibleList(list, html, rankTagsCollapsed, {
                    animated
                });

                if (rankTagsCollapsed) {
                    setSoftElementVisible(hint, false);
                    setRankToggleText('展开榜单', 'down');
                    return;
                }

                if (rankData.length > 10) {
                    setSoftElementVisible(hint, !showAllRank);
                    setRankToggleText(
                        showAllRank ? '收起到前 10 条' : '展开更多',
                        showAllRank ? 'up' : 'down'
                    );
                } else {
                    setSoftElementVisible(hint, false);
                    setRankToggleText('收起榜单', 'up');
                }
            }

            function buildVtquarkTagsHtml() {
                let html = '';

                if (!vtquarkData || vtquarkData.length === 0) {
                    if (showVtquark) {
                        html = `<span class="tag disabled">夸克热搜榜暂无数据，正在尝试重新加载...</span>`;
                    }

                    return html;
                }

                vtquarkData.slice(0, 10).forEach((item, idx) => {
                    const title = normalizeSearchKeyword(item.content_title || '');

                    if (!title) return;

                    html += `<span class="tag" data-keyword="${escapeHtml(title)}">
                            <span class="tag-rank">${item.content_rank || idx + 1}</span>
                            ${escapeHtml(title)}
                            <span class="tag-hot">🔥 ${escapeHtml(item.hot)}</span>
                        </span>`;
                });

                return html;
            }

            function renderVtquarkTags(animated = false) {
                const list = document.getElementById('vtquarkTagsList');

                if (!list) return;

                const html = buildVtquarkTagsHtml();

                smoothRenderCollapsibleList(list, html, !showVtquark, {
                    animated
                });

                setVtquarkToggleText(showVtquark ? '收起' : '展开查看', showVtquark ? 'up' : 'down');
            }

            function searchFromRankKeyword(keyword) {
                const term = normalizeSearchKeyword(keyword);

                if (!term) {
                    showStatus('榜单关键词为空');
                    return;
                }

                if (window.location.hash !== '#/' && window.location.hash !== '') {
                    window.location.hash = '#/';
                } else {
                    navigateTo('search');
                }

                typeSelect.value = 'all';
                currentPreset = 'all';
                searchInput.value = term;

                setTimeout(() => {
                    performSearch(term, {
                        immediate: true,
                        forceAll: true,
                        retryIfEmpty: true
                    });
                }, 0);
            }

            function bindNeoSourceGridLinks() {
                const sourceGrid = document.querySelector('.neo-source-grid');
                if (!sourceGrid) return;

                const sourceLabels = {
                    baidu: '百度网盘',
                    quark: '夸克网盘',
                    aliyun: '阿里云盘',
                    magnet: '磁力链接'
                };

                sourceGrid.addEventListener('click', event => {
                    const chip = event.target.closest('[data-neo-source]');
                    if (!chip) return;

                    const source = chip.getAttribute('data-neo-source');
                    if (!source || !TYPE_PRESETS[source]) return;

                    navigateTo('search');
                    typeSelect.value = source;
                    currentPreset = source;

                    // 中文：快捷来源按钮不仅切换下拉框，也写入可分享 hash，并通过高亮告诉用户当前搜索范围。
                    // English: Source shortcuts update both the select and the shareable hash, while the active highlight shows the current search scope.
                    syncSearchSourceHash(source);
                    updateNeoSourceGridActive(source);

                    const term = normalizeSearchKeyword(searchInput.value);
                    const label = sourceLabels[source] || TYPE_LABEL[source] || source;

                    // 中文：来源标签的职责是快速切换搜索范围；如果已有关键词就立即重搜，否则聚焦输入框减少下一步操作成本。
                    // English: Source chips are quick search-scope switches; with an existing keyword they re-search immediately, otherwise they focus the input to reduce the next action.
                    if (term) {
                        performSearch(term, {
                            immediate: true,
                            retryIfEmpty: true
                        });
                    } else {
                        searchInput.focus();
                        showStatus(`已切换到${label}，请输入关键词搜索`);
                    }
                });

                updateNeoSourceGridActive(currentPreset);
            }

            const toggleMoreRankEl = document.getElementById('toggleMoreRank');

            if (toggleMoreRankEl) {
                toggleMoreRankEl.addEventListener('click', () => {
                    /*
                         * 完全收起状态：
                         * 点击后恢复默认前 10 条。
                         */
                    if (rankTagsCollapsed) {
                        rankTagsCollapsed = false;
                        showAllRank = false;
                        renderRankTags(true);
                        return;
                    }

                    /*
                         * 正常状态：
                         * 前 10 条 <=> 前 20 条。
                         */
                    if (!showAllRank && rankData.length > 10) {
                        showAllRank = true;
                    } else {
                        showAllRank = false;

                        if (rankData.length <= 10) {
                            rankTagsCollapsed = true;
                        }
                    }

                    renderRankTags(true);
                });
            }

            const toggleVtquarkEl = document.getElementById('toggleVtquark');

            if (toggleVtquarkEl) {
                toggleVtquarkEl.addEventListener('click', () => {
                    showVtquark = !showVtquark;

                    if (showVtquark) {
                        if (vtquarkData.length > 0) {
                            setVtquarkStatus(getVtquarkLoadedStatusText(vtquarkData), 'ready');
                        } else {
                            setVtquarkStatus('加载中...', 'loading');
                            loadVtquarkTags();
                        }
                    } else {
                        if (vtquarkData.length > 0) {
                            setVtquarkStatus(getVtquarkLoadedStatusText(vtquarkData), 'ready');
                        } else {
                            setVtquarkStatus('加载中...', 'loading');
                        }
                    }

                    renderVtquarkTags(true);
                });
            }

            const rankTagsListEl = document.getElementById('rankTagsList');

            if (rankTagsListEl) {
                rankTagsListEl.addEventListener('click', (e) => {
                    const tag = e.target.closest('.tag');
                    if (!tag || tag.classList.contains('disabled')) return;

                    searchFromRankKeyword(tag.dataset.keyword);
                });
            }

            const vtquarkTagsListEl = document.getElementById('vtquarkTagsList');

            if (vtquarkTagsListEl) {
                vtquarkTagsListEl.addEventListener('click', (e) => {
                    const tag = e.target.closest('.tag');
                    if (!tag || tag.classList.contains('disabled')) return;

                    searchFromRankKeyword(tag.dataset.keyword);
                });
            }

            // ==================== 热度榜页面逻辑 ====================
            let currentRankSource = 'drama';

            function initRankPage() {
                document.querySelectorAll('.rank-tab').forEach(tab => {
                    tab.onclick = () => {
                        const activeTab = document.querySelector('.rank-tab.active');
                        if (activeTab) activeTab.classList.remove('active');

                        tab.classList.add('active');
                        currentRankSource = tab.dataset.source;
                        renderRankList();
                    };
                });

                rankSearchInput.oninput = renderRankList;

                /**
                 * 不再使用内联 onclick / ondblclick。
                 * 原因：
                 * 标题里如果有引号、HTML实体、特殊符号，内联 JS 容易出问题。
                 */
                rankListContainer.onclick = (e) => {
                    const btn = e.target.closest('.rank-to-search-btn');
                    if (!btn) return;

                    const item = btn.closest('.rank-result-item');
                    const keyword = btn.dataset.keyword || item?.dataset.keyword || '';

                    handleRankItemClick(keyword);
                };

                rankListContainer.ondblclick = (e) => {
                    const item = e.target.closest('.rank-result-item');
                    if (!item) return;

                    handleRankItemClick(item.dataset.keyword);
                };

                renderRankList();
            }

            function renderRankList() {
                const keyword = normalizeSearchKeyword(rankSearchInput.value).toLowerCase();

                let sourceData = currentRankSource === 'drama' ? rankData : vtquarkData;
                let filtered = sourceData;

                if (keyword) {
                    filtered = sourceData.filter(item => {
                        const title = normalizeSearchKeyword(item.title || item.content_title || '').toLowerCase();
                        return title.includes(keyword);
                    });
                }

                if (filtered.length === 0) {
                    rankListContainer.innerHTML = `<div class="status-message"><p>没有找到相关内容</p></div>`;
                    return;
                }

                let html = `<div class="result-list">`;

                filtered.forEach((item, index) => {
                    const title = normalizeSearchKeyword(item.title || item.content_title || '未知');
                    const hot = item.hots || item.hot || '0';
                    const rank = item.ranking || item.content_rank || (index + 1);

                    html += `<div class="result-item rank-result-item"
                            data-keyword="${escapeHtml(title)}"
                            style="animation-delay: ${index * 0.03}s">

                            <div class="drama-title" style="cursor: pointer;">
                                <span class="tag-rank" style="margin-right: 5px; font-size: 14px; color: ${rank <= 3 ? 'var(--accent)' : '#888'};">
                                    ${rank}.
                                </span>
                                ${escapeHtml(title)}
                            </div>

                            <div class="info-list">
                                <div class="info-item">
                                    <span class="info-label">热度:</span>
                                    <span style="color: #ff9500;">🔥 ${escapeHtml(hot)}</span>
                                </div>
                            </div>

                            <div style="text-align: right; margin-top: 5px;">
                                <button class="rank-to-search-btn"
                                    data-keyword="${escapeHtml(title)}"
                                    type="button">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                        <circle cx="11" cy="11" r="8"/>
                                        <path d="m21 21-4.3-4.3"/>
                                    </svg>
                                    全局搜索资源
                                </button>
                            </div>
                        </div>`;
                });

                html += `</div>`;
                rankListContainer.innerHTML = html;
            }

            function handleRankItemClick(keyword) {
                searchFromRankKeyword(keyword);
            }

            // ==================== 每日影视 ====================
            let dailyData = []; let filteredDaily = [];

            async function loadDailyResources() {
                dailyStats.textContent = '正在加载...';
                dailyResultsArea.innerHTML = `<div class="status-message"><div class="spinner"></div><p>正在加载今日影视资源...</p></div>`;
                try {
                    const [baiduData, quarkData] = await Promise.all([fetchDailyApi('baidu'), fetchDailyApi('quark')]);
                    dailyData = [...(baiduData || []), ...(quarkData || [])];
                    dailyData.sort((a, b) => (new Date(b.addtime).getTime() || 0) - (new Date(a.addtime).getTime() || 0));
                    filteredDaily = dailyData;
                    renderDailyResults(filteredDaily);
                } catch (error) { dailyResultsArea.innerHTML = `<div class="status-message" style="color: var(--error);"><p>加载失败</p></div>`; }
            }

            async function fetchDailyApi(source) {
                const controller = new AbortController();
                const timeoutPromise = new Promise((_, reject) => { timeoutId = setTimeout(() => { controller.abort(); reject({ errorType: 'timeout' }); }, SEARCH_TIMEOUT); });
                try {
                    const response = await Promise.race([fetch(`${YINGSHI_API}?${source}`, { signal: controller.signal }), timeoutPromise]);
                    if (!response.ok) throw { errorType: 'server' };
                    const json = await response.json();
                    if (json && json.code === 1 && Array.isArray(json.data)) return json.data.map(item => ({ ...item, _source: source }));
                    return [];
                } catch (error) { if (error.name === 'AbortError') throw { errorType: 'timeout' }; throw error; } finally { clearTimeouts(); }
            }

            function renderDailyResults(data) {
                if (!data || data.length === 0) { dailyStats.textContent = '未获取到今日影视资源。'; dailyResultsArea.innerHTML = `<div class="status-message"><p>未获取到今日影视资源。</p></div>`; return; }

                // 1. 按来源分组
                const grouped = {};
                data.forEach(item => { const source = item._source || 'baidu'; if (!grouped[source]) grouped[source] = []; grouped[source].push(item); });

                // 2. 排序：百度第一，夸克第二
                let sortedSources = [];
                ['baidu', 'quark'].forEach(p => { if (grouped[p]) sortedSources.push(p); });
                Object.keys(grouped).forEach(s => { if (!sortedSources.includes(s)) sortedSources.push(s); });

                dailyStats.textContent = `共 ${data.length} 条影视资源`;
                let html = '';

                sortedSources.forEach((source) => {
                    const items = grouped[source]; if (!items || items.length === 0) return;
                    const sourceName = source === 'baidu' ? '百度网盘' : '夸克网盘';
                    const safeSource = source.replace(/\s+/g, '_');

                    html += `<div class="result-section" id="daily-${safeSource}">
                            <div class="section-header">
                                <div>
                                    <span class="toggle-icon">▼</span>
                                    <span class="section-label ${safeSource}">${sourceName}</span>
                                    <span style="margin-left: 6px; font-size: 13px; color: #888;">${items.length} 条</span>
                                </div>
                            </div>
                            <div class="result-list">`;

                    items.forEach((item, index) => {
                        const name = item.name || '未知'; const link = item.viewlink || '#'; const addtime = item.addtime || '';
                        const domain = extractDomain(link); const iconUrl = domain ? `${ICO_API}?url=https://${domain}` : '';
                        html += `<div class="result-item" style="animation-delay: ${index * 0.03}s" data-link="${escapeHtml(link)}">
                                <button class="qr-toggle-btn" title="分享二维码" onclick="event.stopPropagation(); openQrModal('${escapeHtml(link)}')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg></button>
                                <div class="drama-title">${escapeHtml(name)}</div>
                                <div class="info-list">
                                    <div class="info-item"><span class="info-label">更新:</span><span>${escapeHtml(addtime)}</span></div>
                                    <div class="info-item"><span class="info-label">链接:</span><a href="${escapeHtml(link)}" target="_blank" class="info-link">${iconUrl ? `<img src="${iconUrl}" class="source-icon" onerror="this.style.display='none'">` : ''}${escapeHtml(link)}</a></div>
                                </div>
                            </div>`;
                    });

                    html += `</div></div>`;
                });

                dailyResultsArea.innerHTML = html;
                bindSectionToggleEvents(); // 绑定折叠事件
            }

            dailySearchInput.addEventListener('input', () => { const k = dailySearchInput.value.trim().toLowerCase(); filteredDaily = k ? dailyData.filter(i => (i.name || '').toLowerCase().includes(k) || (i.viewlink || '').toLowerCase().includes(k)) : dailyData; renderDailyResults(filteredDaily); });
            dailyRefreshBtn.addEventListener('click', () => { window.location.hash = '#/daily'; window.location.reload(); });

            // ==================== API 生成器逻辑 ====================
            // function getCurrentPageBaseUrl() {
            //     return window.location.href.split(/[?#]/)[0];
            // }
            function getCurrentPageBaseUrl() {
                const currentUrl = new URL(window.location.href);
                let pathname = currentUrl.pathname || '/';

                /*
                     * 兼容几种部署方式：
                     * 1. https://selfemo.github.io/ShortDramaSearch/
                     * 2. https://selfemo.github.io/ShortDramaSearch/index.html
                     * 3. https://your-domain.com/
                     * 4. https://your-domain.com/index.html
                     *
                     * 目标：统一得到“当前项目根地址”，避免写死 GitHub Pages 地址。
                     */
                pathname = pathname.replace(/\/index\.html?$/i, '/');

                if (!pathname.endsWith('/')) {
                    pathname += '/';
                }

                return `${currentUrl.origin}${pathname}`;
            }

            function buildApiGeneratorUrl() {
                if (!apiKeywordInput || !apiFromSelect) return '';

                const keyword = normalizeSearchKeyword(apiKeywordInput.value);
                const from = apiFromSelect.value || 'all';

                if (!keyword) return '';

                const params = new URLSearchParams();
                params.set('q', keyword);
                params.set('from', from);
                params.set('format', 'json');

                return `${getCurrentPageBaseUrl()}?${params.toString()}`;
            }

            function setApiBuilderStatus(message, type = 'muted') {
                if (!apiPreviewStatus) return;

                apiPreviewStatus.textContent = message || '';
                apiPreviewStatus.className = `api-preview-status is-${type}`;
            }

            function setApiGeneratedUrl(url) {
                if (apiGeneratedUrl) {
                    apiGeneratedUrl.value = url || '';
                }

                if (apiOpenLink) {
                    if (url) {
                        apiOpenLink.href = url;
                        apiOpenLink.classList.remove('is-disabled');
                    } else {
                        apiOpenLink.href = 'javascript:void(0)';
                        apiOpenLink.classList.add('is-disabled');
                    }
                }
            }

            function updateApiGeneratedUrl(options = {}) {
                const url = buildApiGeneratorUrl();
                setApiGeneratedUrl(url);

                if (options.showHint) {
                    if (url) {
                        setApiBuilderStatus('API 链接已生成。可以复制、打开或预览 JSON。', 'success');
                    } else {
                        setApiBuilderStatus('请先输入搜索关键词。', 'error');
                    }
                }

                return url;
            }

            async function copyTextToClipboard(text) {
                if (!text) return false;

                try {
                    if (navigator.clipboard && window.isSecureContext) {
                        await navigator.clipboard.writeText(text);
                        return true;
                    }
                } catch (e) {}

                try {
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.setAttribute('readonly', 'readonly');
                    textarea.style.position = 'fixed';
                    textarea.style.left = '-9999px';
                    textarea.style.top = '-9999px';
                    document.body.appendChild(textarea);
                    textarea.select();

                    const ok = document.execCommand('copy');
                    document.body.removeChild(textarea);

                    return ok;
                } catch (e) {
                    return false;
                }
            }

            async function copyApiGeneratedUrl() {
                const url = updateApiGeneratedUrl();

                if (!url) {
                    setApiBuilderStatus('请先输入搜索关键词，再复制 API 链接。', 'error');
                    return;
                }

                const ok = await copyTextToClipboard(url);

                if (ok) {
                    setApiBuilderStatus('API 链接已复制。', 'success');
                } else {
                    setApiBuilderStatus('复制失败，请手动选中链接复制。', 'error');
                }
            }

            function getOrderedPreviewTypes(typeList) {
                const preferred = [
                    'baidu',
                    'quark',
                    'aliyun',
                    'tianyi',
                    'uc',
                    'mobile',
                    '115',
                    'pikpak',
                    'xunlei',
                    '123',
                    'magnet',
                    'ed2k'
                ];

                const safeList = Array.isArray(typeList) ? typeList : [];

                return [
                    ...preferred.filter(type => safeList.includes(type)),
                    ...safeList.filter(type => !preferred.includes(type))
                ];
            }

            function cleanPreviewItem(item) {
                const fixed = normalizeResourceItem({ ...(item || {}) });

                delete fixed._searchTerm;

                return fixed;
            }

            function buildLimitedPreviewData(mergedByType, typeList, limit = 5) {
                const previewData = {};
                const cursors = {};
                const orderedTypes = getOrderedPreviewTypes(typeList);

                let previewCount = 0;
                let hasMore = true;

                while (previewCount < limit && hasMore) {
                    hasMore = false;

                    for (const type of orderedTypes) {
                        if (previewCount >= limit) break;

                        const list = Array.isArray(mergedByType[type]) ? mergedByType[type] : [];
                        const cursor = cursors[type] || 0;

                        if (cursor >= list.length) continue;

                        if (!previewData[type]) previewData[type] = [];

                        previewData[type].push(cleanPreviewItem(list[cursor]));
                        cursors[type] = cursor + 1;
                        previewCount++;
                        hasMore = true;
                    }
                }

                return {
                    previewData,
                    previewCount,
                    previewTypes: Object.keys(previewData)
                };
            }

            function renderApiPreviewJson(payload) {
                if (!apiPreviewOutput) return;

                apiPreviewOutput.textContent = JSON.stringify(payload, null, 2);
            }

            function clearApiPreviewLinks(message = '暂无链接。请先点击“预览 JSON 结果”。') {
                if (apiPreviewLinksStatus) {
                    apiPreviewLinksStatus.textContent = message;
                }

                if (apiPreviewLinksList) {
                    apiPreviewLinksList.innerHTML = `
                            <div class="api-preview-empty">
                                ${escapeHtml(message)}
                            </div>
                        `;
                }
            }

            function flattenPreviewLinks(previewData, limit = 5) {
                const result = [];

                if (!previewData || typeof previewData !== 'object') {
                    return result;
                }

                const orderedTypes = getOrderedPreviewTypes(Object.keys(previewData));

                for (const type of orderedTypes) {
                    const list = Array.isArray(previewData[type]) ? previewData[type] : [];

                    for (const rawItem of list) {
                        if (result.length >= limit) break;

                        const item = normalizeResourceItem({ ...(rawItem || {}) });
                        const link = item.url || item.link || item.href || '';

                        if (!link || link === '#') continue;

                        result.push({
                            type,
                            item,
                            link
                        });
                    }

                    if (result.length >= limit) break;
                }

                return result;
            }

            function createApiPreviewLinkItem(entry, index) {
                const type = entry.type;
                const item = entry.item || {};
                const link = entry.link || '';

                const name = item.name || item.title || '未知资源';
                const pwd = extractPwdFromLink(link) || formatPwd(item.pwd || item.password || item.pass || item.code);
                const domain = extractDomain(link);
                const iconUrl = domain ? `${ICO_API}?url=https://${domain}` : '';

                return `
                        <div class="api-preview-link-item" style="animation-delay: ${index * 0.04}s" data-link="${escapeHtml(link)}">
                            <button class="api-preview-qr-btn" type="button" title="生成二维码" data-action="qr" data-link="${escapeHtml(link)}">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="3" y="3" width="7" height="7"/>
                                    <rect x="14" y="3" width="7" height="7"/>
                                    <rect x="3" y="14" width="7" height="7"/>
                                    <rect x="14" y="14" width="7" height="7"/>
                                </svg>
                            </button>

                            <div class="api-preview-link-title">${escapeHtml(name)}</div>

                            <div class="api-preview-link-meta">
                                <div class="api-preview-link-row">
                                    <span class="api-preview-link-label">来源:</span>
                                    <span class="api-preview-link-source">${escapeHtml(TYPE_LABEL[type] || type)}</span>
                                </div>

                                <div class="api-preview-link-row">
                                    <span class="api-preview-link-label">链接:</span>
                                    <a href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer" class="api-preview-link-url">
                                        ${iconUrl ? `<img src="${escapeHtml(iconUrl)}" class="source-icon" onerror="this.style.display='none'">` : ''}
                                        ${escapeHtml(link)}
                                    </a>
                                </div>

                                ${pwd ? `
                                    <div class="api-preview-link-row">
                                        <span class="api-preview-link-label">密码:</span>
                                        <span class="api-preview-link-pwd">${escapeHtml(pwd)}</span>
                                    </div>
                                ` : ''}
                            </div>

                            <div class="api-preview-link-actions">
                                <a class="api-preview-small-btn" href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer">
                                    打开链接
                                </a>

                                <button class="api-preview-small-btn" type="button" data-action="copy" data-link="${escapeHtml(link)}">
                                    复制链接
                                </button>

                                <button class="api-preview-small-btn" type="button" data-action="qr" data-link="${escapeHtml(link)}">
                                    生成二维码
                                </button>
                            </div>
                        </div>
                    `;
            }

            function bindApiPreviewLinkActions() {
                if (!apiPreviewLinksList) return;

                apiPreviewLinksList.querySelectorAll('[data-action="qr"]').forEach(btn => {
                    btn.addEventListener('click', event => {
                        event.preventDefault();
                        event.stopPropagation();

                        const link = btn.getAttribute('data-link') || '';
                        if (!link) return;

                        openQrModal(link);
                    });
                });

                apiPreviewLinksList.querySelectorAll('[data-action="copy"]').forEach(btn => {
                    btn.addEventListener('click', async event => {
                        event.preventDefault();
                        event.stopPropagation();

                        const link = btn.getAttribute('data-link') || '';
                        if (!link) return;

                        const ok = await copyTextToClipboard(link);

                        if (apiPreviewLinksStatus) {
                            apiPreviewLinksStatus.textContent = ok ? '链接已复制。' : '复制失败，请手动复制。';
                        }
                    });
                });
            }

            function renderApiPreviewLinks(previewData) {
                if (!apiPreviewLinksList) return;

                const links = flattenPreviewLinks(previewData, 5);

                if (!links.length) {
                    clearApiPreviewLinks('预览结果中没有可操作链接。');
                    return;
                }

                if (apiPreviewLinksStatus) {
                    apiPreviewLinksStatus.textContent = `已展示 ${links.length} 条可操作链接，支持打开、复制和生成二维码。`;
                }

                apiPreviewLinksList.innerHTML = links.map((entry, index) => {
                    return createApiPreviewLinkItem(entry, index);
                }).join('');

                bindApiPreviewLinkActions();
            }

            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }

            function getValidApiPresetName(presetName) {
                return Object.prototype.hasOwnProperty.call(TYPE_PRESETS, presetName) ? presetName : 'all';
            }

            function normalizeMergedSearchResult(result) {
                const mergedByType = result && result.mergedByType ? result.mergedByType : {};

                const typeList = Object.keys(mergedByType).filter(type => {
                    return Array.isArray(mergedByType[type]) && mergedByType[type].length > 0;
                });

                const countedTotal = typeList.reduce((sum, type) => {
                    return sum + mergedByType[type].length;
                }, 0);

                const rawTotal = Number(result && result.total ? result.total : 0);
                const total = Math.max(rawTotal, countedTotal);

                return {
                    mergedByType,
                    total,
                    typeList
                };
            }

            function isMergedSearchEmpty(result) {
                if (!result) return true;
                if (!result.mergedByType) return true;
                if (!Array.isArray(result.typeList)) return true;
                if (result.typeList.length === 0) return true;
                if (!result.total || result.total <= 0) return true;

                return false;
            }

            async function fetchAndMergeDataStable(term, presetName, options = {}) {
                const safePreset = getValidApiPresetName(presetName);
                const attempts = Number(options.attempts || 3);
                const delay = Number(options.delay || 700);

                let lastResult = null;
                let lastError = null;

                for (let i = 0; i < attempts; i++) {
                    try {
                        const result = await fetchAndMergeData(term, safePreset);
                        const normalized = normalizeMergedSearchResult(result);

                        lastResult = normalized;

                        if (!isMergedSearchEmpty(normalized)) {
                            return {
                                ...normalized,
                                effectivePreset: safePreset,
                                retryCount: i
                            };
                        }
                    } catch (error) {
                        lastError = error;
                    }

                    if (i < attempts - 1) {
                        await sleep(delay * (i + 1));
                    }
                }

                if (lastResult) {
                    return {
                        ...lastResult,
                        effectivePreset: safePreset,
                        retryCount: attempts - 1
                    };
                }

                if (lastError) throw lastError;

                return {
                    mergedByType: {},
                    total: 0,
                    typeList: [],
                    effectivePreset: safePreset,
                    retryCount: attempts - 1
                };
            }

            // async function previewApiFromBuilder() {
            //     if (!apiKeywordInput || !apiFromSelect) return;
            //
            //     const keyword = normalizeSearchKeyword(apiKeywordInput.value);
            //     const requestedFrom = apiFromSelect.value || 'all';
            //     const from = getValidApiPresetName(requestedFrom);
            //     const url = updateApiGeneratedUrl();
            //
            //     if (!keyword || !url) {
            //         setApiBuilderStatus('请先输入搜索关键词。', 'error');
            //
            //         renderApiPreviewJson({
            //             code: -1,
            //             msg: 'missing keyword'
            //         });
            //
            //         return;
            //     }
            //
            //     const oldText = apiPreviewBtn ? apiPreviewBtn.textContent : '';
            //
            //     if (apiPreviewBtn) {
            //         apiPreviewBtn.disabled = true;
            //         apiPreviewBtn.textContent = '预览中...';
            //     }
            //
            //     setApiBuilderStatus('正在请求接口并生成预览...', 'loading');
            //
            //     renderApiPreviewJson({
            //         code: 0,
            //         msg: 'loading',
            //         keyword,
            //         type: from,
            //         total: 0,
            //         data: {}
            //     });
            //
            //     try {
            //         const result = await fetchAndMergeDataStable(keyword, from, {
            //             attempts: 3,
            //             delay: 700
            //         });
            //
            //         const { mergedByType, total, typeList, effectivePreset } = result;
            //         const { previewData, previewCount } = buildLimitedPreviewData(mergedByType, typeList, 5);
            //
            //         /*
            //          * 注意：
            //          * 预览 JSON 的字段结构必须和真实 API 保持一致。
            //          * 这里只限制 data 内部最多展示 5 条结果，
            //          * 不额外添加 preview_count、preview_types、retry_count、preview_note、api_url 等字段。
            //          */
            //         const payload = {
            //             code: 0,
            //             msg: 'success',
            //             keyword,
            //             type: effectivePreset,
            //             total,
            //             data: previewData
            //         };
            //
            //         renderApiPreviewJson(payload);
            //
            //         if (previewCount > 0) {
            //             setApiBuilderStatus(`预览完成：真实结果共 ${total} 条，预览区仅展示前 ${previewCount} 条。`, 'success');
            //         } else {
            //             setApiBuilderStatus('接口已自动重试，但仍未搜索到结果。请确认关键词，或把来源切换为“全局聚合 / 网盘聚合”。', 'error');
            //         }
            //     } catch (error) {
            //         console.error(error);
            //
            //         renderApiPreviewJson({
            //             code: -1,
            //             msg: error.message || error.errorType || 'preview error'
            //         });
            //
            //         setApiBuilderStatus('预览失败，请检查关键词、网络或第三方接口状态。', 'error');
            //     } finally {
            //         if (apiPreviewBtn) {
            //             apiPreviewBtn.disabled = false;
            //             apiPreviewBtn.textContent = oldText || '预览 JSON 结果';
            //         }
            //     }
            // }
            async function previewApiFromBuilder() {
                if (!apiKeywordInput || !apiFromSelect) return;

                const keyword = normalizeSearchKeyword(apiKeywordInput.value);
                const requestedFrom = apiFromSelect.value || 'all';
                const from = getValidApiPresetName(requestedFrom);
                const url = updateApiGeneratedUrl();

                if (!keyword || !url) {
                    setApiBuilderStatus('请先输入搜索关键词。', 'error');

                    renderApiPreviewJson({
                        code: -1,
                        msg: 'missing keyword'
                    });

                    clearApiPreviewLinks('请输入关键词后再预览链接。');

                    return;
                }

                const oldText = apiPreviewBtn ? apiPreviewBtn.textContent : '';

                if (apiPreviewBtn) {
                    apiPreviewBtn.disabled = true;
                    apiPreviewBtn.textContent = '预览中...';
                }

                setApiBuilderStatus('正在请求接口并生成预览...', 'loading');
                clearApiPreviewLinks('正在等待 JSON 预览结果...');

                renderApiPreviewJson({
                    code: 0,
                    msg: 'loading',
                    keyword,
                    type: from,
                    total: 0,
                    data: {}
                });

                try {
                    const result = await fetchAndMergeDataStable(keyword, from, {
                        attempts: 3,
                        delay: 700
                    });

                    const { mergedByType, total, typeList, effectivePreset } = result;
                    const { previewData, previewCount } = buildLimitedPreviewData(mergedByType, typeList, 5);

                    /*
                         * JSON 预览保持真实 API 字段结构。
                         * 链接快捷操作单独渲染，不写入 JSON。
                         */
                    const payload = {
                        code: 0,
                        msg: 'success',
                        keyword,
                        type: effectivePreset,
                        total,
                        data: previewData
                    };

                    renderApiPreviewJson(payload);
                    renderApiPreviewLinks(previewData);

                    if (previewCount > 0) {
                        setApiBuilderStatus(`预览完成：真实结果共 ${total} 条，预览区仅展示前 ${previewCount} 条。`, 'success');
                    } else {
                        setApiBuilderStatus('接口已自动重试，但仍未搜索到结果。请确认关键词，或把来源切换为“全局聚合 / 网盘聚合”。', 'error');
                        clearApiPreviewLinks('没有可操作链接。');
                    }
                } catch (error) {
                    console.error(error);

                    renderApiPreviewJson({
                        code: -1,
                        msg: error.message || error.errorType || 'preview error'
                    });

                    clearApiPreviewLinks('预览失败，暂无可操作链接。');
                    setApiBuilderStatus('预览失败，请检查关键词、网络或第三方接口状态。', 'error');
                } finally {
                    if (apiPreviewBtn) {
                        apiPreviewBtn.disabled = false;
                        apiPreviewBtn.textContent = oldText || '预览 JSON 结果';
                    }
                }
            }

            function bindApiBuilderEvents() {
                if (!apiKeywordInput || !apiFromSelect) return;

                apiKeywordInput.addEventListener('input', () => {
                    updateApiGeneratedUrl();
                });

                apiFromSelect.addEventListener('change', () => {
                    updateApiGeneratedUrl({ showHint: true });
                });

                apiKeywordInput.addEventListener('keydown', e => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        previewApiFromBuilder();
                    }
                });

                if (apiGenerateBtn) {
                    apiGenerateBtn.addEventListener('click', () => {
                        updateApiGeneratedUrl({ showHint: true });
                    });
                }

                if (apiCopyBtn) {
                    apiCopyBtn.addEventListener('click', copyApiGeneratedUrl);
                }

                if (apiPreviewBtn) {
                    apiPreviewBtn.addEventListener('click', previewApiFromBuilder);
                }

                if (apiOpenLink) {
                    apiOpenLink.addEventListener('click', e => {
                        const url = updateApiGeneratedUrl();

                        if (!url) {
                            e.preventDefault();
                            setApiBuilderStatus('请先输入搜索关键词，再打开 API 链接。', 'error');
                        }
                    });
                }

                updateApiGeneratedUrl();
            }

            function updateHelpApiUrls() {
                const baseUrl = getCurrentPageBaseUrl();

                if (helpApiTemplateUrl) {
                    helpApiTemplateUrl.textContent = `${baseUrl}?q=关键词&from=来源&format=json`;
                }

                if (helpApiExampleUrl) {
                    const params = new URLSearchParams();
                    params.set('q', '飞驰人生3');
                    params.set('from', 'netdisk');
                    params.set('format', 'json');

                    helpApiExampleUrl.textContent = `${baseUrl}?${params.toString()}`;
                }
            }

            // ==================== URL 参数自动搜索与 API 模式 ====================
            async function checkUrlParams() {
                const params = new URLSearchParams(window.location.search);
                const query = params.get('q') || params.get('name') || params.get('s');
                const from = params.get('from') || 'all';
                const format = params.get('format');

                if (!query) return;

                const decodedQuery = decodeURIComponent(query);
                const safeFrom = getValidApiPresetName(from);

                if (format === 'json') {
                    document.body.innerHTML = 'Loading...';
                    document.body.style.cssText = 'background:#fff; color:#000; font-family: monospace; white-space: pre; padding:20px;';

                    try {
                        const { mergedByType, total, effectivePreset } = await fetchAndMergeDataStable(decodedQuery, safeFrom, {
                            attempts: 3,
                            delay: 700
                        });

                        /*
                             * 真实 API 输出保持稳定、干净。
                             * 不输出 type_count、retry_count 等调试字段。
                             */
                        document.body.innerText = JSON.stringify({
                            code: 0,
                            msg: 'success',
                            keyword: decodedQuery,
                            type: effectivePreset,
                            total,
                            data: mergedByType
                        }, null, 2);
                    } catch (error) {
                        document.body.innerText = JSON.stringify({
                            code: -1,
                            msg: error.message || error.errorType || 'Error'
                        }, null, 2);
                    }

                    return;
                }

                if (window.location.hash !== '#/' && window.location.hash !== '') {
                    window.location.hash = '#/';
                }

                setTimeout(() => {
                    const validTypes = Object.keys(TYPE_PRESETS);
                    typeSelect.value = validTypes.includes(from) ? from : 'all';
                    currentPreset = typeSelect.value;
                    searchInput.value = decodedQuery;

                    performSearch(decodedQuery, {
                        immediate: true,
                        retryIfEmpty: true
                    });
                }, 300);
            }

            // ==================== 帮助弹窗逻辑 ====================
            const helpBtn = document.getElementById('helpBtn');
            const helpModalOverlay = document.getElementById('helpModalOverlay');

            function openHelpModal() {
                if (!helpModalOverlay) return;

                showModalAnimated(helpModalOverlay);

                if (helpModalContent) {
                    helpModalContent.scrollTop = 0;
                    hideHelpScrollbarImmediately();
                }

                setTimeout(() => {
                    updateHelpScrollbar();

                    if (
                        helpModalContent &&
                        helpModalContent.scrollHeight > helpModalContent.clientHeight + 1
                    ) {
                        showHelpScrollbarTemporarily();
                    }
                }, 380);
            }
            function closeHelpModal() {
                hideModalAnimated(helpModalOverlay, () => {
                    hideHelpScrollbarImmediately();
                });
            }

            if (helpBtn) {
                helpBtn.addEventListener('click', openHelpModal);
            }

            // 点击空白区域关闭弹窗
            if (helpModalOverlay) {
                helpModalOverlay.addEventListener('click', e => {
                    if (e.target === helpModalOverlay) closeHelpModal();
                });
            }

            // ==================== 帮助弹窗自定义滚动条逻辑 ====================
            const helpModalBody = document.querySelector('#helpModalOverlay .help-modal-body');
            const helpModalContent = document.querySelector('#helpModalOverlay .help-modal-content');
            const helpScrollbarThumb = document.querySelector('#helpModalOverlay .help-custom-scrollbar-thumb');

            let helpScrollbarTimer = null;
            let helpScrollbarRaf = null;

            function updateHelpScrollbar() {
                if (!helpModalBody || !helpModalContent || !helpScrollbarThumb) return;

                const scrollHeight = helpModalContent.scrollHeight;
                const clientHeight = helpModalContent.clientHeight;
                const scrollTop = helpModalContent.scrollTop;

                const canScroll = scrollHeight > clientHeight + 1;

                if (!canScroll) {
                    helpModalBody.classList.remove('show-scrollbar');
                    helpScrollbarThumb.style.height = '0px';
                    helpScrollbarThumb.style.top = '0px';
                    return;
                }

                const trackHeight = helpModalBody.clientHeight - 28;
                const thumbHeight = Math.max(36, Math.round((clientHeight / scrollHeight) * trackHeight));
                const maxThumbTop = trackHeight - thumbHeight;
                const maxScrollTop = scrollHeight - clientHeight;
                const thumbTop = maxScrollTop > 0
                    ? Math.round((scrollTop / maxScrollTop) * maxThumbTop)
                    : 0;

                helpScrollbarThumb.style.height = `${thumbHeight}px`;
                helpScrollbarThumb.style.top = `${thumbTop}px`;
            }

            function showHelpScrollbarTemporarily() {
                if (!helpModalBody || !helpModalContent) return;

                if (helpScrollbarRaf) {
                    cancelAnimationFrame(helpScrollbarRaf);
                }

                helpScrollbarRaf = requestAnimationFrame(() => {
                    updateHelpScrollbar();
                    helpModalBody.classList.add('show-scrollbar');
                });

                if (helpScrollbarTimer) {
                    clearTimeout(helpScrollbarTimer);
                }

                helpScrollbarTimer = setTimeout(() => {
                    helpModalBody.classList.remove('show-scrollbar');
                }, 1000);
            }

            function hideHelpScrollbarImmediately() {
                if (!helpModalBody) return;

                if (helpScrollbarTimer) {
                    clearTimeout(helpScrollbarTimer);
                    helpScrollbarTimer = null;
                }

                if (helpScrollbarRaf) {
                    cancelAnimationFrame(helpScrollbarRaf);
                    helpScrollbarRaf = null;
                }

                helpModalBody.classList.remove('show-scrollbar');
            }

            if (helpModalContent) {
                helpModalContent.addEventListener('scroll', showHelpScrollbarTemporarily, { passive: true });
                helpModalContent.addEventListener('wheel', showHelpScrollbarTemporarily, { passive: true });
                helpModalContent.addEventListener('touchmove', showHelpScrollbarTemporarily, { passive: true });

                window.addEventListener('resize', updateHelpScrollbar);
            }

            // ==================== 主页自定义滚动条逻辑 ====================
            const pageCustomScrollbar = document.getElementById('pageCustomScrollbar');
            const pageCustomScrollbarThumb = document.getElementById('pageCustomScrollbarThumb');

            let pageScrollbarTimer = null;
            let pageScrollbarRaf = null;

            function getPageScrollElement() {
                return document.scrollingElement || document.documentElement;
            }

            function isPageScrollbarLocked() {
                return document.body.classList.contains('scrollbar-locked') ||
                    document.body.style.overflow === 'hidden' ||
                    document.documentElement.style.overflow === 'hidden';
            }

            function updatePageScrollbar() {
                if (!pageCustomScrollbar || !pageCustomScrollbarThumb) return;

                const scrollElement = getPageScrollElement();
                const scrollHeight = scrollElement.scrollHeight;
                const clientHeight = window.innerHeight;
                const scrollTop = window.pageYOffset || scrollElement.scrollTop || 0;

                const canScroll = scrollHeight > clientHeight + 1 && !isPageScrollbarLocked();

                if (!canScroll) {
                    pageCustomScrollbar.classList.remove('show');
                    pageCustomScrollbarThumb.style.height = '0px';
                    pageCustomScrollbarThumb.style.top = '0px';
                    return;
                }

                const trackHeight = pageCustomScrollbar.clientHeight || Math.max(0, window.innerHeight - 28);
                const thumbHeight = Math.max(36, Math.round((clientHeight / scrollHeight) * trackHeight));
                const maxThumbTop = Math.max(0, trackHeight - thumbHeight);
                const maxScrollTop = Math.max(1, scrollHeight - clientHeight);
                const thumbTop = Math.round((scrollTop / maxScrollTop) * maxThumbTop);

                pageCustomScrollbarThumb.style.height = `${thumbHeight}px`;
                pageCustomScrollbarThumb.style.top = `${thumbTop}px`;
            }

            function showPageScrollbarTemporarily() {
                if (!pageCustomScrollbar || !pageCustomScrollbarThumb) return;

                if (isPageScrollbarLocked()) {
                    hidePageScrollbarImmediately();
                    return;
                }

                if (pageScrollbarRaf) {
                    cancelAnimationFrame(pageScrollbarRaf);
                }

                pageScrollbarRaf = requestAnimationFrame(() => {
                    updatePageScrollbar();

                    const scrollElement = getPageScrollElement();
                    if (scrollElement.scrollHeight > window.innerHeight + 1 && !isPageScrollbarLocked()) {
                        pageCustomScrollbar.classList.add('show');
                    }
                });

                if (pageScrollbarTimer) {
                    clearTimeout(pageScrollbarTimer);
                }

                pageScrollbarTimer = setTimeout(() => {
                    pageCustomScrollbar.classList.remove('show');
                }, 1000);
            }

            function hidePageScrollbarImmediately() {
                if (!pageCustomScrollbar) return;

                if (pageScrollbarTimer) {
                    clearTimeout(pageScrollbarTimer);
                    pageScrollbarTimer = null;
                }

                if (pageScrollbarRaf) {
                    cancelAnimationFrame(pageScrollbarRaf);
                    pageScrollbarRaf = null;
                }

                pageCustomScrollbar.classList.remove('show');
            }

            function bindPageScrollbarEvents() {
                window.addEventListener('scroll', showPageScrollbarTemporarily, { passive: true });
                window.addEventListener('wheel', showPageScrollbarTemporarily, { passive: true });
                window.addEventListener('touchmove', showPageScrollbarTemporarily, { passive: true });
                window.addEventListener('resize', updatePageScrollbar);

                document.addEventListener('keydown', (e) => {
                    const scrollKeys = [
                        'ArrowUp',
                        'ArrowDown',
                        'PageUp',
                        'PageDown',
                        'Home',
                        'End',
                        ' '
                    ];

                    if (scrollKeys.includes(e.key)) {
                        showPageScrollbarTemporarily();
                    }
                });

                if (window.ResizeObserver) {
                    const resizeObserver = new ResizeObserver(() => {
                        updatePageScrollbar();
                    });

                    resizeObserver.observe(document.body);
                } else {
                    const mutationObserver = new MutationObserver(() => {
                        updatePageScrollbar();
                    });

                    mutationObserver.observe(document.body, {
                        childList: true,
                        subtree: true,
                        attributes: true
                    });
                }

                setTimeout(updatePageScrollbar, 300);
            }

            // ==================== 收藏 / 历史事件 ====================
            if (searchHistoryList) {
                searchHistoryList.addEventListener('click', (e) => {
                    const chip = e.target.closest('.history-chip');
                    if (!chip) return;

                    const keyword = chip.dataset.historyKeyword || '';
                    if (!keyword) return;

                    performSearch(keyword, {
                        immediate: true,
                        retryIfEmpty: true
                    });
                });
            }

            if (clearHistoryBtn) {
                clearHistoryBtn.addEventListener('click', clearSearchHistory);
            }

            if (favoriteSearchInput) {
                favoriteSearchInput.addEventListener('input', renderFavorites);
            }

            if (clearFavoritesBtn) {
                clearFavoritesBtn.addEventListener('click', clearFavorites);
            }

            document.addEventListener('click', (e) => {
                const btn = e.target.closest('.resource-action-btn');
                if (!btn || btn.dataset.bound === '1') return;
                bindResourceActionEvents();
            });

            // ==================== 推荐增强功能：主题 / 导入导出 / 批量复制 ====================
            const themeToggleBtn = document.getElementById('themeToggleBtn');
            const copyCurrentLinksBtn = document.getElementById('copyCurrentLinksBtn');

            const exportHistoryBtn = document.getElementById('exportHistoryBtn');
            const importHistoryBtn = document.getElementById('importHistoryBtn');
            const importHistoryInput = document.getElementById('importHistoryInput');

            const exportFavoritesBtn = document.getElementById('exportFavoritesBtn');
            const importFavoritesBtn = document.getElementById('importFavoritesBtn');
            const importFavoritesInput = document.getElementById('importFavoritesInput');

            function downloadJsonFile(filename, data) {
                const blob = new Blob([JSON.stringify(data, null, 2)], {
                    type: 'application/json;charset=utf-8'
                });

                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');

                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();

                a.remove();
                URL.revokeObjectURL(url);
            }

            function readJsonFile(file) {
                return new Promise((resolve, reject) => {
                    if (!file) {
                        reject(new Error('未选择文件'));
                        return;
                    }

                    const reader = new FileReader();

                    reader.onload = () => {
                        try {
                            resolve(JSON.parse(reader.result));
                        } catch (err) {
                            reject(new Error('JSON 文件格式错误'));
                        }
                    };

                    reader.onerror = () => reject(new Error('文件读取失败'));
                    reader.readAsText(file, 'utf-8');
                });
            }

            function getSystemTheme() {
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                    return 'light';
                }
                return 'dark';
            }

            function normalizeTheme(theme) {
                return theme === 'light' || theme === 'dark' ? theme : null;
            }

            function safeGetLocalStorage(key) {
                try {
                    return localStorage.getItem(key);
                } catch (error) {
                    return null;
                }
            }

            function safeSetLocalStorage(key, value) {
                try {
                    localStorage.setItem(key, value);
                } catch (error) {}
            }

            function safeRemoveLocalStorage(key) {
                try {
                    localStorage.removeItem(key);
                } catch (error) {}
            }

            const THEME_MANUAL_KEY = 'kuleu_theme_manual';
            const THEME_MODE_KEY = 'kuleu_theme_mode';
            const THEME_LEGACY_KEY = 'kuleu_theme';

            /*
                 * 深浅模式最终方案：
                 * 1. 真实 DOM 不做颜色过渡。
                 * 2. 使用 View Transition 的页面快照做整页淡入淡出。
                 * 3. 避免“整体幕布闪”和“元素各自闪”。
                 */
            const THEME_SWITCH_UNLOCK_DELAY = 1200;

            let themeSwitchLocked = false;
            let systemThemeMediaQuery = null;
            let systemThemeListenerBound = false;

            function getThemeMode() {
                return safeGetLocalStorage(THEME_MODE_KEY) === 'manual' ? 'manual' : 'system';
            }

            function getInitialTheme() {
                const manualTheme = normalizeTheme(safeGetLocalStorage(THEME_MANUAL_KEY));

                if (getThemeMode() === 'manual' && manualTheme) {
                    return manualTheme;
                }

                // 中文：旧版本只写入 kuleu_theme_manual，容易导致网页永久停在旧主题；这里清掉旧缓存，恢复默认跟随设备。
                // English: Older builds wrote only kuleu_theme_manual, which could pin the page to a stale theme; clearing it restores device-following by default.
                safeRemoveLocalStorage(THEME_MANUAL_KEY);
                safeRemoveLocalStorage(THEME_MODE_KEY);
                return getSystemTheme();
            }

            function updateThemeToggleButton(theme) {
                if (!themeToggleBtn) return;

                const isLight = theme === 'light';
                const themeSource = getThemeMode();
                const modeLabel = themeSource === 'manual' ? '手动主题' : '跟随系统';
                const nextLabel = isLight ? '深色图标' : '浅色图标';

                // 中文：按钮只显示浅色/深色图标，同时在无障碍标签里说明当前是否跟随系统。
                // English: The switch keeps the visible UI icon-only while exposing system/manual state through accessible labels.
                themeToggleBtn.dataset.currentTheme = isLight ? 'light' : 'dark';
                themeToggleBtn.dataset.themeSource = themeSource;
                themeToggleBtn.title = `${modeLabel}：当前为${isLight ? '浅色图标' : '深色图标'}，点击切换为${nextLabel}`;
                themeToggleBtn.setAttribute('aria-label', `${modeLabel}：当前为${isLight ? '浅色图标' : '深色图标'}，点击切换为${nextLabel}`);
                themeToggleBtn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
            }

            function applyTheme(theme, options = {}) {
                const { save = false, showToast = false, source = null } = options;
                const nextTheme = normalizeTheme(theme) || getSystemTheme();
                const nextSource = source === 'manual' || source === 'system'
                    ? source
                    : (save ? 'manual' : getThemeMode());
                const isLight = nextTheme === 'light';
                const root = document.documentElement;

                root.classList.toggle('theme-light', isLight);
                root.setAttribute('data-theme', nextTheme);
                root.setAttribute('data-theme-source', nextSource);
                root.style.colorScheme = nextTheme;

                if (document.body) {
                    document.body.classList.toggle('theme-light', isLight);
                }

                if (save) {
                    safeSetLocalStorage(THEME_MANUAL_KEY, nextTheme);
                    safeSetLocalStorage(THEME_MODE_KEY, 'manual');
                }

                if (nextSource === 'system') {
                    safeRemoveLocalStorage(THEME_MANUAL_KEY);
                    safeRemoveLocalStorage(THEME_MODE_KEY);
                }

                updateThemeToggleButton(nextTheme);

                if (showToast) {
                    showStatus(isLight ? '已切换为浅色模式' : '已切换为深色模式');
                }
            }

            function prefersReducedMotion() {
                return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            }

            function lockThemeSwitch() {
                themeSwitchLocked = true;
                document.documentElement.classList.add('theme-switching');

                if (themeToggleBtn) {
                    themeToggleBtn.disabled = true;
                    themeToggleBtn.setAttribute('aria-busy', 'true');
                }
            }

            function unlockThemeSwitch() {
                document.documentElement.classList.remove('theme-switching');

                if (themeToggleBtn) {
                    themeToggleBtn.disabled = false;
                    themeToggleBtn.removeAttribute('aria-busy');
                }

                themeSwitchLocked = false;
            }

            function switchThemeWithAnimation(nextTheme, event) {
                if (themeSwitchLocked) return;

                const theme = normalizeTheme(nextTheme);
                if (!theme) return;

                const root = document.documentElement;
                const shouldReduceMotion = prefersReducedMotion();
                const transitionDuration = shouldReduceMotion ? 0 : 1050;

                function createThemeFadeLayer() {
                    if (!document.body || shouldReduceMotion) return null;

                    const source = document.querySelector('.bg-pattern') || document.body;
                    const style = window.getComputedStyle(source);
                    const layer = document.createElement('div');

                    layer.className = 'neo-theme-fade-layer';
                    layer.setAttribute('aria-hidden', 'true');
                    layer.style.backgroundColor = style.backgroundColor;
                    layer.style.backgroundImage = style.backgroundImage;
                    layer.style.backgroundPosition = style.backgroundPosition;
                    layer.style.backgroundSize = style.backgroundSize;
                    layer.style.backgroundRepeat = style.backgroundRepeat;
                    layer.style.backgroundAttachment = style.backgroundAttachment;

                    document.body.appendChild(layer);
                    return layer;
                }

                /*
                     * 中文：不再使用 View Transition，改用旧背景淡出层；这样背景会慢慢过渡，同时不会产生右侧半屏遮挡。
                     * English: View Transition is replaced by a fading old-background layer, so the background eases slowly without creating right-side half-screen masks.
                     */
                const fadeLayer = createThemeFadeLayer();
                themeSwitchLocked = true;
                root.classList.add('neo-theme-transitioning');

                if (themeToggleBtn) {
                    themeToggleBtn.disabled = true;
                    themeToggleBtn.setAttribute('aria-busy', 'true');
                }

                requestAnimationFrame(() => {
                    applyTheme(theme, {
                        save: true,
                        showToast: true
                    });

                    if (fadeLayer) {
                        requestAnimationFrame(() => {
                            fadeLayer.classList.add('is-fading');
                        });
                    }
                });

                window.setTimeout(() => {
                    root.classList.remove('neo-theme-transitioning');

                    if (fadeLayer && fadeLayer.parentNode) {
                        fadeLayer.parentNode.removeChild(fadeLayer);
                    }

                    if (themeToggleBtn) {
                        themeToggleBtn.disabled = false;
                        themeToggleBtn.removeAttribute('aria-busy');
                    }

                    themeSwitchLocked = false;
                }, transitionDuration + 120);
            }

            function bindSystemThemeAutoSync() {
                if (!window.matchMedia || systemThemeListenerBound) return;

                systemThemeMediaQuery = window.matchMedia('(prefers-color-scheme: light)');
                systemThemeListenerBound = true;

                const handleSystemThemeChange = event => {
                    const manualThemeNow = normalizeTheme(safeGetLocalStorage(THEME_MANUAL_KEY));
                    if (manualThemeNow) return;

                    // 系统变化不是站内主动点击，不走炫技动画，避免突然的动画干扰。
                    applyTheme(event.matches ? 'light' : 'dark', {
                        save: false,
                        showToast: false
                    });
                };

                if (systemThemeMediaQuery.addEventListener) {
                    systemThemeMediaQuery.addEventListener('change', handleSystemThemeChange);
                } else if (systemThemeMediaQuery.addListener) {
                    systemThemeMediaQuery.addListener(handleSystemThemeChange);
                }
            }

            function initThemeToggle() {
                // 清理旧版本保存的主题键；真正使用的是 kuleu_theme_manual。
                safeRemoveLocalStorage(THEME_LEGACY_KEY);

                // head 内联脚本已经在首屏渲染前设置过 html 主题；
                // 这里仅同步 body class 与按钮文字，不会产生可见跳变。
                applyTheme(getInitialTheme(), {
                    save: false,
                    showToast: false,
                    source: getThemeMode()
                });

                if (themeToggleBtn && themeToggleBtn.dataset.themeBound !== '1') {
                    themeToggleBtn.dataset.themeBound = '1';

                    themeToggleBtn.addEventListener('click', event => {
                        const currentTheme = document.documentElement.getAttribute('data-theme') === 'light'
                            ? 'light'
                            : 'dark';

                        const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
                        switchThemeWithAnimation(nextTheme, event);
                    });
                }

                bindSystemThemeAutoSync();
            }

            function exportSearchHistoryData() {
                const data = {
                    type: 'kuleu_search_history',
                    version: 1,
                    exportedAt: new Date().toISOString(),
                    data: getSearchHistory()
                };

                downloadJsonFile('kuleu-search-history.json', data);
                showStatus('搜索历史已导出');
            }

            async function importSearchHistoryData(file) {
                try {
                    const json = await readJsonFile(file);
                    const list = Array.isArray(json) ? json : json.data;

                    if (!Array.isArray(list)) {
                        showStatus('导入失败：文件内容不是搜索历史', 2500);
                        return;
                    }

                    const cleanList = [...new Set(
                        list
                            .map(item => String(item || '').trim())
                            .filter(Boolean)
                    )].slice(0, 30);

                    writeLocalList(LOCAL_KEYS.searchHistory, cleanList);
                    renderSearchHistory();
                    showStatus(`已导入 ${cleanList.length} 条搜索历史`);
                } catch (err) {
                    showStatus(err.message || '导入失败', 2500);
                } finally {
                    if (importHistoryInput) importHistoryInput.value = '';
                }
            }

            function exportFavoritesData() {
                const data = {
                    type: 'kuleu_favorites',
                    version: 1,
                    exportedAt: new Date().toISOString(),
                    data: getFavorites()
                };

                downloadJsonFile('kuleu-favorites.json', data);
                showStatus('收藏已导出');
            }

            async function importFavoritesData(file) {
                try {
                    const json = await readJsonFile(file);
                    const list = Array.isArray(json) ? json : json.data;

                    if (!Array.isArray(list)) {
                        showStatus('导入失败：文件内容不是收藏数据', 2500);
                        return;
                    }

                    const oldList = getFavorites();
                    const map = new Map();

                    oldList.forEach(item => {
                        if (item && item.link) map.set(item.link, item);
                    });

                    list.forEach(item => {
                        if (!item || !item.link) return;

                        map.set(item.link, {
                            id: item.id || makeResourceId(item),
                            name: item.name || item.title || '未命名资源',
                            link: item.link,
                            pwd: item.pwd || item.password || '',
                            type: item.type || item.source || '',
                            savedAt: item.savedAt || new Date().toISOString()
                        });
                    });

                    const merged = Array.from(map.values());

                    saveFavorites(merged);
                    renderFavorites();
                    updateFavoriteButtons();

                    showStatus(`已导入收藏，共 ${merged.length} 条`);
                } catch (err) {
                    showStatus(err.message || '导入失败', 2500);
                } finally {
                    if (importFavoritesInput) importFavoritesInput.value = '';
                }
            }

            function collectCurrentResultLinks() {
                const links = [];

                document.querySelectorAll('#resultsArea .result-item').forEach(item => {
                    const titleNode = item.querySelector('.drama-title');
                    const title = titleNode
                        ? Array.from(titleNode.childNodes)
                            .filter(node => node.nodeType === Node.TEXT_NODE)
                            .map(node => node.textContent.trim())
                            .join('')
                            .trim()
                        : '未命名资源';

                    const linkEl = item.querySelector('.info-link[href]');
                    const link = linkEl ? linkEl.href : '';

                    if (!link) return;

                    const pwdEl = item.querySelector('.info-item .info-label');
                    let pwd = '';

                    item.querySelectorAll('.info-item').forEach(row => {
                        const label = row.querySelector('.info-label')?.textContent?.trim() || '';
                        if (label.includes('密码') || label.includes('提取码')) {
                            const cloned = row.cloneNode(true);
                            const clonedLabel = cloned.querySelector('.info-label');
                            if (clonedLabel) clonedLabel.remove();

                            pwd = cloned.textContent.replace(/\s+/g, '').trim();
                        }
                    });

                    links.push(`${title}\n${link}${pwd ? `\n密码：${pwd}` : ''}`);
                });

                return links;
            }

            async function copyCurrentResultLinks() {
                const links = collectCurrentResultLinks();

                if (!links.length) {
                    showStatus('当前没有可复制的搜索结果', 2500);
                    return;
                }

                await copyTextToClipboard(links.join('\n\n'));
                showStatus(`已复制 ${links.length} 条结果链接`);
            }

            function bindExtraFeatureEvents() {
                initThemeToggle();

                if (copyCurrentLinksBtn) {
                    copyCurrentLinksBtn.addEventListener('click', copyCurrentResultLinks);
                }

                if (exportHistoryBtn) {
                    exportHistoryBtn.addEventListener('click', exportSearchHistoryData);
                }

                if (importHistoryBtn && importHistoryInput) {
                    importHistoryBtn.addEventListener('click', () => importHistoryInput.click());
                    importHistoryInput.addEventListener('change', () => {
                        importSearchHistoryData(importHistoryInput.files[0]);
                    });
                }

                if (exportFavoritesBtn) {
                    exportFavoritesBtn.addEventListener('click', exportFavoritesData);
                }

                if (importFavoritesBtn && importFavoritesInput) {
                    importFavoritesBtn.addEventListener('click', () => importFavoritesInput.click());
                    importFavoritesInput.addEventListener('change', () => {
                        importFavoritesData(importFavoritesInput.files[0]);
                    });
                }
            }



            function bindNeoCondensedNav() {
                const nav = document.querySelector('.neo-ui .app-nav');
                const menuBtn = document.getElementById('neoNavMenuBtn');
                const navLinksContainer = document.querySelector('.neo-ui .app-nav-links');
                const mainContent = document.querySelector('.neo-ui .main-content');

                if (!nav || !menuBtn || !navLinksContainer || menuBtn.dataset.neoCondensedBound === '1') return;

                menuBtn.dataset.neoCondensedBound = '1';
                let navRaf = null;

                function isMobileCondensedNav() {
                    return window.matchMedia && window.matchMedia('(max-width: 768px)').matches;
                }

                function getCondensedNavMetrics() {
                    const isMobile = isMobileCondensedNav();

                    // 中文：移动端使用“进入阈值”和“退出阈值”两条线，避免在短页面边界附近反复切换标题栏和菜单胶囊。
                    // English: Mobile uses separate enter and exit thresholds so the title bar and menu pill do not oscillate around the same short-page boundary.
                    return isMobile
                        ? { enter: 180, exit: 96, minScrollable: 320 }
                        : { enter: 82, exit: 24, minScrollable: 112 };
                }

                function getCurrentNeoPageName() {
                    if (document.body && document.body.dataset.neoPage) return document.body.dataset.neoPage;
                    return document.documentElement.getAttribute('data-neo-route') || getPageFromHash();
                }

                function getMaxScrollableDistance() {
                    const doc = document.documentElement;
                    const body = document.body;
                    const scrollHeight = Math.max(
                        doc ? doc.scrollHeight : 0,
                        body ? body.scrollHeight : 0
                    );

                    return Math.max(0, scrollHeight - window.innerHeight);
                }

                function canUseCondensedNav() {
                    const metrics = getCondensedNavMetrics();
                    const maxScrollableDistance = getMaxScrollableDistance();
                    const currentPage = getCurrentNeoPageName();
                    const isMobile = isMobileCondensedNav();

                    /*
                     * 中文：收藏为空这类短页面的最大可滚动距离小于菜单收缩所需的安全距离；如果仍然允许收缩，导航从普通流变成 fixed 后会缩短页面高度，scrollY 又被浏览器回弹到阈值以下，最终形成“菜单出现—标题回来—页面上移”的循环闪屏。
                     * English: Short pages such as an empty Favorites page have less scrollable distance than the safe distance needed for condensation; if condensation is still allowed, the nav leaves normal flow as fixed, the page height shrinks, the browser bounces scrollY below the threshold, and this creates the pill-title-page-jump flicker loop.
                     */
                    if (isMobile && currentPage === 'favorites' && maxScrollableDistance < metrics.minScrollable) {
                        return false;
                    }

                    // 中文：其它移动短页面也需要同样的安全距离，否则临界滚动区域会因为导航高度变化而抖动。
                    // English: Other short mobile pages need the same safety distance, otherwise the near-threshold scroll area can jitter when nav height changes.
                    if (isMobile) {
                        return maxScrollableDistance >= metrics.minScrollable;
                    }

                    // 中文：桌面端保留较低门槛，只阻止几乎不可滚动页面进入收缩态。
                    // English: Desktop keeps a lower requirement and only blocks condensation on pages that are almost not scrollable.
                    return maxScrollableDistance >= metrics.minScrollable;
                }

                function setMenuOpen(isOpen) {
                    document.body.classList.toggle('neo-nav-menu-open', isOpen);
                    menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                }

                let restoringTimer = null;
                let restoringRafOne = null;
                let restoringRafTwo = null;

                function clearRestoringState() {
                    if (restoringTimer) {
                        window.clearTimeout(restoringTimer);
                        restoringTimer = null;
                    }

                    if (restoringRafOne) {
                        window.cancelAnimationFrame(restoringRafOne);
                        restoringRafOne = null;
                    }

                    if (restoringRafTwo) {
                        window.cancelAnimationFrame(restoringRafTwo);
                        restoringRafTwo = null;
                    }

                    document.body.classList.remove(
                        'neo-nav-restoring',
                        'neo-nav-geometry-swap',
                        'neo-nav-restored',
                        'neo-nav-uncondensing'
                    );
                }

                function enterCondensedState() {
                    clearRestoringState();
                    document.body.classList.add('neo-nav-condensed');
                }

                function finishInstantRestore() {
                    clearRestoringState();
                    document.body.classList.remove('neo-nav-condensed');
                }

                function leaveCondensedState() {
                    setMenuOpen(false);

                    if (!document.body.classList.contains('neo-nav-condensed')) {
                        clearRestoringState();
                        return;
                    }

                    if (isMobileCondensedNav()) {
                        // 中文：移动端保留即时恢复，避免在短页面或橡皮筋滚动时人为增加一次透明淡入导致页面更容易抖动。
                        // English: Mobile keeps an instant restore so short pages or rubber-band scrolling do not get an extra artificial fade-in that could make jitter more noticeable.
                        finishInstantRestore();
                        return;
                    }

                    clearRestoringState();
                    document.body.classList.add('neo-nav-restoring');

                    restoringRafOne = window.requestAnimationFrame(() => {
                        restoringRafOne = null;

                        // 中文：先让“菜单”胶囊透明，再切换 fixed 胶囊和普通标题栏的几何状态，用户不会看到按钮从右上角滑回标题栏。
                        // English: The menu pill is made transparent before swapping from fixed pill geometry to normal title-bar geometry, so the user never sees the button slide back into the title bar.
                        document.body.classList.add('neo-nav-geometry-swap');
                        document.body.classList.remove('neo-nav-condensed');

                        restoringRafTwo = window.requestAnimationFrame(() => {
                            restoringRafTwo = null;
                            document.body.classList.remove('neo-nav-geometry-swap');
                            document.body.classList.add('neo-nav-restored');

                            restoringTimer = window.setTimeout(() => {
                                document.body.classList.remove('neo-nav-restoring', 'neo-nav-restored');
                                restoringTimer = null;
                            }, 190);
                        });
                    });
                }

                function syncCondensedState() {
                    const metrics = getCondensedNavMetrics();
                    const isCondensedNow = document.body.classList.contains('neo-nav-condensed');
                    const isRestoringNow = document.body.classList.contains('neo-nav-restoring');
                    const canCondense = canUseCondensedNav();

                    if (!canCondense) {
                        if (isCondensedNow) {
                            leaveCondensedState();
                        } else {
                            setMenuOpen(false);
                            clearRestoringState();
                        }
                        return;
                    }

                    // 中文：恢复动画进行中只允许“重新进入收缩态”打断，不重复触发离开逻辑；否则多次 requestAnimationFrame 会造成标题栏二次淡入。
                    // English: While the restore animation is running, only re-entering the condensed state may interrupt it; repeated leave calls are blocked because stacked requestAnimationFrame callbacks can make the title bar fade in twice.
                    if (isRestoringNow) {
                        if (window.scrollY > metrics.enter) {
                            enterCondensedState();
                        }
                        return;
                    }

                    // 中文：进入和退出使用不同阈值；进入需要滚得更深，退出允许回到较靠上的位置才恢复标题栏，从而消除短页面的临界抖动。
                    // English: Enter and exit use different thresholds; entering requires a deeper scroll while exiting waits until the page is closer to the top, removing boundary jitter on short pages.
                    const threshold = isCondensedNow ? metrics.exit : metrics.enter;
                    const shouldCondense = window.scrollY > threshold;

                    if (shouldCondense === isCondensedNow) {
                        if (!shouldCondense) setMenuOpen(false);
                        return;
                    }

                    if (shouldCondense) {
                        enterCondensedState();
                        return;
                    }

                    leaveCondensedState();
                }

                function requestCondensedSync() {
                    if (navRaf) return;

                    navRaf = window.requestAnimationFrame(() => {
                        navRaf = null;
                        syncCondensedState();
                    });
                }

                // 中文：路由切换、收藏列表渲染和窗口尺寸变化都会改变页面可滚动高度，统一暴露一个同步入口让这些变化后重新评估导航状态。
                // English: Route changes, Favorites rendering, and viewport changes all alter scrollable height, so one shared sync entry is exposed to re-evaluate nav state after those changes.
                window.neoRequestCondensedNavSync = requestCondensedSync;

                if (window.MutationObserver && document.body) {
                    const pageObserver = new MutationObserver(requestCondensedSync);
                    pageObserver.observe(document.body, {
                        attributes: true,
                        attributeFilter: ['data-neo-page']
                    });
                }

                if (window.ResizeObserver && mainContent) {
                    const contentObserver = new ResizeObserver(requestCondensedSync);
                    contentObserver.observe(mainContent);
                }

                menuBtn.addEventListener('click', event => {
                    event.preventDefault();
                    event.stopPropagation();

                    if (!document.body.classList.contains('neo-nav-condensed')) {
                        if (!canUseCondensedNav()) return;
                        enterCondensedState();
                    }

                    // 中文：菜单按钮只控制下拉显隐，不改变页面路由，因此不会影响原有导航逻辑。
                    // English: The menu button only toggles the dropdown and never changes routes, so the existing navigation logic remains untouched.
                    setMenuOpen(!document.body.classList.contains('neo-nav-menu-open'));
                });

                navLinksContainer.addEventListener('click', event => {
                    if (!event.target.closest('.nav-link')) return;

                    // 中文：用户从收缩菜单中完成选择后立即收起，避免跳转后菜单遮挡新页面内容。
                    // English: After a selection inside the condensed menu, it closes immediately so it does not cover the newly selected page.
                    if (document.body.classList.contains('neo-nav-condensed')) {
                        setMenuOpen(false);
                    }
                });

                document.addEventListener('click', event => {
                    if (!document.body.classList.contains('neo-nav-menu-open')) return;
                    if (nav.contains(event.target)) return;

                    setMenuOpen(false);
                });

                document.addEventListener('keydown', event => {
                    if (event.key === 'Escape') {
                        setMenuOpen(false);
                    }
                });

                window.addEventListener('scroll', requestCondensedSync, { passive: true });
                window.addEventListener('resize', requestCondensedSync);
                window.addEventListener('orientationchange', () => window.setTimeout(requestCondensedSync, 120));
                syncCondensedState();
            }

            // ==================== 初始化 ====================
            initRouter();
            bindAppTitleRefresh();
            bindNeoCondensedNav();
            bindPageScrollbarEvents();
            loadRankTags();
            loadVtquarkTags();
            bindApiBuilderEvents();
            bindNeoSourceGridLinks();
            updateHelpApiUrls();
            checkUrlParams();
            renderSearchHistory();
            renderFavorites();
            bindExtraFeatureEvents();

            // ==================== 新版稳定性提醒与用户条例每次打开 / 刷新都弹出 ====================
            showNeoNoticeModalOnPageLoad();

        const inlineHandlerExports = [
            ['closeHelpModal', typeof closeHelpModal === 'function' ? closeHelpModal : null],
            ['closeNeoNoticeModal', typeof closeNeoNoticeModal === 'function' ? closeNeoNoticeModal : null],
            ['closePolicyModal', typeof closePolicyModal === 'function' ? closePolicyModal : null],
            ['closeQrModal', typeof closeQrModal === 'function' ? closeQrModal : null],
            ['escapeHtml', typeof escapeHtml === 'function' ? escapeHtml : null],
            ['navigateTo', typeof navigateTo === 'function' ? navigateTo : null],
            ['openPolicyModal', typeof openPolicyModal === 'function' ? openPolicyModal : null],
            ['openQrModal', typeof openQrModal === 'function' ? openQrModal : null],
            ['pushNeoRouteHash', typeof pushNeoRouteHash === 'function' ? pushNeoRouteHash : null],
            ['rejectPolicy', typeof rejectPolicy === 'function' ? rejectPolicy : null],
        ];

        inlineHandlerExports.forEach(([name, handler]) => {
            if (handler) window[name] = handler;
        });

    })();
})();
