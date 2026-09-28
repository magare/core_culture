"""Presentation-only camera refinement; building geometry is unchanged."""
import bpy, math
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=bpy.data.scenes['03 | EXTERIOR • entrance'];c=s.camera
c.location=Vector((136,35,8))*.3048
c.rotation_euler=(Vector((100,44,8.5))*.3048-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=30
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Core_Culture_Gym_Aesthetic.blend'),compress=True)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
bpy.context.window.scene=s;s.cycles.device='GPU';s.render.filepath=str(OUT/'aesthetic_entrance.png')
bpy.ops.render.render(write_still=True)
