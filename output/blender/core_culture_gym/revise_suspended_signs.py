"""Replace oversized floor-pointer callouts with compact ceiling-hung signage.

Runs against a saved copy for previews or directly in the live Blender console.
Only the annotation collections are replaced; architecture/equipment are preserved.
"""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = Path(__file__).resolve().parent
FT = .3048
TARGET = OUT / 'Core_Culture_Gym_Suspended_Signs.blend'
CUT = bpy.data.scenes['01 | CUTAWAY • furnished plan']
PLAN = bpy.data.scenes['02 | PLAN • orthographic']
OLD_PREFIXES = ('22 | FLOATING AREA LABELS', '22 | SUSPENDED AREA SIGNS', '22 | COMPACT PLAN LABELS')

# Dimensions are feet. Upright, double-sided signs; no camera-facing constraints.
SPECS = [
    ('cardio', 'CARDIO', (9, 48, 13), 6.2, 'F2D76A', (10, 48)),
    ('weights', 'WEIGHT TRAINING', (50, 42, 13), 9.6, 'F29D88', (50, 44.5)),
    ('hyrox', 'HYROX', (48, 12, 13), 6.0, 'C6E473', (49, 14)),
    ('reception', 'RECEPTION', (92, 48, 13), 7.2, '76D7E5', (92, 55.5)),
    ('group', 'GROUP EXERCISE', (92, 18, 13), 9.3, 'EBBE8A', (92, 19.2)),
    ('men', "MEN'S WASHROOM", (9, 24, 12.5), 9.0, '9ACAC9', (10, 22.5)),
    ('women', "WOMEN'S WASHROOM", (9, 6, 12.5), 10.2, 'C6AEDB', (10, 7.5)),
    ('central', 'CENTRAL TRAINING', (50, 30, 13), 10.1, 'DAE9B5', (50, 30.7)),
    ('support', 'SUPPORT ROOMS', (92, 36, 12.5), 8.7, 'B7C3CB', (92, 36.3)),
    ('passage', 'PASSAGE', (58, 2, 12.5), 6.0, 'BCD3A2', (53, 2)),
]
HEIGHT = 1.5
OLD_WIDTHS = [17, 22, 18, 16, 18, 18, 20, 20, 18, 17]
OLD_HEIGHTS = [4.6] * 9 + [3.6]

old_cols = [c for c in bpy.data.collections if c.name.startswith(OLD_PREFIXES)]
old_objects = {o for c in old_cols for o in c.all_objects}
protected = {o.name: (o.type, tuple(v for row in o.matrix_world for v in row))
             for o in bpy.data.objects if o not in old_objects}
areas_before = {o.name: float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}
equipment_before = {o.name: tuple(v for row in o.matrix_world for v in row)
                    for o in bpy.data.objects if 'Asset type' in o}

# A separate pre-revision blend retains the previous signs. Remove only those signs.
for o in old_objects:
    bpy.data.objects.remove(o, do_unlink=True)
for c in old_cols:
    bpy.data.collections.remove(c)

def linear(v):
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

def rgb(code):
    return tuple(linear(int(code[i:i+2], 16) / 255) for i in (0, 2, 4))

def material(name, color, emission=0, metal=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb(color), 1)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    p = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = m.diffuse_color
    p.inputs['Roughness'].default_value = .4
    p.inputs['Metallic'].default_value = metal
    p.inputs['Emission Color'].default_value = m.diffuse_color
    p.inputs['Emission Strength'].default_value = emission
    output = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs[0], output.inputs['Surface'])
    return m

panel_mat = material('Suspended signs • matte charcoal', '1C262A')
type_mat = material('Suspended signs • warm white lettering', 'F3F5EB', .6)
cable_mat = material('Suspended signs • satin suspension wire', 'A7AFAD', .12, .65)
mount_mat = bpy.data.materials.get('01 • anthracite powder-coated steel') or panel_mat
font = next((f for f in bpy.data.fonts if 'DIN Condensed' in f.name), None)
if not font:
    font = bpy.data.fonts.load('/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf')

def cube(col, name, location, dims, mat, parent=None):
    x, y, z = (d * FT / 2 for d in dims)
    verts = [(i*x, j*y, k*z) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    faces = [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], [tuple(reversed(face)) for face in faces])
    mesh.materials.append(mat)
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.parent = parent
    o.location = Vector(location) * FT
    return o

