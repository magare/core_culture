"""Measured-plan correction pass, preserving the authored gym and compact signs."""
import bpy, bmesh, math, json, os
from pathlib import Path
from mathutils import Vector, Matrix

OUT=Path(__file__).resolve().parent
FT=.3048
TARGET=OUT/'Core_Culture_Gym_Audited.blend'
CUT=bpy.data.scenes['01 | CUTAWAY • furnished plan']
PLAN=bpy.data.scenes['02 | PLAN • orthographic']
assert not CUT.get('Proportion audit applied'), 'Already audited: use the pre-audit snapshot.'
changes=[]
SOURCES={
 'rower':'https://www.concept2.com/ergs/rowerg',
 'ski erg':'https://www.concept2.com/ergs/skierg',
 'treadmill':'https://support.lifefitness.com/hc/en-us/articles/16340135145623-Life-Fitness-Integrity-Treadmill-Specifications',
 'stair climber':'https://www.corehandf.com/products/stairmaster-8gx-1',
}
COL={c.name[:2]:c for c in CUT.collection.children}
MAT={k:bpy.data.materials[n] for k,n in {
 'steel':'01 • anthracite powder-coated steel','edge':'03 • blackened steel edges',
 'concrete':'11 • warm polished concrete','wall':'12 • warm neutral partition plaster',
 'rib':'02 • folded graphite cladding','chrome':'08 • satin stainless steel',
 'glass':'22 • tinted entrance glass','oak':'14 • natural smoked oak',
 'cyan':'17 • washroom blue-grey','purple':'18 • washroom warm mauve',
 'white':'07 • warm white enamel','accent':'06 • acid yellow lane graphics'}.items()}

def mesh_obj(name, verts, faces, mat, col):
    me=bpy.data.meshes.new(name+' mesh');me.from_pydata(verts,[],faces);me.update()
    me.materials.append(mat)
    o=bpy.data.objects.new(name,me);col.objects.link(o)
    o['Audit geometry']='Corrected proportion / connection'
    return o

def box(name,loc,dims,mat,col,rot=0,bevel=.01):
    a,b,c=[v*FT/2 for v in dims]
    vs=[(i*a,j*b,k*c) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    fs=[(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)]
    o=mesh_obj(name,vs,fs,mat,col);o.location=Vector(loc)*FT;o.rotation_euler.z=math.radians(rot)
    if bevel:
        mod=o.modifiers.new('Manufactured edge','BEVEL');mod.width=bevel*FT;mod.segments=2
    return o

def cylinder(name,a,b,r,mat,col,sides=10):
    a,b=Vector(a)*FT,Vector(b)*FT
    q=(b-a).to_track_quat('Z','Y')
    vs=[p+q@Vector((r*FT*math.cos(i*2*math.pi/sides),r*FT*math.sin(i*2*math.pi/sides),0)) for p in (a,b) for i in range(sides)]
    fs=[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]
    fs += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    return mesh_obj(name,vs,fs,mat,col)

def shift(o,dx=0,dy=0,dz=0):
    o.location += Vector((dx,dy,dz))*FT

def world_bounds(o):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [Vector([f(p[k] for p in pts)/FT for k in range(3)]) for f in (min,max)]

def components(me):
    neighbors=[[] for _ in me.vertices]
    for e in me.edges:
        a,b=e.vertices;neighbors[a].append(b);neighbors[b].append(a)
    pending=set(range(len(me.vertices)))
    while pending:
        seed=pending.pop();stack=[seed];part=[seed]
        while stack:
            for nxt in neighbors[stack.pop()]:
                if nxt in pending:pending.remove(nxt);stack.append(nxt);part.append(nxt)
        yield part

def transform_parts(o,fn):
    # Batches are edited by loose component without increasing object count.
    if o.data.users>1:o.data=o.data.copy()
    inv=o.matrix_world.inverted()
    for ids in components(o.data):
        pts=[o.matrix_world@o.data.vertices[i].co/FT for i in ids]
        center=sum(pts,Vector())/len(pts)
        for idx,p in zip(ids,pts):o.data.vertices[idx].co=inv@(Vector(fn(p,center))*FT)
    o.data.update()

def combine_static(name,parts,col):
    bpy.context.view_layer.update()
    verts=[];faces=[];mats=[];indices=[]
    for o in parts:
        assert o.parent is None
        transform=Matrix.Translation(o.location) @ o.rotation_euler.to_matrix().to_4x4() @ Matrix.Diagonal((*o.scale,1))
        start=len(verts);verts.extend(transform@v.co for v in o.data.vertices)
        slots=[]
        for m in o.data.materials:
            if m not in mats:mats.append(m)
            slots.append(mats.index(m))
        for p in o.data.polygons:
            faces.append(tuple(start+i for i in p.vertices));indices.append(slots[p.material_index])
    me=bpy.data.meshes.new(name+' mesh');me.from_pydata(verts,[],faces);me.update()
    for m in mats:me.materials.append(m)
    for p,idx in zip(me.polygons,indices):p.material_index=idx
    merged=bpy.data.objects.new(name,me);col.objects.link(merged)
    merged['Original part count']=len(parts)
    for o in parts:bpy.data.objects.remove(o,do_unlink=True)

def remove_prefix(prefix):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)

