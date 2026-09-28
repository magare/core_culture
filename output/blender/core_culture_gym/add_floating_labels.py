"""Editable, camera-facing zone labels for the optimized gym model."""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT=Path(__file__).resolve().parent
FT=.3048
TARGET=OUT/'Core_Culture_Gym_Labeled.blend'
cut=bpy.data.scenes['01 | CUTAWAY • furnished plan']
plan=bpy.data.scenes['02 | PLAN • orthographic']
equipment_before={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if 'Asset type' in o}
areas_before={o.name:float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}

def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def rgb(code):return tuple(linear(int(code[i:i+2],16)/255) for i in (0,2,4))
def ink(name,code,strength=1):
    m=bpy.data.materials.new('Label • '+name)
    c=rgb(code)
    m.diffuse_color=(*c,1)
    m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear()
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(*c,1);emission.inputs['Strength'].default_value=strength
    output=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    return m

dark=ink('charcoal panels','142328')
white=ink('white lettering','FFFFFF',1.5)
muted=ink('secondary lettering','D0DEDF',1.1)
leader_mat=ink('connector lines','E6F4EE',1.3)
font=next((f for f in bpy.data.fonts if 'DIN Condensed' in f.name),None)
if not font:font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf')
regular=next((f for f in bpy.data.fonts if f.name.startswith('Arial') and 'Narrow' not in f.name),font)

LABELS=[
 {'id':'cardio','title':'CARDIO','detail':'TREADMILLS  /  BIKES  /  STAIRS','color':'F2D76A','anchor':(10,48,.18),'cut':(9,46,10.5),'plan':(10,48,8),'width':17,'height':4.6},
 {'id':'weights','title':'WEIGHT TRAINING','detail':'FREE WEIGHTS + STRENGTH MACHINES','color':'F29D88','anchor':(51,43,.18),'cut':(50,46,9.5),'plan':(50,44.5,8),'width':22,'height':4.6},
 {'id':'hyrox','title':'HYROX','detail':'SLED LANES + ERGOMETERS','color':'C6E473','anchor':(49,12,.2),'cut':(49,13.5,7.5),'plan':(49,14,8),'width':18,'height':4.6},
 {'id':'reception','title':'RECEPTION','detail':'CHECK-IN + LOUNGE','color':'76D7E5','anchor':(95,53,.18),'cut':(93,52,11.5),'plan':(92,55.5,8),'width':16,'height':4.6},
 {'id':'group','title':'GROUP EXERCISE','detail':'CLASSES + MOBILITY','color':'EBBE8A','anchor':(92,19,.18),'cut':(93,17,9),'plan':(92,19.2,8),'width':18,'height':4.6},
 {'id':'men','title':"MEN'S WASHROOM",'detail':'WC  /  SHOWER  /  LOCKERS','color':'9ACAC9','anchor':(16,21,.18),'cut':(8,22.5,10),'plan':(10,22.5,8),'width':18,'height':4.6},
 {'id':'women','title':"WOMEN'S WASHROOM",'detail':'WC  /  SHOWER  /  LOCKERS','color':'C6AEDB','anchor':(16,6,.18),'cut':(8,7.5,8.5),'plan':(10,7.5,8),'width':20,'height':4.6},
 {'id':'central','title':'CENTRAL TRAINING','detail':'16 FT OPEN CIRCLE','color':'DAE9B5','anchor':(50,30,.18),'cut':(50,30,7.5),'plan':(50,30.7,8),'width':20,'height':4.6},
 {'id':'support','title':'SUPPORT ROOMS','detail':'3 ROOMS  /  FLEXIBLE USE','color':'B7C3CB','anchor':(92,37.7,.18),'cut':(92.5,36,10.5),'plan':(92,36.3,8),'width':18,'height':4.6},
 {'id':'passage','title':'PASSAGE','detail':'4 FT CIRCULATION ROUTE','color':'BCD3A2','anchor':(55,2,.18),'cut':(59,1,5.5),'plan':(53,2,8),'width':17,'height':3.6},
]

def presentation(o):
    o.show_in_front=True
    o.visible_shadow=False
    o.visible_diffuse=False
    o.visible_glossy=False
    o.visible_transmission=False
    return o

