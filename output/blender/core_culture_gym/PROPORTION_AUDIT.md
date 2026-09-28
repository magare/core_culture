# Core Culture — proportion audit

The revised model is `Core_Culture_Gym_Audited.blend`. The previous live session is preserved in `Core_Culture_Gym_before_proportion_audit.blend`.

This audit separates **dimensions written on the supplied plan**, **dimensions inferred from its drawing**, and **unmeasured/proposed details**. It does not certify that every object matches the real building.

## Plan dimensions

The written 100 × 60 ft overall dimension is interpreted as the exterior wall-finish outline. The four-foot passages are modeled as clear space, including skirting. Room-bay labels are gross planning widths, not usable internal room widths. Confirm this interpretation against a site measurement before construction use.

| Check | Earlier model | Revised model |
| --- | ---: | ---: |
| Floor/slab planning footprint | 100 × 60 ft | 100 × 60 ft |
| Main exterior wall-body span | 100.45 × 60.45 ft | Contained in 100 × 60 ft finish outline |
| Zoned gross floor area | 6,000 sq ft | 6,000 sq ft; no overlapping floor zones |
| Central circle | 16 ft diameter | 16 ft diameter |
| Circle to left partition, including skirting | About 21.735 ft | 22 ft |
| Circle to east passage edge | 22 ft | 22 ft |
| AC centreline to circle north edge | 18 ft | 18 ft |
| Circle south edge to HYROX south boundary | 18 ft | 18 ft |
| East passage, including skirting | About 3.735 ft | 4 ft clear |
| South passage, including skirting | About 3.735 ft | 4 ft clear |
| Turf to circle | 0.5 ft overlap | 0.53 ft separation |

The circle and AC axis moved north by 0.53 ft to retain both 18 ft offsets after allowing for the south wall finish and a clear four-foot passage. The circle is now at (50, 30.53) ft; the AC axis is at y = 56.53 ft. The 20/60/4/16 ft horizontal bay split is retained as a planning grid. Only the 60 ft core follows directly from the written 22 + 16 + 22 ft chain; the other room splits were inferred from the image.

Scene **06 | AUDIT • verified plan dimensions** displays the dimension chains separately from the normal presentation labels.

## Corrections made

- Removed the turf/circle overlap and adjusted lane graphics to the smaller turf depth.
- Corrected two SkiErg/partition intersections and equipment resting heights.
- Rebuilt nine doors around real hinge pivots, with aligned jambs, frames and handles. Shifted openings away from perpendicular wall corners. Door heights remain an estimate.
- Removed the two generated south-wall openings that were not supported by the plan; retained the side-wall passage connections and the shown east-side entrances. This is a plan reconstruction, not an egress assessment.
- Resized four equipment categories against published reference envelopes, with the rower rail extended without distorting its round flywheel.
- Moved stair climbers back from the treadmill rear-clearance space; the model now has approximately 2.03 m between the nearest rear treadmill edge and a stair climber.
- Moved the women's locker row and vanity tops clear of the adjusted perimeter wall. Repositioned both changing benches to leave approximately 3 ft between the benches and the locker fronts/cubicle fronts.
- Trimmed cubicle partitions and the studio's terminal mirror to the adjoining walls. Moved the reception plant clear of the partition.
- Seated the exterior planter on the shoe shelf and moved its base fully inside the shelf's support footprint.
- Corrected reversed mesh normals. Repeated equipment still shares mesh data; new repeated south-wall cladding is batched.
- Preserved the smaller, top-suspended signs. No oversized callouts or floor-pointing leaders were restored.

## Equipment reference dimensions

These are **representative reference envelopes**, not a confirmed list of your installed machines and not manufacturer-detailed replicas. The sources were checked on 22 September 2026.

| Model category | Earlier local envelope, W × L × H | Revised reference |
| --- | --- | --- |
| Treadmill | 37.2 × 77.4 × 50.4 in | 36.25 × 82.25 × 56 in; 22 × 60 in belt |
| Stair climber | 37.0 × 50.7 × 64.6 in | 34 × 58 × 79 in |
| SkiErg with floor stand | 38.4 × 55.8 × 90.4 in | 23.5 × 50 × 85 in |
| Rower | 24 × 80.64 in footprint | 24 × 96 in footprint; 14 in seat height |

References: [Life Fitness Integrity+ specifications](https://support.lifefitness.com/hc/en-us/articles/16340135145623-Life-Fitness-Integrity-Treadmill-Specifications), [StairMaster 8Gx specifications](https://www.corehandf.com/products/stairmaster-8gx-1), [Concept2 SkiErg specifications](https://www.concept2.com/ergs/skierg), and [Concept2 RowErg specifications](https://www.concept2.com/ergs/rowerg).

Concept2 specifies a 9 × 4 ft use envelope for its rower. The two modeled rowers occupy separate 9 × 4 ft review rectangles outside the east passage. The treadmill rear space uses a conservative 2 m layout target, consistent with the [manufacturer's published positioning guidance](https://www.lifefitness.com.au/wp-content/uploads/2015/03/CLST_Integrity_Treadmill_User_manual_1_736_1370510166.pdf). The final layout still requires the manuals for the actual installed machines; this is not a safety or regulatory certification.

## Still unverified or missing

1. **Ceiling and steelwork heights.** The 18 ft eaves and 21 ft ridge remain estimates. The photograph supports the exposed-truss style, not these exact dimensions.
2. **Staircase and upper platform.** Visible in the ceiling photo but absent from the floor plan. Their footprint, rise, location and upper-level dimensions are unknown; they remain omitted instead of being positioned arbitrarily.
3. **Window band, wall vents and HYBRID TRAINING wall.** Visible in the photo, but their wall orientation, opening sizes and position in the plan are unconfirmed. These are not yet accurately reconstructed.
4. **Actual equipment inventory/layout.** The photo shows training racks, but the exact count/model and the mapping between photo and plan are unconfirmed. The current equipment arrangement remains a proposal.
5. **Undimensioned room boundaries.** Cardio/washroom splits, reception, three support rooms and the studio follow the plan proportions; their individual dimensions are inferred, not explicitly measured. Support-room functions are unspecified.
6. **Fit-out sizes.** Wall thickness, door heights, toilets, lockers, furniture, mirrors, signage, duct diameter, canopy, glazing and shutter are conceptual dimensions. Plausibility and modeled clashes have been checked; exact correspondence to your gym has not.
7. **Measurement convention.** Confirm whether the 100 × 60 ft refers to clear internal space, structural centre lines or the external faces. This revision consistently uses the exterior finish outline.

For an as-built version, provide the ceiling/eaves/ridge measurements, wall thickness and measurement convention, door/window measurements, an equipment schedule, and a marked plan showing the staircase/platform and the windowed wall.

## Verification files

`proportion_audit_before.json` and `proportion_audit_after.json` contain the geometric inventory, local/world bounding dimensions, floor zones and hard-intersection results. `proportion_corrections.json` records the changes and sources. `audit_proportions.py` checks the explicit dimension chains, zone coverage, equipment/wall and fixture/wall clashes, equipment/equipment intersections and equipment floor contact. Tests use a 0.001 ft dimensional tolerance; that is a modeling tolerance, not survey accuracy.

Unknown site dimensions are intentionally not labeled as passed. The model is a spatial design visualization, not a surveyed as-built, structural design or accessibility/fire/egress compliance drawing.

The final saved-file checks also verify that all ten signs are upright and double-sided, that both cables start above each panel, and that the compact panels do not overlap each other in the cutaway camera. The exterior planter's base is checked against its supporting shelf. All six review cameras were rendered for visual review.
