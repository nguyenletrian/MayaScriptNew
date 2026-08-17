#Nguyen Le Tri An
import maya.cmds as cmds
import importlib
import os
import sys
import subprocess
import pymel.core as pm
from functools import partial



import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)

sceneData = {}
scenePath = "SceneData.json"
patternData = {
    'UpPostScript':{
        'type':type,
        'function':'SingleScriptRun',
        'form':'SingleScriptForm',
        'name':"Up P-Script",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])+'/PostScript.py',
        'order':0,
    },
    'CurrentPostScript':{
        'type':type,
        'function':'SingleScriptRun',
        'form':'SingleScriptForm',
        'name':"Current P-Script",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/PostScript.py',
        'order':0,
    },
    'UpAfterScript':{
        'type':type,
        'function':'SingleScriptRun',
        'form':'SingleScriptForm',
        'name':"Up A-Script",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])+'/AfterScript.py',
        'order':0,
    },
    'CurrentAfterScript':{
        'type':type,
        'function':'SingleScriptRun',
        'form':'SingleScriptForm',
        'name':"Current A-Script",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/AfterScript.py',
        'order':0,
    },
    'Visibility':{
        'type':type,
        'function':'VisibilityRun',
        'form':'VisibilityForm',
        'name':"Visibility",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/Visibility.py',
        'order':0,
    },
    'DefaultValue':{
        'type':type,
        'function':'DefaultValueRun',
        'form':'DefaultValueForm',
        'name':"Default Value",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/DefaultValue.py',
        'order':0,
    },
    'DrivenKey':{
        'type':type,
        'function':'DrivenKeyRun',
        'form':'DrivenKeyForm',
        'name':"Driven Key",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/DrivenKey.py',
        'order':0,
    },
    'SpaceSwitch':{
        'type':type,
        'function':'SpaceSwitchRun',
        'form':'SpaceSwitchForm',
        'name':"Space Switch",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/SpaceSwitch.py',
        'order':0,
    },
    'VisibleSwitch':{
        'type':type,
        'function':'VisibleSwitchRun',
        'form':'VisibleSwitchForm',
        'name':"Visible Switch",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/VisibleSwitch.py',
        'order':0,
    },
    'Global':{
        'type':type,
        'function':'GlobalRun',
        'form':'GlobalForm',
        'name':"Global",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/Global.py',
        'order':0,
    },
    'ProxyAttribute':{
        'type':type,
        'function':'ProxyAttributeRun',
        'form':'ProxyAttributeForm',
        'name':"Proxy Attribute",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/ProxyAttribute.py',
        'order':0,
    },
    'Rivet':{
        'type':type,
        'function':'RivetRun',
        'form':'RivetForm',
        'name':"Rivet",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/Rivet.py',
        'order':0,
    },
    'ModuloSDK':{
        'type':type,
        'function':'ModuloSDKRun',
        'form':'ModuloSDKForm',
        'name':"Modulo SDK",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/Modulo SDK.py',
        'order':0,
    },
    'ParentConstraint':{
        'type':type,
        'function':'ParentConstraintRun',
        'form':'ParentConstraintForm',
        'name':"Parent Constraint",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/NLTA_ParentConstraint.py',
        'order':0,
    },
    'PointOnCurve':{
        'type':type,
        'function':'PointOnCurveRun',
        'form':'PointOnCurveForm',
        'name':"PointOnCurve",
        'path':("/").join(os.path.dirname(pm.sceneName()).split('/'))+'/NLTA_PointOnCurve.py',
        'order':0,
    },
    
    'Note':{
        'type':type,
        'form':'ParentConstraintForm',
        'name':"Parent Constraint",
        'path':"",
        'order':0,
    },

}



def CreateUI(data):  
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data) 

    for type in patternData:
        form = patternData[type]['form']
        if cmds.window(form, exists=True):
            cmds.deleteUI(form)

    titles, buttons, inputs = [], [], []
    parent = data['parent']
    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)#*
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    titles.append(cmds.textField(text=data['title'],editable=False))    

    cmds.rowColumnLayout(nc=2)
    projectUI = cmds.rowColumnLayout(numberOfColumns=4,width=400)
    cmds.setParent("..")
    cmds.rowColumnLayout(nc=1)
    buttons.append(cmds.button(label="Create Function",c=CreateFunction))
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    mainUI = cmds.scrollLayout(horizontalScrollBarThickness=4,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=4)
    buttons.append(cmds.button(label="Up P-Script",width=120,c=partial(AddItem,'UpPostScript',mainUI,{})))
    buttons.append(cmds.button(label="Current P-Script",width=120,c=partial(AddItem,'CurrentPostScript',mainUI,{})))   
    buttons.append(cmds.button(label="Up A-Script",width=120,c=partial(AddItem,'UpAfterScript',mainUI,{})))
    buttons.append(cmds.button(label="Current A-Script",width=120,c=partial(AddItem,'CurrentAfterScript',mainUI,{})))   
    buttons.append(cmds.button(label="Visibility",width=120,c=partial(AddItem,'Visibility',mainUI,{})))  
    buttons.append(cmds.button(label="Default Value",width=120,c=partial(AddItem,'DefaultValue',mainUI,{})))  
    buttons.append(cmds.button(label="Driven Key",width=120,c=partial(AddItem,'DrivenKey',mainUI,{})))  
    buttons.append(cmds.button(label="Space Switch",width=120,c=partial(AddItem,'SpaceSwitch',mainUI,{})))  
    buttons.append(cmds.button(label="Visible Switch",width=120,c=partial(AddItem,'VisibleSwitch',mainUI,{})))
    buttons.append(cmds.button(label="Global",width=120,c=partial(AddItem,'Global',mainUI,{})))
    buttons.append(cmds.button(label="Proxy Attribute",width=120,c=partial(AddItem,'ProxyAttribute',mainUI,{})))
    buttons.append(cmds.button(label="Modulo SDK",width=120,c=partial(AddItem,'ModuloSDK',mainUI,{})))
    buttons.append(cmds.button(label="Rivet",width=120,c=partial(AddItem,'Rivet',mainUI,{})))
    buttons.append(cmds.button(label="Parent Constraint",width=120,c=partial(AddItem,'ParentConstraint',mainUI,{})))
    buttons.append(cmds.button(label="Switch IK/FK",width=120,c=partial(AddItem,'SwitchIKFK',mainUI,{})))
    #buttons.append(cmds.button(label="Point On Curve",width=120,c=partial(AddItem,'PointOnCurve',mainUI,{})))
    buttons.append(cmds.button(label="Note",width=120,c=partial(AddItem,'Note',mainUI,{})))  
    buttons.append(cmds.button(label="Save",c=SaveSceneData,width=120))
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
    projectLoad(projectUI)
    SceneLoad(mainUI)


def GetProjectFunctionPath(*arr):
    path = cmds.file(q=True, sn=True)
    if path:
        projectPath = ("/").join(os.path.dirname(path).split("/")[:-2])+"/ProjectFunction/"
        if not os.path.exists(projectPath):
            os.makedirs(projectPath)
        return(projectPath)
    else:
        cmds.warning("Please save file first!~ ")

def projectLoad(ui,*arr):
    def RunScript(path,*arr):
        NLTA_General.RunScriptFile(path)

    def OpenFile(path,*arr):
        sublimePath = NLTA_General.GetDestopAppRealPath('Sublime')
        subprocess.Popen([sublimePath,path])

    projectPath =  GetProjectFunctionPath()
    fileArrays = NLTA_General.GetFiles(projectPath,"py")
    for fileTemp in fileArrays:
        btn = cmds.button(label=fileTemp,width=120,c=partial(RunScript,projectPath+fileTemp+'.py'),parent=ui)
        popup = cmds.popupMenu(parent=btn)
        cmds.menuItem(label="Edit File", parent=popup,c=partial(OpenFile,projectPath+fileTemp+'.py'))

