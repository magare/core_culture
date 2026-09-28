"""Non-destructive material/lighting refinement; all existing geometry is protected.

Apply once to Core_Culture_Gym_before_aesthetic_pass.blend. Adds two presentation
scenes, never changes the measured layout, equipment, logos, or suspended signs.
"""
import bpy, math, json, hashlib, os
from array import array
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
FT=.3048
assert not bpy.context.scene.get('Aesthetic finish applied'), 'Already refined'

def geometry_signature(o):
    h=hashlib.sha256()
    h.update(str((o.type,tuple(v for row in o.matrix_world for v in row),o.parent.name if o.parent else None,
                  tuple(sorted(c.name for c in o.users_collection)),o.hide_render,o.hide_viewport)).encode())
    if o.type=='MESH':
        coords=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',coords)
        h.update(coords.tobytes());h.update(str((len(o.data.polygons),[(m.type,m.name) for m in o.modifiers if m.name!='Aesthetic • softened botanical surface'])).encode())
    elif o.type=='FONT':h.update(str((o.data.body,o.data.size,o.data.font.name,o.data.extrude)).encode())
    elif o.type=='CURVE':
        h.update(str((o.data.bevel_depth,[(s.type,[tuple(p.co) for p in s.points]) for s in o.data.splines])).encode())
    return h.hexdigest()

original=bpy.context.window.scene
evaluation=bpy.data.scenes.new('__AESTHETIC_GEOMETRY_CHECK')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation;bpy.context.view_layer.update()
protected={o.name:geometry_signature(o) for o in bpy.data.objects if o.type not in {'LIGHT','CAMERA'}}
(OUT/'aesthetic_geometry_baseline.json').write_text(json.dumps(protected,indent=2))
bpy.context.window.scene=original;bpy.data.scenes.remove(evaluation)

