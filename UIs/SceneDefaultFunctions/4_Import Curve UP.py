import os
import maya.cmds as cmds
import pymel.core as pm
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

charizardFolder = os.path.dirname(scenePath)
workFolder = os.path.dirname(charizardFolder)

sceneDataFolder = os.path.join(workFolder, "SceneData")
filePath = os.path.join(sceneDataFolder, "dataCurveShape.json")


if not os.path.exists(filePath):
    cmds.warning("No SceneData found: " + filePath)

dataTemp = NLTA_General.readJsonFile(filePath)

for ctrl in dataTemp:

    if cmds.objExists(ctrl):

        ctrlData = dataTemp[ctrl]

        # controller attrs
        try:
            cmds.setAttr(ctrl + ".overrideEnabled", ctrlData["overrideEnabled"])
            cmds.setAttr(ctrl + ".overrideRGBColors", ctrlData["overrideRGBColors"])
        except:
            pass

        try:
            cmds.setAttr(ctrl + ".visibility", ctrlData["visibility"])
        except:
            pass

        if ctrlData.get("overrideRGBColors") == 1:

            try:
                cmds.setAttr(ctrl + ".drawOverride.overrideColorR", ctrlData["overrideColorR"])
                cmds.setAttr(ctrl + ".drawOverride.overrideColorG", ctrlData["overrideColorG"])
                cmds.setAttr(ctrl + ".drawOverride.overrideColorB", ctrlData["overrideColorB"])
            except:
                pass

        else:
            try:
                cmds.setAttr(ctrl + ".overrideColor", ctrlData["overrideColor"])
            except:
                pass
    if "curveData" in dataTemp[ctrl]:

        for curveChild in dataTemp[ctrl]["curveData"]:

            curveChildPath = ctrl + "|" + curveChild

            if cmds.objExists(curveChildPath):

                curveChildData = dataTemp[ctrl]["curveData"][curveChild]

                try:
                    cmds.setAttr(curveChildPath + ".overrideEnabled", curveChildData["overrideEnabled"])
                    cmds.setAttr(curveChildPath + ".overrideRGBColors", curveChildData["overrideRGBColors"])
                except:
                    pass

                try:
                    cmds.setAttr(curveChildPath + ".visibility", curveChildData["visibility"])
                except:
                    pass

                if curveChildData.get("overrideRGBColors"):

                    try:
                        cmds.setAttr(curveChildPath + ".drawOverride.overrideColorR", curveChildData["overrideColorR"])
                        cmds.setAttr(curveChildPath + ".drawOverride.overrideColorG", curveChildData["overrideColorG"])
                        cmds.setAttr(curveChildPath + ".drawOverride.overrideColorB", curveChildData["overrideColorB"])
                    except:
                        pass

                else:
                    try:
                        cmds.setAttr(curveChildPath + ".overrideColor", curveChildData["overrideColor"])
                    except:
                        pass
                for point in curveChildData["pointData"]:

                    pointPath = curveChildPath + "." + point

                    if cmds.objExists(pointPath):

                        cmds.xform(
                            pointPath,
                            os=True,
                            t=curveChildData["pointData"][point]
                        )

print("Loaded Curve Shape from:", filePath)