def CreateFunction(*arr):
    projectPath = GetProjectFunctionPath()
    if not projectPath:
        return
    result = cmds.promptDialog(
        title='Create Function',
        message='Enter Function Name:',
        button=['Create', 'Cancel'],
        defaultButton='Create',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if result != 'Create':
        return
    fileName = cmds.promptDialog(query=True, text=True).strip()

    if not fileName:
        cmds.warning("Please enter a valid name.")
        return
    filePath = os.path.join(projectPath, fileName + ".py")
    if os.path.exists(filePath):
        cmds.warning("Function already exists!")
        return
    with open(filePath, "w", encoding="utf-8") as f:
        f.write(
'''# -*- coding: utf-8 -*-

def main():
    print("Hello World")


if __name__ == "__main__":
    main()
'''
        )
    NLTA_General.OpenSublime(filePath)

def SceneLoad(ui,*arr):
    path = cmds.file(q=True, sn=True)
    if path:
        filePath = os.path.dirname(path)+'/'+scenePath
        dataTemp = NLTA_General.readJsonFile(filePath)
        if dataTemp:
            data = sorted(dataTemp, key=lambda x: x["order"])
            if data:
                for i in range(len(data)):
                    AddItem(data[i]['type'],ui,data[i])

def SetAttrValue(attr,value,*arr):
    attrType = cmds.getAttr(attr, type=True)
    if attrType in ("double", "float"):
        cmds.setAttr(attr,float(value))
        value = float(value)
    elif attrType in ("long", "short", "byte", "bool"):
        cmds.setAttr(attr,int(value))
    elif attrType in ("string", "enum"):
        cmds.setAttr(attr,str(value))

def GetAttributeSelected(*arr):
    objs =  cmds.ls(selection=True)
    if objs:
        returnData = {
            "allAttr":[]
        }
        mainAttr = cmds.channelBox("mainChannelBox",query=True,sma=True)
        if mainAttr:
            returnData["main"] = mainAttr
            returnData["allAttr"].extend(mainAttr)
        shapeAttr = cmds.channelBox("mainChannelBox",query=True,ssa=True)
        if shapeAttr:
            returnData["shape"] = shapeAttr
            returnData["allAttr"].extend(shapeAttr)
        inputAttr = cmds.channelBox("mainChannelBox",query=True,sha=True)
        if inputAttr:
            returnData["input"] = inputAttr
            returnData["allAttr"].extend(inputAttr)
        outputAttr = cmds.channelBox("mainChannelBox",query=True,soa=True)
        if outputAttr:
            returnData["output"] = outputAttr
            returnData["allAttr"].extend(outputAttr)
        for obj in objs:
            maxIncrease = len(returnData["allAttr"])
            numberIncrease = 0
            for attr in returnData["allAttr"]:
                if cmds.attributeQuery(attr,node=obj,ex=True):
                    numberIncrease +=1
            if maxIncrease == numberIncrease:
                returnData["obj"] = obj
        return(returnData)
    return(None)

def GroupMatchObject(obj,name):
    grp = cmds.group(em=True, name=name)
    cmds.delete(cmds.parentConstraint(obj, grp, mo=False))
    cmds.delete(cmds.scaleConstraint(obj, grp, mo=False))
    return(grp)

def GetUniqueName(name,*arr):
    if not cmds.objExists(name):
        return(name)
    i = 1
    while True:
        newName = name+'_'+str(i)
        if not cmds.objExists(newName):
            return(newName)
        i += 1

def CreateOffsetGroup(obj,offsetName,*arr):
    offsetName = GetUniqueName(offsetName)
    offset = GroupMatchObject(obj,offsetName)
    ctrlParent = cmds.listRelatives(obj,parent=True)
    if ctrlParent:
        rootParent = ctrlParent[0]
        cmds.parent(offset,rootParent)
    else:
        rootParent = GroupMatchObject(offset,offset+'Parent')
        cmds.parent(offset,rootParent)
    cmds.parent(obj,offset)
    return(offset)

def Browser(ui,*arr):
    path = cmds.fileDialog2(dialogStyle=2, fileMode=1, okCaption='Select File')
    if path:
        cmds.scrollField(ui,text=path[0],edit=True)

def OpenSublime(ui,*arr):
    sublimePath = NLTA_General.GetDestopAppRealPath('Sublime')
    path = cmds.scrollField(ui,query=True,text=True)
    if not os.path.exists(path):
        print("The file not exist.")
    else:
        #NLTA_General.writeJsonFile(path,{})
        subprocess.Popen([sublimePath,path])

def SaveSceneData(*arr):
    dataReturn = []
    for key in sceneData:
        itemData = sceneData[key]
        itemDataTemp = {}
        for itemKey in itemData:
            if itemKey!='textShow':
                itemDataTemp[itemKey] = itemData[itemKey]
        dataReturn.append(itemDataTemp)
    path = cmds.file(q=True, sn=True)    
    if path:
        filePath = os.path.dirname(path)+'/'+scenePath
        NLTA_General.writeJsonFile(filePath,dataReturn)

def DefaultFormAction(parentUI,*arr):
    pass

"""
createNode "nearestPointOnCurve"
connectAttr -f curveShape1.worldSpace[0] nearestPointOnCurve1.inputCurve;
connectAttr -f joint1.translate nearestPointOnCurve1.inPosition;
createNode "pointOnSurfaceInfo"
setAttr "pointOnSurfaceInfo1.parameterU" 1.199;
createNode "pointOnCurveInfo"
connectAttr -f curveShape1.worldSpace[0] pointOnCurveInfo1.inputCurve;
setAttr "pointOnCurveInfo1.parameter" 1.199;
connectAttr -f pointOnCurveInfo1.position joint1.translate;
select -r curve1 ;
"""

def AddItem(type,ui,data,*arr):
    global sceneData

    def OpenItem(ui,*arr):
        form = sceneData[itemUI]['form']
        globals()[form](ui)

    def ChangeOrder(orderUI,itemUI,*arr):
        value = cmds.intField(orderUI,query=True,value=True)
        sceneData[itemUI]['order']=value
        SaveSceneData()

    def ChangeNote(noteUI,itemUI,*arr):
        value = cmds.scrollField(noteUI,query=True,text=True)
        sceneData[itemUI]['name']=value
        SaveSceneData()

    def DeleteItem(ui,*arr):        
        cmds.deleteUI(ui)
        if os.path.exists(sceneData[ui]['path']):
            os.remove(sceneData[ui]['path'])
        del sceneData[ui]
        SaveSceneData()

    def RunItem(ui,*arr):
        function = sceneData[ui]['function']
        path = sceneData[ui]['path']
        globals()[function](path)

    dataDefault = patternData[type]
    if data != {}: 
        dataDefault = data
    if type!="Note":
        itemUI = cmds.rowColumnLayout(numberOfColumns=4,parent=ui)
        cmds.button(label="Run",c=partial(RunItem,itemUI),width=40,bgc=(0.0, 0.4, 0.0),height=35)    
        textShow = cmds.button(label=dataDefault['name'],c=partial(OpenItem,itemUI),width=345)
        orderUI = cmds.intField(value=dataDefault['order'],width=50)
        cmds.button(label="X",c=partial(DeleteItem,itemUI),width=40,bgc=(0.4, 0.0, 0.0))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,itemUI),ec=partial(ChangeOrder,orderUI,itemUI),edit=True)    
        cmds.setParent('..')
    else:
        itemUI = cmds.rowColumnLayout(numberOfColumns=4,parent=ui,)
        cmds.textField(text="###",width=40)
        textShow = cmds.scrollField(text=dataDefault['name'],width=345,height=60)
        orderUI = cmds.intField(value=dataDefault['order'],width=50)
        cmds.button(label="X",c=partial(DeleteItem,itemUI),width=40,bgc=(0.4, 0.0, 0.0))
        cmds.intField(orderUI,cc=partial(ChangeOrder,orderUI,itemUI),ec=partial(ChangeOrder,orderUI,itemUI),edit=True)   
        cmds.scrollField(textShow,cc=partial(ChangeNote,textShow,itemUI),ec=partial(ChangeNote,textShow,itemUI),edit=True,) 
        cmds.setParent('..')
    
    dataDefault['type'] = type
    dataDefault['textShow'] = textShow
    sceneData[itemUI] = dataDefault



### SINGLE SCRIPT ###
def SingleScriptRun(path,*arr):
    NLTA_General.RunScriptFile(path)

def SingleScriptForm(ui,*arr):
    global sceneData
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']
    if cmds.window(form, exists=True):
        cmds.deleteUI(form)

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        value = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = value

    def Run(*arr):
        SingleScriptRun(cmds.scrollField(pathUI,query=True,text=True))        

    def Browser(*arr):
        path = cmds.fileDialog2(dialogStyle=2, fileMode=1, okCaption='Select File')
        if path:
            cmds.scrollField(pathUI,text=path[0],edit=True)

    def OpenScript(*arr):
        path = cmds.scrollField(pathUI,query=True,text=True)
        sublimePath = "C:/Program Files/Sublime Text/sublime_text.exe"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                pass
        subprocess.Popen([sublimePath,path])


    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=3)
    cmds.button(label="Run",c=partial(Run,ui),width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=200)
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")
    
    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))

    cmds.setParent("..")
    cmds.showWindow(form)


### VISIBILITY ####
def VisibilityRun(input,*arr):
    objs =  None
    if isinstance(input, list):
        objs = input
    elif isinstance(input, str):
        objs = NLTA_General.readJsonFile(input) 
    if objs:
        for obj in objs:
            if cmds.objExists(obj):
                attr = obj + '.visibility'
                conn =  cmds.listConnections(attr, source=True, destination=False)
                lock = cmds.getAttr(obj + ".visibility", lock=True)
                if conn or lock:
                    grp = cmds.group(empty=True, name="{}_VisOffsetGrp".format(obj))
                    cmds.delete(cmds.parentConstraint(obj, grp))
                    grpReplace = cmds.group(empty=True, name="{}_VisReplaceGrp".format(obj))
                    cmds.delete(cmds.parentConstraint(obj,grpReplace))
                    
                    objParent = cmds.listRelatives(obj,parent=True)[0]     
                    if objParent:
                        cmds.parent(grp,objParent)
                    objChildren = cmds.listRelatives(obj,children=True)
                    if objChildren:
                        cmds.parent(objChildren,grpReplace)
                        cmds.parent(grpReplace,objParent)
                        constrTemp = cmds.parentConstraint(obj,grpReplace,mo=True)[0]                    
                        cmds.setAttr(constrTemp+'.interpType',2)
                        cmds.scaleConstraint(obj,grpReplace,mo=True)
                    else:
                        cmds.delete(grpReplace)
                    cmds.parent(obj,grp)            
                    cmds.setAttr(grp+'.visibility',0)
                else:
                    cmds.setAttr(obj+'.visibility',0)

def VisibilityForm(ui,*arr):
    global sceneData
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)

    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []
        
    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            data = NLTA_General.writeJsonFile(path,[])
        objs = NLTA_General.readJsonFile(path)
        if objs:
            cmds.scrollField(visibilityUI,edit=True,text=('\n').join(objs))
        else:
            cmds.scrollField(visibilityUI,edit=True,text='')

    def AddItem(ui,*arr):
        objs = cmds.ls(selection=True,ap=True)
        currentItems = cmds.scrollField(ui,query=True,text=True).split("\n")
        currentItems = [item for item in currentItems if item != ""]
        if objs:
            for obj in objs:
                if obj not in currentItems:
                    currentItems.append(obj)
        if currentItems:
            string = ('\n').join(currentItems)
            cmds.scrollField(ui,edit=True,text=string)

    def RemoveItem(ui,*arr):
        objs = cmds.ls(selection=True,ap=True)
        currentItems = cmds.scrollField(ui,query=True,text=True).split("\n")
        if objs:
            for obj in objs:
                currentItems.remove(obj)
        if currentItems:
            string = ('\n').join(currentItems)
            cmds.scrollField(ui,edit=True,text=string)        

    def SelectItem(ui,*arr):
        currentItems = cmds.scrollField(ui,query=True,text=True).split("\n")
        cmds.select(currentItems)

    def Run(*arr):
        objs = cmds.scrollField(visibilityUI,query=True,text=True).split("\n")
        VisibilityRun(objs)

    def Save(*arr):
        data = cmds.scrollField(visibilityUI,query=True,text=True).split("\n")
        path = cmds.file(q=True, sn=True)
        if path:
            filePath = cmds.scrollField(pathUI,query=True,text=True)
            NLTA_General.writeJsonFile(filePath,data)
        SaveSceneData()

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=2)#Visibility Setup
    visibilityUI = cmds.scrollField(text=('\n'.join(data) if data else ''),wordWrap=True,height=80,width=300)
    cmds.rowColumnLayout(numberOfColumns=1)#1
    cmds.button(label="Add",c=partial(AddItem,visibilityUI),width=100,height=35)
    cmds.button(label="Remove",c=partial(RemoveItem,visibilityUI),width=100,height=35)
    cmds.button(label="Select",c=partial(SelectItem,visibilityUI),width=100,height=35)
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))

    cmds.setParent("..")
    cmds.showWindow(form)



### DEFAULT VALUE ###
def DefaultValueRun(input,*arr):
    data =  None
    if isinstance(input, dict):
        data = input
    elif isinstance(input, str):
        data = NLTA_General.readJsonFile(input)
    for key in data:
        value = data[key]
        attrType = cmds.getAttr(key, type=True)
        if attrType in ("double", "float",'doubleAngle'):
            value = float(value)
        elif attrType in ("long", "short", "byte", "bool", "enum"):
            value = int(value)
        elif attrType in ("string"):
            value = str(value)
        cmds.setAttr(key,value)

def DefaultValueForm(ui,*arr):
    global sceneData
    global attributeUIs, attributeData

    attributeUIs = {}
    attributeData = {}

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        attributeData = {}        
        for key in attributeUIs:
            attr = cmds.textField(attributeUIs[key]['attr'],query=True,text=True)
            value = cmds.textField(attributeUIs[key]['value'],query=True,text=True)
            if value == 'True':
                value = 1
            if value == 'False':
                value = 0
            attributeData[attr] = value
        return(attributeData) 

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(*arr):
        current = GetAttributeSelected()
        if current:
            for i in range(len(current['main'])):
                attrTemp = current['obj']+'.'+current['main'][i]
                if attrTemp == True:
                    attrTemp = 1
                if attrTemp == False:
                    attrTemp = 0
                Create({
                    'attr':attrTemp,
                    'value':cmds.getAttr(attrTemp)
                })

    def Run(*arr):
        data = GetData()
        DefaultValueRun(data)

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global attributeUIs,attributeData
        attributeUIs = {}
        attributeData = {}
        children = cmds.layout(valueDefaultUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        
        if data:
            for key in data:
                Create({
                    'attr':key,
                    'value':data[key]
                })

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1)#Start
    cmds.rowColumnLayout(numberOfColumns=2)
    valueDefaultUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=300)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)#1
    #cmds.button(label="Add",c=partial(AddAttributeDefaultItem,valueDefaultUI))
    cmds.button(label="Add",c=Add)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")#End
    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)
            

