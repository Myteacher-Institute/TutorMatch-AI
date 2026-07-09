/* Shared app-shell behaviour for the student workspace pages
   (dashboard, bookings, chat). Mirrors the AI assistant page. */
(function () {
  function toggleSidebarDesktop() {
    const root = document.getElementById('chat-app-root');
    if (!root) return;
    const collapsed = root.classList.toggle('sidebar-collapsed');
    try { localStorage.setItem('sidebar-collapsed', collapsed ? 'true' : 'false'); } catch (e) {}
    updateDesktopToggleIcon(collapsed);
  }

  function updateDesktopToggleIcon(collapsed) {
    const btn = document.getElementById('desk-toggle-btn');
    if (!btn) return;

    if (collapsed) {
      btn.title = "Open sidebar";
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><polyline points="12 8 16 12 12 16"></polyline></svg>';
      btn.style.marginRight = '8px';
      if (window.innerWidth > 768) btn.style.display = 'grid';
    } else {
      btn.title = "Close sidebar";
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>';
      btn.style.marginRight = '';
      if (window.innerWidth > 768) btn.style.display = 'none';
    }
  }

  function toggleSidebarMobile(open) {
    const root = document.getElementById('chat-app-root');
    if (!root) return;
    if (open) {
      root.classList.add('sidebar-open');
    } else {
      root.classList.remove('sidebar-open');
    }
  }

  function handleResponsiveLayout() {
    const root = document.getElementById('chat-app-root');
    if (!root) return;
    const deskToggle = document.getElementById('desk-toggle-btn');
    const mobToggle = document.getElementById('mobile-toggle-btn');
    const isCollapsed = root.classList.contains('sidebar-collapsed');

    if (window.innerWidth <= 768) {
      if (deskToggle) deskToggle.style.display = 'none';
      if (mobToggle) mobToggle.style.display = 'grid';
    } else {
      if (deskToggle) deskToggle.style.display = isCollapsed ? 'grid' : 'none';
      if (mobToggle) mobToggle.style.display = 'none';
      root.classList.remove('sidebar-open');
    }
  }

  function setAppTheme(themeVal) {
    try { localStorage.setItem('ai-theme', themeVal); } catch (e) {}
    applyThemeClass(themeVal);
    updateThemeSelectorActiveBtn(themeVal);
  }

  function applyThemeClass(themeVal) {
    const root = document.documentElement;
    if (themeVal === 'dark') {
      root.classList.add('dark');
    } else if (themeVal === 'light') {
      root.classList.remove('dark');
    } else {
      const matchesDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (matchesDark) {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  }

  function updateThemeSelectorActiveBtn(themeVal) {
    document.querySelectorAll('.theme-btn-option').forEach((btn) => {
      if (btn.getAttribute('data-theme-val') === themeVal) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function initSavedAppState() {
    const root = document.getElementById('chat-app-root');
    if (!root) return;
    let sidebarCollapsed = false;
    try { sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true'; } catch (e) {}
    if (sidebarCollapsed && window.innerWidth > 768) {
      root.classList.add('sidebar-collapsed');
      updateDesktopToggleIcon(true);
    } else {
      updateDesktopToggleIcon(false);
    }

    let activeTheme = 'system';
    try { activeTheme = localStorage.getItem('ai-theme') || 'system'; } catch (e) {}
    setAppTheme(activeTheme);

    handleResponsiveLayout();
  }

  window.toggleSidebarDesktop = toggleSidebarDesktop;
  window.toggleSidebarMobile = toggleSidebarMobile;
  window.setAppTheme = setAppTheme;

  window.addEventListener('resize', handleResponsiveLayout);
  window.addEventListener('DOMContentLoaded', function () {
    initSavedAppState();
    handleResponsiveLayout();
  });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    try {
      if (localStorage.getItem('ai-theme') === 'system') {
        applyThemeClass('system');
      }
    } catch (e) {}
  });
})();
