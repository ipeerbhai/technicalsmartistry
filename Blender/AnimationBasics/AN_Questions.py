## Reserach into using blender for simple posing and keyframe transitions via python
import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np
import os
from enum import Enum

class BoneTypes(Enum):
    Deform  = 1
    Control = 2
    Helper  = 3

class SubSurfModifierMethods(Enum):
    Simple = 'SIMPLE'
    CatmullCkark = 'CATMULL_CLARK'

## Notes ##
# Scale is "resize" in blender's API.

## MeshUtilities is a class with some helper functions for working with meshes as arrays of points.
class MeshUtilities():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        pass

    ## CreateKDTreeFromObject makes a KD tree, which is a data structure used to find spatial differences quickly.
    ## Parameters:
    ##  dataItem -- the 'MESH' of the item we want to generate a KD tree from.
    def CreateKDTreeFromObject(self, dataItem):
        kd = mathutils.kdtree.KDTree(len(dataItem.vertices))
        for i, v in enumerate(dataItem.vertices):
            kd.insert(v.co, i)
        kd.balance()
        return(kd)

    ## DeleteAllMeshObjects deletes all objects of type 'MESH'
    def DeleteAllMeshObjects(self):
        ## We want to be in object mode and select all
        if bpy.context.object == None:
            return
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

    ## SelectSomeNearbyVertices selects n number of vertices based on an item, a point, and a target number of vertices.
    ## Params:
    ##  dataItem -- the bpy.object.data of the iterm we want vertices from
    ##  positionWanted -- a point in xyz to find a vertex near and select it.
    ##  vertexCount -- the number of vertices wanted in the selection action.
    def SelectSomeNearbyVertices(self, dataItem, positionWanted, vertexCount):
        kd = self.CreateKDTreeFromObject(dataItem)
        rs = kd.find_n(positionWanted, vertexCount)
        
        vertexIndices = []
        for thisResult in rs:
            vertexIndices.append(thisResult[1])

        ## select the vertices
        self.SelectVerticesByIndex(dataItem, vertexIndices)
        pass

    ## SelectVerticesByIndices selects vertices by index in an 'MESH' object
    ## Parameters:
    ##  dataItem -- the MESH we want to select vertices for
    ##  vertexIndices -- the list of vertex indices we want to select.
    ## Explainer:
    ##  Meshes are lists of points, loops, and faces.  Each list is a 0 indexed array.
    ##  Various functions will give us a list of vertex indices -- we can use those lists to select the vertices for further edits.
    def SelectVerticesByIndices(self, dataItem=None, vertexIndices=[]):
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

    ## IncreaseVertexCount adds vertices to the mesh around the entire mesh by adding a subdivide modifier and applying the modifier.
    def IncreaseVertexCount(self, mesh, method=SubSurfModifierMethods.Simple, level=1):
        self.worldUtils.SetObjectMode()
        self.worldUtils.SelectItems([mesh])
        if bpy.context.object.modifiers.find("Subdivision") < 0:
            bpy.ops.object.modifier_add(type='SUBSURF')

        bpy.context.object.modifiers["Subdivision"].subdivision_type = method.value
        bpy.context.object.modifiers["Subdivision"].levels = level
        bpy.context.object.modifiers["Subdivision"].render_levels = level

        bpy.ops.object.modifier_apply(modifier="Subdivision", report=True) ## applies viewport amount
        pass

