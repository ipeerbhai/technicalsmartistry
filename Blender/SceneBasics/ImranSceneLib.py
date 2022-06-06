## This is a collection of functions I wrote up to make blender easier to deal with / think more like me.
import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np
import os

class Importers():
    def __init__(self) -> None:
        pass

    ## ImportGLTF imports a file and gives you back the imported objects, or None on error.
    ## importing doesn't give you the objects imported.  It gives you a result code, and selects the imported objects.
    ## The blender API here is poorly designed.  Why not do something like object, err = import(), and set the object to None on error?
    ## This function tries to fix that.
    def ImportGLTF(self, filePath="", fileName=""):
        ## simple parameter validation -- don't allow "" for either.
        if filePath == "" or fileName == "":
            return (None, "Invalid path or filename")

        ## deselect all.
        bpy.ops.object.select_all(action='DESELECT')

        ## Import the actual GLTF
        file = filePath + os.sep + fileName
        resultStatus = bpy.ops.import_scene.gltf(filepath=file, files=[{"name":fileName, "name":fileName}], loglevel=50)

        ## Save the selected objects array from import.
        objects = bpy.context.selected_objects

        ## return a tuple with the objects, Status.
        return (objects, resultStatus)

    ## ImportFromBlendFile takes objects, collections, meshes, or other items from 
    ## blend files and imports them into the existing scene
    def ImportFromBlendFile(blendFile="", objectType="Object", objectName=""):
        if blendFile == "" or objectName == "":
            return (None, "Invalid blend file or object name")
        
        ## deselect all
        bpy.ops.object.select_all(action='DESELECT')

        ## append the actual object.
        resultStatus = bpy.ops.wm.append(filepath=os.path.join(blendFile, objectType, objectName), directory=os.path.join(blendFile, objectType), filename=objectName)

        ## Save the selected objects array from import.
        objects = bpy.context.selected_objects

        ## return a tuple with the objects, Status.
        return (objects, resultStatus)
    
    ## Import an EXR/HDR light map as a large dome/sphere mapped as a world background texture/light source
    def ImportHDRorEXRIntoWorld(self, exrFile="", position=[0, 0, 0]):
        if exrFile == "":
            return("No exr or hdr file specified")

        ## get the node tree for the world and clear it.
        node_tree = bpy.context.scene.world.node_tree
        tree_nodes = bpy.context.scene.world.node_tree.nodes
        tree_nodes.clear()

        ## add 3 nodes from left to right -- Environment Texture, Bacgkround, and output
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment') ## Ennvironment Texture
        node_background = tree_nodes.new('ShaderNodeBackground') ## bacgkround node, default position of 0, 0
        node_output = tree_nodes.new(type='ShaderNodeOutputMaterial')   

        ## move the nodes to left/right orderinga
        node_environment.location = -300,0  ## move left 300 px
        node_output.location = 200,0 ## move right 400 px from 0

        ## link the three nodes together.
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
        link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

        ## load the EXF/HDR into the environment node.
        node_environment.image = bpy.data.images.load(exrFile)

        ### Advanced -- change the XYZ position of the EXR
        node_vector = tree_nodes.new(type='ShaderNodeMapping')
        node_vector.location = -500, 0 ## this is the location of the node in the node graph, not the input location!!!!

        ## to set the vector node's input properties, we refer to it by array positions.  So Input[0][0] is the "vector" 0,0 in the input set.
        node_vector.inputs['Location'].default_value[0] = position[0] ## X position
        node_vector.inputs['Location'].default_value[1] = position[1] ## Y position
        node_vector.inputs['Location'].default_value[2] = position[2] ## Z position

        ## link up the new vector node
        link = links.new(node_vector.outputs["Vector"], node_environment.inputs["Vector"])

        ## add a texture coordinate node and link its generated to the vector mapping input vector ( or else the vector mapping node does not work )
        node_textcoord = tree_nodes.new(type='ShaderNodeTexCoord')
        node_textcoord.location = -700, 0
        link = links.new(node_textcoord.outputs["Generated"], node_vector.inputs["Vector"])
        return(link)


class CollectionHelpers():
    ## CreateCollectionWithName Creates a collection with the specified name and links it in as a child of the top level collection
    def CreateCollectionWithName(self, name="ImranCollection"):
        sceneCollection = bpy.context.scene.collection
        newCollection = bpy.data.collections.new(name) ## also available via bpy.data.collection[name]
        sceneCollection.children.link(newCollection) ## make the new collection visible
        return(newCollection)

    ## MoveObjectsBetweenCollections moves all specified objects from one collection to another.
    def MoveObjectsBetweenCollections(self, objects, oldCollection, newCollection):
        for item in objects:
            newCollection.objects.link(item)
            oldCollection.objects.unlink(item)

    ## Quick shortcut to get the top-lvel master/scene collection.
    def GetMasterCollection(self):
        return(bpy.context.scene.collection)


## Generates terrain for a scene
class TerrainGenerators():
    def __init__(self) -> None:
        pass