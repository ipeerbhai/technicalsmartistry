## This script imports/appends objects from blend files.

import bpy
import os

## blender is weird.  Blend files are really a directory system internally, put together into a package.
## So, you don't import blender objects -- you append or link them.

## But, to simplify, we're going to append
## also, blender doesn't return the object - it selects it.
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


