## this script loads a GLTF model complete with textures into the scene.

import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np
import os

## ImportGLTF imports a file and gives you back the imported objects, or None on error.
## importing doesn't give you the objects imported.  It gives you a result code, and selects the imported objects.
## The blender API here is poorly designed.  Why not do something like object, err = import(), and set the object to None on error?
## This function tries to fix that.
def ImportGLTF(filePath="", fileName=""):
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

## Creates a collection with the specified name and links it in as a child of the top level collection
def CreateCollectionWithName(name="woof"):
    sceneCollection = bpy.context.scene.collection
    newCollection = bpy.data.collections.new(name) ## also available via bpy.data.collection[name]
    sceneCollection.children.link(newCollection) ## make the new collection visible
    return(newCollection)

def MoveObjectsBetweenCollections(objects, oldCollection, newCollection):
    for item in objects:
        newCollection.objects.link(item)
        oldCollection.objects.unlink(item)
        


## import an object
chest, status = ImportGLTF(filePath="C:\\temp", fileName="treasure_chest_4k.gltf")

## create a collection called "chest"
chestCollection = CreateCollectionWithName("Chest")

## put the imported chest into the chest collection
MoveObjectsBetweenCollections(chest, bpy.context.scene.collection, chestCollection)

## let's duplicate the imported chest and move the duplicates around.
bpy.ops.object.duplicate()
chest2 = bpy.context.selected_objects
bpy.ops.transform.translate(value=(2, 0, 0))
chest2Collection = CreateCollectionWithName("Chest2")
MoveObjectsBetweenCollections(chest2, chestCollection, chest2Collection)

