(function () {
  "use strict";

  if (window.ETA_SITE_CONFIG) return;

  window.ETA_SITE_CONFIG = Object.freeze({
    environment: "{{ETA_ENVIRONMENT}}",
    brand: Object.freeze({
      name: "Experience The Amazon",
      publicLine: "Experience the Amazon with confidence.",
      domain: "experiencetheamazon.com"
    }),
    contacts: Object.freeze({
      default: Object.freeze({
        whatsappE164: "+593969076501",
        whatsappDisplay: "+593 96 907 6501",
        email: "info@experiencetheamazon.com"
      }),
      ecuador: Object.freeze({
        whatsappE164: "+593969076501",
        whatsappDisplay: "+593 96 907 6501",
        email: "info@experiencetheamazon.com"
      })
    }),
    social: Object.freeze({
      instagram: "https://www.instagram.com/experienceamazon/"
    }),
    analytics: Object.freeze({
      gtmId: "GTM-NT8BL3HL",
      ga4Id: "G-TTSHGZCZZW",
      productionHosts: Object.freeze(["experiencetheamazon.com", "www.experiencetheamazon.com"])
    }),
    leads: Object.freeze({
      endpoint: "/api/contact",
      provider: "brevo",
      listName: "Experience The Amazon Leads"
    }),
    languages: Object.freeze({
      enabled: Object.freeze(["en", "es"]),
      planned: Object.freeze(["pt-BR"])
    }),
    features: Object.freeze({
      whatsapp: true,
      leadForms: true,
      bookingPayments: false,
      newsletter: false
    }),
    messages: Object.freeze({
      en: Object.freeze({
        default: "Hello! I would like help planning an Amazon trip.",
        ecuador: "Hello! I would like help planning a trip to the Ecuadorian Amazon."
      }),
      es: Object.freeze({
        default: "Hola. Quiero ayuda para planificar un viaje por la Amazonía.",
        ecuador: "Hola. Quiero ayuda para planificar un viaje a la Amazonía ecuatoriana."
      })
    })
  });
})();