### VISIBLE SWITCH
def VisibleSwitchRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        ctrl = data['ContentAttr']
        if not cmds.attributeQuery(data['AttrPick'], node=ctrl, exists=True):
            cmds.addAttr(ctrl, ln=data['AttrPick'], at='enum', en=data['Options'])
            cmds.setAttr(ctrl+'.'+data['AttrPick'], e=True, keyable=True)
        objectArrays = data['Objects'].split('\n')
        options = data['Options'].split(':')[0:-1]
        
        for i in range(len(options)):
            if objectArrays[i] != '':
                objs = objectArrays[i].split(';')
                condition = cmds.shadingNode("condition", asUtility=True)
                cmds.connectAttr(ctrl+"."+data['AttrPick'], condition+".firstTerm", force=True)
                cmds.setAttr(condition+".secondTerm",i)
                cmds.setAttr(condition+".colorIfTrueR",1)
                cmds.setAttr(condition+".colorIfFalseR",0)
                for obj in objs:
                    objToConnect = []
                    if data['MeshOnly']:
                        objToConnect.append(obj)
                        objChildren = cmds.listRelatives(obj,children=True,type="mesh")
                        if objChildren:
                            objToConnect.extend(objChildren)
                    else:
                        grp = cmds.group(empty=True,name=NLTA_General.GetUniqueName("{}_VisSwitchOffsetGrp".format(obj)))
                        cmds.delete(cmds.parentConstraint(obj, grp))                   
                        objParent = cmds.listRelatives(obj,parent=True)   
                        if objParent:
                            objParent = cmds.listRelatives(obj,parent=True)[0]
                            cmds.parent(grp,objParent)
                            NLTA_General.ZeroTransform(grp)                            
                        if not data["InorgeChildren"]:
                            objChildren = cmds.listRelatives(obj,children=True,type='transform')
                            if objChildren:                            
                                grpReplace = cmds.group(empty=True,name=NLTA_General.GetUniqueName("{}_VisSwitchReplaceGrp".format(obj)))
                                cmds.delete(cmds.parentConstraint(obj,grpReplace))
                                if objParent:
                                    cmds.parent(grpReplace,objParent)
                                    NLTA_General.ZeroTransform(grpReplace)                     
                                cmds.parent(objChildren,grpReplace)                        
                                constrTemp = cmds.parentConstraint(obj,grpReplace,mo=True)[0]                  
                                cmds.setAttr(constrTemp+'.interpType',2)
                                cmds.scaleConstraint(obj,grpReplace,mo=True) 
                        cmds.parent(obj,grp)
                        objToConnect.append(grp)
                    for objTemp in objToConnect:
                        cmds.connectAttr(condition+".outColorR",objTemp+'.visibility', force=True)
                    

def VisibleSwitchForm(ui,*arr):
    global sceneData
    visibleItems = {
        'order':[],
        'items':{},
    }
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in visibleItems['items']:
            Objects=cmds.scrollField(visibleItems['items'][item]['Objects'],query=True,text=True)
            ContentAttr=cmds.textField(visibleItems['items'][item]['ContentAttr'],query=True,text=True)
            AttrPick=cmds.textField(visibleItems['items'][item]['AttrPick'],query=True,text=True)
            Options=cmds.textField(visibleItems['items'][item]['Options'],query=True,text=True)
            InorgeChildren = cmds.checkBox(visibleItems['items'][item]['InorgeChildren'],query=True,value=True)
            MeshOnly = cmds.checkBox(visibleItems['items'][item]['MeshOnly'],query=True,value=True)
            returnData.append({
                'Objects':Objects,
                'ContentAttr':ContentAttr,
                'AttrPick':AttrPick,
                'Options':Options,
                'InorgeChildren':InorgeChildren,
                "MeshOnly":MeshOnly,
            })
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 90
        inputWidth = 230
        inputHeight = 35
        buttonHeight = 35
        def PickObjects(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = ";".join(selection)
                currentContent = cmds.scrollField(ui, query=True, text=True)
                if currentContent !="":
                    cmds.scrollField(ui, edit=True, text=currentContent+"\n"+content)
                else:
                    cmds.scrollField(ui, edit=True, text=content)   

        def PickContentAttr(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                obj = selection[0]
                cmds.textField(ui,edit=True,text=obj)   

        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del visibleItems['items'][ui]
            visibleItems['order'].remove(ui)

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15),width=390)

        cmds.rowColumnLayout(numberOfColumns=1)


        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Options',editable=False,w=titleWidth)
        options = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Options", ""))
        itemData['Options'] = options
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Objects',editable=False,w=titleWidth)
        Objects = cmds.scrollField(wordWrap=True,height=80,w=inputWidth,text=data.get("Objects", ""))
        itemData['Objects'] = Objects
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickObjects,Objects))
        cmds.button(label="*",w=30,h=buttonHeight)
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Content Attr',editable=False,w=titleWidth)
        ContentAttr =cmds.textField(w=inputWidth,height=inputHeight,text=data.get("ContentAttr", ""))
        itemData['ContentAttr'] = ContentAttr
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickContentAttr,ContentAttr))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Attr Pick',editable=False,w=titleWidth)
        attrPick = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("AttrPick", ""))
        itemData['AttrPick'] = attrPick
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Inorge Children',editable=False,w=titleWidth)
        InorgeChildren = cmds.checkBox("InorgeChildren", value=data.get("InorgeChildren",True))
        itemData['InorgeChildren'] = InorgeChildren
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Mesh Only',editable=False,w=titleWidth)
        MeshOnly = cmds.checkBox("MeshOnly", value=data.get("MeshOnly",True))
        itemData["MeshOnly"] = MeshOnly
        cmds.setParent("..")


        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        visibleItems['items'][itemUI] = itemData
        visibleItems['order'].append(itemUI)


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            VisibleSwitchRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=400)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")
    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)


### GLOBAL ###
def GlobalRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        offset = GroupMatchObject(data['child'],data['offsetName'])
        ctrl = data['child']
        if not cmds.attributeQuery(data['attrSlide'], node=ctrl, exists=True):
            cmds.addAttr(ctrl, ln=data['attrSlide'], at='double', min=0, max=1, dv=float(data['defaultValue']))
            cmds.setAttr(ctrl+'.'+data['attrSlide'], e=True, keyable=True)

        ctrlParent = cmds.listRelatives(ctrl,parent=True)
        parent = data['parent']
        if ctrlParent:
            rootParent = ctrlParent[0]
            cmds.parent(offset,rootParent)
        else:
            rootParent = GroupMatchObject(offset,offset+'Parent')
            cmds.parent(offset,rootParent)
        cmds.parent(ctrl,offset)

        blend = cmds.shadingNode("blendColors", asUtility=True)
        parentConstr = cmds.parentConstraint(rootParent,offset,mo=data['maintain'])[0]                   
        cmds.setAttr(parentConstr+'.interpType',2)

        attrs = ["rx","ry","rz"]
        for attr in attrs:
            for src in cmds.listConnections(offset+'.'+attr, s=True, d=False, plugs=True) or []:
                cmds.disconnectAttr(src,offset+'.'+attr)
        orientConstr = cmds.orientConstraint(parent,offset,mo=data['maintain'])[0]
        for attr in attrs:
            for src in cmds.listConnections(offset+'.'+attr, s=True, d=False, plugs=True) or []:
                cmds.disconnectAttr(src,offset+'.'+attr)
        cmds.connectAttr(parentConstr+".constraintRotate",blend+".color2", force=True)
        cmds.connectAttr(orientConstr+".constraintRotate",blend+".color1", force=True)
        cmds.connectAttr(blend+".output",offset+".rotate", force=True)
        cmds.connectAttr(ctrl+"."+data['attrSlide'],blend+".blender", force=True)

### GLOBAL
def GlobalForm(ui,*arr):
    global sceneData
    spaceItems = {
        'order':[],
        'items':{},
    }

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in spaceItems['items']:
            child=cmds.textField(spaceItems['items'][item]['Child'],query=True,text=True)
            parent=cmds.scrollField(spaceItems['items'][item]['Parent'],query=True,text=True)
            offsetName=cmds.textField(spaceItems['items'][item]['OffsetName'],query=True,text=True)
            attrSlide=cmds.textField(spaceItems['items'][item]['AttrSlide'],query=True,text=True)
            defaultValue=cmds.textField(spaceItems['items'][item]['DefaultValue'],query=True,text=True)
            maintain = cmds.checkBox(spaceItems['items'][item]['Maintain'],query=True,value=True)
            returnData.append({
                'child':child,
                'parent':parent,
                'offsetName':offsetName,
                'attrSlide':attrSlide,
                'defaultValue':defaultValue,
                'maintain':maintain,
            })
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 233
        inputHeight = 25
        buttonHeight = 25

        def PickChild(ui,*arr):
            objs = cmds.ls(selection=True,ap=True)
            if objs:
                obj = objs[0]
                cmds.textField(ui,edit=True,text=obj)
                cmds.textField(offsetName,edit=True,text=obj+'_GlobalGrp')

        def PickParents(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                cmds.scrollField(ui, edit=True, text=selection[0])
        
        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del spaceItems['items'][ui]
            spaceItems['order'].remove(ui)

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))

        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Child',editable=False,w=titleWidth)
        child = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("child", ""))
        itemData['Child'] = child
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickChild,child))
        cmds.button(label="*",w=30,h=buttonHeight)
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Parent',editable=False,w=titleWidth)
        Parents = cmds.scrollField(wordWrap=True,height=52,w=inputWidth,text=data.get("parent", ""))
        itemData['Parent'] = Parents
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickParents,Parents)) 
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Offset Name',editable=False,w=titleWidth)
        offsetName = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("offsetName", ""))
        itemData['OffsetName'] = offsetName
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Attr Slide',editable=False,w=titleWidth)
        attrSlide = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("attrSlide", "Global"))
        itemData['AttrSlide'] = attrSlide
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Default Value',editable=False,w=titleWidth)
        defaultValue = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("defaultValue", "0"))
        itemData['DefaultValue'] = defaultValue
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Maintain',editable=False,w=titleWidth)
        maintain = cmds.checkBox("Maintain", value=data.get("maintain",True))
        itemData['Maintain'] = maintain
        cmds.setParent("..")

        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        spaceItems['items'][itemUI] = itemData
        spaceItems['order'].append(itemUI)


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            GlobalRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=132)  
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)