def panel(col,name,width,height,mat,parent,z=0,radius=.2):
    # A single inexpensive rounded polygon, facing the scene camera.
    w,h=width*FT/2,height*FT/2;r=radius*FT
    vertices=[]
    for cx,cy,start in [(w-r,h-r,0),(-w+r,h-r,90),(-w+r,-h+r,180),(w-r,-h+r,270)]:
        for j in range(5):
            a=math.radians(start+j*90/4)
            vertices.append((cx+r*math.cos(a),cy+r*math.sin(a),z*FT))
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(vertices,[],[tuple(range(len(vertices)))]);mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);o.parent=parent
    return presentation(o)

def lettering(col,name,body,parent,size,y,mat,width,regular_font=False):
    data=bpy.data.curves.new(name+' text','FONT');data.body=body
    data.font=regular if regular_font else font
    data.size=size*FT;data.align_x='CENTER';data.align_y='CENTER'
    data.resolution_u=3;data.render_resolution_u=6
    data.extrude=0;data.materials.append(mat)
    o=bpy.data.objects.new(name,data);col.objects.link(o);o.parent=parent
    o.location=(.16*FT,y*FT,.065*FT)
    bpy.context.view_layer.update()
    measured=max(v[0] for v in o.bound_box)-min(v[0] for v in o.bound_box)
    if measured>(width-1.35)*FT:o.scale.x=(width-1.35)*FT/measured
    return presentation(o)

def line(col,name,pts,mat,radius=.028):
    data=bpy.data.curves.new(name+' path','CURVE');data.dimensions='3D';data.resolution_u=1
    data.bevel_depth=radius*FT;data.bevel_resolution=0;data.materials.append(mat)
    sp=data.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new(name,data);col.objects.link(o)
    return presentation(o)

records=[]
for s,kind in [(cut,'cut'),(plan,'plan')]:
    bpy.context.window.scene=s
    col=bpy.data.collections.new('22 | FLOATING AREA LABELS • '+('overview' if kind=='cut' else 'plan'))
    s.collection.children.link(col)
    cam=s.camera
    quat=cam.matrix_world.to_quaternion()
    planned=[]
    for spec in LABELS:
        pos=Vector(spec[kind])*FT
        width=spec['width'];height=spec['height']
        # Plan labels fit within the 16 ft east rooms, which have narrow boundaries.
        if kind=='plan' and spec['id'] in {'reception','support','group'}:width=14.8
        root=bpy.data.objects.new('LABEL • '+spec['title'],None);col.objects.link(root)
        root.location=pos;root.rotation_mode='QUATERNION';root.rotation_quaternion=quat
        root.empty_display_type='PLAIN_AXES';root.empty_display_size=.18*FT
        root['Area']=spec['title'];root['Description']=spec['detail'];root['Annotation only']=True
        orient=root.constraints.new('COPY_ROTATION');orient.name='Face the saved view camera';orient.target=cam
        accent=ink(kind+' • '+spec['title'],spec['color'],1.25)
        panel(col,'Label background • '+spec['id'],width,height,dark,root,radius=.26)
        stripe=panel(col,'Zone colour • '+spec['id'],.19,height-.7,accent,root,z=.04,radius=.065)
        stripe.location.x=(-width/2+.35)*FT
        small=spec['id']=='passage'
        lettering(col,'Floating title • '+spec['id'],spec['title'],root,2.3 if not small else 2.05,.56 if not small else .38,white,width)
        lettering(col,'Floating description • '+spec['id'],spec['detail'],root,.78,-1.1 if not small else -.84,muted,width,True)
        bpy.context.view_layer.update()
        corners=[root.matrix_world@Vector((x*width*FT/2,y*height*FT/2,0)) for x,y in [(-1,-1),(-1,1),(1,1),(1,-1)]]
        projected=[world_to_camera_view(s,cam,p) for p in corners]
        bbox=[min(p.x for p in projected),min(p.y for p in projected),max(p.x for p in projected),max(p.y for p in projected)]
        planned.append((root,spec,width,height,bbox,accent))

    # Separate any overlapping callouts by raising them in world Z in the overview.
    # Floor plan positions are semantic room centers and are kept exact.
    if kind=='cut':
        for _ in range(8):
            moved=False
            for i in range(len(planned)):
                for j in range(i):
                    a,b=planned[i][4],planned[j][4]
                    if min(a[2],b[2])-max(a[0],b[0])>.005 and min(a[3],b[3])-max(a[1],b[1])>-.009:
                        root,spec,w,h,_,accent=planned[i]
                        root.location.z+=1.4*FT
                        bpy.context.view_layer.update()
                        pts=[world_to_camera_view(s,cam,root.matrix_world@Vector((x*w*FT/2,y*h*FT/2,0))) for x,y in [(-1,-1),(-1,1),(1,1),(1,-1)]]
                        box=[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)]
                        planned[i]=(root,spec,w,h,box,accent);moved=True
            if not moved:break

    collisions=[]
    for i,(root,spec,w,h,box,accent) in enumerate(planned):
        if kind=='cut':
            start=root.matrix_world@Vector((0,-h*FT/2,.01*FT))
            anchor=Vector(spec['anchor'])*FT
            near_floor=Vector((anchor.x,anchor.y,anchor.z+.65*FT))
            line(col,'Area pointer • '+spec['id'],[start,near_floor,anchor],leader_mat)
            points=[anchor+Vector((math.cos(a*2*math.pi/32)*.3*FT,math.sin(a*2*math.pi/32)*.3*FT,.01*FT)) for a in range(33)]
            line(col,'Area marker • '+spec['id'],points,accent,.035)
        for j in range(i):
            b=planned[j][4]
            if min(box[2],b[2])>max(box[0],b[0]) and min(box[3],b[3])>max(box[1],b[1]):collisions.append([spec['id'],planned[j][1]['id']])
        assert box[0]>.01 and box[2]<.99 and box[1]>.01 and box[3]<.99,(kind,spec['id'],box)
        records.append({'view':kind,'area':spec['title'],'height_ft':round(root.location.z/FT,2),'screen_bbox':[round(v,4) for v in box]})
    assert not collisions,(kind,collisions)
    # New callouts take over from the small floor annotation labels in these views.
    old=s.view_layers[0].layer_collection.children.get('20 | Floor wayfinding')
    if old:old.exclude=True
    s['Floating labels']='Ten editable zone callouts. Toggle collection 22 | FLOATING AREA LABELS. Label rotations follow this scene camera.'

