import os
import maya.cmds as cmds
import pymel.core as pm
from functools import partial
from datetime import datetime

import NLTA_General,NLTA_UI
for module in [NLTA_General,NLTA_UI]:
    try:
        importlib.reload(module)
    except:
        from importlib import reload
        reload(module)

ITEMS = {
    "items":{},
    "order":[]
}

def Load(data,listUI,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    path = newestData["path"]
    if ".json" in path:
        children = cmds.layout(listUI,q=True, ca=True) or []
        for child in children:
            if cmds.control(child, exists=True):
                cmds.deleteUI(child)        
        itemDatas = NLTA_General.readJsonFile(path)
        if itemDatas:
            for i in range(len(itemDatas)):
                Add(listUI,itemDatas[i])

def Form(data,*arr):
    def Save(data, *arr):
        itemData = NLTA_General.JsonGetByID({
            "path":data["sceneDataPath"]+"/ScenePatternData.json",
            "id":data["id"]
        })
        returnData = NLTA_UI.GetData(ITEMS['items'])
        NLTA_General.writeJsonFile(itemData["path"],returnData)

    mainForm = NLTA_General.LoadModule("Scene_Form")
    dataBack = mainForm.Create(data)
    buttonUI = dataBack["buttonUI"]
    listUI = dataBack["listUI"]

    cmds.rowColumnLayout(numberOfColumns=3,parent=buttonUI)
    cmds.button(label="Add",width=130,c=partial(Add,listUI,{}))
    cmds.button(label="Save", width=130,c=partial(Save,data))
    cmds.button(label="Run",width=130, c=partial(Run,data))
    cmds.setParent("..")
    Load(data,listUI)

###########################

def DefaultSetting(path,*arr):
    moduleName = os.path.basename(__file__).replace(".py","")
    ext = "json"
    name = "Rename"
    return({
        "ext":ext,
        "path":path+moduleName+"."+ext,
        "moduleName":moduleName,
        "order":0,
        "title":name,
        "name":name,
        "id":datetime.now().strftime("%Y%m%d%H%M%S")
    })

def Run(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    for i in range(len(datas)):
        data = datas[i]
        oldName = data["oldName"]
        newName = data["newName"]
        if cmds.objExists(oldName):
            cmds.rename(oldName,newName)

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def GetAttributeValue(attributeUI,valueUI,*arr):
        data = NLTA_UI.GetSelectedAttribute()
        if data["main"]:
            fullAttr = data["objs"][0]+"."+data["main"][0]
            value = cmds.getAttr(fullAttr)
            cmds.textField(attributeUI,edit=True,text=fullAttr)
            cmds.textField(valueUI,edit=True,text=value)
        else:
            Print("Please select a attribute")

    def SelectObject(attributeUI,*arr):
        text = cmds.textField(attributeUI,query=True,text=True)
        if text:
            obj = text.split(".")[0]
            cmds.select(obj)

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI)

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,260),(3,35)]) #--

    cmds.textField(text='Attribute',editable=False)
    cmds.rowColumnLayout(nc=1)
    itemData['oldName'] = cmds.textField(text=data.get("oldName",""),width=255,height=30)
    itemData['newName'] = cmds.textField(text=data.get("newName",""),height=30)
    cmds.setParent("..")
    cmds.rowColumnLayout(1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['oldName']))
    cmds.button(label="X",w=30,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.setParent("..")    

    cmds.setParent("..") #--

    
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