def wall(name,axis,fixed,start,end,height=10,external=False):
    if end<=start:return
    loc=lambda z:((start+end)/2,fixed,z) if axis=='X' else (fixed,(start+end)/2,z)
    dims=lambda h:(end-start,.45,h) if axis=='X' else (.45,end-start,h)
    box(name+' • base',loc(1.65),dims(3.3),MAT['concrete'] if external else MAT['wall'],COL['02'])
    box(name+' • upper',loc((3.3+height)/2),dims(height-3.3),MAT['rib'] if external else MAT['wall'],COL['04'] if external else COL['05'])
    size=(end-start,.53,.42) if axis=='X' else (.53,end-start,.42)
    box(name+' • skirting',loc(.3),size,MAT['edge'],COL['02'],bevel=0)

def openings(name,axis,fixed,start,end,gaps,height=10):
    cursor=start
    for lo,hi in gaps:
        wall(name,axis,fixed,cursor,lo,height)
        xyz=((lo+hi)/2,fixed,(8+height)/2) if axis=='X' else (fixed,(lo+hi)/2,(8+height)/2)
        dims=(hi-lo,.45,height-8) if axis=='X' else (.45,hi-lo,height-8)
        box(name+' • lintel',xyz,dims,MAT['wall'],COL['05'])
        cursor=hi
    wall(name,axis,fixed,cursor,end,height)

bpy.context.window.scene=CUT
# Interpret the written 100 x 60 as the exterior wall-finish envelope. Inferred
# room-bay widths are gross planning zones, not clear internal room dimensions.
for o in list(bpy.data.objects):
    if o.name.startswith('North corrugated wall'):shift(o,dy=-.265)
    elif o.name.startswith('West corrugated wall'):shift(o,dx=.265)
    elif o.name.startswith('Entrance / east facade'):shift(o,dx=-.265)
    if any(c.name.startswith('07 |') for c in o.users_collection):shift(o,dx=-.265)
    if o.name.startswith('Exterior entry plant'):shift(o,dx=-.2,dy=-.8,dz=-.06)
changes.append('Seated the exterior planter on the shoe-shelf top and centered its base inside the support footprint.')

# The two generated south openings were unsupported by the supplied floor plan;
# its lower door symbols are side-wall entries from the internal passage.
remove_prefix('South exterior')
wall('South exterior','X',.265,0,100,18,True)
for i in range(111):
    box('South exterior • cladding rib',(i*.9+.45,.265,10.7),(.075,.515,14.6),MAT['steel'],COL['04'],bevel=0)
