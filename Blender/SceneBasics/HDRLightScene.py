## this script loads an EXF/HDR as the lighting / background setup.

import bpy
import bmesh
import mathutils
import pdb
import math
import operator
import numpy as np



### Basic -- load an EXR

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
node_environment.image = bpy.data.images.load("F:/github/technicalsmartistry/Blender/SceneBasics/amphitheatre_zanzibar_fort_4k.exr")

### Advanced -- change the XYZ position of the EXR
node_vector = tree_nodes.new(type='ShaderNodeMapping')
node_vector.location = -500, 0 ## this is the location of the node in the node graph, not the input location!!!!

## to set the vector node's input properties, we refer to it by array positions.  So Input[0][0] is the "vector" 0,0 in the input set.
node_vector.inputs['Location'].default_value[0] = 0 ## X position
node_vector.inputs['Location'].default_value[1] = 0 ## Y position
node_vector.inputs['Location'].default_value[2] = 0 ## Z position

## link up the new vector node
link = links.new(node_vector.outputs["Vector"], node_environment.inputs["Vector"])

## add a texture coordinate node and link its generated to the vector mapping input vector ( or else the vector mapping node does not work )
node_textcoord = tree_nodes.new(type='ShaderNodeTexCoord')
node_textcoord.location = -700, 0
link = links.new(node_textcoord.outputs["Generated"], node_vector.inputs["Vector"])
