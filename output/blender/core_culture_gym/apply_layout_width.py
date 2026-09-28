"""Adjust the saved concept's undimensioned left bay to the supplied PDF.

The PDF dimensions the central training floor at 64 ft and the reception bay
at 16 ft. Its plan draws the cardio/changing bay the same width as reception,
so this revision infers a 16 ft left bay and a 96 x 60 ft overall outline.

Run in Blender after loading Core_Culture_Gym_Aesthetic.blend. The caller is
responsible for saving a new file; this script does not overwrite its source.
"""
import bpy
from mathutils import Vector

FT = 0.3048
OLD_LEFT = 20.0
NEW_LEFT = 16.0
SHIFT = OLD_LEFT - NEW_LEFT


def map_x_m(x_m):
    x_ft = x_m / FT
    return (x_ft * NEW_LEFT / OLD_LEFT if x_ft <= OLD_LEFT else x_ft - SHIFT) * FT


if bpy.data.scenes['01 | CUTAWAY • furnished plan'].get('PDF layout width applied'):
    raise RuntimeError('PDF layout width correction has already been applied')

# Equipment is placed through collection-instance roots. Its manufactured
# geometry stays at full size; only each instance centre moves. Fixed building
# elements, including consolidated wall/roof meshes, follow the piecewise bay
# transform so the 64 ft central training span keeps its original dimensions.
targets = []
for obj in bpy.data.objects:
    memberships = [c.name[:2] for c in obj.users_collection]
    if not memberships or all(prefix in {'90', '99'} for prefix in memberships):
        continue
    if obj.name == 'Studio ground':
        continue
    targets.append(obj)

bpy.context.view_layer.update()
old_world = {obj.name: obj.matrix_world.copy() for obj in targets}


def parent_depth(obj):
    depth = 0
    while obj.parent:
        depth += 1
        obj = obj.parent
    return depth


structural_prefixes = {'00', '01', '02', '03', '04', '05', '06', '21'}
deformed = 0
translated = 0
for obj in sorted(targets, key=parent_depth):
    before = old_world[obj.name]
    after = before.copy()
    after.translation.x = map_x_m(before.translation.x)
    prefixes = {c.name[:2] for c in obj.users_collection}
    deform_shape = bool(prefixes & structural_prefixes) and obj.type in {'MESH', 'CURVE'}
    if deform_shape and obj.type == 'MESH':
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        inverse = after.inverted()
        for vertex in obj.data.vertices:
            world_point = before @ vertex.co
            world_point.x = map_x_m(world_point.x)
            vertex.co = inverse @ world_point
        obj.data.update()
        deformed += 1
    elif deform_shape and obj.type == 'CURVE':
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        inverse = after.inverted()
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for point in spline.bezier_points:
                    for attr in ('co', 'handle_left', 'handle_right'):
                        world_point = before @ getattr(point, attr)
                        world_point.x = map_x_m(world_point.x)
                        setattr(point, attr, inverse @ world_point)
            else:
                for point in spline.points:
                    world_point = before @ Vector(point.co[:3])
                    world_point.x = map_x_m(world_point.x)
                    local_point = inverse @ world_point
                    point.co = (*local_point, point.co.w)
        deformed += 1
    else:
        translated += 1
    obj.matrix_world = after

    bounds = obj.get('Boundary in feet')
    if bounds and len(bounds) == 4:
        x1, x2, y1, y2 = (float(v) for v in bounds)
        nx1, nx2 = map_x_m(x1 * FT) / FT, map_x_m(x2 * FT) / FT
        obj['Boundary in feet'] = [nx1, nx2, y1, y2]
        obj['Area in square feet'] = (nx2 - nx1) * (y2 - y1)

# The drawing annotations in the retained orthographic scene are editable
# text, separate from the live website scene.
for obj in bpy.data.objects:
    if obj.type != 'FONT':
        continue
    body = obj.data.body
    obj.data.body = (body.replace('100 FT / 30.48 M', '96 FT / 29.26 M')
                    .replace('100 FT', '96 FT')
                    .replace('30.48 M', '29.26 M')
                    .replace('6,000 SQ FT', '5,760 SQ FT')
                    .replace('6,000 SF', '5,760 SF'))

# The old top dimension chain was 20 + 60 + 4 + 16 = 100 ft. The revised
# drawing-based chain is 16 + 60 + 4 + 16 = 96 ft; the 60-ft clear centre and
# adjoining 4-ft passage together form the PDF's 64-ft training span.
bpy.data.objects['Cardio / washroom bay dimension'].data.body = '16 FT'
bpy.data.objects['Cardio / washroom bay dimension'].name = 'Cardio / changing bay dimension'
bpy.data.objects['Overall width dimension'].data.body = '96 FT  /  29.26 M'
bpy.data.objects['Structural slab • 100 x 60 ft'].name = 'Structural slab • 96 x 60 ft (inferred)'

for scene in bpy.data.scenes:
    scene['PDF layout width applied'] = True
    if 'Measured footprint' in scene:
        del scene['Measured footprint']
    scene['Footprint interpretation'] = ('96 x 60 ft overall INFERRED; '
                                         '64 x 60 ft central training span shown in PDF.')
    scene['Overall footprint ft'] = [96.0, 60.0]
    scene['Training floor span ft'] = [64.0, 60.0]
    scene['Left cardio/changing bay ft'] = 16.0
    scene['Left bay dimension status'] = 'Inferred: drawn equal to 16 ft reception bay; confirm by site measurement.'
    scene['Dimensional confidence'] = ('64-ft training span and 16-ft reception-side bay from PDF; '
                                       'left bay and 96-ft outside width inferred.')
    scene['Proportion audit notes'] = ('Earlier 100 x 60 ft audit is superseded by the '
                                       'PDF layout revision; see LAYOUT_ALIGNMENT.md.')
    if scene.get('Dimension convention'):
        scene['Dimension convention'] = ('Feet; 96 x 60 ft overall inferred from PDF, '
                                         '64 x 60 ft central floor dimensioned, '
                                         '16 ft reception bay dimensioned, left bay inferred.')

guide = bpy.data.texts.get('PDF LAYOUT ALIGNMENT • 2026-09-28')
if not guide:
    guide = bpy.data.texts.new('PDF LAYOUT ALIGNMENT • 2026-09-28')
guide.clear()
guide.write(
    'Source: Gym layout .pdf (8 pages, supplied 2026-09-28).\n'
    'Page 5/7 central training-floor front/back wall: 64 ft.\n'
    'Page 6/8 central training-floor side wall: 60 ft.\n'
    'Page 2 reception bay: 5 + 5 + 6 = 16 ft.\n'
    'Page 4 draws left cardio/changing bay equal to reception: 16 ft INFERRED.\n'
    'Overall footprint: 16 + 64 + 16 = 96 ft x 60 ft INFERRED.\n'
    'No measured overall external dimension is written in the PDF.\n'
    'Existing 100 x 60 ft source is preserved separately; this is a new revision.\n'
)

bpy.context.view_layer.update()
print('PDF_LAYOUT_WIDTH_APPLIED',
      {'overall_ft': [96, 60], 'structural_objects_deformed': deformed,
       'other_objects_repositioned': translated}, flush=True)
