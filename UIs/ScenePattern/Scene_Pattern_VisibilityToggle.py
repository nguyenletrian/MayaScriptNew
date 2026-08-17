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
    name = "Visibility Toggle"
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
    def Save(data,*arr):
        itemData = NLTA_General.JsonGetByID({
            "path":data["sceneDataPath"]+"/ScenePatternData.json",
            "id":data["id"]
        })
        saveData = NLTA_UI.GetData(ITEMS["items"])
        NLTA_General.writeJsonFile(itemData["path"],saveData)
    mainForm = NLTA_General.LoadModule("Scene_Form")
    dataBack = mainForm.Create(data)
    buttonUI = dataBack["buttonUI"]
    listUI = dataBack["listUI"]
    cmds.rowColumnLayout(numberOfColumns=4,parent=buttonUI)
    cmds.button(label="Add",width=130,c=partial(Add,listUI,{}))
    cmds.button(label="Save", width=130,c=partial(Save,data))
    cmds.button(label="Run",width=130, c=partial(Run,data))
    cmds.setParent("..")
    Load(data,listUI)

def Run(data, *args):
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"] + "/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return
    for data in datas:
        print(data)
        ctrl = data["contentAttr"]
        attr = data["attribute"]
        if not cmds.objExists(ctrl):
            continue
        if not cmds.attributeQuery(attr, node=ctrl, exists=True):
            cmds.addAttr(ctrl,ln=attr,at="bool",dv=True,k=True)
        objects = data["objects"].splitlines()
        for obj in objects:
            obj = obj.strip()
            if not obj or not cmds.objExists(obj):
                continue
            objToConnect = []
            if data["meshOnly"]:
                objToConnect.append(obj)
                meshes = cmds.listRelatives(obj,children=True,type="mesh") or []
                objToConnect.extend(meshes)
            else:
                grp = cmds.group(em=True,name=NLTA_General.GetUniqueName("{}_VisToggleOffsetGrp".format(obj)))
                cmds.delete(cmds.parentConstraint(obj, grp))
                parent = cmds.listRelatives(obj,parent=True,type="transform")
                if parent:
                    parent = parent[0]
                    cmds.parent(grp, parent)
                    NLTA_General.ZeroTransform(grp)
                if data["ignoreChildren"]:
                    children = cmds.listRelatives(obj,children=True,type="transform") or []
                    if children:
                        replaceGrp = cmds.group(em=True,name=NLTA_General.GetUniqueName("{}_VisToggleReplaceGrp".format(obj)))
                        cmds.delete(cmds.parentConstraint(obj, replaceGrp))
                        if parent:
                            cmds.parent(replaceGrp, parent)
                            NLTA_General.ZeroTransform(replaceGrp)
                        cmds.parent(children, replaceGrp)
                        pc = cmds.parentConstraint(obj,replaceGrp,mo=True)[0]
                        cmds.setAttr(pc + ".interpType", 2)
                        cmds.scaleConstraint(obj,replaceGrp,mo=True)
                cmds.parent(obj, grp)
                objToConnect.append(grp)
            for target in objToConnect:
                plug = "{}.visibility".format(target)
                source = "{}.{}".format(ctrl, attr)
                if cmds.isConnected(source, plug):
                    continue
                cmds.connectAttr(source,plug,force=True)

def Add(listUI, data, *args):
    global ITEMS
    def Delete(ui, *args):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS["items"][ui]
        ITEMS["order"].remove(ui)

    itemData = {}
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))

    cmds.rowColumnLayout(numberOfColumns=1)
    # Objects
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Objects", editable=False)
    itemData["objects"] = cmds.scrollField(text=data.get("objects",""),h=80)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject, itemData["objects"]))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd, itemData["objects"]))
    cmds.setParent("..")
    cmds.setParent("..")

    # Content Attr
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Content", editable=False)
    itemData["contentAttr"] = cmds.textField(text=data.get("contentAttr",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject, itemData["contentAttr"]))
    cmds.setParent("..")

    # Attr Pick
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Attribute", editable=False)
    itemData["attribute"] = cmds.textField(text=data.get("attribute",""))
    cmds.setParent("..")

    # Ignore Children
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Ignore Child", editable=False)
    itemData["ignoreChildren"] = cmds.checkBox(label="",value=data.get("ignoreChildren", True))
    cmds.setParent("..")

    # Mesh Only
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Mesh Only", editable=False)
    itemData["meshOnly"] = cmds.checkBox(label="",value=data.get("meshOnly", False))
    cmds.setParent("..")

    cmds.button(label="X",w=380,bgc=(0.5,0.2,0.2),c=partial(Delete, itemUI))

    cmds.setParent("..")
    cmds.setParent("..")

    ITEMS["items"][itemUI] = itemData
    ITEMS["order"].append(itemUI)