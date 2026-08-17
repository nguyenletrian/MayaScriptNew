import os
import maya.cmds as cmds
import pymel.core as pm

import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)

folderTemp = os.path.dirname(pm.sceneName())
if not folderTemp:
    folderTemp = pm.mel.eval("SaveSceneAs;")
if folderTemp:
    folderTemp = os.path.dirname(pm.sceneName())+"/SceneData"
    filePath = folderTemp+"/dataCurveShape.json"
    print(filePath)
    if os.path.exists(filePath):
        dataTemp = NLTA_General.readJsonFile(filePath)
        for ctrl in dataTemp:
            if cmds.objExists(ctrl):
                try:
                    cmds.setAttr(ctrl+".overrideEnabled",dataTemp[ctrl]["overrideEnabled"])
                    cmds.setAttr(ctrl+".overrideRGBColors",dataTemp[ctrl]["overrideRGBColors"])
                except:pass
                try:
                    cmds.setAttr(ctrl+".visibility",dataTemp[ctrl]["visibility"])
                except:pass
                if dataTemp[ctrl]["overrideRGBColors"] == 1:
                    cmds.setAttr(ctrl+".drawOverride.overrideColorR",dataTemp[ctrl]["overrideColorR"])
                    cmds.setAttr(ctrl+".drawOverride.overrideColorG",dataTemp[ctrl]["overrideColorG"])
                    cmds.setAttr(ctrl+".drawOverride.overrideColorB",dataTemp[ctrl]["overrideColorB"])
                else:
                    try:
                        cmds.setAttr(ctrl+".overrideColor",dataTemp[ctrl]["overrideColor"])
                    except:pass
            if dataTemp[ctrl]["curveData"]:
                for curveChild in dataTemp[ctrl]["curveData"]:
                    curveChildPath = ctrl+"|"+curveChild
                    if cmds.objExists(curveChildPath):
                        curveChildData = dataTemp[ctrl]["curveData"][curveChild]
                        try:                  
                            cmds.setAttr(curveChildPath+".overrideEnabled",curveChildData["overrideEnabled"])
                            cmds.setAttr(curveChildPath+".overrideRGBColors",curveChildData["overrideRGBColors"])
                        except:pass
                        try:
                            cmds.setAttr(curveChildPath+".visibility",curveChildData["visibility"])
                        except:pass
                        if curveChildData["overrideRGBColors"] == True:
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorR",curveChildData["overrideColorR"])
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorG",curveChildData["overrideColorG"])
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorB",curveChildData["overrideColorB"])
                        else:
                            try:
                                cmds.setAttr(curveChildPath+".overrideColor",curveChildData["overrideColor"])
                            except:pass
                        for point in curveChildData["pointData"]:
                            pointPath = curveChildPath+"."+point
                            if cmds.objExists(pointPath):
                                cmds.xform(pointPath,q=True,os=True,t=True)
                                cmds.xform(pointPath,os=True, translation=curveChildData["pointData"][point])


