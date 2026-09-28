# Core Culture — supplied-logo update

Latest model: **Core_Culture_Gym_Branded.blend**.

The live pre-edit session is preserved in `Core_Culture_Gym_before_logo_update.blend`; `Core_Culture_Gym_before_logo_apply.blend` captures the live session again immediately before application. The proportion-audited edition is also retained. This branding pass does not change the building, equipment layout, room dimensions or hanging signs.

## Artwork and treatment

`core_culture_logo_original.jpg` is a preserved copy of the supplied image beside the model. `core_culture_logo_transparent.png` is the cleaned 1254 × 1254 RGBA texture, prepared with the built-in image-editing tool using the prompt below. The cleaned artwork is packed into the Blender file, along with the previous four building references; no external texture file is required to display the logos.

The source image is only 150 × 150 pixels. The high-resolution cleanup is an image-assisted reconstruction of that reference, not an original vector master. It retains the curved CORE CULTURE / GYM wording, two lightning bolts, interlocking CC composition and silver finish. For strict production-brand fidelity, a higher-resolution or vector original would be preferable.

All placements share one square UV mesh and the same image, without stretching. Signage uses a restrained silver finish. Floor, lane and mat artwork use a rough, non-metallic print material. Alpha transparency removes the black rectangular background. Round, softly edged graphite backings provide contrast on the facade, reception wall and desk, central floor, and presentation title. The central floor graphic is a thin inlay; the 16 ft training circle is unchanged.

## Placements

| Location | Artwork width | Treatment |
| --- | ---: | --- |
| Entrance facade | 5.8 ft | Silver artwork on a 6.1 ft round backing |
| Reception feature wall | 4.6 ft | Silver artwork on a 5 ft round backing |
| Reception desk | 2.15 ft | Compact silver artwork on a 2.45 ft round backing |
| Central training circle | 8 ft | Matte print within a 9.2 ft dark floor inlay |
| HYROX lanes 01 and 02 | 2.1 ft each | Transparent matte print on turf |
| Six group-exercise mats | 0.7 ft each | Small transparent matte print |
| Presentation title | 3.6 ft | Round presentation mark outside the building |

The old typed CC marks, improvised facade ring/wording and mat placeholders are replaced. Functional names such as CARDIO, HYROX, RECEPTION and THE FREE WEIGHT SECTION are not logos and remain unchanged. The overhead signs retain their compact size and top suspension.

The plan-only CENTRAL TRAINING label moves below the floor emblem to avoid covering it. Scene 06 hides the central/lane branding overlays so the dimension chains stay clear. Existing user visibility choices are otherwise preserved.

For editing, find `BRAND` subcollections in the corresponding area collection. Move a `BRAND ASSEMBLY` empty to move the complete logo and backing together. Use Material Preview or Rendered shading to see the texture and transparency. `logo_update_report.json` records placements and preservation checks; `verify_official_logo.py` checks the saved package.

## Image-editing prompt

Built-in image editing was used, not a CLI/API fallback. The sole edit target was the supplied JPEG.

> Use case: background-extraction.
> Asset type: faithful transparent logo texture for native Blender architectural signage, NOT a logo redesign and NOT a mockup.
> Input image 1 is the EDIT TARGET and the sole authoritative brand reference. Extract the complete Core Culture Gym logo from its black background onto a genuinely transparent RGBA background. Clean up the very low resolution edges carefully at high resolution, preserving the exact design and proportions: curved uppercase text CORE CULTURE around the upper perimeter, GYM at the bottom, the two diagonally interlocked gothic/angular C letters, and exactly one lightning bolt on each lower side. Retain the silver/chrome embossed metallic appearance, black inner shading that belongs within the metal, and the existing spacing/orientation. Text verbatim: "CORE CULTURE", "GYM", central "CC". Preserve recognizable letter shapes, outlines, internal cutouts, bevels and silhouette. Do not invent a new monogram or substitute plain typed CC. No solid backdrop, no black square, no white rectangle, no drawn checkerboard, no circular border, no extra lettering, no floor or wall or scene. Straight-on square asset, entire mark centered with a small even transparent margin. This is an edit/extraction of the supplied image, not a different version of the brand.
