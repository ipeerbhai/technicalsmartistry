import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np

## GenerateStrokePtFromKDTree generates a single mouse stroke from a pt
def GenerateStrokePtFromKDTree(tree, location, is_start=False):
    ## find the vertex on the tree nearest the target point
    vertexInfo = tree.find(location)
    pt = np.array(vertexInfo[0])

    ## generate a single point in a stroke path 
    path_point = {"name": "defaultStroke",
            "mouse" : (0, 0),
            "pen_flip" : False,
            "is_start": is_start,
            "location": pt,
            "pressure": 1.0,
            "time": 1.0,
            "size" : 100.0
            }
    return(path_point)

## GeneratePointFromPolarPoint(r, theta, Z) creates an X, Y, Z tuple from a polar displacement radius, theta, and cartesian height
def GeneratePointFromPolarPoint(r, theta, Z):
    rads = math.radians(theta)
    x = r * math.cos(rads)
    y = r * math.sin(rads)
    z = Z
    return((x, y, z))

## GetObjectData is just a shortcut to save typing to bpy...objects
def GetObjectData(objectName):
    target = bpy.data.scenes['Scene'].objects[objectName]
    return(target)

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
    match bpy.context.object.mode:
        case 'EDIT':
            bpy.ops.object.editmode_toggle()
        case 'SCULPT':
             bpy.ops.sculpt.sculptmode_toggle()

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
    return(myData) ## end MakeDonut

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
    return(myData)        

## Add detail to the icing.
def DetailIcing(donut_tree, icing_tree):
    ## deselect everything and select only the icing, make the icing the active object
    if bpy.context.mode == 'EDIT_MESH':
        bpy.ops.mesh.select_all(action='DESELECT') ## note, we have a different object to call select_all with -- the mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
    icing = GetObjectData('Icing')
    bpy.context.view_layer.objects.active = icing
    icing.select_set(True)
    icing_object = bpy.context.object.data ## need the icing as a mesh object for KD trees

    ## Set the solidify modifier to not show in edit mode, then go to edit mode.
    bpy.context.object.modifiers["Solidify"].show_in_editmode = False
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.editmode_toggle()

    ## turn on snap to face with projection.
    bpy.context.scene.tool_settings.use_snap = True
    bpy.context.scene.tool_settings.snap_elements = {'FACE'}
    bpy.context.scene.tool_settings.use_snap_project = True
    
    ## Andrew now has us pull in reference -- we'll skip that.
    
    ## Andrew now applies the subsurf modifier -- let's do that.
    bpy.ops.object.modifier_move_to_index(modifier="Subdivision", index=0)
    bpy.context.object.modifiers["Subdivision"].levels = 1
    bpy.ops.object.editmode_toggle() ## back to object mode
    bpy.ops.object.modifier_apply(modifier="Subdivision", report=True) ## applies viewport amount
    
    ## add another subsurf modifier after the solidify modifier
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 1
    bpy.ops.object.modifier_move_to_index(modifier="Subdivision", index=1)
    

    ## back to edit mode and select some vertices along the bottom
    bpy.ops.object.editmode_toggle()

    ## turn on snap to face with projection.  This seems to do nothing in python.  You'd have to manually tree walk and adjust points.
    ## This would be "incomplete API" behavior, I think.
    bpy.context.scene.tool_settings.use_snap = True
    bpy.context.scene.tool_settings.snap_elements = {'FACE'}
    bpy.context.scene.tool_settings.use_snap_project = True
    
    ## let's generate equal divisions for a wave superimposed on the icing
    divions = 4
    for thetaIndex in range(divions):
        pt1 = np.asarray(GeneratePointFromPolarPoint(.07, thetaIndex*(360/divions), -0.01)) ## 7cm from center, 22 degrees of rotation around 0,0, 1 cm down
        bpy.ops.mesh.select_all(action='DESELECT') ## Don't forget this, or the points stay selected, and displacement becomes cumalative!
        SelectNearestVertext(icing_object, pt1) ## select the icing vertex
        
        ## find the selected point
        selectedPt = icing_tree.find(pt1)
        tp1 = pt1 - np.asarray((0, 0, -0.01)) ## What's a point near pt1, but 0.05 down.
        fi = donut_tree.find(tp1) ## What's the nearest vertex on the donut near that displaced point.
        dp1 = np.asarray(selectedPt[0]) - np.asarray(fi[0]) ## What's the displacement needed to move from the icing point to the donut point?
        
        ## let's try displacing it down and see what happens.
        bpy.ops.transform.translate(value=dp1, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=0.05)

        #bpy.ops.transform.translate(value=dp1, orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=0.0355841, use_proportional_connected=False, use_proportional_projected=False)
    
    ## let's create the little drippings.
    divions = 7
    bpy.ops.mesh.select_all(action='DESELECT') ## Don't forget this, or the points stay selected, and displacement becomes cumalative!
    for thetaIndex in range(divions):
        pt1 = np.asarray(GeneratePointFromPolarPoint(.07, thetaIndex*(360/divions), -0.01)) ## 7cm from center, 22 degrees of rotation around 0,0, 1 cm down
        SelectNearestSetOfVertices(icing_object, pt1,3 ) ## select vertices for extrusion
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(-0.00133574, -9.8661e-05, -0.0146044), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    
    ## exit edit mode, select nothing, return
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='DESELECT')
    pass

