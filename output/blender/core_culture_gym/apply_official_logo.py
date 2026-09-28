"""Replace all placeholder gym branding with the user's cleaned transparent logo.

Run once on the pre-logo live snapshot or live Blender scene. Non-brand geometry,
equipment, area signs, dimensions and user visibility choices are preserved.
"""
import bpy, math, json, hashlib, os
from pathlib import Path
from array import array
from mathutils import Vector, Euler

OUT=Path(__file__).resolve().parent
FT=.3048
TARGET=OUT/'Core_Culture_Gym_Branded.blend'
SOURCE_PATH=bpy.data.filepath
CUT=bpy.data.scenes['01 | CUTAWAY • furnished plan']
assert not CUT.get('Official logo applied'), 'The official branding is already applied.'
previous_scene=bpy.context.window.scene
OLD_NAMES={
    'Central monogram','Central circle lettering',
    'Facade brand circle','Facade monogram','Facade logo heading','Facade logo footer',
    'Reception desk logo','Reception brand wall','Presentation title',
    'Lane finish text 01','Lane finish text 02','Mat centre logo • static batch',
}
assert OLD_NAMES.issubset(bpy.data.objects.keys()),OLD_NAMES-set(bpy.data.objects.keys())
before_scenes=set(bpy.data.scenes.keys())
old_objects={name:bpy.data.objects[name] for name in OLD_NAMES}
COL={c.name[:2]:c for c in CUT.collection.children}
evaluation=bpy.data.scenes.new('__LOGO EDIT EVALUATION')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):
        evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation
bpy.context.view_layer.update()

def signature(o):
    h=hashlib.sha256()
    h.update(o.type.encode())
    h.update(str((tuple(v for row in o.matrix_world for v in row),
                  tuple(sorted(c.name for c in o.users_collection)),o.hide_render,o.hide_viewport)).encode())
    if o.type=='MESH':
        coords=array('f',[0])*(len(o.data.vertices)*3)
        o.data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
        h.update(str((len(o.data.polygons),len(o.modifiers))).encode())
    elif o.type=='FONT':h.update(o.data.body.encode())
    if hasattr(o.data,'materials'):h.update(str([m.name if m else None for m in o.data.materials]).encode())
    return h.hexdigest()

# This one diagram label moves below the new central logo; its size is unchanged.
movable_label='PLAN LABEL • CENTRAL TRAINING'
movable_names={movable_label}|{o.name for o in bpy.data.objects[movable_label].children_recursive}
protected={o.name:signature(o) for o in bpy.data.objects if o.name not in OLD_NAMES|movable_names}
equipment={o.name:signature(o) for o in bpy.data.objects if 'Asset type' in o}
zones={o.name:list(o['Boundary in feet']) for o in bpy.data.objects if 'Boundary in feet' in o}
signs={o.name:signature(o) for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')}
(OUT/'logo_preservation_baseline.json').write_text(json.dumps(protected,indent=2))

logo=bpy.data.images.load(str(OUT/'core_culture_logo_transparent.png'),check_existing=True)
logo.name='CORE CULTURE • official cleaned transparent logo'
logo.alpha_mode='STRAIGHT';logo.use_fake_user=True;logo.pack()
original=bpy.data.images.load(str(OUT/'core_culture_logo_original.jpg'),check_existing=True)
original.name='REFERENCE 05 • user supplied Core Culture logo';original.use_fake_user=True;original.pack()
alpha=list(logo.pixels)[3::4]
assert logo.channels==4 and min(alpha)==0 and max(alpha)==1
assert .2<sum(a<.01 for a in alpha)/len(alpha)<.9

def decal_material(name,roughness,metallic,emission):
    m=bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=(.5,.53,.55,1)
    m.node_tree.nodes.clear();ns=m.node_tree.nodes;lk=m.node_tree.links
    tex=ns.new('ShaderNodeTexImage');tex.name='Official Core Culture logo • shared source';tex.image=logo
    tex.interpolation='Linear';tex.extension='CLIP';tex.location=(-500,120)
    surf=ns.new('ShaderNodeBsdfPrincipled');surf.location=(-180,100)
    surf.inputs['Roughness'].default_value=roughness
    surf.inputs['Metallic'].default_value=metallic
    surf.inputs['Emission Strength'].default_value=emission
    lk.new(tex.outputs['Color'],surf.inputs['Base Color'])
    lk.new(tex.outputs['Color'],surf.inputs['Emission Color'])
    clear=ns.new('ShaderNodeBsdfTransparent');clear.location=(-180,-160)
    mix=ns.new('ShaderNodeMixShader');mix.location=(150,100)
    lk.new(tex.outputs['Alpha'],mix.inputs[0]);lk.new(clear.outputs[0],mix.inputs[1]);lk.new(surf.outputs[0],mix.inputs[2])
    out=ns.new('ShaderNodeOutputMaterial');out.location=(380,100);lk.new(mix.outputs[0],out.inputs['Surface'])
    ns.active=tex
    if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
    m['Brand source']=logo.name
    m['Transparency']='Generated RGBA alpha preserved; no black rectangular background.'
    return m

sign_mat=decal_material('BRAND • silver logo on signage',.42,.12,.18)
floor_mat=decal_material('BRAND • matte printed logo',.78,0,.10)
back_mat=bpy.data.materials.new('BRAND • graphite sign backing');back_mat.use_nodes=True
back_mat.diffuse_color=(.017,.024,.028,1)
bs=back_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=back_mat.diffuse_color
bs.inputs['Roughness'].default_value=.55;bs.inputs['Metallic'].default_value=.15
floor_back=back_mat.copy();floor_back.name='BRAND • charcoal inlaid floor graphic'
floor_back.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.88
floor_back.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=0

quad=bpy.data.meshes.new('Official logo decal • shared square UV mesh')
quad.from_pydata([(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0)],[],[(0,1,2,3)])
quad.update();uv=quad.uv_layers.new(name='Logo UV')
for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
quad.materials.append(sign_mat)

branding_cols={}
def branding_col(key):
    if key not in branding_cols:
        child=bpy.data.collections.new('BRAND • official logo • '+COL[key].name[5:])
        COL[key].children.link(child);branding_cols[key]=child
    return branding_cols[key]

def backing(name,col,parent,diameter,depth,mat):
    n=96;r=diameter*FT/2;dz=depth*FT/2
    vs=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in [-dz,dz] for i in range(n)]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(vs,[],faces);mesh.update();mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);o.parent=parent
    # The decal sits 0.001 ft above the plaque, never coplanar.
    o.location.z=-(depth/2+.001)*FT
    bevel=o.modifiers.new('Soft manufactured edge','BEVEL');bevel.width=min(.035,depth*.2)*FT;bevel.segments=3
    o['Brand detail']='Round graphite support with softened perimeter; not part of the logo image.'
    return o

