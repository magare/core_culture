"""Recheck the live-saved file and render all six review cameras."""
import bpy, os, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT=Path(__file__).resolve().parent
assert len(bpy.data.scenes)==6
assert not bpy.data.libraries
assert len([i for i in bpy.data.images if i.source=='FILE' and i.packed_file])==4
assert len([o for o in bpy.data.objects if 'Asset type' in o])==41
assert len([o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')])==10
assert not any(o.name.startswith(('Area pointer •','Floating description •')) for o in bpy.data.objects)
# Recheck the retained overhead signs against the corrected, final geometry.
cut=bpy.data.scenes['01 | CUTAWAY • furnished plan']
bpy.context.window.scene=cut
bpy.context.view_layer.update()
sign_boxes=[]
for root in [o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')]:
    assert not root.constraints,root.name
    assert (root.matrix_world.to_3x3() @ Vector((0,1,0))).z>.999,root.name
    panel=next(c for c in root.children if c.name.startswith('Suspended panel •'))
    points=[panel.matrix_world @ Vector(v) for v in panel.bound_box]
    zmin,zmax=min(v.z for v in points),max(v.z for v in points)
    assert abs((zmax-zmin)/.3048-1.5)<.001,root.name
    assert zmin/.3048>=11.749,root.name
    cables=[c for c in root.children if c.name.startswith('Top suspension cable •')]
    assert len(cables)==2,root.name
    for cable in cables:
        assert min((cable.matrix_world @ v.co).z for v in cable.data.vertices)>zmax,cable.name
    assert len([c for c in root.children if c.type=='FONT'])==2,root.name
    screen=[world_to_camera_view(cut,cut.camera,p) for p in points]
    box=(min(p.x for p in screen),min(p.y for p in screen),max(p.x for p in screen),max(p.y for p in screen))
    assert 0<box[0]<box[2]<1 and 0<box[1]<box[3]<1,root.name
    for name,other in sign_boxes:
        assert not (min(box[2],other[2])>max(box[0],other[0]) and min(box[3],other[3])>max(box[1],other[1])),(root.name,name)
    sign_boxes.append((root.name,box))
print('SIGN_CHECKS_PASSED: 10 compact upright double-sided signs; 20 cables above panels; no sign/sign overlap in the cutaway camera.',flush=True)
for o in bpy.data.objects:
    assert all(math.isfinite(v) for row in o.matrix_world for v in row),o.name
    assert all(abs(v)>1e-8 for v in o.scale),o.name
for s in bpy.data.scenes:
    assert s.unit_settings.system=='IMPERIAL' and s.unit_settings.scale_length==1
bpy.context.window.scene=bpy.data.scenes['03 | EXTERIOR • entrance']
bpy.context.view_layer.update()
pot=bpy.data.objects['Exterior entry plant planter']
shelf=bpy.data.objects['Entrance shoe shelf • static batch']
pp=[pot.matrix_world @ v.co for v in pot.data.vertices]
sp=[shelf.matrix_world @ v.co for v in shelf.data.vertices]
bottom=min(v.z for v in pp)
assert abs(bottom-max(v.z for v in sp))<1e-5
for p in [v for v in pp if abs(v.z-bottom)<1e-5]:
    assert min(v.x for v in sp)<p.x<max(v.x for v in sp)
    assert min(v.y for v in sp)<p.y<max(v.y for v in sp)
bpy.context.window.scene=cut
os.environ['GYM_AUDIT_LABEL']='after'
audit_path=OUT/'audit_proportions.py'
exec(compile(audit_path.read_text(),str(audit_path),'exec'),{'__file__':str(audit_path)})
print('FINAL_PACKAGE_CHECKS_PASSED: 6 scenes; 41 equipment/fixture instances; 10 hanging signs; 4 packed images; no linked libraries.',flush=True)
if os.environ.get('GYM_AUDIT_RENDER','1')=='0':
    print('FINAL_SAVED_MODEL_CHECKS_COMPLETE',flush=True)
    raise SystemExit(0)
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scenes=[('01 | CUTAWAY • furnished plan','audited_cutaway.png',100),
        ('02 | PLAN • orthographic','audited_floor_plan.png',100),
        ('06 | AUDIT • verified plan dimensions','audited_dimensions.png',100),
        ('03 | EXTERIOR • entrance','audited_entrance.png',75),
        ('04 | INTERIOR • free weights','audited_free_weights.png',75),
        ('05 | INTERIOR • HYROX','audited_hyrox.png',75)]
for name,filename,percent in scenes:
    if os.environ.get('GYM_RENDER_ONLY') and filename!=os.environ['GYM_RENDER_ONLY']:continue
    s=bpy.data.scenes[name];bpy.context.window.scene=s
    original=(s.render.resolution_percentage,s.cycles.samples,s.render.filepath)
    s.render.resolution_percentage=percent
    if percent<100:s.cycles.samples=24
    s.render.filepath=str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    s.render.resolution_percentage,s.cycles.samples,s.render.filepath=original
    print('VERIFIED_RENDER',filename,flush=True)
print('AUDITED_PACKAGE_COMPLETE',flush=True)
