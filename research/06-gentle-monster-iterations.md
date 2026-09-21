# 06-gentle-monster — build log & iteration ledger

## Plan — Gentle Monster x Core Culture

**Concept: "ABSURD ROOM"** — Core Culture exhibited like a Gentle Monster collection: a transparent header with the centered serif logotype, a 3-scene campaign hero (dancer/neon, streaks, parking-at-dusk) with a small Cormorant-caps collection title, ghost pill pairs and thin progress dashes; flat `#f3f4f6` exhibition fields where sessions sit as objects with tiny name/meta captions ("Cold 01(CS) · Ice bath · 20 min drop-in") and underlined "ADD TO PROGRAMME" utilities; a two-panel "Room 07 — the field office" feature (desk-in-field photograph + withheld-information copy); a "Best: the night room" carousel; and a minimal single-row footer. No accent color, no cards, no shadows — objects on gray, film does the talking.

**Signature rules transferred:** serif caps campaign title (small, letterspaced); ghost pill pair; hero progress dashes; flat gray object fields with museum captions; transparent centered-logotype header; "LATEST:/BEST:" + underlined MORE heads; minimal footer. Zero scroll animation (crossfade carousel + hovers only).

**Images:** 12 fresh `w306-*` crops, all verified type-free on the contact sheet (known-clean zones).

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8106/06-gentle-monster/)

## Iteration 1 — launch broke hard: the mobile-menu CSS block (`.mnav`/`.mnav.open`) was MISSING from the stylesheet (skipped during authoring), so the menu rendered as an open static block at desktop and pushed the whole page down. Diagnosed via computed `display:block` + brace-balance + grep → added the full `.mnav` rule set. Re-render: menu hidden, hero correct.

## Iteration 2 — heading structure: three H1s (one per hero scene) → single hidden H1 + three `.stitle` H2s (CSS selector updated, 38px preserved incl. the ≤560px rule which previously targeted `.hero h1`). Verified: h1 count 1, title renders 38px.

## Iteration 3 — interaction battery: dashes jump scenes + aria-current; autoplay wraps past scene 3 (verified scene 3 exits after 7s); header flips solid after the hero; search ("sled"→Engine 02(ER), Enter → #latest, Esc restore); every "ADD TO PROGRAMME" opens the join dialog; validation rejects bad input, success personalizes ("Held a spot for Rafi. First session is free."). Zero console errors.

## Iteration 4 — a11y/dims: alt 12/12; width/height 12/12 (zero CLS); skip link; dashes expose aria-current; dialog native; focus rings white on dark scenes.

## Iteration 5 — viewports: 1920 / 1024 / 768 / 390 all 0px overflow; plates 4→2→1; room feature stacks with image-first at ≤1000px.

## Iteration 6 — mobile: burger overlay (Cormorant letterspaced links) opens/navigates/closes + scrolls to #room (verified scrollY>300).

## Iteration 7 — reduced motion: autoplay disabled (slide 1 still current after 7.6s), crossfades instant, hover zooms neutralized.

## Iteration 8 — hover language: ghost pills fill white with black text (transparent→#fff, 0.25s); object plates zoom 1.03; MORE/add links dim — matching the reference's quiet utilities.

## Iteration 9 — section verification on pixels: gray "Latest: the cold room arrival" field with 4 object plates + MORE ✓; "Room 07 — the field office" split feature ✓; "Best: the night room" carousel with peeking card ✓; minimal single-row footer ("Country : Foundry District · © 2026 Core Culture") ✓.

## Iteration 10 — final fidelity vs live gentlemonster.com (/tmp/gm-shots/): surreal full-bleed campaign scenes with small serif title + ghost pills + dashes ↔ hero carousel; transparent centered serif logotype header ↔ same; gray exhibition fields with tiny object captions + underlined utilities ↔ LATEST/BEST fields; minimal footer ↔ single-row footer. Mysterious withheld-information tone kept ("View the room", "See what's inside"); all content unmistakably Core Culture (Cold 01(CS), Engine 02(ER), Neon 03(NG), Iron 04(IT), the field office). No GM marks, campaigns, or assets.

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors in every run; reduced-motion: autoplay off, transitions instant; keyboard: skip link, dashes buttons, search Esc/Enter + focus restore, native dialog; 12 crops type-free; all images dimensioned + lazy below fold; zero dependencies.
