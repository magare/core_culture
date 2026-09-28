"""Read-only inventory and current-scene review renders for the aesthetic pass."""
import bpy, json
from pathlib import Path
OUT=Path(__file__).resolve().parent
materials=[]
for m in bpy.data.materials:
    nodes=[]
    if m.use_nodes:
        for n in m.node_tree.nodes:
            inputs={}
            for i in n.inputs:
                if i.name in {'Base Color','Metallic','Roughness','Scale','Strength','Distance','Emission Strength','Color','Vector'} and hasattr(i,'default_value'):
                    v=i.default_value
                    inputs[i.name]=list(v) if hasattr(v,'__iter__') else v
            nodes.append({'type':n.type,'name':n.name,'inputs':inputs})
    materials.append({'name':m.name,'users':m.users,'diffuse':list(m.diffuse_color),'nodes':nodes})
report={'materials':materials,'scenes':[{'name':s.name,'camera':s.camera.name,'exposure':s.view_settings.exposure,
    'excluded':[c.name for c in s.view_layers[0].layer_collection.children if c.exclude]} for s in bpy.data.scenes],
    'lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in bpy.data.objects if o.type=='LIGHT'],
    'objects':[{'name':o.name,'type':o.type,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'body':o.data.body if o.type=='FONT' else ''} for o in bpy.data.objects]}
(OUT/'aesthetic_before_inventory.json').write_text(json.dumps(report,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
for name,filename in [('01 | CUTAWAY • furnished plan','aesthetic_before_cutaway.png'),('04 | INTERIOR • free weights','aesthetic_before_interior.png')]:
    s=bpy.data.scenes[name];bpy.context.window.scene=s
    s.cycles.device='GPU';s.cycles.samples=20;s.cycles.use_denoising=True
    s.render.resolution_percentage=60;s.render.filepath=str(OUT/filename)
    bpy.ops.render.render(write_still=True)
    print('BASELINE_RENDERED',filename,flush=True)
