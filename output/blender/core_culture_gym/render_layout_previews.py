"""Render review views from the saved PDF-aligned model without saving it."""
import bpy
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
for key, filename in (
    ('01 | CUTAWAY', 'layout_aligned_cutaway.png'),
    ('02 | PLAN', 'layout_aligned_plan.png'),
    ('03 | EXTERIOR', 'layout_aligned_exterior.png'),
):
    scene = next(s for s in bpy.data.scenes if s.name.startswith(key))
    bpy.context.window.scene = scene
    scene.render.resolution_percentage = 55
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(out / filename)
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 12
        scene.cycles.use_denoising = True
    bpy.ops.render.render(write_still=True)
    print('PDF_LAYOUT_PREVIEW', scene.name, scene.render.filepath, flush=True)

# The PDF's back elevation shows a 64-ft training-floor window band. The
# project's entrance camera does not face it, so add a temporary review view.
scene = next(s for s in bpy.data.scenes if s.name.startswith('03 | EXTERIOR'))
bpy.context.window.scene = scene
camera_data = bpy.data.cameras.new('PDF back elevation review')
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 72 * .3048
camera = bpy.data.objects.new('PDF back elevation review camera', camera_data)
scene.collection.objects.link(camera)
camera.location = Vector((48, -100, 13)) * .3048
target = Vector((48, 0, 13)) * .3048
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
scene.render.filepath = str(out / 'layout_aligned_back_elevation.png')
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_cavity = True
scene.render.resolution_percentage = 80
bpy.ops.render.render(write_still=True)
print('PDF_LAYOUT_PREVIEW', 'back elevation', scene.render.filepath, flush=True)
