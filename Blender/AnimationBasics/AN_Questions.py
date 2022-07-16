## Reserach into using blender for simple posing and keyframe transitions via python
import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np
import os
import enum

## MeshUtilities is a class with some helper functions for working with meshes as arrays of points.
class MeshUtilities():
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

## A class to create meshes
class MeshPrimitives():
    ## Circle is a simple circle
    def Circle(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_circle_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        circle = bpy.context.object.data
        bpy.context.selected_objects[0].name = circle.name
        return(circle)

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

## A class to create bones, append them to meshes, and create named control shapes
class SkeletonUtilities():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        pass

    def CreateBone(self):
        self.worldUtils.DeselectAll()
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')
        bone = bpy.context.object.data
        bpy.context.selected_objects[0].name = bone.name
        return(bone)

    ## ClearAll deletes all armitures
    def DeleteAllArmitureObjects(self, scene='Scene'):
        self.worldUtils.DeselectAll()
        allObjects = bpy.data.scenes['Scene'].objects
        for object in allObjects:
            if object.type == 'ARMATURE':
                ## select the object
                object.select_set(True)
        self.worldUtils.DeleteSelected()
        pass

    ## AddArmitureToMesh adds a single armiture/bone to a mesh at the center of the mesh and auto-weights mesh vertices to it.
    def AddArmitureToMesh(self, mesh, boneSize=(1, 1, 1)):

        ## find the center of the mesh
        center = (bpy.data.objects[mesh.name].location.x, bpy.data.objects[mesh.name].location.y, bpy.data.objects[mesh.name].location.z)
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=center, scale=boneSize)
        
        ## Create the armiture and name it
        armiture = bpy.context.object.data
        bpy.context.selected_objects[0].name = armiture.name

        ## select the mesh and the armiture
        self.worldUtils.SelectItems([mesh, armiture])

        ## Parent the mesh to the armiture
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        return(armiture)

## A class to help add/create textures to a mesh
class TextureUtilities():

    ## AddGeneratedUVMap adds a blender-created UV map to a mesh.
    def AddGeneratedUVMap(self, mesh):
        pass

    ## CreatePaintablePBR creates a basic paintable mesh with base color and base texture resolution.
    def CreatePaintablePBR(self, mesh, colorCode="#ffffff", resolution=(1024, 1024)):
        pass

## Some basic utilites that apply to the basic world
class WorldUtilities():

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
        self.skelUtils.DeleteAllArmitureObjects()
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
        self.skelUtils.DeleteAllArmitureObjects()
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
            bone = self.skelUtils.AddArmitureToMesh(character[eye])
            self.worldUtils.SetSceneKeysToObjectDataNames()
            bpy.ops.object.constraint_add(type='TRACK_TO')
            bpy.context.object.constraints["Track To"].target = self.worldUtils.GetWorldObjectFromObject(reticle)
            bones.append(bone)
        
        ## update the character hash to include the bones.
        character['bones'] = bones
        return(character)
    
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

## run the question
q = BasicAnimationQuestions()
#q.HowDoIAnimateEyes()
q.HowdDoISquishABall()