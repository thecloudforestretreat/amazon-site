// Experience The Amazon analytics and consent foundation.
// Load this file as early as possible in <head> on every public page.
(function () {
  "use strict";

  const GA_ID = "G-TTSHGZCZZW";
  const GTM_ID = "GTM-NT8BL3HL";
  const CONSENT_KEY = "eta_analytics_consent_v1";
  const ATTRIBUTION_KEY = "eta_first_touch_v1";
  const PROD_HOSTS = new Set(["experiencetheamazon.com", "www.experiencetheamazon.com"]);
  const isProduction = PROD_HOSTS.has(window.location.hostname);
  const isTrackablePage = isProduction && !/^\/testing(?:2|3)?(?:\/|$)/.test(window.location.pathname);
  const isSpanish = (document.documentElement.lang || "en").toLowerCase().startsWith("es");

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  // Consent Mode defaults are established before any Google tag can load.
  window.gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    wait_for_update: 500
  });
  window.gtag("set", "ads_data_redaction", true);
  window.gtag("set", "url_passthrough", true);

  let tagManagerLoaded = false;
  function loadTagManager() {
    if (tagManagerLoaded || !isTrackablePage) return;
    tagManagerLoaded = true;
    window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(GTM_ID);
    document.head.appendChild(script);
  }

  function safeStorageGet(key) {
    try { return window.localStorage.getItem(key); } catch (_) { return null; }
  }

  function safeStorageSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (_) {}
  }

  function sanitizeUrl(rawUrl) {
    try {
      const url = new URL(rawUrl, window.location.origin);
      const blocked = /^(email|e-mail|mail|phone|telephone|tel|name|first_name|last_name|fullname|full_name|message|comment|notes|whatsapp)$/i;
      Array.from(url.searchParams.keys()).forEach(function (key) {
        if (blocked.test(key)) url.searchParams.delete(key);
      });
      url.hash = "";
      return url.toString();
    } catch (_) {
      return window.location.origin + window.location.pathname;
    }
  }

  function pageContext() {
    const root = document.documentElement.dataset;
    const body = document.body ? document.body.dataset : {};
    const pathId = window.location.pathname.replace(/^\/+|\/+$/g, "").replace(/\//g, "_") || "home";
    return {
      page_id: body.pageId || root.pageId || pathId,
      pair_id: body.pairId || root.pairId || pathId.replace(/^es_/, ""),
      language: (document.documentElement.lang || "en").toLowerCase(),
      page_type: body.pageType || root.pageType || "landing",
      country: body.country || root.country || "",
      destination: body.destination || root.destination || "",
      topic_cluster: body.topicCluster || root.topicCluster || "",
      funnel_stage: body.funnelStage || root.funnelStage || "awareness"
    };
  }

  function captureFirstTouch() {
    if (safeStorageGet(ATTRIBUTION_KEY)) return;
    const query = new URLSearchParams(window.location.search);
    const record = {
      source: query.get("utm_source") || "",
      medium: query.get("utm_medium") || "",
      campaign: query.get("utm_campaign") || "",
      term: query.get("utm_term") || "",
      content: query.get("utm_content") || "",
      landing_page: window.location.pathname,
      captured_at: new Date().toISOString()
    };
    if (record.source || record.medium || record.campaign) {
      safeStorageSet(ATTRIBUTION_KEY, JSON.stringify(record));
    }
  }

  let pageViewSent = false;
  function loadGoogleTag() {
    if (pageViewSent || !isTrackablePage) return;
    pageViewSent = true;

    const context = pageContext();
    window.gtag("event", "page_view", Object.assign({}, context, {
      page_title: document.title,
      page_location: sanitizeUrl(window.location.href),
      page_referrer: document.referrer ? sanitizeUrl(document.referrer) : ""
    }));
  }

  function track(eventName, parameters) {
    if (safeStorageGet(CONSENT_KEY) !== "granted" || !isTrackablePage) return;
    const safeParameters = Object.assign({}, pageContext(), parameters || {});
    // Never accept arbitrary user-entered text as an event parameter.
    delete safeParameters.email;
    delete safeParameters.phone;
    delete safeParameters.name;
    delete safeParameters.message;
    window.gtag("event", eventName, safeParameters);
  }

  function setConsent(choice) {
    const granted = choice === "granted";
    safeStorageSet(CONSENT_KEY, granted ? "granted" : "denied");
    window.gtag("consent", "update", {
      analytics_storage: granted ? "granted" : "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    if (granted) loadGoogleTag();
    const banner = document.getElementById("eta-consent");
    if (banner) banner.remove();
  }

  function addConsentBanner(force) {
    if (!force && safeStorageGet(CONSENT_KEY)) return;
    const existing = document.getElementById("eta-consent");
    if (existing) existing.remove();

    const style = document.createElement("style");
    style.id = "eta-consent-style";
    style.textContent = "#eta-consent{position:fixed;z-index:2147483647;left:16px;right:16px;bottom:16px;max-width:760px;margin:auto;padding:18px 20px;background:#111;color:#f6f1e7;border:1px solid rgba(255,255,255,.24);border-radius:12px;box-shadow:0 14px 45px rgba(0,0,0,.45);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}#eta-consent p{margin:0 0 14px}#eta-consent strong{display:block;margin-bottom:4px;font-size:16px}#eta-consent .eta-consent-actions{display:flex;gap:10px;flex-wrap:wrap}#eta-consent button{min-height:42px;padding:9px 16px;border-radius:999px;border:1px solid #d7b86a;background:transparent;color:#f6f1e7;font:600 14px system-ui;cursor:pointer}#eta-consent button[data-choice=granted]{background:#d7b86a;color:#111}#eta-consent button:focus-visible{outline:3px solid #fff;outline-offset:2px}";
    if (!document.getElementById(style.id)) document.head.appendChild(style);

    const banner = document.createElement("section");
    banner.id = "eta-consent";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-live", "polite");
    banner.setAttribute("aria-label", isSpanish ? "Preferencias de privacidad" : "Privacy choices");
    banner.innerHTML = isSpanish
      ? "<p><strong>Tu privacidad importa</strong>Usamos analítica opcional para entender qué páginas ayudan a los viajeros. No usamos publicidad personalizada y no enviamos el contenido de formularios a Google Analytics.</p><div class=\"eta-consent-actions\"><button type=\"button\" data-choice=\"granted\">Permitir analítica</button><button type=\"button\" data-choice=\"denied\">Rechazar lo no esencial</button></div>"
      : "<p><strong>Your privacy matters</strong>We use optional analytics to understand which pages help travelers. We do not use personalized advertising or send form contents to Google Analytics.</p><div class=\"eta-consent-actions\"><button type=\"button\" data-choice=\"granted\">Allow analytics</button><button type=\"button\" data-choice=\"denied\">Reject non-essential</button></div>";
    banner.addEventListener("click", function (event) {
      const button = event.target.closest("button[data-choice]");
      if (button) setConsent(button.dataset.choice);
    });
    document.body.appendChild(banner);
  }

  function bindInteractionTracking() {
    document.addEventListener("click", function (event) {
      const link = event.target.closest("a,button");
      if (!link) return;
      const explicit = link.dataset.analyticsEvent;
      const href = link.tagName === "A" ? (link.getAttribute("href") || "") : "";
      const label = link.dataset.analyticsLabel || link.getAttribute("aria-label") || (link.textContent || "").trim().slice(0, 80);
      const common = {
        cta_id: link.dataset.ctaId || "",
        cta_position: link.dataset.ctaPosition || "",
        module_id: link.dataset.moduleId || "",
        link_text: label
      };

      if (explicit) return track(explicit, common);
      if (/^(https?:\/\/)?(wa\.me|api\.whatsapp\.com)/i.test(href)) return track("click_whatsapp", common);
      if (/^tel:/i.test(href)) return track("click_phone", common);
      if (/^mailto:/i.test(href)) return track("click_email", common);
      if (link.matches("[download],a[href$='.pdf'],a[href*='itinerary']")) return track("download_itinerary", common);
      if (link.getAttribute("lang") || /(^|\/)es(\/|$)/.test(href)) return track("language_switch", Object.assign(common, { target_language: /(^|\/)es(\/|$)/.test(href) ? "es" : "en" }));

      if (href && !href.startsWith("#") && !/^(mailto:|tel:|javascript:)/i.test(href)) {
        try {
          const target = new URL(href, window.location.href);
          if (target.origin === window.location.origin) {
            track("internal_link_click", Object.assign(common, { link_url: target.pathname }));
          } else {
            track("outbound_click", Object.assign(common, { link_domain: target.hostname, link_url: sanitizeUrl(target.href) }));
          }
        } catch (_) {}
      }
    }, true);

    document.addEventListener("focusin", function (event) {
      const form = event.target.closest("form");
      if (form && !form.dataset.analyticsStarted) {
        form.dataset.analyticsStarted = "true";
        track("form_start", { form_id: form.id || form.dataset.formId || "lead_form" });
      }
    });

    document.addEventListener("submit", function (event) {
      const form = event.target.closest("form");
      if (form) track("form_submit", { form_id: form.id || form.dataset.formId || "lead_form" });
    });
  }

  window.etaAnalytics = {
    track: track,
    grant: function () { setConsent("granted"); },
    deny: function () { setConsent("denied"); },
    openPrivacyChoices: function () { addConsentBanner(true); },
    firstTouch: function () {
      try { return JSON.parse(safeStorageGet(ATTRIBUTION_KEY) || "null"); } catch (_) { return null; }
    }
  };

  loadTagManager();
  captureFirstTouch();
  const storedConsent = safeStorageGet(CONSENT_KEY);
  if (storedConsent === "granted") {
    window.gtag("consent", "update", { analytics_storage: "granted" });
    loadGoogleTag();
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindInteractionTracking();
    if (isTrackablePage) addConsentBanner(false);
  });
})();
