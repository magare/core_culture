"""Check for modeling changes made while the optimized copy was being prepared."""
import bpy
import hashlib
import json
from array import array
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def state():
    result={}
    for o in bpy.data.objects:
        h=hashlib.sha256()
        h.update(str((o.type,list(o.location),list(o.rotation_euler),list(o.scale),o.hide_viewport,o.hide_render,sorted(c.name for c in o.users_collection),o.parent.name if o.parent else None)).encode())
        if o.type=='MESH':
            for items,prop,count,code in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
                vals=array(code,[0])*(len(items)*count);items.foreach_get(prop,vals);h.update(vals.tobytes())
        elif o.type=='FONT':h.update(str((o.data.body,o.data.size,o.data.extrude)).encode())
        elif o.type=='CURVE':
            h.update(str((o.data.bevel_depth,o.data.bevel_resolution)).encode())
            for s in o.data.splines:
                for p in s.points:h.update(str(tuple(p.co)).encode())
        if o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,tuple(o.data.color))).encode())
        if o.type=='CAMERA':h.update(str((o.data.type,o.data.lens,o.data.ortho_scale)).encode())
        h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
        result[o.name]=h.hexdigest()
    return result

a=state()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Core_Culture_Gym_before_optimized_open.blend'))
b=state()
changed=sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k))
report={'modeling_changes_during_optimization':changed,'same_geometry_and_placements':not changed}
(ROOT/'live_session_check.json').write_text(json.dumps(report,indent=2))
print('LIVE_SESSION_CHECK',json.dumps(report),flush=True)
