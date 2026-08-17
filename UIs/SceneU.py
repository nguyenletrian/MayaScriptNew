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

sceneDataFolder = ("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])+ "/SceneData/"
sceneDataPath = os.path.join(sceneDataFolder,"ScenePatternData.json")


ITEMS_PATTERN = {"items":{},"order":[]}
ITEMS = {}
sceneData = {}

def CreateUI(data):  
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data) 

    titles, buttons, inputs = [], [], []
    parent = data['parent']
    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)#*
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    titles.append(cmds.textField(text=data['title'],editable=False))    


    cmds.rowColumnLayout(nc=1)
    cmds.textField(text="Default Functions",editable=False)
    cmds.rowColumnLayout(nc=2)#<
    defaultFunctionsList = cmds.rowColumnLayout(numberOfColumns=4,width=420)

    cmds.setParent("..")    
    cmds.rowColumnLayout(nc=1)
    buttons.append(cmds.button(label="+",bgc=(0.0, 0.4, 0.0),width=40,c=partial(CreateFunction,defaultFunctionsFolder,defaultFunctionsList)))
    cmds.setParent("..")
    cmds.setParent("..")#>
    cmds.setParent("..")


    cmds.rowColumnLayout(nc=1)
    cmds.textField(text="Project Functions",editable=False)
    cmds.rowColumnLayout(nc=2)#<
    projectFunctionsList = cmds.rowColumnLayout(numberOfColumns=4,width=420)
    cmds.setParent("..")

    cmds.rowColumnLayout(nc=1)
    buttons.append(cmds.button(label="+",bgc=(0.0, 0.4, 0.0),width=40,c=partial(CreateFunction,projectPath,projectFunctionsList)))
    cmds.setParent("..")#>
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.scrollLayout(horizontalScrollBarThickness=4,h=400,width=480)
    mainUI = cmds.rowColumnLayout("mainUI",numberOfColumns=1)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")
    
    cmds.rowColumnLayout(nc=1)
    cmds.textField(text="Current Pattern",editable=False)
    patternListCurrent = cmds.rowColumnLayout(numberOfColumns=5)
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(nc=1)
    cmds.textField(text="Up Pattern",editable=False)
    patternListUp = cmds.rowColumnLayout(numberOfColumns=5)
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.setParent("..")
    cmds.setParent("..")
      
    for title in titles:
        cmds.textField(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)
    SceneLoad(mainUI)
    FunctionsLoad(defaultFunctionsFolder,defaultFunctionsList)
    FunctionsLoad(projectPath,projectFunctionsList)
    PatternLoad(patternListCurrent,mainUI,sceneDataFolder)

def SceneLoad(ui, *arr):
    NLTA_UI.ClearUI(ui)
    if not cmds.file(q=True, sn=True):
        return
    if not os.path.exists(sceneDataPath):
        NLTA_General.writeJsonFile(sceneDataPath, [])
    dataTemp = NLTA_General.readJsonFile(sceneDataPath) or []
    for item in sorted(dataTemp, key=lambda x: x["order"]):
        AddItem(item["moduleName"],item["path"],ui, item)

def PatternLoad(ui,mainUI,path,*arr):
    NLTA_UI.ClearUI(ui)
    prefix = "Scene_Pattern_"
    patterns = {
        "SingleScript":"Single Script",
        "Global":"Global",
        "DefaultValue":"Default Value",
        "SpaceSwitch":"Space Switch",
        "Visibility":"Visibility",
        "Layer":"Layer",        
        "ControlShape":"Control Shape",
        "DefaultSwitchIKFK":"Switch IK/FK",
        "NewSwitchIKFK":"Switch IK/FK New",        
        "Drivenkey":"Driven Key",        
        "ModuloSDK":"Modulo SDK",        
        "ProxyAttribute":"Proxy Attribute",
        "Rivet":"Rivet",
        "Rename":"Rename",
        "GradientTexture":"Gradient Texture",
        "RopeStraight":"Rope Straight",
        "RopeRoll":"Rope Roll",
        "AimConstraint":"AimConstraint",
        "OrientConstraint":"Orient Constraint",
        "Group":"Empty Group",
        "ClearOffset":"Clear Offset",
        "CreateRef":"Create Ref",
        "ReplacePath":"Replace Path",
        "Note":"Note",
        "TransferAttribute":"Transfer Attribute",
        "RenameAttribute":"Rename Attribute",
        "UnlockAttribute":"Unlock Attribute",
        "Delete":"Delete",
    }
    for pattern in patterns:
        moduleName = prefix+pattern
        if cmds.window(moduleName, exists=True):
            cmds.deleteUI(moduleName)
        cmds.button(label=patterns[pattern],width=95,height=30,c=partial(AddItem,moduleName,path,mainUI,{}),parent=ui)

