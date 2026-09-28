"""Add the PDF page-8 side elevation to an open, corrected Core Culture .blend.

Run after the 96 x 60 ft layout correction. Coordinates are in feet and stored
in Blender metres. This script adds shared geometry but does not save the .blend.

The PDF gives the stair rises, its approximate rear-wall offset, the mirror and
rack sizes, and the office elevation width/height. Stair run, office depth,
walkway alignment, rail details and structure are reasonable inferences.
"""

import math

import bpy
from mathutils import Vector


FT = 0.3048
COLLECTION_NAME = '17 | PDF layout • stair and elevated office'
if bpy.data.collections.get(COLLECTION_NAME):
    raise RuntimeError('Page-8 stair and office collection already exists')

col = bpy.data.collections.new(COLLECTION_NAME)
col['source'] = 'Gym layout .pdf, page 8, right-side elevation'
col['drawing_dimensions'] = (
    'stair rises 6.5 ft and 4 ft; offset about 13 ft from window wall; '
    'mirror 29 x 8 ft; rack 6 x 4.5 ft in 1.5-ft sections; '
    'office 16 x 8.5 ft in elevation'
)
col['inferred_geometry'] = (
    'office depth 8 ft; platform top 10.5 ft; stair run/tread dimensions, '
    'catwalk path, supports, frame and furniture are inferred'
)
for scene in bpy.data.scenes:
    if scene.collection.children.get(col.name) is None:
        scene.collection.children.link(col)


def material(name):
    result = bpy.data.materials.get(name)
    if result is None:
        raise RuntimeError('Required base material missing: ' + name)
    return result


steel = material('01 • anthracite powder-coated steel')
edge = material('03 • blackened steel edges')
white = material('07 • warm white enamel')
chrome = material('08 • satin stainless steel')
pad = material('10 • black equipment upholstery')
concrete = material('11 • warm polished concrete')
wall = material('12 • warm neutral partition plaster')
oak = material('14 • natural smoked oak')
mirror = material('15 • mirror panels')
glass = material('22 • tinted entrance glass')

red = bpy.data.materials.get('LAYOUT • red yoga rack')
if red is None:
    red = bpy.data.materials.new('LAYOUT • red yoga rack')
    red.diffuse_color = (0.48, 0.035, 0.03, 1)
    red.use_nodes = True
    bsdf = red.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = red.diffuse_color
    bsdf.inputs['Roughness'].default_value = 0.53


def label(obj, note='', dimension=''):
    obj['source'] = 'Gym layout .pdf page 8'
    obj['placement'] = 'inferred from side elevation; verify on site'
    if note:
        obj['note'] = note
    if dimension:
        obj['drawing_dimension_ft'] = dimension
    return obj


def box(name, center, size, mat, *, bevel=0.0, note='', dimension=''):
    hx, hy, hz = [value * FT / 2 for value in size]
    verts = [
        (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, -hz), (-hx, hy, hz),
        (hx, -hy, -hz), (hx, -hy, hz), (hx, hy, -hz), (hx, hy, hz),
    ]
    faces = [
        (0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4),
        (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6),
    ]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(center) * FT
    col.objects.link(obj)
    if bevel:
        modifier = obj.modifiers.new('Soft fabricated edge', 'BEVEL')
        modifier.width = bevel * FT
        modifier.segments = 2
    return label(obj, note, dimension)


