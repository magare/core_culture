# Final UI verification — 22 September 2026

Served locally at `http://127.0.0.1:8931/site/` and tested interactively in the
Codex in-app Chromium browser. No production service was changed or submitted to.

## Responsive / visual checks

Browser-reported CSS viewport sizes:

| Width × height | Result |
| --- | --- |
| 360 × 800 | No page or component horizontal overflow; narrow room dialog works. |
| 390 × 844 | Two-line hero, deliberate athlete crop, mobile menu, readable day view. |
| 768 × 1024 | Tablet membership cards and side-by-side visit section verified. |
| 1440 × 1000 | Hero, club story, space rail, recovery, schedule, floor plan, and footer reviewed. |

The header, schedule toolbar, membership grid, visit form, and footer controls
were also checked for internal overflow. None was present at these four sizes.
Temporary viewport overrides were cleared after testing.

## Interactive checks

- Space rail next/previous position, counter, disabled edge state.
- All eight room details open with the correct title and project-local image.
- Room deep links load directly; browser Back closes and Forward reopens.
- Gallery thumbnails, enlarged images, arrow navigation, and synchronized selection.
- Escape closes only the top lightbox, preserving its underlying room dialog.
- Keyboard Tab/Shift+Tab wrap correctly inside room and mobile-menu dialogs;
  closing restores focus to the originating control.
- Mobile navigation opens, closes, updates `aria-expanded`, and follows anchors.
- Equipment search, zone filter, no-result state, clear filters, and room-to-kit context.
- The full directory contains 20 entries; studio filtering returns two.
- Weekly day/category filters, class disclosure, event filtering, empty states,
  and arrow-key tab selection work.
- Session and annual-membership actions carry their context into the visit form.
- Empty form, malformed phone, and past-date validation display associated errors
  and focus the first invalid input.
- A successful test using fictional contact information shows the explicit demo
  confirmation and clears the entered information. No request is sent or persisted.
- `?rm=1` disables both CSS motion and JavaScript animation delays.
- No application console errors/warnings, broken loaded images, or third-party
  runtime resource requests were observed.

## Automated checks

`npm --prefix site test` — 17/17 pass, including the new model tests.

`node --check site/js/app.js`, `node --check site/js/data.js`, and
`git diff --check` — pass.

## Interactive 3D update

The rendered-image model gallery has been replaced by a live Three.js scene.
The preceding room-gallery checks still concern concept photographs, not the
3D model. See [THREEJS.md](THREEJS.md) for current viewer-specific verification,
screenshots, performance measures, and limitations.

## Scope / remaining launch dependencies

This is a local design preview, not a deployed booking service. Actual business
details, real venue photography, prices/terms, and a booking backend still need
owner confirmation and integration. This pass did not test physical iOS/Android
devices or independent Safari/Firefox engines.
