## this script loads a GLTF model complete with textures into the scene.

import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np


## importing doesn't give you the objects imported -- you need to plan for that a little bit

def ImportGLTF(file=""):
    resultStatus = bpy.ops.import_scene.gltf(file, files=[{"name":"treasure_chest_4k.gltf", "name":"treasure_chest_4k.gltf"}], loglevel=50)





chest = bpy.ops.import_scene.gltf(filepath="C:/github/technicalsmartistry/Blender/SceneBasics/treasure_chest_4k.gltf", files=[{"name":"treasure_chest_4k.gltf", "name":"treasure_chest_4k.gltf"}], loglevel=50)

