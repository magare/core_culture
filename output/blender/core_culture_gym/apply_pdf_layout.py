"""Build a new Core Culture gym revision from the supplied layout PDF.

Open Core_Culture_Gym_Aesthetic.blend in background Blender and run this file.
The prior source stays intact; the revised Blender project is saved separately.
"""
import bpy
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path(bpy.data.filepath).resolve()
EXPECTED_SOURCE = ROOT / 'Core_Culture_Gym_Aesthetic.blend'
TARGET = ROOT / 'Core_Culture_Gym_Layout_Aligned.blend'
if SOURCE != EXPECTED_SOURCE.resolve():
    raise RuntimeError(f'Open the expected source before applying this pass: {EXPECTED_SOURCE}')
source_sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

for filename in (
    'apply_layout_width.py',
    'apply_layout_floor.py',
    'apply_layout_stair_office.py',
    'apply_layout_shell.py',
):
    print('PDF_LAYOUT_PASS_START', filename, flush=True)
    runpy.run_path(str(ROOT / filename), run_name='__main__')
    print('PDF_LAYOUT_PASS_DONE', filename, flush=True)

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != source_sha256:
    raise RuntimeError('The source Blender file changed during the layout pass')

cutaway = bpy.data.scenes['01 | CUTAWAY • furnished plan']
website = bpy.data.scenes['07 | WEBSITE • architectural cutaway']
for scene in bpy.data.scenes:
    scene['Layout reference'] = 'Gym layout .pdf, supplied 2026-09-28'
    scene['Layout status'] = ('Dimensioned central floor and features aligned; '
                              '16-ft cardio/changing bay and overall width inferred.')

bpy.data.objects['Audit legend'].data.body = 'PDF LAYOUT  /  CENTRAL FLOOR + CIRCULATION'
bpy.data.objects['Audit caveat'].data.body = (
    'OVERALL WIDTH, LEFT BAY AND UNDIMENSIONED DETAILS ARE ESTIMATES')
bpy.data.scenes['05 | INTERIOR • HYROX'].name = '05 | INTERIOR • training floor'
bpy.data.scenes['06 | AUDIT • verified plan dimensions'].name = '06 | LAYOUT • dimension review'

old_guide = bpy.data.texts['START HERE • model guide & assumptions']
old_guide.name = 'HISTORICAL • pre-PDF model guide'
current_guide = bpy.data.texts.get('START HERE • PDF layout aligned')
if current_guide is None:
    current_guide = bpy.data.texts.new('START HERE • PDF layout aligned')
current_guide.write(
    'CORE CULTURE / PDF LAYOUT ALIGNED MODEL\n\n'
    'Open scene 01 for the furnished cutaway, 02 for the floor plan, and 06 '
    'for the dimension chain. Scene 07 supplies the website GLB.\n\n'
    'The PDF dimensions the central training span as 64 x 60 ft and the '
    'reception-side bay as 16 x 8 ft split 5 + 5 + 6 ft. The left cardio / '
    'changing bay is undimensioned and drawn at approximately the same width '
    'as the reception bay. This model uses 16 ft for that bay, giving an '
    'INFERRED 96 x 60 ft overall footprint. Do not treat the outside width '
    'as a field measurement.\n\n'
    'See PDF LAYOUT ALIGNMENT, PDF PAGE 8 STAIR AND OFFICE PLACEMENT, and '
    'the external LAYOUT_ALIGNMENT.md for measured versus inferred features. '
    'The text named HISTORICAL pre-PDF model guide and the older audit files '
    'describe a superseded concept. Equipment and other unmeasured fitout '
    'are illustrative.\n'
)

if bpy.context.window:
    bpy.context.window.scene = cutaway
bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET), compress=True)

report = {
    'source_blend': SOURCE.name,
    'source_sha256': source_sha256,
    'output_blend': TARGET.name,
    'output_sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    'footprint_ft': [96, 60],
    'footprint_confidence': 'inferred from 64-ft central floor, 16-ft reception bay, equal drawn side bays',
    'central_training_floor_ft': [64, 60],
    'roof_center_ft': 25,
    'source_pdf': '/Users/magare/Downloads/Gym layout .pdf',
    'cutaway_scene': cutaway.name,
    'website_scene': website.name,
}
(ROOT / 'layout_alignment_report.json').write_text(json.dumps(report, indent=2) + '\n')
print('PDF_LAYOUT_MODEL_SAVED', json.dumps(report), flush=True)