records=[]
def add_logo(key,title,location,size,rotation=(0,0,0),plate=None,printed=False):
    col=branding_col(key)
    root=bpy.data.objects.new('BRAND ASSEMBLY • '+title,None);col.objects.link(root)
    root.location=Vector(location)*FT;root.rotation_euler=tuple(math.radians(a) for a in rotation)
    root.empty_display_size=.1*FT
    root['Official logo placement']=title;root['Width (ft)']=size
    root['Original reference']='793457297_18085007468438400_6226988260889053662_n.jpg'
    decal=bpy.data.objects.new('OFFICIAL LOGO • '+title,quad);col.objects.link(decal);decal.parent=root
    decal.scale=(size*FT,size*FT,size*FT)
    decal.material_slots[0].link='OBJECT';decal.material_slots[0].material=floor_mat if printed else sign_mat
    decal['Artwork']=logo.name;decal['Aspect ratio']='1:1, unstretched'
    if plate:backing('Logo backing • '+title,col,root,plate[0],plate[1],floor_back if printed else back_mat)
    records.append({'placement':title,'center_ft':list(location),'artwork_width_ft':size,'rotation_degrees':list(rotation),
                    'surface':'matte print' if printed else 'silver sign','rounded_backing':plate is not None,
                    'collection':col.name})
    return root

circle=bpy.data.objects['Central 16 ft functional circle']
circle_pts=[circle.matrix_world @ v.co for v in circle.data.vertices]
cx=(min(v.x for v in circle_pts)+max(v.x for v in circle_pts))/2/FT
cy=(min(v.y for v in circle_pts)+max(v.y for v in circle_pts))/2/FT
top=max(v.z for v in circle_pts)/FT
add_logo('11','central training floor',(cx,cy,top+.010),8.0,plate=(9.2,.009),printed=True)
add_logo('07','entrance facade',(100.155,44.4,7.9),5.8,(90,0,90),plate=(6.1,.12))
add_logo('03','reception feature wall',(92,59.355,10.75),4.6,(90,0,0),plate=(5.0,.10))
add_logo('13','reception desk',(90.752,50.3,2.0),2.15,(90,0,90),plate=(2.45,.08))
for name,number in [('Lane finish text 01','01'),('Lane finish text 02','02')]:
    loc=old_objects[name].matrix_world.translation/FT
    add_logo('11','HYROX lane '+number,(loc.x,loc.y,.178),2.1,(0,0,90),printed=True)

# Recover the six mat centers from the existing batched placeholder geometry.
mat_marks=old_objects['Mat centre logo • static batch']
pending=set(range(len(mat_marks.data.vertices)))
neighbors=[set() for _ in mat_marks.data.vertices]
for edge in mat_marks.data.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
centers=[]
while pending:
    seed=pending.pop();ids=[seed];stack=[seed]
    while stack:
        for nxt in neighbors[stack.pop()]:
            if nxt in pending:pending.remove(nxt);ids.append(nxt);stack.append(nxt)
    pts=[mat_marks.matrix_world @ mat_marks.data.vertices[i].co for i in ids]
    centers.append(sum(pts,Vector())/len(pts)/FT)
