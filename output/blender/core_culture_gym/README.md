# Core Culture gym

**Current PDF-aligned model:** open `Core_Culture_Gym_Layout_Aligned.blend`.
It follows the supplied gym layout's 64 × 60 ft central training floor, room
and door sizes, front racks, roof profile, back windows, and side-elevation
stair/office details. The undimensioned left bay is estimated at 16 ft, so the
96 × 60 ft overall footprint is also an estimate. See
[`LAYOUT_ALIGNMENT.md`](LAYOUT_ALIGNMENT.md) for the measured/inferred table,
rebuild steps, and current render previews. The site GLB is exported from this
file's website scene.

## Earlier concept editions

The following notes describe preceding models. Their 100 × 60 ft outline,
16-ft floor circle, two turf lanes, and 18/21-ft roof are superseded by the
PDF-aligned revision above.

`Core_Culture_Gym_Branded.blend` is the earlier supplied-logo edition. Thirteen branding positions use the cleaned, transparent Core Culture emblem. See `LOGO_UPDATE.md` for placement sizes, artwork provenance and editing instructions. `Core_Culture_Gym_before_logo_update.blend` preserves the live session before this change. The `branded_*.png` files preview that edition.

`Core_Culture_Gym_Audited.blend` is the preceding proportion-checked edition; the branded edition preserves its dimensions and compact ceiling-hung signs. `PROPORTION_AUDIT.md` explains the corrections, sources and unverified site details. The earlier live session is preserved in `Core_Culture_Gym_before_proportion_audit.blend`.

The explicit plan dimensions are checked: 100 × 60 ft exterior finish outline, 16 ft circle, 22 ft offsets on both sides, 18 ft AC-axis/HYROX-edge offsets and 4 ft clear passages. The model's circle and AC axis moved north 0.53 ft to preserve the drawn offsets while allowing for the perimeter wall. Room-bay widths are gross planning zones, not clear internal room dimensions. Confirm the plan's measurement convention before using this for construction.

Corrections cover turf/circle overlap, equipment scale and floor contact, wall clashes, door pivots/frames, washroom bench space and mirror/plant intersections. Four equipment categories use published representative envelopes; actual brands/layout remain unconfirmed. Staircase/platform position, the photographed window wall, ceiling measurements and other undimensioned site details remain unresolved and are explicitly listed in the audit.

Proportion-audit previews: `audited_cutaway.png`, `audited_floor_plan.png` and `audited_dimensions.png`; current branded views use the `branded_` prefix. Scene **06 | AUDIT • verified plan dimensions** displays the dimensional chains. Detailed checks are in `proportion_audit_after.json` and the branded recheck `proportion_audit_branded.json`; changes are in `proportion_corrections.json`. `fix_proportions.py` and `audit_proportions.py` are the correction and verification scripts.

The CUTAWAY scene has ten upright, double-sided hanging signs: cardio, weight training, HYROX, reception, group exercise, men's washroom, women's washroom, central training, support rooms and passage. Each sign has two cables attached ABOVE its panel, ending at a short retained roof-level mounting member. The remainder of the roof is hidden for visibility. These are conceptual mounting details based on the estimated ceiling height, not construction specifications.

The signs are now 1.5 ft high and 6–10.2 ft wide, with 11.75–12.25 ft beneath them. Their combined face area is 85% smaller than the previous callouts. Titles are single-line, with no subtitles, floor pointers or floor markers. They stay physically upright while orbiting the model rather than tilting toward the saved camera. The PLAN scene uses compact horizontal labels so the names remain readable directly overhead. Exterior and close-up interior scenes keep their original architectural presentation.

Toggle `22 | SUSPENDED AREA SIGNS` or `22 | COMPACT PLAN LABELS` to show/hide the respective labels. Move a `HANGING SIGN` Empty to move the complete panel-and-suspension assembly. Select a text object and press Tab to edit; each hanging sign has separate front and reverse text objects.

`Core_Culture_Gym_Suspended_Signs.blend` and `suspended_signs_*.png` are the preceding signage-only revision. That revision preserved all 570 non-label objects; the later proportion audit intentionally corrects some geometry and placements. `Core_Culture_Gym_before_suspended_signs.blend` preserves the session before the signage revision. `Core_Culture_Gym_Labeled.blend` and `labeled_*.png` are the earlier oversized-callout version.

The optimized edition reduces scene objects from 1,985 to 570, unique mesh datablocks from 1,790 to 300, and live bevel modifiers from 862 to 212. Evaluated cutaway triangles fall from 441,104 to 260,840 (41%). Rendered viewport previews use 16 samples with denoising; the final 40-sample limit and output resolutions are retained.

Static roof, trim, grille and joint details are consolidated into labeled meshes. Their original part names are recorded in Custom Properties. To split a batch, enter Edit Mode and choose Mesh → Separate → By Loose Parts. All 41 equipment instances remain individually movable; room areas, equipment transforms, camera transforms and all four packed reference images were checked against the live-session snapshot.

Baking static detail increases the saved file from 3.82 MB to 4.38 MB while reducing evaluated geometry and modifier work. The before/after scene profiles and preservation checks are in `profile_before.json`, `profile_after.json` and `optimization_report.json`. `optimized_cutaway.png` and `optimized_hyrox.png` verify the performance edition visually.

Use the scene selector at the top right to switch views:

1. **CUTAWAY** — overview of the room layout and equipment.
2. **PLAN** — an orthographic floor plan with overall dimensions.
3. **EXTERIOR** — enclosed building, entrance glazing, canopy and signage.
4. **INTERIOR • free weights** — mirrors, dumbbell racks and exposed ductwork.
5. **INTERIOR • HYROX** — training lanes and the exposed ceiling structure.
6. **AUDIT • verified plan dimensions** — the plan's explicit dimensional chains, without area-label panels.

Press Numpad 0 to enter or leave the scene's camera. Equipment, floors, walls, roof, lighting and labels are organized in named collections. Repeated equipment shares mesh data; make an object single-user before changing only one copy.

The model uses the supplied plan's 100 × 60 ft footprint, 4 ft passage and 16 ft central circle. The remaining room boundaries follow the plan proportions. Eaves are estimated at 18 ft, the roof ridge at 21 ft, and internal partitions at 10 ft. Equipment selection and placement, furniture and washroom fixtures are proposed arrangements.

The fourth reference informed the exposed trusses and hanging lights. Its staircase/upper platform, window band and exact training-rack arrangement cannot be accurately located from the supplied floor plan. These remain unresolved, not silently treated as verified.

All four building reference images, the cleaned transparent logo and the fonts are packed into the branded Blender file. A copy of the original supplied JPEG is also retained beside the file as `core_culture_logo_original.jpg`. Further modeling notes are in the `START HERE` text inside Blender and in `MODEL_GUIDE.txt`.

All PNG previews are rendered directly from their corresponding Blender model. `build_gym.py` and `model_validation.json` describe the initial model; consult the newer audit files for the current revision.
