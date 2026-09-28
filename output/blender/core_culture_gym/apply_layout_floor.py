"""Apply the gym drawing's floor, front wall, rooms, and door schedule.

Run inside Blender after the overall x-axis has been corrected to a 96 x 60 ft
shell. This script edits the open file only; saving and export are the caller's
responsibility. Positions not dimensioned in the supplied drawing (notably the
turf's y position and individual door offsets) follow its drawn proportions.
"""

import math
import bpy
from mathutils import Vector


FT = 0.3048
CUT = bpy.data.scenes['01 | CUTAWAY • furnished plan']
assert not CUT.get('Drawing floor revision applied'), 'Drawing floor revision already applied'


def collection(prefix):
    matches = [c for c in bpy.data.collections if c.name.startswith(prefix)]
    assert len(matches) == 1, (prefix, [c.name for c in matches])
    return matches[0]


LOWER = collection('02 | Walls')
UPPER = collection('05 | Partitions')
WEIGHTS = collection('10 | Weight training')
HYROX = collection('11 | HYROX')
DOORS = collection('16 | Doors')
BRAND_FLOOR = collection('BRAND • official logo • HYROX')
MAT_WALL = bpy.data.materials['12 • warm neutral partition plaster']
MAT_CONCRETE = bpy.data.materials['11 • warm polished concrete']
MAT_EDGE = bpy.data.materials['03 • blackened steel edges']
MAT_CHROME = bpy.data.materials['08 • satin stainless steel']
MAT_GLASS = bpy.data.materials['22 • tinted entrance glass']
MAT_OAK = bpy.data.materials['14 • natural smoked oak']
MAT_CYAN = bpy.data.materials['17 • washroom blue-grey']
MAT_PURPLE = bpy.data.materials['18 • washroom warm mauve']
MAT_TURF = bpy.data.materials['05 • deep olive performance turf']


def matte_material(name, rgba):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*rgba, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgba, 1)
    shader.inputs['Roughness'].default_value = 0.76
    return mat


MAT_GREY = matte_material('LAYOUT • matte grey wall panel', (.37, .39, .39))
MAT_RED = matte_material('LAYOUT • red storage rack', (.63, .035, .018))


def box(name, loc_ft, size_ft, mat, col, bevel_ft=0):
    x, y, z = (v * FT / 2 for v in size_ft)
    verts = [(-x, -y, -z), (-x, -y, z), (-x, y, -z), (-x, y, z),
             (x, -y, -z), (x, -y, z), (x, y, -z), (x, y, z)]
    faces = [(2, 6, 4, 0), (5, 7, 3, 1), (4, 5, 1, 0),
             (3, 7, 6, 2), (1, 3, 2, 0), (6, 7, 5, 4)]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = Vector(loc_ft) * FT
    if bevel_ft:
        bevel = obj.modifiers.new('Edge radius', 'BEVEL')
        bevel.width = bevel_ft * FT
        bevel.segments = 2
    return obj