def FunctionsLoad(folder,ui,*arr):
    NLTA_UI.ClearUI(ui)
    fileArrays = NLTA_General.GetFiles(folder,"py")
    for fileTemp in fileArrays:
        btn = cmds.button(label=fileTemp.split("_")[-1],width=105,height=30,c=partial(NLTA_General.RunScriptFile,folder+fileTemp+'.py'),parent=ui)
        popup = cmds.popupMenu(parent=btn)
        cmds.menuItem(label="Edit File", parent=popup,c=partial(NLTA_General.OpenSublime,folder+fileTemp+'.py'))

def AddItem(moduleName,path,ui,data,*arr):
    global sceneData

    def OpenItem(defaultSetting,*arr):
        module.Form(defaultSetting)

    def ChangeOrder(orderUI,data,*arr):
        value = cmds.intField(orderUI,query=True,value=True)
        NLTA_General.JsonUpdateByID({
            "id":data["id"],
            "path":sceneDataPath,
            "values":{
                "order":value
            }
        })

    def DeleteItem(ui, *arr):
        cmds.deleteUI(ui)
        itemID = sceneData[ui]['id']
        del sceneData[ui]
        sceneDatas = NLTA_General.readJsonFile(sceneDataPath) or []
        sceneDatas = [
            data for data in sceneDatas
            if data.get('id') != itemID
        ]
        NLTA_General.writeJsonFile(sceneDataPath, sceneDatas)

    def ChangeNote(noteUI,defaultSetting,*arr):
        value = cmds.scrollField(noteUI,query=True,text=True)
        NLTA_General.JsonUpdateByID({
            "id":defaultSetting["id"],
            "path":sceneDataPath,
            "values":{
                "name":value
            }
        })

    def RunItem(defaultSetting,*arr):
        module.Run(defaultSetting)
    
    module = NLTA_General.LoadModule(moduleName)

    if data!= {}: 
        defaultSetting = data
    else:        
        defaultSetting = module.DefaultSetting(path)
        NLTA_General.JsonAdd({
            "path":sceneDataPath,
            "values":defaultSetting
        })
    
    defaultSetting["sceneDataPath"] = sceneDataPath
    defaultSetting["SceneLoadFunction"] = SceneLoad
    defaultSetting["SceneLoadUI"] = ui

    if moduleName != "Scene_Pattern_Note":
        itemUI = cmds.rowColumnLayout(numberOfColumns=4,parent=ui)
        cmds.button(label="Run",c=partial(RunItem,defaultSetting),width=40,bgc=(0.0, 0.4, 0.0),height=35)    
        textShow = cmds.button(label=defaultSetting['name'],c=partial(OpenItem,defaultSetting),width=330)
        orderUI = cmds.intField(value=defaultSetting['order'],width=50)
        cmds.button(label="X",c=partial(DeleteItem,itemUI),width=40,bgc=(0.4, 0.0, 0.0))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,defaultSetting),ec=partial(ChangeOrder,orderUI,defaultSetting),edit=True)    
        cmds.setParent('..')
    else: 
        itemUI = cmds.rowColumnLayout(numberOfColumns=4,parent=ui)
        cmds.textField(text="###",width=40)
        textShow = cmds.scrollField(text=defaultSetting['name'],width=330,height=60)
        orderUI = cmds.intField(value=defaultSetting['order'],width=50)
        cmds.button(label="X",c=partial(DeleteItem,itemUI),width=40,bgc=(0.4, 0.0, 0.0))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,defaultSetting),ec=partial(ChangeOrder,orderUI,defaultSetting),edit=True)   
        cmds.scrollField(textShow,cc=partial(ChangeNote,textShow,defaultSetting),ec=partial(ChangeNote,textShow,defaultSetting),edit=True) 
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



