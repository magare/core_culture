# 01 — AESOP (aesop.com) — design-grammar study for Core Culture

Reference territory: editorial restraint · sophisticated typography · unusual whitespace · premium cultural feeling.
Confidence: FULL (live-browser observation). Method: headed Chromium via Playwright (`channel="chrome"`), viewport 1440×900, 2026-09-20. Captured: hero + 7 scroll positions + footer of `https://www.aesop.com/` (HTTP 200, 8829px tall, no horizontal overflow) plus product/story subpage `https://apose.aesop.com/products/apose` (in-house-designed "Aposē" table lamp PDP). Computed styles, stylesheet transition/animation rules and nav anatomy read via `tab.evaluate`. Screenshots: `/tmp/aesop-shots/`. Note: the mandated `browser-use:control-browser` skill was not installed in this session (plugin dir empty), so observation ran through Playwright-driving-real-Chrome directly — same real-pixel fidelity, documented honestly.

## Snapshot

A pharmacy-quiet ivory page where everything loud is confined to photography. Warm cream field (#FFFEF2), charcoal #333333 type, one ochre accent. A flared humanist display face (Zapf-Humanist, always weight 400, sentence case) floats over a tiny neutral Swiss body face (SuisseIntl 12px). Square-cornered 1px-outline buttons. Full-bleed cinematic video bands alternate with extreme-whitespace text bands. No cards, no shadows, no rounded corners, no scroll animation — the luxury is spacing, type contrast and photographic warmth. The site behaves like a literary journal that happens to sell bottles.

## Visual identity

Hard values read from the live DOM (`/tmp/aesop-report.json` → `facts`):

- **Backgrounds**: page `rgb(255,254,242)` = **#FFFEF2** (warm ivory); alt band `rgb(246,245,232)` = **#F6F5E8** (pale sage-cream, used for "Recommended reading" and trust bands); footer/solid buttons `rgb(51,51,51)` = **#333333**.
- **Text**: primary `rgb(51,51,51)` **#333333**; secondary `rgb(102,102,102)` **#666666**; text-on-media is the ivory #FFFEF2. Accent observed in labels ("New addition", "Beloved formulation", PDP eyebrow "Designed in-house"): `rgb(148,92,38)` = **#945C26** (bronze ochre). That is the ONLY chromatic UI color on the whole page.
- **Type** (computed):
  - Body: `SuisseIntl, sans-serif` 12px / line-height 18px (1.5) / weight 400.
  - Display headings: `Zapf-Humanist, sans-serif` (a flared humanist in the Optima family) — H2 "Curated Sets" 31px / 41.2px / **weight 400** / normal case / normal tracking.
  - PDP H1 "Aposē": SuisseIntl 35px, letter-spacing **-1.05px** (≈ -0.03em), weight 400.
  - Homepage H1 exists only for screen readers (36px/50.4px) — visible hierarchy starts at H2 31px.
  - Eyebrows/labels: bold SuisseIntl 12–16px (kit style shows 700 / 1px letter-spacing / uppercase variant; live usage mostly bold sentence case: "Introducing", "Eaux de Parfum", "Aesop Upper West Side").
  - Product names: SuisseIntl 14px **700**; descriptors #666666 400.
  - @font-face on site: `SuisseIntl`, `SuisseIntl-Medium`, `Zapf-Humanist`. Google Fonts stand-ins for the builder: **Tenor Sans** or **Marcellus** (flared humanist display) + **Inter** (neutral Swiss body).
- **Buttons**: 1px solid currentColor, `border-radius: 0px`, transparent fill, 16px padding, 14px text; solid #333333 variant only for commerce ("Add to bag", "Pre-order"). Kit rule: `.c-button :: background-color 0.25s ease-out, color 0.25s ease-out` — i.e. hover inverts fill/text. Text links carry a → arrow ("Explore the story →", "View stores →").
- **Decoration inventory**: hairline 1px underlines (active tab, footer column heads, PDP delivery rows); circular ghost icon buttons (carousel arrows, pause/mute, back-to-top); that is all. No gradients, no shadows, no cards.

## Composition

- **Container**: dominant content width **1170px** (95 measured elements); forms 1200px; everything else full-bleed 1425px. Two-column panels split ~562/690. Lead paragraphs constrained to ~690px.
- **Hero**: full-bleed 1440×720 image (2:1) cropped to ~713px (≈79vh) video carousel; centered white text stack low-center: eyebrow → display headline → one-line lede → outlined button; prev/next chevrons at extreme edges; circular pause/mute bottom-left; thin progress dashes bottom-center.
- **Vertical rhythm**: enormous. A pull-quote band is ~500px tall for one 31px line + attribution. Sections breathe 100–180px; imagery bands interrupt like chapter breaks.
- **Section grammar of the homepage, in order**: 79vh video hero → centered intro band → 3-up product carousel ("Curated Sets") → **50/50 split** (full-height media with bottom-left white overlay text | ivory half with eyebrow + display headline + underlined tab row + 3-up product carousel) → 2-col editorial ("Follow your nose") → 5-up category tile strip → featured regimen (image left, purchase rail right) → centered title + 3-up products → trust band (2-col: Certified B Corp / Leaping Bunny) → full-bleed store film → centered "A neighbourly presence" + outlined CTA → 3-up "Recommended reading" → full-viewport pull quote → dark footer.
- **Density discipline**: never more than 3 tiles per row for products/reading (5 only for small category thumbnails); one idea per band; text columns narrow; images do the shouting.

## Navigation

- **Two-row transparent header** over the hero (all text ivory #FFFEF2): utility row — "Stores", "Customer service" left; centered logotype; "Email sign up", "Account", "My cart" right. Primary row — 11 sentence-case items (Shop all, New & Notable, Skin Care, Hand & Body, Fragrance, Home, Hair, Travel, Gifts, Library, Experience) + a **boxed search field** (1px outline, magnifier icon, "Search...").
- Mega-menu with level-1/level-2 grouped panels on hover/focus; hamburger below desktop (`c-hamburger__button`). Header is `position: relative` initially; a compact sticky state slides in (`​.l-header.m-sticked .l-header__inner :: transform 0.15s ease-out`) and the logotype swaps `m-light`/`m-dark` variants per background.
- Footer = dark #333333 band: first a 3-up service-promise row (icon + bold label: Secure checkout / Complimentary samples / Complimentary gift wrapping), then 4 columns with 1px-underlined bold heads and 12px links, newsletter form with ivory input fields, hairline-ruled legal row.

## Photography

- **Ratios observed**: hero 1440×720 (2:1); product shots 370×370 (1:1, rendered 376/216px); PDP gallery 1794×1345 (4:3, huge); reading tiles ≈373×223 (5:3); category tiles ≈222×173 (~4:3). Logotype asset 3000×945.
- **Treatment**: warm, amber-dominant, art-directed stills and film — bottles on stacked books, hands on a bookshelf, storefront with passing cyclist, macro oil-and-bubbles. Objects on seamless warm-cream backdrops for commerce; environmental films for mood. People appear cropped/anonymous (hands, silhouettes) — never smiling-at-camera.
- All product photography sits on the ivory/cream field so bottles float without cards. Below-fold images lazy-load with a **blur-up** (`img.m-blur :: filter 0.4s`).
- Translation note: photography IS the color palette — amber glass, brass, wood, skin. UI chrome stays monochrome.

## Motion

Read from the site's own stylesheet rules (no scroll-driven/parallax rules exist at all):

- Durations cluster **0.15–0.5s**, mostly 0.2–0.3s, `ease-out`. Hover/state only: buttons invert color/background 0.25s; links underline; accordion `max-height 0.1s`; sticky header `transform 0.15s`.
- Keyframe utilities: `fadeIn/fadeOut` 0.2s linear, slide-in/out (4 directions) 0.2s, `loader-spin`. Image blur-up `filter 0.4s`.
- Carousels advance manually (small circular chevrons) or auto with progress dashes; film bands ship **pause and mute controls** (accessibility-respecting autoplay).
- Philosophy: nothing moves unless the user acts or a film plays. No reveals-on-scroll, no parallax, no scroll-jacking. Stillness is the flex.

## Storytelling

- The site narrates like a literary house: hero campaign "The Fragrant Fables" introduces perfumes as chapters; a full-viewport pull quote with attribution (Ada Lovelace: "Your best and wisest refuge from all troubles is in your science.") ties science to romance; "Recommended reading" cards carry category + title + "**Five-minute read**" metas; olfactive **tab row** (Fresh / Floral / Woody / Ambery) sorts the range like an index.
- Product names are titles of small poems; every product gets a one-sentence descriptor in gray, then price — copy is intimate, unhurried, never shouty.
- Trust is stated plainly in a quiet band (B Corp, Leaping Bunny), and craft in an ochre eyebrow ("Designed in-house") on the Aposē lamp PDP — the brand even sells furniture as narrative objects. The PDP itself: giant 4:3 stills left, narrow persistent purchase rail right (eyebrow → 35px tight-tracked name → gray lede → "Read more" → price → chip selectors → solid #333 CTA → hairline-ruled delivery rows → "View stores →").

## SIGNATURE CHARACTERISTICS

1. **Two-voice typography.** A flared humanist display (Zapf-Humanist, weight 400, sentence case, ~31px, line-height 1.3) answers a tiny Swiss body (SuisseIntl 12–14px). Display is never bold, never uppercase; hierarchy comes from size contrast (31 vs 12) not weight.
2. **The ivory field.** Everything lives on #FFFEF2 with #333 text and #F6F5E8 cream section bands; chrome is monochrome; the single accent is ochre #945C26 used only for tiny labels. All other color arrives inside photographs.
3. **Outline-button grammar.** 1px currentColor border, 0px radius, transparent fill, → arrows on text links; solid #333 reserved exclusively for transactional CTAs. Hover = slow (0.25s) color inversion.
4. **Chapter-break composition.** ~79vh full-bleed film hero; alternating 50/50 media-text splits; centered eyebrow→display-headline→lede→outline-CTA stacks; bands of pure whitespace so large a single quote owns a viewport. Max 3 tiles per row; 1170px container; ~690px text columns.
5. **Borderless object display.** Products float on the page background — no cards, borders, shadows or radius anywhere; identity carried by 1:1 images, 14px bold names, #666 descriptors; hairline underlines are the only ruling device.
6. **Quiet state motion.** 0.2–0.3s color/opacity/transform transitions, blur-up images, sticky-header swap; autoplay films with pause/mute; zero scroll-triggered animation.
7. **The literary layer.** Bold sentence-case eyebrows, attributed pull quotes, "x-minute read" metas, index-like tab rows — commerce presented as a journal with an editorial voice.

## Translation opportunities for Core Culture

- **Two-voice type → the house liturgy.** Tenor Sans (or Marcellus) 30–34px sentence-case display for chapter titles ("Training is only part of the culture.", "One space. More than one way to move.") over 12–13px Inter body. Never bold the display face — let size do it.
- **Ivory field + photographic color.** Warm ivory page (near #FFFEF2) with charcoal text; cream #F6F5E8-style bands for RECOVER and CONNECT sections; chrome monochrome; let the red folds, neon dancer and frost photography supply all saturation. Ochre-label slot ("Designed in-house") becomes ochre eyebrows: "Built for biomechanics", "Designed for recovery".
- **Outline-button grammar.** "Book a visit →", "See the timetable →", "Explore recovery →" as 1px square outline buttons; one solid-charcoal transactional CTA only: "Become part of the culture." Hover = 0.25s inversion, with `prefers-reduced-motion` fallback.
- **Chapter-break pacing.** 79vh hero (dance-neon or sled still) with centered eyebrow/display/lede/CTA stack; 50/50 splits: sled-push media | PUSH copy; ice bath B&W | RECOVER; dance studio | MOVE; full-bleed parking-at-dusk band → "A neighbourly presence" analog for arrival (parking, AC, open late) with a single outlined CTA; a full-viewport pull-quote band for "THIS IS NOT JUST A GYM." attributed like the Ada Lovelace quote.
- **Borderless discipline cards.** TRAIN/MOVE offerings as 1:1 crops floating on ivory (machine, sled, dancer): 14px bold name, one gray witty descriptor ("For engines, and the days after leg day."), price/class-length line — no boxes, max 3 per row, 1170px container.
- **Index tab row.** Underline-tabbed section (like Fresh/Floral/Woody/Ambery) switching discipline lists: TRAIN / PUSH / MOVE / RECOVER — 8 lines of vanilla JS, one underline device.
- **The literary layer, Core-Cultured.** "From the floor" reading cards with "Five-minute read"-style metas ("Sixty-minute class", "Two-minute read"); amenity promise band in the B-Corp slot: Netflix on the treadmills · industrial-grade AC · ice bath + steam · ample parking (small line icons, bold labels); hobby clubs (dance/yoga/zumba) as "Recommended reading" analog.
- **Quiet motion.** Blur-up image loads (CSS filter transition), 0.2–0.3s hover inversions, rAF-throttled sticky header with light/dark logo-color swap; autoplaying hero film replaced by a Ken-Burns-still with pause button — stillness preserved, video optional.
- **Footer as dark close.** #333 band: 3-up service promises, underlined column heads (Train / Recover / Community / Visit), ivory newsletter inputs, hairline legal row.
