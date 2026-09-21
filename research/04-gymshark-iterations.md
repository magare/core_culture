# 04-gymshark — build log & iteration ledger

## Plan — Gymshark x Core Culture

**Concept: "WE DO TRAIN"** — Core Culture as training-culture commerce: white page, near-black type, ONE green accent, everything square-cornered, and a bold slightly-condensed UPPERCASE display voice (Barlow Semi Condensed 700/800, ~0.94 leading) over a quiet Inter body. The commercial grammar is kept (promo bar, price-led cards, sale-style bands, tab chips, email capture, utilitarian footer) but the "price" is TIME — "WEIGHTS FROM 45 MIN", "ICE BATH FROM 20 MIN" — preserving the house no-currency rule. Green gradient statement bands carry the hero and the signup; small 17px/800 uppercase heads lead every band.

**Signature rules transferred (research/04-gymshark.md):**
1. Uppercase 800 condensed display at tight leading over tiny quiet body.
2. Radius 0 everywhere — buttons, chips, cards, badges, dialog.
3. One green accent (promo bar, card badges, email band, hero field).
4. Product cards on beige fields: green corner badge + "X FROM Y MIN" uppercase caption + gray sub-line.
5. 2-up full-bleed halves with centered uppercase captions + white square buttons (THE FLOOR / THE STUDIO; CULTURE NIGHTS / COLD START).
6. Square tab chips (MORNING / NIGHT) switching a 4-up card row — real tabs, keyboard operable.
7. Green gradient statement bands: hero + "FIRST SESSION'S ON US. WANT IN?" with underlined SIGN UP opening the join dialog.
8. SEO-style house block ("MORE THAN A GYM" → "TRAIN. MOVE. RECOVER. CONNECT.") and footer: columns, about tiles, payment chips, "© 2026 | Core Culture | Train. Move. Recover. Connect."

**Structure:** promo bar → sticky transparent header (left nav / centered logotype / icons; solid white after the hero) → green hero statement + 2-up halves → "THIS MONTH ON THE FLOOR" 4-up → "AROUND THE CLUB — INCLUDED" 4-up → "NEW THIS SEASON" gapless halves → "POPULAR RIGHT NOW" chips + card sets → green signup band → story block → footer.

**Motion:** hover-only (image scale 1.03–1.04, button dim, underline) — matching the reference's minimalism; no scroll animation. Reduced motion: transforms neutralized, tabs instant.

**Images:** 19 fresh `w304-*` crops, all verified type-free on the contact sheet (known-clean zones only).

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8104/04-gymshark/)

## Iteration 1 — launch audit: the fixed header COVERED the promo bar (logo overlapping promo text at load) → converted header to `position:sticky` so the promo scrolls away naturally. Verified promo visible above header at load, gone when scrolled.

## Iteration 2 — transparent-header state was white-on-white once the header sat above (not over) the hero → hero tucked under the header (`margin-top:-60px`, padding compensated to 188px) and the solid trigger re-tied to the hero's exit (`scrollY > heroBottom − 64`). Verified: white text over green at top, solid white bar with dark text after the hero.

## Iteration 3 — content audit: the "Steam + sauna" amenity card displayed the desk-in-field crop (image/label mismatch) → replaced with the streaks crop and relabeled "Netflix treadmills — OTTI platforms, headphones optional." Verified in render.

## Iteration 4 — real bug: `.row4{display:grid}` overrode the `hidden` attribute, so BOTH timetable sets rendered on load → added `.row4[hidden]{display:none}`. Verified fresh load shows only Morning; clicking NIGHT swaps sets (aria-selected moves, AM hides).

## Iteration 5 — interaction battery: chips (click + ArrowLeft/Right with roving tabindex), header transparent↔solid at the hero boundary, search ("ice"→Ice bath, Enter jumps, Esc restores focus), join dialog (validates, personalizes "Check your inbox, Rafi — your first session is on us."), square-button hover white→#e9e9e9 in 0.2s — all pass, zero console errors.

## Iteration 6 — a11y structure: single hidden H1 + seven H2s; alt on all images; skip link first tab; chips expose role=tablist/tab with aria-selected; dialog native.

## Iteration 7 — performance: 23/23 images given explicit width/height (zero CLS; aspect-ratio boxes govern layout); all below-fold lazy; zero dependencies; no scroll listeners; ~1.2MB imagery total.

## Iteration 8 — multi-viewport: 1920 / 1024 / 768 / 390 all 0px overflow; rows collapse 4→2→1; halves stack at ≤600px with adjusted caption/button offsets; mobile capture verified.

## Iteration 9 — reduced motion + mobile menu: hover transforms neutralized under `prefers-reduced-motion` (tabs still instant, verified by click); burger opens overlay, link navigates + closes + scrolls (scrollY > 400 verified).

## Iteration 10 — final QA + fidelity test: 0 overflow + 0 console errors at 1440/1024/768/390. Live gymshark.com captures (/tmp/gs-shots/) vs /04-gymshark/: green promo bar ✓, transparent header with centered logotype ✓, green gradient hero with centered uppercase statement ✓, 2-up tall halves with uppercase captions + white square buttons ✓, small uppercase section heads over 4-up badge cards with "FROM"-captions ✓, gapless NEW-IN halves ✓, square tab chips filtering a card row ✓, green email band with underlined SIGN UP ✓, uppercase mini-head story block ✓, columns+tiles+legal footer ✓. Voice and imagery 100% Core Culture ("Training is only part of the culture", "Train. Move. Recover. Connect."). Hub updated ("Gymshark — We Do Train").

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors in every run; reduced-motion verified; keyboard: skip link, chips (roving tabindex + arrows), search focus/Esc restore, native dialog; 19 crops type-free; all images dimensioned and lazy below fold.
