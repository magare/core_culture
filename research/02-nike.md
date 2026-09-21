# 02 — NIKE (nike.com, geo-served nike.in — identical global design system) — design-grammar study for Core Culture

Reference territory: enormous sports imagery · campaign-led storytelling · confident typography · athlete-first hierarchy.
Confidence: FULL (live-browser observation). Method: headed Chromium (`channel="chrome"`), 1440×900 + 390×844 mobile, 2026-09-20. `nike.com` IP-redirects to `nike.in` (same platform, same design language; every component observed exists on the global system). Captured: hero + 8 scroll positions + footer, mobile full scroll, hover states, computed styles. Screenshots `/tmp/nike-shots/`, computed facts `/tmp/nike-report.json`.

## Snapshot

White chrome, black type, and a stack of full-bleed campaign posters. All the energy lives inside the photography and inside ONE voice: a giant condensed uppercase headline (Nike Futura ND, 72px at desktop, ~0.9 leading, −0.5px tracking) that never appears anywhere else in the UI. Everything else is quiet Helvetica Now (24px section heads, 16px body). The only rounded thing on the site is the pill button. No cards, no shadows, no borders, no scroll animation — sections are posters separated by white air, and horizontal carousels with circular chevrons carry commerce.

## Visual identity (hard values from live DOM)

- **Page bg** `#FFFFFF`; promo bar `#F5F5F5`; product-tile bg `#F5F5F5`; primary text `#111111` (rgb(17,17,17)); secondary gray `#707072`; over-image text always `#FFFFFF`. No accent color in chrome — saturation arrives only inside campaign photos (red After Dark set, volt Pegasus, golden stairwell run).
- **Type**: campaign voice `"Nike Futura ND"` — hero "ELEVATE YOUR PRE-GAME ROUTINE" measured **72px / 64.8px line-height (0.9) / weight 500 / letter-spacing −0.5px / uppercase, white**. "SPOTLIGHT" center wordmark ~96px. UI voice: `"Helvetica Now Display"` section heads **24px / 500 / capitalize** ("Featured", "Trending", "Fresh Drops", "Shop By Sport"); `"Helvetica Now Text"` body **16px/24px/400**; card eyebrow 16px white; card headline 20–24px/500; product name 16px/500 black, category 16px `#707072`, price 16px. Utility/promo 12–16px.
- **Buttons**: **pill** — border-radius 30px+ (fully rounded), padding ≈ 8px 20px, 16px/500. Two variants: white fill + black text over imagery ("Shop" hero), black fill + white text on white background. Hover = `background 0.2s` (measured: white pill stays white/black → dims). Circular 32px icon buttons (carousel prev/next, pause, mute) — thin gray ring, white fill.
- **Decoration inventory**: none. Zero borders, zero shadows, zero radius on containers. Card separation by whitespace and flat `#F5F5F5` fills. Search field is a gray pill.

## Composition

- Full-width, edge-to-edge. Hero ≈ 1440×648 (~72vh): campaign image, centered-bottom text stack — giant uppercase headline → 16px one-line subline → pill CTA pair ("Shop" + "Watch ▶"); carousel dots bottom-center; pause + prev/next circles bottom-right.
- Section heads left-aligned, 24px/500, small margin (~48px), sitting alone in a white band before each poster group.
- "Featured": 2-up gapless split, full-height media, caption overlay **bottom-left** (eyebrow → 24px headline → pill).
- "Trending": 3-up, 16px gutters, 4:5 cards, same bottom-left caption grammar.
- "Fresh Drops": horizontal product carousel — flat `#F5F5F5` tiles ~433px, image 1:1, name/category/price under; circular chevrons vertically centered at edges; next tile peeks past the right edge.
- "Shop By Sport": 4-up caption-overlay cards.
- "SPOTLIGHT" finale: centered giant condensed wordmark + centered sentence + 8×2 grid of tiny labeled thumbnails (icon index).
- Campaign banner band (beige `#ECE8E1`, "IT'S BETTER ON THE NIKE APP") with rounded app-icon card + QR — giant condensed type as the poster.
- Footer: hairline + small gray legal row only (IN build compressed).
- Density discipline: one message per band; every band ends in exactly one pill; text never sits on white — it sits on imagery, bottom-left or center-bottom.