### RIVET ###
def RivetRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        vertexs = data['Vertexs'].split(';')
        mesh = vertexs[0].split(".")[0]
        name =  data['Name']
        copyTransform = data['CopyTransform']
        child = data['Child']
        parent = data['Parent']
        positions = [cmds.pointPosition(v, w=True) for v in vertexs]
        plane = cmds.polyCreateFacet(p=positions, n="quadPlane")[0]
        cmds.select(plane+'.e[0]',plane+'.e[2]')
        sel_edges = cmds.filterExpand(sm=32)  # polygon edges
        sel_points = cmds.filterExpand(sm=41)  # NURBS surface points
        posi = None
        nameObject = None

        if sel_edges:
            if len(sel_edges) != 2:
                cmds.error("Select exactly 2 edges.")
                return ""

            # Parse edge info
            parts = sel_edges[0].split(".")
            nameObject = parts[0]
            e1 = int(sel_edges[0].split("[")[-1].split("]")[0])
            e2 = int(sel_edges[1].split("[")[-1].split("]")[0])

            # Create nodes
            cfme1 = cmds.createNode("curveFromMeshEdge", n="rivetCurveFromMeshEdge1")
            cfme2 = cmds.createNode("curveFromMeshEdge", n="rivetCurveFromMeshEdge2")
            loft = cmds.createNode("loft", n="rivetLoft1")
            posi = cmds.createNode("pointOnSurfaceInfo", n="rivetPointOnSurfaceInfo1")

            # Set attrs
            cmds.setAttr(cfme1 + ".ihi", 1)
            cmds.setAttr(cfme1 + ".ei[0]", e1)
            cmds.setAttr(cfme2 + ".ihi", 1)
            cmds.setAttr(cfme2 + ".ei[0]", e2)
            cmds.setAttr(loft + ".ic", s=2)
            cmds.setAttr(loft + ".u", True)
            cmds.setAttr(loft + ".rsn", True)

            cmds.setAttr(posi + ".turnOnPercentage", 1)
            cmds.setAttr(posi + ".parameterU", 0.5)
            cmds.setAttr(posi + ".parameterV", 0.5)

            # Connections
            cmds.connectAttr(loft + ".os", posi + ".is", f=True)
            cmds.connectAttr(cfme1 + ".oc", loft + ".ic[0]", f=True)
            cmds.connectAttr(cfme2 + ".oc", loft + ".ic[1]", f=True)
            cmds.connectAttr(nameObject + ".w", cfme1 + ".im", f=True)
            cmds.connectAttr(nameObject + ".w", cfme2 + ".im", f=True)

        elif sel_points:
            if len(sel_points) != 1:
                cmds.error("Select exactly 1 surface point.")
                return ""

            # Parse NURBS point info
            parts = sel_points[0].split(".")
            nameObject = parts[0]
            uv = sel_points[0].split("[")[-1].split("]")[0].split("][")
            u, v = float(uv[0]), float(uv[1])

            posi = cmds.createNode("pointOnSurfaceInfo", n="rivetPointOnSurfaceInfo1")
            cmds.setAttr(posi + ".turnOnPercentage", 0)
            cmds.setAttr(posi + ".parameterU", u)
            cmds.setAttr(posi + ".parameterV", v)
            cmds.connectAttr(nameObject + ".ws", posi + ".is", f=True)

        else:
            cmds.error("Select 2 edges (poly) or 1 point (NURBS).")
            return ""

        # Create locator
        loc = cmds.createNode("transform", n=name+"_Loc")
        cmds.createNode("locator", n=loc + "Shape", p=loc)

        # Create aimConstraint node (not Maya's constraint command, but node)
        ac = cmds.createNode("aimConstraint", n=loc + "_rivetAimConstraint1", p=loc)
        cmds.setAttr(ac + ".tg[0].tw", 1)
        cmds.setAttr(ac + ".a", 0, 1, 0, type="double3")
        cmds.setAttr(ac + ".u", 0, 0, 1, type="double3")

        for attr in ["v","tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
            cmds.setAttr(loc + "." + attr, k=False)

        # Connections
        cmds.connectAttr(posi + ".position", loc + ".translate", f=True)
        cmds.connectAttr(posi + ".n", ac + ".tg[0].tt", f=True)
        cmds.connectAttr(posi + ".tv", ac + ".wu", f=True)
        cmds.connectAttr(ac + ".crx", loc + ".rx", f=True)
        cmds.connectAttr(ac + ".cry", loc + ".ry", f=True)
        cmds.connectAttr(ac + ".crz", loc + ".rz", f=True)


        if copyTransform != "":
            transformName = name+'_CopyTransform'
            GroupMatchObject(copyTransform,transformName)
            cmds.parent(transformName,loc)
        
        if child:
            childParent = cmds.listRelatives(child,parent=True)[0]
            childOffset = child+"_RivetOffset"
            GroupMatchObject(child,childOffset)
            cmds.parent(childOffset,childParent)
            cmds.parent(child,childOffset)
            cmds.parentConstraint(loc,childOffset,mo=True)

        cmds.select(mesh)
        cmds.select(plane,add=True)
        NLTA_General.copyJointBind()       


        if parent:
            cmds.parent([plane,loc],parent)
        

        return loc

### RIVET
def RivetForm(ui,*arr):
    global sceneData
    Items = {'items':{}}

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in Items['items']:
            Vertexs=cmds.textField(Items['items'][item]['Vertexs'],query=True,text=True)
            Name=cmds.textField(Items['items'][item]['Name'],query=True,text=True)
            CopyTransform=cmds.textField(Items['items'][item]['CopyTransform'],query=True,text=True)
            Child=cmds.textField(Items['items'][item]['Child'],query=True,text=True)
            Parent=cmds.textField(Items['items'][item]['Parent'],query=True,text=True)           
            returnData.append({
                'Vertexs':Vertexs,
                'Name':Name,
                'CopyTransform':CopyTransform,
                'Child':Child,
                'Parent':Parent,
                
            })
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 233
        inputHeight = 25
        buttonHeight = 25

        def PickChild(*arr):
            objs = cmds.ls(selection=True,ap=True)
            if objs:
                cmds.textField(Child,edit=True,text=(';').join(objs))

        def PickVertexs(*arr):
            objs = cmds.ls(flatten=True,os=True)
            if objs:
                cmds.textField(Vertexs,edit=True,text=(';').join(objs))
                cmds.textField(Name,edit=True,text=objs[0].split('.')[0]+'_Rivet')

        def PickParents(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                cmds.textField(Parent, edit=True, text=selection[0])

        def PickCopyTransform(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                cmds.textField(CopyTransform, edit=True, text=selection[0])
        
        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del Items['items'][ui]
            Items['order'].remove(ui)

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))

        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Vertexs',editable=False,w=titleWidth)
        Vertexs = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Vertexs", ""))
        itemData['Vertexs'] = Vertexs
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickVertexs,Vertexs))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Name',editable=False,w=titleWidth)
        Name = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Name", ""))
        itemData['Name'] = Name
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Copy Transform',editable=False,w=titleWidth)
        CopyTransform = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("CopyTransform", ""))
        itemData['CopyTransform'] = CopyTransform
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickCopyTransform,CopyTransform))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Child',editable=False,w=titleWidth)
        Child = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Child", ""))
        itemData['Child'] = Child
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickChild,Child))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Parent',editable=False,w=titleWidth)
        Parent = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Parent", ""))
        itemData['Parent'] = Parent
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickParents,Parent)) 
        cmds.setParent("..")
        cmds.setParent("..")



        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        Items['items'][itemUI] = itemData


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            RivetRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=132)  
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)







### SPACE SWITCH ###
def SpaceSwitchRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        print(data)
        offset = GroupMatchObject(data['child'],data['offsetName'])
        ctrl = data['child']
        ctrlParent = cmds.listRelatives(ctrl,parent=True)
        parents = data['parents'].split('\n')

        if ctrlParent:
            rootParent = ctrlParent[0]
            cmds.parent(offset,rootParent)
        else:
            rootParent = GroupMatchObject(offset,offset+'Parent')
            cmds.parent(offset,rootParent)

        for axis in ['x','y','z']:
            cmds.setAttr(offset+'.r'+axis,0)
            cmds.setAttr(offset+'.t'+axis,0)
        
        cmds.parent(ctrl,offset)
        
        if data['maintain']:
            constr = cmds.parentConstraint(*(parents + [offset]), mo=data['maintain'])
            cmds.setAttr(constr+'.interpType',2)
            addStt = 0
        else:
            constr = cmds.parentConstraint(rootParent,offset,mo=data['maintain'])[0]
            cmds.setAttr(constr+'.interpType',2)
            constrTemp = cmds.parentConstraint(*(parents + [offset]), mo=data['maintain'])
            cmds.setAttr(constrTemp+'.interpType',2)
            addStt = 1

        
        connOrder = {}

        if not cmds.attributeQuery(data['attrPick'], node=ctrl, exists=True):
            cmds.addAttr(ctrl, ln=data['attrPick'], at='enum', en=data['options'])
            cmds.setAttr(ctrl+'.'+data['attrPick'], e=True, keyable=True)

        if data["attrSlide"] != "":
            if not cmds.attributeQuery(data['attrSlide'], node=ctrl, exists=True):
                cmds.addAttr(ctrl, ln=data['attrSlide'], at='double', min=0, max=1, dv=float(data['defaultValue']))
                cmds.setAttr(ctrl+'.'+data['attrSlide'], e=True, keyable=True)

        stt = 0
        for i in range(len(parents)):
            condition = cmds.shadingNode("condition", asUtility=True)
            cmds.connectAttr(ctrl+"."+data['attrPick'], condition+".firstTerm", force=True)
            cmds.setAttr(condition+".secondTerm",i)
            cmds.setAttr(condition+'.colorIfFalseR', 0)
            if data["attrSlide"] != "":
                cmds.connectAttr(ctrl+"."+data['attrSlide'],condition+".colorIfTrueR", force=True)
            else:
                cmds.setAttr(condition+'.colorIfTrueR', 1)            
            cmds.connectAttr(condition+".outColorR", constr+"."+(parents[i]+'W'+str(i+addStt)), force=True)
            stt +=1

        if data["attrSlide"] != "":
            plus = cmds.shadingNode("plusMinusAverage", asUtility=True)
            cmds.setAttr(plus+".operation", 2)
            cmds.connectAttr(ctrl+"."+data['attrSlide'],plus+".input1D[0]", force=True)
            cmds.connectAttr(ctrl+"."+data['attrSlide'],plus+".input1D[1]", force=True)
            cmds.disconnectAttr(ctrl+"."+data['attrSlide'],plus+".input1D[0]")
            cmds.setAttr(plus+".input1D[0]", 1)

        if data["attrSlide"] != "":
            constrTemp = cmds.parentConstraint(rootParent,offset,mo=True)[0]
            cmds.setAttr(constrTemp+'.interpType',2)
            cmds.connectAttr(plus+".output1D", constr+"."+rootParent+"W"+str(0), force=True)

