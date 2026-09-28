"""Verify the saved aesthetic model, then export final presentation images."""
import bpy, os, json, hashlib
from array import array
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
# Execute only the definition, not the mutation script.
source=(OUT/'refine_aesthetics.py').read_text()
signature_source=source[source.index('def geometry_signature'):source.index('\noriginal=bpy.context.window.scene')]
exec(signature_source)
baseline=json.loads((OUT/'aesthetic_geometry_baseline.json').read_text())
original=bpy.context.window.scene
evaluation=bpy.data.scenes.new('__VERIFY_AESTHETIC')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation;bpy.context.view_layer.update()
changed=[name for name,v in baseline.items() if name not in bpy.data.objects or geometry_signature(bpy.data.objects[name])!=v]
assert not changed,changed
assert len(bpy.data.scenes)==9 # eight saved views plus this verification scene
assert len([o for o in bpy.data.objects if 'Asset type' in o])==41
assert len([o for o in bpy.data.objects if o.name.startswith('OFFICIAL LOGO •')])==13
for root in [o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')]:
    cables=[o for o in root.children if o.name.startswith('Top suspension cable •')]
    assert len(cables)==2
    for cable in cables:assert min((cable.matrix_world@v.co).z for v in cable.data.vertices)>root.location.z+.75*.3048
assert len([o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')])==10
logo=bpy.data.images['CORE CULTURE • official cleaned transparent logo']
assert logo.packed_file and logo.channels==4
assert len({o.data.as_pointer() for o in bpy.data.objects if o.name.startswith('OFFICIAL LOGO •')})==1
bpy.context.window.scene=original;bpy.data.scenes.remove(evaluation)
os.environ['GYM_AUDIT_LABEL']='aesthetic'
p=OUT/'audit_proportions.py';exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
print('SAVED_AESTHETIC_VERIFIED: dimensions, 41 equipment, 10 top-hung signs, 13 logos, protected meshes preserved.',flush=True)
if os.environ.get('GYM_AESTHETIC_RENDER','1')=='0':raise SystemExit(0)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
views=[('07 | WEBSITE • architectural cutaway','aesthetic_cutaway.png'),('04 | INTERIOR • free weights','aesthetic_free_weights.png'),
       ('08 | DETAIL • reception','aesthetic_reception.png'),('03 | EXTERIOR • entrance','aesthetic_entrance.png'),('05 | INTERIOR • HYROX','aesthetic_hyrox.png')]
for name,filename in views:
    s=bpy.data.scenes[name];bpy.context.window.scene=s;s.cycles.device='GPU';s.cycles.samples=64;s.render.resolution_percentage=100
    s.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
    print('FINAL_AESTHETIC_RENDER',filename,flush=True)
