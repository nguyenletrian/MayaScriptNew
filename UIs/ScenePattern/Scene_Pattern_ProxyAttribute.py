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
    name = "ProxyAttribute"
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

def Form(data,*args):
    def Save(data,*args):
        itemData = NLTA_General.JsonGetByID({
            "path": data["sceneDataPath"]+"/ScenePatternData.json",
            "id": data["id"]
        })
        saveData = NLTA_UI.GetData(ITEMS["items"])
        NLTA_General.writeJsonFile(itemData["path"],saveData)

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

def Run(data,*args):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return
    for itemData in datas:
        source = itemData["source"]
        sourceAttr = itemData["sourceAttr"]
        targetAttr = itemData["targetAttr"]
        targets = [
            x.strip()
            for x in itemData["targets"].split("\n")
            if x.strip()
        ]
        sourcePlug = "{}.{}".format(source,sourceAttr)
        if not cmds.objExists(sourcePlug):
            cmds.warning("Missing source attr : {}".format(sourcePlug))
            continue
        for target in targets:
            if not cmds.objExists(target):
                continue
            try:
                cmds.addAttr(target,proxy=sourcePlug,ln=targetAttr)
            except:
                pass
            

def Add(listUI,data,*args):
    global ITEMS
    def Delete(ui,*args):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS["items"][ui]
        ITEMS["order"].remove(ui)

    itemData = {}
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15,0.15,0.15))
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Source",editable=False)
    itemData["source"] = cmds.textField(text=data.get("source",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["source"]))
    cmds.setParent("..")

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Source Attr",editable=False)
    itemData["sourceAttr"] = cmds.textField(text=data.get("sourceAttr",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickAttrOnly,itemData["sourceAttr"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Targets",editable=False)
    itemData["targets"] = cmds.scrollField(text=data.get("targets",""),h=80)
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData["targets"]))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData["targets"]))
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=2,columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Target Attr",editable=False)
    itemData["targetAttr"] = cmds.textField(text=data.get("targetAttr",""))
    cmds.setParent("..")

    cmds.button(label="X",w=380,bgc=(0.5,0.2,0.2),c=partial(Delete,itemUI))

    cmds.setParent("..")
    cmds.setParent("..")

    ITEMS["items"][itemUI] = itemData
    ITEMS["order"].append(itemUI)