combine_static('South exterior • cladding rib • static batch',[o for o in COL['04'].objects if o.name.startswith('South exterior • cladding rib')],COL['04'])
remove_prefix('South exit')

# Keep the documented clear core at x=20..80 and the passage at x=80..84.
remove_prefix('Cardio & washroom partition')
openings('Cardio & washroom partition','Y',19.735,0,60,[(.7,4.0),(15.55,18.85),(30.55,33.85)])
remove_prefix('East circulation partition')
openings('East circulation partition','Y',84.265,0,60,[(.7,4.0),(40.5,44)])
changes.append('Contained exterior wall finishes in 100 x 60 ft; maintained 22+16+22 ft clear core; restored true 4 ft passages, including skirting.')

# Re-seat wall-mounted finishes on the revised wall faces.
for o in bpy.data.objects:
    if o.name.startswith(('Free-weight mirror','Mirror vertical','Mirror bottom','Free-weight wall sign','Cardio wall','Reception brand wall','Reception descriptor')):shift(o,dy=-.265)
    if 'vanity mirror' in o.name:shift(o,dx=.265)
    if any(s in o.name for s in ['vanity worktop','inset basin','basin recess','faucet']):shift(o,dx=.12)
    if o.name.startswith(('Men changing bench','Women changing bench','Men bench leg','Women bench leg')):shift(o,dy=1.02)
    if o.name.startswith(('Studio full-height mirror','Oak studio barre','Barre bracket')):shift(o,dx=.265)
    if o.name.startswith('Welcome plant'):shift(o,dx=.6,dy=.45)
    if 'cubicle partition' in o.name and o.location.x/FT<.4:shift(o,dx=.35)
    if 'cubicle door' in o.name and o.location.x/FT<3:shift(o,dx=.1)
    if 'cubicle handle' in o.name and o.location.x/FT<4:shift(o,dx=.1)
for o in bpy.data.objects:
    if o.name.startswith('Studio full-height mirror') and o.location.y/FT>29:
        o.data=o.data.copy()
        for v in o.data.vertices:v.co.y=min(v.co.y,(31.70-o.location.y/FT)*FT)

# Floor datum compensates for the 0.53 ft inward perimeter finish thickness.
DELTA=.53
for name,new_bounds in [('HYROX floor',[20,80,4+DELTA,28]),('Passage south floor',[20,84,0,4+DELTA]),('Passage east floor',[80,84,4+DELTA,46])]:
    o=bpy.data.objects[name];x1,x2,y1,y2=new_bounds
    old=o['Boundary in feet'];old_depth=old[3]-old[2]
    if o.data.users>1:o.data=o.data.copy()
    for v in o.data.vertices:v.co.y*=(y2-y1)/old_depth
    o.location.y=(y1+y2)*FT/2
    o['Boundary in feet']=new_bounds;o['Area in square feet']=(x2-x1)*(y2-y1)
for o in bpy.data.objects:
    if o.name.startswith(('Central 16 ft','Central circle','Central monogram','HANGING SIGN • CENTRAL','PLAN LABEL • CENTRAL','HANGING SIGN • PASSAGE','PLAN LABEL • PASSAGE','South passage label','Circulation arrow')):shift(o,dy=DELTA)
    if o.name.startswith(('Main AC duct','Spiral duct seam','AC grille','Duct hanger')):shift(o,dy=DELTA)
    if o.name=='Side AC distribution':
        for v in o.data.vertices:v.co.y=(8+(v.co.y/FT-8)*(48+DELTA)/48)*FT
    if o.name.startswith('Side duct collar'):
        transform_parts(o,lambda p,c: (p.x,8+(p.y-8)*(48+DELTA)/48,p.z))

