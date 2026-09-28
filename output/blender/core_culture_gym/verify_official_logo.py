"""Check the saved branded Blender model and render review views."""
import bpy, os, json, math, hashlib
from array import array
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent
FT=.3048
assert len(bpy.data.scenes)==6
assert not bpy.data.libraries
assert len([o for o in bpy.data.objects if 'Asset type' in o])==41
assert len([o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')])==10
assert not any(o.type=='FONT' and o.data.body.strip() in {'CC','CORE CULTURE','GYM'} for o in bpy.data.objects)
decals=[o for o in bpy.data.objects if o.name.startswith('OFFICIAL LOGO •')]
assert len(decals)==13
assert len({o.data.as_pointer() for o in decals})==1
required_images={
    '806299212_18087386489438400_7001765476852721714_n.jpg',
    '806299245_18087386486438400_8726183399223928327_n.jpg',
    'codex-clipboard-282e20e2-b4a5-49a7-ace7-e58382ba158a.png',
    'WhatsApp Image 2026-09-21 at 5.05.08 PM.jpeg',
    'CORE CULTURE • official cleaned transparent logo',
}
assert required_images.issubset({i.name for i in bpy.data.images if i.source=='FILE' and i.packed_file})
image=bpy.data.images['CORE CULTURE • official cleaned transparent logo']
assert image.packed_file and image.channels==4
pixels=list(image.pixels)
assert min(pixels[3::4])==0 and max(pixels[3::4])==1
for x,y in [(0,0),(0,image.size[1]-1),(image.size[0]-1,0),(image.size[0]-1,image.size[1]-1)]:
    # Permit one 8-bit alpha step from the generated asset's soft-edge quantization.
    assert pixels[4*(y*image.size[0]+x)+3]<=1/255+1e-6
for o in decals:
    assert max(o.scale)-min(o.scale)<1e-6
    assert len(o.data.uv_layers)==1 and len(o.data.polygons)==1
    assert o.parent and 'Official logo placement' in o.parent
    mat=o.material_slots[0].material
    textures=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE']
    assert len(textures)==1 and textures[0].image==image
    assert any(link.from_node==textures[0] and link.from_socket.name=='Alpha' for link in mat.node_tree.links)
    assert not o.hide_render

# Re-evaluate all original objects so excluded facade/roof matrices are current.
original=bpy.context.window.scene
evaluation=bpy.data.scenes.new('__FINAL LOGO VERIFICATION')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation;bpy.context.view_layer.update()
def signature(o):
    h=hashlib.sha256();h.update(o.type.encode())
    h.update(str((tuple(v for row in o.matrix_world for v in row),tuple(sorted(c.name for c in o.users_collection)),o.hide_render,o.hide_viewport)).encode())
    if o.type=='MESH':
        coords=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
        h.update(str((len(o.data.polygons),len(o.modifiers))).encode())
    elif o.type=='FONT':h.update(o.data.body.encode())
    if hasattr(o.data,'materials'):h.update(str([m.name if m else None for m in o.data.materials]).encode())
    return h.hexdigest()
baseline=json.loads((OUT/'logo_preservation_baseline.json').read_text())
changed=[name for name,sig in baseline.items() if name not in bpy.data.objects or signature(bpy.data.objects[name])!=sig]
assert not changed,changed
for root in [o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')]:
    cables=[c for c in root.children if c.name.startswith('Top suspension cable •')]
    assert len(cables)==2
    for cable in cables:assert min((cable.matrix_world @ v.co).z for v in cable.data.vertices)>root.location.z+.75*FT
bpy.context.window.scene=original;bpy.data.scenes.remove(evaluation)
os.environ['GYM_AUDIT_LABEL']='branded'
p=OUT/'audit_proportions.py'
exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
print('BRANDING_SAVED_FILE_VERIFIED: 13 official-logo placements; shared packed transparent artwork; all protected geometry unchanged; proportions rechecked.',flush=True)
if os.environ.get('GYM_LOGO_RENDER','1')=='0':raise SystemExit(0)

prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scenes=[('01 | CUTAWAY • furnished plan','branded_cutaway.png'),('02 | PLAN • orthographic','branded_floor_plan.png'),
        ('03 | EXTERIOR • entrance','branded_entrance.png'),('05 | INTERIOR • HYROX','branded_hyrox.png'),
        ('06 | AUDIT • verified plan dimensions','branded_dimensions.png')]
for name,filename in scenes:
    if os.environ.get('GYM_LOGO_REVIEW')=='detail' and not name.startswith('06 |'):continue
    scene=bpy.data.scenes[name];bpy.context.window.scene=scene
    scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
    print('FINAL_BRANDED_RENDER',filename,flush=True)

# Additional non-destructive detail render, without adding a new saved scene/camera.
scene=bpy.data.scenes['03 | EXTERIOR • entrance'];bpy.context.window.scene=scene
previous_camera=scene.camera
data=bpy.data.cameras.new('Temporary reception logo detail');data.lens=23
camera=bpy.data.objects.new('Temporary reception logo detail',data);scene.collection.objects.link(camera)
camera.location=Vector((98.1,44.0,6.4))*FT
camera.rotation_euler=(Vector((91.3,54.0,6.0))*FT-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera
scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'branded_reception_detail.png')
bpy.ops.render.render(write_still=True)
scene.camera=previous_camera;bpy.data.objects.remove(camera,do_unlink=True)
print('BRANDED_PACKAGE_AND_DETAIL_COMPLETE',flush=True)
