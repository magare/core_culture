# 01-aesop — build log & iteration ledger

## Plan — Aesop x Core Culture

**Concept: "Quiet Authority"** — Core Culture as a literary house of training: a pharmacy-quiet ivory page where all the noise is confined to the photography, and the discipline of the club is expressed as restraint. The page reads like a journal that happens to sell memberships — chapters, not sections; stillness, not stunts. Three sentences: an ivory field (#FFFEF2) carries two-voice typography (flared humanist display at weight 400 over a tiny Swiss body), chapter-break bands of enormous whitespace interrupt with full-bleed warm photography, and the only chrome is hairlines, 1px square outline buttons and one ochre label color — every drop of saturation arrives inside the photographs.

**Signature rules transferred (from research/01-aesop.md §Signature Characteristics, to be re-verified against the live site):**
1. Two-voice typography — Tenor Sans display, weight 400, sentence case, 30–34px, never bold, never uppercase; Inter 12–13px body; hierarchy by size contrast, not weight.
2. The ivory field — #FFFEF2 page, #333 text, #F6F5E8 cream bands, monochrome chrome, single accent ochre #945C26 used only for tiny labels.
3. Outline-button grammar — 1px currentColor, 0px radius, transparent fill, → arrows on text links; one solid-charcoal transactional CTA; 0.25s hover inversion.
4. Chapter-break composition — ~79vh full-bleed hero with centered low stack; 50/50 media-text split; centered eyebrow→display→lede→CTA stacks; max 3 tiles per row; 1170px container; ~690px text columns.
5. Borderless object display — 1:1 images floating on ivory, 14px bold names, #666 descriptors, hairline underlines as the only ruling device.
6. Quiet state motion — 0.2–0.3s color/opacity/transform only, blur-up image loads, sticky header swap, hero "film" as slow crossfade/Ken-Burns stills with a working pause control; zero scroll-triggered animation.
7. The literary layer — bold sentence-case eyebrows, attributed full-viewport pull quote, "x-minute read" metas, index-like underline tab row.

**Section flow:** two-row transparent header (utility row / primary row + boxed search; compact ivory sticky state after hero; hamburger overlay under 900px) → 79vh still-carousel hero with pause control, edge chevrons, progress dashes → centered intro band → 3-up borderless "First movements" → 50/50 split with underline tab row (Train/Push/Move/Recover, media crossfades) → 2-col editorial (the lounge/field story) → amenity promise band on cream → full-bleed dusk-arrival band with centered CTA → 3-up "From the floor" reading cards with metas → full-viewport attributed pull quote → dark #333 footer (3 service promises, underlined column heads, ivory newsletter inputs, hairline legal row).

**Nav model:** Aesop's two-row header translated — utility row ("Visit · Contact" left, logotype center, "Hours · Book a visit" right), primary row of six sentence-case anchors + boxed 1px-outline search field that live-filters an in-page index dropdown (real behavior, keyboard operable). Compact sticky bar with light/dark logotype swap; mobile hamburger overlay, Esc-closable.

**Motion system:** none on scroll. Only hover/state transitions (0.2–0.3s ease-out), hero crossfade + 14s Ken Burns with pause button and dash progress, blur-up image load, sticky header transform 0.25s. `prefers-reduced-motion`: no Ken Burns, no auto-advance, instant swaps, no smooth scroll.

**Image treatment plan (all new crops, prefix `w301-`, type-free zones only, each verified by eye):**
- Hero carousel 3× full-width slices: w301-hero-dance (slide-5 y150–730 — dancer between neon tubes), w301-hero-frost (slide-8 bottom half — quiet frost), w301-hero-ice (slide-6 upper band — B&W ice crystals).
- Tab media tall crops: w301-machine-tall (slide-2 left column), w301-sled-tall (slide-3 right column), w301-dance-tall (slide-5 right column), w301-ice-tall (slide-6 upper-left strip).
- 1:1 borderless tiles: w301-machine-sq, w301-sled-sq, w301-ice-sq.
- Editorial: w301-field-card (slide-7 bottom — man-at-desk surreal, lounge story).
- Dusk band: w301-dusk-wide (slide-10 upper-left full-width slice).
- Reading cards 5:3: w301-streak-card (slide-4 bottom), w301-pop-card (slide-9 upper-right), w301-frost-card (slide-8 lower band).
No baked slide type anywhere; the page's own type is the only type.

**What makes it unmistakably Core Culture:** the voice ("Training is only part of the culture.", "This is not just a gym.", descriptors like "For engines, and the days after leg day."), the disciplines TRAIN/PUSH/MOVE/RECOVER as the index tabs, real amenities as the promise band (Netflix on treadmills, industrial AC, ice bath + steam, ample parking), and neon/red/sweat photography doing all the talking on an Aesop-quiet field. The reference's warm stillness is kept; its apothecary subject matter is fully replaced.

---

## Iteration log (all verified on rendered pixels via Playwright-Chrome, served at http://localhost:8101/01-aesop/)

## Iteration 1 — hero: pause control showed a PLAY triangle while the reel was playing (icon logic inverted) → added real pause-bars icon; `[aria-pressed="true"]` now swaps pause→play, aria-label swaps too → verified in /tmp/w301-ix-search.png (pause bars while playing) and /tmp/w301-ix-paused.png (play triangle after pause, dashes frozen, `aria-pressed=true`, `.paused` class set).

## Iteration 2 — full-height audit at window-size 1440×9500 blew up every `vh` band: `.arrival`/`.quote` min-height:72vh became ~6800px black voids and the arrival copy vanished below the frame → capped both to `min-height:min(72vh,780px)` (hero was already capped by `max-height:900px`) → re-render: page height 6496px at 1440, arrival stack (eyebrow/headline/lede/CTA) centered and visible (/tmp/w301-i2-5-y3690.png).

## Iteration 3 — disciplines 50/50: white overlay caption ("Train / Machines that fit biomechanics.") sat directly on the pale machine photo — illegible → added a quiet bottom scrim (`linear-gradient(rgba(24,14,12,.62)→0)`, same device as hero veil, no card/box) → verified legible on all four tab medias, desktop (/tmp/w301-i2-3-y2214.png) and mobile (/tmp/w301-m1-4-y2768.png).

## Iteration 4 — lounge editorial: field image crop showed the man-at-desk tiny at the top with a sea of empty grass below — composition dead-center wrong; first recut still caught the baked yellow type line → final recut `w301-field-tall.jpg` 480×500 @ (340,830), subject now fills the frame, type-free verified by eye → re-rendered editorial reads as an Aesop-style image/text pairing (/tmp/w301-i2-3-y2214.png, mobile /tmp/w301-m1-5-y3460.png).

## Iteration 5 — amenity band: the "industrial-grade air conditioning" icon read as a sun (radiating circle), wrong register for cold air → replaced with a hairline snowflake → verified in /tmp/w301-i2-5-y3690.png and mobile /tmp/w301-m1-6-y4152.png.

## Iteration 6 — footer: legal row's right-hand text ran underneath the fixed back-to-top circle → `padding-right:64px` on `.legal` → re-verified in final footer capture (no overlap).

## Iteration 7 — arrival band read as near-black mush: source photo is dusk-dark AND veil was `rgba(.30→.56)` plus image at `opacity:.92` → lightened veil to `.18→.46`, image to full opacity → snow-covered cars, tail-lights and the yellow-jacket cyclist now visible behind the ivory stack (/tmp/w301-i2-5-y3690.png).

## Iteration 8 — a11y/semantics pass: tab rows used `h4` directly under an `h2` (skipped level) and the disciplines section carried BOTH a visually-hidden h2 and a visible display h2 → rows became `h3`, hidden duplicate h2 removed, `aria-labelledby` now points at the visible "A chapter for every appetite." → heading chain now h1→h2→h3 throughout; verified via code diff + unchanged render.

## Iteration 9 — type-behavior pass vs live Aesop: hero h1 rendered 44px at 1440 — louder than the live site's ~34–36px hero voice (live measured: H2 Zapf-Humanist 31px/400; hero stack small and restrained) → `h1.display` clamp trimmed 44→40px max, 3.4vw→3vw → re-rendered hero noticeably quieter; also killed the WebKit native clear-"x" inside the boxed search field (off-style chrome).

## Iteration 10 — mobile recomposition pass (390×844, full scroll capture + interaction): tiles stack 1-col with 16:10 crops; duo reorders media-above-copy at 64vw height with caption scrim intact; lounge flips image-first; promises go 1-col with hairline tops; burger opens the ivory overlay (Tenor links + index numerals), body scroll locks, Esc closes, tapping a link closes + scrolls (verified `scrollY=3539` at #lounge), burger tap target 44×40 → all verified in /tmp/w301-m1-*.png and /tmp/w301-m-menu.png.

## Iteration 11 — interactive state pass (desktop, scripted): tab click + ArrowLeft/Right/Home/End swap rows, media and caption (Push → "Engines over egos.", Recover → "Cold, then warm, then quiet."); search combobox filters ("ice"→"Ice bath / Class"), Enter scrolls to target (scrollY 1914); outline button hover inverts transparent→ivory in 0.25s; newsletter rejects `not-an-email` with an inline message and accepts a valid address with a written confirmation; sticky compact bar engages after the hero (`stickyOn=true`); zero console errors across every run.

---

## Final fidelity test — live aesop.com (fresh headed-Chrome captures /tmp/aesop-fin-1..3.png) vs /01-aesop/

- **Hierarchy philosophy — match.** Both open with a full-bleed cinematic hero carrying a small bold eyebrow → modest weight-400 display headline → one-line lede → wide 1px-outline CTA with a trailing →; both reserve solid fill for the single transactional action (theirs "Add to bag", mine the ivory "Subscribe"); both let the display face stay unbolded at ~30–40px over a 12–13px Swiss body (live re-measured this session: H2 Zapf-Humanist 31px/400 sentence case, body SuisseIntl 12/18; mine: Tenor Sans 40px h1 / 31px h2, Inter 13px — verified `h1px:40, h1Font:"Tenor Sans"` in the final run).
- **Pacing — match.** One idea per band, alternating ivory text chapters and photographic chapter breaks; a single line is allowed to own a viewport in both (their Ada Lovelace quote ↔ my "This is not just a gym."); band order deliberately varied in the back half (quote before reading) so the structure isn't a trace.
- **Image scale — match.** 79vh full-bleed hero; 50/50 full-height split media; 3-up borderless 1:1 objects floating on the field; 5:3 reading cards; full-bleed arrival band — the same four photographic scales, no boxes/shadows/radius anywhere.
- **Whitespace — match.** ~150–180px section breathing, 690px text columns, 1170px container discipline.
- **Emotional character — match.** Pharmacy-quiet, literary, unhurried: "A chapter for every appetite.", "Small mercies, kept daily.", "Nobody sleds alone." — the club narrated like a journal.
- **Still Core Culture, never Aesop — confirmed.** All color lives in the neon dancer, sled grit, B&W ice, frost and dusk-lot photography; the apothecary subject, amber palette, logotype and product voice are fully replaced by TRAIN/PUSH/MOVE/RECOVER, the amenity promises (Netflix treadmills / industrial AC / ice bath + steam / parking) and the house creed. No reference marks, no reference copy. A person who knows Aesop will say "that grammar"; nobody will say "that's Aesop".

## Final QA state (all executed this session)
- Overflow: 0px horizontal at 1440 / 1024 / 768 / 390.
- Console: zero errors on every Playwright run (console + pageerror hooks; `window.onerror`-class errors also mirrored to `<html data-err>`).
- Reduced motion (emulated): auto-advance off (`aria-pressed=true` on load), Ken Burns `none`, dash animation `none`, slide static after 3s wait, smooth-scroll disabled via `behavior:"auto"` branch.
- Keyboard: tab row arrow/Home/End navigable with `aria-selected`/`tabIndex` management; square 1px `:focus-visible` rings verified in pixels on tabs; skip link; Esc closes mobile menu.
- Images: 17 new `w301-*` crops, every one visually verified type-free (three re-cut after baked-type edges were caught in verification); `loading="lazy"` + `decoding="async"` below the fold; explicit width/height + aspect-ratio boxes (no layout shift); blur-up on load.
- Performance: zero JS dependencies; single passive rAF-throttled scroll listener; transform/opacity-only animations.


