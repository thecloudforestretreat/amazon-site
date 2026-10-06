(function () {
  "use strict";

  const config = window.ETA_SITE_CONFIG;
  if (!config) return;

  const consentKey = "eta_analytics_consent_v1";
  const attributionKey = "eta_first_touch_v1";
  const productionHosts = new Set(config.analytics.productionHosts || []);
  const isProduction = config.environment === "production" && productionHosts.has(window.location.hostname);
  const isSpanish = (document.documentElement.lang || "en").toLowerCase().startsWith("es");

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    wait_for_update: 500
  });
  window.gtag("set", "ads_data_redaction", true);

  function storageGet(key) {
    try { return window.localStorage.getItem(key); } catch (_) { return null; }
  }

  function storageSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (_) {}
  }

  function context() {
    const data = document.documentElement.dataset;
    return {
      page_id: data.pageId || "unknown",
      pair_id: data.pairId || "unknown",
      language: document.documentElement.lang || "en",
      page_type: data.pageType || "unknown",
      country: data.country || "",
      topic_cluster: data.topicCluster || "",
      funnel_stage: data.funnelStage || "awareness"
    };
  }

  let gtmLoaded = false;
  function loadGtm() {
    if (!isProduction || gtmLoaded) return;
    gtmLoaded = true;
    window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(config.analytics.gtmId);
    document.head.appendChild(script);
  }

  function sendPageView() {
    if (!isProduction) return;
    window.gtag("event", "page_view", Object.assign(context(), {
      page_title: document.title,
      page_location: window.location.origin + window.location.pathname,
      page_referrer: document.referrer ? new URL(document.referrer).origin : ""
    }));
  }

  function track(name, values) {
    if (!isProduction || storageGet(consentKey) !== "granted") return;
    const parameters = Object.assign(context(), values || {});
    delete parameters.email;
    delete parameters.phone;
    delete parameters.name;
    delete parameters.message;
    window.gtag("event", name, parameters);
  }

  function setConsent(value) {
    const granted = value === "granted";
    storageSet(consentKey, granted ? "granted" : "denied");
    window.gtag("consent", "update", { analytics_storage: granted ? "granted" : "denied" });
    if (granted) { captureAttribution(); loadGtm(); sendPageView(); }
    document.getElementById("eta-consent")?.remove();
  }

  function showConsent(force) {
    if (!force && storageGet(consentKey)) return;
    document.getElementById("eta-consent")?.remove();
    const banner = document.createElement("section");
    banner.id = "eta-consent";
    banner.className = "eta-consent";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-label", isSpanish ? "Preferencias de privacidad" : "Privacy choices");
    banner.innerHTML = isSpanish
      ? "<strong>Tu privacidad importa</strong><p>Usamos analítica opcional para mejorar la planificación de viajes. No enviamos el contenido de formularios a Google Analytics. <a href='/es/politica-de-privacidad/'>Política de privacidad</a>.</p><div><button type='button' data-consent='granted'>Permitir analítica</button><button type='button' data-consent='denied'>Rechazar</button></div>"
      : "<strong>Your privacy matters</strong><p>We use optional analytics to improve trip planning. We do not send form contents to Google Analytics. <a href='/privacy-policy/'>Privacy policy</a>.</p><div><button type='button' data-consent='granted'>Allow analytics</button><button type='button' data-consent='denied'>Reject</button></div>";
    banner.addEventListener("click", function (event) {
      const button = event.target.closest("[data-consent]");
      if (button) setConsent(button.dataset.consent);
    });
    document.body.appendChild(banner);
  }

  function captureAttribution() {
    if (storageGet(attributionKey)) return;
    const query = new URLSearchParams(window.location.search);
    const record = {
      source: query.get("utm_source") || "",
      medium: query.get("utm_medium") || "",
      campaign: query.get("utm_campaign") || "",
      landing_page: window.location.pathname,
      captured_at: new Date().toISOString()
    };
    if (record.source || record.medium || record.campaign) storageSet(attributionKey, JSON.stringify(record));
  }

  document.addEventListener("click", function (event) {
    const element = event.target.closest("a,button");
    if (!element) return;
    const href = element.getAttribute("href") || "";
    const common = {
      cta_id: element.dataset.ctaId || "",
      cta_position: element.dataset.ctaPosition || "",
      link_text: (element.dataset.analyticsLabel || element.textContent || "").trim().slice(0, 80)
    };
    if (element.dataset.analyticsEvent) return track(element.dataset.analyticsEvent, common);
    if (/wa\.me/i.test(href)) return track("click_whatsapp", common);
    if (/^mailto:/i.test(href)) return track("click_email", common);
  }, true);

  window.etaAnalytics = {
    track,
    openPrivacyChoices: function () { showConsent(true); },
    firstTouch: function () {
      try { return JSON.parse(storageGet(attributionKey) || "null"); } catch (_) { return null; }
    }
  };

  if (storageGet(consentKey) === "granted") {
    captureAttribution();
    loadGtm();
    window.gtag("consent", "update", { analytics_storage: "granted" });
    sendPageView();
  }
  document.addEventListener("DOMContentLoaded", function () { showConsent(false); });
})();
