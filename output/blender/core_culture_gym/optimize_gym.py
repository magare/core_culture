"""Optimize a saved live-session copy without modifying the original gym file."""
import bpy
import json
import re
import math
import hashlib
import time
import os
from array import array
from pathlib import Path
from collections import Counter, defaultdict
from mathutils import Vector

OUT=Path(__file__).resolve().parent
TARGET=OUT/'Core_Culture_Gym_Optimized.blend'
started=time.perf_counter()
source_path=bpy.data.filepath
before=json.loads((OUT/'profile_before.json').read_text())
original_scene_names=[s.name for s in bpy.data.scenes]
original_units={s.name:(s.unit_settings.system,s.unit_settings.scale_length,s.unit_settings.length_unit) for s in bpy.data.scenes}
original_zone_areas={o.name:float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}
original_equipment={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if 'Asset type' in o}
original_cameras={o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if o.type=='CAMERA'}
initial_modifiers=sum(len(o.modifiers) for o in bpy.data.objects)
batch_records=[]

# Use a temporary evaluation scene so excluded roof/facade objects are evaluated too.
# Originals keep exactly their scene links and visibility choices.
evaluation=bpy.data.scenes.new('__Optimization evaluation only')
roots=list(bpy.data.scenes.get(original_scene_names[0]).collection.children)
for c in roots:evaluation.collection.children.link(c)
bpy.context.window.scene=evaluation
bpy.context.view_layer.update()

def world_mesh_bounds(o):
    points=[o.matrix_world@v.co for v in o.data.vertices]
    return [fn(p[k] for p in points) for fn in [min,max] for k in range(3)]

initial_mesh_bounds={o.name:world_mesh_bounds(o) for o in bpy.data.objects if o.type=='MESH'}

def mesh_signature(o):
    m=o.data
    if m.shape_keys or m.uv_layers or len(o.vertex_groups) or m.has_custom_normals:return None
    permitted={'position','.edge_verts','.corner_vert','.corner_edge','material_index','sharp_face','sharp_edge','.select_vert','.select_edge','.select_poly'}
    if any(a.name not in permitted for a in m.attributes):return None
    h=hashlib.sha256()
    for items,prop,count,code in [(m.vertices,'co',3,'f'),(m.edges,'vertices',2,'i'),(m.loops,'vertex_index',1,'i'),(m.polygons,'loop_total',1,'i'),(m.polygons,'material_index',1,'i'),(m.polygons,'use_smooth',1,'b')]:
        values=array(code,[0])*(len(items)*count)
        items.foreach_get(prop,values)
        h.update(values.tobytes())
    for name in ['sharp_edge','sharp_face']:
        attr=m.attributes.get(name)
        if attr:
            values=array('b',[0])*len(attr.data);attr.data.foreach_get('value',values);h.update(name.encode()+values.tobytes())
    h.update(json.dumps([s.material.name_full if s.material else None for s in o.material_slots]).encode())
    return h.hexdigest()

def deduplicate():
    seen={};count=0
    for o in list(bpy.data.objects):
        if o.type!='MESH':continue
        sig=mesh_signature(o)
        if sig is None:continue
        if sig in seen and o.data!=seen[sig]:o.data=seen[sig];count+=1
        else:seen[sig]=o.data
    return count

linked_before=deduplicate()
print('Shared identical mesh datablocks:',linked_before,flush=True)

# Remove only exact overlapping duplicate parts within the same collection.
# The original generator created two copies of each weight-tree upright.
removed_duplicates=[]
seen={}
for o in list(bpy.data.objects):
    if o.type!='MESH' or o.modifiers or o.constraints or o.animation_data or o.parent or o.keys():continue
    sig=mesh_signature(o)
    if sig is None:continue
    key=(sig,tuple(v for row in o.matrix_world for v in row),tuple(sorted(c.name for c in o.users_collection)),o.hide_render,o.hide_viewport)
    if key in seen:
        removed_duplicates.append({'name':o.name,'duplicate_of':seen[key]})
        bpy.data.objects.remove(o,do_unlink=True)
    else:seen[key]=o.name

# Curve simplification affects millimetre-scale pipe and grille trim, not floor geometry.
curve_changes=[]
for curve in bpy.data.curves:
    if isinstance(curve,bpy.types.TextCurve):
        old=curve.resolution_u
        curve.resolution_u=4
        curve.render_resolution_u=8
        if old!=4:curve_changes.append({'name':curve.name,'change':'text viewport tessellation 4; render tessellation 8'})
        continue
    old=curve.bevel_resolution
    if old>1:curve.bevel_resolution=1
    reduced=0
    for spline in curve.splines:
        if spline.type!='POLY' or not spline.use_cyclic_u or len(spline.points)!=96:continue
        pts=[p.co.copy() for p in spline.points]
        center=sum((Vector(p[:3]) for p in pts),Vector())/len(pts)
        radius=max((Vector(p[:3])-center).length for p in pts)
        if radius>=1:continue
        replacement=curve.splines.new('POLY')
        replacement.points.add(47)
        for dst,src in zip(replacement.points,pts[::2]):dst.co=src
        replacement.use_cyclic_u=True
        curve.splines.remove(spline)
        reduced+=48
    if old!=curve.bevel_resolution or reduced:
        curve_changes.append({'name':curve.name,'bevel_resolution_before':old,'bevel_resolution_after':curve.bevel_resolution,'control_points_removed':reduced})

