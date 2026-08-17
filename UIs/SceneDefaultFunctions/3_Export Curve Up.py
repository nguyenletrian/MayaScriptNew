import os
import json
import maya.cmds as cmds
import pymel.core as pm

import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)

folder_temp = os.path.dirname(pm.sceneName())
if not folder_temp:
    folder_temp = pm.mel.eval("SaveSceneAs;")
folder_temp = os.path.dirname(pm.sceneName())
if folder_temp: 
    data_temp = {}
    selection = cmds.ls(selection=True, long=True)
    allAsCtrl = []
    if selection:
        for obj in selection:
            if cmds.nodeType(obj) == "transform":
                if cmds.listRelatives(obj, children=True, type="nurbsCurve"):
                    if obj not in allAsCtrl:
                        allAsCtrl.append(obj)
    else:
        allAsCtrlTemp = cmds.ls(type="nurbsCurve", ap=True)
        for a in allAsCtrlTemp:
            transformNode = cmds.listRelatives(a,parent=True,pa=True)[0]
            if transformNode not in allAsCtrl:
                allAsCtrl.append(transformNode)
    for ctrl in allAsCtrl:
        data_temp[ctrl] = {}
        data_temp[ctrl]["overrideEnabled"] = cmds.getAttr(ctrl+".overrideEnabled")
        data_temp[ctrl]["overrideRGBColors"] = cmds.getAttr(ctrl+".overrideRGBColors")
        data_temp[ctrl]["visibility"] = cmds.getAttr(ctrl+".visibility")
        if cmds.getAttr(ctrl+".overrideRGBColors") == 1:
            data_temp[ctrl]["overrideColorR"] = cmds.getAttr(ctrl+".drawOverride.overrideColorR")
            data_temp[ctrl]["overrideColorG"] = cmds.getAttr(ctrl+".drawOverride.overrideColorG")
            data_temp[ctrl]["overrideColorB"] = cmds.getAttr(ctrl+".drawOverride.overrideColorB")
        else:
            data_temp[ctrl]["overrideColor"] = cmds.getAttr(ctrl+".overrideColor")

        if cmds.listRelatives(ctrl,children=True,type="nurbsCurve"):
            curveData = {}
            for curveChild in cmds.listRelatives(ctrl,children=True,type="nurbsCurve",pa=True): 
                if "Orig" not in curveChild:
                    curveChildName = curveChild.split("|")[-1]
                    curveData[curveChildName] = {}
                    pointData = {}
                    for point in cmds.ls(curveChild+".controlPoints[*]",flatten=True):
                        if cmds.objExists(point):
                            pointName = point.split("|")[-1]
                            pointName = pointName.split(".")[-1]
                            pointData[pointName] = cmds.xform(point,q=True,os=True,t=True)
                    curveData[curveChildName]["pointData"] = pointData
                    curveData[curveChildName]["overrideEnabled"] = cmds.getAttr(curveChild+".overrideEnabled")
                    curveData[curveChildName]["overrideRGBColors"] = cmds.getAttr(curveChild+".overrideRGBColors")
                    curveData[curveChildName]["visibility"] = cmds.getAttr(curveChild+".visibility")
                    if cmds.getAttr(curveChild+".overrideRGBColors") == 1:
                        curveData[curveChildName]["overrideColorR"] = cmds.getAttr(curveChild+".drawOverride.overrideColorR")
                        curveData[curveChildName]["overrideColorG"] = cmds.getAttr(curveChild+".drawOverride.overrideColorG")
                        curveData[curveChildName]["overrideColorB"] = cmds.getAttr(curveChild+".drawOverride.overrideColorB")
                    else:
                        curveData[curveChildName]["overrideColor"] = cmds.getAttr(curveChild+".overrideColor")
            data_temp[ctrl]["curveData"] = curveData                    
        if ctrl == "HipSwinger_M":
            offsetGroup = cmds.listRelatives(ctrl,parent=True)[0]
            data_temp[ctrl]["translate"] = (
                cmds.getAttr(offsetGroup+".translateX"),
                cmds.getAttr(offsetGroup+".translateY"),
                cmds.getAttr(offsetGroup+".translateZ")
            )
    scene_path = pm.sceneName()
    if scene_path:
        charizard_folder = os.path.dirname(scene_path)
        work_folder = os.path.dirname(charizard_folder)
        scene_data_folder = os.path.join(work_folder, "SceneData")
        os.makedirs(scene_data_folder, exist_ok=True)
        file_path = os.path.join(scene_data_folder, "dataCurveShape.json")
        NLTA_General.writeJsonFile(file_path, data_temp)
        print("Url export: " + file_path)