# Remove the 0.5 ft circle/turf collision; keep a visible 0.53 ft gap.
turf=bpy.data.objects['HYROX performance turf']
if turf.data.users>1:turf.data=turf.data.copy()
for v in turf.data.vertices:v.co.y*=16/17
for o in bpy.data.objects:
    if o.name.startswith(('HYROX lane boundary','HYROX start / finish')):
        transform_parts(o,lambda p,c:(p.x,14+(p.y-14)*(15.5/16.5),p.z))
    elif o.name.startswith('Lane distance hash'):
        transform_parts(o,lambda p,c:(p.x,p.y+(.55 if c.y<10 else -.1),p.z))
    elif o.name.startswith(('Lane 01','Lane finish text 01','Weighted push sled • lane 01')):shift(o,dy=.325)
    elif o.name.startswith(('Lane 02','Lane finish text 02','Weighted push sled • lane 02')):shift(o,dy=-.325)
changes.append('Preserved the 16 ft circle and both 18 ft plan-axis spacings; eliminated the turf overlap.')

# Match clearly identifiable equipment categories to a documented representative
# envelope. These are dimensional stand-ins, NOT claimed as the user's brands.
asset_objs=[o for o in bpy.data.objects if 'Asset type' in o]
targets={'treadmill':(36.25/12,82.25/12,56/12),
         'stair climber':(34/12,58/12,79/12),
         'ski erg':(23.5/12,50/12,85/12),
         'rower':(2,8,None)}
equipment_changes=[]
for kind,target in targets.items():
    matches=[o for o in asset_objs if o['Asset type']==kind]
    for me in {o.data for o in matches}:
        lo=Vector([min(v.co[k] for v in me.vertices)/FT for k in range(3)])
        hi=Vector([max(v.co[k] for v in me.vertices)/FT for k in range(3)])
        size=hi-lo;center=(lo+hi)/2
        ratios=[target[k]/size[k] if target[k] is not None else (14/12)/(1.09-lo.z) for k in range(3)]
        belt_ids=[]
        if kind=='treadmill':
            for ids in components(me):
                pts=[me.vertices[i].co/FT for i in ids]
                c=sum(pts,Vector())/len(pts)
                if abs(c.z-.72)<.035 and max(p.x for p in pts)-min(p.x for p in pts)>2:
                    belt_ids=ids;break
        for v in me.vertices:
            p=v.co/FT
            v.co=Vector(((p.x-center.x)*ratios[0],(p.y-center.y)*ratios[1],(p.z-lo.z)*ratios[2]))*FT
        if belt_ids:
            pts=[me.vertices[i].co/FT for i in belt_ids]
            l=Vector([min(p[k] for p in pts) for k in range(3)])
            h=Vector([max(p[k] for p in pts) for k in range(3)])
            c=(l+h)/2
            for i in belt_ids:
                p=me.vertices[i].co/FT
                p.x=(p.x-c.x)*(22/12)/(h.x-l.x)
                p.y=c.y+(p.y-c.y)*5/(h.y-l.y)
                me.vertices[i].co=p*FT
        if kind=='rower':
            # Extend the rail, not the flywheel: preserve round drums and spokes.
            restored={v.index:Vector((v.co.x/FT/ratios[0]+center.x,v.co.y/FT/ratios[1]+center.y,v.co.z/FT/ratios[2]+lo.z)) for v in me.vertices}
            for ids in components(me):
                pts=[restored[i] for i in ids]
                lower=Vector([min(p[k] for p in pts) for k in range(3)])
                upper=Vector([max(p[k] for p in pts) for k in range(3)])
                c=(lower+upper)/2
                rail=(upper.y-lower.y)>6 and (upper.x-lower.x)<.5
                foot=(upper.z<.31 and upper.x-lower.x>1.9)
                rear_foot=foot and c.y<0
                for i,p in zip(ids,pts):
                    y=2.5+(p.y-2.5)*7.68/6.4 if rail else p.y-(1.28 if rear_foot else 0)
                    z=p.z-.02 if foot else p.z+.0766666667
                    me.vertices[i].co=Vector((p.x,y+1.18,z))*FT
            bm=bmesh.new();bm.from_mesh(me)
            for y in [-3.6,3.53]:
                a=Vector((0,y,.14))*FT;b=Vector((0,y,.72))*FT
                new=bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=8,radius1=.075*FT,radius2=.075*FT,depth=(b-a).length)['verts']
                bmesh.ops.transform(bm,matrix=Matrix.Translation((a+b)/2),verts=new)
            bm.to_mesh(me);bm.free()
        me.update()
        actual_size=[(max(v.co[k] for v in me.vertices)-min(v.co[k] for v in me.vertices))/FT for k in range(3)]
        equipment_changes.append({'category':kind,'previous_xyz_ft':list(size),
                                  'corrected_xyz_ft':actual_size,'source':SOURCES[kind]})
    for o in matches:
        o['Dimensional reference']=SOURCES[kind]
        o['Verification status']='Representative product envelope; actual installed make/model not provided.'
        if kind=='rower':o['Seat height above finished floor (in)']=14

