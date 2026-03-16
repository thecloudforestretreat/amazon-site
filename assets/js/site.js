(function () {
  "use strict";

  const LAT = -0.0516;
  const LON = -78.7764;

  const CACHE_KEY = "mindotours_wx_mindo_v1";
  const CACHE_TTL_MS = 60 * 60 * 1000;

  const elGrid = document.getElementById("wxGrid");
  const elNote = document.getElementById("wxNote");

  if (!elGrid) return;

  function cToF(c) {
    return (c * 9 / 5) + 32;
  }

  function round(n) {
    return Math.round(n);
  }

  function safeNum(n) {
    return (typeof n === "number" && isFinite(n)) ? n : null;
  }

  function fmtTempLine(c) {
    const cc = safeNum(c);
    if (cc === null) return "-- C / -- F";
    return round(cc) + " C / " + round(cToF(cc)) + " F";
  }

  function fmtMm(mm) {
    const v = safeNum(mm);
    if (v === null) return "--";
    if (v === 0) return "0";
    if (v < 1) return v.toFixed(1);
    return round(v).toString();
  }

  function dowShort(iso) {
    const d = new Date(iso + "T00:00:00");
    if (isNaN(d.getTime())) return "--";
    return d.toLocaleDateString("en-US", { weekday: "short" });
  }

  function iconFromCode(code, mm) {
    const c = safeNum(code);
    const r = safeNum(mm);

    if (r !== null && r >= 15) return "⛈️";
    if (r !== null && r >= 6) return "🌧️";
    if (r !== null && r > 0) return "🌦️";

    if (c === null) return "🌥️";
    if (c === 0) return "☀️";
    if (c === 1 || c === 2) return "🌤️";
    if (c === 3) return "☁️";
    if (c === 45 || c === 48) return "🌫️";
    if (c === 51 || c === 53 || c === 55) return "🌦️";
    if (c === 56 || c === 57) return "🌧️";
    if (c === 61 || c === 63 || c === 65) return "🌧️";
    if (c === 66 || c === 67) return "🌧️";
    if (c === 71 || c === 73 || c === 75) return "❄️";
    if (c === 77) return "❄️";
    if (c === 80 || c === 81 || c === 82) return "🌧️";
    if (c === 85 || c === 86) return "❄️";
    if (c === 95 || c === 96 || c === 99) return "⛈️";
    return "🌥️";
  }

  function setSkeleton(isOn) {
    const wx = document.querySelector(".wx");
    if (!wx) return;
    wx.classList.toggle("wxSkeleton", isOn);
  }

  function setNote(msg) {
    if (!elNote) return;
    elNote.hidden = !msg;
    elNote.textContent = msg || "";
  }

  function renderDaily(data) {
    try {
      const daily = data && data.daily ? data.daily : null;
      if (!daily) throw new Error("No daily data");

      const tmax = daily.temperature_2m_max || [];
      const tmin = daily.temperature_2m_min || [];
      const psum = daily.precipitation_sum || [];
      const time = daily.time || [];
      const wcode = daily.weathercode || daily.weather_code || [];

      if (!time.length || tmax.length < 7 || tmin.length < 7 || psum.length < 7) {
        throw new Error("Insufficient daily arrays");
      }

      let html = "";

      const todayMax = tmax[0];
      const todayMin = tmin[0];
      const todayRain = psum[0];
      const todayCode = wcode.length ? wcode[0] : null;
      const todayIcon = iconFromCode(todayCode, todayRain);

      html += ""
        + '<div class="wxDay wxNow">'
        +   '<div class="wxDayTop">'
        +     '<span class="wxPlace"><span class="wxPinDot" aria-hidden="true">📍</span>Mindo</span>'
        +     '<span class="wxIcon" aria-hidden="true">' + todayIcon + '</span>'
        +   '</div>'
        +   '<div class="wxTempsRow">'
        +     '<div class="wxTempsLines">'
        +       '<div class="wxLine">' + fmtTempLine(todayMax) + '</div>'
        +       '<div class="wxLine">' + fmtTempLine(todayMin) + '</div>'
        +     '</div>'
        +   '</div>'
        +   '<div class="wxRain"><span aria-hidden="true">💧</span><span>' + fmtMm(todayRain) + ' mm</span></div>'
        + '</div>';

      for (let i = 0; i < 7; i++) {
        const d = time[i];
        const maxC = tmax[i];
        const minC = tmin[i];
        const mm = psum[i];
        const code = wcode.length ? wcode[i] : null;
        const dayIcon = iconFromCode(code, mm);

        html += ""
          + '<div class="wxDay">'
          +   '<div class="wxDayTop">'
          +     '<span class="wxDow">' + dowShort(d) + '</span>'
          +     '<span class="wxIcon" aria-hidden="true">' + dayIcon + '</span>'
          +   '</div>'
          +   '<div class="wxTempsRow">'
          +     '<div class="wxTempsLines">'
          +       '<div class="wxLine">' + fmtTempLine(maxC) + '</div>'
          +       '<div class="wxLine">' + fmtTempLine(minC) + '</div>'
          +     '</div>'
          +   '</div>'
          +   '<div class="wxRain"><span aria-hidden="true">💧</span><span>' + fmtMm(mm) + ' mm</span></div>'
          + '</div>';
      }

      elGrid.innerHTML = html;
      setSkeleton(false);
      setNote("");
    } catch (e) {
      setSkeleton(false);
      setNote("");
    }
  }

  function readCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const obj = JSON.parse(raw);
      if (!obj || !obj.ts || !obj.data) return null;
      if ((Date.now() - obj.ts) > CACHE_TTL_MS) return null;
      return obj.data;
    } catch (e) {
      return null;
    }
  }

  function writeCache(data) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }));
    } catch (e) {}
  }

  function fetchWx() {
    const url =
      "https://api.open-meteo.com/v1/forecast"
      + "?latitude=" + encodeURIComponent(LAT)
      + "&longitude=" + encodeURIComponent(LON)
      + "&timezone=auto"
      + "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode";

    return fetch(url, { cache: "no-store" }).then((r) => {
      if (!r.ok) throw new Error("Bad response");
      return r.json();
    });
  }

  setSkeleton(true);

  const cached = readCache();
  if (cached) {
    renderDaily(cached);
    fetchWx().then((data) => {
      writeCache(data);
      renderDaily(data);
    }).catch(() => {});
  } else {
    fetchWx().then((data) => {
      writeCache(data);
      renderDaily(data);
    }).catch(() => {
      setSkeleton(false);
      setNote("");
    });
  }
})();
