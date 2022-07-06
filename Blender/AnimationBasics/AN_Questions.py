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
    def IcoSphere(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        sphere = bpy.context.object.data
        return(sphere)

    def UVSphere(self, radius=1, location=(0, 0, 0)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        sphere = bpy.context.object.data
        return(sphere)

## A class to create bones, append them to meshes, and create named control shapes
class SkeletonUtilities():
    def AddBoneToMesh(self, mesh, boneSize=(1, 1, 1)):
        pass



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
    def SetupWorld(self, system='METRIC', unit='METERS'):
        bpy.context.scene.unit_settings.system = system
        bpy.context.scene.unit_settings.length_unit = unit
     
###
## Main Questions
###

class BasicAnimationQuestions():
    def __init__(self):
        self.worldUtils = WorldUtilities()
        self.meshPrims = MeshPrimitives()
        self.meshUtils = MeshUtilities()

        ## clean up the world
        self.meshUtils.DeleteAllMeshObjects()
        self.worldUtils.SetupWorld()
        pass

    ## CreateHeadMeshes creates three spheres to represent the head of some toy thing.
    def CreateHeadMeshes(self):
        head = self.meshPrims.IcoSphere(radius=4)
        leftEye = self.meshPrims.UVSphere(radius=1.5, location=(0, 4, 0))
        rightEye = self.meshPrims.UVSphere(radius=1.5, location=(0, -4, 0))

        primBody = {'head': head, 'leftEye': leftEye, 'rightEye': rightEye}
        return(primBody)


    def HowDoIattachABoneToAUVSphere(self):
        self.meshUtils.DeleteAllMeshObjects()
        character = self.CreateHeadMeshes()
        print(character['leftEye'])
        return(character)

## run the question
q = BasicAnimationQuestions()
q.HowDoIattachABoneToAUVSphere()