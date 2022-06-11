## This script makes a scene of a house in an hdr with a treasure chest inside.

## Import my scene library to do some of the work.
import importlib.util
import sys
from inspect import getsourcefile
from os.path import abspath
import os
import pdb

github_drive = "f"
file_path = github_drive + ":/github/technicalsmartistry/Blender/SceneBasics/ImranSceneLib.py"
module_name = "ImranSceneLib"


spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

import ImranSceneLib as im

## Setup an importer and import the house, HDR, and treasure chest into the scene
importer = im.Importers()
chest, chestErr = importer.ImportGLTF("C:\\temp\\AssetLibrary\\furniture\\chest", "treasure_chest_4k.gltf")
house, houseErr = importer.ImportFromBlendFile(blendFile="C:\\temp\\AssetLibrary\\buildings\\Cottage_FREE.blend", objectName="Cottage_Free")
importer.ImportHDRorEXRIntoWorld("C:\\temp\\AssetLibrary\\EXRs\\je_gray_park_4k.hdr")

