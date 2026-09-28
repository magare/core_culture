"""Core Culture gym — measured plan reconstruction, authored in feet, stored in meters.

Run with Blender's bundled Python. All assets are native, editable mesh/curve objects.
"""
import bpy
import math
import json
import os
from mathutils import Vector
from pathlib import Path

OUT = Path(__file__).resolve().parent
FT = 0.3048
PI = math.pi
W, D, H = 100.0, 60.0, 18.0
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = '01 | CUTAWAY • furnished plan'
COL = {}

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    COL[name] = c
    return c

ground = collection('00 | Presentation base')
floors = collection('01 | Floors • measured zoning')
lowwalls = collection('02 | Walls • lower cutaway')
rearwalls = collection('03 | Rear feature wall • full height')
upperwalls = collection('04 | Exterior walls • upper')
partitions = collection('05 | Partitions • upper')
roof = collection('06 | Roof & steel structure • removable')
facade = collection('07 | Entrance facade & canopy')
hvac = collection('08 | Exposed silver HVAC')
weights = collection('10 | Weight training')
hyrox = collection('11 | HYROX & 16 ft central circle')
cardio = collection('12 | Cardio')
reception = collection('13 | Reception & support rooms')
studio = collection('14 | Group exercise')
washrooms = collection('15 | Washrooms & changing')
doors = collection('16 | Doors & glazing')
labels = collection('20 | Floor wayfinding')
dimensions = collection('21 | Plan dimensions & title')
lights = collection('30 | Interior lights')
studio_lights = collection('31 | Presentation lighting')
cameras = collection('40 | Cameras')
refs = collection('90 | Packed source images • hidden')
library = collection('99 | Equipment templates • hidden')
ACTIVE = floors

def material(name, color, rough=0.5, metallic=0, noise=0, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    if noise:
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = noise
        tex.inputs['Detail'].default_value = 2
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .15
        ramp.color_ramp.elements[0].color = tuple(c*.68 for c in color)+(1,)
        ramp.color_ramp.elements[1].position = .85
        ramp.color_ramp.elements[1].color = tuple(min(1,c*1.2) for c in color)+(1,)
        m.node_tree.links.new(tex.outputs['Fac'], ramp.inputs[0])
        m.node_tree.links.new(ramp.outputs[0], p.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .15
        bump.inputs['Distance'].default_value = .012 if noise<40 else .002
        m.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs[0], p.inputs['Normal'])
    return m

M = {}
M['metal'] = material('01 • anthracite powder-coated steel',(.035,.047,.048),.32,.6)
M['rib'] = material('02 • folded graphite cladding',(.06,.075,.078),.42,.58)
M['edge'] = material('03 • blackened steel edges',(.012,.018,.021),.3,.62)
M['rubber'] = material('04 • charcoal recycled rubber flooring',(.03,.037,.038),.86,noise=150)
M['turf'] = material('05 • deep olive performance turf',(.075,.12,.025),.92,noise=95)
M['accent'] = material('06 • acid yellow lane graphics',(.76,.89,.17),.6)
M['white'] = material('07 • warm white enamel',(.89,.9,.85),.36,.08)
M['chrome'] = material('08 • satin stainless steel',(.57,.62,.62),.27,.92)
M['duct'] = material('09 • galvanized spiral duct',(.47,.54,.57),.38,.82,noise=65)
M['pad'] = material('10 • black equipment upholstery',(.018,.025,.024),.6,noise=110)
M['concrete'] = material('11 • warm polished concrete',(.37,.35,.31),.56,noise=9)
M['wall'] = material('12 • warm neutral partition plaster',(.62,.61,.55),.7,noise=18)
M['tile'] = material('13 • pale porcelain tile',(.6,.64,.6),.34,noise=50)
M['oak'] = material('14 • natural smoked oak',(.36,.22,.105),.52,noise=7)
M['mirror'] = material('15 • mirror panels',(.74,.83,.83),.045,1)
M['screen'] = material('16 • inactive blue console glass',(.045,.12,.16),.22,.35)
M['cyan'] = material('17 • washroom blue-grey',(.18,.32,.34),.6)
M['purple'] = material('18 • washroom warm mauve',(.35,.25,.3),.6)
M['led'] = material('19 • warm LED diffuser',(1,.87,.61),.28,emission=5)
M['ground'] = material('20 • presentation background',(.24,.27,.265),.92)
M['ink'] = material('21 • drawing annotation',(.78,.84,.77),.8)
M['glass'] = material('22 • tinted entrance glass',(.22,.4,.4),.15,.12)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = .74
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.45
M['ceramic'] = material('23 • white sanitary ceramic',(.86,.88,.86),.2)

def obj_mesh(name, verts, faces, mat, col=None):
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o = bpy.data.objects.new(name,mesh)
    (col or ACTIVE).objects.link(o)
    if mat: mesh.materials.append(mat)
    return o

def bevel(o, amount=.025, segments=2):
    if amount:
        mod = o.modifiers.new('Soft manufactured edges','BEVEL')
        mod.width = amount*FT
        mod.segments = segments
    return o

def box(name, loc, size, mat, col=None, edge=.02, rot=0):
    a,b,c = [s*FT/2 for s in size]
    verts = [(-a,-b,-c),(-a,-b,c),(-a,b,-c),(-a,b,c),(a,-b,-c),(a,-b,c),(a,b,-c),(a,b,c)]
    faces = [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o = obj_mesh(name,verts,faces,mat,col)
    o.location = Vector(loc)*FT
    o.rotation_euler.z = math.radians(rot)
    return bevel(o,edge)

def cylinder(name, a, b, radius, mat, col=None, sides=20, radius2=None):
    a,b = Vector(a)*FT,Vector(b)*FT
    d = b-a
    n = d.normalized()
    u = n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized()
    v = n.cross(u).normalized()
    r1,r2 = radius*FT,(radius if radius2 is None else radius2)*FT
    verts = [tuple(p+r*(u*math.cos(i*2*PI/sides)+v*math.sin(i*2*PI/sides))) for p,r in [(a,r1),(b,r2)] for i in range(sides)]
    faces = [tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]
    faces += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    o = obj_mesh(name,verts,faces,mat,col)
    for p in o.data.polygons[2:]: p.use_smooth=True
    return o

def tube(name, points, radius, mat, col=None, cyclic=False):
    curve=bpy.data.curves.new(name+' path','CURVE')
    curve.dimensions='3D'
    curve.resolution_u=12
    curve.bevel_depth=radius*FT
    curve.bevel_resolution=3
    s=curve.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*[c*FT for c in co],1)
    s.use_cyclic_u=cyclic
    curve.materials.append(mat)
    o=bpy.data.objects.new(name,curve)
    (col or ACTIVE).objects.link(o)
    return o

def sphere(name, center, radius, mat, col=None):
    verts=[]
    n,rings=24,12
    for j in range(rings+1):
        t=PI*j/rings
        for i in range(n):
            p=Vector(center)+radius*Vector((math.sin(t)*math.cos(i*2*PI/n),math.sin(t)*math.sin(i*2*PI/n),math.cos(t)))
            verts.append(tuple(p*FT))
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rings) for i in range(n)]
    o=obj_mesh(name,verts,faces,mat,col)
    for p in o.data.polygons:p.use_smooth=True
    return o

def ring(name, center, radius, thickness, mat, col=None, plane='XY'):
    pts=[]
    for i in range(96):
        u,v=radius*math.cos(2*PI*i/96),radius*math.sin(2*PI*i/96)
        off=(u,v,0) if plane=='XY' else ((u,0,v) if plane=='XZ' else (0,u,v))
        pts.append(tuple(center[j]+off[j] for j in range(3)))
    return tube(name,pts,thickness,mat,col,True)

font_path='/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf'
FONT=bpy.data.fonts.load(font_path)
REG=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial.ttf')
def text(name, body, loc, size, mat, col=None, rot=(0,0,0), align='CENTER', regular=False):
    data=bpy.data.curves.new(name+' typography','FONT')
    data.body=body
    data.font=REG if regular else FONT
    data.align_x=align
    data.align_y='CENTER'
    data.size=size*FT
    data.extrude=.003*FT
    data.space_character=1.1
    data.materials.append(mat)
    o=bpy.data.objects.new(name,data)
    (col or ACTIVE).objects.link(o)
    o.location=Vector(loc)*FT
    o.rotation_euler=[math.radians(a) for a in rot]
    return o

