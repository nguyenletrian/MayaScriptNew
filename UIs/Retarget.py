import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import pymel.core as pm

import importlib
import math
import json
from functools import partial

import NLTA_General,NLTA_Retarget, NLTA_UI
importlib.reload(NLTA_General)
importlib.reload(NLTA_Retarget)
importlib.reload(NLTA_UI)

### UIS
UIs = {}
def CreateUI(data):
    global UIs
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data)

    def GetObjName(obj):
        return(obj.split(":")[-1])

    def CreatePairItem(data):
        def DeletePairItem(ui,parentUI,*arr):
            UIs["pairs"] = [item for item in UIs["pairs"] if ui not in item]
            cmds.deleteUI(parentUI)
        ui = data["ui"]
        src = data["src"]
        des = data["des"]
        srcName = GetObjName(src)
        desName = GetObjName(des)
        parent = cmds.rowColumnLayout(numberOfColumns=9,parent=ui)

        srcUI = cmds.textField(placeholderText="Src Name",width=150,text=srcName)
        cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,srcUI),width=30,height=30)

        desUI = cmds.textField(placeholderText="Des Name",width=150,text=desName)
        cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,desUI),width=30)
        
        srcUI = cmds.textField(placeholderText="Src Name",width=150,text=srcName)
        cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,srcUI),width=30,height=30)
        
        desUI = cmds.textField(placeholderText="Des Name",width=150,text=desName)
        cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,desUI),width=30)

        cmds.button(label="X",c=partial(DeletePairItem,srcUI,parent),width=35)
        cmds.setParent("..")
        UIs["pairs"].append([srcUI,desUI])

    def CreateItemFromType(ui,type_,*arr):
        desNS = cmds.textField(UIs["desNS"],query=True,text=True)
        desRootName = cmds.textField(UIs["desRoot"],query=True,text=True)
        if desNS !="":
            desRoot = f"{desNS}:{desRootName}"
        else:
            desRoot = desRootName
        objs = NLTA_Retarget.GetChildren({"root":desRoot,"type":type_})#nurbsCurve
        if objs:
            NLTA_UI.ClearUI(ui)
            UIs["pairs"] = []
            for obj in objs:
                CreatePairItem({"src":obj,"des":"","ui":ui})

    def MatchSameName(*arr):
        for pair in UIs["pairs"]:
            srcValue = cmds.textField(pair[0],query=True,text=True)
            cmds.textField(pair[1],edit=True,text=srcValue)

  
    titles, buttons, inputs = [], [], []
    parent = data['parent']

    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)#*
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    titles.append(cmds.text(label=data['title']))

    cmds.rowColumnLayout(numberOfColumns=1)#+
    cmds.rowColumnLayout(numberOfColumns=1)#--


    #[
    cmds.rowColumnLayout(numberOfColumns=3)
    
    titles.append(cmds.text(label="Src NS",width=60))
    srcNS = cmds.textField(placeholderText="Source Namespace",width=200)
    inputs.append(srcNS)
    UIs["srcNS"] = srcNS
    buttons.append(cmds.button(label="->",c=partial(NLTA_UI.PickNamespace,srcNS),width=35))

    titles.append(cmds.text(label="Src Root"))
    srcRoot = cmds.textField(placeholderText="Source Root")
    UIs["srcRoot"] = srcRoot
    inputs.append(srcRoot)
    buttons.append(cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,srcRoot)))
    
    titles.append(cmds.text(label="Des NS"))
    desNS = cmds.textField(placeholderText="Destination Namespace")    
    inputs.append(desNS)
    UIs["desNS"] = desNS
    buttons.append(cmds.button(label="->",c=partial(NLTA_UI.PickNamespace,desNS),))

    titles.append(cmds.text(label="Des Root"))
    desRoot = cmds.textField(placeholderText="Destination Root")
    UIs["desRoot"] = desRoot
    inputs.append(desRoot)
    buttons.append(cmds.button(label="->",c=partial(NLTA_UI.PickObjectName,desRoot)))

    cmds.setParent("..")
    #]


    #[
    cmds.rowColumnLayout(numberOfColumns=3)

    UIs["scrollArea"] = cmds.scrollLayout(height=400,width=1000)#START SCROLL    
    listPair = cmds.rowColumnLayout(nc=1)
    cmds.setParent("..")
    cmds.setParent("..")#END SCROLL

    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="From control",c=partial(CreateItemFromType,listPair,"nurbsCurve")))
    buttons.append(cmds.button(label="From Joint",c=partial(CreateItemFromType,listPair,"joint")))
    buttons.append(cmds.button(label="Match Same name",c=partial(MatchSameName,)))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="From control",c=BakeAnimation))
    cmds.setParent("..")

    cmds.setParent("..")
    #]


    cmds.setParent("..")#--
    cmds.setParent("..")#-
    cmds.setParent("..")#*

    for title in titles:
        cmds.text(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)

