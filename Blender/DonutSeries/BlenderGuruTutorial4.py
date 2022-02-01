import bpy
import bmesh
import mathutils
import pdb

## CreateKDTreeFromObject makes a KD tree, which is a data structure used to find spatial differences quickly.
## Parameters:
##  dataItem -- the 'MESH' of the item we want to generate a KD tree from.
def CreateKDTreeFromObject(dataItem):
    kd = mathutils.kdtree.KDTree(len(dataItem.vertices))
    for i, v in enumerate(dataItem.vertices):
        kd.insert(v.co, i)
    kd.balance()
    return(kd)

## SelectVertices selects vertices by index in an 'MESH' object
## Parameters:
##  dataItem -- the MESH we want to select vertices for
##  vertexIndices -- the list of vertex indices we want to select.
## Explainer:
##  Meshes are lists of points, loops, and faces.  Each list is a 0 indexed array.
##  Various functions will give us a list of vertex indices -- we can use those lists to select the vertices for further edits.
def SelectVertices(dataItem=None, vertexIndices=[]):
    ## Get the bmesh object from edit mode 
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.editmode_toggle()
    bm = bmesh.from_edit_mesh(dataItem)
    
    ## select the found target vertex
    for targetVertexIndex in vertexIndices:
        bm.verts.ensure_lookup_table()
        bm.verts[targetVertexIndex].select_set(True)
        
    ## To update blender's UX with the selection change, we need to flush and update
    bm.select_mode |= {'VERT'}
    bm.select_flush_mode()
    bmesh.update_edit_mesh(dataItem)
    pass ## Just to look pretty

## SelectNearestSetOfVertices selects a count of vertices based on an item, a point, and a target number of vertices.
## Params:
##  dataItem -- the bpy.object.data of the iterm we want vertices from
##  positionWanted -- a point in xyz to find a vertex near and select it.
##  vertexCount -- the number of vertices wanted in the selection action.
def SelectNearestSetOfVertices(dataItem, positionWanted, vertexCount):
    kd = CreateKDTreeFromObject(dataItem)
    rs = kd.find_n(positionWanted, vertexCount)
    
    vertexIndices = []
    for thisResult in rs:
        vertexIndices.append(thisResult[1])

    ## select the vertices
    SelectVertices(dataItem, vertexIndices)
    pass

## SelectNearestVertex attempts to select a single vertex in edit mode to a given position.
## Params:
##  dataItem -- the bpy.object.data of the item we want to select
##  positionWanted -- a point in xyz to find a vertex near and select it.
def SelectNearestVertext(dataItem, positionWanted):
    SelectNearestSetOfVertices(dataItem, positionWanted, 1)
    pass

## DeleteAllMeshObjects deletes all objects of type 'MESH'
def DeleteAllMeshObjects():
    ## We want to be in object mode and select all
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='SELECT')
    
    ## deselect anything that isn't a mesh
    for selectedObject in bpy.context.selected_objects:
        if selectedObject.type != "MESH":
            selectedObject.select_set(False)
    
    ## delete all selected objects.
    bpy.ops.object.delete(use_global=False, confirm=False)
    pass