def area(name, loc, target, energy, size, col=lights, color=(1,.89,.73), size_y=None):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=energy
    data.color=color
    data.shape='DISK' if size_y is None else 'RECTANGLE'
    data.size=size*FT
    if size_y is not None: data.size_y=size_y*FT
    o=bpy.data.objects.new(name,data)
    col.objects.link(o)
    o.location=Vector(loc)*FT
    o.rotation_euler=(Vector(target)*FT-o.location).to_track_quat('-Z','Y').to_euler()
    return o

def mesh_asset(name, builder):
    global ACTIVE
    old=ACTIVE
    ACTIVE=library
    before=set(library.objects)
    builder()
    parts=[o for o in library.objects if o not in before]
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    verts,faces,matids,mats=[],[],[],[]
    for o in parts:
        eo=o.evaluated_get(dg)
        me=eo.to_mesh()
        offset=len(verts)
        verts.extend([tuple(o.matrix_world@v.co) for v in me.vertices])
        slots=[]
        # Keep original material datablocks; evaluated copies are transient.
        for m in o.data.materials:
            if m not in mats: mats.append(m)
            slots.append(mats.index(m))
        for p in me.polygons:
            faces.append(tuple(offset+i for i in p.vertices))
            matids.append(slots[p.material_index] if slots else 0)
        eo.to_mesh_clear()
    for o in parts: bpy.data.objects.remove(o,do_unlink=True)
    o=obj_mesh(name,verts,faces,None,library)
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,matids):p.material_index=i
    ACTIVE=old
    return o

def place(proto, name, loc, col, rot=0, scale=1):
    o=bpy.data.objects.new(name,proto.data)
    col.objects.link(o)
    o.location=Vector(loc)*FT
    o.rotation_euler.z=math.radians(rot)
    o.scale=(scale,scale,scale)
    o['Asset type']=proto.name
    return o

def foot(x,y,w=.5,d=.7):box('Non-slip rubber foot',(x,y,.08),(w,d,.16),M['pad'])
def beam(name,a,b,r=.075,mat=None):return cylinder(name,a,b,r,mat or M['metal'])
def plate(x,y,z,r=.72,axis='X',thickness=.18):
    a=[x,y,z];b=[x,y,z]
    k={'X':0,'Y':1,'Z':2}[axis]
    a[k]-=thickness/2;b[k]+=thickness/2
    cylinder('Bumper plate',a,b,r,M['pad'],sides=32)
    a[k]-=.013;b[k]+=.013
    cylinder('Steel plate hub',a,b,.14,M['chrome'],sides=16)

def dumbbell_at(x,y,z,r=.24):
    cylinder('Knurled dumbbell grip',(x,y-.3,z),(x,y+.3,z),.06,M['chrome'],sides=12)
    for d in [-1,1]:
        cylinder('Dumbbell rubber head',(x,y+d*.32,z),(x,y+d*.52,z),r,M['pad'],sides=16)
        cylinder('Dumbbell end cap',(x,y+d*.522,z),(x,y+d*.53,z),r*.7,M['metal'],sides=16)
        cylinder('Dumbbell chrome inset',(x,y+d*.533,z),(x,y+d*.542,z),.055,M['chrome'],sides=12)

def build_rack():
    for x in [-6.6,6.6]:
        foot(x,0,.6,2)
        box('Rack upright',(x,0,1.4),(.22,.32,2.7),M['metal'])
    for z,y in [(1.0,-.28),(2.1,.08)]:
        box('Angled steel dumbbell shelf',(0,y,z),(13.9,1.22,.16),M['metal'])
        box('Shelf lip',(0,y-.59,z+.12),(13.9,.07,.22),M['chrome'])
        for i in range(12):dumbbell_at(-6.1+i*1.1,y,z+.2+.14+i*.012,.2+i*.012)
    beam('Rear cross brace',(-6.6,.42,.45),(6.6,.42,2.45),.055)

def build_bench():
    for y in [-1.8,1.8]:
        box('Bench stabilizer',(0,y,.18),(1.7,.32,.25),M['metal'])
        for x in [-.7,.7]:foot(x,y,.36,.4)
        beam('Bench leg',(0,y,.25),(0,y*.8,1.1),.12)
    box('Bench main rail',(0,0,.72),(.25,4.5,.25),M['metal'])
    box('Bench back pad',(0,.65,1.3),(1.12,2.95,.32),M['pad'],edge=.12)
    box('Bench seat pad',(0,-1.28,1.3),(1.2,.82,.32),M['pad'],edge=.12)
    beam('Adjustment strut',(0,.8,.8),(0,1.8,1.13),.08,M['chrome'])
    cylinder('Bench transport wheel',(-.8,2,.2),(-.55,2,.2),.2,M['pad'])
    cylinder('Bench transport wheel',(.55,2,.2),(.8,2,.2),.2,M['pad'])

def build_power_rack():
    for x in [-2.05,2.05]:
        box('Rack base runner',(x,0,.15),(.45,5.1,.3),M['metal'])
        for y in [-1.8,1.8]:
            box('Perforated rack post',(x,y,3.7),(.28,.28,7.4),M['metal'])
            for z in [1+i*.4 for i in range(14)]:
                cylinder('Post adjustment hole',(x,y-.151,z),(x,y-.159,z),.045,M['chrome'],sides=8)
        box('Rack top rail',(x,0,7.35),(.3,4.2,.3),M['metal'])
        box('Safety spotter arm',(x,-.15,2.65),(.2,3.8,.22),M['chrome'])
        for z in [1.6,3.0,4.4]:
            cylinder('Plate storage horn',(x,1.8,z),(x+math.copysign(.85,x),1.8,z),.065,M['chrome'])
            plate(x+math.copysign(.4,x),1.8,z,.64)
    beam('Pull-up bar',(-2.05,-1.8,7.2),(2.05,-1.8,7.2),.07)
    beam('Rear upper crossbar',(-2.05,1.8,7.25),(2.05,1.8,7.25),.14)
    cylinder('Olympic barbell',(-3.65,-1.3,4.25),(3.65,-1.3,4.25),.053,M['chrome'])
    for x in [-2.85,-2.62,2.62,2.85]:plate(x,-1.3,4.25)

def build_cable():
    for x in [-3.2,3.2]:
        box('Cable tower base',(x,0,.18),(1.6,2.6,.35),M['metal'])
        box('Cable tower',(x,.65,3.9),(1.3,1,7.5),M['metal'])
        for z in [1+i*.2 for i in range(16)]:box('Selector weight plate',(x,0,z),(.98,.72,.15),M['edge'],edge=.01)
        for u in [-.43,.43]:beam('Guide rod',(x+u,-.45,.6),(x+u,-.45,7.3),.038,M['chrome'])
        cylinder('Cable pulley',(x-.1,-.55,6.9),(x+.1,-.55,6.9),.2,M['chrome'])
        tube('Coated pull cable',[(x,-.5,7),(x,-1.2,5.3),(x,-1.6,4.7)],.018,M['edge'])
        ring('Triangular-style cable handle',(x,-1.6,4.5),.22,.04,M['chrome'],plane='XZ')
    box('Cable crossover bridge',(0,.5,7.55),(7.5,.55,.42),M['metal'])
    for x in [-1.6,1.6]:beam('Pull-up angled grip',(x,.25,7.3),(x*1.35,-.3,7),.065)

def build_press():
    for x in [-1.5,1.5]:
        box('Press base',(x,0,.18),(.3,5.5,.3),M['metal'])
        beam('Angled press upright',(x,1.8,.3),(x,.75,5.3),.16)
        beam('Press lever',(x,.75,5.1),(x,-1.8,3.9),.12)
        beam('Press handle',(x,-1.8,3.9),(x*.65,-2.2,3.7),.09,M['chrome'])
        cylinder('Plate horn',(x,.25,4.85),(x*1.9,.25,4.85),.06,M['chrome'])
        plate(x*1.5,.25,4.85,.67)
    box('Seat',(0,-.8,1.6),(1.65,1.8,.35),M['pad'],edge=.1)
    back=box('Backrest',(0,.32,2.8),(1.6,.36,2.5),M['pad'],edge=.1)
    back.rotation_euler.x=math.radians(12)
    beam('Seat support',(0,-.8,.3),(0,-.8,1.4),.2)

