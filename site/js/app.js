/* Core Culture — progressive, dependency-free interactions. */
(function () {
  "use strict";
  const CC = window.CC;
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const esc = value => String(value == null ? "" : value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const pad = n => String(n).padStart(2, "0");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const forcedReducedMotion = new URLSearchParams(location.search).has("rm");
  const motion = () => reducedMotion.matches || forcedReducedMotion ? "auto" : "smooth";
  if (motion() === "auto") document.documentElement.classList.add("reduce-motion");
  const days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
  const dayNames = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };
  const roomById = id => CC.rooms.find(room => room.id === id);
  const localISO = date => date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate());
  const dateLabel = date => date.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
  const makeDate = (iso, time) => new Date(iso + "T" + time + ":00");
  $("#year").textContent = new Date().getFullYear();

  function occurrences(roomId) {
    const now = new Date();
    const list = [];
    CC.batches.forEach(item => {
      if (roomId && item.roomId !== roomId) return;
      item.days.forEach(day => {
        const date = new Date(now);
        const [hour, minute] = item.time.split(":").map(Number);
        date.setHours(hour, minute, 0, 0);
        date.setDate(date.getDate() + (days.indexOf(day) - now.getDay() + 7) % 7);
        if (date <= now) date.setDate(date.getDate() + 7);
        list.push({ ...item, dateObject: date });
      });
    });
    CC.events.forEach(item => {
      const date = makeDate(item.date, item.time);
      if ((!roomId || item.roomId === roomId) && date > now) list.push({ ...item, dateObject: date });
    });
    return list.sort((a, b) => a.dateObject - b.dateObject);
  }

  /* Native dialogs provide focus containment, inert backgrounds, and restoration. */
  const roomDialog = $("#roomPanel");
  const directory = $("#directory");
  const lightbox = $("#lightbox");
  const modelDialog = $("#modelDialog");
  const menu = $("#mobileMenu");
  let currentRoute = "";
  let originFocus = null;
  let routeSequence = 0;
  const routeOrigins = new Map();
  let gallery = [];
  let galleryIndex = 0;
  const lockScroll = () => document.body.classList.toggle("modal-open", $$("dialog[open]").length > 0);

  function openRoute(hash) {
    if (hash === location.hash) return;
    const isOverlay = location.hash.startsWith("#room=") || location.hash === "#directory";
    if (!isOverlay) originFocus = document.activeElement;
    const focusId = ++routeSequence;
    routeOrigins.set(focusId, originFocus);
    history.pushState({ ccOverlay: true, ccFocusId: focusId }, "", hash);
    syncRoute();
  }

  function closeRoute() {
    if (lightbox.open) { lightbox.close(); return; }
    if (history.state && history.state.ccOverlay) history.back();
    else {
      history.replaceState(null, "", "#amenities");
      syncRoute();
      $("#amenities").scrollIntoView({ behavior: motion() });
    }
  }

  function syncRoute() {
    const hash = location.hash;
    if (hash === currentRoute) return;
    if (lightbox.open) lightbox.close();
    if (modelDialog.open) modelDialog.close();
    if (roomDialog.open) roomDialog.close();
    if (directory.open) directory.close();
    currentRoute = hash;
    if (hash.startsWith("#room=")) {
      originFocus = routeOrigins.get(history.state && history.state.ccFocusId) || null;
      let id;
      try { id = decodeURIComponent(hash.slice(6)); } catch (_) { id = ""; }
      const room = roomById(id);
      if (room) {
        renderRoom(room);
        roomDialog.showModal();
        roomDialog.scrollTop = 0;
      }
    } else if (hash === "#directory") {
      originFocus = routeOrigins.get(history.state && history.state.ccFocusId) || null;
      renderDirectory();
      directory.showModal();
      directory.scrollTop = 0;
    } else if (originFocus && originFocus.isConnected) {
      const trigger = originFocus;
      // History traversal can reset focus after popstate; restore it after that work.
      requestAnimationFrame(() => {
        if (currentRoute === hash && hash !== "#book" && !$$("dialog[open]").length) trigger.focus({ preventScroll: true });
      });
      originFocus = null;
    }
    lockScroll();
  }
  window.addEventListener("popstate", syncRoute);
  window.addEventListener("hashchange", syncRoute);
  $("#rpClose").addEventListener("click", closeRoute);
  $("#dirClose").addEventListener("click", closeRoute);
  [roomDialog, directory].forEach(dialog => dialog.addEventListener("cancel", event => { event.preventDefault(); closeRoute(); }));
  $$("dialog").forEach(dialog => {
    dialog.addEventListener("close", lockScroll);
    dialog.addEventListener("click", event => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (event.clientX >= r.left && event.clientX <= r.right && event.clientY >= r.top && event.clientY <= r.bottom) return;
      if (dialog === roomDialog || dialog === directory) closeRoute();
      else dialog.close();
    });
  });
  // Keep Tab cycling inside the topmost dialog, including browser chrome edges.
  document.addEventListener("keydown", event => {
    if (event.key !== "Tab") return;
    const dialog = $$("dialog[open]").at(-1);
    if (!dialog) return;
    const controls = $$("a[href],button,input,select,textarea,[tabindex]", dialog)
      .filter(node => !node.disabled && node.tabIndex >= 0 && node.getClientRects().length && getComputedStyle(node).visibility !== "hidden");
    if (!controls.length) { event.preventDefault(); return; }
    const first = controls[0];
    const last = controls[controls.length - 1];
    const active = document.activeElement;
    if (!dialog.contains(active) || active === dialog || (event.shiftKey && active === first)) {
      event.preventDefault();
      (event.shiftKey ? last : first).focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  }, true);
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const routeLink = event.target.closest('a[href^="#room="], a[href="#directory"]');
    if (routeLink) { event.preventDefault(); openRoute(routeLink.getAttribute("href")); }
    const book = event.target.closest("[data-book-context]");
    if (book) {
      event.preventDefault();
      startBooking(book.dataset.bookContext, book.dataset.category || "general", book.dataset.bookDate, book.dataset.bookTime);
    }
  });

  $("#menuBtn").addEventListener("click", () => {
    menu.showModal();
    $("#menuBtn").setAttribute("aria-expanded", "true");
    lockScroll();
  });
  $("#menuClose").addEventListener("click", () => menu.close());
  menu.addEventListener("close", () => $("#menuBtn").setAttribute("aria-expanded", "false"));
  $$("a", menu).forEach(link => link.addEventListener("click", () => menu.close()));

  /* A native horizontal rail: no scroll hijacking, no automatic motion. */
  const order = ["strength", "hybrid", "studio", "cardio", "recovery", "lounge", "lobby", "arrival"];
  const track = $("#spaceTrack");
  track.innerHTML = order.map((id, i) => {
    const room = roomById(id);
    return '<a class="space-card" data-room="' + id + '" href="#room=' + id + '"><div class="space-photo"><img src="' + esc(room.photo.src) + '" alt="' + esc(room.photo.alt) + '" width="1122" height="1402" loading="lazy" decoding="async"><span class="space-no">' + pad(i + 1) + '</span><span class="space-tag">' + esc(CC.categories[room.category].label) + '</span></div><div class="space-caption"><h3>' + esc(room.name) + '</h3><i class="ph ph-arrow-up-right" aria-hidden="true"></i></div><p>' + esc(room.tagline) + '</p></a>';
  }).join("");
  const cardStep = () => {
    const cards = $$(".space-card", track);
    return cards[1].offsetLeft - cards[0].offsetLeft;
  };
  function updateRail() {
    const step = cardStep();
    const index = Math.min(order.length - 1, Math.round(track.scrollLeft / step));
    $$(".space-card", track).forEach((card, cardIndex) => card.classList.toggle("is-active", cardIndex === index));
    $("#spaceCounter").textContent = pad(index + 1) + " — " + pad(order.length);
    $("#carPrev").disabled = track.scrollLeft < 5;
    $("#carNext").disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 5;
  }
  const moveRail = direction => track.scrollBy({ left: direction * cardStep(), behavior: motion() });
  $("#carPrev").addEventListener("click", () => moveRail(-1));
  $("#carNext").addEventListener("click", () => moveRail(1));
  track.addEventListener("scroll", updateRail, { passive: true });
  track.addEventListener("keydown", event => {
    if (event.target !== track) return;
    if (event.key === "ArrowRight" || event.key === "ArrowLeft") { event.preventDefault(); moveRail(event.key === "ArrowRight" ? 1 : -1); }
  });
  new ResizeObserver(updateRail).observe(track);
  updateRail();

  /* The architectural model has its own lazy-loaded Three.js viewer. */
  const planOrder = ["strength", "hybrid", "cardio", "studio", "recovery", "lounge", "lobby", "arrival"];
  $("#roomList").innerHTML = planOrder.map((id, i) => '<button data-room="' + id + '"><span>' + pad(i + 1) + '</span><strong>' + esc(roomById(id).name) + '</strong><i class="ph ph-arrow-up-right" aria-hidden="true"></i></button>').join("");
  $$("button", $("#roomList")).forEach(button => {
    button.addEventListener("click", () => openRoute("#room=" + button.dataset.room));
  });

  function renderRoom(room) {
    gallery = room.gallery;
    galleryIndex = 0;
    const sessions = occurrences(room.id).slice(0, 3);
    $("#rpBody").innerHTML =
      '<div class="room-hero"><img id="roomGalleryImg" src="' + esc(gallery[0].src) + '" alt="' + esc(gallery[0].alt) + '"><button class="gallery-enlarge" id="enlargePhoto">View full image <i class="ph ph-arrows-out" aria-hidden="true"></i></button></div>' +
      '<div class="room-content"><p class="eyebrow">' + esc(CC.categories[room.category].label) + ' / CONCEPT SPACE</p><h2 id="rpName">' + esc(room.name) + '</h2><p class="room-intro">' + esc(room.intro) + '</p>' +
      (gallery.length > 1 ? '<div class="gallery-thumbs" aria-label="Room photos">' + gallery.map((photo, i) => '<button data-photo="' + i + '" aria-label="View photo ' + (i + 1) + '" aria-pressed="' + (i === 0) + '"><img src="' + esc(photo.src) + '" alt=""></button>').join("") + '</div>' : '') +
      '<div class="room-section"><h3>A space concept, not a promise.</h3><p class="room-access">The imagery describes a possible training mood. Final equipment, facilities, access, capacity, and operating details will be published only when confirmed.</p></div>' +
      (room.equipment.length ? '<div class="room-section"><h3>Tools under consideration.</h3><div class="room-features">' + room.equipment.map(id => { const item = CC.equipment.find(e => e.id === id); return '<button class="equipment-chip" data-equipment="' + id + '">' + esc(item.name) + ' <i class="ph ph-arrow-up-right" aria-hidden="true"></i></button>'; }).join("") + '</div></div>' : '') +
      '<div class="room-section"><h3>Sample sessions in this space.</h3>' + (sessions.length ? sessions.map(item => '<div class="room-session"><div>' + esc(item.name) + '<small>' + esc(dateLabel(item.dateObject)) + ' · ' + item.time + ' · Sample session</small></div><button data-book-context="' + esc(item.name) + '" data-category="' + item.category + '" data-book-date="' + localISO(item.dateObject) + '" data-book-time="' + item.time + '">Preview <i class="ph ph-arrow-up-right" aria-hidden="true"></i></button></div>').join("") : '<p class="room-access">Explore this space as part of your first-visit preview.</p>') + '</div>' +
      '<button class="button" data-book-context="' + esc(room.name) + '" data-category="' + room.category + '">Preview this starting point <i class="ph ph-arrow-up-right" aria-hidden="true"></i></button><p class="room-access">Concept imagery, not verified venue photography. Facilities and access are not confirmed.</p></div>';
    $("#roomGalleryImg").style.objectPosition = gallery[0].heroPosition || "50% 50%";
    $("#enlargePhoto").addEventListener("click", () => { updateLightbox(); lightbox.showModal(); lockScroll(); });
    $$("[data-photo]", roomDialog).forEach(button => button.addEventListener("click", () => {
      galleryIndex = Number(button.dataset.photo);
      updateRoomPhoto();
    }));
    $$("[data-equipment]", roomDialog).forEach(button => button.addEventListener("click", () => {
      const item = CC.equipment.find(e => e.id === button.dataset.equipment);
      $("#dirSearch").value = item.name;
      $("#dirZone").value = item.roomId;
      openRoute("#directory");
    }));
  }
  function updateLightbox() {
    lightbox.setAttribute("aria-label", "Enlarged room photo");
    $("#lbImg").src = gallery[galleryIndex].src;
    $("#lbImg").alt = gallery[galleryIndex].alt;
    $("#lbCap").textContent = gallery[galleryIndex].caption + " · " + (galleryIndex + 1) + " / " + gallery.length;
    $("#lbPrev").hidden = $("#lbNext").hidden = gallery.length < 2;
  }
  function updateRoomPhoto() {
    $("#roomGalleryImg").src = gallery[galleryIndex].src;
    $("#roomGalleryImg").alt = gallery[galleryIndex].alt;
    $("#roomGalleryImg").style.objectPosition = gallery[galleryIndex].heroPosition || "50% 50%";
    $$("[data-photo]", roomDialog).forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.photo) === galleryIndex)));
  }
  function stepPhoto(delta) {
    galleryIndex = (galleryIndex + delta + gallery.length) % gallery.length;
    updateLightbox();
    updateRoomPhoto();
  }
  $("#lbClose").addEventListener("click", () => lightbox.close());
  $("#lbPrev").addEventListener("click", () => stepPhoto(-1));
  $("#lbNext").addEventListener("click", () => stepPhoto(1));
  lightbox.addEventListener("keydown", event => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") { event.preventDefault(); stepPhoto(event.key === "ArrowLeft" ? -1 : 1); }
  });

  /* Search and zone filtering share the central inventory. */
  CC.rooms.filter(r => r.equipment.length).forEach(room => $("#dirZone").insertAdjacentHTML("beforeend", '<option value="' + room.id + '">' + esc(room.name) + '</option>'));
  function renderDirectory() {
    const query = $("#dirSearch").value.trim().toLowerCase();
    const zone = $("#dirZone").value;
    const items = CC.equipment.filter(item => roomById(item.roomId).equipment.includes(item.id) && (zone === "all" || item.roomId === zone) && (item.name + " " + item.purpose + " " + CC.categories[item.category].label).toLowerCase().includes(query));
    $("#dirCount").textContent = items.length + (items.length === 1 ? " item" : " items");
    $("#dirGrid").innerHTML = items.length ? items.map(item =>
      '<article class="equipment-item"><div><p class="eyebrow">' + esc(roomById(item.roomId).name) + '</p><h3>' + esc(item.name) + '</h3><p>' + esc(item.purpose) + '</p><details><summary>Unconfirmed specifications</summary><dl><div><dt>Status</dt><dd>To be confirmed</dd></div></dl></details></div><a class="text-link" href="#room=' + item.roomId + '">Explore the concept <i class="ph ph-arrow-up-right" aria-hidden="true"></i></a></article>'
    ).join("") : '<div class="empty-state"><p>No equipment matches your search.</p><button class="text-link" id="clearSearch">Clear filters</button></div>';
    const clear = $("#clearSearch");
    if (clear) clear.addEventListener("click", () => { $("#dirSearch").value = ""; $("#dirZone").value = "all"; renderDirectory(); $("#dirSearch").focus(); });
  }
  $("#openDirectory").addEventListener("click", () => { $("#dirSearch").value = ""; $("#dirZone").value = "all"; openRoute("#directory"); });
  $("#dirSearch").addEventListener("input", renderDirectory);
  $("#dirZone").addEventListener("change", renderDirectory);

  /* An actual day view keeps the weekly schedule short and useful. */
  const schedule = { type: "classes", day: days[new Date().getDay()], category: "all" };
  Object.entries(CC.categories).forEach(([key, category]) => $("#classCategory").insertAdjacentHTML("beforeend", '<option value="' + key + '">' + esc(category.label) + '</option>'));
  const scheduleDates = {};
  const today = new Date();
  Array.from({ length: 7 }, (_, i) => days[(today.getDay() + i) % 7]).forEach((day, i) => {
    const date = new Date(today); date.setDate(date.getDate() + i);
    scheduleDates[day] = localISO(date);
    const button = document.createElement("button");
    button.dataset.day = day;
    button.setAttribute("aria-label", dayNames[day] + ", " + dateLabel(date) + (i === 0 ? ", today" : ""));
    button.setAttribute("aria-pressed", String(schedule.day === day));
    button.innerHTML = day.toUpperCase() + '<span>' + date.getDate() + '</span>';
    button.addEventListener("click", () => { schedule.day = day; renderSchedule(); });
    $("#dayChips").append(button);
  });
  function renderSchedule() {
    $$("[data-day]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.day === schedule.day)));
    $("#dayChips").hidden = schedule.type === "events";
    const source = schedule.type === "classes" ? CC.batches.filter(item => item.days.includes(schedule.day) && makeDate(scheduleDates[schedule.day], item.time) > new Date()) : CC.events.filter(item => makeDate(item.date, item.time) > new Date());
    const items = source.filter(item => schedule.category === "all" || item.category === schedule.category).sort((a, b) => ((a.date || "") + a.time).localeCompare((b.date || "") + b.time));
    $("#scheduleEmpty").hidden = items.length > 0;
    $("#scheduleEmptyText").textContent = schedule.type === "events" ? "No event concepts in this selection. Explore the sample week instead." : "No sample sessions in this selection. Try another day or discipline.";
    $("#scheduleCount").textContent = items.length + (schedule.type === "classes" ? " sample " + (items.length === 1 ? "session" : "sessions") + " · " + dateLabel(new Date(scheduleDates[schedule.day] + "T12:00:00")) : " sample " + (items.length === 1 ? "event concept" : "event concepts"));
    $("#sessionList").innerHTML = items.map(item => {
      const room = roomById(item.roomId);
      const date = item.date ? new Date(item.date + "T12:00:00") : null;
      return '<details class="session"><summary><span class="session-time">' + (date ? date.toLocaleDateString("en-GB", { day: "numeric", month: "short" }) + '<small>' + item.time + '</small>' : item.time) + '</span><span class="session-name">' + esc(item.name) + '<span class="session-subtitle">' + esc(room.name) + ' · ' + esc(item.level) + '</span></span><span class="session-duration">' + item.duration + ' MIN</span><i class="session-plus ph ph-plus" aria-hidden="true"></i></summary><div class="session-detail"><p>' + esc(item.desc) + '</p><p>Bring: ' + esc(item.bring) + '</p><div class="session-detail-actions"><a class="text-link" href="#room=' + item.roomId + '">Explore the concept <i class="ph ph-arrow-up-right" aria-hidden="true"></i></a><button class="button" data-book-context="' + esc(item.name) + '" data-category="' + item.category + '" data-book-date="' + (item.date || scheduleDates[schedule.day]) + '" data-book-time="' + item.time + '">Preview this session <i class="ph ph-arrow-up-right" aria-hidden="true"></i></button></div></div></details>';
    }).join("");
    $$(".session", $("#sessionList")).forEach((session, index) => session.style.setProperty("--session-index", index));
  }
  function setScheduleTab(type, focus) {
    schedule.type = type;
    const active = type === "classes" ? $("#tabBatches") : $("#tabEvents");
    [$("#tabBatches"), $("#tabEvents")].forEach(tab => { tab.setAttribute("aria-selected", String(tab === active)); tab.tabIndex = tab === active ? 0 : -1; });
    $("#schedulePanel").setAttribute("aria-labelledby", active.id);
    if (focus) active.focus();
    renderSchedule();
  }
  $("#tabBatches").addEventListener("click", () => setScheduleTab("classes"));
  $("#tabEvents").addEventListener("click", () => setScheduleTab("events"));
  $(".tabs").addEventListener("keydown", event => {
    if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
      event.preventDefault();
      setScheduleTab(event.key === "Home" ? "classes" : event.key === "End" ? "events" : schedule.type === "classes" ? "events" : "classes", true);
    }
  });
  $("#classCategory").addEventListener("change", event => { schedule.category = event.target.value; renderSchedule(); });
  $("#scheduleReset").addEventListener("click", () => {
    schedule.category = "all";
    $("#classCategory").value = "all";
    const next = occurrences().find(item => !item.date);
    if (next) schedule.day = days[next.dateObject.getDay()];
    setScheduleTab("classes", true);
  });
  let nextSignature = "";
  function renderNext() {
    const next = occurrences()[0];
    const signature = next ? next.id + next.dateObject.toISOString() : "empty";
    if (signature === nextSignature) return;
    nextSignature = signature;
    if (!next) { $("#nextSession").innerHTML = '<h3 id="next-title">A new week awaits.</h3>'; return; }
    $("#nextSession").innerHTML = '<p class="next-day">' + esc(dateLabel(next.dateObject)) + '</p><p class="next-time">' + next.time + '</p><h3 id="next-title">' + esc(next.name) + '</h3><p class="next-meta">' + esc(roomById(next.roomId).name) + ' / ' + next.duration + ' MIN</p><button class="text-link" data-book-context="' + esc(next.name) + '" data-category="' + next.category + '" data-book-date="' + localISO(next.dateObject) + '" data-book-time="' + next.time + '">Preview this session <i class="ph ph-arrow-up-right" aria-hidden="true"></i></button>';
  }
  renderSchedule(); renderNext();
  window.setInterval(() => { if (!document.hidden) renderNext(); }, 60000);

  $("#plansGrid").innerHTML = [
    ["01", "Plans", "Formats are still being defined."],
    ["02", "Rates", "No price has been published."],
    ["03", "Access", "Benefits and terms are not yet confirmed."]
  ].map(item => '<article class="membership-notice"><span>' + item[0] + '</span><h3>' + item[1] + '</h3><p>' + item[2] + '</p></article>').join("");

  /* Explicit local-only demo. No network request and no persistent form data. */
  const form = $("#trialForm");
  const fields = { Name: $("#fName"), Phone: $("#fPhone"), Date: $("#fDate") };
  fields.Date.min = localISO(new Date());
  let bookingContext = "";
  $("#fInterest").addEventListener("change", () => {
    bookingContext = "";
    $("#formContext").hidden = true;
  });
  function startBooking(context, category, date, time) {
    bookingContext = context;
    Object.entries(fields).forEach(([name, input]) => {
      $("#err" + name).textContent = "";
      input.removeAttribute("aria-invalid");
    });
    fields.Date.min = localISO(new Date());
    $("#formContext").hidden = false;
    $("#formContext").innerHTML = '<span>Your interest: <strong>' + esc(context) + '</strong>' + (date ? '<small>' + esc(dateLabel(new Date(date + "T12:00:00"))) + (time ? ' · ' + esc(time) : '') + '</small>' : '') + '</span><button type="button" id="clearContext" aria-label="Clear selected interest">Clear</button>';
    $("#clearContext").addEventListener("click", () => { bookingContext = ""; $("#formContext").hidden = true; $("#fInterest").value = "general"; $("#fInterest").focus(); });
    $("#fInterest").value = category;
    if (date) fields.Date.value = date;
    if (time) $("#fTime").value = Number(time.slice(0, 2)) < 12 ? "Morning" : Number(time.slice(0, 2)) < 17 ? "Afternoon" : "Evening";
    $("#formStatus").hidden = true;
    if (menu.open) menu.close();
    if (lightbox.open) lightbox.close();
    if (location.hash !== "#book") history.pushState(null, "", "#book");
    syncRoute();
    $("#book").scrollIntoView({ behavior: motion() });
    fields.Name.focus({ preventScroll: true });
  }
  form.addEventListener("input", () => { $("#formStatus").hidden = true; });
  Object.entries(fields).forEach(([name, input]) => input.addEventListener("input", () => {
    $("#err" + name).textContent = "";
    input.removeAttribute("aria-invalid");
    $("#formStatus").hidden = true;
  }));
  form.addEventListener("submit", event => {
    event.preventDefault();
    $("#formStatus").hidden = true;
    const name = fields.Name.value.trim();
    const phone = fields.Phone.value.trim();
    const date = fields.Date.value;
    const digits = phone.replace(/\D/g, "");
    const errors = {
      Name: name.length < 2 ? "Please enter your full name." : "",
      Phone: !/^\+?[()\d\s.-]+$/.test(phone) || digits.length < 7 || digits.length > 15 ? "Please enter a valid phone number." : "",
      Date: !date || date < localISO(new Date()) || !Number.isFinite(new Date(date + "T12:00:00").getTime()) ? "Choose today or a future date." : ""
    };
    Object.entries(errors).forEach(([key, error]) => {
      $("#err" + key).textContent = error;
      fields[key].setAttribute("aria-invalid", String(Boolean(error)));
    });
    const first = Object.keys(errors).find(key => errors[key]);
    if (first) { fields[first].focus(); return; }
    const context = bookingContext ? " for " + bookingContext : "";
    $("#formStatus").innerHTML = '<strong>Visit preview ready.</strong><p>Your visit preview' + esc(context) + ' is ready for ' + esc(dateLabel(new Date(date + "T12:00:00"))) + ' · ' + esc($("#fTime").value) + '. This is a demo: nothing was sent, no visit was booked, and your details have not been saved.</p>';
    $("#formStatus").hidden = false;
    $("#formStatus").focus({ preventScroll: true });
    form.reset();
    Object.values(fields).forEach(field => field.removeAttribute("aria-invalid"));
    bookingContext = "";
    $("#formContext").hidden = true;
  });

  // Observe every page region so a previous section is not left active in the hero.
  const navSections = ["top", "club", "amenities", "recovery", "schedule", "plan", "memberships", "book", "contact"].map(id => $("#" + id));
  const navObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      $$(".desktop-nav a").forEach(link => {
        if (link.getAttribute("href") === "#" + entry.target.id) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    });
  }, { rootMargin: "-15% 0px -60% 0px", threshold: 0 });
  navSections.forEach(section => navObserver.observe(section));
  syncRoute();
})();