### FUNCTIONS
def GetPairsName(*arr):
    returnData = []
    srcNS = cmds.textField(UIs["srcNS"],query=True,text=True)
    desNS = cmds.textField(UIs["desNS"],query=True,text=True)
    for pair in UIs["pairs"]:
        srcUI = pair[0]
        desUI = pair[1]
        srcText = cmds.textField(srcUI,query=True,text=True)
        desText = cmds.textField(desUI,query=True,text=True)                
        srcName = f"{srcNS}:{srcText}" if srcNS else srcText
        desName = f"{desNS}:{desText}" if desNS else desText
        returnData.append([srcName,desName])
    return(returnData)


def BakeAnimation(*arr):
    keyRange = NLTA_Retarget.GetAllTimes()
    pairs = GetPairsName()
    for time in keyRange:
        cmds.currentTime(time)
        for pair in pairs:
            NLTA_Retarget.BakeTransformSameKeys({
                "obj1":pair[0],
                "obj2":pair[1],
                "time":time    
            })
    


def BakeControlsToJoint(data):
    print(NLTA_Retarget.GetChildren({"root":"DeformationSystem","type":"joint"}))
    pass
    """
    data = {}
    data["srcNS"] = "Ref"
    data["srcRoot"] = "Rig"
    data["targetNS"] = "BakeAnimationJoints"
    data["targetRoot"] = "Rig"
    data["pairs"] = {
        "RigHips":["RigHips"]
    }

    srcNS = data["srcNS"]
    srcRoot = data["srcRoot"]
    srcRootName = f"{srcNS}:{srcRoot}"
    targetNS = data["targetNS"]
    targetRoot = data["targetRoot"]
    targetRootName = f"{targetNS}:{targetRoot}"

    try:
        cmds.delete(targetRootName)
    except:pass
    cmds.currentTime(0)
    NLTA_Retarget.HierarchyToJoints(srcRootName)

    pairs = data["pairs"]
    targetChilren =  cmds.listRelatives(targetRootName,ad=True)[::-1]
    targetChilren.insert(0,targetRootName)

    matchData = {}
    for targetChild in targetChilren:
        
        srcName = targetChild.split(":")[-1]
        srcNode = f"{srcNS}:{srcName}"
        matchData[targetChild] = NLTA_Retarget.RotateOrderConnect({
            "source":srcNode,
            "target":targetChild
        })
    
    cmds.autoKeyframe(state=False)

    keyRange = NLTA_Retarget.GetAllTimes()
    for time in keyRange:
        cmds.currentTime(time)
        for key in matchData:
            srcTemp = matchData[key]
            desTemp = key
            cmds.matchTransform(desTemp,srcTemp)
    """
    """
        for targetChild in targetChilren:
            name = targetChild.split(":")[-1]
            targetName = f"{targetNS}:{name}"
            srcName = f"{srcNS}:{name}"
            cmds.matchTransform(targetName,srcName)
            for key in pairs:
                targetName = f"{targetNS}:{key}"
                controls = pairs[key]
                for control in controls:
                    controlName = f"{srcNS}:{control}"
                    NLTA_Retarget.BakeTransfromKeys({
                        "obj1":controlName,
                        "obj2":targetName,
                        "time":time
                    })

    """
