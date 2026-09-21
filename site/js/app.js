/* =====================================================================
   CORE CULTURE — site behaviour
   Sections: helpers · notice · nav · hero torch · carousel · plan ·
   room panel · equipment + directory · flap board · timetable ·
   memberships · trial form · contact · hash router
   All content comes from window.CC (js/data.js).
   ===================================================================== */
(function () {
  "use strict";
  const CC = window.CC;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches
    || new URLSearchParams(location.search).has("rm"); /* rm=1 → preview the reduced-motion experience */

  /* ---------- helpers ---------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const DAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
  const DAY_LABEL = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };
  const roomById = id => CC.rooms.find(r => r.id === id);
  const catOf = id => CC.categories[id] || CC.categories.community;

  function el(tag, cls, html) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) { const d = el("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }
  const pad = n => String(n).padStart(2, "0");
  function toMin(t) { const [h, m] = t.split(":").map(Number); return h * 60 + m; }

  function nextDateFor(day, time, from) {
    const d = new Date(from);
    d.setHours(toMin(time) >= 24 * 60 ? 23 : Math.floor(toMin(time) / 60), toMin(time) % 60, 0, 0);
    let diff = (DAYS.indexOf(day) - d.getDay() + 7) % 7;
    if (diff === 0 && d < from) diff = 7;
    d.setDate(d.getDate() + diff);
    return d;
  }
  function fmtDay(d) {
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const that = new Date(d); that.setHours(0, 0, 0, 0);
    const diff = Math.round((that - today) / 86400000);
    if (diff === 0) return "Today";
    if (diff === 1) return "Tomorrow";
    return DAY_LABEL[DAYS[that.getDay()]].slice(0, 3) + " " + that.getDate() + "/" + (that.getMonth() + 1);
  }

  /* One shared "what's on" occurrence list for board, timetable links, rooms */
  function occurrences(limit) {
    const now = new Date();
    const list = [];
    CC.batches.forEach(b => b.days.forEach(day => {
      list.push({ kind: "batch", ref: b, day, date: nextDateFor(day, b.time, now) });
    }));
    CC.events.forEach(e => {
      const d = new Date(e.date + "T" + e.time + ":00");
      if (d >= now) list.push({ kind: "event", ref: e, day: e.day, date: d });
    });
    list.sort((a, b) => a.date - b.date);
    return limit ? list.slice(0, limit) : list;
  }

  /* focus trap */
  function trap(container, onClose) {
    const sel = 'a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])';
    function key(e) {
      if (e.key === "Escape") { e.preventDefault(); onClose(); return; }
      if (e.key !== "Tab") return;
      const items = $$(sel, container).filter(n => n.offsetParent !== null || n === document.activeElement);
      if (!items.length) return;
      const first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    container.addEventListener("keydown", key);
    return () => container.removeEventListener("keydown", key);
  }

  /* =====================================================
     NOTICE
  ===================================================== */
  const notice = $("#notice");
  try {
    if (sessionStorage.getItem("cc-notice") !== "1") notice.hidden = false;
  } catch (e) { notice.hidden = false; }
  $("#noticeClose").addEventListener("click", () => {
    notice.hidden = true;
    try { sessionStorage.setItem("cc-notice", "1"); } catch (e) {}
  });

  /* =====================================================
     NAV
  ===================================================== */
  const nav = $("#siteNav");
  const menuBtn = $("#menuBtn");
  const mobileMenu = $("#mobileMenu");
  let menuOpen = false, menuUntrap = null, menuReturnFocus = null;

  function setMenu(open) {
    menuOpen = open;
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    mobileMenu.hidden = !open;
    document.documentElement.style.overflow = open ? "hidden" : "";
    if (open) {
      menuReturnFocus = document.activeElement;
      const first = $("a", mobileMenu); if (first) first.focus();
      menuUntrap = trap(mobileMenu, () => setMenu(false));
    } else {
      if (menuUntrap) { menuUntrap(); menuUntrap = null; }
      if (menuReturnFocus) menuReturnFocus.focus();
    }
  }
  menuBtn.addEventListener("click", () => setMenu(!menuOpen));
  $$("a", mobileMenu).forEach(a => a.addEventListener("click", () => setMenu(false)));

  /* active section highlight */
  const navMap = { amenities: 0, plan: 1, equipment: 2, schedule: 3, memberships: 4, contact: 5 };
  const navLinks = $$(".nav-links a");
  const secObserver = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const idx = navMap[en.target.id];
      if (idx == null) return;
      navLinks.forEach((a, i) => a.classList.toggle("active", i === idx));
    });
  }, { rootMargin: "-40% 0px -55% 0px" });
  Object.keys(navMap).forEach(id => { const s = document.getElementById(id); if (s) secObserver.observe(s); });

  /* =====================================================
     HERO — concept 24 torch
  ===================================================== */
  const hero = $("#top");
  const torch = $("#torch");
  const lightsBtn = $("#lightsBtn");
  const lightsState = $("#lightsState");
  const heroHint = $("#heroHint");
  const heroImg = $("#heroImg");
  let lit = reduced; // reduced motion → fully lit from the start

  heroImg.src = CC.profile.hero.src;
  heroImg.alt = CC.profile.hero.alt;

  function setLit(v) {
    lit = v;
    hero.classList.toggle("lit", v);
    lightsBtn.setAttribute("aria-pressed", String(v));
    lightsState.textContent = v ? "power restored — full floor visible" : "the floor, before the lights";
    heroHint.textContent = v ? "" : "Move to explore · flip the lights when ready";
  }
  setLit(lit);
  lightsBtn.addEventListener("click", () => setLit(!lit));
  document.addEventListener("keydown", e => {
    if (e.key.toLowerCase() === "l" && !e.metaKey && !e.ctrlKey && !e.altKey &&
        !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) setLit(!lit);
  });

  if (!reduced) {
    let raf = null, tx = "50%", ty = "44%";
    function apply() {
      raf = null;
      torch.style.setProperty("--mx", tx);
      torch.style.setProperty("--my", ty);
    }
    function move(x, y) {
      const r = hero.getBoundingClientRect();
      tx = ((x - r.left) / r.width * 100).toFixed(2) + "%";
      ty = ((y - r.top) / r.height * 100).toFixed(2) + "%";
      if (!raf && !lit) raf = requestAnimationFrame(apply);
    }
    hero.addEventListener("pointermove", e => move(e.clientX, e.clientY), { passive: true });
    hero.addEventListener("pointerdown", e => move(e.clientX, e.clientY), { passive: true });
    apply();
  } else {
    torch.style.display = "none";
  }

  /* hero meta */
  $("#heroHours").textContent = "Hours — sample 05:30–23:00 · to confirm";
  $("#heroRooms").textContent = CC.rooms.length + " zones · one floor";

  /* =====================================================
     MARQUEE — concept 11 energy
  ===================================================== */
  const mUnit = "<span>Train <em>★</em> Move <em>★</em> Recover <em>★</em> Connect <em>★</em> This is your Training Ground <em>★</em>&nbsp;</span>";
  $("#marqueeTrack").innerHTML = mUnit + mUnit;

  /* =====================================================
     AMENITIES CAROUSEL — concept 07
  ===================================================== */
  const track = $("#carTrack");
  const carChips = $("#carChips");
  const carBar = $("#carBar");
  const walkOrder = ["lobby", "strength", "hybrid", "cardio", "studio", "recovery", "lounge", "arrival"]
    .map(roomById).filter(Boolean);

  walkOrder.forEach(room => {
    const cat = catOf(room.category);
    const panel = el("article", "car-panel cat-" + room.category);
    panel.id = "car-" + room.id;
    panel.setAttribute("aria-label", room.name);
    panel.innerHTML =
      '<div class="car-copy">' +
        '<div class="car-num" aria-hidden="true">' + room.num + '</div>' +
        '<p class="car-kicker"><span class="cat-dot" aria-hidden="true"></span>' + esc(cat.label) + '</p>' +
        '<h3 class="car-name">' + esc(room.name) + '</h3>' +
        '<p class="car-line">' + esc(room.tagline) + ' ' + esc(room.intro.split(". ")[0]) + '.</p>' +
        '<div class="car-chips">' + room.amenities.slice(0, 4).map(a => "<span>" + esc(a) + "</span>").join("") + "</div>" +
        '<button class="car-open" data-room="' + room.id + '">Explore this space →</button>' +
      '</div>' +
      '<div class="car-photo">' +
        '<img src="' + room.photo.src + '" alt="' + esc(room.photo.alt) + '" loading="lazy">' +
        '<span class="car-tag">Art direction — not a verified photo</span>' +
      "</div>";
    track.appendChild(panel);

    const chip = el("button", "", esc(room.num + " · " + room.name));
    chip.dataset.room = room.id;
    chip.addEventListener("click", () => goToPanel(room.id));
    carChips.appendChild(chip);
  });

  function panelIndex(id) { return walkOrder.findIndex(r => r.id === id); }
  function goToPanel(id) {
    const p = document.getElementById("car-" + id);
    if (!p) return;
    track.scrollTo({ left: p.offsetLeft - track.offsetLeft, behavior: reduced ? "auto" : "smooth" });
  }
  function currentPanelId() {
    const max = track.scrollWidth - track.clientWidth;
    if (max <= 0) return walkOrder[0].id;
    const i = Math.min(walkOrder.length - 1, Math.round(track.scrollLeft / max * (walkOrder.length - 1)));
    return walkOrder[i].id;
  }
  function syncCarousel() {
    const id = currentPanelId();
    const max = track.scrollWidth - track.clientWidth;
    const p = max > 0 ? track.scrollLeft / max : 0;
    carBar.style.left = (p * 88) + "%";
    $$("button", carChips).forEach(c => c.setAttribute("aria-current", String(c.dataset.room === id)));
    $("#carPrev").disabled = track.scrollLeft <= 2;
    $("#carNext").disabled = track.scrollLeft >= max - 2;
  }
  track.addEventListener("scroll", syncCarousel, { passive: true });
  addEventListener("resize", syncCarousel);
  $("#carPrev").addEventListener("click", () => goToPanel(walkOrder[Math.max(0, panelIndex(currentPanelId()) - 1)].id));
  $("#carNext").addEventListener("click", () => goToPanel(walkOrder[Math.min(walkOrder.length - 1, panelIndex(currentPanelId()) + 1)].id));
  syncCarousel();

  /* =====================================================
     FLOOR PLAN — concept 19
  ===================================================== */
  const planSvg = $("#planSvg");
  const SVG = "http://www.w3.org/2000/svg";
  function sv(tag, attrs, parent) {
    const n = document.createElementNS(SVG, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  /* walls */
  sv("rect", { class: "wall", x: 30, y: 20, width: 940, height: 500 }, planSvg);
  const walls = [
    { x1: 370, y1: 40, x2: 370, y2: 340 }, { x1: 640, y1: 40, x2: 640, y2: 340 },
    { x1: 660, y1: 185, x2: 960, y2: 185 }, { x1: 40, y1: 340, x2: 960, y2: 340 },
    { x1: 240, y1: 360, x2: 240, y2: 520 }, { x1: 570, y1: 360, x2: 570, y2: 520 }
  ];
  walls.forEach(w => sv("line", { class: "thin", x1: w.x1, y1: w.y1, x2: w.x2, y2: w.y2 }, planSvg));

  /* parking strip */
  const park = sv("g", { class: "zone parking-zone cat-community", "data-room": "arrival", role: "button", tabindex: "0", "aria-label": "Arrival and member parking — open details", "aria-haspopup": "dialog" }, planSvg);
  sv("rect", { class: "zshape", x: 30, y: 548, width: 940, height: 66 }, park);
  const pkt1 = sv("text", { class: "zlabel", x: 60, y: 588 }, park); pkt1.textContent = "P · ARRIVAL & MEMBER PARKING";
  const pkt2 = sv("text", { class: "zsub", x: 60, y: 604 }, park); pkt2.textContent = "spaces & terms TBC — brand promise: plenty";

  /* zones */
  CC.rooms.forEach(room => {
    const z = room.plan;
    if (!z || z.strip) return;
    const g = sv("g", { class: "zone cat-" + room.category, "data-room": room.id, role: "button", tabindex: "0", "aria-label": room.name + " — open room details", "aria-haspopup": "dialog" }, planSvg);
    sv("rect", { class: "zshape", x: z.x, y: z.y, width: z.w, height: z.h }, g);
    const t = sv("text", { class: "zlabel", x: z.x + 14, y: z.y + 26 }, g);
    t.textContent = z.letter + " · " + room.name.toUpperCase();
    const s = sv("text", { class: "zsub", x: z.x + 14, y: z.y + 44 }, g);
    s.textContent = room.amenities.slice(0, 2).join(" · ").toUpperCase();
    sv("circle", { class: "zdot", cx: z.x + z.w - 22, cy: z.y + 22, r: 6 }, g);
  });

  /* entrance + dims */
  const ent = sv("text", { class: "entrance", x: 60, y: 536 }, planSvg); ent.textContent = "↑ ENTRANCE — LOBBY & DESK";
  sv("line", { class: "dim", x1: 30, y1: 8, x2: 970, y2: 8 }, planSvg);
  const dimT = sv("text", { class: "dimt", x: 470, y: 16 }, planSvg); dimT.textContent = "OVERALL FOOTPRINT — ILLUSTRATIVE SCALE, SURVEY TBC";

  const roomList = $("#roomList");
  CC.rooms.forEach(room => {
    const cat = catOf(room.category);
    const key = el("button", "room-key cat-" + room.category);
    key.setAttribute("role", "listitem");
    key.dataset.room = room.id;
    key.innerHTML =
      '<span class="kb" aria-hidden="true">' + room.plan.letter + "</span>" +
      '<span class="kn">' + esc(room.name) + "</span>" +
      '<span class="ks">' + esc(cat.label) + "</span>" +
      '<span class="kd">' + esc(room.tagline) + "</span>";
    key.addEventListener("click", () => openRoom(room.id, key));
    key.addEventListener("mouseenter", () => highlightZone(room.id, true));
    key.addEventListener("focus", () => highlightZone(room.id, true));
    key.addEventListener("mouseleave", () => highlightZone(room.id, false));
    key.addEventListener("blur", () => highlightZone(room.id, false));
    roomList.appendChild(key);
  });

  function highlightZone(id, on) {
    const z = $('.zone[data-room="' + id + '"]', planSvg);
    if (z) z.classList.toggle("hl", on);
    const k = $('.room-key[data-room="' + id + '"]');
    if (k) k.style.background = on ? "rgba(243,240,231,.07)" : "";
  }
  function markSelected(id) {
    $$(".zone", planSvg).forEach(z => z.classList.toggle("sel", z.dataset.room === id));
  }
  $$(".zone", planSvg).forEach(z => {
    const id = z.dataset.room;
    z.addEventListener("click", () => openRoom(id, z));
    z.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openRoom(id, z); }
    });
    z.addEventListener("mouseenter", () => highlightZone(id, true));
    z.addEventListener("mouseleave", () => highlightZone(id, false));
    z.addEventListener("focus", () => highlightZone(id, true));
    z.addEventListener("blur", () => highlightZone(id, false));
  });

  /* =====================================================
     ROOM DETAIL PANEL (shared)
  ===================================================== */
  const scrim = $("#scrim");
  const panel = $("#roomPanel");
  const panelBody = $("#rpBody");
  const rpClose = $("#rpClose");
  let panelUntrap = null, panelTrigger = null, lastRoom = null;
  let galleryImages = [], galleryIndex = 0;

  function accessLine(room) {
    if (room.access === "included") return "<b>Included with membership</b> — " + esc(room.accessNote);
    if (room.access === "bookable") return "<b>Bookable</b> — slots may be reserved or charged separately. " + esc(room.accessNote);
    return "<b>To be confirmed</b> — " + esc(room.accessNote);
  }

  function sessionsFor(roomId, limit) {
    const now = new Date();
    const rows = [];
    CC.batches.filter(b => b.roomId === roomId).forEach(b =>
      b.days.forEach(day => rows.push({ kind: "batch", ref: b, date: nextDateFor(day, b.time, now) })));
    CC.events.filter(e => e.roomId === roomId).forEach(e => {
      const d = new Date(e.date + "T" + e.time + ":00");
      if (d >= now) rows.push({ kind: "event", ref: e, date: d });
    });
    rows.sort((a, b) => a.date - b.date);
    return rows.slice(0, limit || 4);
  }

  function renderRoom(room) {
    lastRoom = room;
    markSelected(room.id);
    panelBody.className = "panel-body cat-" + room.category;
    const cat = catOf(room.category);
    galleryImages = room.gallery;
    galleryIndex = 0;

    panelBody.innerHTML =
      '<p class="rp-kicker"><span class="cat-dot" aria-hidden="true"></span>' + esc(cat.label) + " · Room " + esc(room.num) + "</p>" +
      '<h2 class="rp-name" id="rpName"><span class="rp-num" aria-hidden="true">' + esc(room.num) + "</span>" + esc(room.name) + "</h2>" +
      '<p class="rp-intro">' + esc(room.intro) + "</p>" +

      '<div class="rp-gallery">' +
        '<div class="rp-main">' +
          '<img id="rpImg" src="' + esc(room.gallery[0].src) + '" alt="' + esc(room.gallery[0].alt) + '">' +
          '<button class="rp-nav rp-prev" id="rpPrev" aria-label="Previous photo">←</button>' +
          '<button class="rp-nav rp-next" id="rpNext" aria-label="Next photo">→</button>' +
          '<button class="lb-open" id="rpLb">Enlarge ⤢</button>' +
        "</div>" +
        '<p class="rp-caption" id="rpCap">' + esc(room.gallery[0].caption) + ' · <span class="sample-chip">art direction</span></p>' +
        '<div class="rp-thumbs" id="rpThumbs">' +
          room.gallery.map((g, i) =>
            '<button class="rp-thumb" data-i="' + i + '" aria-label="Photo ' + (i + 1) + ": " + esc(g.caption) + '"' + (i === 0 ? ' aria-current="true"' : "") + '><img src="' + esc(g.src) + '" alt=""></button>').join("") +
        "</div>" +
      "</div>" +

      '<div class="rp-sec"><h4>Facilities &amp; specifications</h4>' +
        '<dl class="rp-specs">' +
          room.facilities.map(f => "<div><dt>" + esc(f[0]) + "</dt><dd>" + esc(f[1]) + "</dd></div>").join("") +
        "</dl>" +
        '<p class="rp-access">' + accessLine(room) + "</p>" +
      "</div>" +

      (room.equipment.length ?
        '<div class="rp-sec"><h4>Equipment in this zone</h4><div class="rp-chips">' +
          room.equipment.map(eqId => {
            const eq = CC.equipment.find(x => x.id === eqId);
            return eq ? '<button data-eq="' + eq.id + '">' + esc(eq.name) + "</button>" : "";
          }).join("") +
        "</div></div>" : "") +

      '<div class="rp-sec"><h4>On the timetable here</h4><div class="rp-sess">' +
        (() => {
          const rows = sessionsFor(room.id, 4);
          if (!rows.length) return '<div class="srow"><span class="sday">Nothing scheduled here yet — sessions to be confirmed.</span></div>';
          return rows.map(r =>
            '<div class="srow">' +
              '<span><span class="stime">' + esc(r.ref.time) + '</span><span class="sday">' + esc(fmtDay(r.date)) + "</span></span>" +
              "<span>" + esc(r.ref.name) + (r.kind === "event" ? '<span class="tt-event-tag">Event</span>' : "") + "</span>" +
              '<button class="sbook" data-session="' + esc(r.ref.id) + '" data-kind="' + r.kind + '">Book</button>' +
            "</div>").join("");
        })() +
      '</div><p style="margin-top:10px"><a href="#schedule" style="color:var(--w-dim);font-size:12.5px">See the full timetable →</a></p></div>' +

      '<div class="rp-ctas">' +
        '<button class="btn btn-accent" data-book-context="' + esc(room.name) + '">Book a trial' + (room.id !== "lobby" ? " — see this space" : "") + "</button>" +
        '<a class="btn btn-ghost" href="#contact">Enquire about this space</a>' +
      "</div>";

    /* gallery behaviour */
    function showGallery(i) {
      galleryIndex = (i + galleryImages.length) % galleryImages.length;
      const g = galleryImages[galleryIndex];
      const img = $("#rpImg", panelBody);
      img.style.opacity = "0";
      setTimeout(() => { img.src = g.src; img.alt = g.alt; img.style.opacity = "1"; }, reduced ? 0 : 120);
      $("#rpCap", panelBody).innerHTML = esc(g.caption) + ' · <span class="sample-chip">art direction</span>';
      $$(".rp-thumb", panelBody).forEach((t, ti) => t.setAttribute("aria-current", String(ti === galleryIndex)));
    }
    $("#rpImg", panelBody).style.transition = "opacity .18s ease";
    $("#rpPrev", panelBody).addEventListener("click", () => showGallery(galleryIndex - 1));
    $("#rpNext", panelBody).addEventListener("click", () => showGallery(galleryIndex + 1));
    $("#rpLb", panelBody).addEventListener("click", () => openLightbox(galleryImages, galleryIndex));
    $$(".rp-thumb", panelBody).forEach(t => t.addEventListener("click", () => showGallery(+t.dataset.i)));

    /* equipment chips → directory filtered to this room */
    $$("[data-eq]", panelBody).forEach(b => b.addEventListener("click", () => {
      closeRoomUI();
      openDirectory({ zone: room.id });
    }));

    /* book with context */
    $$("[data-book-context]", panelBody).forEach(b => b.addEventListener("click", () => {
      setBookContext({ label: room.name, kind: "Room" });
      closeRoomUI();
      goToBook(b);
    }));
    $$(".sbook", panelBody).forEach(b => b.addEventListener("click", () => {
      const kind = b.dataset.kind;
      const occ = kind === "event" ? CC.events.find(x => x.id === b.dataset.session) : CC.batches.find(x => x.id === b.dataset.session);
      setBookContext({ label: occ.name, kind: kind === "event" ? "Event" : "Batch" });
      closeRoomUI();
      goToBook(b);
    }));
    $$('a[href="#schedule"]', panelBody).forEach(a => a.addEventListener("click", () => closeRoomUI()));
    $$('a[href="#contact"]', panelBody).forEach(a => a.addEventListener("click", () => closeRoomUI()));

    panel.scrollTop = 0;
    rpClose.focus({ preventScroll: true });
  }

  function showRoomUI() {
    scrim.hidden = false; panel.hidden = false;
    document.documentElement.style.overflow = "hidden";
    requestAnimationFrame(() => panel.classList.add("open"));
    panelUntrap = trap(panel, () => closeView("room"));
  }
  function closeRoomUI() {
    if (panel.hidden) return;
    panel.classList.remove("open");
    panelUntrap && panelUntrap(); panelUntrap = null;
    document.documentElement.style.overflow = menuOpen ? "hidden" : "";
    const finish = () => {
      scrim.hidden = true; panel.hidden = true;
      if (panelTrigger && document.contains(panelTrigger)) panelTrigger.focus({ preventScroll: true });
      panelTrigger = null;
    };
    reduced ? finish() : setTimeout(finish, 320);
  }
  function openRoom(id, trigger) {
    const room = roomById(id);
    if (!room) return;
    panelTrigger = trigger || document.activeElement;
    hideDirectoryUI();
    renderRoom(room);
    showRoomUI();
    pushView("room", id);
  }

  /* =====================================================
     EQUIPMENT — preview + directory
  ===================================================== */
  const photoFirst = [...CC.equipment].sort((a, b) => (b.photo ? 1 : 0) - (a.photo ? 1 : 0));
  const previewItems = photoFirst.slice(0, 6);

  function eqCard(eq, context) {
    const room = roomById(eq.roomId);
    const cat = catOf(eq.category);
    const card = el("article", "eq-card cat-" + eq.category);
    card.innerHTML =
      '<div class="eq-photo">' +
        (eq.photo
          ? '<img src="' + esc(eq.photo.src) + '" alt="' + esc(eq.photo.alt) + '" loading="lazy">'
          : '<span class="eq-mono" aria-hidden="true">' + esc(eq.name.charAt(0)) + "</span>") +
        '<span class="eq-cat">' + esc(cat.label) + "</span>" +
      "</div>" +
      '<div class="eq-body">' +
        '<h3 class="eq-name">' + esc(eq.name) + "</h3>" +
        '<p class="eq-purpose">' + esc(eq.purpose) + "</p>" +
        (context === "directory"
          ? '<dl class="eq-detail" hidden>' +
              eq.specs.map(s => "<dt>" + esc(s[0]) + "</dt><dd>" + esc(s[1]) + "</dd>").join("") +
              '<dt>Brand / model</dt><dd>' + esc(eq.brand) + "</dd>" +
              '<dt>Zone</dt><dd>' + esc(room.name) + "</dd>" +
            "</dl>" +
            (eq.specs.length || eq.brand !== "TBC"
              ? '<button class="eq-specs-btn" aria-expanded="false">Specs &amp; details ▾</button>'
              : "") +
            '<div class="eq-actions">' +
              '<button class="mini" data-find="' + eq.roomId + '">Find on layout</button>' +
              '<button class="mini" data-openroom="' + eq.roomId + '">Open room</button>' +
            "</div>"
          : '<p class="eq-meta"><span>' + esc(room.name) + '</span><span class="find">In directory →</span></p>') +
      "</div>";
    return card;
  }

  const equipPreview = $("#equipPreview");
  previewItems.forEach(eq => {
    const card = eqCard(eq, "preview");
    card.addEventListener("click", () => openDirectory({ search: eq.name }));
    equipPreview.appendChild(card);
  });

  /* directory overlay */
  const directory = $("#directory");
  const dirGrid = $("#dirGrid");
  const dirSearch = $("#dirSearch");
  const dirZone = $("#dirZone");
  const dirCats = $("#dirCats");
  const dirCount = $("#dirCount");
  let dirUntrap = null, dirTrigger = null, dirState = { search: "", cat: "all", zone: "all" };

  CC.rooms.forEach(r => {
    const o = el("option"); o.value = r.id; o.textContent = r.plan.letter + " · " + r.name;
    dirZone.appendChild(o);
  });
  const dirCatBtns = [];
  [["all", "Everything"]].concat(Object.entries(CC.categories).map(([k, v]) => [k, v.label])).forEach(([k, label]) => {
    const b = el("button", "chip", esc(label));
    b.dataset.cat = k;
    b.setAttribute("aria-pressed", String(k === "all"));
    b.addEventListener("click", () => {
      dirState.cat = k;
      dirCatBtns.forEach(x => x.setAttribute("aria-pressed", String(x.dataset.cat === k)));
      renderDirectory();
    });
    dirCatBtns.push(b); dirCats.appendChild(b);
  });

  function renderDirectory() {
    const q = dirState.search.trim().toLowerCase();
    const items = CC.equipment.filter(eq => {
      const room = roomById(eq.roomId);
      const okCat = dirState.cat === "all" || eq.category === dirState.cat;
      const okZone = dirState.zone === "all" || eq.roomId === dirState.zone;
      const hay = (eq.name + " " + eq.purpose + " " + room.name + " " + catOf(eq.category).label).toLowerCase();
      return okCat && okZone && (!q || hay.includes(q));
    });
    dirGrid.innerHTML = "";
    dirCount.textContent = items.length + " of " + CC.equipment.length + " items" +
      (q ? " · search “" + dirState.search.trim() + "”" : "");
    if (!items.length) {
      dirGrid.appendChild(el("p", "dir-empty", "Nothing matches. Clear the search or pick another zone."));
      return;
    }
    items.forEach(eq => {
      const card = eqCard(eq, "directory");
      const specBtn = $(".eq-specs-btn", card);
      if (specBtn) specBtn.addEventListener("click", () => {
        const d = $(".eq-detail", card);
        const open = d.hidden;
        d.hidden = !open;
        specBtn.setAttribute("aria-expanded", String(open));
        specBtn.textContent = open ? "Specs & details ▴" : "Specs & details ▾";
      });
      $("[data-find]", card).addEventListener("click", () => findOnLayout(eq.roomId));
      $("[data-openroom]", card).addEventListener("click", () => openRoom(eq.roomId));
      dirGrid.appendChild(card);
    });
  }
  dirSearch.addEventListener("input", () => { dirState.search = dirSearch.value; renderDirectory(); });
  dirZone.addEventListener("change", () => { dirState.zone = dirZone.value; renderDirectory(); });

  function showDirectoryUI() {
    directory.hidden = false;
    document.documentElement.style.overflow = "hidden";
    if (!reduced) { directory.style.opacity = "0"; directory.style.transition = "opacity .25s ease"; requestAnimationFrame(() => { directory.style.opacity = "1"; }); }
    dirUntrap = trap(directory, () => closeView("directory"));
    dirCloseBtn.focus({ preventScroll: true });
  }
  function closeDirectoryUI() {
    if (directory.hidden) return;
    dirUntrap && dirUntrap(); dirUntrap = null;
    directory.hidden = true;
    document.documentElement.style.overflow = panel.hidden ? "" : "hidden";
    if (dirTrigger) { dirTrigger.focus({ preventScroll: true }); dirTrigger = null; }
  }
  const dirCloseBtn = $("#dirClose");
  dirCloseBtn.addEventListener("click", () => closeView("directory"));
  function openDirectory(preset) {
    if (panel.hidden === false) closeRoomUI();
    dirTrigger = document.activeElement;
    if (preset) {
      if (preset.zone) { dirState.zone = preset.zone; dirZone.value = preset.zone; }
      if (preset.search != null) { dirState.search = preset.search; dirSearch.value = preset.search; }
    }
    renderDirectory();
    showDirectoryUI();
    directory.scrollTop = 0;
    pushView("directory");
  }
  $("#openDirectory").addEventListener("click", () => openDirectory());

  function findOnLayout(roomId) {
    closeDirectoryUI();
    if (history.state && history.state.ccView === "directory") history.back();
    const plan = $("#plan");
    plan.scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
    markSelected(roomId);
    const z = $('.zone[data-room="' + roomId + '"]', planSvg);
    if (z) {
      z.classList.add("hl");
      setTimeout(() => z.classList.remove("hl"), 2600);
      const name = roomById(roomId).name;
      dirCount.textContent = "On the plan: " + name + " — highlighted for a moment. Click it to open the room.";
      dirCount.classList.add("ok");
    }
  }

  /* =====================================================
     LIGHTBOX
  ===================================================== */
  const lightbox = $("#lightbox");
  const lbImg = $("#lbImg");
  const lbCap = $("#lbCap");
  let lbImages = [], lbIndex = 0, lbUntrap = null, lbReturn = null;
  function showLb(i) {
    lbIndex = (i + lbImages.length) % lbImages.length;
    const g = lbImages[lbIndex];
    lbImg.src = g.src; lbImg.alt = g.alt;
    lbCap.textContent = g.caption + " — art direction";
  }
  function openLightbox(images, index) {
    lbImages = images; lbReturn = document.activeElement;
    showLb(index);
    lightbox.hidden = false;
    document.documentElement.style.overflow = "hidden";
    lbUntrap = trap(lightbox, closeLightbox);
    $("#lbClose").focus();
  }
  function closeLightbox() {
    lbUntrap && lbUntrap(); lbUntrap = null;
    lightbox.hidden = true;
    document.documentElement.style.overflow = panel.hidden ? "" : "hidden";
    if (lbReturn) lbReturn.focus({ preventScroll: true });
  }
  $("#lbClose").addEventListener("click", closeLightbox);
  $("#lbPrev").addEventListener("click", () => showLb(lbIndex - 1));
  $("#lbNext").addEventListener("click", () => showLb(lbIndex + 1));

  /* =====================================================
     SPLIT-FLAP BOARD — concept 20
  ===================================================== */
  const flapBoard = $("#flapBoard");
  const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:·-& ";
  let flapRows = [], flapSignature = "";

  function flapRow(occ) {
    const room = roomById(occ.ref.roomId);
    const row = el("div", "frow");
    const time = el("div", "ftime", esc(occ.ref.time));
    const line = el("div", "flapline");
    const name = occ.ref.name.toUpperCase();
    const where = el("div", "fwhere", esc(fmtDay(occ.date).toUpperCase()) + "<br>" + esc(room.name.toUpperCase()));
    row.append(time, line, where);
    [...name].forEach(ch => {
      const cell = el("div", "fc", "&nbsp;");
      line.appendChild(cell);
      flapRows.push({ cell, target: ch });
    });
    return row;
  }
  function buildBoard(list) {
    flapBoard.innerHTML = "";
    flapRows = [];
    list.forEach(occ => flapBoard.appendChild(flapRow(occ)));
    flapSignature = list.map(o => o.ref.id + o.date.toISOString()).join("|");
  }
  function spinBoard() {
    if (reduced) {
      flapRows.forEach(r => { r.cell.textContent = r.target === " " ? "·" : r.target; });
      return;
    }
    flapRows.forEach(r => {
      let n = 0;
      const max = 4 + Math.floor(Math.random() * 9);
      const iv = setInterval(() => {
        n++;
        if (n >= max) { r.cell.textContent = r.target === " " ? "·" : r.target; clearInterval(iv); return; }
        r.cell.innerHTML = '<span class="flip">' + (CHARS[Math.floor(Math.random() * CHARS.length)] || "·") + "</span>";
      }, 48);
    });
  }
  function refreshBoard(force) {
    const list = occurrences(4);
    const sig = list.map(o => o.ref.id + o.date.toISOString()).join("|");
    if (force || sig !== flapSignature) { buildBoard(list); spinBoard(); }
  }
  refreshBoard(true);
  setInterval(() => refreshBoard(false), 60000);

  /* =====================================================
     TIMETABLE — concept 13
  ===================================================== */
  const ttRows = $("#ttRows");
  const ttEmpty = $("#ttEmpty");
  const dayChips = $("#dayChips");
  const catChips = $("#catChips");
  const tabBatches = $("#tabBatches");
  const tabEvents = $("#tabEvents");
  let ttState = { tab: "batches", day: "all", cat: "all" };

  [["all", "All days"]].concat(DAYS.slice(1).concat(DAYS.slice(0, 1)).map(d => [d, DAY_LABEL[d].slice(0, 3)])).forEach(([k, label]) => {
    const b = el("button", "tt-chip", esc(label));
    b.dataset.day = k;
    b.setAttribute("aria-pressed", String(k === "all"));
    b.addEventListener("click", () => {
      ttState.day = k;
      $$("button", dayChips).forEach(x => x.setAttribute("aria-pressed", String(x.dataset.day === k)));
      renderTimetable();
    });
    dayChips.appendChild(b);
  });
  [["all", "All categories"]].concat(Object.entries(CC.categories).map(([k, v]) => [k, v.label])).forEach(([k, label]) => {
    const b = el("button", "tt-chip" + (k !== "all" ? " cat-" + k : ""));
    b.dataset.cat = k;
    b.innerHTML = (k !== "all" ? '<span class="cdot" aria-hidden="true"></span>' : "") + esc(label);
    b.setAttribute("aria-pressed", String(k === "all"));
    b.addEventListener("click", () => {
      ttState.cat = k;
      $$("button", catChips).forEach(x => x.setAttribute("aria-pressed", String(x.dataset.cat === k)));
      renderTimetable();
    });
    catChips.appendChild(b);
  });

  function ttRow(occ) {
    const b = occ.ref;
    const room = roomById(b.roomId);
    const cat = catOf(b.category);
    const wrap = el("div", "tt-row cat-" + b.category);
    const main = el("div", "tt-main");
    main.setAttribute("role", "button");
    main.tabIndex = 0;
    main.setAttribute("aria-expanded", "false");
    main.innerHTML =
      '<span class="tt-time">' + esc(b.time) + "</span>" +
      '<span class="tt-name">' + esc(b.name) + (occ.kind === "event" ? '<span class="tt-event-tag">Event · ' + esc(fmtDay(occ.date)) + "</span>" : "") + "</span>" +
      '<span class="tt-coach">Coach ' + esc(b.coach) + " · " + esc(b.level) + "</span>" +
      '<button class="tt-where" data-room="' + room.id + '" aria-label="' + esc(room.name) + ' — open room details"><span class="cat-dot" aria-hidden="true"></span>' + esc(room.name) + "</button>" +
      '<span class="tt-chev" aria-hidden="true">+</span>';
    const detail = el("div", "tt-detail");
    detail.innerHTML =
      "<div><div class='tt-detail-inner'>" +
        "<p class='d1'><b>What it is</b><br>" + esc(b.desc) + "</p>" +
        "<p><b>Duration</b><br>" + b.duration + " minutes</p>" +
        "<p><b>Level</b><br>" + esc(b.level) + "</p>" +
        "<p><b>What to bring</b><br>" + esc(b.bring) + "</p>" +
        "<div class='bookline'><span style='font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-dim)'>Trial week covers this session</span>" +
        "<button class='mini-accent' data-book-session='" + b.id + "' data-kind='" + occ.kind + "'>Book into “" + esc(b.name) + "”</button>" +
        "<span class='sample-chip'>sample schedule</span></div>" +
      "</div></div>";

    function toggle() {
      const open = main.getAttribute("aria-expanded") === "true";
      main.setAttribute("aria-expanded", String(!open));
      detail.classList.toggle("open", !open);
      $(".tt-chev", main).textContent = open ? "+" : "−";
    }
    main.addEventListener("click", e => { if (!e.target.closest(".tt-where")) toggle(); });
    main.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
    });
    $(".tt-where", main).addEventListener("click", e => {
      e.stopPropagation();
      openRoom(room.id, e.currentTarget);
    });
    $(".mini-accent", detail).addEventListener("click", e => {
      setBookContext({ label: b.name, kind: occ.kind === "event" ? "Event" : "Batch", when: occ.when || b.time });
      goToBook(e.currentTarget);
    });
    wrap.append(main, detail);
    return wrap;
  }

  function renderTimetable() {
    ttRows.innerHTML = "";
    ttEmpty.hidden = true;
    const rows = [];
    if (ttState.tab === "batches") {
      /* fixed weekly grid — every batch shows on its day, every week */
      const order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
      order.forEach(day => {
        if (ttState.day !== "all" && ttState.day !== day) return;
        const dayBatches = CC.batches.filter(b =>
          b.days.includes(day) && (ttState.cat === "all" || b.category === ttState.cat));
        if (!dayBatches.length) return;
        const head = el("p", "tt-day-head");
        head.innerHTML = "<b>" + DAY_LABEL[day] + "</b><span>recurring batch</span>";
        rows.push(head);
        dayBatches.forEach(b => rows.push(ttRow({ kind: "batch", ref: b, day, when: DAY_LABEL[day] + "s · " + b.time })));
      });
    } else {
      /* one-off events, soonest first */
      const now = new Date();
      const evs = CC.events
        .map(e => ({ e, d: new Date(e.date + "T" + e.time + ":00") }))
        .filter(x => x.d >= now)
        .filter(x => ttState.day === "all" || x.e.day === ttState.day)
        .filter(x => ttState.cat === "all" || x.e.category === ttState.cat)
        .sort((a, b) => a.d - b.d);
      evs.forEach(x => {
        const head = el("p", "tt-day-head");
        head.innerHTML = "<b>" + fmtDay(x.d) + " · " + x.d.toDateString().slice(4, 10) + "</b><span>one-off event</span>";
        rows.push(head);
        rows.push(ttRow({ kind: "event", ref: x.e, day: x.e.day, when: fmtDay(x.d) + " " + x.e.time, date: x.d }));
      });
    }
    if (!rows.length) { ttEmpty.hidden = false; return; }
    rows.forEach(r => ttRows.appendChild(r));
  }
  function setTab(tab) {
    ttState.tab = tab;
    tabBatches.setAttribute("aria-selected", String(tab === "batches"));
    tabEvents.setAttribute("aria-selected", String(tab === "events"));
    ttRows.setAttribute("aria-labelledby", tab === "batches" ? "tabBatches" : "tabEvents");
    renderTimetable();
  }
  tabBatches.addEventListener("click", () => setTab("batches"));
  tabEvents.addEventListener("click", () => setTab("events"));
  renderTimetable();

  /* =====================================================
     MEMBERSHIPS
  ===================================================== */
  const plansGrid = $("#plansGrid");
  CC.memberships.forEach(plan => {
    const card = el("article", "plan" + (plan.highlight ? " hl" : ""));
    card.innerHTML =
      (plan.highlight ? '<span class="plan-tag">' + esc(plan.highlightNote || "House pick") + "</span>" : "") +
      '<h3 class="plan-name">' + esc(plan.name) + "</h3>" +
      '<p class="plan-price"><span class="tbc">Price TBC</span></p>' +
      '<p class="plan-billing">' + esc(plan.billing) + " · " + esc(plan.duration) + '</p>' +
      "<div><h4>Included facilities</h4><ul>" + plan.included.map(i => "<li>" + esc(i) + "</li>").join("") + "</ul></div>" +
      "<div><h4>Classes</h4><ul><li>" + esc(plan.classes) + "</li></ul></div>" +
      "<div><h4>Separately charged</h4><ul>" + plan.extras.map(x => '<li class="dimli">' + esc(x) + "</li>").join("") + "</ul></div>" +
      "<div><h4>Terms</h4><ul>" + plan.terms.map(t => '<li class="dimli"><span><b style="font-weight:600">' + esc(t[0]) + "</b> — " + esc(t[1]) + "</span></li>").join("") + "</ul></div>" +
      '<a class="btn btn-accent" href="#book" data-book data-plan="' + esc(plan.id) + '">Start with a trial</a>';
    plansGrid.appendChild(card);
  });

  /* =====================================================
     TRIAL FORM
  ===================================================== */
  const form = $("#trialForm");
  const formContext = $("#formContext");
  const formStatus = $("#formStatus");
  const formSubmit = $("#formSubmit");
  const fName = $("#fName"), fPhone = $("#fPhone"), fDate = $("#fDate");
  fDate.min = new Date().toISOString().slice(0, 10);
  let bookCtx = null;

  function setBookContext(ctx) {
    bookCtx = ctx;
    formContext.hidden = false;
    formContext.innerHTML = "<b>Noted from your visit:</b> " + esc(ctx.kind) + " — “" + esc(ctx.label) + "”" +
      (ctx.when ? " · " + esc(ctx.when) : "") + ". We'll build your trial around it.";
  }
  function goToBook(trigger) {
    closeDirectoryUI();
    document.getElementById("book").scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
    setTimeout(() => fName.focus({ preventScroll: true }), reduced ? 0 : 450);
  }
  $$("[data-plan]").forEach(a => a.addEventListener("click", () => {
    setBookContext({ label: a.dataset.plan === "m2" ? "Training Pass — Annual" : a.textContent.trim(), kind: "Membership interest" });
  }));
  $$("[data-book]").forEach(a => a.addEventListener("click", () => {
    if (!bookCtx) formContext.hidden = true;
  }));

  function validate() {
    let ok = true;
    const nameOk = fName.value.trim().length > 1;
    fName.setAttribute("aria-invalid", String(!nameOk));
    $("#errName").hidden = nameOk;
    if (!nameOk) ok = false;

    const digits = fPhone.value.replace(/[^\d]/g, "");
    const phoneOk = digits.length >= 7;
    fPhone.setAttribute("aria-invalid", String(!phoneOk));
    $("#errPhone").hidden = phoneOk;
    if (!phoneOk) ok = false;

    let dateOk = false;
    if (fDate.value) {
      const picked = new Date(fDate.value + "T23:59");
      dateOk = picked >= new Date();
    }
    fDate.setAttribute("aria-invalid", String(!dateOk));
    $("#errDate").hidden = dateOk;
    if (!dateOk) ok = false;
    return ok;
  }
  [fName, fPhone, fDate].forEach(i => i.addEventListener("input", () => {
    i.setAttribute("aria-invalid", "false");
    $("#err" + i.id.slice(1)).hidden = true;
  }));

  form.addEventListener("submit", e => {
    e.preventDefault();
    formStatus.className = "form-status";
    formStatus.textContent = "";
    if (!validate()) {
      formStatus.className = "form-status err";
      formStatus.textContent = "Almost — check the highlighted fields.";
      const bad = $("[aria-invalid='true']", form);
      if (bad) bad.focus();
      return;
    }
    formSubmit.disabled = true;
    formSubmit.textContent = "Sending…";
    formStatus.className = "form-status loading";
    formStatus.textContent = "Demo mode — simulating the request.";
    setTimeout(() => {
      formSubmit.disabled = false;
      formSubmit.textContent = "Request my trial";
      formStatus.className = "form-status ok";
      formStatus.textContent = "✓ Demo complete — nothing was sent. In production the desk would call " + fPhone.value + " to confirm " + (fDate.value ? "your visit on " + fDate.value : "your visit") + (bookCtx ? " (interest noted: " + bookCtx.kind + " — " + bookCtx.label + ")" : "") + ".";
      form.reset();
    }, 900);
  });

  /* =====================================================
     CONTACT
  ===================================================== */
  $("#contactSampleNote").textContent = CC.contact.sampleNotice;
  const cg = $("#contactGrid");
  cg.innerHTML =
    '<div class="c-card"><h3>Visit</h3><p>' + CC.contact.address.map(esc).join("<br>") + '</p>' +
      '<p class="dim">' + esc(CC.contact.parking) + "</p>" +
      '<p class="dim">' + esc(CC.contact.access) + "</p>" +
      '<p><a href="' + esc(CC.contact.directions) + '">Directions / map link — to add</a></p></div>' +
    '<div class="c-card"><h3>Hours ◇</h3>' +
      CC.contact.hours.map(h => "<p>" + esc(h[0]) + " — <b>" + esc(h[1]) + "</b></p>").join("") +
      '<p class="dim">Staffed vs unstaffed hours to be confirmed.</p></div>' +
    '<div class="c-card"><h3>Talk to the desk ◇</h3>' +
      '<p>Phone — <a href="tel:' + esc(CC.contact.phone.replace(/\s/g, "")) + '">' + esc(CC.contact.phone) + "</a></p>" +
      "<p>WhatsApp — " + esc(CC.contact.whatsapp) + "</p>" +
      '<p>Email — <a href="mailto:' + esc(CC.contact.email) + '">' + esc(CC.contact.email) + "</a></p>" +
      '<p class="dim">Real destinations will replace these samples.</p></div>' +
    '<div class="c-card"><h3>Follow</h3><div class="socials">' +
      CC.contact.socials.map(s => '<a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a>").join("") +
      '</div><p class="dim">Profiles to be linked once confirmed.</p></div>';

  /* =====================================================
     REVEAL (subtle)
  ===================================================== */
  if (!reduced) {
    $$(".section-head, .plans-grid, .equip-grid").forEach(n => n.classList.add("reveal"));
    const rio = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add("in"); rio.unobserve(e.target); }
    }), { threshold: 0.12 });
    $$(".reveal").forEach(n => rio.observe(n));
  }

  /* =====================================================
     HASH ROUTER — deep links + Back support
  ===================================================== */
  function pushView(kind, id) {
    const hash = kind === "room" ? "#room=" + id : "#directory";
    history.pushState({ ccView: kind, id: id || null }, "", hash);
  }
  function closeView(kind) {
    const isRoom = kind === "room";
    const closer = isRoom ? closeRoomUI : closeDirectoryUI;
    if (history.state && history.state.ccView === kind) {
      closer();               /* restore focus + hide now… */
      history.back();         /* …then unwind the pushed entry (popstate re-checks) */
    } else {
      closer();
      history.replaceState(null, "", location.pathname + location.search + "#plan");
    }
  }
  function router() {
    const h = location.hash;
    const roomMatch = h.match(/^#room=([\w-]+)/);
    if (roomMatch && roomById(roomMatch[1])) {
      const id = roomMatch[1];
      if (lastRoom == null || lastRoom.id !== id || panel.hidden) { renderRoom(roomById(id)); showRoomUI(); }
      hideDirectoryUI(true);
      return;
    }
    if (h === "#directory") {
      renderDirectory();
      showDirectoryUI();
      closeRoomUI();
      return;
    }
    /* any other hash → close overlays (page anchors navigate normally) */
    closeRoomUI();
    hideDirectoryUI(true);
  }
  function hideDirectoryUI(silent) {
    if (!directory.hidden) {
      dirUntrap && dirUntrap(); dirUntrap = null;
      directory.hidden = true;
      document.documentElement.style.overflow = panel.hidden ? "" : "hidden";
    }
  }
  addEventListener("popstate", router);
  addEventListener("hashchange", router);
  rpClose.addEventListener("click", () => closeView("room"));
  router();
})();
