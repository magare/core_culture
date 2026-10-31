# Core Culture — final website

A responsive, editorial training-club concept with a live Three.js gym model.
The app is in this folder. The original pitch pages and Blender source remain
separate; the website uses an exported, optimized copy of the Blender cutaway.

## Run

From the repository root:

```sh
python3 -m http.server 8931 --bind 127.0.0.1
```

Open http://127.0.0.1:8931/site/ (or `#plan` for the interactive model).
The bundled viewer is included, so no installation or build is needed to view
the site. Serve over HTTP: ES modules and GLB loading do not support `file://`.
All fonts, imagery, model data, and runtime scripts are local.

## Verify

```sh
npm --prefix site ci
npm --prefix site test
node --check site/js/app.js
node --check site/js/data.js
node --check site/js/motion.js
git diff --check
```

The 17 tests check site content, accessibility hooks, local-only form behavior,
GLB validity, decoded geometry, branding, signage, source-file preservation,
and viewer loading contracts. Interactive checks are documented in
[design/QA.md](design/QA.md), [design/CLEANUP-QA.md](design/CLEANUP-QA.md),
[design/MOTION-QA.md](design/MOTION-QA.md), and
[design/THREEJS.md](design/THREEJS.md). The PDF-aligned Blender revision was
exported anew on September 28; its manifest hash matches the saved source.

## Design

- Black, bone, rust, and amber, with the existing Core Culture identity.
- Distressed brand headlines, Barlow Condensed for functional titles and times,
  and Manrope for readable body text.
- Seven cohesive AI-generated concept images, compressed to WebP.
- Large photographic opening, concise club philosophy, native horizontal
  space rail, quiet recovery feature, daily timetable, interactive 3D floor,
  proposed memberships, and a contextual first-visit form.
- Lenis-powered smooth scrolling and GSAP/ScrollTrigger choreography: directional
  scene curtains, staggered perspective entrances, drifting display type,
  scroll-scrubbed image lighting/depth, a moving typography band, header progress,
  and precise anchor navigation.
- Deliberate mobile compositions, usable keyboard states, reduced motion,
  lazy-loaded supporting images, and preloaded hero/display font.
- Lazy-loaded Three.js, with no autoplay, analytics, third-party runtime requests,
  or frontend framework. The main page does not wait for the 3D bundle.

## Structure

- `index.html` — semantic page shell, form, and native dialogs.
- `css/styles.css` — tokens, layouts, component states, and responsive styles.
- `css/refinements.css` — shared website/model aesthetic refinement.
- `css/model-viewer.css` — responsive 3D viewport and controls.
- `css/motion.css` — responsive narrative layout, entrances, and scroll effects.
- `js/data.js` — sample club content and image mappings.
- `js/app.js` — navigation, room rail, gallery, directory, schedule, form, routing.
- `js/motion.source.js` — editable Lenis and GSAP motion source.
- `js/motion.js` — bundled, ready-to-serve motion runtime and dependencies.
- `js/model-loader.js` — lazy loading, data-saver opt-in, and retry handling.
- `js/model-viewer.js` — editable Three.js viewer source.
- `js/model-viewer.bundle.js` — ready-to-serve local viewer and dependencies.
- `assets/models/` — compressed GLB and export manifest.
- `assets/images/` — optimized project-local imagery.
- `assets/fonts/` — self-hosted fonts and their OFL licenses.
- `tests/` — content smoke tests and model validation/decoding tests.
- `design/ASSETS.md` — image provenance and art direction.

The old `design/wireframe-*.html` files are retained as historical references,
not as a specification of this redesign.

## Interaction details

- The floor is real 3D geometry, not a rendered image or image sequence.
- Four camera presets, orbit/pan/zoom, keyboard controls, labels toggle, reset,
  and expanded view. Enable orbit to capture pointer/touch input; Escape exits.
- The expanded dialog reuses the same WebGL canvas and downloaded model.
- Rendering is on demand and pauses offscreen. There is no automatic rotation.
- `#room=strength` (or any other room ID) opens a shareable room detail.
- `#directory` opens the searchable equipment directory.
- Browser Back, Escape, and the close buttons return through routed dialogs.
  Room-to-equipment navigation retains the room in browser history.
- Room galleries enlarge in a nested lightbox; arrows cycle available images.
- Native dialogs make the background inert. Explicit Tab wrapping and focus
  restoration support keyboard use, including nested galleries.
- Weekly classes show the next seven local dates, starting today, with discipline filters.
  Finished sessions are omitted and empty results offer a reset action.
  Events share the same filter; the upcoming session is computed from the clock.
- Session, room, and membership enquiries carry context into the visit form.
  Session enquiries also fill the date and time of day. Browser Back returns to
  the originating room or section.
- Form validation checks name, phone format, and local-date availability.
  Successful demo submission clears entered details without storing or sending.
- `?rm=1` forces reduced motion for both CSS and JavaScript; the operating
  system's reduced-motion preference is also honored, including live changes.
- Lenis and GSAP share one animation ticker, while the room rail, dialogs, model,
  and touch interactions remain native. Dialogs pause page scrolling, keyboard
  focus reveals content immediately, and reduced motion removes both smoothing
  and animation so the narrative remains a readable static layout.

## Rebuild the motion bundle

```sh
npm --prefix site ci
npm --prefix site run build:motion
```

Lenis and GSAP are bundled locally; the production page makes no CDN requests.

## Rebuild the 3D viewer

```sh
npm --prefix site ci
npm --prefix site run build:viewer
```

The package lock pins Three.js 0.186.0 and the build/validation dependencies.
Model export instructions and realtime material limitations are in
[design/THREEJS.md](design/THREEJS.md). The source Blender file is never saved
by the exporter.

## Before going live

This remains an explicitly labelled design preview:

- Replace concept imagery with verified photography if representing the actual venue.
- Confirm location, opening hours, parking/accessibility, facilities, equipment,
  classes, coaches, membership benefits, prices, and terms.
- Replace the local-only form with an approved booking endpoint and appropriate
  privacy/consent handling. Do not remove the demo notice before that is done.
- Review page copy and business details with the owner.

No fabricated prices, working-looking placeholder telephone numbers, or dead
social links are exposed by the final UI.
