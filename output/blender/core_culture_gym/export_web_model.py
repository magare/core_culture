"""Export the saved website cutaway, without saving/modifying the source .blend.

Run with Blender --background Core_Culture_Gym_Layout_Aligned.blend --python this.py.
Evaluated collection instances, curves, text and bevels become real glTF meshes.
Opaque pieces are batched by logical group; dimensions/transforms are untouched.
"""
import bpy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
SITE = OUT.parents[2] / 'site'
DEST = SITE / 'assets' / 'models'
DEST.mkdir(parents=True, exist_ok=True)
SOURCE = Path(bpy.data.filepath)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source = bpy.data.scenes['07 | WEBSITE • architectural cutaway']
bpy.context.window.scene = source
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
records = []
for instance in dg.object_instances:
    obj = instance.object
    if obj.type not in {'MESH', 'FONT', 'CURVE', 'SURFACE'} or obj.hide_render or not instance.show_self:
        continue
    # Presentation backdrop is replaced by a realtime shadow-catching stage.
    if any(slot.material and slot.material.name == '20 • presentation background' for slot in obj.material_slots):
        continue
    original = obj.original
    group = 'signage' if any(c.name.startswith('22 | SUSPENDED') for c in original.users_collection) else 'architecture'
    if original.name.startswith('OFFICIAL LOGO'):
        group = 'logos'
    records.append((original, instance.matrix_world.copy(), group))

sign_roots = {obj.parent.name for obj, _, group in records
              if group == 'signage' and obj.parent and obj.parent.name.startswith('HANGING SIGN •')}
assert len(sign_roots) == 10, sign_roots

web_materials = {}
logo_image = bpy.data.images['CORE CULTURE • official cleaned transparent logo'].copy()
logo_image.name = 'CC accepted transparent logo • web'
logo_image.scale(1024, 1024)

def web_material(mat):
    if mat.name in web_materials:
        return web_materials[mat.name]
    result = bpy.data.materials.new(mat.name + ' | web')
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    original = next((node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None) if mat.use_nodes else None
    shader.inputs['Base Color'].default_value = mat.diffuse_color
    for key in ('Roughness', 'Metallic', 'IOR', 'Emission Color', 'Emission Strength'):
        if original:
            shader.inputs[key].default_value = original.inputs[key].default_value
    if mat.name.startswith(('BRAND • matte printed', 'BRAND • silver logo')):
        texture = result.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = logo_image
        result.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
        result.node_tree.links.new(texture.outputs['Alpha'], shader.inputs['Alpha'])
        shader.inputs['Metallic'].default_value = .35 if 'silver' in mat.name else .05
        shader.inputs['Roughness'].default_value = .42 if 'silver' in mat.name else .78
        result.surface_render_method = 'DITHERED'
    elif mat.name == '22 • tinted entrance glass':
        # Alpha glazing is stable and inexpensive on mobile; no offscreen transmission pass.
        shader.inputs['Alpha'].default_value = .19
        shader.inputs['Metallic'].default_value = .12
        shader.inputs['Roughness'].default_value = .14
        result.surface_render_method = 'DITHERED'
    web_materials[mat.name] = result
    return result

staged = []
mesh_cache = {}
for original, matrix, group in records:
    evaluated = original.evaluated_get(dg)
    key = original.as_pointer()
    if key not in mesh_cache:
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=dg)
        if group != 'logos':
            for layer in list(mesh.uv_layers):
                mesh.uv_layers.remove(layer)
        # Object-linked material overrides must survive mesh conversion.
        mesh.materials.clear()
        for slot in evaluated.material_slots:
            if slot.material:
                mesh.materials.append(web_material(slot.material))
        mesh_cache[key] = mesh
    duplicate = bpy.data.objects.new(original.name, mesh_cache[key])
    duplicate.matrix_world = matrix
    duplicate['web_group'] = group
    staged.append(duplicate)

export_scene = bpy.data.scenes.new('Core Culture • interactive ground floor')
bpy.context.window.scene = export_scene
for obj in staged:
    export_scene.collection.objects.link(obj)
bpy.context.view_layer.update()

# Merge opaque objects without simplifying geometry. Text remains real extruded mesh.
for group in ('architecture', 'signage'):
    candidates = [o for o in export_scene.objects if o['web_group'] == group]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in candidates:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = candidates[0]
    bpy.ops.object.join()
    candidates[0].name = 'CC_' + group
    candidates[0]['web_group'] = group

triangles = 0
for obj in export_scene.objects:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)

target = DEST / 'core-culture-gym.glb'
bpy.ops.export_scene.gltf(
    filepath=str(target), export_format='GLB', use_active_scene=True,
    export_animations=False, export_cameras=False, export_lights=False,
    export_extras=True, export_yup=True, export_apply=False,
    export_materials='EXPORT', export_image_format='AUTO',
    export_meshopt_compression_enable=True, export_meshopt_extension='EXT_meshopt_compression',
)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash, 'Source blend changed'
report = {
    'source': SOURCE.name, 'source_sha256': source_hash, 'source_unchanged': True,
    'scene': source.name,
    'footprint_ft': list(source.get('Overall footprint ft', [100, 60])),
    'evaluated_mesh_objects': len(records), 'exported_objects': len(export_scene.objects),
    'triangles': triangles, 'materials': len(web_materials),
    'hanging_signs': len(sign_roots), 'exported_logos': sum(o.get('web_group') == 'logos' for o in export_scene.objects),
    'bytes': target.stat().st_size,
    'notes': ['Visible website cutaway; roof/exterior upper walls intentionally omitted.',
              'Geometry evaluated and batched, not decimated.',
              'Procedural shader nodes reduced to their base PBR finishes.',
              'Glazing uses alpha transparency; logos embedded at 1024px.'],
}
(DEST / 'model-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print('WEB_MODEL_EXPORTED', json.dumps(report), flush=True)
