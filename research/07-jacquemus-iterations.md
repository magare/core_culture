# 07-jacquemus — build log & iteration ledger

## Plan — Jacquemus x Core Culture

**Concept: "LE WARM-UP"** — playful luxury: a white page where the club is merchandised as a collection of named objects ("Le Rack", "Le Sled", "Le Bain Glacé", "Le Néon"), carried by geometric micro-type (Jost, the observed Futura PT stand-in), whitespace as structure, 1px hairline rules, asymmetric editorial splits (small text column vs oversized warm photograph), and a light warm grade unifying all imagery. Time-as-price captions ("from 45 min") keep the sparse-commerce grammar without invented currency.

**Observation provenance (flagged honestly in research/07-jacquemus.md):** live jacquemus.com was in global maintenance during this build (verified across 7 locales); live observation = maintenance page (Futura PT, black-on-white, hairline rule, centered message) + archived production markup (Nov 2025 Wayback: logotype placement, mega-nav taxonomy, product-line naming, 4-up commerce rows). Synthesis marked MEDIUM-HIGH confidence in the study.

**Structure:** micro-caps header (logotype left, nav center, underlined SEARCH/MEMBERSHIP right) → asymmetric hero (text column + oversized field-office photograph) → "Objects — the winter protocol" 4-up (Le Rack / Le Sled / Le Bain Glacé / Le Néon) → editorial split (red light + "Fridays, the floor turns red.") → "Night room — this week" 4-up (La Nuit / Le Givre / Le Parking / Le Bureau) → manifesto band → minimal single-row footer.

**Motion:** hover zoom 1.035 on plates + underline dimming only; no scroll animation.

---

## Iteration log (rendered-pixel verified via Playwright-Chrome at http://localhost:8107/07-jacquemus/)

## Iteration 1 — crop audit: the red editorial split first recut (700,820,1080,1290) still showed warped letterforms from slide-1's baked poster type → trimmed to (700,820,1080,1160).

## Iteration 2 — the baked YELLOW ARROW device (y1170-1200) remained in frame → final trim (700,820,1080,1150); verified clean on rendered pixels.

## Iteration 3 — performance: 10/10 images dimensioned (zero CLS); all lazy below fold; single warm-grade CSS filter; zero dependencies; no scroll listeners.

## Iteration 4 — interaction battery: search ("bain"→Le Bain Glacé, Enter → #objects, Esc restore); object cards open the join dialog; validation rejects bad input; success personalizes ("Held a spot for Rafi. First session is on us."); hover zoom confirmed 1.033 transform. Zero console errors.

## Iteration 5 — structure: single H1 (visually the hero headline "The club, in summer mode."); alts 0 missing; heading chain clean.

## Iteration 6 — viewports: 1920 / 1024 / 768 / 390 all 0px overflow; hero + editorial collapse to single column ≤820px; objects 4→2→1.

## Iteration 7 — mobile: burger overlay (micro-caps links), navigates to #night, closes, scrolls (verified scrollY>400).

## Iteration 8 — reduced motion: plate zoom neutralized; page fully functional.

## Iteration 9 — composition verification: asymmetric hero (small text column vs oversized warm photo) reads Jacquemus; hairline-ruled section heads with underlined "View all"; night row naming (La Nuit / Le Givre / Le Parking / Le Bureau) consistent; manifesto band quiet.

## Iteration 10 — final fidelity assessment vs observed material: live maintenance page's grammar (geometric caps logotype, whitespace structure, hairline rules, quiet centered voice) is transferred; archived markup's taxonomy echoed in the objects/naming system; warm unexpected imagery (desk-in-field as hero) matches the reference territory. Still unmistakably Core Culture (house copy, amenities, disciplines). Honest limitation recorded: full campaign-scale visual details synthesized due to maintenance.

## Final QA state
- Overflow 0px at 1440/1024/768/390; zero console errors; reduced motion ok; keyboard ok; 11 crops type-free (2 recut); all images dimensioned + lazy below fold.