def build_treadmill():
    box('Treadmill deck',(0,0,.42),(3.1,6.45,.52),M['metal'],edge=.15)
    box('Running belt',(0,-.15,.72),(2.35,5.7,.06),M['pad'],edge=.03)
    for x in [-1.4,1.4]:
        box('Side step rail',(x,-.1,.75),(.26,5.8,.13),M['chrome'])
        beam('Treadmill upright',(x,1.6,.6),(x,2.1,4.1),.13)
        tube('Handrail',[(x,2,3.8),(x,.5,3.1),(x,-.3,3.1)],.08,M['metal'])
    console=box('Console housing',(0,2.05,4.1),(2.95,.85,.24),M['metal'],edge=.12)
    console.rotation_euler.x=math.radians(22)
    display=box('Digital console',(0,1.97,4.25),(1.25,.57,.025),M['screen'],edge=.04)
    display.rotation_euler.x=math.radians(22)
    box('Safety key',(0,1.67,4.08),(.18,.1,.07),M['accent'])
    for x in [-.95,.95]:ring('Cup holder',(x,2.05,4.25),.16,.025,M['chrome'])

def build_bike():
    for y in [-1.55,1.55]:box('Bike stabilizer',(0,y,.15),(2,.3,.24),M['metal'])
    beam('Bike diagonal',(0,-1.4,.3),(0,.65,2.35),.16)
    beam('Bike seat tube',(0,-.7,.4),(0,-.65,2.7),.12)
    beam('Bike front strut',(0,1.35,.3),(0,.85,3.35),.12)
    cylinder('Flywheel',(-.18,1,.92),(.18,1,.92),.8,M['edge'],sides=40)
    cylinder('Flywheel inset',(-.2,1,.92),(.2,1,.92),.63,M['chrome'],sides=40)
    box('Saddle',(0,-.8,2.83),(1,.9,.18),M['pad'],edge=.09)
    tube('Bike handlebar',[(-.7,.8,3.2),(-.65,1.2,3.5),(.65,1.2,3.5),(.7,.8,3.2)],.07,M['pad'])
    cylinder('Crank axle',(-.4,-.15,.95),(.4,-.15,.95),.12,M['chrome'])
    for x,s in [(-.55,-1),(.55,1)]:
        beam('Pedal crank',(x,-.15,.95),(x,-.15+s*.4,.95+s*.35),.045,M['chrome'])
        box('Pedal',(x,-.15+s*.4,.95+s*.35),(.45,.28,.1),M['pad'])

def build_stair():
    profile=[(-2,0),(2,0),(2,2.4),(-2,.1)]
    verts=[(x*FT,y*FT,z*FT) for x in [-1.5,1.5] for y,z in profile]
    shell=obj_mesh('Stair climber sloping chassis',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],M['metal'])
    bevel(shell,.06)
    for i in range(4):box('Climber step',(0,-1.7+i*.85,.5+i*.58),(2.55,.85,.25),M['pad'],edge=.04)
    for x in [-1.45,1.45]:tube('Stair rail',[(x,-1.6,1),(x,-1.1,3.1),(x,1.6,5.3),(x,1.9,4.6)],.09,M['metal'])
    box('Stair console',(0,1.8,5.2),(1.8,.6,.18),M['screen'],edge=.1)

def build_rower():
    box('Rower sliding rail',(0,-.7,.65),(.35,6.4,.22),M['chrome'])
    for y in [-3.5,2.35]:box('Rower stabilizer',(0,y,.16),(2,.3,.28),M['metal'])
    cylinder('Air resistance drum',(-.42,2,1.4),(.42,2,1.4),.82,M['metal'],sides=36)
    for x in [-.435,.435]:
        ring('Flywheel trim',(x,2,1.4),.68,.028,M['chrome'],plane='YZ')
        for i in range(12):
            a=2*PI*i/12
            beam('Flywheel spoke',(x,2,1.4),(x,2+.63*math.cos(a),1.4+.63*math.sin(a)),.014,M['chrome'])
    box('Sliding rower seat',(0,-1.5,.98),(1.25,.92,.22),M['pad'],edge=.12)
    for x in [-.55,.55]:box('Rower foot plate',(x,.55,.95),(.42,.85,.1),M['pad'])
    beam('Rower screen arm',(0,2.05,1.9),(0,1.8,3.1),.06)
    box('Rower monitor',(0,1.7,3.12),(.6,.15,.65),M['screen'],edge=.035)
    tube('Rower pull chain',[(0,1.6,1.1),(0,.3,1.5)],.015,M['chrome'])
    beam('Rower handle',(-.65,.3,1.5),(.65,.3,1.5),.045)

def build_skierg():
    box('SkiErg platform',(0,0,.15),(3.2,4.6,.25),M['metal'],edge=.1)
    box('SkiErg upright',(0,1.7,3.7),(.4,.6,7.1),M['metal'])
    cylinder('SkiErg fan',(-.3,1.4,1.6),(.3,1.4,1.6),.95,M['edge'],sides=32)
    for s in [-1,1]:
        beam('SkiErg upper arm',(0,1.7,6.1),(s*1.2,1.1,7.5),.09)
        tube('SkiErg pull cord',[(s*1.2,1.1,7.5),(s*1.05,.8,4.3)],.017,M['chrome'])
        beam('SkiErg handle',(s*1.05,.8,4.3),(s*1.05,.8,3.8),.055)
    box('SkiErg monitor',(0,1.25,3.5),(.6,.15,.65),M['screen'])

def build_sled():
    for x in [-1.1,1.1]:
        box('Sled runner',(x,0,.15),(.38,3.3,.24),M['metal'],edge=.12)
        for y in [-1.1,1.1]:cylinder('Sled push post',(x,y,.3),(x,y,3.1),.09,M['metal'])
    box('Sled bridge',(0,0,.32),(2.4,2.2,.28),M['metal'])
    cylinder('Sled weight pin',(0,0,.4),(0,0,2.3),.08,M['chrome'])
    for z in [.6,.8,1,1.2]:plate(0,0,z,.67,'Z')

def build_toilet():
    box('Toilet foot',(0,0,.5),(1.2,1.45,1),M['ceramic'],edge=.25)
    box('Toilet bowl',(0,-.25,1.1),(1.45,2,.5),M['ceramic'],edge=.3)
    ring('Toilet seat',(0,-.3,1.38),.53,.1,M['white'])
    box('Toilet cistern',(0,.7,1.55),(1.5,.55,1.5),M['ceramic'],edge=.12)
    box('Flush button',(0,.7,2.32),(.22,.18,.04),M['chrome'])

def build_locker():
    box('Locker carcass',(0,0,3),(1.45,1.6,6),M['oak'],edge=.04)
    for z in [1.52,4.5]:
        box('Locker door',(0,-.84,z),(1.37,.08,2.88),M['wall'],edge=.025)
        box('Locker handle',(.44,-.925,z),(.04,.06,.45),M['edge'])
        for zz in [-.85,-.75,-.65]:box('Locker ventilation slot',(0,-.888,z+zz),(.65,.009,.025),M['edge'],edge=0)

print('Building native equipment library',flush=True)
assets={}
for key,fn in [('dumbbell rack',build_rack),('bench',build_bench),('power rack',build_power_rack),('cable machine',build_cable),('chest press',build_press),('treadmill',build_treadmill),('spin bike',build_bike),('stair climber',build_stair),('rower',build_rower),('ski erg',build_skierg),('sled',build_sled),('toilet',build_toilet),('locker',build_locker)]:
    assets[key]=mesh_asset(key,fn)
    print('  Asset:',key,flush=True)

