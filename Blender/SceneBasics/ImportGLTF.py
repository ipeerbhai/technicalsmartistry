## this script loads a GLTF model complete with textures into the scene.

import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np


bpy.ops.import_scene.gltf(filepath="C:/github/technicalsmartistry/Blender/SceneBasics/treasure_chest_4k.gltf", files=[{"name":"treasure_chest_4k.gltf", "name":"treasure_chest_4k.gltf"}], loglevel=50)

