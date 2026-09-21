# CORE CULTURE — REFERENCE-INSPIRED PAGES (WAVE THREE) — SHARED BRIEF

Read this fully before doing any work. It is the contract for every agent on this project.

## THE BRAND — CORE CULTURE

Premium fitness, movement, recovery and lifestyle destination. Includes weight training, strength, hybrid training, functional training, dance studio, recovery (ice bath + steam), lounge, community, lifestyle experiences.

Core Culture is NOT "a room full of gym equipment". It is:

**TRAIN / MOVE / RECOVER / CONNECT**

House messaging (use, adapt, or write better original copy in the same voice):
- TRAINING IS ONLY PART OF THE CULTURE.
- THIS IS NOT JUST A GYM.
- FIND YOUR CORE.
- BECOME PART OF THE CULTURE.
- ONE SPACE. MORE THAN ONE WAY TO MOVE.

Content pillars to draw from (adapt labels per reference):
- TRAIN — weight training, strength, functional training
- PUSH — hybrid performance, conditioning, athletic training (sled push, HYROX-style)
- MOVE — dance studio, mobility, movement
- RECOVER — ice bath, steam, rest, reset
- CONNECT — lounge, community, culture
Also real amenities from the brand's social content: machines that fit biomechanics, OTT screens on treadmills ("Running can get boring. So we put Netflix on the treadmill."), hobby clubs (dance/yoga/zumba), industrial-grade air conditioning, ample parking.

Tone: confident, warm, a little witty, never corporate. Premium club, real personality.

## THE MISSION (per page)

Build ONE landing page for Core Culture whose design philosophy is transferred from ONE live reference website. This is DESIGN-GRAMMAR TRANSFER, never copying: no reference logos, no reference copy/slogans, no proprietary graphics. Extract the system (composition, scale, whitespace philosophy, typography behavior, image treatment, motion philosophy, pacing, density) and reinterpret it so the page is unmistakably Core Culture.

The page must pass both tests:
1. A person who knows the reference thinks "ah, this speaks that design language".
2. The page still feels 100% like Core Culture, not like a clone of the reference.

## STACK & ENGINEERING CONVENTIONS (mandatory — respect the repo)

- Repo root: `/Users/magare/Dev/web-app-farm/core_culture` (referred to as `ROOT` below).
- Pure static HTML. NO package.json, NO framework, NO build step. Each page is ONE self-contained `index.html` in its own folder, with inline `<style>` and inline `<script>` (vanilla JS only).
- Google Fonts via CDN is allowed and expected (the existing 40 pages do this).
- New wave-three folders are named: `01-aesop`, `02-nike`, `03-on`, `04-gymshark`, `05-arcteryx`, `06-gentle-monster`, `07-jacquemus`, `08-acne`, `09-moncler`, `10-nothing`, `11-teenage-engineering`, `12-polestar`, `13-apple`, `14-bang-olufsen`, `15-vercel`, `16-linear`, `17-stripe`, `18-off-white`, `19-porsche`, `20-red-bull`. (Folders `01`…`40` already exist for waves one/two — NEVER write into them.)
- Asset references from a page folder are relative: `../assets/slide-3.jpg`, `../crops/p03-plate.jpg`.
- Never modify: folders `01`…`40`, `assets/`, `crops/`, `images/`, `MANIFEST.md`, `MANIFEST2.md`, `prompt0.md`, `prompt1.md`. The hub `index.html` is updated ONLY by the lead, not by agents.
- Existing pages follow this pattern — you may Read `ROOT/01/index.html` or others for engineering conventions (meta tags, favicon data-URI, reduced-motion block style) but NEVER for visual structure.

## IMAGE ASSETS (the only photography allowed)

All in `ROOT/assets/` (10 slides, 1080×1440 portrait, JPEG) — Canva-designed brand slides WITH baked-in headline type. Type-free zones (verified) for clean crops:

| file | content | palette | BAKED TYPE LOCATION (avoid these zones when cropping) |
|---|---|---|---|
| slide-1 | warped red glossy folds ("FUN?" poster bg) | signal red / dark | top 8% header; large yellow serif type upper-left→center 18–55%; thin arrow lower-right |
| slide-2 | black/silver gym machine, light-gray studio bg | silver / black / white | top 8%; red serif headline right half 28–62% |
| slide-3 | athlete pushing sled, dark gym, motion blur | dark / warm skin | top 8%; white serif type left 40–60% — RIGHT half of image is clean |
| slide-4 | vertical light streaks, abstract | red/purple/white on black | top 8%; white serif type center 25–60% — left and right edges are clean |
| slide-5 | dancer silhouette, neon pink backlight, wet floor | pink/red/black | top 8%; white type lower-left 50–90% — upper-right quadrant clean |
| slide-6 | ice bath tub close-up, B&W | monochrome | top 8%; white type lower-right 52–85% — upper-left two-thirds clean |
| slide-7 | man at desk in vast green field (surreal) | green / warm | top 8%; yellow type right-center 30–55% — left third and bottom third clean |
| slide-8 | condensation/frost texture, deep blue | blue/teal/dark | top 8%; pale blue type 22–52% — bottom half clean |
| slide-9 | pop-art painted figure (red/blue/yellow brush) | red/blue/yellow | top 8%; white type lower-left 47–78% — upper-right two-thirds clean |
| slide-10 | snowy parking lot at dusk, warm headlights | dark / warm amber | top 8%; yellow type lower-right 50–80% — upper-left two-thirds clean |