## Navigation

- Initial: utility row (Help | Sign Up | Log In, 12px, right) above main bar — swoosh left, centered nav (New & Featured / Men / Women / Kids / Jordan, 16px/500), gray pill search + heart + bag icons right. White bar always — never transparent over the hero; utility row scrolls away, main bar stays fixed.
- Mobile: swoosh left; search, bag, burger right. No mega-menu observed; hamburger overlay pattern standard to the platform.

## Photography

- Campaign-scale athletes in dramatic directional light (night run under a bridge, golden-lit stairwell, storm-sky golf, red-monochrome runner). Full-body or 3/4 crops, low camera, subjects centered or right-weighted. Strong per-campaign color grades (full red, volt, gold).
- Commerce photography: isolated product dead-center on flat `#F5F5F5`.
- Text always overlays the image directly (bottom-left or centered-bottom); no text-on-white sections except section heads.
- Hero ratios ~20:9; featured halves ~3:4; trending 4:5; product 1:1; sport cards 3:4; spotlight thumbs tiny squares.

## Motion

- Hero carousel auto-advances (dots + progress), pause + chevrons; slide/crossfade between campaigns. Horizontal rows scroll with circular chevrons; peeking next card invites drag.
- Button hover `background 0.2s`; link hover underline. NO scroll-triggered reveals, no parallax, no scroll-jacking anywhere on the homepage.
- Philosophy: the energy is in the imagery + type; motion is carousels and hovers only.

## Storytelling

- Open: campaign hero (product-legend "MOON SHOE — The origin of speed" or culture "ELEVATE YOUR PRE-GAME ROUTINE" + Watch). Then Featured (new stories 2-up) → Trending (3-up events/collections) → Fresh Drops (product carousel) → Shop By Sport (categories) → SPOTLIGHT (icon index) → app banner → minimal footer.
- Commerce presented as campaign season: each band is one poster with one headline + one pill. Voice: short, declarative, athlete-first ("Fast is Fun", "Power Up for Your Workouts", "More Comfort, More Running").

## SIGNATURE CHARACTERISTICS

1. **The giant condensed uppercase campaign headline** — one typeface voice reserved for posters only (72–96px, 0.9 leading, tight tracking, white over photo), instantly recognizable.
2. **Pill buttons as the only radius on the site** — white-over-image / black-on-white, 0.2s hover, one pill per poster.
3. **Full-bleed poster-band composition** — bottom-left caption stacks (eyebrow → sentence headline → pill), gapless 2-up splits, left-aligned 24px quiet section heads between bands.
4. **Black-and-white chrome discipline** — pure white UI, black type, `#F5F5F5` flat fills, `#707072` secondary; every drop of color arrives inside photography.
5. **Carousel culture** — hero with dots+pause+arrows; horizontal rows with circular chevrons and a peeking next card.
6. **Product-tile anatomy** — flat tile, 1:1 image, bold name / gray category / price triplet; no borders, no shadows.
7. **The centered giant wordmark finale** — "SPOTLIGHT"-scale condensed type over a tiny labeled thumbnail index.

## Translation opportunities for Core Culture

- Campaign voice = **Anton** (condensed uppercase energy), UI voice = Inter. Hero: "TRAIN. MOVE. RECOVER. CONNECT." as rotating campaigns ("SWEAT IS ONLY THE BEGINNING", "STRONG IS A SKILL", "COLD IS A SKILL TOO.").
- Disciplines as campaign posters: sled-push (dark) + ice bath as the gapless 2-up Featured; STRENGTH / DANCE / HYBRID as Trending 3-up; classes as "Fresh Drops"-style carousel (name / discipline / "60 MIN · ALL LEVELS" in place of name/category/price).
- "THE CULTURE" centered wordmark finale over an amenity thumbnail grid (ice bath, steam, Netflix treadmills, industrial AC, lounge, parking, desks, pop-art culture).
- Membership banner band (Nike app-band analog): cream field, giant type "BECOME PART OF THE CULTURE.", one pill + membership-card device.
- Keep zero scroll animation; motion = hero carousel + class carousel + hovers. White chrome, black type, color only in photos.
