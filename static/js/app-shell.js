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

  function isStudentWorkspace() {
    const root = document.getElementById('chat-app-root');
    return !!(root && root.classList.contains('student-workspace'));
  }

  function tabletBreakpoint() {
    return isStudentWorkspace() ? 1024 : 768;
  }

  function updateDesktopToggleIcon(collapsed) {
    const btn = document.getElementById('desk-toggle-btn');
    if (!btn) return;

    if (collapsed) {
      btn.title = "Open sidebar";
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><polyline points="12 8 16 12 12 16"></polyline></svg>';
      btn.style.marginRight = '8px';
      if (window.innerWidth > tabletBreakpoint()) btn.style.display = 'grid';
    } else {
      btn.title = "Close sidebar";
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>';
      btn.style.marginRight = '';
      if (window.innerWidth > tabletBreakpoint()) btn.style.display = 'none';
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

    if (window.innerWidth <= tabletBreakpoint()) {
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
    if (sidebarCollapsed && window.innerWidth > tabletBreakpoint()) {
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

  window.toggleSaveTutor = function (button) {
    const tutorId = button.getAttribute('data-tutor-id');
    if (!tutorId) return;
    const url = '/toggle-save-tutor/' + tutorId + '/';
    const icon = button.querySelector('i');
    const label = button.querySelector('.save-tutor-label');
    button.disabled = true;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        const saved = !!data.saved;
        button.classList.toggle('is-saved', saved);
        if (icon) {
          icon.className = saved
            ? 'fa-solid fa-bookmark'
            : 'fa-regular fa-bookmark';
        }
        if (label) {
          label.textContent = saved ? 'Saved' : 'Save';
        }
        if (saved === false && button.hasAttribute('data-remove-on-unsave')) {
          const card = button.closest('[data-tutor-card]');
          if (card) card.remove();
          const grid = document.getElementById('saved-tutors-grid');
          if (grid && !grid.querySelector('[data-tutor-card]')) {
            const empty = document.getElementById('saved-tutors-empty');
            if (empty) empty.style.display = '';
          }
        }
      })
      .catch(function () {
        button.classList.remove('is-saved');
        if (icon) icon.className = 'fa-regular fa-bookmark';
        if (label) label.textContent = 'Save';
      })
      .finally(function () { button.disabled = false; });
  };

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const c = cookies[i].trim();
        if (c.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

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
