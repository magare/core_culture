"""Apply the PDF elevation details to the already revised gym floor plan.

Run in Blender with Core_Culture_Gym_Aesthetic.blend (or its 96 x 60 ft
layout-revised successor) loaded. This script edits the open blend in memory;
the caller decides where to save it. It deliberately leaves the ground plan,
room furnishings, and source .blend untouched.

The PDF states a 25 ft centre height and a 64 ft back training elevation. Its
side elevation draws 9 ft of lower wall plus 11 ft above, so 20 ft eaves are
inferred. Window sill ~5 ft, vent centre ~13 ft, fan centre ~16.9 ft and roof
steel offsets are inferred from the elevations, not explicit dimensions.
"""

import math

import bpy
from mathutils import Vector


FT = 0.3048
EAVE_FT = 20.0  # Inferred: side elevation has 9 + 11 ft wall bands.
RIDGE_FT = 25.0  # Explicit PDF centre height.
CENTRAL_LEFT_FT = 16.0
CENTRAL_RIGHT_FT = 80.0
WINDOW_SILL_FT = 5.0  # Inferred from the page-7 back elevation.
WINDOW_HEAD_FT = 9.5  # 4.5 ft stated window height.
VENT_CENTER_FT = 13.0  # Inferred from the page-7 vent band.
FAN_CENTER_FT = 16.9  # Inferred above the 14.5 ft yoga rack on page 8.

ROOF = bpy.data.collections['06 | Roof & steel structure • removable']
UPPER = bpy.data.collections['04 | Exterior walls • upper']
HVAC = bpy.data.collections['08 | Exposed silver HVAC']
PARTITIONS = bpy.data.collections['05 | Partitions • upper']
SIGNS = bpy.data.collections['22 | SUSPENDED AREA SIGNS • overhead']
EXTERIOR = bpy.data.scenes['03 | EXTERIOR • entrance']
original_scene = bpy.context.window.scene
bpy.context.window.scene = EXTERIOR
bpy.context.view_layer.update()


def mat(name):
    return bpy.data.materials[name]


METAL = mat('01 • anthracite powder-coated steel')
RIB = mat('02 • folded graphite cladding')
EDGE = mat('03 • blackened steel edges')
CHROME = mat('08 • satin stainless steel')
DUCT_MAT = mat('09 • galvanized spiral duct')
GLASS = mat('22 • tinted entrance glass')