def SpaceSwitchForm(ui,*arr):
    global sceneData
    spaceItems = {
        'order':[],
        'items':{},
    }

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in spaceItems['items']:
            child=cmds.textField(spaceItems['items'][item]['Child'],query=True,text=True)
            parents=cmds.scrollField(spaceItems['items'][item]['Parents'],query=True,text=True)
            offsetName=cmds.textField(spaceItems['items'][item]['OffsetName'],query=True,text=True)
            attrPick=cmds.textField(spaceItems['items'][item]['AttrPick'],query=True,text=True)
            attrSlide=cmds.textField(spaceItems['items'][item]['AttrSlide'],query=True,text=True)
            defaultValue=cmds.textField(spaceItems['items'][item]['DefaultValue'],query=True,text=True)
            options=cmds.textField(spaceItems['items'][item]['Options'],query=True,text=True)
            maintain = cmds.checkBox(spaceItems['items'][item]['Maintain'],query=True,value=True)
            returnData.append({
                'child':child,
                'parents':parents,
                'offsetName':offsetName,
                'attrPick':attrPick,
                'attrSlide':attrSlide,
                'defaultValue':defaultValue,
                'options':options,
                'maintain':maintain,

            })
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 233
        inputHeight = 25
        buttonHeight = 25

        def PickChild(ui,*arr):
            objs = cmds.ls(selection=True,ap=True)
            if objs:
                obj = objs[0]
                cmds.textField(ui,edit=True,text=obj)
                cmds.textField(offsetName,edit=True,text=obj+'_SpaceSwitchGrp')

        def PickParents(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = "\n".join(selection)
                cmds.scrollField(ui, edit=True, text=content)
                cmds.textField(options,edit=True,text=':'.join(selection)+':')

        def AddParents(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                current_text = cmds.scrollField(ui, query=True, text=True).strip()
                new_lines = current_text.splitlines() if current_text else []
                new_lines += selection
                updated_text = "\n".join(new_lines)
                cmds.scrollField(ui, edit=True, text=updated_text)
                cmds.textField(options,edit=True,text=':'.join(new_lines)+':')
        
        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del spaceItems['items'][ui]
            spaceItems['order'].remove(ui)

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))

        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Child',editable=False,w=titleWidth)
        child = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("child", ""))
        itemData['Child'] = child
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickChild,child))
        cmds.button(label="*",w=30,h=buttonHeight)
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Parents',editable=False,w=titleWidth)
        Parents = cmds.scrollField(wordWrap=True,height=52,w=inputWidth,text=data.get("parents", ""))
        itemData['Parents'] = Parents
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickParents,Parents))
        cmds.button(label="*",w=30,h=buttonHeight)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(AddParents,Parents))    
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Offset Name',editable=False,w=titleWidth)
        offsetName = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("offsetName", ""))
        itemData['OffsetName'] = offsetName
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Attr Pick',editable=False,w=titleWidth)
        attrPick = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("attrPick", ""))
        itemData['AttrPick'] = attrPick
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Attr Slide',editable=False,w=titleWidth)
        attrSlide = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("attrSlide", ""))
        itemData['AttrSlide'] = attrSlide
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Default Value',editable=False,w=titleWidth)
        defaultValue = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("defaultValue", "0"))
        itemData['DefaultValue'] = defaultValue
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Options',editable=False,w=titleWidth)
        options = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("options", ""))
        itemData['Options'] = options
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Maintain',editable=False,w=titleWidth)
        maintain = cmds.checkBox("Maintain", value=data.get("maintain",True))
        itemData['Maintain'] = maintain
        cmds.setParent("..")

        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        spaceItems['items'][itemUI] = itemData
        spaceItems['order'].append(itemUI)


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            SpaceSwitchRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=132)  
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)


### PROXY ATTRIBUTE
def ProxyAttributeRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        source = data['source']
        sourceAttr = data['sourceAttr']
        targets = data['targets'].split('\n')
        targetAttr = data['targetAttr']
        for target in targets:
            #print('cmds.addAttr('+source+', proxy='+target+', ln='+targetAttr+')')
            cmds.addAttr(target, proxy=source+'.'+sourceAttr, ln=targetAttr)

def ProxyAttributeForm(ui,*arr):
    global sceneData
    Items = {
        'order':[],
        'items':{},
    }

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in Items['items']:
            source=cmds.textField(Items['items'][item]['Source'],query=True,text=True)
            sourceAttr=cmds.textField(Items['items'][item]['SourceAttr'],query=True,text=True)
            targets=cmds.scrollField(Items['items'][item]['Targets'],query=True,text=True)
            targetAttr=cmds.textField(Items['items'][item]['TargetAttr'],query=True,text=True)
            returnData.append({
                'source':source,
                'sourceAttr':sourceAttr,
                'targets':targets,
                'targetAttr':targetAttr,
            })
        return(returnData)

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 263
        inputHeight = 25
        buttonHeight = 25
        def PickSource(*arr):
            current = GetAttributeSelected()
            if current:
                attr = current['main'][0]                
                cmds.textField(source,edit=True,text=current['obj'])
                cmds.textField(sourceAttr,edit=True,text=attr)
                cmds.textField(targetAttr,edit=True,text=attr)

        def PickTargets(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = "\n".join(selection)
                cmds.scrollField(targets, edit=True, text=content)

        def AddTargets(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                current_text = cmds.scrollField(targets, query=True, text=True).strip()
                new_lines = current_text.splitlines() if current_text else []
                new_lines += selection
                updated_text = "\n".join(new_lines)
                cmds.scrollField(targets, edit=True, text=updated_text)

        def DeleteItem(ui,*arr):
            cmds.deleteUI(itemUI)
            del Items['items'][itemUI]

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))

        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Souce',editable=False,w=titleWidth)
        source = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("source", ""))
        itemData['Source'] = source
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickSource,source))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Souce Attr',editable=False,w=titleWidth)
        sourceAttr = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("sourceAttr", ""))
        itemData['SourceAttr'] = sourceAttr
        cmds.setParent("..")
        cmds.setParent("..")


        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Targets',editable=False,w=titleWidth)
        targets = cmds.scrollField(wordWrap=True,height=80,w=inputWidth,text=data.get("targets", ""))
        itemData['Targets'] = targets
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickTargets,targets))
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(AddTargets,targets))    
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Target Attr',editable=False,w=titleWidth)
        targetAttr = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("targetAttr", ""))
        itemData['TargetAttr'] = targetAttr
        cmds.setParent("..")

        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        Items['items'][itemUI] = itemData
        Items['order'].append(itemUI)


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            ProxyAttributeRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=400)  
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)


### MODULO SDK
def ModuloSDKRun(input,*arr): 
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for a in range(len(datas)):
        data = datas[a]
        source = data['source']
        sourceAttr = data['sourceAttr']
        attrsData =  data['attrsData']

        scriptPattern = """
float $val = {}.{};
int $r = abs((int)$val % 10);
{}
        """
        if cmds.objExists(source):
            if not cmds.attributeQuery(sourceAttr, node=source, exists=True):
                cmds.addAttr(driver, ln=sourceAttr, at="long", k=True)
            offsetData = {}
            for attr in attrsData:
                target = attr.split('.')[0]
                offsetName = target+'_Modulo_Grp'
                if not cmds.objExists(offsetName):
                    offsetData[target] = CreateOffsetGroup(target,offsetName)
                else:
                    offsetData[target] = offsetName

            moduloData = {}
            for b in range(9):
                modulo = str(b)
                valueString = []
                for attr in attrsData:
                    target = attr.split('.')[0]
                    attrName = attr.split('.')[1]
                    offset = offsetData[target]
                    valuesData = attrsData[attr]
                    if modulo in valuesData:
                        valueString.append(offset+'.'+attrName+'='+valuesData[modulo])
                if valueString:
                    moduloData[modulo] = valueString

            stringConcat = ""
            for b in range(9):
                modulo =  str(b)
                if modulo in moduloData:
                    if modulo == '0':
                        stringConcat = stringConcat+'if ($r == '+modulo+') { '+(';').join(moduloData[modulo])+'; }\n'
                    else:
                        stringConcat = stringConcat+'else if ($r == '+modulo+') { '+(';').join(moduloData[modulo])+'; }\n'
            script = scriptPattern.format(source, sourceAttr,stringConcat)
            cmds.expression(s=script, o="", ae=True, uc="all")

def ModuloSDKForm(ui,*arr):
    global sceneData
    Items = {'items':{}}
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in Items['items']:
            itemData = Items['items'][item]
            source = cmds.textField(itemData['Source'],query=True,text=True)
            sourceAttr = cmds.textField(itemData['SourceAttr'],query=True,text=True)
            allAttrData = {}
            for a in range(len(itemData['attrsData'])):
                attrItem = itemData['attrsData'][a]
                targetAttr = attrItem['targetAttr']
                attrValues = attrItem['values']
                attrName = cmds.textField(targetAttr,query=True,text=True)
                valuesDict = {}
                for b in range(len(attrValues)):
                    valueItemUI = attrValues[b]
                    valueItemValue = cmds.textField(valueItemUI,query=True,text=True)
                    if valueItemValue != '':
                        valuesDict[str(b)] = valueItemValue
                allAttrData[attrName] = valuesDict
            returnData.append({
                'source':source,
                'sourceAttr':sourceAttr,
                'attrsData':allAttrData,
            })
        return(returnData)

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 263
        inputHeight = 25
        buttonHeight = 25
        def PickSource(*arr):
            current = GetAttributeSelected()
            if current:
                attr = current['main'][0]                
                cmds.textField(source,edit=True,text=current['obj'])
                cmds.textField(sourceAttr,edit=True,text=attr)

        def PickTargets(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = "\n".join(selection)
                cmds.scrollField(targets, edit=True, text=content)

        def AddTargets(*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                current_text = cmds.scrollField(targets, query=True, text=True).strip()
                new_lines = current_text.splitlines() if current_text else []
                new_lines += selection
                updated_text = "\n".join(new_lines)
                cmds.scrollField(targets, edit=True, text=updated_text)

        def DeleteItem(ui,*arr):
            cmds.deleteUI(itemUI)
            del Items['items'][itemUI]

        def ItemLoad(*arr):
            print

        def AddAttrItem(attrData,*arr):
            def DeleteAttrItem(ui,*arr):
                for i in range(len(Items['items'][itemUI]['attrsData'])):
                    attrItem = Items['items'][itemUI]['attrsData'][i]
                    if attrItem['ui'] == ui:
                        cmds.deleteUI(ui)
                        del Items['items'][itemUI]['attrsData'][i]

            if attrData=={}:
                current = GetAttributeSelected()
                if current:
                    obj =  current['obj']
                    attrs = current['main']
                    for attr in attrs:
                        attrReturn = {}
                        attrTemp = obj+'.'+attr
                        attrItem = cmds.rowColumnLayout(numberOfColumns=1,parent=itemAttrList)
                        cmds.rowColumnLayout(numberOfColumns=3)
                        cmds.textField(text='Target Attr',editable=False,w=titleWidth)
                        targetAttr = cmds.textField(w=inputWidth,height=inputHeight,text=attrTemp)
                        cmds.button(label="X",h=buttonHeight,c=partial(DeleteAttrItem,attrItem))
                        attrReturn['ui'] = attrItem
                        attrReturn['targetAttr'] = targetAttr
                        attrReturn['values'] = []
                        cmds.setParent("..")                        
                        cmds.rowColumnLayout(numberOfColumns=5)
                        for i in range(9):
                            keyTemp = "value"+str(i)
                            inputTemp = cmds.textField(height=inputHeight,width=75,text='')
                            attrReturn['values'].append(inputTemp) 
                        cmds.setParent("..")
                        cmds.setParent("..")
                        Items['items'][itemUI]['attrsData'].append(attrReturn)                 
            else:
                attrTemp = attrData['attr']
                values = attrData['values']
                attrsData = {}
                attrsData[attrTemp] = {}
                attrReturn = {}
                attrItem = cmds.rowColumnLayout(numberOfColumns=1,parent=itemAttrList)
                cmds.rowColumnLayout(numberOfColumns=3)
                cmds.textField(text='Target Attr',editable=False,w=titleWidth)
                targetAttr = cmds.textField(w=inputWidth,height=inputHeight,text=attrTemp)
                cmds.button(label="X",h=buttonHeight,c=partial(DeleteAttrItem,attrItem))
                attrReturn['ui'] = attrItem
                attrReturn['targetAttr'] = targetAttr
                attrReturn['values'] = []
                cmds.setParent("..")                        
                cmds.rowColumnLayout(numberOfColumns=5)
                for i in range(9):
                    key = str(i)
                    if key in values:
                        inputTemp = cmds.textField(height=inputHeight,width=75,text=values[key])
                    else:
                        inputTemp = cmds.textField(height=inputHeight,width=75,text='') 
                    attrReturn['values'].append(inputTemp) 
                cmds.setParent("..")
                cmds.setParent("..")
                Items['items'][itemUI]['attrsData'].append(attrReturn)   
        
        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))

        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Source',editable=False,w=titleWidth)
        source = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("source", ""))
        itemData['Source'] = source
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickSource,source))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Souce Attr',editable=False,w=titleWidth)
        sourceAttr = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("sourceAttr", ""))
        itemData['SourceAttr'] = sourceAttr
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="Add Attr",h=buttonHeight,backgroundColor=(.5,.2,.2),c=partial(AddAttrItem,{}))
        cmds.button(label="X",h=buttonHeight,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.setParent("..")

        itemAttrList = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
        cmds.setParent("..")

        itemData['attrsData'] = []
        Items['items'][itemUI] = itemData
        if 'attrsData' in data:
            for attr in data['attrsData']:
                AddAttrItem({
                    'attr':attr,
                    'values':data['attrsData'][attr]
                })
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")



    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            ModuloSDKRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=400)  
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)