assert equipment_before=={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if 'Asset type' in o}
assert areas_before=={o.name:float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}
guide=bpy.data.texts.new('FLOATING LABELS • editing guide')
guide.write('Ten floating zone labels are included in the CUTAWAY and PLAN scenes.\n\nToggle collection 22 | FLOATING AREA LABELS to hide/show annotations. Each label has an Empty parent named LABEL, a rounded dark panel, a colour strip, editable title and editable description. Edit text with Tab in the selected text object. Move the Empty to move its text and panel together. Connector curves in the overview point to the correct floor area. COPY ROTATION keeps each panel facing its saved scene camera.\n\nLabels are annotations and do not cast shadows or appear in mirror reflections. Exterior and close-up interior scenes remain architectural views. All room and equipment transforms have been preserved.\n')
cut.render.filepath=str(OUT/'labeled_cutaway.png')
plan.render.filepath=str(OUT/'labeled_floor_plan.png')
bpy.context.window.scene=cut
for screen in bpy.data.screens:
    for a in screen.areas:
        for space in a.spaces:
            if space.type=='VIEW_3D':
                space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=13
                space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False
                space.clip_start=.1;space.clip_end=200
for o in bpy.context.selected_objects:o.select_set(False)
bpy.context.view_layer.objects.active=None
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='METAL'
except Exception:pass
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
(OUT/'floating_labels_report.json').write_text(json.dumps({'labels_per_view':len(LABELS),'views':['CUTAWAY','PLAN'],'room_areas_preserved':True,'equipment_transforms_preserved':True,'projected_overlap_check':'passed','labels':records},indent=2))
print('LABELS_SAVED',str(TARGET),json.dumps(records),flush=True)
for s in [cut,plan]:
    bpy.context.window.scene=s
    bpy.ops.render.render(write_still=True)
    print('LABEL_RENDER_DONE',s.name,flush=True)
bpy.context.window.scene=cut
print('FLOATING_LABELS_COMPLETE',flush=True)