assert len(centers)==6
for i,loc in enumerate(sorted(centers,key=lambda p:(p.x,p.y)),1):
    add_logo('14','studio mat %02d'%i,(loc.x,loc.y,.152),.70,printed=True)
add_logo('21','presentation title',(1.9,-7.6,.041),3.6,plate=(4.0,.010),printed=True)

for obj in old_objects.values():bpy.data.objects.remove(obj,do_unlink=True)
plan_label=bpy.data.objects[movable_label]
plan_label.location.y=(cy-6.2)*FT
plan_label['Logo clearance']='Moved below the central floor emblem; size and text retained.'

# Dimension-review scene stays free of branding overlay across the clear chains.
audit=bpy.data.scenes.get('06 | AUDIT • verified plan dimensions')
if audit:
    bpy.context.window.scene=audit;bpy.context.view_layer.update()
    layer=audit.view_layers[0].layer_collection.children.get(COL['11'].name)
    layer.children[branding_cols['11'].name].exclude=True
    audit.use_fake_user=True

bpy.context.window.scene=evaluation;bpy.context.view_layer.update()
changed=[name for name,sig in protected.items() if signature(bpy.data.objects[name])!=sig]
assert not changed,('Non-brand object changed',changed)
assert equipment=={name:signature(bpy.data.objects[name]) for name in equipment}
assert zones=={o.name:list(o['Boundary in feet']) for o in bpy.data.objects if 'Boundary in feet' in o}
assert signs=={name:signature(bpy.data.objects[name]) for name in signs}
assert not any(o.type=='FONT' and o.data.body.strip() in {'CC','CORE CULTURE','GYM'} for o in bpy.data.objects)
bpy.context.window.scene=previous_scene
bpy.data.scenes.remove(evaluation)
assert set(bpy.data.scenes.keys())==before_scenes

report={
    'source':SOURCE_PATH,'output':str(TARGET),'placement_count':len(records),'placements':records,
    'replaced_placeholder_objects':sorted(OLD_NAMES),'non_brand_objects_preserved':len(protected),
    'equipment_instances_preserved':len(equipment),'hanging_signs_preserved':len(signs),
    'zone_boundaries_preserved':True,'all_existing_scenes_preserved':True,
    'image_dimensions':list(logo.size),'image_has_real_alpha':True,'packed_images':True,
    'material_note':'One shared RGBA artwork and one shared square UV mesh. Silver signage and matte floor print; no stretch or rectangular background.',
    'layout_adjustment':'The plan-only CENTRAL TRAINING label moves below the floor logo. Audit scene 06 excludes the central/lane artwork for clear dimension chains.',
    'source_limitation':'The source was 150 x 150 px. The cleaned high-resolution texture is an image-assisted extraction/reconstruction, not a recovered original vector master.',
}
(OUT/'logo_update_report.json').write_text(json.dumps(report,indent=2))
note=bpy.data.texts.get('OFFICIAL LOGO • placements and editing') or bpy.data.texts.new('OFFICIAL LOGO • placements and editing')
note.clear();note.write(json.dumps(report,indent=2))
guide=bpy.data.texts.get('START HERE • model guide & assumptions')
if guide:guide.write('\n\nOFFICIAL LOGO UPDATE\n13 branding placements use the supplied logo artwork.\nSee OFFICIAL LOGO text. Previous geometry/proportion assumptions still apply.\n')
for scene in bpy.data.scenes:
    scene['Official logo applied']=True
    scene['Logo artwork']=logo.name
    scene['Logo backup']='Core_Culture_Gym_before_logo_update.blend'
    scene.render.filepath=str(OUT/('branded_'+{'01':'cutaway','02':'floor_plan','03':'entrance','04':'free_weights','05':'hyrox','06':'dimensions'}[scene.name[:2]]+'.png'))

# Image-based decals require textured/material display; solid mode cannot show them.
for screen in bpy.data.screens:
    for area in screen.areas:
        if bpy.app.background and area.type=='CONSOLE':area.type='VIEW_3D' if area.width>500 else 'PROPERTIES'
        for space in area.spaces:
            if space.type=='VIEW_3D':
                space.shading.type='MATERIAL'
                space.shading.use_scene_world=False
                space.shading.use_scene_lights=False
                space.overlay.show_overlays=False
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
print('OFFICIAL_BRANDING_APPLIED_AND_SAVED',json.dumps(report,indent=2),flush=True)

if bpy.app.background and os.environ.get('GYM_LOGO_RENDER','1')=='1':
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='METAL'
    for name in ['01 | CUTAWAY • furnished plan','02 | PLAN • orthographic','03 | EXTERIOR • entrance','05 | INTERIOR • HYROX']:
        scene=bpy.data.scenes[name];bpy.context.window.scene=scene
        bpy.ops.render.render(write_still=True)
        print('BRANDED_PREVIEW_SAVED',scene.render.filepath,flush=True)
print('LOGO_UPDATE_COMPLETE',flush=True)