# Exact outer shell: 100 x 60 ft. Floor zoning follows the supplied drawing.
ACTIVE=floors
box('Structural slab • 100 x 60 ft',(50,30,-.55),(100,60,1.1),M['concrete'],edge=.1)
zones=[('Cardio',0,20,30,60,'rubber'),('Men washroom',0,20,15,30,'tile'),('Women washroom',0,20,0,15,'tile'),('Weight training',20,80,28,60,'rubber'),('Weight training return',80,84,46,60,'rubber'),('HYROX',20,80,4,28,'rubber'),('Passage south',20,84,0,4,'concrete'),('Passage east',80,84,4,46,'concrete'),('Reception',84,100,40,60,'concrete'),('Support rooms',84,100,32,40,'concrete'),('Group exercise',84,100,0,32,'oak')]
for name,x1,x2,y1,y2,m in zones:
    o=box(name+' floor',((x1+x2)/2,(y1+y2)/2,.025),(x2-x1,y2-y1,.05),M[m],edge=0)
    o['Boundary in feet']=[x1,x2,y1,y2]
    o['Area in square feet']=(x2-x1)*(y2-y1)

# Flooring joints. Thin grooves use subdued materials rather than heavy diagram lines.
for x in range(22,80,4):box('Rubber tile joint X',(x,32,.057),(.012,55.7,.008),M['edge'],edge=0)
for y in range(6,60,4):box('Rubber tile joint Y',(50,y,.057),(59.8,.012,.008),M['edge'],edge=0)
for x in range(2,20,2):box('Washroom grout X',(x,15,.06),(.017,29.6,.008),M['wall'],edge=0)
for y in range(2,30,2):box('Washroom grout Y',(10,y,.06),(19.6,.017,.008),M['wall'],edge=0)
for i in range(25):box('Studio oak plank joint',(84.4+i*.62,16,.058),(.014,31.5,.012),M['edge'],edge=0)
for j in range(6):
    for i in range(25):box('Staggered end grain joint',(84.4+i*.62,1+j*5+(i%3)*1.4,.058),(.62,.017,.01),M['edge'],edge=0)

# Ground and architectural display plinth.
box('Dark concrete presentation plinth',(50,30,-1.4),(103,63,.7),M['edge'],ground,edge=.2)
box('Studio ground',(50,30,-1.85),(1000,1000,.15),M['ground'],ground,edge=0)

def wall_seg(name,a,b,height=H,external=False,rear=False,thickness=.45):
    a,b=Vector(a),Vector(b)
    length=(b-a).length
    mid=(a+b)/2
    rot=math.degrees(math.atan2(b.y-a.y,b.x-a.x))
    cut=3.3
    box(name+' • base',(mid.x,mid.y,cut/2),(length,thickness,cut),M['concrete'] if external else M['wall'],lowwalls,edge=.025,rot=rot)
    col=rearwalls if rear else (upperwalls if external else partitions)
    if height>cut:
        box(name+' • upper',(mid.x,mid.y,(cut+height)/2),(length,thickness,height-cut),M['rib'] if external else M['wall'],col,edge=.025,rot=rot)
    if external:
        n=max(1,int(length/.9))
        for i in range(n):
            t=(i+.5)/n
            p=a+(b-a)*t
            box(name+' • cladding rib',(p.x,p.y,(3.4+height)/2),(.075,thickness+.065,height-3.4),M['metal'],col,edge=.007,rot=rot)
    box(name+' • skirting',(mid.x,mid.y,.3),(length,thickness+.08,.42),M['edge'],lowwalls,edge=.01,rot=rot)

def wall_open(name,orientation,fixed,start,end,openings,height=H,external=False,rear=False):
    point=lambda t:(t,fixed) if orientation=='X' else (fixed,t)
    cur=start
    for lo,hi,dh in sorted(openings):
        if lo>cur:wall_seg(name,point(cur),point(lo),height,external,rear)
        center=(lo+hi)/2
        loc=(center,fixed,(dh+height)/2) if orientation=='X' else (fixed,center,(dh+height)/2)
        size=(hi-lo,.45,height-dh) if orientation=='X' else (.45,hi-lo,height-dh)
        box(name+' • lintel',loc,size,M['rib'] if external else M['wall'],rearwalls if rear else (upperwalls if external else partitions),edge=.02)
        cur=hi
    if cur<end:wall_seg(name,point(cur),point(end),height,external,rear)

wall_seg('North corrugated wall',(0,60),(100,60),external=True,rear=True)
wall_seg('West corrugated wall',(0,0),(0,60),external=True)
wall_open('South exterior','X',0,0,100,[(20,23.5,8),(84,87.5,8)],external=True)
wall_open('Entrance / east facade','Y',100,0,60,[(9,12.5,8),(33.5,40,10),(49,56,9)],external=True)
wall_open('Cardio & washroom partition','Y',20,0,60,[(.4,3.5,8),(15.2,18.3,8),(29.8,33,8)],height=10)
wall_seg('Washroom separation',(0,15),(20,15),height=10)
wall_seg('Cardio / washroom partition',(0,30),(20,30),height=10)
wall_open('East circulation partition','Y',84,0,60,[(.4,3.5,8),(40.5,44,8)],height=10)
wall_seg('Studio north wall',(84,32),(100,32),height=10)
wall_open('Support room front','X',40,84,100,[(86,88.8,8),(91,93.8,8),(96.3,99.1,8)],height=10)
wall_seg('Support room partition A',(89.3,32),(89.3,40),height=10)
wall_seg('Support room partition B',(94.5,32),(94.5,40),height=10)

def door_leaf(name,loc,width=3.1,rot=0,mat=None,glass=False):
    # Leaf is shown slightly open. Frame dimensions remain at the true opening.
    m=mat or M['oak']
    o=box(name+' door leaf',(0,0,0),(width,.12,7.7),m,doors,edge=.04)
    o.location=Vector((loc[0],loc[1],3.9))*FT
    o.rotation_euler.z=math.radians(rot)
    direction=Vector((math.cos(math.radians(rot)),math.sin(math.radians(rot)),0))
    handle=o.location/FT+direction*(width*.35)
    cylinder(name+' handle',(handle.x,handle.y-.13,3.6),(handle.x,handle.y-.13,4.15),.045,M['chrome'],doors)
    return o

door_leaf('Cardio',(19.3,31.6),2.9,55,M['glass'])
door_leaf('Men',(19.45,16.8),2.8,67,M['cyan'])
door_leaf('Women',(19.45,1.9),2.8,67,M['purple'])
door_leaf('Group studio',(84.55,2),2.9,62,M['oak'])
door_leaf('Reception access',(83.5,42.3),3.2,72,M['glass'])
for x in [87.4,92.4,97.7]:door_leaf('Support',(x,40),2.6,16,M['oak'])
door_leaf('South exit',(21.8,.15),3.2,12,M['edge'])
door_leaf('Group exercise exterior exit',(99.85,10.75),3.1,90,M['edge'])

# Roof: low-pitch warehouse gable and black steel trusses; separately removable.
for y1,y2,z1,z2 in [(0,30,H,21),(30,60,21,H)]:
    verts=[(-.5*FT,y1*FT,z1*FT),(100.5*FT,y1*FT,z1*FT),(100.5*FT,y2*FT,z2*FT),(-.5*FT,y2*FT,z2*FT)]
    o=obj_mesh('Standing seam roof slope',verts,[(0,1,2,3)],M['rib'],roof)
    sol=o.modifiers.new('Roof sheet thickness','SOLIDIFY');sol.thickness=.06*FT
for i in range(112):
    x=-.2+i*.9
    cylinder('Roof standing seam A',(x,-.3,H+.015),(x,30,21.04),.035,M['metal'],roof,sides=6)
    cylinder('Roof standing seam B',(x,30,21.04),(x,60.3,H+.015),.035,M['metal'],roof,sides=6)
for x in range(0,101,20):
    for y in [0,60]:box('Portal steel column',(x,y,8.8),(.48,.48,17.6),M['metal'],roof)
    for a,b in [((x,0,17.6),(x,30,20.5)),((x,30,20.5),(x,60,17.6)),((x,0,16.5),(x,60,16.5))]:
        cylinder('Steel truss chord',a,b,.15,M['metal'],roof,sides=8)
    for y in range(0,60,6):
        z=17.6+2.9*(1-abs((y+3)-30)/30)
        cylinder('Triangular web bracing',(x,y,16.5),(x,y+3,z),.075,M['metal'],roof,sides=8)
        cylinder('Triangular web bracing',(x,y+3,z),(x,y+6,16.5),.075,M['metal'],roof,sides=8)
for y in range(6,60,6):
    z=H+3*(1-abs(y-30)/30)-.3
    box('Roof purlin',(50,y,z),(100,.18,.28),M['metal'],roof)