# Restore actual floor contact instead of leaving models floating/embedded.
for o in asset_objs:
    if o['Asset type']=='rower':
        o.location.y=(9.2 if o.location.y/FT<15 else 19.2)*FT
    if o['Asset type']=='stair climber':o.location.y=41.5*FT
    if o.name.startswith('Women two-tier changing locker'):o.location.y=1.36*FT
    floor=.2075 if o['Asset type']=='power rack' else (.175 if o['Asset type']=='sled' else .05)
    local_low=min(v.co.z for v in o.data.vertices)/FT
    o.location.z=(floor-local_low*o.scale.z)*FT
    if 'Verification status' not in o:
        o['Verification status']='Generic equipment/fixture; dimensions plausible but not measured on site.'
changes.append('Rescaled treadmills, stair climbers, rowers and SkiErgs using manufacturer envelopes; fixed floor contact and two SkiErg/wall clashes.')
changes.append('Moved stair climbers away from treadmill rear clearance zones; retained all equipment instances.')
changes.append('Repositioned vanity tops and the women’s locker row clear of perimeter finishes; provided approximately 3 ft on both sides of the changing benches.')

# Rebuild each internal leaf around a true jamb hinge, with matching frame and
# handles, instead of rotating a floating rectangle around its center.
door_col=COL['16']
for o in list(door_col.objects):bpy.data.objects.remove(o,do_unlink=True)
door_records=[]
def door(name,axis,fixed,lo,hi,angle,mat):
    rough=hi-lo;clear=rough-.2;width=clear-.12
    hinge=(fixed,lo+.16,0) if axis=='Y' else (lo+.16,fixed,0)
    root=bpy.data.objects.new('Door pivot • '+name,None);door_col.objects.link(root)
    root.location=Vector(hinge)*FT;root.rotation_euler.z=math.radians(angle);root.empty_display_size=.12*FT
    root['Opening clear width (ft)']=clear;root['Rough height (ft)']=8
    root['Status']='Illustrative 8 ft rough height; actual door measurements required.'
    bottom=.075;top=7.88
    leaf=box(name+' door leaf',(width/2,0,(bottom+top)/2),(width,.12,top-bottom),mat,door_col,bevel=.025);leaf.parent=root
    for z in [1,4,7]:
        hinge_part=cylinder(name+' hinge',(0,0,z),(0,0,z+.2),.045,MAT['chrome'],door_col);hinge_part.parent=root
    for side in (-1,1):
        handle=cylinder(name+' handle',(width-.35,side*.13,3.45),(width-.35,side*.13,3.95),.035,MAT['chrome'],door_col);handle.parent=root
    for side in (lo+.05,hi-.05):
        loc=(fixed,side,4.025) if axis=='Y' else (side,fixed,4.025)
        dims=(.49,.1,7.95) if axis=='Y' else (.1,.49,7.95)
        box(name+' door jamb',loc,dims,MAT['edge'],door_col)
    loc=(fixed,(lo+hi)/2,7.95) if axis=='Y' else ((lo+hi)/2,fixed,7.95)
    dims=(.49,rough,.1) if axis=='Y' else (rough,.49,.1)
    box(name+' door head',loc,dims,MAT['edge'],door_col)
    door_records.append({'door':name,'rough_width_ft':rough,'clear_jamb_width_ft':clear,'rough_height_ft':8,'hinge_ft':hinge})