def cylinder(col, name, a, b, radius, mat, parent=None):
    a, b = Vector(a) * FT, Vector(b) * FT
    direction = b-a
    quat = direction.to_track_quat('Z', 'Y')
    verts = []
    for end in (a,b):
        for i in range(8):
            theta = 2*math.pi*i/8
            verts.append(end + quat @ Vector((radius*FT*math.cos(theta), radius*FT*math.sin(theta), 0)))
    faces = [tuple(range(7,-1,-1)), tuple(range(8,16))]
    faces += [(i, (i+1)%8, (i+1)%8+8, i+8) for i in range(8)]
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.parent = parent
    return o

def text(col, name, body, parent, width, reverse=False):
    curve = bpy.data.curves.new(name+' text', 'FONT')
    curve.body = body
    curve.font = font
    curve.size = 1.42 * FT
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.resolution_u = 3
    curve.render_resolution_u = 5
    curve.extrude = .001
    curve.materials.append(type_mat)
    o = bpy.data.objects.new(name, curve)
    col.objects.link(o)
    o.parent = parent
    o.location = (.10*FT, 0, (-.08 if reverse else .08)*FT)
    if reverse:
        o.rotation_euler.y = math.pi
    bpy.context.view_layer.update()
    extent = max(v[0] for v in o.bound_box)-min(v[0] for v in o.bound_box)
    if extent > (width-.7)*FT:
        o.scale.x = (width-.7)*FT/extent
    return o

def bbox(scene, root, width, height):
    bpy.context.view_layer.update()
    points = [world_to_camera_view(scene, scene.camera, root.matrix_world @ Vector((x*width*FT/2,y*height*FT/2,0)))
              for x,y in [(-1,-1),(-1,1),(1,1),(1,-1)]]
    return [min(p.x for p in points), min(p.y for p in points), max(p.x for p in points), max(p.y for p in points)]

def check(boxes):
    for i,(key,a) in enumerate(boxes):
        assert 0 < a[0] < a[2] < 1 and 0 < a[1] < a[3] < 1, (key, a)
        for other,b in boxes[:i]:
            assert not (min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])), (key, other)

records = []
for scene, physical in [(CUT, True),(PLAN, False)]:
    bpy.context.window.scene = scene
    col = bpy.data.collections.new('22 | SUSPENDED AREA SIGNS • overhead' if physical else '22 | COMPACT PLAN LABELS')
    scene.collection.children.link(col)
    boxes = []
    for key,title,pos,width,color,plan_pos in SPECS:
        root = bpy.data.objects.new(('HANGING SIGN • ' if physical else 'PLAN LABEL • ') + title, None)
        col.objects.link(root)
        root.empty_display_size = .1*FT
        root['Area'] = title
        root['Sign width (ft)'] = width
        root['Sign height (ft)'] = HEIGHT
        root['Revision'] = 'Compact single-line overhead signage; no floor pointer'
        root.location = Vector(pos if physical else (*plan_pos, 8))*FT
        if physical:
            root.rotation_euler = (math.pi/2, 0, 0)
        # Plan is intentionally a compact diagram label, not a sideways physical sign.
        accent = material('Suspended signs • zone '+key, color, .18)
        board = cube(col, 'Suspended panel • '+key if physical else 'Plan panel • '+key,
                     (0,0,0), (width,HEIGHT,.11), panel_mat, root)
        bevel = board.modifiers.new('Subtle sign-edge radius', 'BEVEL')
        bevel.width = .04*FT
        bevel.segments = 2
        text(col, 'Suspended title • '+key if physical else 'Plan title • '+key, title, root, width)
        cube(col, 'Sign colour key • '+key, (-width/2+.19,0,.062), (.085,1.08,.012), accent, root)
        if physical:
            text(col, 'Suspended reverse title • '+key, title, root, width, True)
            cube(col, 'Reverse colour key • '+key, (width/2-.19,0,-.062), (.085,1.08,.012), accent, root)
            # Short retained roof-level purlin segments keep the roof-off view open.
            # Their elevation follows the existing 18–21 ft pitched-roof model.
            mount_z = 18 + 3*(1-abs(pos[1]-30)/30) - .3
            relative_mount = mount_z-pos[2]
            beam = cube(col, 'Overhead mounting rail • '+key, (0,relative_mount,0), (width+1.4,.24,.2), mount_mat, root)
            beam['Cutaway note'] = 'Roof-level mounting member shown as a short retained segment; full roof hidden.'
            for side in (-1,1):
                x = side*(width/2-.62)
                cylinder(col, 'Top suspension cable • '+key, (x,HEIGHT/2+.04,0), (x,relative_mount-.12,0), .027, cable_mat, root)
                cube(col, 'Roof clamp • '+key, (x,relative_mount,0), (.18,.32,.29), cable_mat, root)
                cube(col, 'Top sign fixing • '+key, (x,HEIGHT/2+.055,0), (.12,.15,.16), cable_mat, root)
            root['Bottom clearance (ft)'] = pos[2]-HEIGHT/2
            root['Mount elevation (ft)'] = round(mount_z, 2)
            root['Ceiling suspension'] = 'Two cables above the panel; nothing continues to the floor.'
        screen_box = bbox(scene,root,width,HEIGHT)
        boxes.append((key,screen_box))
        records.append({'view':'cutaway' if physical else 'plan','area':title,'width_ft':width,'height_ft':HEIGHT,
                        'bottom_clearance_ft':pos[2]-HEIGHT/2 if physical else None,
                        'screen_bbox':screen_box})
    check(boxes)
    old = scene.view_layers[0].layer_collection.children.get('20 | Floor wayfinding')
    if old:
        old.exclude = True
    scene['Floating labels'] = 'Replaced with compact upright ceiling-hung signs; single-line plan labels.'
    scene['Suspended signage'] = 'Two top cables and retained roof-level mounting rails. No bottom leaders. Roof elevations remain estimated.'