def rail(name, points, radius=0.055, mat=chrome, *, note=''):
    curve = bpy.data.curves.new(name + ' path', 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius * FT
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for control, point in zip(spline.points, points):
        control.co = (*(value * FT for value in point), 1)
    curve.materials.append(mat)
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    return label(obj, note)


def cylinder(name, a, b, radius, mat, *, sides=16, note=''):
    a = Vector(a) * FT
    b = Vector(b) * FT
    axis = (b - a).normalized()
    radial_u = axis.cross(Vector((0, 0, 1)) if abs(axis.z) < .9 else Vector((0, 1, 0))).normalized()
    radial_v = axis.cross(radial_u).normalized()
    radius *= FT
    verts = []
    for center in (a, b):
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            verts.append(tuple(center + radius * (radial_u * math.cos(angle) + radial_v * math.sin(angle))))
    faces = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
    faces += [(i, (i + 1) % sides, (i + 1) % sides + sides, i + sides)
              for i in range(sides)]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return label(obj, note)


# The elevated 29 x 8 ft mirror faces the central training room from the
# changing-room wall. The slim opaque back helps it read as a real wall finish.
box('PDF mirror • continuous back', (16.31, 14.5, 14.6), (.10, 29, 8.05), edge,
    dimension='29 x 8 mirror')
for i in range(5):
    y = (i + .5) * (29 / 5)
    box('PDF mirror • panel %02d' % (i + 1), (16.385, y, 14.6),
        (.055, 29 / 5 - .045, 8), mirror, bevel=.008,
        dimension='total 29 x 8 mirror')
    if i:
        box('PDF mirror • vertical joint %02d' % i,
            (16.43, i * (29 / 5), 14.6), (.045, .035, 8.05), chrome)
box('PDF mirror • lower guard', (16.44, 14.5, 10.63), (.08, 29, .11), chrome)
box('PDF mirror • upper trim', (16.44, 14.5, 18.62), (.08, 29, .10), chrome)


# Three 1.5-ft high compartments, spanning 6 ft along the wall. The rack is
# above the cardio doorway, as drawn, so the door and circulation stay open.
rack_y = 32.0
for y in (29.06, 34.94):
    box('PDF yoga rack • side frame', (17.22, y, 12.25),
        (1.65, .12, 4.5), red, bevel=.018, dimension='6 x 4.5 rack')
for z in (10.02, 11.52, 13.02, 14.48):
    box('PDF yoga rack • shelf', (17.22, rack_y, z),
        (1.65, 6, .12), red, bevel=.018, dimension='1.5-ft sections')
box('PDF yoga rack • rear', (16.43, rack_y, 12.25),
    (.10, 6, 4.5), red, dimension='6 x 4.5 rack')
for level in range(3):
    for index in range(5):
        y = 29.58 + index * 1.20
        z = 10.75 + level * 1.5
        cylinder('PDF yoga rack • rolled mat', (16.75, y, z),
                 (17.79, y, z), .26, pad, sides=14)

# The exhaust fan itself is supplied by the shell/elevation pass. This backing
# stops at 19 ft, leaving a foot beneath the corrected 20-ft side-bay roof.
box('PDF exhaust fan • upper backing', (16.24, 32, 16.72),
    (.18, 6, 4.55), wall, dimension='fan above rack; backing inferred')
box('PDF exhaust fan • backing border', (16.36, 32, 16.72),
    (.035, 6.08, 4.63), steel)


# First stair flight: 6.5 ft rise. Eleven approximately 7.1-inch risers keep
# its foot at the indicated ~13-ft offset and its head outside the y<4 passage.
first_steps = 11
first_rise = 6.5 / first_steps
first_run = .82
first_y0 = 13.35
stair_x = 18.65
stair_width = 3.25
for i in range(first_steps):
    y = first_y0 - (i + .5) * first_run
    top = (i + 1) * first_rise
    box('PDF stair • lower flight tread %02d' % (i + 1),
        (stair_x, y, top - .085),
        (stair_width, first_run + .025, .17), oak, bevel=.018,
        dimension='6.5-ft first flight rise')
    box('PDF stair • lower flight riser %02d' % (i + 1),
        (stair_x, y + first_run / 2 - .045, top - first_rise / 2),
        (stair_width, .09, first_rise), steel)
for x in (stair_x - stair_width / 2 - .09,
          stair_x + stair_width / 2 + .09):
    rail('PDF stair • first steel stringer',
         [(x, first_y0 + .1, .08), (x, first_y0 - first_steps * first_run, 6.42)],
         .14, steel)
    for i in (0, 3, 6, 9, 10):
        y = first_y0 - (i + .5) * first_run
        top = (i + 1) * first_rise
        rail('PDF stair • first baluster', [(x, y, top), (x, y, top + 3.0)],
             .045, steel)
    rail('PDF stair • first handrail',
         [(x, first_y0 - .35, 3.55),
          (x, first_y0 - first_steps * first_run + .3, 9.5)], .065)
box('PDF stair • 6.5-ft turn landing', (18.65, 5.8, 6.37),
    (3.35, 3.6, .26), concrete, bevel=.035,
    dimension='landing at 6.5-ft first-flight rise')
rail('PDF stair • turn landing rear guard',
     [(16.93, 4.02, 9.5), (20.24, 4.02, 9.5)], .065)
rail('PDF stair • turn landing side guard',
     [(16.93, 4.02, 9.5), (16.93, 7.58, 9.5)], .065)


# The 90-degree right turn climbs a further 4 ft toward the gym side. Its
# second landing joins an elevated route leading back to the office.
second_steps = 7
second_rise = 4 / second_steps
second_run = .82
second_x0 = 20.27
second_y = 5.96
for i in range(second_steps):
    x = second_x0 + (i + .5) * second_run
    top = 6.5 + (i + 1) * second_rise
    box('PDF stair • upper flight tread %02d' % (i + 1),
        (x, second_y, top - .085),
        (second_run + .025, 3.25, .17), oak, bevel=.018,
        dimension='4-ft second-flight rise')
    box('PDF stair • upper flight riser %02d' % (i + 1),
        (x - second_run / 2 + .045, second_y, top - second_rise / 2),
        (.09, 3.25, second_rise), steel)
for y in (second_y - 1.73, second_y + 1.73):
    rail('PDF stair • second steel stringer',
         [(second_x0, y, 6.45),
          (second_x0 + second_steps * second_run, y, 10.43)], .14, steel)
    for i in (0, 2, 4, 6):
        x = second_x0 + (i + .5) * second_run
        top = 6.5 + (i + 1) * second_rise
        rail('PDF stair • second baluster', [(x, y, top), (x, y, top + 3)],
             .045, steel)
    rail('PDF stair • second handrail',
         [(second_x0 + .3, y, 10.05),
          (second_x0 + second_steps * second_run - .2, y, 13.5)], .065)
box('PDF stair • 10.5-ft upper landing', (26.7, 5.96, 10.36),
    (2.25, 3.4, .28), concrete, bevel=.035,
    dimension='total rise 10.5 ft')
rail('PDF stair • upper landing rear guard',
     [(25.65, 4.20, 13.5), (27.8, 4.20, 13.5)], .065)
rail('PDF stair • upper landing end guard',
     [(27.8, 4.2, 13.5), (27.8, 7.7, 13.5)], .065)


# A dogleg walkway keeps the four-foot rear passage clear. The return bridge
# crosses the foot of the stair high enough to preserve ground-level clearance.
walk_top = 10.5
box('PDF elevated walk • landing return', (26.7, 9.65, 10.36),
    (2.8, 6.3, .28), concrete, bevel=.025)
box('PDF elevated walk • cross bridge', (20.85, 12.5, 10.36),
    (12.9, 3.0, .28), concrete, bevel=.025)
box('PDF elevated walk • side-bay catwalk', (14.82, 28.55, 10.36),
    (2.65, 31.1, .28), concrete, bevel=.025)
for y in (15.0, 22.0, 29.0, 36.0, 42.0):
    rail('PDF elevated walk • wall bracket',
         [(16.04, y, 8.4), (13.58, y, 10.30)], .11, steel)
    box('PDF elevated walk • wall ledger', (15.98, y, 9.15),
        (.16, .32, 2.0), steel)
for y in (14.0, 20.0, 26.0, 32.0, 38.0, 43.0):
    rail('PDF elevated walk • catwalk baluster',
         [(13.43, y, walk_top), (13.43, y, 13.5)], .052, steel)
rail('PDF elevated walk • catwalk handrail',
     [(13.43, 13.0, 13.5), (13.43, 44.1, 13.5)], .065)
for x in (15.2, 19.0, 23.0):
    rail('PDF elevated walk • cross-bridge north baluster',
         [(x, 11.0, walk_top), (x, 11.0, 13.5)], .05, steel)
for x in (19.0, 23.0, 27.2):
    rail('PDF elevated walk • cross-bridge south baluster',
         [(x, 14.0, walk_top), (x, 14.0, 13.5)], .05, steel)
rail('PDF elevated walk • bridge guard beside return',
     [(14.4, 11.0, 13.5), (25.2, 11.0, 13.5)], .065)
rail('PDF elevated walk • bridge guard beside catwalk',
     [(16.4, 14.0, 13.5), (27.3, 14.0, 13.5)], .065)
for y in (7.75, 12.7):
    rail('PDF elevated walk • return end baluster',
         [(27.84, y, walk_top), (27.84, y, 13.5)], .05, steel)
rail('PDF elevated walk • return handrail',
     [(27.84, 7.5, 13.5), (27.84, 12.8, 13.5)], .065)


# Office: 16 ft along the side elevation, 8.5 ft clear height above the 10.5-ft
# platform. Eight-foot depth is inferred because the PDF does not give it.
office_x = 12.0
office_y = 52.0
box('PDF office • elevated 16-ft floor',
    (office_x, office_y, 10.32), (8, 16, .36), concrete, bevel=.035,
    dimension='16-ft elevation width; 8.5-ft height')
for x in (8.22, 15.62):
    for y in (44.45, 59.25):
        box('PDF office • platform column', (x, y, 5.12),
            (.28, .28, 10.24), steel, bevel=.012)
for y in (44.15, 59.85):
    box('PDF office • floor edge beam', (office_x, y, 9.98),
        (8.2, .22, .5), steel)
box('PDF office • west wall', (8.06, 52, 14.78),
    (.16, 16, 8.4), wall)
box('PDF office • 20-ft roof clearance cap', (12, 52, 19.05),
    (8, 16, .16), steel,
    note='Upper face 19.13 ft, below the inferred 20-ft side-bay roof')

# South office wall leaves a glazed door reached by the catwalk.
box('PDF office • entry partition', (10.65, 44.06, 14.8),
    (5.3, .15, 8.4), wall)
box('PDF office • catwalk door', (14.65, 44.06, 14.65),
    (2.7, .08, 7.7), glass, bevel=.018)
for x in (13.25, 16.05):
    box('PDF office • door jamb', (x, 44.0, 14.8),
        (.10, .16, 8.4), steel)
box('PDF office • door header', (14.65, 44.0, 18.9),
    (2.8, .16, .16), steel)
cylinder('PDF office • door pull', (15.55, 43.92, 14.2),
         (15.55, 43.92, 15.6), .045, chrome)

# The gym-facing wall is glazed to make the upper office legible in cutaway and
# website views; the existing glass material is exported as translucent.
for i in range(4):
    y = 46 + i * 4
    box('PDF office • gym-facing glass %02d' % (i + 1),
        (16.14, y, 15.0), (.075, 3.9, 7.8), glass,
        dimension='office 16 x 8.5 in elevation')
    box('PDF office • glass mullion %02d' % (i + 1),
        (16.19, 44 + i * 4, 15.0), (.10, .10, 8.0), steel)
box('PDF office • glass mullion end', (16.19, 60, 15.0),
    (.10, .10, 8.0), steel)
for z in (11.02, 18.96):
    box('PDF office • glass transom', (16.2, 52, z),
        (.11, 16, .11), steel)

# A compact visible fit-out identifies the elevated volume as an office.
box('PDF office • work desk', (11.35, 53.2, 13.15),
    (4.9, 2.15, .2), oak, bevel=.045)
for x in (9.3, 13.4):
    for y in (52.35, 54.05):
        box('PDF office • desk leg', (x, y, 11.8),
            (.13, .13, 2.6), steel)
box('PDF office • chair seat', (11.3, 55.8, 12.45),
    (1.6, 1.5, .18), pad, bevel=.09)
box('PDF office • chair back', (11.3, 56.52, 13.13),
    (1.6, .18, 1.45), pad, bevel=.08)
cylinder('PDF office • chair stem', (11.3, 55.8, 10.58),
         (11.3, 55.8, 12.38), .10, steel)
box('PDF office • low storage', (9.0, 47.5, 12.0),
    (1.4, 4.6, 2.8), oak, bevel=.035)

guide_name = 'PDF PAGE 8 • STAIR AND OFFICE PLACEMENT'
guide = bpy.data.texts.get(guide_name) or bpy.data.texts.new(guide_name)
guide.clear()
guide.write(
    'Source: Gym layout .pdf page 8, right-side elevation.\n'
    'Direct dimensions: mirror 29 x 8 ft; yoga rack 6 x 4.5 ft with three '
    '1.5-ft sections; office 16 x 8.5 ft in elevation; stairs rise 6.5 ft '
    'then turn right and rise 4 ft; foot near 13 ft from rear window wall.\n'
    'Inferred for a complete 3D volume: office depth 8 ft, platform height '
    '10.5 ft, stair tread/run and landing sizes, elevated catwalk route, '
    'structural brackets and supports, glazing, furniture, material colours.\n'
    'The 4-ft rear passage at y0..4 and changing/cardio doors remain clear '
    'at ground level. The separate shell pass supplies the exhaust fan.\n'
)

print('Added PDF page-8 stair, walkway, mirror, rack and elevated office:',
      len(col.objects), 'objects in', COLLECTION_NAME)
