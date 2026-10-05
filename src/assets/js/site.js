(function () {
  "use strict";

  const config = window.ETA_SITE_CONFIG;
  if (!config) return;

  const language = (document.documentElement.lang || "en").toLowerCase().startsWith("es") ? "es" : "en";

  function normalizeCountry(value) {
    const country = String(value || "default").toLowerCase();
    return config.contacts[country] ? country : "default";
  }

  function contactFor(country) {
    return config.contacts[normalizeCountry(country)] || config.contacts.default;
  }

  function whatsappUrl(element) {
    const country = normalizeCountry(element.dataset.country || document.documentElement.dataset.country);
    const contact = contactFor(country);
    const digits = String(contact.whatsappE164 || "").replace(/\D/g, "");
    if (!digits) return "";
    const messageKey = element.dataset.messageKey || country;
    const languageMessages = config.messages[language] || config.messages.en;
    const message = languageMessages[messageKey] || languageMessages[country] || languageMessages.default;
    const pageLine = (language === "es" ? "Página: " : "Page: ") + window.location.href.split("#")[0];
    return "https://wa.me/" + digits + "?text=" + encodeURIComponent(message + "\n\n" + pageLine);
  }

  function bindContacts() {
    document.querySelectorAll("[data-contact='whatsapp']").forEach(function (element) {
      const href = whatsappUrl(element);
      if (!config.features.whatsapp || !href) {
        element.hidden = true;
        return;
      }
      element.href = href;
      element.target = "_blank";
      element.rel = "noopener noreferrer";
    });

    document.querySelectorAll("[data-contact='email']").forEach(function (element) {
      const contact = contactFor(element.dataset.country || document.documentElement.dataset.country);
      if (!contact.email) {
        element.hidden = true;
        return;
      }
      element.href = "mailto:" + contact.email;
      if (element.dataset.showAddress === "true") element.textContent = contact.email;
    });
  }

  function initNavigation() {
    const toggle = document.querySelector("[data-menu-toggle]");
    const menu = document.querySelector("[data-mobile-menu]");
    if (toggle && menu) {
      const spanish = document.documentElement.lang === "es";
      function setMenu(open, restoreFocus) {
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", spanish ? (open ? "Cerrar menú" : "Abrir menú") : (open ? "Close menu" : "Open menu"));
        menu.hidden = !open;
        document.body.classList.toggle("menu-open", open);
        if (restoreFocus) toggle.focus();
      }
      toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
      document.addEventListener("keydown", function (event) {
        if (toggle.getAttribute("aria-expanded") !== "true") return;
        if (event.key === "Escape") { setMenu(false, true); return; }
        if (event.key === "Tab") {
          const controls = [toggle, ...menu.querySelectorAll('a:not([hidden]), summary, button:not([disabled])')].filter(el => el.getClientRects().length);
          const first = controls[0], last = controls[controls.length - 1];
          if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
          else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
      });
      menu.addEventListener("click", function (event) { if (event.target.closest("a")) setMenu(false); });
      window.matchMedia("(min-width: 961px)").addEventListener("change", function (event) { if (event.matches) setMenu(false); });

    }

    const currentPath = window.location.pathname.replace(/index\.html$/, "");
    document.querySelectorAll("[data-nav-link]").forEach(function (link) {
      const linkPath = new URL(link.href, window.location.origin).pathname.replace(/index\.html$/, "");
      if (linkPath === currentPath) link.setAttribute("aria-current", "page");
    });

    const languagePair = document.documentElement.dataset.languagePair;
    if (languagePair) {
      document.querySelectorAll("[data-language-switch]").forEach(function (link) {
        link.href = languagePair;
      });
    }
  }

  function initGlobalBindings() {
    document.querySelectorAll("[data-current-year]").forEach(function (element) {
      element.textContent = String(new Date().getFullYear());
    });
    document.querySelectorAll("[data-instagram]").forEach(function (element) {
      element.href = config.social.instagram;
    });
    document.querySelectorAll("[data-privacy-choices]").forEach(function (element) {
      element.addEventListener("click", function () {
        if (window.etaAnalytics) window.etaAnalytics.openPrivacyChoices();
      });
    });
    if (config.environment === "staging") document.documentElement.dataset.environment = "staging";
  }

  function initLeadForms() {
    document.querySelectorAll("[data-lead-form]").forEach(function (form) {
      form.addEventListener("focusin", function () {
        if (form.dataset.analyticsStarted) return;
        form.dataset.analyticsStarted = "true";
        window.etaAnalytics?.track("lead_start", { form_id: form.id || "trip_planning" });
      });

      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const status = form.querySelector("[data-form-status]");
        const submit = form.querySelector("[type='submit']");
        if (!config.leads.endpoint) {
          if (status) status.textContent = language === "es"
            ? "El envío seguro se activará cuando finalicemos Brevo. Por ahora, utiliza WhatsApp o correo."
            : "Secure submission will activate after Brevo setup. For now, please use WhatsApp or email.";
          return;
        }

        const payload = Object.fromEntries(new FormData(form).entries());
        payload.page_url = window.location.href;
        payload.language = language;
        payload.first_touch = window.etaAnalytics?.firstTouch() || null;
        if (submit) submit.disabled = true;
        if (status) status.textContent = language === "es" ? "Enviando…" : "Sending…";
        try {
          const response = await fetch(config.leads.endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          if (!response.ok) throw new Error("Lead endpoint rejected request");
          form.reset();
          if (status) status.textContent = language === "es" ? "Gracias. Te responderemos pronto." : "Thank you. We will reply soon.";
          window.etaAnalytics?.track("lead_submit", { form_id: form.id || "trip_planning" });
        } catch (_) {
          if (status) status.textContent = language === "es" ? "No pudimos enviar el formulario. Contáctanos por WhatsApp o correo." : "We could not submit the form. Please contact us by WhatsApp or email.";
        } finally {
          if (submit) submit.disabled = false;
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindContacts();
    initNavigation();
    initGlobalBindings();
    initLeadForms();
  });
})();
