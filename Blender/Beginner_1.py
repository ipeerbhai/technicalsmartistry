import bpy
import bgl
import blf
import mathutils

#PYTHON INTERACTIVE CONSOLE 3.9.7 (default, Oct 11 2021, 19:31:28) [MSC v.1916 64 bit (AMD64)]

#Builtin Modules:       bpy, bpy.data, bpy.ops, bpy.props, bpy.types, bpy.context, bpy.utils, bgl, blf, mathutils
#Convenience Imports:   from mathutils import *; from math import *
#Convenience Variables: C = bpy.context, D = bpy.data

C = bpy.context
D = bpy.data

## How do I resize the initial cube?
##  "find it" to select/activate it
bpy.data.scenes['Scene'].objects.get('Cube').select_set(True)

##  call a resize function:
bpy.ops.transform.resize(value=(1,1.11,2))

## Note, blender has "scale" and "resize".  They are not the same.  "Scale" does not affect the root object, and "resize" does change the root object.

## now, let's rotate the object 90 degrees (pi/2 radians) around Z
bpy.ops.transform.rotate(value=pi/2, orient_axis='Z')

## now, let's translate the object 10 units along the X axis
bpy.ops.transform.translate(value=(10, 0, 0))

