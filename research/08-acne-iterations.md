# 08-acne — build log & iteration ledger

## Plan — Acne Studios x Core Culture

**Concept: "GRAY ROOM"** — Core Culture through Acne's Scandinavian avant-garde: a monochrome page with a 12px uppercase micro-type system (Inter for Helvetica Now; IBM Plex Mono for meta), a centered sentence-case logotype, and a hero carrying the GIANT ghost logotype watermark across a darkened campaign image with a tiny eyebrow top-left and a single underlined utility bottom-left. Objects sit as cutouts on flat gray; a gapless 2-up "new this week"; a "discover more" 4-up of gray tiles with micro captions; a NEWS section mixing a large plain-type paragraph with two small cards; and the utilitarian footer with the huge gray EMAIL input, four tiny columns, and a bottom row ending "Training in Foundry District (English)". Zero radius, zero decoration, no accent color — except the reference's signature default-blue links in the footer.

**Structure:** sticky light header (nav left / logotype center / SEARCH HELP MEMBERSHIP 00 right) → ghost-watermark hero → gray object strip (The rack / The cold room / The studio / The sled) → "New this week" gapless 2-up → "Discover more" 4-up (Night training / Ice protocol / Arrival / Culture wall) → News (paragraph + 2 cards) → footer.

**Images:** 13 fresh `w308-*` crops, verified type-free on the contact sheet.

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8108/08-acne/)

## Iteration 1 — launch audit: arrivals caption white-on-light ("The studio — new programme" over the pale machine image, low contrast) → added text-shadow 0 1px 10px rgba(0,0,0,.55). Verified shadow applied.

## Iteration 2 — performance: 13/13 images dimensioned (zero CLS); all lazy below fold; two hover transitions total; zero dependencies; no scroll listeners.

## Iteration 3 — interaction battery: search ("sled"→The sled, Enter → #recover, Esc restore), newsletter (rejects "bad", accepts valid → "Signed up. News only, no noise."), sticky header, hover states (image opacity .82/.85). Zero console errors.

## Iteration 4 — structure: single hidden H1; alts 13/13; heading chain clean; focus-visible rings; Esc semantics on overlays.

## Iteration 5 — viewports: 1920 / 1024 / 768 / 390 all 0px overflow; arrivals + discover collapse 2→1 and 4→2→1.

## Iteration 6 — mobile: burger overlay opens/navigates (#discover)/closes/scrolls (verified scrollY>300); header condenses.

## Iteration 7 — composition verification: ghost watermark spans edge-to-edge over the darkened dancer scene; eyebrow top-left + utility bottom-left exactly like the reference; object strip reads as cutouts on gray with micro captions.

## Iteration 8 — news section verification: large plain paragraph + two small captioned cards mirrors the reference's house-journal block.

## Iteration 9 — footer verification: NEWSLETTER + gray EMAIL input, four tiny columns, bottom row © + IG/FB/TW/YT + "TRAINING IN FOUNDRY DISTRICT (ENGLISH)" — including the reference's deliberate default-blue link tint.

## Iteration 10 — final fidelity vs live acnestudios.com (/tmp/acne-shots/): micro-uppercase header with centered sentence-case logotype ✓; ghost logotype hero ✓; objects-on-gray strip ✓; gapless arrivals ✓; DISCOVER MORE tiles ✓; NEWS paragraph block ✓; utilitarian footer ✓. Dry institutional voice ("The training club culture — est. 2026") with Core Culture content throughout. No Acne marks or assets.

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors in every run; keyboard ok; 13 crops type-free; all images dimensioned + lazy below fold; no scroll-triggered animation (deliberate, like the reference).
