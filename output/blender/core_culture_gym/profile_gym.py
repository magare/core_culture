import bpy
import json
import time
import hashlib
import os
from pathlib import Path
from collections import Counter, defaultdict

OUT=Path(__file__).resolve().parent

def signature(mesh):
    h=hashlib.sha256()
    for v in mesh.vertices:h.update((','.join(float(c).hex() for c in v.co)+';').encode())
    for p in mesh.polygons:h.update((str(tuple(p.vertices))+':'+str(p.material_index)+':'+str(p.use_smooth)).encode())
    h.update(str([m.name if m else None for m in mesh.materials]).encode())
    return h.hexdigest()

def profile():
    meshes=[m for m in bpy.data.meshes if m.users]
    groups=defaultdict(list)
    for m in meshes:groups[signature(m)].append(m.name)
    cols=[]
    for c in bpy.data.collections:
        obs=list(c.objects)
        cols.append({'name':c.name,'objects':len(obs),'meshes':sum(o.type=='MESH' for o in obs),'base_vertices':sum(len(o.data.vertices) for o in obs if o.type=='MESH'),'base_faces':sum(len(o.data.polygons) for o in obs if o.type=='MESH'),'modifiers':dict(Counter(m.type for o in obs for m in o.modifiers))})
    scene_stats=[]
    for s in bpy.data.scenes:
        bpy.context.window.scene=s
        start=time.perf_counter()
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        tris=0;polys=0;vs=0
        for o in bpy.context.view_layer.objects:
            if o.type not in {'MESH','CURVE','FONT'}:continue
            eo=o.evaluated_get(dg);me=eo.to_mesh()
            if me:
                vs+=len(me.vertices);polys+=len(me.polygons)
                tris+=sum(max(0,len(p.vertices)-2) for p in me.polygons)
            eo.to_mesh_clear()
        scene_stats.append({'name':s.name,'view_layer_objects':len(bpy.context.view_layer.objects),'evaluated_vertices':vs,'evaluated_faces':polys,'evaluated_triangles':tris,'evaluation_seconds':round(time.perf_counter()-start,4),'samples':s.cycles.samples,'preview_samples':s.cycles.preview_samples,'adaptive_threshold':s.cycles.adaptive_threshold,'noise_threshold':s.cycles.use_adaptive_sampling})
    return {'file':bpy.data.filepath,'bytes':Path(bpy.data.filepath).stat().st_size,'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'used_meshes':len(meshes),'unique_exact_meshes':len(groups),'duplicate_mesh_datablocks':sum(len(v)-1 for v in groups.values()),'unique_base_vertices':sum(len(m.vertices) for m in meshes),'unique_base_faces':sum(len(m.polygons) for m in meshes),'curves':len(bpy.data.curves),'modifiers':dict(Counter(m.type for o in bpy.data.objects for m in o.modifiers)),'collections':cols,'scenes':scene_stats,'largest_meshes':sorted([{'name':m.name,'vertices':len(m.vertices),'faces':len(m.polygons),'users':m.users} for m in meshes],key=lambda m:m['vertices'],reverse=True)[:15],'transforms':{o.name:{'type':o.type,'matrix':[list(row) for row in o.matrix_world],'dimensions':list(o.dimensions)} for o in bpy.data.objects},'scene_names':[s.name for s in bpy.data.scenes]}

report=profile()
(OUT/('profile_'+os.environ.get('GYM_PROFILE_LABEL','before')+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='transforms'},indent=2),flush=True)
