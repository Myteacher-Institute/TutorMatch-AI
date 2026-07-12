(function () {
  "use strict";

  var overlay = document.getElementById("mtcConfirmOverlay");
  if (!overlay) return;

  var messageEl = document.getElementById("mtcConfirmMessage");
  var titleEl = document.getElementById("mtcConfirmTitle");
  var okBtn = document.getElementById("mtcConfirmOk");
  var cancelBtn = document.getElementById("mtcConfirmCancel");

  var pendingForm = null;
  var pendingHref = null;

  function showModal(message, opts) {
    opts = opts || {};
    messageEl.textContent =
      message || "Are you sure you want to do this?";
    titleEl.textContent = opts.title || "Are you sure?";
    okBtn.textContent = opts.confirmLabel || "Yes, I'm sure";

    if (opts.danger) {
      overlay.classList.add("is-danger");
    } else {
      overlay.classList.remove("is-danger");
    }

    overlay.hidden = false;
    document.body.style.overflow = "hidden";
    okBtn.focus();
  }

  function hideModal() {
    overlay.hidden = true;
    document.body.style.overflow = "";
    pendingForm = null;
    pendingHref = null;
  }

  okBtn.addEventListener("click", function () {
    if (pendingForm) {
      pendingForm.submit();
    } else if (pendingHref) {
      window.location.href = pendingHref;
    }
    hideModal();
  });

  cancelBtn.addEventListener("click", hideModal);

  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) hideModal();
  });

  document.addEventListener("keydown", function (e) {
    if (overlay.hidden) return;
    if (e.key === "Escape") {
      hideModal();
    } else if (e.key === "Enter") {
      e.preventDefault();
      okBtn.click();
    }
  });

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (form && form.matches && form.matches("[data-confirm]")) {
      e.preventDefault();
      pendingForm = form;
      showModal(form.getAttribute("data-confirm"), {
        title: form.getAttribute("data-confirm-title") || undefined,
        confirmLabel: form.getAttribute("data-confirm-label") || undefined,
        danger: form.hasAttribute("data-confirm-danger"),
      });
    }
  });

  document.addEventListener("click", function (e) {
    var link = e.target.closest("a[data-confirm]");
    if (link) {
      e.preventDefault();
      pendingHref = link.getAttribute("href");
      showModal(link.getAttribute("data-confirm"), {
        title: link.getAttribute("data-confirm-title") || undefined,
        confirmLabel: link.getAttribute("data-confirm-label") || undefined,
        danger: link.hasAttribute("data-confirm-danger"),
      });
    }
  });

  window.mtcConfirm = showModal;
})();
