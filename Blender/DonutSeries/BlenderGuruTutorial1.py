## Basic navigation of API.

import bpy
import bgl
import blf
import mathutils
from math import *

## This script is a simple Q&A format for "how do I do X" type questions, where each "X" is one of the items from Blender Guru's video doing the same thing.

## How do I resize the initial cube?
##  "find it" to select/activate it
bpy.data.scenes['Scene'].objects.get('Cube').select_set(True)
##  call a resize function:
bpy.ops.transform.resize(value=(1,1.11,2))

## Note, blender has "scale" and "resize".  They are not the same.  "Scale" does not affect the root object, and "resize" does change the root object.

## How do I rotate the object 45 degrees (pi/4 radians) around the 'Z' axis?
bpy.ops.transform.rotate(value=pi/2, orient_axis='Z')

## How do I translate the object 10 units along the X axis?
bpy.ops.transform.translate(value=(10, 0, 0))