door('Women','Y',19.735,.7,4,150,MAT['purple'])
door('Men','Y',19.735,15.55,18.85,150,MAT['cyan'])
door('Cardio','Y',19.735,30.55,33.85,150,MAT['glass'])
door('Group studio','Y',84.265,.7,4,30,MAT['oak'])
door('Reception access','Y',84.265,40.5,44,30,MAT['glass'])
for i,(lo,hi) in enumerate([(86,88.8),(91,93.8),(96.3,99.1)]):
    door('Support '+str(i+1),'X',40,lo,hi,-65,MAT['oak'])
door('Group exercise exterior exit','Y',99.735,9,12.5,90,MAT['edge'])
changes.append('Rebuilt nine doors with true hinge pivots and jambs; corrected openings that intersected perpendicular walls; removed two unsupported south-wall openings.')

# Keep portal columns and terminal trusses inside the revised exterior finish.
for o in list(COL['06'].objects):
    if o.type!='MESH':continue
    if o.name.startswith('Portal steel column'):
        transform_parts(o,lambda p,c:(p.x+(.265 if c.x<1 else (-.265 if c.x>99 else 0)),p.y+(.265 if c.y<1 else -.265),p.z))
    elif o.name.startswith(('Steel truss chord','Triangular web bracing')):
        transform_parts(o,lambda p,c:(p.x+(.265 if c.x<1 else (-.265 if c.x>99 else 0)),.265+p.y*(59.47/60),p.z))
    elif o.name.startswith(('Enclosed corrugated gable','Gable vertical seam')):
        transform_parts(o,lambda p,c:(p.x+(.265 if c.x<50 else -.265),p.y,p.z))

# Trim sanitary cubicle partitions at the adjoining wall face (they previously
# ran through it by 2.1 inches). No fixture count changes.
for o in COL['15'].objects:
    if 'cubicle partition' in o.name:
        if o.data.users>1:o.data=o.data.copy()
        ceiling_y=29.735 if o.name.startswith('Men') else 14.735
        inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            if p.y/FT>ceiling_y:p.y=ceiling_y*FT
            v.co=inv@p

# Correct inward-facing box normals inherited from the first generator, without
# changing mesh dimensions. One pass per shared datablock preserves instancing.
normal_meshes={o.data for o in bpy.data.objects if o.type=='MESH'}
for me in normal_meshes:
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update()
changes.append('Corrected reversed mesh normals and clipped sanitary partitions to their wall faces; shared equipment meshes retained.')

for o in bpy.data.objects:
    if o.name.startswith('Rubber tile joint X'):
        transform_parts(o,lambda p,c:(p.x,max(p.y,4.55),p.z))

# A dedicated review scene adds the plan's dimensional chains without crowding
# the normal presentation scenes or enlarging the hanging signage.
audit_scene=PLAN.copy();audit_scene.name='06 | AUDIT • verified plan dimensions'
audit_scene.use_fake_user=True  # A copied, inactive scene otherwise drops out on save/reopen.
bpy.context.window.scene=audit_scene
dim_col=bpy.data.collections.new('23 | AUDIT DIMENSIONS • optional')
audit_scene.collection.children.link(dim_col)
bpy.context.view_layer.update()
for lc in audit_scene.view_layers[0].layer_collection.children:
    if lc.name.startswith('22 |'):lc.exclude=True
