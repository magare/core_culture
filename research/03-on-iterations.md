# 03-on — build log & iteration ledger

## Plan — On Running x Core Culture

**Concept: "MOVEMENT, ENGINEERED"** — Core Culture read through On's Swiss-engineering friendliness: an all-white page, everything sentence case, huge bold tight-tracked heads, light-gray product fields with deadpan gray descriptors, rounded pill buttons (white-on-image / black-on-white, arrows on text actions), arrow-glyph carousel controls with a hairline progress line, a giant interactive discipline index that swaps one image, black sentence cards interleaved with imagery, and a mission close. Color only inside photography. Inter (400/500/700) stands in for On's grotesk. Deliberately NOT the Nike page: no uppercase campaign voice, no circular controls, no poster veils everywhere — friendly precision instead of loudness.

**Signature rules transferred (research/03-on.md):**
1. Sentence-case bold everything — heads clamp(36→52px)/700/−0.02em; captions 18-20px/700 white bottom-left on tiles.
2. Pill buttons with arrows — `.pill-white` on imagery, `.pill-black` + `→` on white.
3. Light-gray `#f0f0f0` object fields — class cards: image field, 16/700 name, gray descriptor line.
4. Arrow-glyph carousel controls + hairline progress line bound to scrollLeft.
5. Giant interactive index — Strength / Conditioning / Dance / Recovery / Community / Arrival as clamp(34→54px)/700 lines; hover/click/arrow-keys swap the right-hand image with a crossfade.
6. Black sentence cards between imagery — "Powered by industrial air.", "We believe recovery is training."
7. Mission close — collage strip + "Our mission" + "Training is only part of the culture." + "Read more →"; light footer with newsletter + region line.

**Section flow:** transparent header → white sticky on scroll (wordmark, centered nav Train/Move/Recover/Explore, search overlay + icons) → 86vh full-bleed hero, bottom-left headline + white pill → "The floor" giant head + 3-up tall caption tiles (Weights/Studio/Engine) → discipline index (interactive) → "On the timetable" class carousel (6 tiles, gray fields, ← → + progress line) → "Stories that move" 4-up alternating image/black-sentence cards → mission collage + statement + pill → light footer (newsletter, columns, region line, legal+social).

**Motion:** index crossfade + carousel smooth scroll + progress line (rAF on scroll event, passive); tile hover subtle image scale 1.04 (off in reduced motion); header background swap on scroll; zero scroll-triggered reveals.

**Images:** 23 fresh `w303-*` crops, all in verified type-free zones (slide-7 gridded for the first time — its "LOUNGE" block sits at x415-1020/y400-780, man-at-desk y890-1230; two initial crops recut after contact-sheet verification, plus ix-strength recut to (560,150,1080,700) for a stronger athlete read).

**Unmistakably Core Culture:** sled/ice/dance/desk/parking imagery, deadpan house voice ("For engines, and the days after leg day.", "Cold, then warm, then quiet."), real amenities (Netflix treadmills, industrial AC, ice bath + steam, lounge desks, parking) as story cards and index entries, membership dialog as the close.

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8103/03-on/)

## Iteration 1 — launch audit: icon buttons rendered dark over the dark transparent-header hero → white in `header.site:not(.solid)` state; nav "Recover" pointed at a floor tile (wrong destination) → anchor moved to the Recovery index `<li>` with **real behavior**: navigating to `#recover` auto-selects the Recovery tab; class-sled tile duplicated the index's Strength imagery → recut to a distinct framing (660,600,1060,1000) + dims updated. Verified on pixels.

## Iteration 2 — story card audit: the red culture card caught yellow descenders of slide-1's baked "FUN?" (type reaches ~y850, mapped to y820) → recut to (100,880,680,1150); verified clean; width/height attrs updated to 580×270.

## Iteration 3 — interaction battery: discipline index (click selects + crossfades + caption swap; hover selects; ArrowUp/Down/Left/Right/Home/End move selection with roving tabindex), `#recover` hash auto-select, class carousel (progress 25%→54%, prev enables at scroll>0), header transparent↔solid swap at hero edge, search ("cold"→Cold Start, Enter, Esc), newsletter (rejects "nope", accepts valid with confirmation), join dialog (validates, personalizes) — all pass, zero console errors.

## Iteration 4 — mobile recomposition (390×844): hero stacks cleanly with white icons; index media reorders above the list (`order:-1`); giant discipline lines wrap at 32px; class carousel scrolls with peek; stories/collage stack 1-col; zero overflow.

## Iteration 5 — a11y structure: single hidden H1 + six H2s (verified counts), alt on all images, skip link verified first in tab order (Tab 1 → `a.skip`, Tab 2 → wordmark — earlier "story" reading was stale focus from a prior interaction, re-verified clean).

## Iteration 6 — performance: 20/20 imgs given explicit width/height (zero-CLS; layout governed by aspect-ratio boxes); all below-fold lazy; no scroll-triggered animation; two passive listeners; zero dependencies.

## Iteration 7 — reduced motion: transitions neutralized (tiles/carousel/pills), index still fully keyboard-operable with instant swaps (aria-selected verified after ArrowDown presses).

## Iteration 8 — multi-viewport: 1920 / 1024 / 768 / 390 all 0px horizontal overflow; index collapses to single column with media-first at ≤1100px.

## Iteration 9 — micro-detail pass: index count superscripts normalized ("14 classes" → "14" to match the numeric 9/11/7/6 pattern); mobile menu verified (opens, big links navigate + close + scroll).

## Iteration 10 — final QA battery + fidelity test: 0 overflow + 0 console errors at 1440/1024/768/390. Live on.com (fresh capture /tmp/on-fin-index.png) vs /03-on/: giant sentence-case bold index lines with swapped image ↔ Running/Marathon list; gray object fields with name + deadpan descriptor ↔ class tiles; arrow-glyph controls + hairline progress ↔ carousel; black sentence cards ↔ "Powered by industrial air."; mission close + light newsletter footer ↔ Our culture + footer. Same friendly-precision grammar; subject, voice and imagery 100% Core Culture. Hub updated ("On — Movement, Engineered").

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors in every run; reduced-motion fallbacks verified; keyboard: skip link, search focus/Esc restore, index roving-tabindex tabs, carousel buttons; dialogs native `<dialog>`; 23 crops all visually verified type-free (3 recut); ~1.1MB imagery, all lazy below fold, all dimensioned.
