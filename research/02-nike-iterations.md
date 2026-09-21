# 02-nike — build log & iteration ledger

## Plan — Nike x Core Culture

**Concept: "CAMPAIGN SEASON"** — Core Culture run like a sports brand's campaign season: white chrome, black type, and a stack of full-bleed campaign posters, each carried by ONE giant condensed uppercase headline (Anton, the Nike-Futura-energy stand-in) with quiet Inter UI voice beneath. The only rounded object on the page is the pill button. All saturation lives inside the photography; the UI is pure black/white/#f5f5f5/#707072. Motion = carousels and hovers only (zero scroll animation — stillness between posters, exactly like the live homepage).

**Signature rules transferred (research/02-nike.md §Signature Characteristics):**
1. Giant condensed uppercase campaign headlines — Anton, clamp(44px→96px), leading 0.92, tracking −0.5px, white over photo; reserved for posters + one centered wordmark finale ("THE CULTURE").
2. Pill buttons as the only radius — white-over-image / black-on-white variants, `background 0.2s` hover, one pill per poster.
3. Full-bleed poster bands — bottom-left caption stacks (eyebrow → sentence headline → pill); gapless 2-up Featured; left-aligned 24px/500 quiet section heads between bands.
4. Black-and-white chrome discipline — white UI, #111 type, #f5f5f5 flat fills, #707072 secondary gray; color only inside photos.
5. Carousel culture — hero carousel (dots + pause + prev/next circles bottom-right), horizontal class carousel with circular chevrons + peeking card.
6. Product-tile anatomy → class tiles on #f5f5f5: 1:1 image, bold name, gray discipline, "60 MIN · ALL LEVELS" meta.
7. Centered giant wordmark finale over a tiny labeled thumbnail index → "THE CULTURE" + 8 amenity thumbs; then cream #ece8e1 campaign band ("BECOME PART OF THE CULTURE.") with membership card device (Nike app-band analog).

**Section flow:** promo bar → header (utility row scrolls away; white sticky main bar; swoosh-slot wordmark; centered nav; pill search opening live-filter overlay) → 72vh hero carousel ×3 campaigns (dance / sled / streak) → Featured 2-up gapless (machine | ice) → Trending 3-up (pop-art nights / frost AC / parking) → "This week on the floor" class carousel ×6 on #f5f5f5 → "Train by discipline" 4-up caption cards → "THE CULTURE" wordmark + amenity thumb index ×8 → cream membership band with dialog-backed "Join now" → compact hairline footer.

**Nav model:** utility row (Hours · Membership · Sign in) scrolls away; main bar sticky white — never transparent; centered 5-item nav; pill search right opening a full-width overlay that live-filters an in-page index (classes + sections), Enter jumps; burger under 900px opens full-screen white overlay with Anton links; Esc closes; body scroll locks.

**Motion system:** hero 6s auto-advance crossfade with working pause (aria-pressed), dots, circular chevrons; carousels = native horizontal scroll + smooth + chevron buttons; hovers 0.2s; `prefers-reduced-motion`: autoplay off, instant crossfade, `scroll-behavior:auto`. No scroll-triggered animation anywhere.

**Image treatment:** 27 fresh `w302-*` crops, every one cut from verified type-free zones of assets/slide-N.jpg (baked-header line sits at y≈20–100 — all crops start y≥100; per-slide type blocks mapped with grid overlays in /tmp/grids/). Heroes wides (dance 1080×640, sled 1080×480, streak 1080×430); featured halves (machine column 410×1190, ice band); trending 4:5 (pop / frost / parking); class tiles 1:1 (ice / dance / machine / sled / streak / frost); discipline 3:4 (weights / dance / condition / recover); parking band; 8 amenity thumbs.

**What makes it unmistakably Core Culture:** campaign copy in the house voice ("STRONG IS A SKILL.", "SWEAT IS ONLY THE BEGINNING.", "PARKING. FINALLY."), TRAIN/MOVE/RECOVER/CONNECT as nav and discipline posters, real amenities as THE CULTURE index (ice bath, steam, Netflix treadmills, industrial AC, lounge desks, parking, culture nights, strength floor), and membership as the transactional close. Nike's chrome grammar without a single Nike asset or slogan.

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8102/02-nike/)

## Iteration 1 — launch audit: 2px horizontal overflow (`.track-ctrl.prev{left:-2px}` at full-width wrap) → `6px`; favicon 404 → inline SVG data-icon; console otherwise clean; 4984px height at 1440.

## Iteration 2 — baked-type hunt: first renders showed the slide header line ("…| TRAINING CLUB") on feat-ice, trend-pop, trend-park. Grid overlays (/tmp/grids) proved the baked line reaches ~y100, not y50 → re-cut 15 crops with y≥110 (y≥120 for slide-9); verified every crop via a top-90px danger-zone strip sheet (all 26 clean).

## Iteration 3 — copy conventions: dropped invented ৳ price + phone number (house voice keeps commerce vague); membership card gained a "ONE PASS / EVERY FLOOR" middle so the device isn't an empty slab; verified in render.