for x in [0,100]:
    verts=[(x*FT,0,H*FT),(x*FT,60*FT,H*FT),(x*FT,30*FT,21*FT)]
    gable=obj_mesh('Enclosed corrugated gable end',verts,[(0,1,2)],M['rib'],roof)
    solid=gable.modifiers.new('Gable sheet thickness','SOLIDIFY');solid.thickness=.08*FT
    for y in range(1,60):
        h=3*(1-abs(y-30)/30)
        box('Gable vertical seam',(x,y,H+h/2),(.12,.07,h),M['metal'],roof,edge=.004)
# Longitudinal open web truss and vertical pendants from the fourth ceiling photo.
for z in [17.8,20.2]:cylinder('Longitudinal ridge truss chord',(0,30,z),(100,30,z),.12,M['metal'],roof,sides=8)
for x in range(0,100,5):
    cylinder('Ridge truss diagonal',(x,30,17.8),(x+5,30,20.2),.07,M['metal'],roof,sides=8)
    cylinder('Ridge truss vertical',(x,30,17.8),(x,30,20.2),.06,M['metal'],roof,sides=8)
for x in [25,40,55,70]:
    for y in [16,37]:
        cylinder('Pendant suspension wire',(x,y,15.6),(x,y,18.1),.013,M['edge'],roof,sides=8)
        cylinder('Vertical pendant dark backing',(x,y,12.7),(x,y,15.6),.065,M['metal'],roof,sides=12)
        cylinder('Vertical warm-white tube',(x,y-.02,12.72),(x,y-.02,15.57),.035,M['led'],roof,sides=12)

# Rear free-weight wall: continuous mirror, 3 racks, lettering and exposed duct.
for i in range(12):
    x=22.5+i*4.6
    box('Free-weight mirror panel %02d'%i,(x,59.66,4.5),(4.54,.05,7),M['mirror'],weights,edge=.012)
    box('Mirror vertical mullion',(x+2.29,59.6,4.5),(.035,.07,7.05),M['chrome'],weights,edge=0)
box('Mirror bottom protective rail',(48,59.48,1.0),(56,.16,.13),M['chrome'],weights)
text('Free-weight wall sign','THE  FREE WEIGHT  SECTION',(50,59.45,10.5),2.3,M['white'],rearwalls,rot=(90,0,0))
for x in [30,50,70]:place(assets['dumbbell rack'],'Two-tier dumbbell rack • '+str(x),(x,57,0),weights)
for x in [30,43,57,70]:place(assets['bench'],'Adjustable free-weight bench • '+str(x),(x,49,0),weights,rot=-15 if x<50 else 15)
for x in [27,37]:
    box('Lifting platform',(x,38,.105),(7.4,8.2,.14),M['edge'],weights)
    box('Oak platform center',(x,38,.19),(3.3,8.1,.035),M['oak'],weights)
    place(assets['power rack'],'Olympic squat rack • '+str(x),(x,38,.2),weights)
place(assets['cable machine'],'Dual adjustable cable crossover',(74,39,0),weights)
place(assets['chest press'],'Plate loaded chest press',(64,37,0),weights,rot=-12)
for x in [24,77]:
    for z in [1,2.7]:
        cylinder('Weight tree upright',(x,46,0),(x,46,3.5),.13,M['metal'],weights)
        for y in [-.7,.7]:cylinder('Plate storage branch',(x,46,z),(x,46+y,z),.07,M['chrome'],weights)
    box('Weight tree foot',(x,46,.1),(2.3,2.3,.2),M['metal'],weights)
    for z in [1,2.7]:
        for y in [45.5,46.5]:
            cylinder('Stored bumper plate',(x,y-.14,z),(x,y+.14,z),.7,M['pad'],weights)

# Duct coordinates preserve the diagram's 18 ft clearance to the 16 ft circle.
cylinder('Main AC duct • plan y = 56 ft',(20.7,56,14.0),(83,56,14.0),1.22,M['duct'],hvac,sides=48)
for x in range(21,84,2):ring('Spiral duct seam',(x,56,14),1.228,.022,M['chrome'],hvac,plane='YZ')
for x in [25,36,47,58,69,80]:
    box('AC grille collar',(x,54.86,14),(2.5,.12,1.35),M['chrome'],hvac)
    box('AC grille dark insert',(x,54.77,14),(2.22,.06,1.08),M['edge'],hvac)
    for z in [-.4,-.2,0,.2,.4]:box('AC grille horizontal louver',(x,54.72,14+z),(2.18,.04,.028),M['chrome'],hvac,edge=0)
    for dx in [-.9,-.6,-.3,0,.3,.6,.9]:box('AC grille upright',(x+dx,54.71,14),(.025,.03,1.05),M['chrome'],hvac,edge=0)
    cylinder('Duct hanger',(x,56,15.22),(x,56,18.1),.035,M['chrome'],roof,sides=10)
cylinder('Side AC distribution',(81.5,8,14),(81.5,56,14),.72,M['duct'],hvac,sides=32)
for y in range(9,56,3):ring('Side duct collar',(81.5,y,14),.73,.022,M['chrome'],hvac,plane='XZ')

# HYROX turf, two long lanes, start markings and detailed training equipment.
box('HYROX performance turf',(49,14,.1),(48,17,.15),M['turf'],hyrox,edge=.035)
for y in [5.75,14,22.25]:box('HYROX lane boundary',(49,y,.18),(47.8,.09,.018),M['white'],hyrox,edge=0)
for x in [25.5,72.5]:box('HYROX start / finish',(x,14,.18),(.16,16.5,.018),M['white'],hyrox,edge=0)
for y,number in [(9.8,'01'),(18.2,'02')]:
    text('Lane '+number,number,(28,y,.2),2.1,M['white'],hyrox,rot=(0,0,90))
    place(assets['sled'],'Weighted push sled • lane '+number,(36 if number=='01' else 62,y,.2),hyrox,rot=90)
    for x in range(33,72,8):box('Lane distance hash',(x,y-3.7,.19),(.1,.8,.025),M['accent'],hyrox,edge=0)
    text('Lane finish text '+number,'CORE CULTURE',(69,y,.2),.64,M['white'],hyrox,rot=(0,0,90))
for y in [9,19]:place(assets['rower'],'HYROX rowing ergometer',(76.5,y,0),hyrox)
for y in [10,20]:place(assets['ski erg'],'HYROX SkiErg',(22.4,y,0),hyrox,rot=90)
for x in [28,32,36]:
    box('Plyometric oak box',(x,25.5,1.05),(2.3,2,2.1),M['oak'],hyrox,edge=.09)
    box('Plyo hand slot',(x,24.486,1.2),(.65,.025,.16),M['edge'],hyrox,edge=.04)
for i in range(6):
    x=63+i*1.6
    sphere('Weighted wall ball',(x,26.2,.6),.52,M['pad'],hyrox)
    ring('Wall ball accent',(x,26.2,.6),.524,.018,M['accent'],hyrox,plane='XZ')
for i in range(3):
    pts=[(60-i*.35+j*.55,24.6+math.sin(j*.7)*.38,.12) for j in range(17)]
    tube('Coiled battle rope',pts,.052,M['pad'],hyrox)
cylinder('Central 16 ft functional circle',(50,30,.061),(50,30,.085),8,M['concrete'],hyrox,sides=128)
ring('Central circle • 16 ft diameter',(50,30,.105),7.96,.042,M['accent'],hyrox)
text('Central monogram','CC',(50,30.6,.12),3.3,M['white'],hyrox)
text('Central circle lettering','CORE CULTURE',(50,28.2,.12),.68,M['white'],hyrox)

# Cardio: three treadmills, two stair climbers, three cycles.
for x in [4.4,10,15.6]:place(assets['treadmill'],'Cardio treadmill',(x,54,0),cardio)
for x in [5.5,14]:place(assets['stair climber'],'Cardio stair climber',(x,43.5,0),cardio)
for x in [4,10,16]:place(assets['spin bike'],'Cardio spin cycle',(x,35.2,0),cardio)
for x in [5,10,15]:
    box('Cardio wall display surround',(x,59.5,8.3),(3.4,.15,2),M['edge'],cardio,edge=.1)
    box('Cardio wall display',(x,59.4,8.3),(3.15,.025,1.78),M['screen'],cardio,edge=.03)
