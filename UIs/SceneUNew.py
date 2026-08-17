import maya.cmds as cmds
import importlib
import os
import sys
import subprocess
import pymel.core as pm
from functools import partial


import NLTA_General, NLTA_UI
for module in [NLTA_General,NLTA_UI]:
    try:
        importlib.reload(module)
    except:
        reload(module)


currentFile = os.path.abspath(__file__)
currentFolder = os.path.dirname(currentFile)
for folder in ["ScenePattern","SceneDefaultFunctions"]:
    folderTemp = os.path.join(currentFolder,folder)
    if folderTemp not in sys.path:
        sys.path.insert(0, folderTemp)


defaultFunctionsFolder = os.path.join(currentFolder,"SceneDefaultFunctions")+"/"
scenePatternFolder = os.path.join(currentFolder,"ScenePattern")+"/"
projectPath =  NLTA_General.GetProjectFunctionPath()
if not projectPath:
    print("#### Please save the scene!~")

upDataFolder = ("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])+ "/SceneData/"
currentDataFolder = ("/").join(os.path.dirname(pm.sceneName()).split('/'))+ "/SceneData/"

patterns = {
    "Scene_Pattern_SingleScript":"Single Script",
    "Scene_Pattern_Global":"Global",
    "Scene_Pattern_SpaceSwitch":"Space Switch",
    "Scene_Pattern_Visibility":"Visibility",
    "Scene_Pattern_VisibilitySwitch":"Visibility Switch",
    "Scene_Pattern_VisibilityToggle":"Visibility Toggle",
    "Scene_Pattern_Layer":"Layer",        
    "Scene_Pattern_ControlShape":"Control Shape",
    "Scene_Pattern_ControlShapeAS":"AS Control Shape",
    "Scene_Pattern_DefaultSwitchIKFK":"Switch IK/FK",
    "Scene_Pattern_NewSwitchIKFK":"Switch IK/FK New",        
    "Scene_Pattern_Drivenkey":"Driven Key",        
    "Scene_Pattern_ModuloSDK":"Modulo SDK",
    "Scene_Pattern_ModuloSDKNew":"Modulo SDK New",
    "Scene_Pattern_DefaultValue":"Default Value",
    "Scene_Pattern_TransferAttribute":"Transfer Attribute",
    "Scene_Pattern_RenameAttribute":"Rename Attribute",
    "Scene_Pattern_UnlockAttribute":"Unlock Attribute",
    "Scene_Pattern_ProxyAttribute":"Proxy Attribute",
    "Scene_Pattern_CreateAttribute":"Create Attribute",
    "Scene_Pattern_DeleteAttribute":"Delete Attribute",
    "Scene_Pattern_Rivet":"Rivet",
    "Scene_Pattern_Rename":"Rename",
    "Scene_Pattern_GradientTexture":"Gradient Texture",
    "Scene_Pattern_RopeStraight":"Rope Straight",
    "Scene_Pattern_RopeRoll":"Rope Roll",
    "Scene_Pattern_AimConstraint":"AimConstraint",
    "Scene_Pattern_OrientConstraint":"Orient Constraint",    
    "Scene_Pattern_ClearOffset":"Clear Offset",
    "Scene_Pattern_CreateRef":"Create Ref",
    "Scene_Pattern_CreateCurve":"Create Curve",
    "Scene_Pattern_Group":"Create Group",
    "Scene_Pattern_CreateOffset":"Create Offset",
    "Scene_Pattern_CreateIK":"Create IK",
    "Scene_Pattern_ReplacePath":"Replace Path",
    "Scene_Pattern_Note":"Note",
    "Scene_Pattern_Delete":"Delete",
    "Scene_Pattern_SplineRig":"Spline Rig",
    "Scene_Pattern_SplineCurveFromObjs":"Spline Curve From Objs",
    "Scene_Pattern_SplineControlFromObjs":"Spline Controls From Objs",
    "Scene_Pattern_FoldRig":"Fold Rig",
    "Scene_Pattern_DeformSine":"Deform Sine",
    "Scene_Pattern_DeformSineForControls":"Deform Sine For Controls",
    "Scene_Pattern_MatchPairs":"Match Pairs",
    "Scene_Pattern_BSSequenceFromObjKeys":"BS Sequel from obj keys",
    "Scene_Pattern_MeshVertex":"Mesh Vertex",
    "Scene_Pattern_TransformBackup":"Transform Backup",
    "Scene_Pattern_AnimationBackup":"Animation Backup",
    "Scene_Pattern_SkinJointToNearestComponent":"Skin joint to nearest component",
}


ITEMS_PATTERN = {"items":{},"order":[]}
ITEMS = {}
sceneData = {}

def CreateUI(data):
    global upList
    global currentList
    def GetModuleName(ui,*arr):
        label = cmds.menuItem(ui, q=True, label=True)
        return(next(k for k, v in patterns.items() if v == label))

    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data) 

    for key in patterns:
        if cmds.window(key, exists=True):
            cmds.deleteUI(key)

    titles, buttons, inputs = [], [], []
    parent = data['parent']
    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)#*
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    titles.append(cmds.textField(text=data['title'],editable=False))    

    cmds.rowColumnLayout(nc=1)
    cmds.textField(text="Project Functions",editable=False)
    cmds.rowColumnLayout(nc=2)#<
    projectFunctionsList = cmds.rowColumnLayout(numberOfColumns=4,width=420)
    cmds.setParent("..")
    cmds.rowColumnLayout(nc=1)
    buttons.append(cmds.button(label="+",bgc=(0.0, 0.4, 0.0),width=40,c=partial(CreateFunction,projectPath,projectFunctionsList)))
    cmds.setParent("..")#>
    cmds.setParent("..")
    FunctionsLoad(projectPath,projectFunctionsList)

    cmds.rowColumnLayout(nc=1)
    cmds.rowColumnLayout(nc=1)

    patternsUI = cmds.optionMenu(width=460)
    for key, value in patterns.items():
        cmds.menuItem(label=value)
    cmds.setParent("..")
    cmds.rowColumnLayout(nc=2)
    buttons.append(cmds.button("AddUpItem",label="Up Level",width=230))
    buttons.append(cmds.button("AddCurrentItem",label="Current",width=230))    
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=2)#<
    # UP LIST
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.scrollLayout(horizontalScrollBarThickness=4,h=650,width=240)
    upList = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")
    # CURRENT LIST
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.scrollLayout(horizontalScrollBarThickness=4,h=650,width=240)
    currentList = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")#>

    cmds.button("AddCurrentItem",edit=True,c=partial(
        AddNewItem,
        patternsUI,
        currentDataFolder,
        currentList,
    ))

    cmds.button("AddUpItem",edit=True,c=partial(
        AddNewItem,
        patternsUI,
        upDataFolder,
        upList,
    ))
      
    for title in titles:
        cmds.textField(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)

    SceneLoad(currentList,currentDataFolder)
    SceneLoad(upList,upDataFolder)