### DRIVEN KEY ###
def DrivenKeyRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        itemData = datas[i]
        driver = itemData['Driver']
        driverAttr = itemData['DriverAttr']
        drivens = itemData['Drivens'].split(';')
        offsetDict = {}
        for driven in drivens:
            offsetGroup = cmds.group(em=True, name=driven+"_SDKGrp")
            cmds.delete(cmds.parentConstraint(driven,offsetGroup, mo=False))
            drivenParent =  cmds.listRelatives(driven,parent=True)
            if drivenParent:
                cmds.parent(offsetGroup,drivenParent)
            cmds.parent(driven,offsetGroup)
            offsetDict[driven] = offsetGroup
        
        for i in range(len(itemData['keyData'])):
            keyData = itemData['keyData'][i]
            driverValue =  float(keyData['driverValue'])
            drivenData = keyData['drivenData']
            for driven in drivenData:
                offsetGroup = offsetDict[driven]
                attrData = drivenData[driven]
                for attr in attrData:
                    attrValue = attrData[attr]
                    drivenAttr = offsetGroup+'.'+attr
                    cmds.setDrivenKeyframe(
                        offsetGroup+'.'+attr,
                        currentDriver=driver+"."+driverAttr,
                        driverValue=driverValue,
                        value=attrValue
                    )
                    cmds.keyTangent(drivenAttr, itt='linear', ott='linear')

def DrivenKeyForm(ui,*arr):
    global sceneData
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']
    SDKUis = {}
    SDKData = {}
    titleWidth = 80
    inputWidth = 233
    inputHeight = 25
    buttonHeight = 25


    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):        
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for ParentUI in SDKUis:
            if 'keyData' in SDKUis[ParentUI]:
                itemData = {}
                DriverUI = SDKUis[ParentUI]['Driver']
                DriverAttrUI = SDKUis[ParentUI]['DriverAttr']
                DirvensUI = SDKUis[ParentUI]['Drivens']
                DrivensAttrsUI =  SDKUis[ParentUI]['DrivenAttrs']
                DriverName = cmds.textField(DriverUI,query=True,text=True)
                DriverAttr = cmds.textField(DriverAttrUI,query=True,text=True)
                Drivens = cmds.scrollField(DirvensUI,query=True,text=True)
                DrivensAttrs = cmds.textField(DrivensAttrsUI,query=True,text=True)
                itemData['Driver'] = DriverName
                itemData['DriverAttr'] = DriverAttr
                itemData['Drivens'] = Drivens
                itemData['DrivenAttrs'] = DrivensAttrs
                itemData['keyData'] = []
                keyData = SDKUis[ParentUI]['keyData']
                for key in keyData:
                    DriverValueUI = keyData[key]['DriverValueUI']
                    DriverValue = cmds.floatField(DriverValueUI,query=True,value=True)
                    keyTemp = {
                        'driverValue':str(DriverValue),
                        'drivenData':{}
                    }
                    for driven in keyData[key]['DrivenUIs']:
                        keyTemp['drivenData'][driven] = {}
                        drivenData = keyData[key]['DrivenUIs'][driven]
                        for attr in drivenData:
                            valueUI = drivenData[attr]
                            keyTemp['drivenData'][driven][attr]= cmds.floatField(valueUI,query=True,value=True)
                    itemData['keyData'].append(keyTemp)
                returnData.append(itemData)
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 80
        inputWidth = 233
        inputHeight = 25
        buttonHeight = 25

        def PickDriver(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                obj = selection[0]
                cmds.textField(ui,edit=True,text=obj)

        def PickDriven(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = ";".join(selection)
                currentContent = cmds.scrollField(ui, query=True, text=True)
                if currentContent !="":
                    cmds.scrollField(ui, edit=True, text=currentContent+"\n"+content)
                else:
                    cmds.scrollField(ui, edit=True, text=content)

        def PickAttrs(ui,*arr):
            attrs = GetAttributeSelected()
            if attrs:
                cmds.textField(ui,edit=True,text=(';').join(attrs['allAttr']))   
            else:
                cmds.textField(ui,edit=True,text='')

        def PickContentAttr(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                obj = selection[0]
                cmds.textField(ui,edit=True,text=obj)   

        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del SDKUis[ui]

        def AddKeyItem(itemUI,data,*arr):

            def GetValue(inputData,*arr):
                obj = cmds.ls(selection=True)
                if obj:
                    obj = obj[0]
                    driven = inputData['driven']
                    itemUI = inputData['itemUI']
                    driverValue = inputData['driverValue']
                    attrs = inputData['attrs']
                    for attr in attrs:
                        attrUI = SDKUis[itemUI]['keyData'][driverValue]['DrivenUIs'][driven][attr]
                        currentValue = cmds.getAttr(obj+'.'+attr)
                        cmds.floatField(attrUI,value = currentValue,edit=True)

            if 'keyData' not in SDKUis[itemUI]:
                SDKUis[itemUI]['keyData'] = {}        
            UIData = SDKUis[itemUI]
            ScrollArea = UIData['ScrollArea']
            Driver = UIData['Driver']
            DriverAttr = UIData['DriverAttr']
            Drivens =  UIData['Drivens']
            DrivenAttrs = UIData['DrivenAttrs']

            driverVal = cmds.textField(Driver,query=True,text=True)
            driverAttrVal = cmds.textField(DriverAttr,query=True,text=True)
            drivensVal = cmds.scrollField(Drivens,query=True,text=True)
            drivensAttrsVal = cmds.textField(DrivenAttrs,query=True,text=True)        
            drivens = drivensVal.split(';')
            drivensAttrs = drivensAttrsVal.split(';')        

            if data == {}:
                driverCurrentValue = cmds.getAttr(driverVal+'.'+driverAttrVal)   
                if str(driverCurrentValue) in SDKUis[itemUI]['keyData']:
                    cmds.deleteUI(SDKUis[itemUI]['keyData'][str(driverCurrentValue)]['ItemUI'])
                    del SDKUis[itemUI]['keyData'][str(driverCurrentValue)]

                ItemUI = cmds.frameLayout(
                    label=driverCurrentValue,
                    parent=ScrollArea,
                    collapsable=True,
                    collapse=True,width=380
                )

                cmds.rowColumnLayout(numberOfColumns=2)
                cmds.textField(text='Driver value',editable=False,width=80,bgc=(0.216, 0.216, 0.216))                  
                driverValueUI = cmds.floatField(value=driverCurrentValue,width=283)
                cmds.setParent('..')

                itemData = {'ItemUI':ItemUI,'DriverValueUI':driverValueUI,}
                cmds.rowColumnLayout(numberOfColumns=1,bgc=(0.15, 0.15, 0.15))
                itemData['DrivenUIs'] = {}
                for driven in drivens:
                    
                    cmds.rowColumnLayout(numberOfColumns=2)
                    cmds.textField(text=driven,editable=False,height=35,width=272,bgc=(0.216, 0.216, 0.216))
                    cmds.button(label="Get Current",h=buttonHeight,width=100,c=partial(GetValue,
                        {
                            'itemUI':itemUI,
                            'driverValue':str(driverCurrentValue),
                            'driven':driven,
                            'attrs':drivensAttrs,
                        }
                    ))
                    cmds.setParent('..')

                    itemData['DrivenUIs'][driven] = {}
                    cmds.rowColumnLayout(numberOfColumns=6)
                    for attr in drivensAttrs:
                        cmds.rowColumnLayout(numberOfColumns=1,width=60)
                        cmds.textField(text=attr,editable=False)
                        if 'drivenData' in data:
                            attrValueUI = cmds.floatField(value = float(data['drivenData'][driven][attr]))
                        else:
                            attrValueUI = cmds.floatField(value = cmds.getAttr(driven+'.'+attr))
                        itemData['DrivenUIs'][driven][attr] = attrValueUI
                        cmds.setParent('..')
                    cmds.setParent('..')
                cmds.setParent('..')
                cmds.setParent('..')
                SDKUis[itemUI]['keyData'][str(driverCurrentValue)] = itemData
            else:
                ItemUI = cmds.frameLayout(
                    label=str(data['driverValue']),
                    parent=ScrollArea,
                    collapsable=True,
                    collapse=True,width=380
                )
                cmds.rowColumnLayout(numberOfColumns=2)
                cmds.textField(text='Driver value',editable=False,width=80,bgc=(0.216, 0.216, 0.216))                  
                driverValueUI = cmds.floatField(value=float(data['driverValue']),width=283)
                cmds.setParent('..')


                itemData = {'ItemUI':ItemUI,'DriverValueUI':driverValueUI}
                cmds.rowColumnLayout(numberOfColumns=1,bgc=(0.15, 0.15, 0.15))
                itemData['DrivenUIs'] = {}
                for driven in drivens:

                    cmds.rowColumnLayout(numberOfColumns=2)
                    cmds.textField(text=driven,editable=False,height=35,width=272,bgc=(0.20, 0.20, 0.20))
                    cmds.button(label="Get Current",h=buttonHeight,width=100,c=partial(GetValue,
                        {
                            'itemUI':itemUI,
                            'driverValue':str(data['driverValue']),
                            'driven':driven,
                            'attrs':drivensAttrs,
                        }
                    ))
                    cmds.setParent('..')

                    itemData['DrivenUIs'][driven] = {}
                    cmds.rowColumnLayout(numberOfColumns=6)
                    for attr in drivensAttrs:
                        cmds.rowColumnLayout(numberOfColumns=1,width=60)
                        cmds.textField(text=attr,editable=False)
                        attrValueUI = cmds.floatField(value = float(data['drivenData'][driven][attr]))
                        itemData['DrivenUIs'][driven][attr] = attrValueUI
                        cmds.setParent('..')
                    cmds.setParent('..')

                cmds.setParent('..')
                cmds.setParent('..')                
                SDKUis[itemUI]['keyData'][str(data['driverValue'])] = itemData
            cmds.separator(height=2, style='none')
        #itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15))    
        itemUI = cmds.frameLayout(
            label=data.get("Driver", "")+' | '+data.get("Drivens", ""),
            parent=parentUI,
            collapsable=True,
            collapse=True,
            width=380,
            bgc=(0.4,0.4,0.0)
        )
        
        SDKUis[itemUI] = {}
        itemData = {}
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Driver',editable=False,w=titleWidth)
        Driver = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Driver", ""))
        itemData['Driver'] = Driver
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickDriver,Driver))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Driver Attrs',editable=False,w=titleWidth)
        DriverAttr = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("DriverAttr", ""))
        itemData['DriverAttr'] = DriverAttr
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickAttrs,DriverAttr))
        cmds.setParent("..")
        cmds.setParent("..")


        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Driven',editable=False,w=titleWidth)
        Drivens = cmds.scrollField(wordWrap=True,height=80,w=inputWidth,text=data.get("Drivens", ""))
        itemData['Drivens'] = Drivens
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickDriven,Drivens))
        cmds.setParent("..")
        cmds.setParent("..")


        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Driven Attrs',editable=False,w=titleWidth)
        DrivenAttrs = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("DrivenAttrs", ""))
        itemData['DrivenAttrs'] = DrivenAttrs
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickAttrs,DrivenAttrs))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="Add",h=buttonHeight,w=190,c=partial(AddKeyItem,itemUI,{}))
        cmds.button(label="X",h=buttonHeight,w=190,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))        
        cmds.setParent("..")

        ScrollArea = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=300)
        itemData['ScrollArea'] = ScrollArea
        cmds.setParent("..")

        SDKUis[itemUI] = itemData
        
        
        if data and ('keyData' in data):
            for i in range(len(data['keyData'])):
                AddKeyItem(itemUI,data['keyData'][i])

        
        cmds.setParent("..")    
        cmds.setParent("..")
        cmds.separator(height=10, style='none')


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            DrivenKeyRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=600)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=132)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)