text('Cardio wall sign','CARDIO',(10,59.5,11.5),1.75,M['white'],rearwalls,rot=(90,0,0))

# Reception: ribbed desk, seating, brand wall, planting and support rooms.
box('Reception desk body',(89,50.3,1.8),(3.1,9.3,3.6),M['oak'],reception,edge=.08)
box('Reception stone worktop',(89,50.3,3.68),(3.45,9.65,.2),M['concrete'],reception,edge=.06)
for y in [46+i*.3 for i in range(30)]:box('Reception desk fluting',(90.59,y,1.85),(.12,.11,3.45),M['edge'],reception,edge=.015)
box('Desk monitor stand',(88.8,51.4,3.95),(.65,.55,.35),M['metal'],reception)
box('Desk display',(88.75,51.4,4.45),(.12,1.6,.9),M['screen'],reception,edge=.06)
box('Reception illuminated toe',(90.66,50.3,.22),(.035,8.6,.1),M['led'],reception)
text('Reception desk logo','CC',(90.68,50.3,2.0),1.75,M['white'],reception,rot=(90,0,90))
box('Lobby sofa plinth',(96,44,.6),(5.6,2.6,1.1),M['edge'],reception,edge=.2)
box('Lobby sofa seat',(96,43.7,1.3),(5.6,2.4,.7),M['pad'],reception,edge=.2)
box('Lobby sofa back',(96,44.85,2),(5.6,.5,2),M['pad'],reception,edge=.2)
for x in [93.2,98.8]:box('Lobby sofa arm',(x,44,1.7),(.45,2.6,1.5),M['pad'],reception,edge=.12)
box('Lobby coffee table',(95.8,47,1.4),(3.5,1.65,.16),M['oak'],reception,edge=.07)
for x in [94.5,97.1]:
    for y in [46.5,47.5]:cylinder('Coffee table leg',(x,y,0),(x,y,1.3),.05,M['edge'],reception)
text('Reception brand wall','CORE CULTURE',(92,59.5,9.4),1.5,M['white'],rearwalls,rot=(90,0,0))
text('Reception descriptor','TRAIN WITH INTENT',(92,59.5,7.6),.5,M['white'],rearwalls,rot=(90,0,0),regular=True)
for x in [86.4,91.7,97.2]:
    box('Support desk',(x,33.3,2.5),(3.8,1.65,.18),M['oak'],reception)
    for dx in [-1.5,1.5]:box('Support desk leg',(x+dx,33.3,1.22),(.16,1.4,2.4),M['metal'],reception)
    box('Support chair seat',(x,35,1.55),(1.5,1.45,.2),M['pad'],reception,edge=.1)
    box('Support chair back',(x,35.6,2.35),(1.5,.18,1.4),M['pad'],reception,edge=.1)
    cylinder('Chair stem',(x,35,.25),(x,35,1.45),.08,M['chrome'],reception)
    for d in [-1,1]:box('Chair base',(x,35,.18),(1.8,.16,.13),M['metal'],reception,rot=d*45)

def plant(name,x,y,z=0,col=reception):
    cylinder(name+' planter',(x,y,z),(x,y,z+1.5),.7,M['concrete'],col,sides=24,radius2=.85)
    for i in range(9):
        a=i*2.4
        tip=(x+math.cos(a)*(1+.1*(i%3)),y+math.sin(a)*(1+.1*(i%3)),z+2.4+(i%4)*.45)
        cylinder(name+' stem',(x,y,z+1.2),tip,.025,M['turf'],col,sides=8)
        mid=Vector(tip);side=Vector((math.cos(a+PI/2),math.sin(a+PI/2),0))*.3
        base=mid-Vector((math.cos(a),math.sin(a),.4))*.7
        end=mid+Vector((math.cos(a),math.sin(a),.5))*.55
        verts=[tuple(v*FT) for v in [base,mid+side+Vector((0,0,.1)),end,mid-side,mid+Vector((0,0,.15))]]
        obj_mesh(name+' leaf',verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],M['turf'],col)
plant('Lobby plant',97.7,57.3)
plant('Welcome plant',86,56.5)

# Group exercise: continuous mirror, wall barre, mats and equipment storage.
for y in range(6,31,4):box('Studio full-height mirror',(84.28,y,4.7),(.045,3.94,6.5),M['mirror'],studio,edge=.01)
cylinder('Oak studio barre',(84.85,5,3.4),(84.85,30,3.4),.068,M['oak'],studio)
for y in range(6,31,4):cylinder('Barre bracket',(84.32,y,3.4),(84.85,y,3.4),.045,M['chrome'],studio)
for x in [89,95.5]:
    for y in [7.8,15.5,23.2]:
        box('Group exercise mat',(x,y,.105),(2.2,5.5,.09),M['pad'],studio,edge=.13)
        box('Mat centre logo',(x,y,.16),(.5,.15,.018),M['accent'],studio,edge=0)
        box('Yoga support block',(x+1.5,y+1.8,.3),(.65,1,.5),M['oak'],studio,edge=.05)
box('Studio equipment cabinet',(95,30.8,1.55),(7,1.6,3.1),M['oak'],studio,edge=.06)
for x in [92.5,94,95.5,97]:
    for z in [.8,2]:box('Studio cubby',(x,29.96,z),(1.3,.04,.9),M['edge'],studio)
    cylinder('Rolled exercise mat',(x,30.7,3.2),(x,30.7,4.1),.2,M['turf'],studio,sides=20)

# Washrooms: measured rooms, proposed sanitary fit-out and changing lockers.
for prefix,y0,m in [('Men',15,M['cyan']),('Women',0,M['purple'])]:
    for x in [2.2,6.4,10.6]:
        place(assets['toilet'],prefix+' WC',(x,y0+12.7,0),washrooms)
        box(prefix+' cubicle door',(x,y0+10,3),(3.5,.12,5.9),m,washrooms,edge=.04)
        box(prefix+' cubicle handle',(x+1.1,y0+9.88,3.1),(.09,.09,.5),M['chrome'],washrooms)
    for x in [.25,4.3,8.5,12.7]:box(prefix+' cubicle partition',(x,y0+12.45,3.4),(.13,5,6.7),M['wall'],washrooms)
    box(prefix+' vanity worktop',(2,y0+5.6,2.7),(3.1,6.5,.2),M['concrete'],washrooms,edge=.05)
    for yy in [y0+3.8,y0+7.3]:
        cylinder(prefix+' inset basin',(2,yy,2.79),(2,yy,3.05),.63,M['ceramic'],washrooms,sides=32,radius2=.71)
        cylinder(prefix+' basin recess',(2,yy,3.058),(2,yy,3.062),.48,M['tile'],washrooms,sides=32)
        tube(prefix+' faucet',[(1.15,yy,2.8),(1.15,yy,3.7),(1.7,yy,3.7)],.038,M['chrome'],washrooms)
    box(prefix+' vanity mirror',(.29,y0+5.6,5.25),(.045,6.2,3.4),M['mirror'],washrooms)
    for i in range(5):place(assets['locker'],prefix+' two-tier changing locker',(8+i*1.6,y0+1.2,0),washrooms,rot=180)
    box(prefix+' changing bench',(10,y0+5.1,1.5),(6,1.6,.22),M['oak'],washrooms,edge=.08)
    for x in [7.5,12.5]:box(prefix+' bench leg',(x,y0+5.1,.7),(.18,1.3,1.4),M['metal'],washrooms)
    box(prefix+' shower tray',(16.3,y0+12.3,.12),(4.8,4.8,.2),M['tile'],washrooms)
    box(prefix+' shower privacy screen',(14,y0+12.3,3.6),(.06,4.7,7),M['glass'],washrooms)
    tube(prefix+' shower riser',[(18.7,y0+13.7,3.4),(18.7,y0+13.7,7.4),(18.2,y0+13.7,7.4)],.037,M['chrome'],washrooms)
    cylinder(prefix+' shower head',(18.2,y0+13.7,7.3),(18.2,y0+13.7,7.4),.23,M['chrome'],washrooms)