def remove_objects(objects):
    for obj in list(objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_named(*prefixes):
    remove_objects(o for o in bpy.data.objects if o.name.startswith(prefixes))


def wall_segment(name, axis, fixed, lo, hi, height=10):
    if hi <= lo:
        return
    mid = (lo + hi) / 2
    center = (mid, fixed) if axis == 'X' else (fixed, mid)
    dims = (hi - lo, .45) if axis == 'X' else (.45, hi - lo)
    skirting = (hi - lo, .53, .42) if axis == 'X' else (.53, hi - lo, .42)
    box(name + ' • base', (*center, 1.65), (*dims, 3.3), MAT_WALL, LOWER)
    box(name + ' • upper', (*center, (3.3 + height) / 2),
        (*dims, height - 3.3), MAT_WALL, UPPER)
    box(name + ' • skirting', (*center, .3), skirting, MAT_EDGE, LOWER)


def wall_with_openings(name, axis, fixed, start, end, gaps, height=10):
    cursor = start
    for lo, hi, door_height in gaps:
        assert start <= lo < hi <= end and lo >= cursor
        wall_segment(name, axis, fixed, cursor, lo, height)
        mid = (lo + hi) / 2
        center = (mid, fixed) if axis == 'X' else (fixed, mid)
        dims = (hi - lo, .45) if axis == 'X' else (.45, hi - lo)
        box(name + ' • lintel', (*center, (door_height + height) / 2),
            (*dims, height - door_height), MAT_WALL, UPPER)
        cursor = hi
    wall_segment(name, axis, fixed, cursor, end, height)


def door(name, axis, fixed, lo, hi, height, angle_degrees, leaf_material):
    """A modeled leaf and frame within a drawing-sized rough opening."""
    width = hi - lo
    hinge = (fixed, lo + .1, 0) if axis == 'Y' else (lo + .1, fixed, 0)
    root = bpy.data.objects.new('Door pivot • ' + name, None)
    DOORS.objects.link(root)
    root.location = Vector(hinge) * FT
    root.rotation_euler.z = math.radians(angle_degrees)
    root.empty_display_size = .12 * FT
    root['Rough width (ft)'] = width
    root['Rough height (ft)'] = height
    root['Drawing reference'] = 'Gym layout PDF, pages 2, 6, 8'
    leaf_width = width - .18
    leaf = box(name + ' door leaf', (leaf_width / 2, 0, height / 2),
               (leaf_width, .12, height - .14), leaf_material, DOORS, .02)
    leaf.parent = root
    # Keep the frame flush with the opening: its stated size is the rough size.
    for side in (lo + .05, hi - .05):
        at = (fixed, side, height / 2) if axis == 'Y' else (side, fixed, height / 2)
        size = (.5, .1, height) if axis == 'Y' else (.1, .5, height)
        box(name + ' door jamb', at, size, MAT_EDGE, DOORS)
    mid = (lo + hi) / 2
    at = (fixed, mid, height - .05) if axis == 'Y' else (mid, fixed, height - .05)
    size = (.5, width, .1) if axis == 'Y' else (width, .5, .1)
    box(name + ' door head', at, size, MAT_EDGE, DOORS)
    for side in (-1, 1):
        grip = box(name + ' handle', (leaf_width - .4, side * .11, 3.6),
                   (.08, .08, .5), MAT_CHROME, DOORS)
        grip.parent = root


# The PDF's circle is an AC-vent cross-section in the side elevation. Remove
# floor graphics and the dimension callouts that treated it as a floor feature.
remove_named('Central 16 ft functional circle', 'Central circle •',
             'Central monogram', 'Central circle lettering',
             'Core clear chain', 'North 18 ft chain', 'South 18 ft chain')
remove_objects(o for o in BRAND_FLOOR.objects if 'central training floor' in o.name.lower())

# Page 4 depicts one narrow, unmarked turf strip. Its 50 x 6.5 ft size and
# x=26..76, y=15..21.5 placement are inferred by comparing drawn proportions
# against the 64 ft main bay. The PDF does not provide a turf dimension.
remove_named('HYROX performance turf', 'HYROX lane boundary',
             'HYROX start / finish', 'Lane 01', 'Lane 02',
             'Lane distance hash', 'Weighted push sled • lane')
remove_objects(o for o in BRAND_FLOOR.objects if 'HYROX lane' in o.name)
turf = box('LAYOUT • single performance turf', (51, 18.25, .1),
           (50, 6.5, .15), MAT_TURF, HYROX, .03)
turf['Inferred plan bounds (ft)'] = [26, 76, 15, 21.5]
turf['Dimension confidence'] = 'Approximate from PDF page 4 proportions'
for sign_name in ('HANGING SIGN • HYROX', 'PLAN LABEL • HYROX'):
    sign = bpy.data.objects.get(sign_name)
    if sign:
        sign.location.x = 51 * FT
        sign.location.y = 18.25 * FT

# The source drawing has no equipment schedule. The first SkiErg currently
# stands in the stair footprint at x≈17..20, y≈5..14; remove that instance.
# Keep the other conceptual training assets where they do not block circulation.
for obj in list(HYROX.objects):
    if obj.name.startswith('HYROX SkiErg') and obj.location.y / FT < 15:
        bpy.data.objects.remove(obj, do_unlink=True)
    elif obj.name.startswith('HYROX rowing ergometer') and 15 <= obj.location.y / FT <= 21.5:
        obj.location.y = 26.5 * FT
        obj['Layout status'] = 'Moved off the single turf strip; conceptual machine position'

# Page 5: 12 ft grey / 4 ft red rack / 32 ft grey / 4 ft red rack /
# 12 ft grey. Grey panels are 8 ft high; rack height is 7.5 ft.
remove_named('Free-weight mirror panel', 'Mirror vertical mullion',
             'Mirror bottom protective rail', 'Two-tier dumbbell rack •')
for lo, hi in [(16, 28), (32, 64), (68, 80)]:
    panel = box('LAYOUT • grey free-weight panel', ((lo + hi) / 2, 59.37, 4),
                (hi - lo, .10, 8), MAT_GREY, WEIGHTS)
    panel['Drawing span (ft)'] = [lo, hi]

for lo, hi in [(28, 32), (64, 68)]:
    cx = (lo + hi) / 2
    rack_parts = []
    for side in (-1, 1):
        rack_parts.append(box('LAYOUT • red rack upright',
                              (cx + side * 1.9, 58.58, 3.75),
                              (.2, 1.3, 7.5), MAT_RED, WEIGHTS))
    # Bottom cubby is 3 ft high; three 1.5 ft shelves fill to 7.5 ft.
    for z in (3, 4.5, 6, 7.44):
        rack_parts.append(box('LAYOUT • red rack shelf',
                              (cx, 58.58, z), (3.8, 1.3, .12), MAT_RED, WEIGHTS))
    for side in (-1, 1):
        rack_parts.append(box('LAYOUT • red lower cabinet front',
                              (cx + side * .95, 57.9, 1.45),
                              (1.86, .08, 2.9), MAT_RED, WEIGHTS))
    for obj in rack_parts:
        obj['Rack drawing bounds (ft)'] = [lo, hi, 0, 7.5]

# Pages 2, 6 and 8 give the room partitions and interior door schedule.
# y offsets are placed within their drawn bays because no plan coordinate is
# written for the individual doors. Support room widths are gross dimensions.
remove_named('Support room front', 'Support room partition A',
             'Support room partition B', 'Cardio & washroom partition',
             'East circulation partition')
wall_with_openings('Cardio & changing partition', 'Y', 15.735, 0, 60,
                   [(.55, 4.05, 8), (15.5, 19, 8), (30.5, 33.5, 9)])
wall_with_openings('Studio & reception partition', 'Y', 80.265, 0, 60,
                   [(.55, 3.55, 8), (40.5, 43.5, 9), (44, 47, 9)])
wall_with_openings('Support room front', 'X', 40, 80, 96,
                   [(81.2, 83.8, 8), (86.2, 88.8, 8), (91.7, 94.3, 8)])
wall_segment('Support room partition A', 'Y', 85, 32, 40)
wall_segment('Support room partition B', 'Y', 90, 32, 40)

door_names = ('Women', 'Men', 'Cardio', 'Group studio', 'Reception access', 'Support ')
old_pivot_names = tuple('Door pivot • ' + name for name in door_names)
remove_objects(o for o in DOORS.objects
               if o.name.startswith(door_names)
               or o.name.startswith(old_pivot_names))
door('Women changing', 'Y', 15.735, .55, 4.05, 8, 60, MAT_PURPLE)
door('Men changing', 'Y', 15.735, 15.5, 19, 8, 60, MAT_CYAN)
door('Cardio', 'Y', 15.735, 30.5, 33.5, 9, 60, MAT_GLASS)
door('Dance studio', 'Y', 80.265, .55, 3.55, 8, 30, MAT_OAK)
door('Reception 1', 'Y', 80.265, 40.5, 43.5, 9, 30, MAT_GLASS)
door('Reception 2', 'Y', 80.265, 44, 47, 9, 30, MAT_GLASS)
for index, (lo, hi) in enumerate([(81.2, 83.8), (86.2, 88.8),
                                  (91.7, 94.3)], 1):
    door('Support ' + str(index), 'X', 40, lo, hi, 8, -65, MAT_OAK)

# Model labels previously called the specified changing rooms washrooms.
for obj in bpy.data.objects:
    if obj.type != 'FONT':
        continue
    if obj.name == 'Floor label • MEN':
        obj.data.body = "MEN'S CHANGING"
        obj.data.size *= .72
    elif obj.name == 'Floor label • WOMEN':
        obj.data.body = "WOMEN'S CHANGING"
        obj.data.size *= .68
    elif obj.name.startswith(('Plan title • men', 'Suspended title • men',
                               'Suspended reverse title • men')):
        obj.data.body = "MEN'S CHANGING ROOM"
        obj.data.size *= .78
    elif obj.name.startswith(('Plan title • women', 'Suspended title • women',
                               'Suspended reverse title • women')):
        obj.data.body = "WOMEN'S CHANGING ROOM"
        obj.data.size *= .74
    elif obj.name == 'Floor label • HYROX':
        obj.data.body = 'TRAINING TURF'
        obj.data.size *= .8
        obj.location.x = 51 * FT
        obj.location.y = 22.7 * FT
    elif obj.name.startswith(('Plan title • hyrox', 'Suspended title • hyrox',
                               'Suspended reverse title • hyrox')):
        # Keep the ten sign assemblies for the website label toggle; only the
        # visible title changes to reflect the single, unmarked turf strip.
        obj.data.body = 'TRAINING TURF'
        obj.data.size *= .83

for scene in bpy.data.scenes:
    scene['Drawing floor revision applied'] = True
    scene['Turf position'] = 'Approximate 50 x 6.5 ft, x26..76 y15..21.5, PDF page 4'
    scene['Front wall sequence'] = '12 grey + 4 red rack + 32 grey + 4 red rack + 12 grey ft, PDF page 5'
    scene['Door schedule'] = 'PDF pages 6 and 8: reception 2x 3x9; studio 3x8; cardio 3x9; changing 2x 3.5x8 ft'

print('DRAWING FLOOR REVISION APPLIED',
      'single turf 50x6.5 ft; two red 4x7.5 ft racks; rooms 5/5/6x8 ft;'
      'drawing-sized interior doors; central floor circle removed', flush=True)