## Iteration 4 — interaction pass: nav "Classes" pointed at a section with **no id** (dead link) → added `id="classes"`. Re-verified: search live-filter ("ice"→Ice bath, Enter jumps to #recover, Esc closes + focus restore), class chevrons scroll 434px with disabled end-states, pill hover white→#dcdcdc in 0.2s, join dialog rejects invalid input and personalizes confirmation, zero console errors.

## Iteration 5 — hero slide 2+3 imagery: streak hero showed baked italic "One less excuse." (line actually ends ~y905, not y840) → re-cut whole streak family to y915 (hero/amen/class); sled hero read as 90% dark ceiling (composition dead) → re-cut as right-column close-up; that caught the baked serif "G" of "TRAINING" at its left edge → final cut at x690. All three hero slides re-verified on pixels.

## Iteration 6 — mobile recomposition (390×844): verified hero stacks (3-line headline, stacked pills, dots+controls), trending 1-col, class carousel peek + chevrons, 2-col amenity grid, join band + card, stacked footer; burger menu opens/navigates/closes and scrolls to #recover; zero overflow, zero errors.

## Iteration 7 — a11y structure: three H1s (one per slide) → single visually-hidden H1 + three H2 campaign headlines (`.slide h2.campaign` selectors, 96px preserved); 8px carousel dots → 22px hit area (radial-gradient keeps 8px visual); verified single h1 in DOM, 22×22 dot rects, Anton applied, dots still render correctly.

## Iteration 8 — multi-viewport: 1920 (sections capped at 1440, zero overflow), 1024 (nav fits, 3-up holds), 768 (2-up trending) — all clean, screenshots verified.

## Iteration 9 — performance: 1.3MB total imagery, 25/26 lazy, 1 passive scroll listener, no scroll-triggered animation; all 26 `<img>` given explicit width/height (layout inside aspect-ratio boxes → zero CLS); injected via script and re-verified count in DOM.

## Iteration 10 — micro-detail pass vs live measurements: gapped grids 24→**64px** side margins (Nike's measured 64px), class carousel 24→**48px**, section-head rhythm 64→**88px** top padding, culture/join/footer 24→48px side padding, class-card name weight 700→**500** (Nike Medium). Re-rendered: whitespace now breathes like the reference.

## Iteration 11 — final QA battery: 0 overflow + 0 console errors at 1440/1024/768/390; hero next works, pause *stays* paused (timer dead), all six anchors exist and nav click scrolls; reduced-motion disables autoplay (slide 1 still current after 3.3s). Hub updated ("Nike — Campaign Season").

---

## Final fidelity test — live nike.com/nike.in (fresh captures /tmp/nike-fin-*.png) vs /02-nike/

- **Hierarchy philosophy — match.** Both open with a full-bleed campaign hero: centered-bottom stack (eyebrow → giant condensed uppercase headline → one-line subline → pill CTA), dots bottom-center, pause + prev/next circles bottom-right; white header with utility row that scrolls away and a centered nav; promo bar above. Live re-measured: 72px/0.9/500 Futura caps over 16px Helvetica; mine: 96px/0.92 Anton caps over 16px Inter.
- **Pacing — match.** One message per band; quiet left-aligned 24px section heads alone in white air between poster groups; gapless 2-up Featured; gapped 3-up Trending; gray-tile carousel with circular chevrons and a peeking card; centered giant wordmark finale (SPOTLIGHT ↔ THE CULTURE) over a tiny labeled thumbnail index; cream campaign band before a hairline footer (app band ↔ membership band).
- **Chrome discipline — match.** Pure white UI, #111 type, #f5f5f5 flat tiles, #707072 secondary, one #ece8e1 band; zero borders/shadows on cards; pills are the only radius; `background 0.2s` hovers.
- **Still Core Culture, never Nike — confirmed.** Sled/ice/neon-dance/streak/parking photography, TRAIN·PUSH·MOVE·RECOVER discipline posters, class tiles with "60 MIN · ALL LEVELS" instead of prices, amenities as THE CULTURE index (ice bath, steam, Netflix treadmills, industrial AC, lounge desks, parking, culture nights, strength floor), membership dialog as the transactional close, house voice throughout ("STRONG IS A SKILL.", "PARKING. FINALLY."). No Nike marks, slogans, or assets.

## Final QA state (all executed this session)
- Overflow: 0px at 1440 / 1024 / 768 / 390. Console: zero errors in every run.
- Reduced motion: autoplay off, transitions minimal, smooth-scroll off. Keyboard: skip link, search open/filter/Enter/Esc with focus restore, operable dots (22px) and chevrons.
- Images: 26 crops, all visually verified type-free (three recut rounds); lazy + async below fold; explicit dimensions; ~1.3MB total.
- A11y: single hidden H1 → H2 sections → H3 cards; alt text on all images; aria-pressed pause; aria-current dots; labeled icon buttons; dialog semantics native.
