"""Verify the final saved live revision and render both annotated views."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
FT = .3048
signs = [o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')]
assert len(signs) == 10
assert not bpy.data.libraries
assert not any(o.name.startswith(('Area pointer •', 'Area marker •', 'Floating description •')) for o in bpy.data.objects)
for root in signs:
    assert not root.constraints
    up = root.matrix_world.to_3x3() @ Vector((0,1,0))
    assert up.dot(Vector((0,0,1))) > .999
    cables = [c for c in root.children if c.name.startswith('Top suspension cable •')]
    assert len(cables) == 2
    for cable in cables:
        world_points = [cable.matrix_world @ v.co for v in cable.data.vertices]
        assert min(v.z for v in world_points) > root.location.z+.75*FT
    assert root['Bottom clearance (ft)'] >= 11.75
    assert len([c for c in root.children if c.type=='FONT']) == 2
print('FINAL_VERIFIED: 10 upright double-sided signs; 20 top cables; no floor leaders; no linked dependencies.', flush=True)
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == 'METAL'
for scene_name, filename in [('01 | CUTAWAY • furnished plan','suspended_signs_cutaway.png'),
                              ('02 | PLAN • orthographic','suspended_signs_plan.png')]:
    scene = bpy.data.scenes[scene_name]
    bpy.context.window.scene = scene
    scene.render.filepath = str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    print('FINAL_PREVIEW', filename, flush=True)
print('VERIFICATION_COMPLETE', flush=True)
