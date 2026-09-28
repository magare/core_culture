"""Read-only branding, material and reference inventory."""
import bpy, json
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent
FT=.3048
original=bpy.context.window.scene
evaluation=bpy.data.scenes.new('__BRAND_INSPECTION')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):
        evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation
bpy.context.view_layer.update()
records=[]
for o in bpy.data.objects:
    if any(s in o.name.lower() for s in ['logo','monogram','brand','central circle','lane finish','presentation title','north corrugated wall','mat centre','yoga mat']):
        pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
        records.append({'name':o.name,'type':o.type,'body':o.data.body if o.type=='FONT' else '',
            'location_ft':[v/FT for v in o.matrix_world.translation],'rotation':list(o.rotation_euler),
            'collections':[c.name for c in o.users_collection],
            'bbox_ft':[[f(v[i] for v in pts)/FT for i in range(3)] for f in [min,max]],
            'hidden_render':o.hide_render,'hidden_viewport':o.hide_viewport,'modifiers':[m.type for m in o.modifiers]})
report={'logos':records,'text_objects':[{'name':o.name,'body':o.data.body} for o in bpy.data.objects if o.type=='FONT'],
        'scenes':[(s.name,len(s.objects)) for s in bpy.data.scenes if s!=evaluation]}
image=bpy.data.images.load(str(OUT/'core_culture_logo_transparent.png'),check_existing=True)
alpha=list(image.pixels)[3::4]
report['logo_image']={'size':list(image.size),'channels':image.channels,'alpha_min':min(alpha),'alpha_max':max(alpha),
                     'transparent_fraction':sum(a<.01 for a in alpha)/len(alpha)}
(OUT/'branding_inventory.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
bpy.context.window.scene=original
bpy.data.scenes.remove(evaluation)
