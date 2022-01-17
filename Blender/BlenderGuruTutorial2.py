import bpy
import bmesh
import mathutils
import pdb


## SelectNearestVertex attempts to select a single vertex in edit mode to a given position.
## Params:
##  dataItem -- the bpy.object.data of the item we want to select
##  positionWanted -- a point in xyz to find a vertex near and select it.
def SelectNearestVertext(dataItem, positionWanted):
    # This is a little complicated, and needs an explainer.
    # According to the docs,  Blender's Edit mode changes to using a different type system known as BMeshes.
    # In the BMeshes are the vertices, faces, probably edges, UVs, normals, etc.
    # Each of those types has its own objects.  A vertex, for example, has more than just its (xyz) position,
    # It also has properties like select, which can be get/set.

    # So, to get a single vertex selected means finding it in the nesting of objects that define its location.
    # Then setting that vertex's selected property.

    # Then, to do what Andrew did, we translate the vertex with the right options set for the translate function.
    # The proportional fall-off in the UX is really just a set of constants to the translate transform.
    
    ## build a KD tree from the dataItem passed in
    kd = mathutils.kdtree.KDTree(len(dataItem.vertices))
    for i, v in enumerate(dataItem.vertices):
        kd.insert(v.co, i)
    kd.balance()
    targetVertexPos, targetVertexIndex, targetVertexDistance = kd.find(positionWanted)

    ## Get the bmesh object from edit mode 
    if bpy.context.object.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
    bm = bmesh.from_edit_mesh(dataItem)
    
    ## select the found target vertex
    bm.verts.ensure_lookup_table()
    bm.verts[targetVertexIndex].select_set(True)
    
    ## To update blender's UX with the selection change, we need to flush and update
    bm.select_mode |= {'VERT'}
    bm.select_flush_mode()
    bmesh.update_edit_mesh(dataItem)


## Delete the base cube if it exists
if bpy.data.scenes['Scene'].objects.find('Cube') >= 0:
    bpy.data.scenes['Scene'].objects.get('Cube').select_set(True)
    bpy.ops.object.delete(use_global=False, confirm=False)
    

## Make sure our unit is metric, as my measures are in metric.
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.length_unit = 'METERS'


## create the Donut mesh if it doesn't already exist.
if bpy.data.scenes['Scene'].objects.find('Donut') < 0:
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), major_segments=40, minor_segments=16, major_radius=0.04, minor_radius=0.03, abso_major_rad=1.25, abso_minor_rad=0.75)
    bpy.context.selected_objects[0].name = "Donut" ## I want a better name than "Torus" in the scene collection. This seems to only be Scene Collection name -- other places will keep the "Torus" name.

## Select the donut
bpy.data.scenes['Scene'].objects.get('Donut').select_set(True)

## shade selected Donut smooth in object mode
if bpy.context.object.mode == 'EDIT':
    bpy.ops.object.editmode_toggle()
bpy.ops.object.shade_smooth()

## Add a subdivision modifier if it doesn't exist
if bpy.context.object.modifiers.find("Subdivision") < 0:
    bpy.ops.object.modifier_add(type='SUBSURF')

## Set the subdivision modifer properties to match Andrew's settings from the video
bpy.context.object.modifiers["Subdivision"].show_viewport = False
bpy.context.object.modifiers["Subdivision"].levels = 0
bpy.context.object.modifiers["Subdivision"].render_levels = 2

## Get into edit mode if not already, set proportional selection on.
if bpy.context.object.mode == 'OBJECT':
    bpy.ops.object.editmode_toggle()
bpy.context.scene.tool_settings.use_proportional_edit = True

## Let's make the lumps using the same technique Andrew did.
## That means we need to select a vertex, then translate it along its normal


myData = bpy.context.object.data
SelectNearestVertext(myData, (.07, 0, 0))
