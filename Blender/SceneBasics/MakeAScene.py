## This script makes a scene of a house in an hdr with a treasure chest inside.

## Import my scene library to do some of the work.
import importlib.util
import sys

file_path = "C:/github/technicalsmartistry/Blender/SceneBasics/ImranSceneLib.py"
module_name = "ImranSceneLib"

spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

import ImranSceneLib as im
import pdb

## Setup an importer and import the house, HDR, and treasure chest into the scene
importer = im.Importers()
chest, chestErr = importer.ImportGLTF("C:\\temp\\furniture\\chest", "treasure_chest_4k.gltf")
pdb.set_trace()
house, houseErr = importer.ImportFromBlendFile(blendFile="C:\\temp\\buildings", objectName="Cottage_FREE")
importer.ImportHDRorEXRIntoWorld("C:\\temp\\EXRs\\je_gray_park_4k.hdr")