Pre-cut type-free crops exist in `ROOT/crops/` (p01-… p26-…, 38 files; names hint content, e.g. p03-plate, p05-run, p12-f01…f12 are 12 contact-sheet frames). Inventory them with `ls ROOT/crops/` and look at any you plan to use.

Cutting NEW crops (preferred over shipping baked-type zones): use `sips`:
`sips -c <cropH> <cropW> --cropOffset <offY> <offX> ROOT/assets/slide-N.jpg --out ROOT/crops/w3NN-slug.jpg`
(cropOffset is top-left of the crop, in px, of the ORIGINAL 1080×1440). ALWAYS verify a new crop by Reading the output file as an image — never ship an unverified crop. Prefix new wave-three crops `w3NN-`.

The 10 photos cover: red texture, machine, sled/athlete, abstract streaks, dance/neon, ice bath, lounge/field surreal, frost/steam texture, pop-art energy, parking/arrival. Chosen image TREATMENT (full-bleed, extreme crop, duotone, grayscale, masked, oversized, tiny-editorial, filmstrip…) must come from the reference being studied — do not reuse one treatment across pages.

## QUALITY BAR (zero tolerance)

NO lorem ipsum, no TODOs, no placeholder boxes, no broken images, no console errors, no horizontal overflow, no fake/dead buttons (every interactive control does something real or is a clearly-styled anchor), no default framework styling, no unfinished mobile layout.
Accessibility: semantic landmarks, one h1 then ordered headings, alt text on meaningful images (decorative ones `alt=""`), visible focus states, contrast-aware color pairs, keyboard-operable nav/menus, `prefers-reduced-motion` fallback for ALL motion.
Performance: `loading="lazy"` on below-fold images, `decoding="async"`, no layout shift (explicit dimensions or aspect-ratio), transform/opacity-only animations, no heavy libraries (zero JS dependencies — vanilla only), scroll listeners passive + rAF-throttled.

## VISUAL QA LOOP (mandatory per page — this is the heart of the job)

Serve and inspect REAL rendered pixels. Never judge design by reading code.

1. Serve: `cd ROOT && python3 -m http.server <PORT>` (run_in_background). Page URL `http://localhost:<PORT>/<NN-slug>/`.
2. Browser: invoke the Skill tool `browser-use:control-browser` first and follow it (bootstrap `setupBrowserRuntime`, `agent.browsers.getForUrl(...)`, read the API doc once, reuse tabs via `browser.tabs.list()`). 
3. Inspect AT MINIMUM: desktop 1440×900 (hero, every major section at scroll positions, hover states, footer) and mobile 390×844 (full recomposition, menu, tap targets). Use `tab.screenshot()` + `nodeRepl.emitImage(...)` per the skill, or screenshot files on disk you then Read.
4. ITERATE ≥10 MEANINGFUL TIMES. An iteration = run → look at pixels → compare against the reference's documented grammar → identify a real weakness → change something structural or clearly visible (composition, hierarchy, scale, spacing rhythm, type behavior, image treatment, motion, pacing, density, microdetail) → re-run → visually verify. Changing one margin to tick a counter does NOT count; log each iteration in `ROOT/research/<NN>-<slug>-iterations.md` as: `## Iteration N — <what was weak> → <what you changed> → <verified result>`.
5. Also check in the browser: console errors, overflow at 1440/1024/768/390, focus-visible states (Tab), reduced-motion (emulate), image rendering, type rendering.

## DIFFERENTIATION GUARDRAILS

The repo already contains 40 built pages (see ROOT/MANIFEST.md + MANIFEST2.md). Their concepts — swiss rules index, fight flyers, choreography score, telemetry console, fashion magazine issue, riso newspaper, horizontal rooms, application form, brutal blocks, wellness ritual, Y2K episodes, contact sheet, timetable, elevator, thermal survey, rave listings, field journal, grayscale cinema, prospectus plans, LED scoreboard, eclipse, cable stack, heavy bag, blackout torch, orrery, night drive, wind tunnel, mirror room, prism, steam, well, gimbal, pinball, lockers, relay, rubber type, darkroom, speakeasy, foundry, event horizon — are TAKEN. Do not reproduce their structures or signature devices.
Likewise, never reuse the structure of earlier wave-three pages (list grows as the project proceeds — check `ROOT/index.html` hub section "Reference studies" for the current set before you start).
Each page gets a FRESH composition: different hero, nav model, section order, motion system, CTA logic, footer.

## REFERENCE RESEARCH DOC

The research agent saves findings to `ROOT/research/<NN>-<slug>.md` with sections: Visual identity / Composition / Navigation / Photography / Motion / Storytelling / Signature characteristics (3–7 bullet "recognize without a logo" rules) / Translation opportunities for Core Culture. The build agent must READ this doc before writing a line of code and follow its signature rules.