# Industrial entrance facade, placed on the plan's right-hand / east wall.
for y in [49,52.5,56]:box('Entry aluminium stile',(100.02,y,4.5),(.24,.12,9),M['edge'],facade)
for z in [.15,9]:box('Entry aluminium transom',(100.02,52.5,z),(.25,7.2,.15),M['edge'],facade)
for y in [50.75,54.25]:
    box('Entrance glass leaf',(100.035,y,4.5),(.06,3.36,8.65),M['glass'],facade,edge=.015)
    cylinder('Entrance pull handle',(100.19,y+(.9 if y<52 else -.9),3.5),(100.19,y+(.9 if y<52 else -.9),5.1),.045,M['chrome'],facade)
    box('Frosted glass band',(100.076,y,3.2),(.01,3.3,2.1),M['cyan'],facade,edge=0)
box('Entrance canopy',(101.85,52.5,10.2),(4,9,.18),M['rib'],facade,edge=.03)
for y in [48,57]:
    cylinder('Canopy black support',(103.5,y,.1),(103.5,y,10.2),.09,M['edge'],facade)
    cylinder('Canopy diagonal bracket',(100,y,8.8),(103.5,y,10.1),.06,M['edge'],facade)
for y in [48.2+i*.45 for i in range(20)]:box('Canopy corrugation',(101.9,y,10.33),(4,.045,.07),M['chrome'],facade,edge=.006)
text('Exterior entrance lettering','THE ENTRANCE',(100.3,52.5,13.3),2.15,M['white'],facade,rot=(90,0,90))
ring('Facade brand circle',(100.3,44.4,7.9),2.9,.035,M['white'],facade,plane='YZ')
text('Facade monogram','CC',(100.32,44.4,7.8),3.5,M['white'],facade,rot=(90,0,90))
text('Facade logo heading','CORE CULTURE',(100.32,44.4,9.7),.61,M['white'],facade,rot=(90,0,90))
text('Facade logo footer','GYM',(100.32,44.4,5.9),.82,M['white'],facade,rot=(90,0,90))
box('Closed auxiliary rolling shutter',(100.015,36.75,5),(.15,6.5,10),M['rib'],facade)
for z in [i*.22 for i in range(46)]:box('Shutter slat',(100.11,36.75,z),(.045,6.45,.045),M['chrome'],facade,edge=.004)
box('Shutter protective hood',(100.7,36.75,10.4),(1.4,7,.18),M['edge'],facade)
for z in [.3,1.35,2.4]:box('Entrance shoe shelf',(101,44.3,z),(1.5,6.2,.08),M['metal'],facade)
for y in [41.2,44.3,47.4]:box('Shoe shelf frame',(101,y,1.3),(1.6,.09,2.6),M['chrome'],facade)
for y in [42,43.4,45,46.4]:
    for z in [.55,1.6]:
        for d in [-.16,.16]:box('Shoe pair',(101,y+d,z),(.9,.24,.25),M['pad'],facade,edge=.1)
plant('Exterior entry plant',101.2,47.3,2.5,facade)
box('Entrance concrete apron',(106,40,-.15),(12,42,.28),M['concrete'],facade,edge=.02)

# Legible floor wayfinding stays in the model; removable drawing annotations are separate.
for body,loc,size in [('CARDIO',(10,48.5,.085),1.35),('WEIGHT TRAINING',(50,44,.12),1.35),('HYROX',(51,24.7,.12),1.4),('RECEPTION',(94,56.9,.09),.84),('GROUP EX',(92,3.4,.09),1),('MEN',(16,21.4,.09),.9),('WOMEN',(16,6.2,.09),.8)]:
    text('Floor label • '+body,body,loc,size,M['white'] if body not in ['MEN','WOMEN','RECEPTION','GROUP EX'] else M['edge'],labels)
text('East passage label','4 FT  /  PASSAGE',(82,23,.09),.58,M['edge'],labels,rot=(0,0,90))
text('South passage label','C I R C U L A T I O N',(51,2,.09),.6,M['edge'],labels)
for i,x in enumerate([86.6,91.9,97.1]):text('Support label','SUPPORT %02d'%(i+1),(x,37.5,.09),.45,M['edge'],labels)
for x in [35,66]:
    tube('Circulation arrow',[(x-1.3,2,.1),(x+1.3,2,.1),(x+.6,2.5,.1)],.025,M['white'],labels)

def dimension(name,a,b,label,offset_text=(0,0),size=.95):
    tube(name+' line',[(*a,.06),(*b,.06)],.026,M['ink'],dimensions)
    direction=(Vector(b)-Vector(a)).normalized()
    normal=Vector((-direction.y,direction.x))*.55
    for p in [Vector(a),Vector(b)]:
        tube(name+' witness',[(p.x-normal.x,p.y-normal.y,.06),(p.x+normal.x,p.y+normal.y,.06)],.024,M['ink'],dimensions)
    mid=(Vector(a)+Vector(b))/2+Vector(offset_text)
    text(name+' dimension',label,(mid.x,mid.y,.08),size,M['ink'],dimensions,rot=(0,0,90 if abs(direction.y)>.5 else 0))
dimension('Overall width',(0,-3.2),(100,-3.2),'100 FT  /  30.48 M',(0,-1.0),1.1)
dimension('Overall depth',(-3.2,0),(-3.2,60),'60 FT  /  18.29 M',(-1.1,0),1.1)
dimension('Cardio / washroom bay',(0,63),(20,63),'20 FT',(0,1),.85)
dimension('Central clear width',(20,63),(80,63),'60 FT',(0,1),.85)
dimension('Passage width',(80,63),(84,63),'4 FT',(0,1),.75)
dimension('Reception / studio bay',(84,63),(100,63),'16 FT',(0,1),.85)
text('Presentation title','CORE CULTURE',(0,-8.5,.03),2.1,M['white'],dimensions,align='LEFT')
text('Presentation subtitle','GROUND FLOOR  /  6,000 SQ FT  /  FURNISHED SPATIAL STUDY',(0,-11,.03),.7,M['ink'],dimensions,align='LEFT',regular=True)
text('Scale caveat','PLAN DIMENSIONS MATCH REFERENCE  /  HEIGHTS + EQUIPMENT ESTIMATED',(100,-8.4,.03),.43,M['ink'],dimensions,align='RIGHT',regular=True)

# Lighting fixture geometry belongs to removable roof; light sources are independently grouped.
for x in [10,29,49,69,92]:
    for y in [10,28,46]:
        z=16.2 if 20<x<84 else 14.5
        box('Suspended linear luminaire',(x,y,z),(10,.32,.22),M['edge'],roof)
        box('Linear LED diffuser',(x,y,z-.13),(9.8,.24,.025),M['led'],roof,edge=.01)
        area('Linear interior light',(x,y,z-.18),(x,y,0),380,9.8,lights,size_y=1.2)
for x in [30,50,70]:area('Free-weight wall washer',(x,53,12),(x,59.5,5),280,9,lights,size_y=1.5)
for y in [7.5,22.5]:area('Washroom ceiling light',(10,y,9.6),(10,y,0),150,6,lights)
area('Studio softbox',(15,-25,90),(48,30,0),19000,75,studio_lights,color=(1,.93,.82))
area('Studio fill',(95,60,65),(50,30,0),14000,60,studio_lights,color=(.78,.88,1))
area('Studio rim',(-20,50,45),(35,35,0),8000,45,studio_lights,color=(1,.91,.74))
sun_data=bpy.data.lights.new('Daylight sun','SUN');sun_data.energy=1.5;sun_data.angle=.18
sun=bpy.data.objects.new('Daylight sun',sun_data);studio_lights.objects.link(sun)
sun.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-55))

def camera(name,loc,target,lens=35,ortho=None):
    data=bpy.data.cameras.new(name)
    data.lens=lens
    data.clip_end=1500
    o=bpy.data.objects.new(name,data);cameras.objects.link(o)
    o.location=Vector(loc)*FT
    o.rotation_euler=(Vector(target)*FT-o.location).to_track_quat('-Z','Y').to_euler()
    if ortho:data.type='ORTHO';data.ortho_scale=ortho*FT
    return o

