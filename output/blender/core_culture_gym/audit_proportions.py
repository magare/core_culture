"""Read-only geometric inventory, plan measurements and hard-clash audit."""
import bpy, json, math, os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).resolve().parent
FT=.3048
label=os.environ.get('GYM_AUDIT_LABEL','before')
original_scene=bpy.context.window.scene
evaluation=bpy.data.scenes.new('__DIMENSION AUDIT ONLY')
for col in list(bpy.data.collections):
    if any(col.name in s.collection.children for s in bpy.data.scenes if s!=evaluation):
        evaluation.collection.children.link(col)
bpy.context.window.scene=evaluation
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
geometries={}
metrics={}
for o in bpy.data.objects:
    record={'type':o.type,'collections':[c.name for c in o.users_collection],
            'location_ft':[v/FT for v in o.matrix_world.translation],
            'scale':list(o.scale),'rotation_degrees':[math.degrees(v) for v in o.rotation_euler],
            'props':{k:str(o[k]) for k in o.keys()}}
    if o.type in {'MESH','CURVE','FONT'}:
        eo=o.evaluated_get(dg)
        me=eo.to_mesh()
        if me and len(me.vertices):
            points=[o.matrix_world@v.co for v in me.vertices]
            lo=[min(v[k] for v in points)/FT for k in range(3)]
            hi=[max(v[k] for v in points)/FT for k in range(3)]
            record['bbox_ft']=[lo,hi]
            record['world_size_ft']=[b-a for a,b in zip(lo,hi)]
            record['local_size_ft']=[(max(v.co[k] for v in me.vertices)-min(v.co[k] for v in me.vertices))/FT for k in range(3)]
            record['vertices']=len(me.vertices)
            geometries[o.name]=(points,[tuple(p.vertices) for p in me.polygons])
        eo.to_mesh_clear()
    metrics[o.name]=record

assets=[o for o in bpy.data.objects if 'Asset type' in o]
walls=[o for o in bpy.data.objects if any(c.name.startswith(('02 | Walls','03 | Rear','04 | Exterior','05 | Partitions')) for c in o.users_collection)
       and (' • base' in o.name or ' • upper' in o.name or ' • lintel' in o.name)]
doors=[o for o in bpy.data.objects if o.name.endswith('door leaf') or 'door leaf.' in o.name]
trees={}
def bbox_overlap(a,b):
    x,y=metrics[a.name].get('bbox_ft'),metrics[b.name].get('bbox_ft')
    return x and y and all(min(x[1][k],y[1][k])-max(x[0][k],y[0][k])>.015 for k in range(3))
def tree(o):
    if o.name not in trees:
        vs,fs=geometries[o.name]
        trees[o.name]=BVHTree.FromPolygons(vs,fs,all_triangles=False)
    return trees[o.name]
clashes=[]
for item in assets+doors:
    for wall in walls:
        if bbox_overlap(item,wall):
            hits=tree(item).overlap(tree(wall))
            if hits:clashes.append({'object':item.name,'wall':wall.name,'intersecting_faces':len(hits)})
asset_clashes=[]
for i,a in enumerate(assets):
    for b in assets[:i]:
        if bbox_overlap(a,b):
            hits=tree(a).overlap(tree(b))
            if hits:asset_clashes.append({'a':a.name,'b':b.name,'intersecting_faces':len(hits)})
fixture_clashes=[]
for item in bpy.data.objects:
    if item in assets or item.name not in geometries:continue
    if not any(c.name.startswith(('13 |','14 |','15 |')) for c in item.users_collection):continue
    for wall in walls:
        if bbox_overlap(item,wall):
            hits=tree(item).overlap(tree(wall))
            if hits:fixture_clashes.append({'object':item.name,'wall':wall.name,'intersecting_faces':len(hits)})

def box(name):return metrics[name]['bbox_ft']
slab=box('Structural slab • 100 x 60 ft')
circle=box('Central 16 ft functional circle')
turf=box('HYROX performance turf')
zones=[{'object':o.name,'bounds':list(o['Boundary in feet']),'area':o['Area in square feet'],'mesh_bbox':box(o.name)}
       for o in bpy.data.objects if 'Boundary in feet' in o]