def SceneLoad(ui,folderPath, *arr):
    filePath = folderPath+"/ScenePatternData.json"
    if not os.path.exists(filePath):
        NLTA_General.writeJsonFile(filePath, [])
    dataTemp = NLTA_General.readJsonFile(filePath) or []
    if dataTemp:
        NLTA_UI.ClearUI(ui)
        for item in sorted(dataTemp, key=lambda x: x["order"]):
            AddItem(item["moduleName"],folderPath,ui,item)

def FunctionsLoad(folder,ui,*arr):
    if folder:
        NLTA_UI.ClearUI(ui)
        fileArrays = NLTA_General.GetFiles(folder,"py")
        if fileArrays:
            for fileTemp in fileArrays:
                btn = cmds.button(label=fileTemp.split("_")[-1],width=105,height=30,c=partial(NLTA_General.RunScriptFile,folder+fileTemp+'.py'),parent=ui)
                popup = cmds.popupMenu(parent=btn)
                cmds.menuItem(label="Edit File", parent=popup,c=partial(NLTA_General.OpenSublime,folder+fileTemp+'.py'))

def AddNewItem(patternsUI,dataFolder,listUI,*arr):
    patternText = cmds.optionMenu(patternsUI,query=True,value=True)
    moduleName = next((k for k, v in patterns.items() if v == patternText), None)
    AddItem(moduleName,dataFolder,listUI,{})