def plain_materials(o):
    # Unlinked noise coordinates use per-object Generated space; leave these parts separate.
    for slot in o.material_slots:
        m=slot.material
        if m and m.node_tree and any(n.type=='TEX_NOISE' for n in m.node_tree.nodes):return False
    return True

def base_name(o):return re.sub(r'\.\d{3,}$','',o.name)

static_families={
 '01':{'Rubber tile joint X','Rubber tile joint Y','Studio oak plank joint','Staggered end grain joint'},
 '06':{'Roof standing seam A','Roof standing seam B','Portal steel column','Steel truss chord','Triangular web bracing','Roof purlin','Gable vertical seam','Longitudinal ridge truss chord','Ridge truss diagonal','Ridge truss vertical','Pendant suspension wire','Vertical pendant dark backing','Vertical warm-white tube','Duct hanger','Suspended linear luminaire','Linear LED diffuser'},
 '07':{'Entry aluminium stile','Entry aluminium transom','Entrance pull handle','Canopy black support','Canopy diagonal bracket','Canopy corrugation','Shutter slat','Entrance shoe shelf','Shoe shelf frame'},
 '08':{'Spiral duct seam','Side duct collar','AC grille collar','AC grille dark insert','AC grille horizontal louver','AC grille upright'},
 '10':{'Mirror vertical mullion','Mirror bottom protective rail','Plate storage branch','Stored bumper plate'},
 '11':{'HYROX lane boundary','HYROX start / finish','Lane distance hash','Wall ball accent'},
 '13':{'Reception desk fluting','Coffee table leg','Support desk leg','Chair stem','Chair base'},
 '14':{'Barre bracket','Mat centre logo','Studio cubby'},
}

groups=defaultdict(list)
for c in roots:
    for o in list(c.objects):
        if o.type not in {'MESH','CURVE'} or o.constraints or o.animation_data or o.parent or 'Asset type' in o or o.keys():continue
        name=base_name(o)
        eligible=(' • cladding rib' in name or ' • skirting' in name or name in static_families.get(c.name[:2],set()))
        if eligible and plain_materials(o) and len(o.users_collection)==1 and not o.hide_render and not o.hide_viewport:
            groups[(c.name,name)].append(o)

bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
for (colname,name),parts in groups.items():
    if len(parts)<3:continue
    c=bpy.data.collections[colname]
    verts,faces,matids,smooth,mats=[],[],[],[],[]
    originals=[o.name for o in parts]
    for o in parts:
        eo=o.evaluated_get(dg);me=eo.to_mesh()
        offset=len(verts)
        verts.extend([tuple(o.matrix_world@v.co) for v in me.vertices])
        slots=[]
        for slot in o.material_slots:
            m=slot.material
            if m not in mats:mats.append(m)
            slots.append(mats.index(m))
        for p in me.polygons:
            faces.append(tuple(offset+i for i in p.vertices))
            matids.append(slots[p.material_index] if slots else 0)
            smooth.append(p.use_smooth)
        eo.to_mesh_clear()
    mesh=bpy.data.meshes.new(name+' • consolidated mesh')
    mesh.from_pydata(verts,[],faces);mesh.update()
    for m in mats:
        if m:mesh.materials.append(m)
    for p,i,s in zip(mesh.polygons,matids,smooth):p.material_index=i;p.use_smooth=s
    batch=bpy.data.objects.new(name+' • static batch',mesh);c.objects.link(batch)
    batch['Optimization']='Static repeated details combined; Edit Mode > Separate > By Loose Parts to split.'
    batch['Original part count']=len(parts)
    batch['Original parts']=json.dumps(originals)
    batch_records.append({'collection':colname,'batch':batch.name,'parts':len(parts),'vertices':len(verts),'faces':len(faces)})
    for o in parts:bpy.data.objects.remove(o,do_unlink=True)
    print('Combined',len(parts),'parts:',name,flush=True)

bpy.context.window.scene=bpy.data.scenes[original_scene_names[0]]
bpy.data.scenes.remove(evaluation)
bpy.context.view_layer.update()
linked_after=deduplicate()