def finish(name,color,rough=.5,metal=0,texture=None,bump=.0,scale=1,stretch=(1,1,1),emission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True;m.diffuse_color=(*color,1)
    n=m.node_tree.nodes;n.clear();links=m.node_tree.links
    p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    out=n.new('ShaderNodeOutputMaterial');links.new(p.outputs['BSDF'],out.inputs['Surface'])
    if texture:
        coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=stretch;links.new(coord.outputs['Object'],mapping.inputs[0])
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2.5
        links.new(mapping.outputs[0],noise.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        for el,factor in zip(ramp.color_ramp.elements,texture):el.color=tuple(v*factor for v in color)+(1,)
        links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
        if bump:
            b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=bump
            links.new(noise.outputs['Fac'],b.inputs['Height']);links.new(b.outputs[0],p.inputs['Normal'])
    return m

# Material hierarchy: honed stone, warm graphite, satin silver, smoked timber.
finish('01 • anthracite powder-coated steel',(.038,.043,.044),.36,.48,texture=(.94,1.06),scale=180,bump=.00025)
finish('02 • folded graphite cladding',(.031,.036,.038),.47,.35)
finish('03 • blackened steel edges',(.012,.014,.015),.38,.50)
finish('04 • charcoal recycled rubber flooring',(.034,.039,.039),.83,texture=(.91,1.09),scale=145,bump=.0007)
finish('05 • deep olive performance turf',(.050,.078,.043),.94,texture=(.87,1.12),scale=180,bump=.0008,stretch=(1,1,2))
finish('06 • acid yellow lane graphics',(.70,.73,.62),.72)
finish('07 • warm white enamel',(.79,.80,.75),.40,.06)
finish('08 • satin stainless steel',(.56,.58,.59),.31,.86)
finish('09 • galvanized spiral duct',(.39,.42,.44),.43,.78,texture=(.97,1.03),scale=220,bump=.00012)
finish('10 • black equipment upholstery',(.014,.017,.017),.65,texture=(.95,1.06),scale=240,bump=.00035)
finish('11 • warm polished concrete',(.32,.307,.281),.51,texture=(.94,1.06),scale=3.8,bump=.0008)
finish('12 • warm neutral partition plaster',(.55,.53,.49),.76,texture=(.97,1.03),scale=55,bump=.0003)
finish('13 • pale porcelain tile',(.48,.49,.465),.40,texture=(.985,1.015),scale=80,bump=.0001)
finish('14 • natural smoked oak',(.27,.185,.113),.49,texture=(.78,1.18),scale=4,stretch=(15,.45,12),bump=.00035)
finish('15 • mirror panels',(.86,.88,.88),.032,1)
finish('16 • inactive blue console glass',(.023,.043,.048),.25,.28)
finish('17 • washroom blue-grey',(.20,.255,.26),.61)
finish('18 • washroom warm mauve',(.275,.243,.235),.61)
finish('19 • warm LED diffuser',(1,.91,.76),.28,emission=4.0)
finish('20 • presentation background',(.215,.217,.207),.94)
finish('21 • drawing annotation',(.62,.65,.60),.8)
glass=finish('22 • tinted entrance glass',(.55,.65,.65),.095,.02)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.94;p.inputs['IOR'].default_value=1.45
finish('Suspended signs • matte charcoal',(.013,.017,.018),.58)
finish('Suspended signs • warm white lettering',(.84,.86,.80),.52,emission=.22)
finish('Suspended signs • satin suspension wire',(.25,.28,.28),.43,.68)
finish('BRAND • graphite sign backing',(.014,.018,.019),.56,.13)
finish('BRAND • charcoal inlaid floor graphic',(.026,.033,.034),.86)
# Small keys retain zone distinction without candy-coloured highlights.
zone_colors={'cardio':(.51,.47,.30),'central':(.41,.48,.32),'group':(.51,.36,.25),'hyrox':(.34,.45,.27),
             'men':(.27,.40,.41),'women':(.41,.31,.32),'reception':(.29,.43,.43),
             'support':(.37,.40,.43),'weights':(.50,.32,.24),'passage':(.35,.43,.29)}
for key,color in zone_colors.items():finish('Suspended signs • zone '+key,color,.55,emission=.04)

# Quiet the bright central target without changing its diameter or logo size.
central=finish('AESTHETIC • honed graphite central ring',(.115,.13,.129),.76,texture=(.95,1.05),scale=20,bump=.0005)
o=bpy.data.objects['Central 16 ft functional circle']
o.material_slots[0].link='OBJECT';o.material_slots[0].material=central
joint=finish('AESTHETIC • soft timber joints',(.052,.040,.029),.80)
for name in ['Studio oak plank joint • static batch','Staggered end grain joint • static batch']:
    o=bpy.data.objects.get(name)
    if o:
        for slot in o.material_slots:slot.link='OBJECT';slot.material=joint

# Soften only the decorative foliage; original mesh control points remain intact.
leaf=finish('AESTHETIC • satin living foliage',(.038,.065,.033),.45)
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('Lobby plant leaf','Welcome plant leaf','Exterior entry plant leaf')):
        mod=o.modifiers.new('Aesthetic • softened botanical surface','SUBSURF');mod.levels=2;mod.render_levels=2
        for slot in o.material_slots:slot.link='OBJECT';slot.material=leaf
        for polygon in o.data.polygons:polygon.use_smooth=True

# Neutral, broad sources separate equipment silhouettes and avoid yellow mirrors.
for o in bpy.data.objects:
    if o.type!='LIGHT':continue
    d=o.data
    if o.name.startswith('Linear interior light'):d.color=(1,.95,.86);d.energy=440
    elif o.name.startswith('Free-weight wall washer'):d.color=(1,.97,.91);d.energy=170;d.size*=1.12
    elif o.name.startswith('Washroom ceiling light'):d.color=(1,.94,.85);d.energy=180
    elif o.name=='Studio softbox':d.energy=17000;d.color=(1,.96,.89)
    elif o.name=='Studio fill':d.energy=15500;d.color=(.91,.96,1)
    elif o.name=='Studio rim':d.energy=10000;d.color=(1,.97,.89)
    elif d.type=='SUN':d.energy=.65;d.angle=math.radians(30)
for w in bpy.data.worlds:
    if w.use_nodes:
        bg=w.node_tree.nodes.get('Background')
        if bg:bg.inputs[0].default_value=(.50,.53,.54,1);bg.inputs[1].default_value=.32

for s in bpy.data.scenes:
    s.use_fake_user=True;s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.02
    s.view_settings.look='AgX - Medium High Contrast'
    s.view_settings.exposure=.10 if s.name.startswith(('04 |','05 |')) else -.10
    s['Aesthetic finish applied']='2026-09-22: neutral industrial finishes; measured geometry unchanged.'

# A street-height facade viewpoint keeps the canopy from masking the brand sign.
facade_camera=bpy.data.scenes['03 | EXTERIOR • entrance'].camera
facade_camera.location=Vector((136,35,8))*FT
facade_camera.rotation_euler=(Vector((100,44,8.5))*FT-facade_camera.location).to_track_quat('-Z','Y').to_euler()
facade_camera.data.lens=30

# A clean presentation view for the website, with all ten hanging area signs.
web=bpy.data.scenes['01 | CUTAWAY • furnished plan'].copy()
web.name='07 | WEBSITE • architectural cutaway';web.use_fake_user=True
web.view_layers[0].layer_collection.children['21 | Plan dimensions & title'].exclude=True
web.camera=web.camera.copy();web.camera.data=web.camera.data.copy();web.collection.objects.link(web.camera)
web.camera.name='07 • Clean architectural overview'
web.camera.rotation_euler=(Vector((49,29,2.6))*FT-web.camera.location).to_track_quat('-Z','Y').to_euler()
web.camera.data.ortho_scale=129*FT
web.render.resolution_x=1800;web.render.resolution_y=1400

reception=bpy.data.scenes['03 | EXTERIOR • entrance'].copy()
reception.name='08 | DETAIL • reception';reception.use_fake_user=True
camdata=bpy.data.cameras.new('08 • Reception lens');camdata.lens=23
cam=bpy.data.objects.new('08 • Reception detail',camdata);reception.collection.objects.link(cam)
cam.location=Vector((98.1,44,6.4))*FT
cam.rotation_euler=(Vector((91.3,54,6))*FT-cam.location).to_track_quat('-Z','Y').to_euler()
reception.camera=cam;reception.render.resolution_x=1500;reception.render.resolution_y=1200

guide=bpy.data.texts.new('AESTHETIC PASS • 2026-09-22')
guide.write('Refined graphite, honed concrete, satin silver and smoked oak. Muted moss turf with ivory markings.\n'
            'Existing mesh vertices, transforms, dimensions, equipment, logos and all top-suspended signs preserved.\n'
            'The 27 decorative leaves have a reversible subdivision modifier and a separate foliage finish.\n'
            'Scene 07 is the clean website presentation, without drawing annotations. Scene 08 is a reception detail.\n'
            'Scenes 01–06 retain the original view purposes. Reference images and dimension audit remain packed.\n'
            'Source photograph heights and unmeasured fitout details remain conceptual. This is not a certified as-built model.\n')

# Compare geometry in a single fully-evaluated scene, independent of exclusions.
evaluation=bpy.data.scenes.new('__AESTHETIC_GEOMETRY_CHECK')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation;bpy.context.view_layer.update()
changed=[n for n,v in protected.items() if n not in bpy.data.objects or geometry_signature(bpy.data.objects[n])!=v]
assert not changed,changed
bpy.context.window.scene=original;bpy.data.scenes.remove(evaluation)
assert len([o for o in bpy.data.objects if 'Asset type' in o])==41
assert len([o for o in bpy.data.objects if o.name.startswith('HANGING SIGN •')])==10
assert len([o for o in bpy.data.objects if o.name.startswith('OFFICIAL LOGO •')])==13
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='VIEW_3D':
                space.shading.type='MATERIAL';space.shading.use_scene_world=False;space.shading.use_scene_lights=False
                space.shading.studio_light='studio.exr'
                space.shading.studiolight_rotate_z=math.radians(35);space.shading.studiolight_intensity=.9

bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Core_Culture_Gym_Aesthetic.blend'),compress=True)
(OUT/'aesthetic_refinement_report.json').write_text(json.dumps({'protected_objects':len(protected),'geometry_changes':changed,
    'equipment_instances':41,'hanging_signs':10,'official_logos':13,'scenes':len(bpy.data.scenes)},indent=2))
print('AESTHETIC_SAVED_GEOMETRY_PRESERVED',len(protected),flush=True)

if os.environ.get('GYM_AESTHETIC_PREVIEW','1')=='1':
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='METAL'
    for s,filename in [(web,'aesthetic_preview_cutaway.png'),(bpy.data.scenes['04 | INTERIOR • free weights'],'aesthetic_preview_interior.png'),(reception,'aesthetic_preview_reception.png')]:
        bpy.context.window.scene=s;s.cycles.device='GPU';s.cycles.samples=28;s.render.resolution_percentage=65
        s.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
        print('AESTHETIC_PREVIEW',filename,flush=True)
