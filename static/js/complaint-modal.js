(function () {
  "use strict";

  var activeModal = null;
  var activeTrigger = null;

  function closeModal() {
    if (!activeModal) return;
    activeModal.hidden = true;
    document.body.classList.remove("mtc-modal-open");
    if (activeTrigger) activeTrigger.focus();
    activeModal = null;
    activeTrigger = null;
  }

  function openModal(trigger) {
    var modal = document.getElementById(trigger.getAttribute("data-complaint-trigger"));
    if (!modal) return;

    activeModal = modal;
    activeTrigger = trigger;
    modal.hidden = false;
    document.body.classList.add("mtc-modal-open");
    var firstField = modal.querySelector("select, textarea, input:not([type=hidden])");
    if (firstField) firstField.focus();
  }

  document.addEventListener("click", function (event) {
    var trigger = event.target.closest("[data-complaint-trigger]");
    if (trigger) {
      openModal(trigger);
      return;
    }

    if (!activeModal) return;
    if (event.target === activeModal || event.target.closest("[data-complaint-close]")) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (activeModal && event.key === "Escape") closeModal();
  });
})();
