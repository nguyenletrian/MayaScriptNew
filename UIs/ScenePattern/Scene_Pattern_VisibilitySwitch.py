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
    name = "Visibility Switch"
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

def Run(data, *arr):
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"] + "/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return
    for data in datas:
        ctrl = data["contentAttr"]
        if not cmds.attributeQuery(data["attrPick"], node=ctrl, exists=True):
            cmds.addAttr(ctrl,ln=data["attrPick"],at="enum",en=data["options"])
            cmds.setAttr(ctrl + "." + data["attrPick"], e=True, keyable=True)
        objectArrays = data["objects"].splitlines()
        options = [x.strip()for x in data["options"].split(":")if x.strip()]
        for index, option in enumerate(options):
            if index >= len(objectArrays):
                continue
            if not objectArrays[index]:
                continue
            condition = cmds.shadingNode("condition", asUtility=True)
            cmds.connectAttr(ctrl + "." + data["attrPick"],condition + ".firstTerm",force=True)
            cmds.setAttr(condition + ".secondTerm", index)
            cmds.setAttr(condition + ".colorIfTrueR", 1)
            cmds.setAttr(condition + ".colorIfFalseR", 0)
            objs = [x.strip() for x in objectArrays[index].split(";") if x.strip()]
            for obj in objs:
                objToConnect = []
                if data["meshOnly"]:
                    objToConnect.append(obj)
                    meshes = cmds.listRelatives(obj,children=True,type="mesh") or []
                    objToConnect.extend(meshes)
                else:
                    grp = cmds.group(em=True,name=NLTA_General.GetUniqueName("{}_VisSwitchOffsetGrp".format(obj)))
                    cmds.delete(cmds.parentConstraint(obj, grp))
                    parent = cmds.listRelatives(obj, parent=True)
                    if parent:
                        parent = parent[0]
                        cmds.parent(grp, parent)
                        NLTA_General.ZeroTransform(grp)
                    if data["ignoreChildren"]:
                        children = cmds.listRelatives(obj,children=True,type="transform") or []
                        if children:
                            replaceGrp = cmds.group(em=True,name=NLTA_General.GetUniqueName("{}_VisSwitchReplaceGrp".format(obj)))
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
                    cmds.connectAttr(condition + ".outColorR",target + ".visibility",force=True)

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
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObjectSemi, itemData["objects"]))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectSemiAdd, itemData["objects"]))
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
    cmds.textField(text="Attr Pick", editable=False)
    itemData["attrPick"] = cmds.textField(text=data.get("attrPick",""))
    cmds.setParent("..")

    # Options
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Options", editable=False)
    itemData["options"] = cmds.textField(text=data.get("options",""))
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