# Scroll motion — 26 September 2026

The existing marketing site now includes a staged headline entrance, hero
parallax, a three-chapter club story, a moving typography band, section and
image reveals, image depth, and hover feedback. The club story stays in view
on larger, taller screens and uses a natural layout on mobile and short screens.
Tablet navigation switches to the compact menu before its labels wrap.

## Implementation

- `css/motion.css` and `js/motion.js` contain the enhancement independently of
  room routing, schedules, forms, and the model viewer.
- Scrolling remains native. Updates share one requested animation frame;
  measurements are cached and refreshed when the layout changes.
- Existing local images and fonts are reused, with no additional dependencies.
- Reduced motion removes parallax, pinning, and entrances, including when the
  system preference changes during a visit. `?rm=1` also disables motion.
- Content stays visible without JavaScript. Keyboard focus reveals cards
  immediately; inactive story images are hidden from the accessibility tree.

## Verification

- 55 browser checks passed for scroll response, all three pinned chapters,
  image accessibility, title fills, typography movement, card reveals, keyboard
  focus, tablet navigation, live motion preferences, and the JavaScript fallback.
- Layout checks passed at 320, 390, 768, 1024, 1120, 1121, 1440, and 1920 CSS
  pixels. Both 600px and 1000px viewport heights were checked at 1440px width.
- The 95 navigation, room/gallery, directory, schedule, history, membership,
  and visit-preview checks passed with motion enabled and with `?rm=1`.
- All 20 model interaction, expanded-view, mobile, and retry checks passed
  with motion enabled.
- All 11 content smoke tests, JavaScript syntax checks, and whitespace checks
  passed. No browser JavaScript errors occurred in the motion checks.
- Desktop, tablet, and mobile screenshots were inspected. The user's in-app
  preview was refreshed after the changes.

The scripts, result logs, and screenshots are in `output/playwright/`, including
`check-motion.js`, `motion-results.txt`, `motion-flow-results.txt`,
`reduced-flow-results.txt`, and `motion-model-results.txt`.

Checks used Chromium; physical devices, Safari, and Firefox were not tested.
The visit form remains the existing explicitly labelled local preview.
The unrelated Blender fingerprint mismatch is documented in `CLEANUP-QA.md`;
neither model assets nor the backend were changed for this motion pass.