assert protected == {n:(bpy.data.objects[n].type,tuple(v for row in bpy.data.objects[n].matrix_world for v in row)) for n in protected}
assert areas_before == {o.name:float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}
assert equipment_before == {o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if 'Asset type' in o}
assert not any(o.name.startswith(('Area pointer •','Area marker •','Floating description •')) for o in bpy.data.objects)

guide = bpy.data.texts.get('FLOATING LABELS • editing guide') or bpy.data.texts.new('FLOATING LABELS • editing guide')
guide.clear()
guide.name = 'SUSPENDED SIGNS • editing guide'
guide.write('Ten compact double-sided signs hang from two overhead cables in CUTAWAY.\n'
            'Signs are upright physical objects, not camera-facing billboards. Titles only; all floor leaders and secondary descriptions removed.\n'
            'Panels are 1.5 ft high, 6–10.2 ft wide, with at least 11.75 ft below them. Roof heights and mounting details are conceptual.\n'
            'Mounting rails are shown as short retained roof-level segments so the roof-off view stays open.\n'
            'Toggle collection 22 | SUSPENDED AREA SIGNS. Move a HANGING SIGN Empty to move the complete assembly.\n'
            'Each title is editable text. The reverse side has its own editable title.\n'
            'PLAN retains much smaller horizontal single-line labels for legibility from directly overhead.\n'
            'Existing architecture, equipment, floor areas, cameras and other scenes are unchanged.\n')

old_area = sum(w*h for w,h in zip(OLD_WIDTHS,OLD_HEIGHTS))
new_area = sum(spec[3]*HEIGHT for spec in SPECS)
report = {'signs':len(SPECS),'old_total_panel_area_sqft':old_area,'new_total_panel_area_sqft':new_area,
          'panel_area_reduction_percent':round((1-new_area/old_area)*100,1),
          'floor_leaders':0,'title_only':True,'upright_physical_signs':True,'cables_per_sign':2,
          'non_label_objects_preserved':len(protected),'equipment_transforms_preserved':True,
          'room_areas_preserved':True,'projected_overlap_check':'passed','labels':records}
(OUT/'suspended_signs_report.json').write_text(json.dumps(report,indent=2))
CUT.render.filepath = str(OUT/'suspended_signs_cutaway.png')
PLAN.render.filepath = str(OUT/'suspended_signs_plan.png')
bpy.context.window.scene = CUT
for screen in bpy.data.screens:
    for area in screen.areas:
        if bpy.app.background and area.type == 'CONSOLE':
            area.type = 'VIEW_3D'
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                space.region_3d.view_camera_zoom = 13
                space.shading.type = 'SOLID'
                space.shading.color_type = 'MATERIAL'
                space.overlay.show_overlays = False
for o in bpy.context.selected_objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = None
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == 'METAL'
except Exception:
    pass
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
print('SUSPENDED_SIGNS_SAVED',str(TARGET),json.dumps({k:v for k,v in report.items() if k!='labels'}),flush=True)
if bpy.app.background:
    for scene in (CUT,PLAN):
        bpy.context.window.scene = scene
        bpy.ops.render.render(write_still=True)
        print('SUSPENDED_RENDER_DONE',scene.name,flush=True)
    bpy.context.window.scene = CUT
print('SUSPENDED_SIGNS_COMPLETE',flush=True)
