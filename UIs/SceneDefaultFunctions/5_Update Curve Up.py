import os
import maya.cmds as cmds
import pymel.core as pm
import json
import importlib

import NLTA_General

for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)

scenePath = pm.sceneName()
if not scenePath:
    pm.mel.eval("SaveSceneAs;")
    scenePath = pm.sceneName()

scenePath = pm.sceneName()
charizardFolder = os.path.dirname(scenePath)
workFolder = os.path.dirname(charizardFolder)
sceneDataFolder = os.path.join(workFolder, "SceneData")
file_path = os.path.join(sceneDataFolder, "dataCurveShape.json")

# CREATE FOLDER
if not os.path.exists(sceneDataFolder):
    os.makedirs(sceneDataFolder)

# LOAD OLD DATA
oldData = {}
if os.path.exists(file_path):
    oldData = NLTA_General.readJsonFile(file_path) or {}

# GET CONTROLS
selection = cmds.ls(sl=True, long=True)
allAsCtrl = []

if selection:
    for obj in selection:
        if cmds.nodeType(obj) == "transform":
            if cmds.listRelatives(obj, c=True, type="nurbsCurve"):
                if obj not in allAsCtrl:
                    allAsCtrl.append(obj)
else:
    for shape in cmds.ls(type="nurbsCurve", ap=True):
        ctrl = cmds.listRelatives(shape, p=True, pa=True)[0]
        if ctrl not in allAsCtrl:
            allAsCtrl.append(ctrl)

# BUILD NEW DATA
newData = {}

for ctrl in allAsCtrl:

    newData[ctrl] = {}

    newData[ctrl]["overrideEnabled"] = cmds.getAttr(ctrl + ".overrideEnabled")
    newData[ctrl]["overrideRGBColors"] = cmds.getAttr(ctrl + ".overrideRGBColors")
    newData[ctrl]["visibility"] = cmds.getAttr(ctrl + ".visibility")

    if cmds.getAttr(ctrl + ".overrideRGBColors"):
        newData[ctrl]["overrideColorR"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorR")
        newData[ctrl]["overrideColorG"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorG")
        newData[ctrl]["overrideColorB"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorB")
    else:
        newData[ctrl]["overrideColor"] = cmds.getAttr(ctrl + ".overrideColor")

    # CURVE DATA
    curveData = {}

    shapes = cmds.listRelatives(ctrl, c=True, type="nurbsCurve", pa=True) or []

    for shape in shapes:

        if "Orig" in shape:
            continue

        shapeName = shape.split("|")[-1]

        curveData[shapeName] = {}

        pointData = {}

        for p in cmds.ls(shape + ".controlPoints[*]", fl=True):
            if cmds.objExists(p):
                pointName = p.split(".")[-1]
                pointData[pointName] = cmds.xform(p, q=True, os=True, t=True)

        curveData[shapeName]["pointData"] = pointData
        curveData[shapeName]["overrideEnabled"] = cmds.getAttr(shape + ".overrideEnabled")
        curveData[shapeName]["overrideRGBColors"] = cmds.getAttr(shape + ".overrideRGBColors")
        curveData[shapeName]["visibility"] = cmds.getAttr(shape + ".visibility")

        if cmds.getAttr(shape + ".overrideRGBColors"):
            curveData[shapeName]["overrideColorR"] = cmds.getAttr(shape + ".drawOverride.overrideColorR")
            curveData[shapeName]["overrideColorG"] = cmds.getAttr(shape + ".drawOverride.overrideColorG")
            curveData[shapeName]["overrideColorB"] = cmds.getAttr(shape + ".drawOverride.overrideColorB")
        else:
            curveData[shapeName]["overrideColor"] = cmds.getAttr(shape + ".overrideColor")

    newData[ctrl]["curveData"] = curveData

    # special case
    if ctrl == "HipSwinger_M":
        parent = cmds.listRelatives(ctrl, p=True)[0]
        newData[ctrl]["translate"] = cmds.getAttr(parent + ".translate")[0]

# MERGE OLD + NEW
for ctrl in newData:
    oldData[ctrl] = newData[ctrl]

# SAVE
NLTA_General.writeJsonFile(file_path, oldData)

print("Updated Curve Shape:", file_path)