## A class to create meshes
class MeshPrimitives():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        pass

    ## Circle is a simple circle
    def Circle(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_circle_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        circle = bpy.context.object.data
        bpy.context.selected_objects[0].name = circle.name
        return(circle)
    

    ## Cylinder is a simple cylinder with radius r and height h
    def Cylinder(self, r=1, h=2):
        self.worldUtils.DeselectAll()
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        cyl = bpy.context.object.data
        bpy.context.selected_objects[0].name = cyl.name
        return(cyl)

    ## IvoShphere is a sphere with regularly placed vertices
    def IcoSphere(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        sphere = bpy.context.object.data
        bpy.context.selected_objects[0].name = sphere.name
        return(sphere)

    ## UVSphere is a sphere with vertices increasing in concentration around one axis.
    def UVSphere(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        sphere = bpy.context.object.data
        bpy.context.selected_objects[0].name = sphere.name
        return(sphere)

## A class to create Armatures/bones, append them to meshes, and create named control shapes
class SkeletonUtilities():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        pass

    def CreateArmature(self, type=BoneTypes.Deform):
        ## create an Armature
        self.worldUtils.DeselectAll()
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')
        bone = bpy.context.object.data
        bpy.context.selected_objects[0].name = bone.name
        return(bone)

    ## ClearAll deletes all Armatures
    def DeleteAllArmatureObjects(self, scene='Scene'):
        self.worldUtils.DeselectAll()
        allObjects = bpy.data.scenes['Scene'].objects
        for object in allObjects:
            if object.type == 'ARMATURE':
                ## select the object
                object.select_set(True)
        self.worldUtils.DeleteSelected()
        pass

    ## AddNewArmatureToMesh adds a single Armature/bone to a mesh at the center of the mesh and auto-weights mesh vertices to it.
    def AddNewArmatureToMesh(self, mesh, boneSize=(1, 1, 1)):

        ## find the center of the mesh
        center = (bpy.data.objects[mesh.name].location.x, bpy.data.objects[mesh.name].location.y, bpy.data.objects[mesh.name].location.z)
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=center, scale=boneSize)
        
        ## Create the Armature and name it
        Armature = bpy.context.object.data
        bpy.context.selected_objects[0].name = Armature.name

        self.BindExistingArmatureToMesh(Armature, mesh)
        return(Armature)
    
    ## Subdivide makes a single armature/bone into many linear bones.
    def Subdivide(self, armature, count=1):
        self.worldUtils.SetObjectMode()
        self.worldUtils.SelectItems([armature])
        bpy.ops.object.editmode_toggle() ## this selects the tail of the bone -- gotta select the bone itself.
        armature.edit_bones[0].select = True
        bpy.ops.armature.subdivide(number_cuts=count)
        bpy.ops.object.editmode_toggle()
        pass

    ## BindExistingArmatureToMesh binds an existing armature to a mesh
    def BindExistingArmatureToMesh(self, armature, mesh):
         ## select the mesh and the Armature
        self.worldUtils.SelectItems([mesh, armature])

        ## Parent the mesh to the Armature
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        pass

    ## ExtrudeBoneFromArmature extrudes a single bone from the armatrue in the Z direction
    def ExtrudeBoneFromArmatureAndEdit(self, armature, length=1):
        self.worldUtils.SetObjectMode()
        self.worldUtils.SelectItems([armature])

        ## Change to edit mode and select nothing.
        bpy.ops.object.editmode_toggle()
        bpy.ops.armature.select_all(action='DESELECT')
        
        ## Get the bone I want to extrude another bone from, and select the tail by edit mode foolishness (IMHO, this is a bug).
        lastBone = armature.bones[len(armature.bones)-1]
        bpy.ops.object.editmode_toggle()
        lastBone.select_tail = True
        bpy.ops.object.editmode_toggle()
        
        ## extrude a bone 1 unit vertically constrained on Z from this selected tail
        bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":(0, 0, 1), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        
        ## this extruded bone is now the active object, capture a reference to it before I lose it.
        newBone = bpy.context.active_bone

        ## deslect all, go back to object mode and return
        bpy.ops.armature.select_all(action='DESELECT')
        return (newBone)

    ## SelectSingleBoneForEdit selects a single bone and puts in edit mode.
    def SelectSingleBoneForEdit(self, armature, boneName):
        ## setup no selection, then select the armature
        self.worldUtils.SetObjectMode()
        self.worldUtils.SelectItems([armature])

        ## enter edit mode and select no bones at all
        bpy.ops.object.editmode_toggle()
        bpy.ops.armature.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

        ## select the bone and re-enter edit mode
        armature.bones[boneName].select=True
        bpy.ops.object.editmode_toggle()
        pass


    







## A class to help add/create textures to a mesh
class TextureUtilities():

    ## AddGeneratedUVMap adds a blender-created "smart UV" map to a mesh.
    def AddGeneratedUVMap(self, mesh):
        pass

    ## CreatePBRMaterialForMesh creates a basic paintable material with base color and base texture resolution.
    def CreatePBRMaterialForMesh(self, mesh, colorCode="#ffffff", resolution=(1024, 1024)):
        pass

## Some basic utilites that apply to the basic world
class WorldUtilities():

    ## ActivateObject sets the passed in object to active
    ## The bpy.context.scene.active_object needs to be set to the data block of the active object?
    def ActivateObject(self, object):
        bpy.context.scene.active_object = object
        pass

    ## SetupWorld sets the world's unit system
    def SetupWorld(self, system='METRIC', unit='METERS'):
        bpy.context.scene.unit_settings.system = system
        bpy.context.scene.unit_settings.length_unit = unit
        pass

    ## DeleteSelected deletes a selected object from the world
    def DeleteSelected(self):
        bpy.ops.object.delete(use_global=False, confirm=False)
        pass

    ## DeselectAll selects nothing.
    def DeselectAll(self):
        bpy.ops.object.select_all(action='DESELECT')
        pass

    ## SelectItems first deselects any other item, then selects the list of items.
    def SelectItems(self, items):
        self.DeselectAll()
        self.SelectAdditionalItems(items)
        pass

    ## SelectAdditionalItems adds items to the selection
    def SelectAdditionalItems(self, items, scene='Scene'):
        for toselectItem in items:
            bpy.data.scenes[scene].objects.get(toselectItem.name).select_set(True)
        pass

    ## SetSceneKeysToObjectDataNames sets the world outline name for an object to the same name as the objects data name.
    def SetSceneKeysToObjectDataNames(self, scene='Scene'):
        allObjects = bpy.data.scenes[scene].objects
        for object in allObjects:
            object.name = object.data.name
        pass

    ## SetSceneObjectDataNamesToSceneNames sets the object's data name to the world outliner name.
    def SetSceneObjectDataNamesToSceneNames(self, scene='Scene'):
        allObjects = bpy.data.scenes[scene].objects
        for object in allObjects:
            object.data.name = object.name
        pass

    ## GetWorldObjectFromObject gets the data object from a world object. In blender, objects are typed.  The world/scene objects are a different type than the same object as a Mesh, bone, etc
    def GetWorldObjectFromObject(self, object, scene='Scene'):
         target = bpy.data.scenes[scene].objects.get(object.name)
         return(target)

    ## HideObjectFromRender hides an object from being rendered in a full render, but shows in viewport.
    def HideObjectFromRender(self, object):
        worldRef = self.GetWorldObjectFromObject(object)
        worldRef.hide_render = True
        pass

    ## ScaleSelectedObject scales whatever is selected
    def ScaleSelectedObject(self, scale=(1, 1, 1)):
        bpy.ops.transform.resize(value=scale)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        pass


    ## SetObjectMode selects nothing and puts the system in object mode.
    def SetObjectMode(self):
        self.DeselectAll()
        bpy.ops.object.mode_set()
        pass

    ## TranslateSelected will translate the selected objects
    def TransateSelected(self, translate_displacement=(0, 0, 0)):
        bpy.ops.transform.translate(value=translate_displacement)
        pass

     
###
## Main Questions
###

class BasicAnimationQuestions():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        self.meshPrims = MeshPrimitives()
        self.meshUtils = MeshUtilities()
        self.skelUtils = SkeletonUtilities()

        ## clean up the world
        self.meshUtils.DeleteAllMeshObjects()
        self.skelUtils.DeleteAllArmatureObjects()
        self.worldUtils.SetupWorld()
        pass

    ## CreateHeadMeshes creates three spheres to represent the head of some toy thing.
    def CreateHeadMeshes(self):
        head = self.meshPrims.IcoSphere(radius=4)
        leftEye = self.meshPrims.UVSphere(radius=1.5, location=(0, -4, 0))
        rightEye = self.meshPrims.UVSphere(radius=1.5, location=(0, 4, 0))

        primBody = {'head': head, 'leftEye': leftEye, 'rightEye': rightEye}
        return(primBody)


    ## How do I use what I know to animate two eyes tracking something?
    def HowDoIAnimateEyes(self):
        ## clear everything, draw the character, create a bone, and parent an eye to the created bone.
        self.meshUtils.DeleteAllMeshObjects()
        self.skelUtils.DeleteAllArmatureObjects()
        character = self.CreateHeadMeshes()

        ## Blender doesn't support points as meshes, so create a very small circle as a control point and aim the bone at the circle.  
        reticle = self.meshPrims.Circle(radius=0.01, location=(0, 0, 5))
        reticle.name = 'Reticle'
        self.worldUtils.SetSceneKeysToObjectDataNames()
        self.worldUtils.HideObjectFromRender(reticle)

        ## add a bone to each eye and a tracking constraint to the bone.
        eyes = ['leftEye', 'rightEye']
        bones = []
        for eye in eyes:
            self.worldUtils.DeselectAll()
            bone = self.skelUtils.AddNewArmatureToMesh(character[eye])
            self.worldUtils.SetSceneKeysToObjectDataNames()
            bpy.ops.object.constraint_add(type='TRACK_TO')
            bpy.context.object.constraints["Track To"].target = self.worldUtils.GetWorldObjectFromObject(reticle)
            bones.append(bone)
        
        ## update the character hash to include the bones.
        character['bones'] = bones
        return(character)

    ## How do I bend a tube?  Adapted from https://www.youtube.com/watch?v=jw30S-Oepyo
    def HowDoIBendATube(self):
        self.meshUtils.DeleteAllMeshObjects()
        cylinderHeight = 10

        ## step -- create a tube and add enough points to the mesh for good bending.
        tube = self.meshPrims.Cylinder(r=1, h=cylinderHeight)
        self.meshUtils.IncreaseVertexCount(mesh=tube, level=3)

        ## step -- create an Armature with 5 bones in it
        armature = self.skelUtils.CreateArmature() ## start with 1 bone, not attached to the mesh
        self.worldUtils.ScaleSelectedObject((1, 1, cylinderHeight)) ## armatures start off 1 unit tall -- let's make it the same height as the cylinder.
        self.skelUtils.Subdivide(armature, count=4)

        ## step -- place the armature inside the mesh
        self.worldUtils.TransateSelected((0, 0, -cylinderHeight/2))

        ## save the name of the final bone.
        lastBoneName = armature.bones[len(armature.bones)-1].name ## the actual object changes underneath internal to blender, and we can't be sure this object will remain the one we want.

        ## extrude a bone from the tail, name that bone IK, make it a non-deforming bone, and clear its parent.
        ikBone = self.skelUtils.ExtrudeBoneFromArmatureAndEdit(armature, length=1) ## this put me into armature edit mode.
        ikBone.name = 'IK'
        ikBone.use_deform = False
        finalDeformBone = ikBone.parent
        ikBone.parent = None

        ## clear the parent, exit edit mode
        bpy.ops.armature.parent_clear(type='CLEAR')
        bpy.ops.object.editmode_toggle()

        ## Complex step -- setup the armature to use the ikBone for inverse kinematics via constraints.
        self.skelUtils.SelectSingleBoneForEdit(armature, lastBoneName)

        ## change to pose mode from previous edit mode ( still in complex step )
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.posemode_toggle()

        ## add an IK contstraint and set some poorly documented properties
        armatureAsSceneType = self.worldUtils.GetWorldObjectFromObject(armature)
        ikConstraint = armatureAsSceneType.pose.bones[lastBoneName].constraints.new("IK")
        ikConstraint.target = armatureAsSceneType
        ikConstraint.subtarget = ikBone.name
        ikConstraint.use_stretch = False
        bpy.ops.object.posemode_toggle()

        ## step -- skin the mesh
        self.skelUtils.BindExistingArmatureToMesh(armature, tube)
        pass
    


    ## How do I squish a ball?
    def HowdDoISquishABall(self):
        ## step 1 -- create a ball and a bone
        ball = self.meshPrims.IcoSphere()
        bone = self.skelUtils.CreateBone()

        ## step 2 -- figure out how to assign weights to vertices.
        self.worldUtils.SelectItems([ball, bone])
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        ## how do I figure out the vertex weights?
        ## maybe something to do with the bpy.types.VertexGroup class?

 
        pass

## run the questions
q = BasicAnimationQuestions()
# q.HowDoIAnimateEyes() ## learn basic object tracking via bones -- done!
q.HowDoIBendATube() ## Learn basic IK for an object via bones and a control bone -- done!
# q.HowdDoISquishABall() ## learn how to apply shapes to bones
# q.HowDoIAnimateATentacle() ## learn IK, shape bones, rotation and noise constraints.
# q.HowDoIBendALeg() ## Learn how to use IK, FK, and poles together to make "plastic doll" motion
# q.HowDoIMoveLips() ## Learn how to use blends/morphs to move lips to the A and O visemes
# q.HowDoIInsertKeyFrames() ## How do I add a keyframe?
# q.HowDoIchangeSCurves() ## How do I modify the acceleration interpolation curve implied between keyframes?
# q.ProjectBoundBallWithTailUpStairsMovie() ## Tie all this together to make a video of a sentient ball that has a tail bouncing up some stairs.

## What I've learned along the way
# Blender has bones.  Bones can be of different types -- deformation bones, control bones, and helper bones.
# Armatures are collections of bones that can be bound to a mesh.
# Bone Constraints are how you configure bones to enable motion plans.
# Meshes can only deform in "Pose Mode" -- you can't move items around in object or edit mode.
# IK Constraint is inverse kinematics, and it solves the deform backwards to hit a target point.
# FK constraint is forward kinematics, and it solves positioning of bones down the chain if that bone moved a certain way.
# IK can have a pole constraint, which restricts rotation of the object around the X axis.
# The axis of constraint is always local x, not global X, in an IK Pole constraint, but the bone can have its own origin tranform matrix, so X can be aligned to any direction locally.

## Useful videos to watch from here
## https://www.youtube.com/watch?v=suP14lYWpN8 -- learn how to animate a leg rig