zone_area=sum(z['area'] for z in zones)
west_faces=[box(o.name)[1][0] for o in walls if o.name.startswith('Cardio & washroom partition') and ' • base' in o.name]
east_faces=[box(o.name)[0][0] for o in walls if o.name.startswith('East circulation partition') and ' • base' in o.name]
south_faces=[box(o.name)[1][1] for o in walls if o.name.startswith('South exterior') and ' • base' in o.name]
ext_bboxes=[box(o.name) for o in bpy.data.objects if o.name.startswith(('North corrugated wall','West corrugated wall','South exterior','Entrance / east facade')) and o.name in geometries]
west_trim=[box(o.name)[1][0] for o in bpy.data.objects if o.name.startswith('Cardio & washroom partition') and 'skirting' in o.name]
east_trim=[box(o.name)[0][0] for o in bpy.data.objects if o.name.startswith('East circulation partition') and 'skirting' in o.name]
south_trim=[box(o.name)[1][1] for o in bpy.data.objects if o.name.startswith('South exterior') and 'skirting' in o.name]
hyrox_south=float(bpy.data.objects['HYROX floor']['Boundary in feet'][2])
passage_start=float(bpy.data.objects['Passage east floor']['Boundary in feet'][0])
duct_box=box(next(o.name for o in bpy.data.objects if o.name.startswith('Main AC duct')))
duct_axis=(duct_box[0][1]+duct_box[1][1])/2
measurements={
    'floor_slab_ft':[slab[1][k]-slab[0][k] for k in (0,1)],
    'zoned_floor_area_sqft':zone_area,
    'exterior_wall_outer_span_ft':[max(b[1][k] for b in ext_bboxes)-min(b[0][k] for b in ext_bboxes) for k in (0,1)],
    'central_circle_diameter_ft':[circle[1][k]-circle[0][k] for k in (0,1)],
    'circle_center_ft':[(circle[1][k]+circle[0][k])/2 for k in (0,1)],
    'circle_west_edge_to_partition_face_ft':circle[0][0]-max(west_faces),
    'circle_east_edge_to_passage_start_ft':passage_start-circle[1][0],
    'circle_west_edge_to_finished_trim_ft':circle[0][0]-max(west_trim),
    'east_passage_nominal_ft':4,
    'east_passage_between_hyrox_and_partition_face_ft':min(east_faces)-passage_start,
    'east_passage_clear_including_trim_ft':min(east_trim)-passage_start,
    'south_passage_nominal_ft':4,
    'south_passage_to_wall_face_ft':hyrox_south-max(south_faces),
    'south_passage_clear_including_trim_ft':hyrox_south-max(south_trim),
    'circle_south_edge_to_hyrox_south_edge_ft':circle[0][1]-hyrox_south,
    'circle_north_edge_to_duct_axis_ft':duct_axis-circle[1][1],
    'turf_north_edge_ft':turf[1][1],
    'turf_to_circle_y_gap_ft':circle[0][1]-turf[1][1],
}
support_errors=[]
for o in assets:
    low=box(o.name)[0][2]
    expected=.2075 if o['Asset type']=='power rack' else (.175 if o['Asset type']=='sled' else .05)
    if abs(low-expected)>.015:support_errors.append({'object':o.name,'support_gap_ft':low-expected})
treadmills=[o for o in assets if o['Asset type']=='treadmill']
stairs=[o for o in assets if o['Asset type']=='stair climber']
rear_gaps=[box(t.name)[0][1]-box(st.name)[1][1] for t in treadmills for st in stairs
           if min(box(t.name)[1][0],box(st.name)[1][0])>max(box(t.name)[0][0],box(st.name)[0][0])]
measurements['minimum_treadmill_to_stair_rear_gap_ft']=min(rear_gaps)
measurements['minimum_treadmill_to_stair_rear_gap_m']=min(rear_gaps)*FT
zone_pairs=[]
for i,a in enumerate(zones):
    ax1,ax2,ay1,ay2=a['bounds']
    for b in zones[:i]:
        bx1,bx2,by1,by2=b['bounds']
        overlap=max(0,min(ax2,bx2)-max(ax1,bx1))*max(0,min(ay2,by2)-max(ay1,by1))
        if overlap>1e-6:zone_pairs.append([a['object'],b['object'],overlap])
report={'source':bpy.data.filepath,'measurements':measurements,'zones':zones,
        'equipment':{o.name:metrics[o.name] for o in assets},
        'equipment_or_door_wall_clashes':clashes,'equipment_equipment_clashes':asset_clashes,
        'fixture_wall_clashes':fixture_clashes,
        'equipment_floor_support_errors':support_errors,'floor_zone_overlaps':zone_pairs,
        'object_count':len(metrics),'objects':metrics,
        'limitations':'Geometry checks do not establish as-built dimensions, human operating clearances, egress or code compliance.'}
(OUT/f'proportion_audit_{label}.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in {'objects','equipment'}},indent=2),flush=True)
print('EQUIPMENT SIZES (local XYZ ft):',flush=True)
for kind in sorted({o['Asset type'] for o in assets}):
    o=next(o for o in assets if o['Asset type']==kind)
    print(kind,metrics[o.name]['local_size_ft'],flush=True)
if label in {'after','branded','aesthetic'}:
    for actual,target in [(measurements['floor_slab_ft'][0],100),(measurements['floor_slab_ft'][1],60),
                          (measurements['exterior_wall_outer_span_ft'][0],100),(measurements['exterior_wall_outer_span_ft'][1],60),
                          (measurements['central_circle_diameter_ft'][0],16),(measurements['central_circle_diameter_ft'][1],16),
                          (measurements['circle_west_edge_to_finished_trim_ft'],22),(measurements['circle_east_edge_to_passage_start_ft'],22),
                          (measurements['east_passage_clear_including_trim_ft'],4),(measurements['south_passage_clear_including_trim_ft'],4),
                          (measurements['circle_south_edge_to_hyrox_south_edge_ft'],18),(measurements['circle_north_edge_to_duct_axis_ft'],18)]:
        assert abs(actual-target)<.001,(actual,target)
    assert abs(zone_area-6000)<.001 and not zone_pairs
    assert not clashes,clashes
    assert not asset_clashes,asset_clashes
    assert not fixture_clashes,fixture_clashes
    assert not support_errors,support_errors
    assert measurements['turf_to_circle_y_gap_ft']>.5
    assert measurements['minimum_treadmill_to_stair_rear_gap_m']>=2
    print('ALL_EXPLICIT_DIMENSION_AND_EQUIPMENT_CLASH_CHECKS_PASSED',flush=True)
bpy.context.window.scene=original_scene
bpy.data.scenes.remove(evaluation)