### PARENT CONSTRAINT ###
def ParentConstraintRun(input,*arr):
    data =  None
    if isinstance(input, dict) or isinstance(input,list):
        data = input
    elif isinstance(input, str):
        data = NLTA_General.readJsonFile(input)
    if data:
        def ConstraintDefault(pair):
            parentCon = cmds.parentConstraint(pair[0], pair[1], mo=True, name=pair[0] +"_"+pair[1]+"_parentConstraint")[0]        
            cmds.setAttr(parentCon+".interpType", 2)
            return(parentCon)

        def ConstraintRotateOrder(pair):    
            source = pair[0]
            dest = pair[1]
            if cmds.objExists(source) and cmds.objExists(dest):
                parent = "ParentConstraint_"+source+"_"+dest+"_Grp"
                offset = "ParentConstraint_"+source+"-"+dest+"_Offset"
                locator1 = "ParentConstraint_"+source+"-"+dest+"_Loc"
                if cmds.objExists(parent):
                    cmds.delete(parent)               

                parent = cmds.group(n=parent,empty=True)
                cmds.matchTransform(parent,source,rot=True,pos=True)
                cmds.select(clear=True)
                locator1 = cmds.group(n=locator1,empty=True)
                offset = cmds.group(locator1,n=offset)
                cmds.matchTransform(offset,dest,rot=True,pos=True)
                cmds.parent(offset,parent)

                constaint = cmds.parentConstraint(source,parent,mo=True)[0]
                cmds.setAttr(constaint+".interpType", 2)
                try:
                    cmds.parent(constaint,parent)
                except:pass
                constaint = cmds.parentConstraint(locator1,dest,mo=True)[0]#constaint = cmds.pointConstraint(locator1,dest,mo=True,skip="y")
                cmds.setAttr(constaint+".interpType", 2)
                try:
                    cmds.parent(constaint,parent)
                except:pass
                
                cmds.connectAttr(source+'.scale',parent+'.scale',f=True)          
                cmds.setAttr(dest+".sx", lock=False)
                cmds.setAttr(dest+".sy", lock=False)
                cmds.setAttr(dest+".sz", lock=False)
                constaintScale = cmds.scaleConstraint(locator1,dest,mo=True)
                cmds.parent(constaintScale,parent)
                return(parent)

        for i in range(len(data)):

            itemData =  data[i]
            rotateOrder = itemData['rotateOrder']
            contentName = itemData['contentName']
            contentParent = itemData['contentParent']
            pairs = itemData['pairs']
            print(pairs)
            if contentName != "":
                if not cmds.objExists(contentName):
                    cmds.group(empty=True,name=contentName)
            for a in range(len(pairs)):
                pairTemp = pairs[a]
                if rotateOrder:
                    consTemp = ConstraintRotateOrder(pairTemp)
                else:
                    consTemp =  ConstraintDefault(pairTemp)
                cmds.parent(consTemp,contentName)


def ParentConstraintForm(ui,*arr):
    global sceneData

    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']
    Items = {}

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        dataReturn = []
        for key in Items:
            itemData = Items[key]
            rotateOrder = cmds.checkBox(itemData['rotateOrder'],query=True,value=True)
            contentName = cmds.textField(itemData['contentName'],query=True,text=True)
            contentParent = cmds.textField(itemData['contentParent'],query=True,text=True)
            pairs = []
            for i in range(len(itemData['pairs'])):
                pairs.append([
                    cmds.textField(itemData['pairs'][i][0],query=True,text=True),
                    cmds.textField(itemData['pairs'][i][1],query=True,text=True)
                ])
            dataReturn.append({
                'rotateOrder':rotateOrder,
                'contentName':contentName,
                'contentParent':contentParent,
                'pairs':pairs
            })


        return(dataReturn) 

    def Delete(Item,*arr):
        cmds.deleteUI(Item)
        del Items[Item]

    def Add(data,*arr):
        def CreatePair(pairs,*arr):
            def ChangeItem(ui,*arr):
                objs = cmds.ls(selection=True)
                if objs:
                    obj = objs[0]
                    cmds.textField(ui,text=obj,edit=True)

            def SelectPair(driverUITemp,drivenUITemp,*arr):
                driverName = cmds.textField(driverUITemp,query=True,text=True)
                drivenName = cmds.textField(drivenUITemp,query=True,text=True)
                cmds.select(clear=True)
                for obj in [driverName,drivenName]:
                    if cmds.objExists(obj):
                        cmds.select(obj,add=True)

            def DeletePair(pairUITemp,driverUITemp,drivenUITemp,*arr):
                cmds.deleteUI(pairUITemp)
                if [driverUITemp,drivenUITemp] in Items[Item]['pairs']:
                    Items[Item]['pairs'].remove([driverUITemp,drivenUITemp])           
            for b in range(len(pairs)):
                driver = pairs[b][0]
                driven = pairs[b][1]
                pairUI = cmds.rowColumnLayout(numberOfColumns=6,parent=ItemScroll)
                driverUI = cmds.textField(text=driver,width=140)
                cmds.button(label="->",c=partial(ChangeItem,driverUI))
                drivenUI = cmds.textField(text=driven,width=140)
                cmds.button(label="->",c=partial(ChangeItem,drivenUI))
                cmds.button(label="->|",c=partial(SelectPair,driverUI,drivenUI))
                cmds.button(label="X",c=partial(DeletePair,pairUI,driverUI,drivenUI),backgroundColor=(0.3,0,0),width=25,al='center')
                cmds.setParent('..')
                Items[Item]['pairs'].append([driverUI,drivenUI])

        def SelectPair(data,*arr):
            sel = cmds.ls(selection=True)
            count = len(sel)
            if count < 2:
                cmds.warning("Please select at least two objects to split to array.")
                return
            mid = count // 2
            drivers = sel[:mid]
            drivens = sel[mid:]
            if len(drivers) != len(drivens):
                cmds.warning("Drivers and drivens amount are not equal.")
                return
            pairs = []
            for a in range(len(drivers)):
                pairs.append([drivers[a],drivens[a]])
            CreatePair(pairs)

        def SelectHierachyPair(*arr):
            import maya.api.OpenMaya as om2  
            def GetJointHierarchy(root):
                joints = cmds.listRelatives(root, allDescendents=True,type=['joint']) or []
                joints.append(root)
                return(joints[::-1])

            def GetWorldPosition(joint):
                selList = om2.MSelectionList()
                selList.add(joint)
                dagPath = selList.getDagPath(0)
                transform = om2.MFnTransform(dagPath)
                return transform.translation(om2.MSpace.kWorld)

            def PairClosestJoints(jointsA, jointsB):
                pairs = []
                for jointA in jointsA:
                    posA = GetWorldPosition(jointA)
                    closestJoint = None
                    minDistance = float('inf')

                    for jointB in jointsB:
                        #if jointB in usedB:
                        #   continue
                        posB = GetWorldPosition(jointB)
                        distance = (posA - posB).length()

                        if distance < minDistance:
                            minDistance = distance
                            closestJoint = jointB

                    if closestJoint:
                        pairs.append((jointA, closestJoint))
                return pairs

            selection = cmds.ls(selection=True)
            if len(selection) != 2:
                cmds.error("Please select 2 root joint from 2 different joint hierarchy.")
                return
            rootA, rootB = selection
            jointsA = GetJointHierarchy(rootA)
            jointsB = GetJointHierarchy(rootB)
            pairs = PairClosestJoints(jointsA, jointsB)
            firstJoints = [a for a, b in pairs]
            secondJoints = [b for a, b in pairs]

            from collections import Counter
            counted = Counter(secondJoints)
            duplicate = [item for item, count in counted.items() if count > 1]

            for i in range(len(firstJoints)):
                if secondJoints[i] not in duplicate:
                    cmds.select(clear=True)
                    cmds.select(firstJoints)
                    cmds.select(secondJoints, add=True)
                    CreatePair([[firstJoints[i],secondJoints[i]]])
                else:
                    CreatePair([[firstJoints[i],""]])
            cmds.select(selection)

        Item = cmds.rowColumnLayout(numberOfColumns=1,parent=mainScroll)
        cmds.rowColumnLayout(numberOfColumns=2,parent=Item)
        cmds.textField(text='Rotate Order',editable=False,width=130)
        rotateOrderUI = cmds.checkBox(value=False,label="")
        cmds.textField(text='Group Offset',editable=False)
        contentNameUI = cmds.textField(width=245,text="ParentConstraintContent_Grp")
        cmds.textField(text='Group Offset Content',editable=False,width=100)
        contentParentUI = cmds.textField(width=245,text="")
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfColumns=3,parent=Item)
        cmds.button(label="Select",c=partial(SelectPair,{}))
        cmds.button(label="Select Hierarchy",c=SelectHierachyPair)
        cmds.button(label="Delete",c=partial(Delete,Item))        
        cmds.setParent('..')
        ItemScroll = cmds.scrollLayout(horizontalScrollBarThickness=4,w=380,h=300,parent=Item)        
        cmds.setParent('..')
        Items[Item] = {
            'rotateOrder':rotateOrderUI,
            'contentName':contentNameUI,
            'contentParent':contentParentUI,
            'pairs':[]
        }
        if data:
            cmds.checkBox(rotateOrderUI,value=data['rotateOrder'],edit=True)
            cmds.textField(contentNameUI,text=data['contentName'],edit=True)
            cmds.textField(contentParentUI,text=data['contentParent'],edit=True)
            CreatePair(data['pairs'])


    def Run(*arr):
        data = GetData()
        ParentConstraintRun(data)

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        children = cmds.layout(mainScroll,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        print(data)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1)#Start
    cmds.rowColumnLayout(numberOfColumns=1)
    mainScroll = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=300)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)#1
    cmds.button(label="Add",c=partial(Add,{}),w=400)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")#End
    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)

