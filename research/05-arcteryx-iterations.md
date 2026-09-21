# 05-arcteryx — build log & iteration ledger

## Plan — Arc'teryx x Core Culture

**Concept: "THE OUTPOST"** — Core Culture as an expedition-grade training outpost. Black utility bar, white rounded header card floating over a dark documentary hero (scroll-away, not sticky), centered letterspaced serif-caps campaign voice (Marcellus, uppercase, +0.32em tracking, clamp 26→34px — small size, huge authority), outline button pairs and underlined text links (never filled on imagery), caption stacks in the upper third of tiles, a value-props trio with text marks, and a black "LEAVE IT STRONGER" newsletter close. UI stays white/black; color arrives only inside the photography. Inter for UI voice.

**Structure:** black utility bar (THE OUTPOST / PROGRAMMES / FIELD NOTES + center promo + Find the club) → white rounded header card (logo, centered nav, icons; absolute, scrolls away) → 88vh documentary hero (parking-at-dusk) with monogram CC, "WINTER INTAKE. THE FLOOR OPENS EARLY.", outline pair "Book the floor / Book the studio", underlined "See the timetable" → 2-up tiles (FIELD NOTES 047 / COLD PROTOCOL) → 3-up categories (STRENGTH / MOVEMENT / RECOVERY) → 2-up action tiles (TRAIN IN THE DARK / ARRIVAL, SOLVED) → value trio (COLD·WARM·QUIET protocol / 05:00–23:00 hours / FOUNDRY DISTRICT) → black footer ("LEAVE IT STRONGER", 4 columns, functional newsletter, socials/legal).

**Motion:** hover underlines only; no scroll animation (reference is stillness + gravity). Reduced motion: nothing to disable except smooth scroll.

**Images:** 8 fresh `w305-*` crops in verified clean zones (tile-notes recut from (0,110,540,1290) — caught slide-7's "LOUNGE" block at x415+ — to the clean bottom field (60,790,900,1440) with the desk subject).

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8105/05-arcteryx/)

## Iteration 1 — launch: hero's negative margin (-116px) pulled the dark image up OVER the black utility bar (bar invisible at load) → hero re-sized to start below the utility bar (`height:calc(min(92vh,880px) − 36px)`), letting the white header card float over the hero top naturally (absolute at top:52px). Verified: bar visible, card floating, stack centered.

## Iteration 2 — crop audit: w305-tile-notes caught slide-7's baked "LO…/Work-lif…" block (type at x415-1020/y400-780; crop had overlapped x415-540) → recut to the clean bottom field (60,790,900,1440) keeping the desk subject. Verified on contact sheet + render.

## Iteration 3 — value-mark wrap: "COLD · WARM · QUIET" broke awkwardly onto two lines → `white-space:nowrap` + size 19→17px. Verified single line, still balanced with the other two marks.

## Iteration 4 — heading structure: two H1s (hidden intro + hero headline) → hero headline is the single H1 (Marcellus 34px uppercase, +0.32em), hidden intro removed. Verified h1 count = 1.

## Iteration 5 — interaction battery: header card is absolute and scrolls away (bottom < 0 past hero ✓); search ("cold"→Cold protocol, Enter → #recover, Esc restore); outline button hover fills white with black text (rgba(0,0,0,.08)→#fff); newsletter rejects "bad" and accepts a valid email ("The programme lands every Sunday."); zero console errors.

## Iteration 6 — a11y: alt on all images; dims 8/8 (zero CLS); skip link; focus-visible rings (white on dark sections); icon buttons labelled; native search-overlay Esc semantics.

## Iteration 7 — viewports: 1920 / 1024 / 768 / 390 all 0px overflow; duo collapses to 1-col ≤820px; cats 3→1; footer columns 4→2→1.

## Iteration 8 — mobile: burger overlay opens (Marcellus letterspaced links), navigates to #cats, closes, scrolls (scrollY>300 verified); utility bar condenses (center promo + region only at ≤560px).

## Iteration 9 — category captions verified on pixels: STRENGTH / MOVEMENT / RECOVERY serif-caps + underlined "Explore…" links match the reference's 3-up grammar; hover zoom on card images 1.035 (neutralized in reduced motion).

## Iteration 10 — final fidelity test vs live arcteryx.com (/tmp/arc-shots/00-hero.png, 03, 06, 08): black utility bar with center promo ✓; white rounded header card floating over a documentary hero ✓; centered letterspaced uppercase campaign headline + outline button pair + underlined text link ✓; 2-up tiles with upper-third caption stacks ✓; 3-up categories with caps captions ✓; 2-up action tiles ("TRAIN IN THE DARK" / "ARRIVAL, SOLVED") ✓; value trio with text marks ✓; black close with serif statement ("LEAVE IT STRONGER" ↔ "LEAVE IT BETTER") + newsletter ✓. Voice/imagery 100% Core Culture. Hub updated ("Arc'teryx — The Outpost").

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors in every run; single H1 (34px Marcellus caps); alt 8/8; dims 8/8; reduced-motion: zoom/transition neutralized; keyboard: skip link, search Esc/Enter with focus restore, labelled icon buttons; newsletter validation functional.
