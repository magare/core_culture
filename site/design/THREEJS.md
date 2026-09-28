# Interactive Core Culture model

Implemented 22 September 2026; PDF layout revision 28 September 2026. Local preview:
`http://127.0.0.1:8931/site/#plan`.

## What is displayed

The website now draws real geometry with Three.js 0.186.0. It is not a model
photograph, panorama, or image sequence. The default view is the same roofless
architectural cutaway used for the previous website render. Upper exterior
walls and the roof are intentionally excluded so the training floor is visible.

The export has a 64 × 60 ft central training span within an **estimated**
96 × 60 ft overall footprint. It includes the revised room bays, single turf,
front racks, stair/office, ten top-suspended area signs, and eight visible
logo placements. The three floor-circle logos were removed with that
unsupported feature. The facade and presentation-title logos remain in the
Blender source outside the website cutaway.

## Export and preservation

- Source: `output/blender/core_culture_gym/Core_Culture_Gym_Layout_Aligned.blend`.
- Source scene: `07 | WEBSITE • architectural cutaway`.
- Exporter: `output/blender/core_culture_gym/export_web_model.py`.
- Output: `site/assets/models/core-culture-gym.glb` (4,382,628 bytes).
- 780 evaluated mesh objects, including instanced equipment and meshed text.
- 264,072 triangles; batching/compression without mesh decimation.
- 10 exported scene objects, 42 materials; signs are a separately toggleable group.
- Embedded accepted logo texture, resized to 1024 × 1024.
- Source file SHA-256 is checked before/after export and recorded in the manifest.
  No Blender save operation is performed; the user's open Blender state is untouched.

From the repository root on this Mac:

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" \
  --background output/blender/core_culture_gym/Core_Culture_Gym_Layout_Aligned.blend \
  --python-exit-code 1 \
  --python output/blender/core_culture_gym/export_web_model.py
npm --prefix site ci
npm --prefix site run build:viewer
npm --prefix site test
```

The exporter resolves the Blender scene into a temporary scene in a separate
background process. Objects are merged by logical group, and unused UVs are
removed from untextured meshes. EXT_meshopt_compression is decoded locally.
The runtime bundle, decoder, logo texture, and model need no CDN or account.
Licenses are in `assets/licenses/THREEJS-MESHOPT.txt` and the bundle's legal file.

## Realtime presentation

Four presets: overview, top view, free weights, and reception. Orbit/pan/zoom,
zoom buttons, reset, and a labels toggle work on the live scene. Expanded mode
moves the same viewer into a native modal rather than creating another renderer.

Orbit starts disabled so the model does not capture page scrolling. Enabling it
focuses the canvas. Arrow keys orbit, Shift+arrows pan, plus/minus zoom, Home
resets, and Escape returns to page scrolling. The expanded dialog can then be
closed with Escape, restoring focus to its trigger.

No camera animation or auto-rotation is used. Frames render only after a view,
material-visibility, or size change, and rendering pauses offscreen/when hidden.
The bundle/model load near the section; data-saver mode waits for an explicit
load click. Pixel ratio is capped at 1.5. Shadows are cached and recomputed only
when required; ambient occlusion gives equipment and walls contact depth.

This is a realtime interpretation of the Blender finishes, not a pixel-identical
Cycles render. Procedural shader noise is represented by base PBR finishes;
glass uses inexpensive alpha transparency, and mirrors use environment
reflections rather than reflecting the full gym. Printed decals have a small
depth bias and do not cast self-shadows. The measured geometry is not altered
to accommodate these material changes.

## Verification

- 17 automated tests pass, including core glTF validation with zero errors or
  warnings; the validator does not support EXT_meshopt, so every compressed
  buffer is also decoded and every position checked for finite coordinates.
- Export triangle count, embedded textures, source-file hash, and sign/logo
  metadata pass the model checks for the revised GLB.
- All four revised presets were visually inspected in Chromium. The widened
  free-weights view shows both red storage racks; the browser console reported
  zero errors and warnings.
- Keyboard orbit, pan, zoom, reset, and two-stage Escape behavior exercised.
- Label visibility toggle, native expanded dialog, one-canvas reuse, preserved
  custom camera, and focus restoration exercised.
- Blocked GLB download shows a retry/download message and removes the failed
  canvas. Unblocking and retrying successfully creates exactly one live canvas.
- Responsive checks at browser-reported CSS widths 360, 767, and 1440 found no
  horizontal page/viewer overflow. Mobile expanded dialog also fits its viewport.
- No physical mobile device, independent Safari/Firefox engine, or touch/pinch
  gesture test was completed. Pinch behavior comes from OrbitControls; the
  available browser automation did not support synthetic touch dispatch.

Screenshots are in `aesthetic-review/threejs/`: mobile viewer, reception, and
top view, with responsive-check records. Capture density follows the browser's
zoom/device ratio; these are UI verification images, not replacement assets.

## Remaining boundaries

The source remains an architectural design study, not a certified as-built
survey. The PDF dimensions the 25-ft roof centre, while the 20-ft eaves and
96-ft overall width are inferred. Unmeasured fitout and equipment remain
illustrative. See `output/blender/core_culture_gym/LAYOUT_ALIGNMENT.md`.
The existing website still contains labelled concept photographs and proposed
amenities beyond the modeled ground floor. No booking backend or deployment
was added in this update.

## API references

[Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html) and
[OrbitControls](https://threejs.org/docs/pages/OrbitControls.html). Rendering and
postprocessing options were verified against the installed, pinned package.