font=next(f for f in bpy.data.fonts if 'DIN Condensed' in f.name)
ink=bpy.data.materials.get('Audit • dimension ink') or bpy.data.materials.new('Audit • dimension ink')
ink.diffuse_color=(.78,.92,.72,1);ink.use_nodes=True
p=ink.node_tree.nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value=ink.diffuse_color
p.inputs['Emission Color'].default_value=ink.diffuse_color
p.inputs['Emission Strength'].default_value=.75
dark_ink=ink.copy();dark_ink.name='Audit • charcoal dimension ink';dark_ink.diffuse_color=(.012,.024,.025,1)
dark_p=dark_ink.node_tree.nodes.get('Principled BSDF')
dark_p.inputs['Base Color'].default_value=dark_ink.diffuse_color
dark_p.inputs['Emission Color'].default_value=dark_ink.diffuse_color
def dim_line(name,points):
    data=bpy.data.curves.new(name+' curve','CURVE');data.dimensions='3D'
    data.bevel_depth=.025*FT;data.bevel_resolution=0
    sp=data.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*[x*FT for x in co],1)
    data.materials.append(ink);o=bpy.data.objects.new(name,data);dim_col.objects.link(o)
    o.visible_shadow=False;o.visible_diffuse=False;o.visible_glossy=False;o.show_in_front=True
    return o
def dim_text(name,body,loc,vertical=False,size=1.05):
    data=bpy.data.curves.new(name+' text','FONT');data.body=body;data.font=font
    data.size=size*FT;data.align_x='CENTER';data.align_y='CENTER';data.resolution_u=3
    data.materials.append(ink);o=bpy.data.objects.new(name,data);dim_col.objects.link(o)
    o.location=Vector(loc)*FT
    if vertical:o.rotation_euler.z=math.pi/2
    o.visible_shadow=False;o.visible_diffuse=False;o.visible_glossy=False;o.show_in_front=True
    return o
def dimension(name,a,b,body,offset=.8):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))
    parts=[dim_line(name,[(*a,9),(*b,9)])]
    for pt in (a,b):parts.append(dim_line(name+' tick',[(*(pt-n*.3),9),(*(pt+n*.3),9)]))
    if body=='16 FT':offset=-1
    mid=(a+b)/2+n*offset
    parts.append(dim_text(name,body,(*mid,9.02),abs(d.y)>.5))
    if body in {'16 FT','4 FT'}:
        for o in parts:o.data.materials.clear();o.data.materials.append(dark_ink)
cy=30+DELTA
for a,b,body in [(20,42,'22 FT'),(42,58,'16 FT'),(58,80,'22 FT')]:
    dimension('Core clear chain',(a,cy),(b,cy),body)
dimension('South 18 ft chain',(50,4+DELTA),(50,22+DELTA),'18 FT')
dimension('North 18 ft chain',(50,38+DELTA),(50,56+DELTA),'18 FT')
dimension('East passage clear',(80,25),(84,25),'4 FT',1)
dimension('South passage clear',(64,.53),(64,4.53),'4 FT',-1)
dim_line('AC axis datum',[(20.7,56+DELTA,9),(80,56+DELTA,9)])
dim_text('AC reference note','AC CENTRELINE',(69,57.6,9.02),size=.8)
dim_text('Audit legend','DIMENSION AUDIT  /  CLEAR CORE + CIRCULATION',(50,-5.5,9.02),size=1.0)
dim_text('Audit caveat','HEIGHTS, FIXTURES AND UNLOCATED PHOTO FEATURES REMAIN UNVERIFIED',(50,-7,9.02),size=.65)
audit_scene.render.filepath=str(OUT/'audited_dimensions.png')

