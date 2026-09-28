# Gym layout PDF alignment

The current editable model is `Core_Culture_Gym_Layout_Aligned.blend`. It was
built from `Core_Culture_Gym_Aesthetic.blend` using the supplied eight-page
`Gym layout .pdf`; the earlier model remains intact. The live site uses the
scene `07 | WEBSITE • architectural cutaway` exported from this new file.

## Drawing measurements and model decisions

| PDF reference | Drawing evidence | Model treatment |
| --- | --- | --- |
| Pages 5 and 7 | Training-floor front and back elevations span 64 ft; page 4 plan shows side bays beyond this span. | Central span is x=16–80 ft, y=0–60 ft. |
| Pages 2 and 4 | Reception-side rooms total 5 + 5 + 6 = 16 ft; the left cardio/changing bay has no written width and is drawn about as wide. | Right bay is 16 ft. Left bay is **estimated at 16 ft**, giving an **estimated 96 × 60 ft overall**. The PDF does not state an overall width. |
| Page 4 | One narrow green turf strip is drawn. | Replaced two marked lanes and the unsupported 16-ft floor circle with one 50 × 6.5 ft strip. Turf length and position are visual estimates. |
| Page 5 | Front wall: 12 ft grey, 4 ft red rack, 32 ft grey, 4 ft red rack, 12 ft grey. Grey panels are 8 ft high; racks 7.5 ft high. | Rebuilt the 64-ft training-side wall finish and red shelves to that sequence. |
| Pages 6 and 8 | Two reception doors 3 × 9 ft; studio door 3 × 8 ft; cardio door 3 × 9 ft; two changing-room doors 3.5 × 8 ft. | Resized wall openings and door assemblies. Individual door offsets are estimated where the drawing gives no coordinate. |
| Page 7 | Four 9 × 4.5 ft back windows with 4-ft gaps plus a fifth unlabeled opening; grey vents above. | Added five back openings and five upper vents. First opening width, sill and vent levels are estimates. |
| Pages 5–8 | 25-ft roof centre; page 6 shows 9 + 11 ft side-wall bands. | Gable ridge is 25 ft, running front to back. Eaves are **inferred at 20 ft** from the side elevation. |
| Page 5 | Front air duct tapers from 2.5-ft diameter at the cardio end to 4 ft at the reception end. | Rebuilt the 64-ft duct with that taper. |
| Page 8 | Upper mirror 29 × 8 ft; yoga mat rack 6 × 4.5 ft, in 1.5-ft sections; exhaust fan above. | Added these features to the cardio/changing-side elevation. |
| Page 8 | Stair rises 6.5 ft, turns right and rises another 4 ft; elevated office is 16 × 8.5 ft in elevation. | Added two flights, landing, elevated route and office. Tread runs, walkway, office depth and fitout are estimates. |

The PDF's circle on page 6 is the duct vent shown in side elevation, not a
dimensioned floor marking. The prior model treated it as a 16-ft floor circle.
The new model removes that circle and its floor decals.

## Rebuild

From the repository root:

```sh
"/Applications/Blender.app/Contents/MacOS/Blender" --background \
  output/blender/core_culture_gym/Core_Culture_Gym_Aesthetic.blend \
  --python-exit-code 1 \
  --python output/blender/core_culture_gym/apply_pdf_layout.py

"/Applications/Blender.app/Contents/MacOS/Blender" --background \
  output/blender/core_culture_gym/Core_Culture_Gym_Layout_Aligned.blend \
  --python-exit-code 1 \
  --python output/blender/core_culture_gym/export_web_model.py

npm --prefix site run build:viewer
npm --prefix site test
```

`layout_alignment_report.json` records the source and output hashes. The new
file contains current `START HERE` and feature notes under Blender's Text
Editor. `layout_aligned_cutaway.png`, `layout_aligned_plan.png` and
`layout_aligned_back_elevation.png` are rendered review views from it.

This is a drawing-aligned design model. The overall width, unmarked fitout,
stair footprint, office depth, window sill and similar missing dimensions need
site measurements before construction use.
