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
    name = "Default Value"
    return({
        "ext":ext,
        "path":path+moduleName+"."+ext,
        "moduleName":moduleName,
        "order":0,
        "title":name,
        "name":name,
        "id":datetime.now().strftime("%Y%m%d%H%M%S")
    })


def Run(data, *arr):
    def disconnectCompoundConnections(attr):
        node, child = attr.split(".", 1)
        attrs = [attr]
        current = child
        while True:
            parent = cmds.attributeQuery(current, node=node, listParent=True)
            if not parent:
                break
            current = parent[0]
            attrs.append("{}.{}".format(node, current))
        attrs.reverse()
        for a in attrs:
            cmds.setAttr(a, lock=False)
            conns = cmds.listConnections(a,source=True,destination=False,plugs=True,connections=True) or []
            for i in range(0, len(conns), 2):
                dst = conns[i]
                src = conns[i + 1]
                cmds.disconnectAttr(src, dst)

    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"]+"/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    for item in datas:
        attr = item["attribute"]
        value = item["value"]
        node = attr.split(".", 1)[0]
        if cmds.objExists(node):
            disconnectCompoundConnections(attr)
            attrType = cmds.getAttr(attr, type=True)
            if attrType in ("double", "float", "doubleAngle", "doubleLinear"):
                value = float(value)
            elif attrType in ("long", "short", "byte", "bool", "enum"):
                value = int(value)
            if attrType == "string":
                cmds.setAttr(attr, str(value), type="string")
            else:
                cmds.setAttr(attr, value)

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

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI)

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=4) #--
    cmds.rowColumnLayout(nc=4)
    itemData['attribute'] = cmds.textField(text=data.get("attribute",""),width=240,height=30)
    itemData['value'] = cmds.textField(text=data.get("value",""),width=70,height=30)
    cmds.button(label="->",w=30,height=29,c=partial(GetAttributeValue,itemData['attribute'],itemData['value']))
    cmds.button(label="X",w=30,height=29,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.setParent("..")
    cmds.setParent("..") #--

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