cam_cut=camera('01 • Overall architectural cutaway',(142,-115,137),(49,26,0),ortho=137)
cam_plan=camera('02 • True orthographic floor plan',(50,27,170),(50,27,0),ortho=119)
cam_ext=camera('03 • Entrance facade',(141,77,19),(100,47,7.8),lens=34)
cam_int=camera('04 • Free-weight interior',(50,29,7.1),(50,58,6.1),lens=20)
cam_hyrox=camera('05 • HYROX interior',(77,6,6),(36,27,5.1),lens=22)

world=bpy.data.worlds.new('Neutral daylight world');world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(.37,.45,.5,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=.4

def scene_settings(s,cam,res=(1600,1200)):
    s.camera=cam;s.world=world
    s.unit_settings.system='IMPERIAL';s.unit_settings.scale_length=1;s.unit_settings.length_unit='FEET'
    s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True
    s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3
    s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'
    s.view_settings.view_transform='AgX'
    try:s.view_settings.look='AgX - Medium High Contrast'
    except TypeError:pass
    s.render.film_transparent=False
    s.render.image_settings.color_mode='RGB'
    s['Measured footprint']='100 ft x 60 ft (6,000 sq ft / 557.42 sq m)'
    s['Height assumption']='18 ft eaves / 21 ft ridge. Not measured from photographs.'
    s['Drawing coordinates']='Origin: lower-left of supplied floor plan. +X right, +Y up; stored in meters.'

def exclude(s,cols):
    for c in cols:
        lc=s.view_layers[0].layer_collection.children.get(c.name)
        if lc:lc.exclude=True

scene_settings(scene,cam_cut,(1800,1350))
exclude(scene,[upperwalls,partitions,roof,facade,lights,library,refs])
scene.view_settings.exposure=-.35
scene['View notes']='Cutaway removes upper front/side walls, internal upper walls and roof. Other scenes preserve enclosure.'

def new_scene(name,cam,excludes,res):
    s=bpy.data.scenes.new(name)
    for col in COL.values():s.collection.children.link(col)
    bpy.context.window.scene=s
    bpy.context.view_layer.update()
    scene_settings(s,cam,res);exclude(s,excludes)
    return s

plan_scene=new_scene('02 | PLAN • orthographic',cam_plan,[upperwalls,partitions,roof,facade,hvac,rearwalls,lights,library,refs],(1800,1400))
plan_scene.view_settings.exposure=-.3
ext_scene=new_scene('03 | EXTERIOR • entrance',cam_ext,[dimensions,labels,library,refs],(1600,1200))
int_scene=new_scene('04 | INTERIOR • free weights',cam_int,[dimensions,labels,library,refs,studio_lights],(1600,1100))
int_scene.view_settings.exposure=-.2
hyrox_scene=new_scene('05 | INTERIOR • HYROX',cam_hyrox,[dimensions,labels,library,refs,studio_lights],(1600,1100))

# Self-contained reference images, retained in the .blend but hidden from renders.
source_paths=[
 '/Users/magare/Downloads/WhatsApp Image 2026-09-21 at 5.05.08 PM.jpeg',
 '/Users/magare/Downloads/cc_core_culture_files/806299212_18087386489438400_7001765476852721714_n.jpg',
 '/Users/magare/Downloads/cc_core_culture_files/806299245_18087386486438400_8726183399223928327_n.jpg',
 '/var/folders/4f/_l80_r291837skq88vhgs0_80000gn/T/codex-clipboard-282e20e2-b4a5-49a7-ace7-e58382ba158a.png']
for idx,path in enumerate(source_paths):
    im=bpy.data.images.load(path,check_existing=True);im.pack()
    o=bpy.data.objects.new(['REFERENCE • dimensioned plan','REFERENCE • entrance photo','REFERENCE • free-weight photo','REFERENCE • ceiling and trusses'][idx],None)
    o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=100*FT
    o.location=Vector((50,30,-4-idx))*FT
    refs.objects.link(o)

readme='''CORE CULTURE / GYM MODEL
========================
01 CUTAWAY: furnished architectural overview (opens by default).
02 PLAN: true orthographic view of the supplied 100 x 60 ft layout.
03 EXTERIOR: enclosed warehouse with entrance glazing, sign and canopy.
04 INTERIOR: free-weight wall, mirror, racks, exposed AC duct.
05 INTERIOR: HYROX view.

Choose a scene from Blender's top-right scene selector. Numpad 0 = camera.
The roof, upper walls, partitions, equipment and labels have named collections.
All furniture/equipment is editable native geometry, with linked repeated meshes.
Use Object > Relations > Make Single User > Object & Data to vary one instance.
The source images and fonts are packed; no external assets are needed.

PLAN DIMENSIONS: 100 x 60 ft overall. Left bay 20 ft; clear central bay 60 ft;
east passage 4 ft; right bay 16 ft. Circle diameter 16 ft; AC centerline at y=56 ft.
The 18 ft dimensions locate the circle relative to the duct and HYROX south edge.
Cardio 20 x 30 ft. Each washroom 20 x 15 ft. Group studio 16 x 32 ft.
Reception 16 x 20 ft. Three support rooms are not assigned uses in the source.

ASSUMPTIONS: eaves 18 ft, ridge 21 ft, room partitions 10 ft, exterior walls 5.4 in.
Some zone boundaries are inferred from the diagram's proportions. The photo shows
finishes, not an equipment inventory. Equipment, sanitary fixtures, reception
furniture, roof structure and the roller shutter dimensions are proposed details.
The dashed circle is treated as an open central training/identity area.
This is a spatial visualization, not a surveyed as-built or construction drawing.

Ceiling steelwork and vertical pendant lights follow the fourth reference image.
The staircase/platform location remains unconfirmed and is not included in this version.
Created from the four user-supplied images; feet are converted to meters in mesh data.
'''
t=bpy.data.texts.new('START HERE • model guide & assumptions');t.write(readme)
(OUT/'MODEL_GUIDE.txt').write_text(readme)

prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL';prefs.get_devices()
    for dev in prefs.devices:dev.use=(dev.type=='METAL')
    for s in bpy.data.scenes:s.cycles.device='GPU'
except Exception as e:print('Using CPU rendering:',e,flush=True)

# Clean saved viewport: material colors, camera framing, no lights/camera wires.
bpy.context.window.scene=scene
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA'
            a.spaces.active.overlay.show_overlays=False
            a.spaces.active.shading.type='SOLID'
            a.spaces.active.shading.light='STUDIO'
            a.spaces.active.shading.color_type='MATERIAL'
            a.spaces.active.shading.show_cavity=True
            a.spaces.active.shading.cavity_type='BOTH'
            a.spaces.active.clip_end=1500
            a.spaces.active.region_3d.view_camera_zoom=13
for o in bpy.context.selected_objects:o.select_set(False)
bpy.context.view_layer.objects.active=None

summary={'footprint_ft':[W,D],'footprint_sqm':round(W*D*FT*FT,3),'assumed_eaves_ft':H,'scenes':[s.name for s in bpy.data.scenes],'object_count':len(bpy.data.objects),'mesh_count':len(bpy.data.meshes),'zone_area_sqft':sum((x2-x1)*(y2-y1) for _,x1,x2,y1,y2,_ in zones),'references_packed':all(bpy.data.images.get(Path(p).name).packed_file is not None for p in source_paths),'equipment_assets':list(assets),'assumptions':'See MODEL_GUIDE.txt and START HERE text in Blender'}
assert summary['zone_area_sqft']==6000,summary
assert len(source_paths)==4 and summary['references_packed']
(OUT/'model_validation.json').write_text(json.dumps(summary,indent=2))
bpy.ops.file.pack_all()
scene.render.filepath=str(OUT/'01_cutaway.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Core_Culture_Gym.blend'))
print('MODEL_SAVED',json.dumps(summary),flush=True)

if os.environ.get('GYM_RENDER','1')=='1':
    for s,filename in [(scene,'01_cutaway.png'),(plan_scene,'02_floor_plan.png'),(ext_scene,'03_entrance.png'),(int_scene,'04_free_weights.png'),(hyrox_scene,'05_hyrox_ceiling.png')]:
        bpy.context.window.scene=s
        s.render.filepath=str(OUT/filename)
        print('RENDER_START',filename,flush=True)
        bpy.ops.render.render(write_still=True)
        print('RENDER_DONE',filename,flush=True)
    bpy.context.window.scene=scene
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Core_Culture_Gym.blend'))
print('COMPLETE',flush=True)