render_settings=[]
for s in bpy.data.scenes:
    s.cycles.preview_samples=16
    s.cycles.use_preview_denoising=True
    s.cycles.use_preview_adaptive_sampling=True
    s.cycles.preview_adaptive_threshold=.12
    s.cycles.preview_adaptive_min_samples=4
    s.cycles.use_adaptive_sampling=True
    s.cycles.adaptive_threshold=.025
    s.cycles.adaptive_min_samples=8
    # Retain final sample ceiling, image sizes, bounce limits and render engine.
    s['Optimization notes']='Shared identical meshes; batched static trim; lighter small curves; 16-sample denoised viewport. Room and equipment transforms retained.'
    s.render.filepath=str(OUT/('optimized_'+{'01':'cutaway','02':'plan','03':'entrance','04':'free_weights','05':'hyrox'}[s.name[:2]]+'.png'))
    render_settings.append({'scene':s.name,'engine':s.render.engine,'final_samples':s.cycles.samples,'preview_samples':s.cycles.preview_samples,'adaptive_threshold':s.cycles.adaptive_threshold})

for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='CONSOLE':a.type='VIEW_3D' if a.width>500 else 'OUTLINER'
        for space in a.spaces:
            if space.type!='VIEW_3D':continue
            space.clip_start=.1;space.clip_end=200
            space.shading.type='SOLID';space.shading.color_type='MATERIAL'
            space.shading.show_cavity=True;space.shading.cavity_type='WORLD'
            space.overlay.show_overlays=False
            space.region_3d.view_perspective='CAMERA'
            space.region_3d.view_camera_zoom=13

# Retain sources, fonts, semantic objects, camera framing and all user equipment changes.
assert [s.name for s in bpy.data.scenes]==original_scene_names
assert all((s.unit_settings.system,s.unit_settings.scale_length,s.unit_settings.length_unit)==original_units[s.name] for s in bpy.data.scenes)
assert {o.name:float(o['Area in square feet']) for o in bpy.data.objects if 'Area in square feet' in o}==original_zone_areas
assert {o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if 'Asset type' in o}==original_equipment
assert {o.name:tuple(v for row in o.matrix_world for v in row) for o in bpy.data.objects if o.type=='CAMERA'}==original_cameras
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
changed_bounds=[]
for o in bpy.data.objects:
    if o.name in initial_mesh_bounds:
        bounds=world_mesh_bounds(o)
        if max(abs(a-b) for a,b in zip(bounds,initial_mesh_bounds[o.name]))>1e-5:changed_bounds.append(o.name)
assert not changed_bounds,changed_bounds

# Remove only unreferenced datablocks from this optimized copy.
bpy.data.orphans_purge(do_recursive=True)
after={'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'curves':len(bpy.data.curves),'modifiers':dict(Counter(m.type for o in bpy.data.objects for m in o.modifiers)),'scenes':len(bpy.data.scenes),'equipment_instances':len(original_equipment),'packed_reference_images':len([i for i in bpy.data.images if i.source=='FILE' and i.packed_file])}
report={'source':source_path,'output':str(TARGET),'before':{k:before[k] for k in ['objects','meshes','curves','modifiers','bytes']},'after':after,'exact_mesh_links_created':linked_before+linked_after,'duplicate_parts_removed':removed_duplicates,'static_batches':batch_records,'curve_changes':curve_changes,'render_settings':render_settings,'preserved_checks':{'all_five_scenes':True,'room_areas':True,'equipment_transforms':True,'camera_transforms':True,'retained_mesh_bounds':True,'packed_references':True},'elapsed_seconds':round(time.perf_counter()-started,2)}
guide=bpy.data.texts.new('OPTIMIZATION • changes and controls')
guide.write('PERFORMANCE EDITION\n\nOriginal and pre-optimization snapshot are retained alongside this file.\n\n'+json.dumps({k:v for k,v in report.items() if k not in ['curve_changes','static_batches']},indent=2)+'\n\nStatic batches contain original part names in Custom Properties. To split one: Edit Mode > Select All > Mesh > Separate > By Loose Parts. Equipment remains independently selectable and movable. Final image dimensions and sample limits are retained; rendered viewport preview is limited to 16 samples with denoising.\n')
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='METAL'
except Exception:pass
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET),compress=True)
after['bytes']=TARGET.stat().st_size
(OUT/'optimization_report.json').write_text(json.dumps(report,indent=2))
print('OPTIMIZED',json.dumps({k:v for k,v in report.items() if k not in ['curve_changes','static_batches','render_settings']}),flush=True)

if os.environ.get('GYM_OPT_RENDER','1')=='1':
    for name in [original_scene_names[0],original_scene_names[4]]:
        s=bpy.data.scenes[name]
        bpy.context.window.scene=s
        t=time.perf_counter()
        bpy.ops.render.render(write_still=True)
        print('RENDER_VERIFIED',name,round(time.perf_counter()-t,3),flush=True)
    bpy.context.window.scene=bpy.data.scenes[original_scene_names[0]]
print('OPTIMIZATION_COMPLETE',flush=True)