def DetailDonut(donut_object):
    ## make sure to deselect everything.
    if bpy.context.mode == 'EDIT_MESH':
        bpy.ops.mesh.select_all(action='DESELECT') ## note, we have a different object to call select_all with -- the mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
    

    ## select the donut and make it active
    donut = GetObjectData('Donut')
    bpy.context.view_layer.objects.active = donut
    donut.select_set(True)

    ## add and apply a subdiv surf modifier of 1 viewport level.
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 1
    bpy.ops.object.modifier_move_to_index(modifier="Subdivision", index=1)
    bpy.ops.object.modifier_apply(modifier="Subdivision", report=True) ## This invalidates the donut kd_tree, as I added vertices.  Ooops.

    ## select the ring around the middle.
    SelectNearestSetOfVertices(bpy.context.object.data, (1, 0, 0), 2)
    bpy.ops.mesh.loop_multi_select(ring=False)

    ## shrink the center
    bpy.ops.transform.shrink_fatten(value=-0.005, use_even_offset=False, mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=.01, use_proportional_connected=False, use_proportional_projected=False)
    
    ## fatten the bottom a bit
    bpy.ops.mesh.select_all(action='DESELECT')
    targetPt = GeneratePointFromPolarPoint(.07, 1, -0.03)
    SelectNearestSetOfVertices(bpy.context.object.data, targetPt, 2)
    bpy.ops.mesh.loop_multi_select(ring=False)
    bpy.ops.transform.shrink_fatten(value=0.0033, use_even_offset=False, mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=.02, use_proportional_connected=False, use_proportional_projected=False)
    
    ## deselect and exit edit mode
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action='DESELECT')
    pass

def EditDonutAndIciningMeshes(donut_object, icing_object):
    ## get the KD tree for the donut
    donut_tree = CreateKDTreeFromObject(donut_object)
    icing_tree = CreateKDTreeFromObject(icing_object)

    ## add some more detail to the icing
    DetailIcing(donut_tree, icing_tree)

    ## Make the center ring of the donut a little smaller
    DetailDonut(donut_object)

    ## put the shrinkwrap modifier on the icing.
    icing = GetObjectData('Icing')
    bpy.context.view_layer.objects.active = icing
    icing.select_set(True)
    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects["Donut"]
    bpy.ops.object.modifier_move_to_index(modifier="Shrinkwrap", index=0)
    bpy.ops.object.modifier_apply(modifier="Shrinkwrap", report=True)

    ## deselect all
    bpy.ops.object.select_all(action='DESELECT')

        
## Make the base donut
DeleteAllMeshObjects()

## generate the base objects
donut_object = MakeDonut()
icing_object = MakeIcing()

## add mesh details to both donut and icing per Andrew's video 4.
EditDonutAndIciningMeshes(donut_object, icing_object)

## Apply all modifiers
icing = GetObjectData('Icing')
bpy.context.view_layer.objects.active = icing
icing.select_set(True)
bpy.ops.object.modifier_apply(modifier="Solidify", report=True)
bpy.ops.object.modifier_apply(modifier="Subdivision", report=True)

## Switch to a sculpting tool and drag it across the icing?
bpy.ops.object.mode_set(mode='SCULPT')
bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")

## define a stroke to sculpt
stroke = [{ "name": "defaultStroke",
                            "mouse" : (0.0, 0.0),
                            "pen_flip" : False,
                            "is_start": True,
                            "location": (0, 0, 0),
                            "pressure": 1.0,
                            "time": 1.0}]