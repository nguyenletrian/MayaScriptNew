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

def DefaultSetting(path,*arr):
    moduleName = os.path.basename(__file__).replace(".py","")
    ext = "json"
    name = "Deform Sine"
    return({
        "ext":ext,
        "path":path+moduleName+"."+ext,
        "moduleName":moduleName,
        "order":0,
        "title":name,
        "name":name,
        "id":datetime.now().strftime("%Y%m%d%H%M%S")
    })


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

def Run(data, *arr):
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"] + "/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return
    for data in datas:
        parent = data["parent"]
        holder = data["attrHolder"]
        attrName = data["attrName"]
        curve = data["curve"]
        sineHandle, sineNode = cmds.nonLinear(curve,type="sine",name=curve +"_SineDeform")
        if cmds.objExists(parent):
            cmds.parent(sineNode, parent)

        separator = attrName+"Ops"
        if not cmds.attributeQuery(separator, node=holder, exists=True):
            cmds.addAttr(holder,ln=separator,at="enum",en="--------------",)
            cmds.setAttr(f"{holder}.{separator}", e=True, channelBox=True)


        # Envelope
        envAttr = attrName + "_Active"
        if not cmds.attributeQuery(envAttr, node=holder, exists=True):
            cmds.addAttr(holder,ln=envAttr,at="bool",dv=0,k=True)
        cmds.connectAttr(f"{holder}.{envAttr}",f"{sineHandle}.envelope",force=True)

        # Offset
        offsetAttr = attrName + "_Offset"
        if not cmds.attributeQuery(offsetAttr, node=holder, exists=True):
            cmds.addAttr(holder, ln=offsetAttr, at="double", k=True)
        cmds.connectAttr(f"{holder}.{offsetAttr}",f"{sineHandle}.offset",force=True)

        # Visibility
        visAttr = attrName + "_Visible"
        if not cmds.attributeQuery(visAttr, node=holder, exists=True):
            cmds.addAttr(holder,ln=visAttr,at="bool",dv=0,k=True)
        cmds.connectAttr(f"{holder}.{visAttr}",f"{sineNode}.visibility",force=True)

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)]) #--

    cmds.textField(text='Parent',editable=False)
    itemData["parent"] = cmds.textField(text=data.get('parent', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['parent']))

    cmds.textField(text='Attr Holder',editable=False)
    itemData['attrHolder'] = cmds.textField(text=data.get('attrHolder', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['attrHolder']))

    cmds.textField(text='Curve',editable=False)
    itemData['curve'] = cmds.textField(text=data.get('curve', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['curve']))

    cmds.textField(text="Attr Name",editable=False)
    itemData["attrName"] = cmds.textField(text=data.get("attrName",""))
    cmds.text(label="")

    cmds.setParent("..") #--
    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