def world_bounds_ft(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return ([min(p[i] for p in points) / FT for i in range(3)],
            [max(p[i] for p in points) / FT for i in range(3)])


def mesh_object(name, verts_ft, faces, material, collection):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata([tuple(v * FT for v in xyz) for xyz in verts_ft], [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box_geometry(verts, faces, x1, x2, y1, y2, z1, z2):
    base = len(verts)
    verts.extend([(x1,y1,z1),(x2,y1,z1),(x2,y2,z1),(x1,y2,z1),
                  (x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)])
    faces.extend([tuple(base+i for i in side) for side in
                  ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),
                   (2,3,7,6),(3,0,4,7))])


def box(name, bounds, material, collection):
    verts, faces = [], []
    box_geometry(verts, faces, *bounds)
    return mesh_object(name, verts, faces, material, collection)


def rod_geometry(verts, faces, a, b, radius, sides=8):
    va, vb = Vector(a), Vector(b)
    direction = vb-va
    if direction.length < 1e-6:
        return
    quat = direction.to_track_quat('Z', 'Y')
    base = len(verts)
    for end in (va, vb):
        for i in range(sides):
            theta = 2 * math.pi * i / sides
            p = end + quat @ Vector((radius*math.cos(theta),
                                     radius*math.sin(theta), 0))
            verts.append(tuple(p))
    faces.extend([tuple(base+i for i in range(sides-1,-1,-1)),
                  tuple(base+sides+i for i in range(sides))])
    for i in range(sides):
        j = (i+1) % sides
        faces.append((base+i,base+j,base+sides+j,base+sides+i))


def rod(name, a, b, radius, material, collection, sides=8):
    verts, faces = [], []
    rod_geometry(verts, faces, a, b, radius, sides)
    return mesh_object(name, verts, faces, material, collection)


def remove_prefixes(collection, prefixes):
    for obj in list(collection.all_objects):
        if obj.name.startswith(prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)


def roof_height(x):
    """Gable runs along y; pages 5 and 7 show its peak at the 64 ft midpoint."""
    if x < CENTRAL_LEFT_FT or x > CENTRAL_RIGHT_FT:
        return EAVE_FT
    half_span = (CENTRAL_RIGHT_FT-CENTRAL_LEFT_FT)/2
    ridge_x = (CENTRAL_LEFT_FT+CENTRAL_RIGHT_FT)/2
    return EAVE_FT + (RIDGE_FT-EAVE_FT) * (1-abs(x-ridge_x)/half_span)


# The preceding layout pass contracts the 100 ft shell to an inferred 96 ft.
# Take the present lower-wall endpoint so this script also works in isolation
# on the original 100 ft blend for inspection, without shrinking the plan.
south_base = bpy.data.objects['South exterior • base']
_, south_max = world_bounds_ft(south_base)
outer_width = round(south_max[0], 3)
assert outer_width >= CENTRAL_RIGHT_FT + 16.0 - 0.2, outer_width


# Raise the other three exterior wall tops. Every original upper wall is split
# at 3.3 ft. Moving only its 18 ft top vertices retains doors and wall bases.
for obj in bpy.data.objects:
    if any(obj.name.startswith(prefix) for prefix in
           ('North corrugated wall • upper',
            'North corrugated wall • cladding rib',
            'West corrugated wall • upper',
            'West corrugated wall • cladding rib',
            'Entrance / east facade • upper',
            'Entrance / east facade • lintel',
            'Entrance / east facade • cladding rib')) and obj.type == 'MESH':
        inv = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            world = obj.matrix_world @ vertex.co
            if abs(world.z / FT - 18.0) < 0.03:
                world.z = EAVE_FT * FT
                vertex.co = inv @ world
        obj.data.update()


# Page 7: four labelled 9 x 4.5 ft windows plus an unlabeled first opening
# drawn approximately 7 ft wide. The first opening starts at the 16 ft bay
# boundary, each clear gap is 4 ft and the remaining right margin is 5 ft.
remove_prefixes(UPPER, ('South exterior • upper', 'South exterior • cladding rib',
                        'PDF • south'))
windows = [(16.0,23.0),(27.0,36.0),(40.0,49.0),(53.0,62.0),(66.0,75.0)]
wall_verts, wall_faces = [], []
box_geometry(wall_verts, wall_faces, 0, outer_width, 0.035, 0.485, 3.3, WINDOW_SILL_FT)
box_geometry(wall_verts, wall_faces, 0, outer_width, 0.035, 0.485, WINDOW_HEAD_FT, EAVE_FT)
last = 0.0
for lo, hi in windows:
    if lo > last:
        box_geometry(wall_verts, wall_faces, last, lo, 0.035, 0.485,
                     WINDOW_SILL_FT, WINDOW_HEAD_FT)
    last = hi
if outer_width > last:
    box_geometry(wall_verts, wall_faces, last, outer_width, 0.035, 0.485,
                 WINDOW_SILL_FT, WINDOW_HEAD_FT)
wall = mesh_object('PDF • south exterior with five window openings',
                   wall_verts, wall_faces, RIB, UPPER)
wall['Source'] = 'Gym layout PDF page 7'
wall['Window sill elevation (ft)'] = WINDOW_SILL_FT
wall['Window head elevation (ft)'] = WINDOW_HEAD_FT
wall['First opening width'] = 'About 7 ft, inferred from drawing'

rib_verts, rib_faces = [], []
for i in range(int(outer_width / .9) + 1):
    x = .45 + i*.9
    if x >= outer_width:
        break
    in_window = any(lo < x < hi for lo, hi in windows)
    levels = [(3.4,WINDOW_SILL_FT),(WINDOW_HEAD_FT,EAVE_FT)] if in_window else [(3.4,EAVE_FT)]
    for z1,z2 in levels:
        if z2-z1 > .1:
            box_geometry(rib_verts,rib_faces,x-.038,x+.038,0.005,.515,z1,z2)
mesh_object('PDF • south cladding ribs around windows',rib_verts,rib_faces,METAL,UPPER)

for index,(lo,hi) in enumerate(windows,1):
    pane = box('PDF • back window %d'%index,
               (lo+.07,hi-.07,-.015,.055,WINDOW_SILL_FT+.07,WINDOW_HEAD_FT-.07),
               GLASS,UPPER)
    pane['Width (ft)'] = hi-lo
    pane['Height (ft)'] = 4.5
    if index == 1:
        pane['Width status'] = 'Inferred from drawing; unlabeled first opening'
    frame_verts,frame_faces = [],[]
    for b in ((lo-.06,lo+.06,-.07,.07,WINDOW_SILL_FT-.06,WINDOW_HEAD_FT+.06),
              (hi-.06,hi+.06,-.07,.07,WINDOW_SILL_FT-.06,WINDOW_HEAD_FT+.06),
              (lo,hi,-.07,.07,WINDOW_SILL_FT-.06,WINDOW_SILL_FT+.06),
              (lo,hi,-.07,.07,WINDOW_HEAD_FT-.06,WINDOW_HEAD_FT+.06)):
        box_geometry(frame_verts,frame_faces,*b)
    mesh_object('PDF • back window frame %d'%index,frame_verts,frame_faces,CHROME,UPPER)

# Five grey vent boxes as drawn on the upper band. Their widths and heights
# are visual estimates; only the five-box arrangement is explicit in the PDF.
for i, offset in enumerate((5.8,14.0,31.7,39.8,55.5),1):
    x = CENTRAL_LEFT_FT + offset
    vent = box('PDF • back AC vent %d'%i,
               (x-1.2,x+1.2,-.32,.015,VENT_CENTER_FT-.78,VENT_CENTER_FT+.78),
               CHROME,UPPER)
    vent['Elevation (ft)'] = 'Approx. 13 ft centre, inferred'
    box('PDF • back AC vent dark grille %d'%i,
        (x-1.0,x+1.0,-.35,-.32,VENT_CENTER_FT-.58,VENT_CENTER_FT+.58),
        EDGE,UPPER)


# Replace the original 18/21 ft pitched shell and optimized steel batches.
pendant_backing = next((o for o in ROOF.objects
                        if o.name.startswith('Vertical pendant dark backing')), None)
if pendant_backing:
    pendant_min,pendant_max = world_bounds_ft(pendant_backing)
    pendant_x = [pendant_min[0]+.065 + i*(pendant_max[0]-pendant_min[0]-.13)/3
                 for i in range(4)]
    pendant_y = [pendant_min[1]+.065, pendant_max[1]-.065]
else:
    pendant_x = [21,36,51,66]
    pendant_y = [16,37]
remove_prefixes(ROOF, ('Standing seam roof slope', 'Roof standing seam',
                       'Portal steel column', 'Steel truss chord',
                       'Triangular web bracing', 'Roof purlin',
                       'Enclosed corrugated gable', 'Gable vertical seam',
                       'Longitudinal ridge truss chord', 'Ridge truss diagonal',
                       'Ridge truss vertical', 'Pendant suspension wire',
                       'Duct hanger', 'PDF •'))
ridge_x=(CENTRAL_LEFT_FT+CENTRAL_RIGHT_FT)/2
for x1,x2,z1,z2 in ((-.5,CENTRAL_LEFT_FT,EAVE_FT,EAVE_FT),
                    (CENTRAL_LEFT_FT,ridge_x,EAVE_FT,RIDGE_FT),
                    (ridge_x,CENTRAL_RIGHT_FT,RIDGE_FT,EAVE_FT),
                    (CENTRAL_RIGHT_FT,outer_width+.5,EAVE_FT,EAVE_FT)):
    panel = mesh_object('PDF • 20–25 ft standing seam roof',
                        [(x1,-.3,z1),(x2,-.3,z2),
                         (x2,60.3,z2),(x1,60.3,z1)],
                        [(0,1,2,3)],RIB,ROOF)
    solid = panel.modifiers.new('Roof sheet thickness','SOLIDIFY')
    solid.thickness = .06 * FT

seam_verts,seam_faces = [],[]
for i in range(int(outer_width/.9)+1):
    x = .45+i*.9
    if x >= outer_width:
        break
    z=roof_height(x)+.03
    rod_geometry(seam_verts,seam_faces,(x,-.3,z),(x,60.3,z),.035,6)
mesh_object('PDF • roof standing seams',seam_verts,seam_faces,METAL,ROOF)

steel_verts,steel_faces = [],[]
for y in (.75,12,24,36,48,59.25):
    for x in (0,CENTRAL_LEFT_FT,CENTRAL_RIGHT_FT,outer_width):
        box_geometry(steel_verts,steel_faces,x-.24,x+.24,y-.24,y+.24,0,19.6)
    for a,b,r in (((CENTRAL_LEFT_FT,y,19.6),(ridge_x,y,24.4),.15),
                  ((ridge_x,y,24.4),(CENTRAL_RIGHT_FT,y,19.6),.15),
                  ((CENTRAL_LEFT_FT,y,18.5),(CENTRAL_RIGHT_FT,y,18.5),.15),
                  ((0,y,19.6),(CENTRAL_LEFT_FT,y,19.6),.13),
                  ((CENTRAL_RIGHT_FT,y,19.6),(outer_width,y,19.6),.13)):
        rod_geometry(steel_verts,steel_faces,a,b,r)
    for x in range(int(CENTRAL_LEFT_FT),int(CENTRAL_RIGHT_FT),6):
        next_x=min(x+6,CENTRAL_RIGHT_FT)
        middle=(x+next_x)/2
        z=roof_height(middle)-.4
        rod_geometry(steel_verts,steel_faces,(x,y,18.5),(middle,y,z),.075)
        rod_geometry(steel_verts,steel_faces,(middle,y,z),(next_x,y,18.5),.075)
mesh_object('PDF • portal columns and trusses',steel_verts,steel_faces,METAL,ROOF)

purlin_verts,purlin_faces = [],[]
for x in range(int(CENTRAL_LEFT_FT)+6,int(CENTRAL_RIGHT_FT),6):
    z=roof_height(x)-.3
    box_geometry(purlin_verts,purlin_faces,x-.09,x+.09,0,60,z-.14,z+.14)
mesh_object('PDF • roof purlins',purlin_verts,purlin_faces,METAL,ROOF)

gable_verts,gable_faces = [],[]
for y in (-.18,60.18):
    base=len(gable_verts)
    gable_verts.extend(((CENTRAL_LEFT_FT,y,EAVE_FT),
                        (CENTRAL_RIGHT_FT,y,EAVE_FT),(ridge_x,y,RIDGE_FT)))
    gable_faces.append((base,base+1,base+2))
gable=mesh_object('PDF • enclosed 20–25 ft gable ends',gable_verts,gable_faces,RIB,ROOF)
gable.modifiers.new('Gable sheet thickness','SOLIDIFY').thickness=.08*FT
gable_rib_verts,gable_rib_faces = [],[]
for y in (-.22,60.22):
    for x in range(int(CENTRAL_LEFT_FT)+1,int(CENTRAL_RIGHT_FT)):
        rise=roof_height(x)-EAVE_FT
        box_geometry(gable_rib_verts,gable_rib_faces,
                     x-.06,x+.06,y-.035,y+.035,EAVE_FT,EAVE_FT+rise)
mesh_object('PDF • gable vertical seams',gable_rib_verts,gable_rib_faces,METAL,ROOF)

ridge_verts,ridge_faces = [],[]
for z in (19.8,24.2):
    rod_geometry(ridge_verts,ridge_faces,(ridge_x,0,z),(ridge_x,60,z),.12)
for y in range(0,60,5):
    rod_geometry(ridge_verts,ridge_faces,(ridge_x,y,19.8),(ridge_x,y+5,24.2),.07)
    rod_geometry(ridge_verts,ridge_faces,(ridge_x,y,19.8),(ridge_x,y,24.2),.06)
mesh_object('PDF • longitudinal ridge truss',ridge_verts,ridge_faces,METAL,ROOF)

pendant_verts,pendant_faces = [],[]
for x in pendant_x:
    for y in pendant_y:
        rod_geometry(pendant_verts,pendant_faces,(x,y,15.6),
                     (x,y,roof_height(x)-.3),.013)
mesh_object('PDF • pendant suspension wires',pendant_verts,pendant_faces,EDGE,ROOF)


# Reattach the existing compact sign mounts to the new roof underside. Roots,
# panels, type and bottom clearances stay at their original elevations.
for root in (o for o in SIGNS.objects if o.name.startswith('HANGING SIGN •')):
    root_z = root.location.z / FT
    root_x = root.location.x / FT
    mount_z = roof_height(root_x)-.3
    relative = mount_z-root_z
    for child in (o for o in SIGNS.objects if o.parent == root):
        if child.name.startswith(('Overhead mounting rail', 'Roof clamp')):
            child.location.y = relative*FT
        elif child.name.startswith('Top suspension cable') and child.type == 'MESH':
            ys=[v.co.y/FT for v in child.data.vertices]
            lower=min(ys)
            old_upper=max(ys)
            new_upper=relative-.12+.027
            if old_upper > lower+.001:
                factor=(new_upper-lower)/(old_upper-lower)
                for v in child.data.vertices:
                    v.co.y = (lower+(v.co.y/FT-lower)*factor)*FT
                child.data.update()
    root['Mount elevation (ft)'] = round(mount_z,2)
    root['Roof height basis'] = '20 ft eaves inferred; 25 ft ridge specified'


# Main front duct: PDF page 5 specifies 4 ft diameter at the reception/right
# end and 2.5 ft at the cardio/left end. Axial length is the 64 ft training bay.
old_duct = next(o for o in HVAC.objects if o.name.startswith('Main AC duct'))
old_min,old_max=world_bounds_ft(old_duct)
duct_y=(old_min[1]+old_max[1])/2
duct_z=(old_min[2]+old_max[2])/2
old_radius=(old_max[2]-old_min[2])/2
grille_batch=next(o for o in HVAC.objects if o.name.startswith('AC grille collar'))
grille_min,grille_max=world_bounds_ft(grille_batch)
grille_x=[grille_min[0]+1.25+i*((grille_max[0]-grille_min[0]-2.5)/5)
          for i in range(6)]


def duct_radius(x):
    t=max(0,min(1,(x-CENTRAL_LEFT_FT)/(CENTRAL_RIGHT_FT-CENTRAL_LEFT_FT)))
    return 1.25+.75*t


remove_prefixes(HVAC, ('Main AC duct','Spiral duct seam','PDF • tapered'))
duct_verts,duct_faces=[],[]
segments=48
for x in (CENTRAL_LEFT_FT,CENTRAL_RIGHT_FT):
    r=duct_radius(x)
    for i in range(segments):
        a=2*math.pi*i/segments
        duct_verts.append((x,duct_y+r*math.cos(a),duct_z+r*math.sin(a)))
duct_faces.extend((tuple(range(segments-1,-1,-1)),
                   tuple(range(segments,2*segments))))
for i in range(segments):
    j=(i+1)%segments
    duct_faces.append((i,j,j+segments,i+segments))
duct=mesh_object('PDF • tapered main AC duct 2.5 to 4 ft',
                 duct_verts,duct_faces,DUCT_MAT,HVAC)
duct['Diameter (ft)'] = '2.5 cardio/left; 4 reception/right'
duct['Length (ft)'] = 64.0

seam_verts,seam_faces=[],[]
for x in range(int(CENTRAL_LEFT_FT)+2,int(CENTRAL_RIGHT_FT),2):
    r=duct_radius(x)+.022
    for i in range(segments):
        a=2*math.pi*i/segments
        y=duct_y+r*math.cos(a)
        z=duct_z+r*math.sin(a)
        b=2*math.pi*(i+1)/segments
        y2=duct_y+r*math.cos(b)
        z2=duct_z+r*math.sin(b)
        rod_geometry(seam_verts,seam_faces,(x,y,z),(x,y2,z2),.022,5)
mesh_object('PDF • tapered duct seams',seam_verts,seam_faces,CHROME,HVAC)

# Existing grilles were optimized into one mesh per component type. Move each
# vertex outward according to its x position, keeping six grille assemblies.
for obj in list(HVAC.objects):
    if obj.name.startswith('AC grille') and obj.type == 'MESH':
        inv=obj.matrix_world.inverted()
        for v in obj.data.vertices:
            world=obj.matrix_world @ v.co
            x=world.x/FT
            world.y -= (duct_radius(x)-old_radius)*FT
            v.co=inv @ world
        obj.data.update()

hanger_verts,hanger_faces=[],[]
for x in grille_x:
    rod_geometry(hanger_verts,hanger_faces,
                 (x,duct_y,duct_z+duct_radius(x)+.04),
                 (x,duct_y,roof_height(x)-.3),.035,10)
mesh_object('PDF • tapered duct hangers',hanger_verts,hanger_faces,CHROME,ROOF)


# Page 8 shows one dark exhaust fan above the red rack on the training-floor
# face of the cardio/changing-side partition. Its exact size and level are
# inferred from the side elevation; the partition backing is owned by the
# separate interior layout pass.
remove_prefixes(PARTITIONS, ('PDF • exhaust fan',))
fan_y=31.3
fan_x=CENTRAL_LEFT_FT+.42
fan=box('PDF • exhaust fan housing',
        (fan_x-.2,fan_x+.2,fan_y-1.35,fan_y+1.35,
         FAN_CENTER_FT-1.35,FAN_CENTER_FT+1.35),EDGE,PARTITIONS)
fan['Source'] = 'Gym layout PDF page 8'
fan['Centre elevation (ft)'] = 'Approx. 16.9, inferred'
box('PDF • exhaust fan face',
    (fan_x+.2,fan_x+.23,fan_y-1.12,fan_y+1.12,
     FAN_CENTER_FT-1.12,FAN_CENTER_FT+1.12),METAL,PARTITIONS)
ring_verts,ring_faces=[],[]
for i in range(32):
    a=2*math.pi*i/32
    b=2*math.pi*(i+1)/32
    rod_geometry(ring_verts,ring_faces,
                 (fan_x+.26,fan_y+math.cos(a),FAN_CENTER_FT+math.sin(a)),
                 (fan_x+.26,fan_y+math.cos(b),FAN_CENTER_FT+math.sin(b)),.04,6)
mesh_object('PDF • exhaust fan safety ring',ring_verts,ring_faces,CHROME,PARTITIONS)
blade_verts,blade_faces=[],[]
for i in range(4):
    a=math.pi*i/2+math.pi/7
    dy,dz=math.cos(a),math.sin(a)
    py,pz=-dz,dy
    blade_verts.extend(((fan_x+.27,fan_y+dy*.18+py*.08,FAN_CENTER_FT+dz*.18+pz*.08),
                        (fan_x+.27,fan_y+dy*.85+py*.19,FAN_CENTER_FT+dz*.85+pz*.19),
                        (fan_x+.27,fan_y+dy*.85-py*.19,FAN_CENTER_FT+dz*.85-pz*.19)))
    b=3*i
    blade_faces.append((b,b+1,b+2))
mesh_object('PDF • exhaust fan blades',blade_verts,blade_faces,CHROME,PARTITIONS)
rod('PDF • exhaust fan hub',(fan_x+.23,fan_y,FAN_CENTER_FT),
    (fan_x+.31,fan_y,FAN_CENTER_FT),.17,CHROME,PARTITIONS,16)


for scene in bpy.data.scenes:
    scene['PDF shell revision'] = '25 ft centre; 20 ft inferred eaves; five back windows and vents; tapered 64 ft front duct'
    scene['Height assumption'] = '25 ft centre per PDF; 20 ft eaves inferred from 9 + 11 ft side elevation.'
    scene['Elevation limits'] = 'Back first window width, sill, vents and exhaust fan position estimated from drawing.'

bpy.context.window.scene=original_scene
print('PDF_LAYOUT_SHELL_APPLIED',
      {'outer_width_ft':outer_width,'central_back_ft':[CENTRAL_LEFT_FT,CENTRAL_RIGHT_FT],
       'eaves_ft':EAVE_FT,'ridge_ft':RIDGE_FT,'windows':windows,
       'duct_diameter_ft':[2.5,4.0]},flush=True)