def AddItem(moduleName,dataFolder,ui,data,*arr):
    global sceneData

    def OpenItem(defaultSetting,*arr):
        module.Form(defaultSetting)

    def ChangeOrder(orderUI,data,dataFile,*arr):
        value = cmds.intField(orderUI,query=True,value=True)
        NLTA_General.JsonUpdateByID({
            "id":data["id"],
            "path":dataFile,
            "values":{
                "order":value
            }
        })

    def DeleteItem(ui,path, *arr):
        cmds.deleteUI(ui)
        itemID = sceneData[ui]['id']
        sceneDatas = NLTA_General.readJsonFile(path) or []        
        del sceneData[ui]        
        returnData = []
        for data in sceneDatas:
            if data.get('id') != itemID:
                returnData.append(data)
        NLTA_General.writeJsonFile(path,returnData)

    def ChangeNote(noteUI,defaultSetting,dataFile,*arr):
        value = cmds.scrollField(noteUI,query=True,text=True)
        NLTA_General.JsonUpdateByID({
            "id":defaultSetting["id"],
            "path":dataFile,
            "values":{
                "name":value
            }
        })

    def ChangeLevel(ui, dataFile, *arr):
        ID = sceneData[ui]['id']
        sourceDatas = NLTA_General.readJsonFile(dataFile) or []
        for data in sourceDatas[:]:
            if data["id"] == ID:
                if upDataFolder in dataFile:
                    targetFile = currentDataFolder + "/ScenePatternData.json"
                else:
                    targetFile = upDataFolder + "/ScenePatternData.json"
                targetDatas = NLTA_General.readJsonFile(targetFile) or []
                targetDatas.append(data)
                sourceDatas.remove(data)
                break
        NLTA_General.writeJsonFile(dataFile, sourceDatas)
        NLTA_General.writeJsonFile(targetFile, targetDatas)
        SceneLoad(upList,upDataFolder)
        SceneLoad(currentList,currentDataFolder)


    def RunItem(defaultSetting,*arr):
        module.Run(defaultSetting)

    module = NLTA_General.LoadModule(moduleName)
    dataFile =  dataFolder + "/ScenePatternData.json"

    if data!= {}: 
        defaultSetting = data
    else:        
        defaultSetting = module.DefaultSetting(dataFolder)
        NLTA_General.JsonAdd({
            "path":dataFile,
            "values":defaultSetting
        })

    defaultSetting["sceneDataPath"] = dataFolder
    defaultSetting["SceneLoadFunction"] = SceneLoad
    defaultSetting["SceneLoadUI"] = ui
    if moduleName != "Scene_Pattern_Note":
        itemUI = cmds.rowColumnLayout(numberOfColumns=5,parent=ui)
        cmds.button(label="->",c=partial(RunItem,defaultSetting),bgc=(0.0, 0.4, 0.0),width=25,height=25)    
        textShow = cmds.button(label=defaultSetting['name'],c=partial(OpenItem,defaultSetting),width=125)
        orderUI = cmds.intField(value=defaultSetting['order'],width=30)
        cmds.button(label="X",c=partial(DeleteItem,itemUI,dataFile),width=25,bgc=(0.4, 0.0, 0.0))
        cmds.button(label="<->",c=partial(ChangeLevel,itemUI,dataFile),width=25,bgc=(0.0, 0.3, 0.3))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,defaultSetting,dataFile),ec=partial(ChangeOrder,orderUI,defaultSetting,dataFile),edit=True)    
        cmds.setParent('..')
    else: 
        itemUI = cmds.rowColumnLayout(numberOfColumns=4,parent=ui)
        cmds.textField(text="###",width=25)
        textShow = cmds.scrollField(text=defaultSetting['name'],width=125,height=25)
        orderUI = cmds.intField(value=defaultSetting['order'],width=30)
        cmds.button(label="X",c=partial(DeleteItem,itemUI,dataFile),width=25,bgc=(0.4, 0.0, 0.0))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,defaultSetting,dataFile),ec=partial(ChangeOrder,orderUI,defaultSetting,dataFile),edit=True)   
        cmds.scrollField(textShow,cc=partial(ChangeNote,textShow,defaultSetting,dataFile),ec=partial(ChangeNote,textShow,defaultSetting,dataFile),edit=True) 
        cmds.setParent('..')
    sceneData[itemUI] = defaultSetting


def CreateFunction(folder,ui, *args):
    result = cmds.promptDialog(
        title='Create Python File',
        message='File Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if result != 'OK':
        return
    fileName = cmds.promptDialog(q=True, text=True).strip()
    if not fileName:
        cmds.warning("Please enter a file name.")
        return
    if not fileName.endswith(".py"):
        fileName += ".py"
    if not os.path.exists(folder):
        os.makedirs(folder)
    filePath = os.path.join(folder, fileName)
    if not os.path.exists(filePath):
        with open(filePath, "w") as f:
            f.write(
'''# -*- coding: utf-8 -*-

def Run(*args):
    pass
'''
            )
    NLTA_General.OpenSublime(filePath)
    FunctionsLoad(folder,ui)
    return filePath



