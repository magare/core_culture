/* Core Culture motion system: Lenis scroll physics + GSAP choreography. */
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

(() => {
  "use strict";

  gsap.registerPlugin(ScrollTrigger);

  const root = document.documentElement;
  const nav = document.querySelector("#siteNav");
  const reducedQuery = matchMedia("(prefers-reduced-motion: reduce)");
  const forcedReduced = new URLSearchParams(location.search).has("rm");
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  let teardown = () => {};

  root.classList.add("motion-ready");

  function showEverything() {
    $$(".motion-reveal").forEach(element => {
      element.classList.add("is-visible");
      gsap.set(element, { clearProps: "all" });
    });
    gsap.set($$(".hero-copy-panel > *, .hero-media, .hero-media img, .first-route, main section h2"), { clearProps: "all" });
    nav?.style.removeProperty("--page-progress");
  }

  function configure() {
    teardown();
    const isReduced = reducedQuery.matches || forcedReduced;
    root.classList.toggle("reduce-motion", isReduced);
    root.classList.toggle("gsap-ready", !isReduced);

    const events = new AbortController();
    const listen = (target, event, callback, options = {}) => target?.addEventListener(event, callback, { ...options, signal: events.signal });
    const setHeader = scroll => nav?.classList.toggle("is-scrolled", scroll > 20);
    setHeader(scrollY);

    if (isReduced) {
      showEverything();
      listen(window, "scroll", () => setHeader(scrollY), { passive: true });
      teardown = () => events.abort();
      return;
    }

    const lenis = new Lenis({
      duration: 1.08,
      easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 0.88,
      touchMultiplier: 1,
      syncTouch: false,
      overscroll: true
    });

    const reflectiveTargets = $$("main h1, main h2, main h3, .kinetic-track span, .footer-wordmark");
    const reflectiveOverlays = [];
    reflectiveTargets.forEach(target => {
      target.classList.add("reflective-type-target");
      const overlay = document.createElement("span");
      overlay.className = "reflective-type-overlay";
      overlay.innerHTML = target.innerHTML;
      overlay.setAttribute("aria-hidden", "true");
      target.append(overlay);
      reflectiveOverlays.push(overlay);
    });

    function updateReflectiveLighting(scroll, velocity = 0) {
      const speed = Math.min(1, Math.abs(Number(velocity) || 0) / 2.4);
      reflectiveTargets.forEach((target, index) => {
        const rect = target.getBoundingClientRect();
        const visibility = Math.max(0, Math.min(1, (innerHeight - rect.top) / (innerHeight + rect.height)));
        const lightX = -38 + visibility * 176 + ((scroll * 0.012 + index * 11) % 12);
        const values = {
          "--reflect-x": `${lightX.toFixed(2)}%`,
          "--reflect-opacity": (0.34 + speed * 0.34).toFixed(3),
          "--reflect-angle": `${(106 + Math.max(-1, Math.min(1, Number(velocity) || 0)) * 12).toFixed(2)}deg`
        };
        [target, reflectiveOverlays[index]].forEach(layer => {
          if (!layer) return;
          Object.entries(values).forEach(([property, value]) => layer.style.setProperty(property, value));
        });
      });
    }
    updateReflectiveLighting(scrollY);

    window.CoreCultureMotion = { lenis, gsap, ScrollTrigger };
    const onTick = time => lenis.raf(time * 1000);
    gsap.ticker.add(onTick);
    gsap.ticker.lagSmoothing(0);

    const progressTo = gsap.quickTo(nav || root, "--page-progress", {
      duration: 0.18,
      ease: "power1.out"
    });
    lenis.on("scroll", state => {
      setHeader(state.scroll);
      progressTo(state.limit > 0 ? state.scroll / state.limit : 0);
      updateReflectiveLighting(state.scroll, state.velocity);
      ScrollTrigger.update();
    });

    const cinematicVeils = [];
    const cinematicSections = ["#plan", "#club", "#amenities", "#recovery", "#schedule", "#memberships", "#book"];
    cinematicSections.forEach((selector, index) => {
      const section = $(selector);
      if (!section) return;
      section.classList.add("cinematic-section");
      const veil = document.createElement("div");
      veil.className = "cinematic-veil";
      veil.setAttribute("aria-hidden", "true");
      veil.style.setProperty("--veil-color", getComputedStyle(section).backgroundColor || "#0b0d0c");
      veil.style.transformOrigin = index % 2 ? "left center" : "right center";
      section.prepend(veil);
      cinematicVeils.push(veil);
    });

    const media = gsap.matchMedia();
    const context = gsap.context(() => {
      const editorialEase = "power3.out";
      const hero = gsap.timeline({ defaults: { ease: editorialEase } });
      hero
        .fromTo(".hero-copy-panel > .eyebrow", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.7 }, 0.05)
        .fromTo("#hero-title > span:not(.reflective-type-overlay), #hero-title > em",
          { autoAlpha: 0, yPercent: 105, rotate: 2, clipPath: "inset(100% 0 0)" },
          { autoAlpha: 1, yPercent: 0, rotate: 0, clipPath: "inset(0% 0 0)", duration: 0.9, stagger: 0.08 }, 0.1)
        .fromTo(".hero-copy", { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.7 }, 0.32)
        .fromTo(".hero-actions", { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.7 }, 0.4)
        .fromTo(".hero-media", { autoAlpha: 0, clipPath: "inset(4% 5% 4% 0)" }, { autoAlpha: 1, clipPath: "inset(0% 0% 0% 0%)", duration: 1.05 }, 0.08)
        .fromTo(".hero-media img", { scale: 1.13, filter: "saturate(.72) contrast(1.14) brightness(.88)" }, { scale: 1.045, filter: "saturate(.98) contrast(1.1) brightness(.94)", duration: 1.3 }, 0.08)
        .fromTo(".hero-media-meta, .hero-media figcaption, .first-route", { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.7, stagger: 0.08 }, 0.5);

      gsap.to(".hero-copy-panel", {
        y: -18,
        opacity: 0.9,
        ease: "none",
        scrollTrigger: { trigger: "#top", start: "top top", end: "bottom top", scrub: 0.8 }
      });

      gsap.to(".hero-media img", {
        yPercent: 7,
        scale: 1.095,
        filter: "saturate(.72) contrast(1.18) brightness(.72)",
        ease: "none",
        scrollTrigger: { trigger: ".hero-media", start: "top top+=72", end: "bottom top", scrub: 1 }
      });

      gsap.to("#hero-title > span:first-child", {
        xPercent: -7,
        ease: "none",
        scrollTrigger: { trigger: "#top", start: "top top", end: "bottom top", scrub: 1 }
      });
      gsap.to("#hero-title > span:nth-child(2), #hero-title > em", {
        xPercent: 5,
        ease: "none",
        scrollTrigger: { trigger: "#top", start: "top top", end: "bottom top", scrub: 1.1 }
      });
      gsap.to(".first-route", {
        y: -34,
        autoAlpha: 0.35,
        ease: "none",
        scrollTrigger: { trigger: "#top", start: "55% top", end: "bottom top", scrub: 0.9 }
      });

      function revealGroup(selector, options = {}) {
        const elements = $$(selector);
        if (!elements.length) return;
        elements.forEach(element => element.classList.add("motion-reveal", "is-visible"));
        gsap.fromTo(elements,
          {
            autoAlpha: 0,
            y: options.y ?? 28,
            rotate: options.rotate ?? 0,
            scale: options.scale ?? 1
          },
          {
            autoAlpha: 1,
            y: 0,
            rotate: 0,
            scale: 1,
            duration: options.duration ?? 0.78,
            stagger: options.stagger ?? 0.07,
            ease: editorialEase,
            clearProps: "opacity,visibility,transform",
            scrollTrigger: {
              trigger: options.trigger || elements[0].parentElement,
              start: options.start || "top 84%",
              once: true
            }
          });
      }

      revealGroup(".plan-intro > *", { trigger: ".plan-intro" });
      revealGroup(".story-heading > *", { trigger: ".story-heading" });
      revealGroup(".story-principles article", { trigger: ".story-principles", stagger: 0.1 });
      revealGroup(".spaces-section .section-heading > div:first-child > *", { trigger: ".spaces-section .section-heading" });
      revealGroup(".space-card", { trigger: "#spaceTrack", stagger: 0.075, start: "top 90%", y: 64, rotate: 1.4, scale: 0.96, duration: 1.05 });
      revealGroup(".recovery-copy > *", { trigger: ".recovery-copy" });
      revealGroup(".schedule-section .section-heading > div:first-child > *", { trigger: ".schedule-section .section-heading" });
      revealGroup(".membership-layout > div:first-child > *", { trigger: ".membership-layout" });
      revealGroup(".plans-grid > *", { trigger: ".plans-grid", stagger: 0.09, y: 42, scale: 0.975, duration: 0.9 });
      revealGroup(".visit-content > .eyebrow, .visit-content > h2, .visit-content > .visit-lede, .visit-content > form", { trigger: ".visit-content" });
      revealGroup(".contact-strip > *", { trigger: ".contact-strip" });
      revealGroup(".footer-top > *, .footer-bottom > *", { trigger: ".site-footer", start: "top 90%" });
      [
        ".plan-model-panel",
        ".spaces-section .heading-aside",
        ".space-ledger",
        ".schedule-section .heading-aside",
        ".next-session",
        ".timetable",
        ".membership-layout > div:last-child"
      ].forEach(selector => revealGroup(selector, { trigger: selector, stagger: 0 }));

      $$(".story-image, .recovery-visual, .visit-image").forEach(figure => {
        figure.classList.add("motion-reveal", "motion-image", "is-visible");
        const image = $("img", figure);
        const timeline = gsap.timeline({
          scrollTrigger: { trigger: figure, start: "top 88%", once: true }
        });
        timeline
          .fromTo(figure, { autoAlpha: 0, y: 18, clipPath: "inset(7% 0 7% 0)" }, { autoAlpha: 1, y: 0, clipPath: "inset(0% 0% 0% 0%)", duration: 0.95, ease: editorialEase })
          .fromTo(image, { scale: 1.12 }, { scale: 1.055, duration: 1.15, ease: editorialEase }, 0);
        gsap.fromTo(image, { yPercent: -3 }, {
          yPercent: 5,
          ease: "none",
          scrollTrigger: { trigger: figure, start: "top bottom", end: "bottom top", scrub: 1.15 }
        });
        gsap.fromTo(figure, { "--cinema-light": 0.62 }, {
          "--cinema-light": 0.08,
          ease: "none",
          scrollTrigger: { trigger: figure, start: "top 95%", end: "center 42%", scrub: 1.1 }
        });
      });

      cinematicVeils.forEach(veil => {
        gsap.fromTo(veil, { scaleX: 1 }, {
          scaleX: 0,
          duration: 1.25,
          ease: "power4.inOut",
          scrollTrigger: { trigger: veil.parentElement, start: "top 92%", once: true }
        });
      });

      $$("main section h2").forEach((heading, index) => {
        const distance = index % 2 ? -2.8 : 2.8;
        gsap.fromTo(heading, { xPercent: -distance }, {
          xPercent: distance,
          ease: "none",
          scrollTrigger: { trigger: heading.closest("section"), start: "top bottom", end: "bottom top", scrub: 1.7 }
        });
      });

      const bandTrack = $(".kinetic-track");
      if (bandTrack) {
        gsap.fromTo(bandTrack, { xPercent: 0 }, {
          xPercent: -16,
          ease: "none",
          scrollTrigger: { trigger: ".kinetic-band", start: "top bottom", end: "bottom top", scrub: 0.75 }
        });
      }

      gsap.fromTo(".kinetic-band", { scale: 0.985 }, {
        scale: 1.015,
        ease: "none",
        scrollTrigger: { trigger: ".kinetic-band", start: "top bottom", end: "bottom top", scrub: 1 }
      });

      media.add("(min-width: 781px)", () => {
        gsap.fromTo(".plan-model-panel", { clipPath: "inset(0 9% 0 0)", x: 36 }, {
          clipPath: "inset(0% 0% 0% 0%)",
          x: 0,
          ease: "none",
          scrollTrigger: { trigger: "#plan", start: "top 82%", end: "top 22%", scrub: 1.15 }
        });
        gsap.fromTo(".story-image", { xPercent: 4 }, {
          xPercent: -2,
          ease: "none",
          scrollTrigger: { trigger: "#club", start: "top bottom", end: "bottom top", scrub: 1.35 }
        });
        gsap.fromTo(".recovery-copy", { x: -28 }, {
          x: 18,
          ease: "none",
          scrollTrigger: { trigger: "#recovery", start: "top bottom", end: "bottom top", scrub: 1.4 }
        });
        gsap.fromTo(".schedule-layout", { y: 42 }, {
          y: -18,
          ease: "none",
          scrollTrigger: { trigger: "#schedule", start: "top bottom", end: "bottom top", scrub: 1.6 }
        });
      });

      gsap.fromTo(".footer-wordmark", { y: 40 }, {
        y: 0,
        ease: "none",
        scrollTrigger: { trigger: ".site-footer", start: "top bottom", end: "bottom bottom", scrub: 0.8 }
      });
    });

    function scrollToHash(hash, immediate = false) {
      if (!hash || hash === "#" || hash.startsWith("#room=") || hash === "#directory") return false;
      const target = document.querySelector(hash);
      if (!target) return false;
      lenis.scrollTo(target, { offset: 0, duration: immediate ? 0 : 1.12, immediate });
      return true;
    }

    listen(document, "click", event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest('a[href^="#"]:not(.skip)');
      if (!link) return;
      const hash = link.getAttribute("href");
      if (!hash || hash === "#" || hash.startsWith("#room=") || hash === "#directory" || !document.querySelector(hash)) return;
      event.preventDefault();
      if (location.hash !== hash) history.pushState(null, "", hash);
      if (lenis.isStopped) requestAnimationFrame(() => scrollToHash(hash));
      else scrollToHash(hash);
    });

    listen(window, "hashchange", () => requestAnimationFrame(() => scrollToHash(location.hash)));
    listen(window, "pageshow", () => {
      lenis.resize();
      ScrollTrigger.refresh();
    });
    listen(document, "visibilitychange", () => document.hidden ? lenis.stop() : lenis.start());
    listen(document, "focusin", event => {
      const element = event.target.closest(".motion-reveal");
      if (element) gsap.set(element, { autoAlpha: 1, y: 0, clipPath: "inset(0% 0% 0% 0%)" });
    });

    const modalObserver = new MutationObserver(() => {
      if (document.body.classList.contains("modal-open")) lenis.stop();
      else if (!document.hidden) lenis.start();
    });
    modalObserver.observe(document.body, { attributes: true, attributeFilter: ["class"] });

    const resizeObserver = new ResizeObserver(() => {
      lenis.resize();
      ScrollTrigger.refresh();
    });
    resizeObserver.observe($("main") || document.body);

    const refresh = () => requestAnimationFrame(() => ScrollTrigger.refresh());
    document.fonts.ready.then(refresh);
    $$('#main img[loading="lazy"]').forEach(image => {
      if (!image.complete) listen(image, "load", refresh, { once: true });
    });
    requestAnimationFrame(() => {
      ScrollTrigger.refresh();
      if (location.hash && !location.hash.includes("=")) scrollToHash(location.hash, true);
    });

    teardown = () => {
      events.abort();
      modalObserver.disconnect();
      resizeObserver.disconnect();
      media.revert();
      context.revert();
      gsap.ticker.remove(onTick);
      lenis.destroy();
      delete window.CoreCultureMotion;
      reflectiveOverlays.forEach(overlay => overlay.remove());
      reflectiveTargets.forEach(target => {
        target.classList.remove("reflective-type-target");
        target.style.removeProperty("--reflect-x");
        target.style.removeProperty("--reflect-opacity");
        target.style.removeProperty("--reflect-angle");
      });
      cinematicVeils.forEach(veil => veil.remove());
      cinematicSections.forEach(selector => $(selector)?.classList.remove("cinematic-section"));
      showEverything();
      root.classList.remove("gsap-ready", "lenis", "lenis-smooth", "lenis-scrolling", "lenis-stopped");
    };
  }

  reducedQuery.addEventListener("change", configure);
  configure();
})();