unknowns=[
 'Eaves/ridge height: retained at estimated 18/21 ft; no measured height was provided.',
 'The photographed staircase and upper platform are not located on the plan. They remain omitted pending a marked location and dimensions.',
 'The photographed window band, wall vents and HYBRID TRAINING wall are not located on the plan; their exact position/size is unresolved.',
 'The ceiling photo shows a row of training racks. Their exact count, model and mapping to the plan are unconfirmed; the current equipment arrangement is proposed.',
 'Actual equipment makes, quantity and detailed mechanism dimensions are unverified. Four categories use documented representative product envelopes, not exact replicas.',
 'Doors, wall thickness, sanitary fixtures, lockers, reception furniture, exterior canopy/shutter, duct diameter and structural steel are conceptual dimensions.',
 'Only 100 x 60 ft, 16 ft circle, 22/18 ft offsets and 4 ft east passage are explicitly dimensioned in the source. Remaining zone splits are inferred.',
 '100 x 60 ft is interpreted as the exterior finish outline for this revision; confirm whether the site measurement is outside-to-outside or clear internal.',
 'This is not a surveyed as-built model, a structural check or an accessibility/fire/egress compliance assessment.',
]
summary={'output':str(TARGET),'source':bpy.data.filepath,'changes':changes,'equipment_envelope_corrections':equipment_changes,
         'door_openings':door_records,'remaining_unknowns':unknowns,
         'dimension_convention':'Feet. 100 x 60 exterior-finish outline; 4 ft clear paths. Undimensioned room bays remain inferred gross zones.',
         'references':SOURCES}
(OUT/'proportion_corrections.json').write_text(json.dumps(summary,indent=2))
for s in bpy.data.scenes:
    s['Proportion audit applied']=True
    s['Dimensional confidence']='Explicit plan dimensions checked. Inferred room splits and unmeasured site details are not certified.'
    s['Dimension convention']=summary['dimension_convention']
    s['Height assumption']='18 ft eaves / 21 ft ridge — UNMEASURED, retained estimate.'
    s['Measured footprint']='100 ft x 60 ft matches the supplied drawing; not a site survey.'
    s['Proportion audit notes']='See PROPORTION AUDIT text and scene 06. Door jamb clear widths do not certify usable egress width.'
note=bpy.data.texts.get('PROPORTION AUDIT • measurements and unresolved items') or bpy.data.texts.new('PROPORTION AUDIT • measurements and unresolved items')
note.clear();note.write(json.dumps(summary,indent=2))
guide=bpy.data.texts.get('START HERE • model guide & assumptions')
if guide:
    guide.clear()
    guide.write('CORE CULTURE / PROPORTION-AUDITED MODEL\n\nOpen scene 06 for the dimensional chains, or scene 01 for the furnished cutaway.\n'
                'The prior model is retained as Core_Culture_Gym_before_proportion_audit.blend.\n\n'+
                '\n'.join(changes)+'\n\nUNVERIFIED / MISSING SITE INFORMATION\n'+ '\n'.join(unknowns)+'\n')
for o in bpy.data.objects:
    if o.name=='Scale caveat':o.data.body='DRAWN DIMENSIONS CHECKED  /  UNMEASURED SITE DETAILS REMAIN ESTIMATED'
    if o.name.startswith('HANGING SIGN •'):
        o['Verification status']='Proposed signage, not an existing measured installation.'
CUT.render.filepath=str(OUT/'audited_cutaway.png')
PLAN.render.filepath=str(OUT/'audited_floor_plan.png')
bpy.context.window.scene=CUT
for screen in bpy.data.screens:
    for area in screen.areas:
        if bpy.app.background and area.type=='CONSOLE':area.type='VIEW_3D' if area.width>500 else 'PROPERTIES'
        for space in area.spaces:
            if space.type=='VIEW_3D':
                space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=13
                space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False
for o in bpy.context.selected_objects:o.select_set(False)
bpy.context.view_layer.objects.active=None
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
print('AUDITED_MODEL_SAVED',str(TARGET),flush=True)
print(json.dumps(summary,indent=2),flush=True)
if bpy.app.background and os.environ.get('GYM_AUDIT_RENDER','1')=='1':
    for scene in (CUT,PLAN,audit_scene):
        bpy.context.window.scene=scene;bpy.ops.render.render(write_still=True)
        print('AUDIT_RENDER_DONE',scene.name,flush=True)
    bpy.context.window.scene=CUT
print('PROPORTION_CORRECTION_COMPLETE',flush=True)