## MakeDonut creates a base torus and deforms it, naming the creation "Donut"
def MakeDonut():
    ## Delete the base cube if it exists
    if bpy.data.scenes['Scene'].objects.find('Cube') >= 0:
        bpy.data.scenes['Scene'].objects.get('Cube').select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)

    ## Delete the Donut if it exsts.
    if bpy.data.scenes['Scene'].objects.find('Donut') >= 0:
        bpy.data.scenes['Scene'].objects.get('Donut').select_set(True)
        ## We can only delete in Object mode 
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
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


    ## Let's create an arrays of points, displacements, and proportions we can use for translation experimentation
    translate_pts = [(.07, 0, 0), (.09, .11, .09), (-.04, .04, 0.015)]
    translate_displacement = [(0.005, 0, 0), (0.005, 0.005, 0.005), (-.005, -0.005, 0.005)]
    translate_proportion = [0.035, 0.07, 0.05]

    ## translate experiment
    myData = bpy.context.object.data
    for index, pt in enumerate(translate_pts):
        bpy.ops.mesh.select_all(action='DESELECT')
        SelectNearestVertext(myData, pt)
        bpy.ops.transform.translate(value=translate_displacement[index], use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=translate_proportion[index])


    ## Let's create an array of points, displacements, and proportions we can use for shrink_fatten
    sf_pts = [(-.07, -0.07, 0), (1, -1, 1), (1, -1, 0.015)]
    sf_displacement = [-0.001, 0.005, -0.003]
    sf_proportion = [0.04, 0.035, .024]

    ## run the shrink_fatten transform
    for index, pt in enumerate(sf_pts):
        bpy.ops.mesh.select_all(action='DESELECT')
        SelectNearestVertext(myData, pt)
        bpy.ops.transform.shrink_fatten(value=sf_displacement[index], use_even_offset=False, mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=sf_proportion[index], use_proportional_connected=False, use_proportional_projected=False)
    pass ## end MakeDonut

def MakeIcing():
    bpy.ops.mesh.select_all(action='DESELECT')
    myData = bpy.context.object.data
    myVertexCount = int(len(myData.vertices)/2) + 40 ## Need more than 1/2 the vertices, as many are on the top.
    SelectNearestSetOfVertices(myData, (0, 0, 1), myVertexCount) ## (0,0,1) is a point 1 meter (3 feet) above the origin, and far above the donut.

    ## Duplicate the mesh to a different spot, separate it, and give it it's own name
    bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0.005)})
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.context.selected_objects[1].name = "Icing"

    # exit edit mode for the donut
    if bpy.context.object.mode == 'EDIT':
        bpy.ops.object.editmode_toggle()

    ## select only the Icing 
    bpy.ops.object.select_all(action='DESELECT') ## select nothing
    bpy.data.scenes['Scene'].objects.get('Icing').select_set(True) ## select the icing

    ## Selected objects and active objects are different.  I need to make the active object the Icing
    icing_object = bpy.data.objects['Icing'] ## this is the 'MESH' of the Icing object.
    bpy.context.view_layer.objects.active = icing_object ## selected objects aren't always active ones. Active objects recieve updates from bpy operations.  

    ## if the icing does not have a Solidify modifier, add it
    if bpy.context.object.modifiers.find("SOLIDIFY") < 0:
        bpy.ops.object.modifier_add(type='SOLIDIFY')

    ## set the modifier properties to match Andrew's
    bpy.context.object.modifiers["Solidify"].offset = 1
    bpy.context.object.modifiers["Solidify"].thickness = 0.0025

    ## make the solidify modifier the first in the list of modifiers to reduce the "hat" ness.
    bpy.ops.object.modifier_move_to_index(modifier="Solidify", index=0)
    pass        

## Make the base donut
#DeleteAllMeshObjects()
#MakeDonut()
#MakeIcing()

## Figure out how to select just the donut and put it into edit mode.
## select nothing
if bpy.context.mode != 'EDIT_MESH':
    bpy.ops.object.select_all(action='DESELECT') ## select nothing


def GetObjectData(objectName):
    target = bpy.data.scenes['Scene'].objects[objectName]
    return(target)


donut = GetObjectData('Donut')
bpy.context.view_layer.objects.active = donut
donut.select_set(True)
if bpy.context.object.mode != 'EDIT':
    bpy.ops.object.editmode_toggle()

## The little section above sets a single mesh to active + edit, which makes
## bpy.context.object.data now what I need to select points.
## now, let's select the loop.

SelectNearestSetOfVertices(bpy.context.object.data, (1, 0, 0), 2)
bpy.ops.mesh.loop_multi_select(ring=False)

