# Image, model, and font provenance

## Accepted branding and actual 3D geometry

`assets/images/core-culture-logo.png` is a small derivative of the accepted
transparent CC logo already used in the Blender project. The accepted larger
asset was previously reconstructed from the user-supplied low-resolution logo;
it is not an original vector master.

`assets/models/core-culture-gym.glb` is exported from
`output/blender/core_culture_gym/Core_Culture_Gym_Layout_Aligned.blend`, scene 07.
It contains actual mesh geometry, PBR finishes, and embedded logo textures.
No rendered images are used as substitutes for the interactive model.
See `model-manifest.json` beside the GLB for the source hash and export counts,
and [THREEJS.md](THREEJS.md) for the export procedure and material limitations.

The earlier `model-cutaway.webp`, `model-weights.webp`, and
`model-reception.webp` remain as historical local renders; the model section
no longer uses them. Its current views are rendered live by Three.js.

## Concept photography

Created for the September 2026 editorial redesign with the built-in ImageGen
tool. All seven images are original conceptual campaign/architectural visuals,
not verified photography of the actual club. That distinction is disclosed on
the site and in room details.

Each original is 1536 × 1024 PNG. Site versions are WebP, encoded with cwebp at
quality 83. Original generated files were preserved. No remote image hosting is
required.

## Art direction and generation briefs

Shared direction: photorealistic premium sports/architectural editorial,
brutalist concrete and steel, tactile black equipment, natural light, warm
grey/bronze grading, restrained composition, no neon, text, logos, or watermarks.

| Site asset | Generation brief | Original filename |
| --- | --- | --- |
| hero.webp | Low-angle athlete driving a weighted black sled on dark turf. Athlete in right third; entire left half dark and clear for headline. Industrial windows, warm natural light shaft, realistic technique, subtle film grain. | exec-e494f382-cb25-4856-9ba4-80da2a7a025c.png |
| movement.webp | Woman in terracotta training top and black leggings doing a controlled lateral lunge. Full figure, industrial studio, diagonal afternoon light, natural proportions. | exec-4b6c7a7b-8552-4c32-902d-447ccc5a4059.png |
| recovery.webp | Serene charcoal basalt recovery room. Circular brushed stainless cold plunge, narrow daylight shaft, walnut slats, stone bench, cream towels, no people. | exec-3cd1ccc8-2e29-470b-96c7-f53840888770.png |
| strength.webp | Organized strength floor, matte black power racks and dumbbells, high concrete columns, double-height steel windows, warm natural daylight, no people. | exec-4f162611-1512-4008-a5cd-a2cfb195cedc.png |
| lounge.webp | Members lounge and reception. Walnut communal table, black chairs, steel coffee counter, cream sofa, olive tree, warm plaster and afternoon sunlight. | exec-1085ca7e-b35b-47ee-95b8-c1bf9ab38e2e.png |
| cardio.webp | Orderly cardio room with matte black treadmills and foreground rowing machines along steel-framed windows overlooking a courtyard. Warm grey, silver, black; no people. | exec-a5c34b73-7a2f-4e48-abbb-07df09db01c9.png |
| arrival.webp | Low-rise concrete club exterior at dusk, recessed glass entrance, bronze panels, broad step-free path, landscaped spacious parking with two understated cars. | exec-730546fc-601c-41ef-9ed9-07102ff4ac05.png |

Original directory:
`/Users/magare/.codex/generated_images/01a0c789-d14a-7840-8232-7d672b2029b0/`.

## Fonts

Barlow Condensed 600 and Manrope 400/600 were obtained from Google Fonts and are
self-hosted in `assets/fonts/`. Their respective SIL Open Font License files are
included alongside them. No Google Fonts request is made at runtime.