### SWITCH IK FK RUN
def SwitchIKFKRun(input,*arr):
    datas =  None
    if isinstance(input, dict):
        datas = [input]
    elif isinstance(input, str):
        datas = NLTA_General.readJsonFile(input)
    for i in range(len(datas)):
        data = datas[i]
        ctrl = data['ContentAttr']
        if not cmds.attributeQuery(data['AttrPick'], node=ctrl, exists=True):
            cmds.addAttr(ctrl, ln=data['AttrPick'], at='enum', en=data['Options'])
            cmds.setAttr(ctrl+'.'+data['AttrPick'], e=True, keyable=True)
        objectArrays = data['Objects'].split('\n')
        options = data['Options'].split(':')[0:-1]
        
        for i in range(len(options)):
            if objectArrays[i] != '':
                objs = objectArrays[i].split(';')
                condition = cmds.shadingNode("condition", asUtility=True)
                cmds.connectAttr(ctrl+"."+data['AttrPick'], condition+".firstTerm", force=True)
                cmds.setAttr(condition+".secondTerm",i)
                cmds.setAttr(condition+".colorIfTrueR",1)
                cmds.setAttr(condition+".colorIfFalseR",0)
                for obj in objs:
                    objToConnect = []
                    if data['MeshOnly']:
                        objToConnect.append(obj)
                        objChildren = cmds.listRelatives(obj,children=True,type="mesh")
                        if objChildren:
                            objToConnect.extend(objChildren)
                    else:
                        grp = cmds.group(empty=True,name=NLTA_General.GetUniqueName("{}_VisSwitchOffsetGrp".format(obj)))
                        cmds.delete(cmds.parentConstraint(obj, grp))                   
                        objParent = cmds.listRelatives(obj,parent=True)   
                        if objParent:
                            objParent = cmds.listRelatives(obj,parent=True)[0]
                            cmds.parent(grp,objParent)
                            NLTA_General.ZeroTransform(grp)                            
                        if not data["InorgeChildren"]:
                            objChildren = cmds.listRelatives(obj,children=True,type='transform')
                            if objChildren:                            
                                grpReplace = cmds.group(empty=True,name=NLTA_General.GetUniqueName("{}_VisSwitchReplaceGrp".format(obj)))
                                cmds.delete(cmds.parentConstraint(obj,grpReplace))
                                if objParent:
                                    cmds.parent(grpReplace,objParent)
                                    NLTA_General.ZeroTransform(grpReplace)                     
                                cmds.parent(objChildren,grpReplace)                        
                                constrTemp = cmds.parentConstraint(obj,grpReplace,mo=True)[0]                  
                                cmds.setAttr(constrTemp+'.interpType',2)
                                cmds.scaleConstraint(obj,grpReplace,mo=True) 
                        cmds.parent(obj,grp)
                        objToConnect.append(grp)
                    for objTemp in objToConnect:
                        cmds.connectAttr(condition+".outColorR",objTemp+'.visibility', force=True)
                    

def SwitchIKFKForm(ui,*arr):
    global sceneData
    visibleItems = {
        'order':[],
        'items':{},
    }
    type = sceneData[ui]['type']
    name = sceneData[ui]['name']
    form = sceneData[ui]['form']
    path = sceneData[ui]['path']

    if cmds.window(form, exists=True):
        cmds.deleteUI(form)
    if os.path.exists(path):
        data = NLTA_General.readJsonFile(path)
    else:
        data = []

    def ChangeName(nameUI,parentUI,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        cmds.button(sceneData[parentUI]['textShow'],edit=True,label=value)
        sceneData[parentUI]['name'] = value

    def ChangePath(pathUI,parentUI,*arr):
        cmds.setFocus(browerUI)        
        path = cmds.scrollField(pathUI,query=True,text=True)
        sceneData[parentUI]['path'] = path
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        Load(path)

    def GetData(*arr):        
        returnData = []
        for item in visibleItems['items']:
            Objects=cmds.scrollField(visibleItems['items'][item]['Objects'],query=True,text=True)
            ContentAttr=cmds.textField(visibleItems['items'][item]['ContentAttr'],query=True,text=True)
            AttrPick=cmds.textField(visibleItems['items'][item]['AttrPick'],query=True,text=True)
            Options=cmds.textField(visibleItems['items'][item]['Options'],query=True,text=True)
            InorgeChildren = cmds.checkBox(visibleItems['items'][item]['InorgeChildren'],query=True,value=True)
            MeshOnly = cmds.checkBox(visibleItems['items'][item]['MeshOnly'],query=True,value=True)
            returnData.append({
                'Objects':Objects,
                'ContentAttr':ContentAttr,
                'AttrPick':AttrPick,
                'Options':Options,
                'InorgeChildren':InorgeChildren,
                "MeshOnly":MeshOnly,
            })
        return(returnData)

    def Delete(attr,*arr):
        cmds.deleteUI(attributeUIs[attr]['parent'])        
        del attributeUIs[attr]
        del attributeData[attr]

    def Create(data,*arr):
        if data['attr'] not in attributeUIs:
            item = cmds.rowColumnLayout(numberOfColumns=2,parent=valueDefaultUI)# Open Item
            cmds.rowColumnLayout(numberOfColumns=3)
            attr = cmds.textField(text=data.get("attr", ""),width=280)
            value = cmds.textField(text=data.get("value", ""),width=50)
            cmds.button(label="X",c=partial(Delete,data['attr']),width=50)
            attributeUIs[data['attr']] = {
                'parent':item,
                'attr':attr,
                'value':value
            }
            attributeData[data['attr']] = data['value']
            cmds.setParent("..")
            cmds.setParent("..")#Close
        else:
            cmds.textField(attributeUIs[data['attr']]['value'],edit=True,text=data['value'])

    def Add(data,*arr):
        titleWidth = 90
        inputWidth = 230
        inputHeight = 35
        buttonHeight = 35
        def PickObjects(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                content = ";".join(selection)
                currentContent = cmds.scrollField(ui, query=True, text=True)
                if currentContent !="":
                    cmds.scrollField(ui, edit=True, text=currentContent+"\n"+content)
                else:
                    cmds.scrollField(ui, edit=True, text=content)   

        def PickContentAttr(ui,*arr):
            selection = cmds.ls(selection=True) or []
            if selection:
                obj = selection[0]
                cmds.textField(ui,edit=True,text=obj)   

        def DeleteItem(ui,*arr):
            cmds.deleteUI(ui)
            del visibleItems['items'][ui]
            visibleItems['order'].remove(ui)

        itemData = {}   
        itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=parentUI,backgroundColor=(0.15, 0.15, 0.15),width=390)

        cmds.rowColumnLayout(numberOfColumns=1)


        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Options',editable=False,w=titleWidth)
        options = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("Options", ""))
        itemData['Options'] = options
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Objects',editable=False,w=titleWidth)
        Objects = cmds.scrollField(wordWrap=True,height=80,w=inputWidth,text=data.get("Objects", ""))
        itemData['Objects'] = Objects
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="+",w=30,h=buttonHeight,c=partial(PickObjects,Objects))
        cmds.button(label="*",w=30,h=buttonHeight)
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Content Attr',editable=False,w=titleWidth)
        ContentAttr =cmds.textField(w=inputWidth,height=inputHeight,text=data.get("ContentAttr", ""))
        itemData['ContentAttr'] = ContentAttr
        cmds.setParent("..")
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label="->",w=30,h=buttonHeight,c=partial(PickContentAttr,ContentAttr))
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Attr Pick',editable=False,w=titleWidth)
        attrPick = cmds.textField(w=inputWidth,height=inputHeight,text=data.get("AttrPick", ""))
        itemData['AttrPick'] = attrPick
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Inorge Children',editable=False,w=titleWidth)
        InorgeChildren = cmds.checkBox("InorgeChildren", value=data.get("InorgeChildren",True))
        itemData['InorgeChildren'] = InorgeChildren
        cmds.setParent("..")

        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField(text='Mesh Only',editable=False,w=titleWidth)
        MeshOnly = cmds.checkBox("MeshOnly", value=data.get("MeshOnly",True))
        itemData["MeshOnly"] = MeshOnly
        cmds.setParent("..")


        cmds.button(label="X",h=buttonHeight,w=35,backgroundColor=(.5,.2,.2),c=partial(DeleteItem,itemUI))
        cmds.separator(height=10, style='none')

        cmds.setParent("..")    
        cmds.setParent("..")

        visibleItems['items'][itemUI] = itemData
        visibleItems['order'].append(itemUI)


    def Run(*arr):
        data = GetData()
        for i in range(len(data)):
            VisibleSwitchRun(data[i])

    def Save(*arr):
        data = GetData()
        path = cmds.scrollField(pathUI,query=True,text=True)
        if not os.path.exists(path):
            NLTA_General.writeJsonFile(path,{})
        NLTA_General.writeJsonFile(path,data)
        SaveSceneData()

    def Load(path,*arr):
        global visibleItems
        visibleItems = {
            'order':[],
            'items':{},
        }
        children = cmds.layout(parentUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)
        data = NLTA_General.readJsonFile(path)
        if data:
            for i in range(len(data)):
                Add(data[i])

    cmds.window(form, title=name)
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.button(label="Run",c=Run,width=100)
    cmds.button(label="Save",c=Save,width=100)
    browerUI = cmds.button(label="Brower",width=100)
    openScriptUI = cmds.button(label="Edit File",width=100)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField(text='Name',editable=False,width=100)
    nameUI = cmds.textField(text=sceneData[ui]['name'],width=300)
    cmds.textField(text='Path',editable=False)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,nameUI,ui))
    pathUI = cmds.scrollField(text=sceneData[ui]['path'],wordWrap=True,height=80,editable=False)
    cmds.scrollField(pathUI,edit=True,cc=partial(ChangePath,pathUI,ui))
    cmds.setParent("..")

    cmds.separator(height=10, style='none')

    cmds.rowColumnLayout(numberOfColumns=1,backgroundColor=(0.2, 0.2, 0.2),)
    parentUI = cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=500)
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3)#1
    cmds.button(label="Add",c=partial(Add,{}),w=400)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")
    Load(path)

    cmds.button(browerUI,edit=True,c=partial(Browser,pathUI))
    cmds.button(openScriptUI,edit=True,c=partial(OpenSublime,pathUI))
    cmds.setParent("..")
    cmds.showWindow(form)


#########################################################

def RunCurrentPostScript(*arr):
    folderTemp = os.path.dirname(pm.sceneName())
    if not folderTemp:
        folderTemp = pm.mel.eval("SaveSceneAs;")
    if folderTemp:
        folderTemp = os.path.dirname(pm.sceneName())
        NLTA_General.RunScriptFile(folderTemp+'/PostScript.py')

def RunCurrentAfterScript(*arr):
    folderTemp = os.path.dirname(pm.sceneName())
    if not folderTemp:
        folderTemp = pm.mel.eval("SaveSceneAs;")
    if folderTemp:
        folderTemp = os.path.dirname(pm.sceneName())
        NLTA_General.RunScriptFile(folderTemp+'/AfterScript.py')

def RunUpPostScript(*arr):
    folderTemp = os.path.dirname(pm.sceneName())
    if not folderTemp:
        folderTemp = pm.mel.eval("SaveSceneAs;")
    if folderTemp:
        folderTemp = ("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])
        NLTA_General.RunScriptFile(folderTemp+'/PostScript.py')

def RunUpAfterScript(*arr):
    folderTemp = os.path.dirname(pm.sceneName())
    if not folderTemp:
        folderTemp = pm.mel.eval("SaveSceneAs;")
    if folderTemp:
        folderTemp = ("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])
        NLTA_General.RunScriptFile(folderTemp+'/AfterScript.py')