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
    document.querySelectorAll("[data-lead-form]").forEach(async function (form) {
      const status = form.querySelector("[data-form-status]");
      const submit = form.querySelector("[type='submit']");
      const say = (en, es) => { if (status) status.textContent = language === "es" ? es : en; };
      form.querySelectorAll("[data-capitalize-name]").forEach(input => {
        input.addEventListener("blur", () => {
          input.value = input.value.trim().replace(/^\p{L}/u, letter => letter.toLocaleUpperCase(language));
        });
      });
      const startDate = form.querySelector('[name="start_date"]');
      const endDate = form.querySelector('[name="end_date"]');
      const guests = form.querySelector('[data-guests]');
      function updateDates() {
        const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/Guayaquil',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
        const part = type => parts.find(p => p.type === type).value;
        const today = part('year') + '-' + part('month') + '-' + part('day');
        startDate.min = today;
        endDate.min = startDate.value && startDate.value >= today ? startDate.value : today;
        endDate.setCustomValidity(endDate.value && endDate.value < endDate.min ? (language === 'es' ? 'Elige una fecha de fin igual o posterior al inicio, desde hoy.' : 'Choose an end date on or after the start date, from today onward.') : '');
      }
      updateDates();
      form.addEventListener('focusin', updateDates);
      startDate.addEventListener('input', updateDates);
      endDate.addEventListener('input', updateDates);
      guests.addEventListener('input', () => { guests.value = guests.value.replace(/\D/g, '').slice(0,2); });
      let widget;
      let preserveResult = false;
      submit.disabled = true;
      try {
        const response = await fetch(config.leads.endpoint, {cache: "no-store"});
        if (!response.ok) throw new Error("Unavailable");
        const settings = await response.json();
        if (!settings.siteKey) throw new Error("Unavailable");
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
          script.onload = resolve; script.onerror = reject; document.head.appendChild(script);
        });
        widget = window.turnstile.render(form.querySelector("[data-turnstile]"), {
          sitekey: settings.siteKey, action: "contact", language: language,
          callback: () => { submit.disabled = !settings.enabled; if (preserveResult) return; if (settings.enabled) say("Ready to send.", "Listo para enviar."); else say("Verification complete. Delivery is not active yet; please use email or WhatsApp.", "Verificación completada. El envío aún no está activo; usa correo o WhatsApp."); },
          "expired-callback": () => { submit.disabled = true; say("Please verify again.", "Verifica de nuevo."); },
          "error-callback": () => { submit.disabled = true; say("Verification unavailable. Use email or WhatsApp.", "La verificación no está disponible. Usa correo o WhatsApp."); }
        });
      } catch {
        say("The secure form is not active yet. Please use email or WhatsApp.", "El formulario seguro aún no está activo. Usa correo o WhatsApp.");
      }
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        updateDates();
        if (widget === undefined || submit.disabled || !form.reportValidity()) return;
        const values = Object.fromEntries(new FormData(form).entries());
        const payload = Object.fromEntries(["first_name","last_name","email","country","travelers","phone","start_date","end_date","interests","privacy_consent","website","cf-turnstile-response"].map(k => [k, values[k] || ""]));
        payload.language = language;
        preserveResult = true;
        submit.disabled = true; say("Sending…", "Enviando…");
        try {
          const response = await fetch(config.leads.endpoint, {method:"POST", headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
          const result = await response.json();
          if (!response.ok || result.ok !== true || result.status !== "queued") throw new Error("Not accepted");
          form.reset();
          if (result.acknowledgment === "queued") say("Your request has been received. A confirmation email is on its way; please check your spam folder too.", "Recibimos tu solicitud. El correo de confirmación está en camino; revisa también la carpeta de spam.");
          else say("Your request has been received, but we could not send the confirmation email. There is no need to submit again; our team will follow up.", "Recibimos tu solicitud, pero no pudimos enviar el correo de confirmación. No hace falta enviarla otra vez; nuestro equipo se pondrá en contacto contigo.");
          window.etaAnalytics?.track("lead_submit", {form_id:form.id});
        } catch {
          say("Your request was not confirmed. Please retry verification or use email or WhatsApp.", "No se confirmó tu solicitud. Verifica de nuevo o usa correo o WhatsApp.");
        } finally {
          window.turnstile.reset(widget);
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
