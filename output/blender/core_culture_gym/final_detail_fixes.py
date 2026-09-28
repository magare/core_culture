"""Seat the exterior planter on its shelf, preserving the audited model."""
import bpy
from mathutils import Vector
from pathlib import Path
import json

FT=.3048
OUT=Path(__file__).resolve().parent
original_scene=bpy.context.window.scene
bpy.context.window.scene=bpy.data.scenes['03 | EXTERIOR • entrance']
bpy.context.view_layer.update()
pot=bpy.data.objects['Exterior entry plant planter']
shelf=bpy.data.objects['Entrance shoe shelf • static batch']
pot_points=[pot.matrix_world @ v.co for v in pot.data.vertices]
shelf_points=[shelf.matrix_world @ v.co for v in shelf.data.vertices]
bottom=min(v.z for v in pot_points)
base=[v for v in pot_points if abs(v.z-bottom)<1e-5]
shelf_lo=Vector([min(v[k] for v in shelf_points) for k in range(3)])
shelf_hi=Vector([max(v[k] for v in shelf_points) for k in range(3)])
base_center=Vector(((min(v.x for v in base)+max(v.x for v in base))/2,
                    (min(v.y for v in base)+max(v.y for v in base))/2,bottom))
target=Vector(((shelf_lo.x+shelf_hi.x)/2,shelf_hi.y-.9*FT,shelf_hi.z))
delta=target-base_center
for obj in bpy.data.objects:
    if obj.name.startswith('Exterior entry plant'):
        assert obj.parent is None
        obj.location+=delta
bpy.context.view_layer.update()
pot_points=[pot.matrix_world @ v.co for v in pot.data.vertices]
bottom=min(v.z for v in pot_points)
base=[v for v in pot_points if abs(v.z-bottom)<1e-5]
assert abs(bottom-shelf_hi.z)<1e-5
assert all(shelf_lo.x<v.x<shelf_hi.x and shelf_lo.y<v.y<shelf_hi.y for v in base)
pot['Support verified']='Planter base fully inside the shoe shelf footprint, seated on its top surface.'
note='Seated the exterior planter on the shoe-shelf top and centered its base inside the support footprint.'
corrections=OUT/'proportion_corrections.json'
summary=json.loads(corrections.read_text())
if note not in summary['changes']:summary['changes'].append(note)
corrections.write_text(json.dumps(summary,indent=2))
text=bpy.data.texts['PROPORTION AUDIT • measurements and unresolved items']
text.clear();text.write(json.dumps(summary,indent=2))
bpy.data.scenes['06 | AUDIT • verified plan dimensions'].use_fake_user=True
bpy.context.window.scene=original_scene
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
print('EXTERIOR_PLANT_SUPPORT_VERIFIED_AND_SAVED',flush=True)
