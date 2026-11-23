(function () {
    const MANUAL_THEME_KEY = 'kuleu_theme_manual';
    const LEGACY_THEME_KEY = 'kuleu_theme';
    try { window.localStorage.removeItem(LEGACY_THEME_KEY); } catch (_) {}
    let manualTheme = null;
    try { manualTheme = window.localStorage.getItem(MANUAL_THEME_KEY); } catch (_) {}
    const sysLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    const theme = (manualTheme === 'light' || manualTheme === 'dark') ? manualTheme : (sysLight ? 'light' : 'dark');
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    root.classList.toggle('theme-light', theme === 'light');
    root.style.colorScheme = theme;
})();
