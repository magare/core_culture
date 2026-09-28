/* Campaign 02: editorial entrance, one-shot reveals, and lightweight scroll motion. */
(() => {
  "use strict";

  const root = document.documentElement;
  const nav = document.querySelector("#siteNav");
  const reducedQuery = matchMedia("(prefers-reduced-motion: reduce)");
  const forcedReduced = new URLSearchParams(location.search).has("rm");
  const $ = selector => document.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const clamp = value => Math.max(0, Math.min(1, value));
  let teardown = () => {};

  root.classList.add("motion-ready");

  function configure() {
    teardown();
    const isReduced = reducedQuery.matches || forcedReduced;
    root.classList.toggle("reduce-motion", isReduced);

    const events = new AbortController();
    const listen = (target, event, callback, options = {}) => target?.addEventListener(event, callback, { ...options, signal: events.signal });
    const setHeader = () => nav?.classList.toggle("is-scrolled", scrollY > 20);
    setHeader();

    if (isReduced || !("IntersectionObserver" in window)) {
      $$(".motion-reveal").forEach(element => element.classList.add("is-visible"));
      listen(window, "scroll", setHeader, { passive: true });
      teardown = () => {
        events.abort();
        $$(".motion-reveal").forEach(element => element.classList.add("is-visible"));
        nav?.style.removeProperty("--page-progress");
      };
      return;
    }

    const hero = $("#top");
    const heroMedia = $(".hero-media");
    const band = $(".kinetic-band");
    const bandTrack = $(".kinetic-track");
    const footer = $(".site-footer");
    const footerWord = $(".footer-wordmark");
    const parallaxImages = $$(".story-image img, .recovery-visual img, .visit-image img");
    let frame = 0;
    let measureFrame = 0;
    let geometry = null;

    const reveals = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        reveals.unobserve(entry.target);
      });
    }, { threshold: .08, rootMargin: "0px 0px -10% 0px" });

    function register(elements, kind = "rise", step = 55) {
      elements.filter(Boolean).forEach((element, index) => {
        element.classList.add("motion-reveal");
        element.dataset.revealKind = kind;
        element.style.setProperty("--reveal-delay", `${Math.min(index, 4) * step}ms`);
        if (kind === "image") element.classList.add("motion-image");
        reveals.observe(element);
      });
    }

    const groups = [
      $$(".plan-intro > *"),
      $$(".story-heading > *"),
      $$(".story-principles article"),
      $$(".spaces-section .section-heading > div:first-child > *"),
      $$(".space-card"),
      $$(".recovery-copy > *"),
      $$(".schedule-section .section-heading > div:first-child > *"),
      $$(".membership-layout > div:first-child > *"),
      $$(".membership-notice"),
      $$(".visit-content > .eyebrow, .visit-content > h2, .visit-content > .visit-lede, .visit-content > form"),
      $$(".contact-strip > *"),
      $$(".footer-top > *, .footer-bottom > *")
    ];
    groups.forEach(group => register(group));
    register($$(".plan-model-panel, .heading-aside, .space-ledger, .next-session, .timetable, .membership-layout > div:last-child"), "rise", 45);
    register($$(".story-image, .recovery-visual, .visit-image"), "image", 0);

    function revealHashTarget() {
      if (!location.hash || location.hash.includes("=")) return;
      const target = document.querySelector(location.hash);
      if (!target) return;
      $$(".motion-reveal", target).forEach(element => {
        element.classList.add("is-visible");
        reveals.unobserve(element);
      });
    }
    revealHashTarget();

    const bandVisibility = band ? new IntersectionObserver(entries => {
      entries.forEach(entry => band.classList.toggle("is-moving", entry.isIntersecting));
    }, { rootMargin: "25% 0px" }) : null;
    if (bandVisibility) bandVisibility.observe(band);

    function rect(element) {
      const value = element.getBoundingClientRect();
      return { top: value.top + scrollY, height: value.height };
    }

    function measureNow() {
      measureFrame = 0;
      geometry = {
        hero: hero ? rect(hero) : null,
        heroMedia: heroMedia ? rect(heroMedia) : null,
        band: band ? rect(band) : null,
        bandTravel: band && bandTrack ? Math.min(Math.max(0, bandTrack.scrollWidth - band.clientWidth), innerWidth * .28) : 0,
        footer: footer ? rect(footer) : null,
        images: parallaxImages.map(rect),
        document: Math.max(1, root.scrollHeight - innerHeight)
      };
      requestUpdate();
    }

    function measure() {
      cancelAnimationFrame(measureFrame);
      measureFrame = requestAnimationFrame(measureNow);
    }

    function update() {
      frame = 0;
      if (!geometry || document.hidden || document.body.classList.contains("modal-open")) return;
      const pageY = scrollY;
      setHeader();
      nav?.style.setProperty("--page-progress", clamp(pageY / geometry.document).toFixed(4));

      if (geometry.hero && hero) {
        const progress = clamp((pageY - geometry.hero.top) / Math.max(1, geometry.hero.height));
        hero.style.setProperty("--hero-copy-y", `${(-progress * 16).toFixed(2)}px`);
        hero.style.setProperty("--hero-copy-opacity", (1 - progress * .08).toFixed(3));
      }
      if (geometry.heroMedia && heroMedia) {
        const progress = clamp((pageY + innerHeight - geometry.heroMedia.top) / (innerHeight + geometry.heroMedia.height));
        heroMedia.style.setProperty("--hero-media-y", `${((progress - .5) * -18).toFixed(2)}px`);
      }
      if (geometry.band && bandTrack) {
        const progress = clamp((pageY + innerHeight - geometry.band.top) / (innerHeight + geometry.band.height));
        bandTrack.style.setProperty("--band-x", `${(-progress * geometry.bandTravel).toFixed(2)}px`);
      }
      parallaxImages.forEach((image, index) => {
        const item = geometry.images[index];
        if (pageY + innerHeight < item.top || pageY > item.top + item.height) return;
        const progress = clamp((pageY + innerHeight - item.top) / (innerHeight + item.height));
        image.style.setProperty("--parallax-y", `${((progress - .5) * -20).toFixed(2)}px`);
      });
      if (geometry.footer && footerWord) {
        const progress = clamp((pageY + innerHeight - geometry.footer.top) / Math.max(1, geometry.footer.height));
        footerWord.style.setProperty("--footer-y", `${((1 - progress) * 28).toFixed(2)}px`);
      }
    }

    function requestUpdate() {
      if (!frame) frame = requestAnimationFrame(update);
    }

    listen(window, "scroll", requestUpdate, { passive: true });
    listen(window, "resize", measure, { passive: true });
    listen(window, "pageshow", measure);
    listen(window, "hashchange", revealHashTarget);
    listen(document, "visibilitychange", requestUpdate);
    listen(document, "focusin", event => {
      const element = event.target.closest(".motion-reveal");
      if (!element) return;
      element.classList.add("is-visible");
      reveals.unobserve(element);
    });
    $$("dialog").forEach(dialog => listen(dialog, "close", requestUpdate));

    const layout = "ResizeObserver" in window ? new ResizeObserver(measure) : null;
    if (layout) layout.observe($("main") || document.body);
    measure();
    document.fonts.ready.then(() => {
      if (!events.signal.aborted) measure();
    });

    teardown = () => {
      events.abort();
      reveals.disconnect();
      bandVisibility?.disconnect();
      layout?.disconnect();
      cancelAnimationFrame(frame);
      cancelAnimationFrame(measureFrame);
      $$(".motion-reveal").forEach(element => element.classList.add("is-visible"));
      parallaxImages.forEach(image => image.style.removeProperty("--parallax-y"));
      hero?.style.removeProperty("--hero-copy-y");
      hero?.style.removeProperty("--hero-copy-opacity");
      heroMedia?.style.removeProperty("--hero-media-y");
      bandTrack?.style.removeProperty("--band-x");
      band?.classList.remove("is-moving");
      footerWord?.style.removeProperty("--footer-y");
      nav?.style.removeProperty("--page-progress");
    };
  }

  reducedQuery.addEventListener("change", configure);
  configure();
})();
