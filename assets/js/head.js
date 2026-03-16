// Global Head Loader
// Google Analytics + basic conversion tracking
// Works for ALL pages and BOTH sites

(function () {

  const GA_ID = "G-1ZYLW22XWP";

  const gaScript = document.createElement("script");
  gaScript.async = true;
  gaScript.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
  document.head.appendChild(gaScript);

  const gaConfig = document.createElement("script");
  gaConfig.innerHTML = `
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', '${GA_ID}');
  `;
  document.head.appendChild(gaConfig);

  window.addEventListener("DOMContentLoaded", function () {

    function trackClick(selector, eventName) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.addEventListener("click", function () {
          if (typeof gtag === "function") {
            gtag("event", eventName, {
              page_location: window.location.href
            });
          }
        });
      });
    }

    trackClick(".btn-book", "book_tour_click");
    trackClick(".btn-tour", "view_tours_click");
    trackClick(".btn-contact", "contact_click");

    document.querySelectorAll("a[href*='mindobirdwatching.com']").forEach(function (link) {
      link.addEventListener("click", function () {
        if (typeof gtag === "function") {
          gtag("event", "funnel_to_mbw", {
            destination: link.href
          });
        }
      });
    });

  });

})();
