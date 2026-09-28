# Core Culture visual QA — Campaign 02

## Direction carried forward

- Selected direction: **Floor in Motion**.
- The retained language is a near-black architectural grid, oversized condensed type, signal orange, compact technical labels, restrained editorial photography, and an obvious first-visit route.
- Per the revised brief, the hero is now campaign-image-led. The supplied interactive gym model has its own chapter immediately below the hero rather than competing with the opening message.

## Finished implementation

- Live preview: `http://127.0.0.1:8931/site/`
- Desktop proof, 1440 × 900: `output/playwright/core-culture-final-desktop.png`
- Mobile proof, 390 × 844: `output/playwright/core-culture-final-mobile.png`
- Reduced-motion full-page proof: `output/playwright/cc-campaign-v2-reduced-full-loaded.png`
- Thirteen new local WebP campaign images replace every user-facing photograph. Four of those are smoky, reference-guided scenes for the hero, barbell route, strength, and hybrid conditioning; none copy the supplied people, compositions, logos, text, or watermarks.

## Comparison with the chosen direction

- The compressed display type, dark structural frame, orange calls to action, technical metadata, and disciplined section rhythm remain faithful to the selected direction.
- The opening hierarchy is stronger for the new brief: statement and actions on the left, one atmospheric athlete image on the right, then a three-step first-visit route.
- The 3D model remains functional in the dedicated **See the floor** chapter with four viewpoints, orbit, zoom, reset, labels, expanded view, keyboard support, and the clearly marked estimates **64 × 60 ft training floor** and **96 × 60 ft overall**.
- Every space card now has its own image and the story, recovery, and first-visit chapters have distinct editorial frames.
- Motion now uses a staged hero reveal, image clip-and-scale entrances, restrained scroll drift, the kinetic word band, local section staggers, card/focus feedback, and schedule-entry transitions. Nothing essential depends on motion.

## Findings fixed during final QA

1. The desktop hero column and type scale were rebalanced so the three headline lines do not crop.
2. A duplicate fixed-header anchor offset was removed so **Explore the floor** lands on the intended chapter on mobile.
3. The mobile navigation now includes the floor plan and matches the page's 01–07 chapter numbering.
4. First-visit labels were raised to 11px and changed to a dark neutral for readable contrast on the pale surface.
5. Modal image captions now use the final concept names and do not imply unconfirmed parking, wings, or facilities.
6. The model's completed state now reports **Interactive model ready.** instead of retaining an intermediate loading message.

## Interaction, accessibility, and content checks

- The hero contains no model; `#plan` contains the single reusable live viewer.
- Navigation anchors, mobile menu, space rail, cards, dialogs, lightbox, schedule tabs/filters/session disclosures, local first-visit validation, and all model controls passed desktop and mobile interaction checks.
- The first-visit preview prevents submission, creates no booking, sends no request, and stores no personal data.
- No prices, testimonials, or confirmed facility/equipment inventory are published. All schedule, space, membership, and imagery claims are labeled sample, concept, illustrative, estimated, or to be confirmed.
- Alternative text accurately describes all new images; decorative assets remain silent.
- At 390px there is no document-level horizontal overflow. All campaign images, fonts, the GLB, and runtime assets return successfully.
- Reduced-motion mode keeps all content visible, disables smooth scrolling and decorative movement, and leaves the model user-loadable.

## Verification

- Automated suite: **17 passed, 0 failed**.
- JavaScript syntax checks passed for app, data, motion, model loader, and model viewer sources.
- Desktop and mobile browser consoles: **0 errors, 0 warnings**.
- No actionable P0, P1, or P2 visual or functional issues remain.

final result: passed
