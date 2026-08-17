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
    name = "Create Attibute"
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
    cmds.button(label="Add",c=partial(Add,listUI,{}),width=130)
    cmds.button(label="Save",c=partial(Save,data),width=130)
    cmds.button(label="Run",c=partial(Run,data),width=130)
    cmds.setParent("..")
    Load(data,listUI)

def Run(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if datas:
        for i in range(len(datas)):
            data = datas[i]
            objects = data["objects"].splitlines()
            attrName = data["attrName"]
            attrType = data["attrType"]

            for obj in objects:
                if not cmds.objExists(obj):
                    continue
                if cmds.attributeQuery(attrName, node=obj, exists=True):
                    continue
                kwargs = {"ln": attrName,"k": data["keyable"]}
                # ---------- Type ----------
                if attrType in ("string", "matrix"):
                    kwargs["dt"] = attrType
                else:
                    kwargs["at"] = attrType

                # ---------- Enum ----------
                if attrType == "enum":
                    kwargs["en"] = data["enum"]

                # ---------- Default ----------
                if data["default"] not in ("", None):
                    kwargs["dv"] = float(data["default"])

                # ---------- Min ----------
                if data["min"] not in ("", None):
                    kwargs["min"] = float(data["min"])

                # ---------- Max ----------
                if data["max"] not in ("", None):
                    kwargs["max"] = float(data["max"])

                cmds.addAttr(obj, **kwargs)
            
                plug = "{}.{}".format(obj, attrName)
                cmds.setAttr(plug, lock=data["lock"])

                if not cmds.getAttr(plug, keyable=True):
                    cmds.setAttr(plug, channelBox=data["channelBox"])
        cmds.warning("Create Attribute done!~")

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def PickAttrInfo(name, type, keyable, lock, channelBox, minUI, maxUI, defaultUI, enumUI, *args):
        pickData = NLTA_UI.GetSelectedAttribute()
        attr = pickData["allAttr"][0]
        obj = pickData["objs"][0]
        attrInfo = NLTA_UI.GetAttributeInfo(obj, attr)
        uiMap = {"name": name,"type": type,"keyable": keyable,"lock": lock,"channelBox": channelBox,"min": minUI,"max": maxUI,"default": defaultUI,"enum": enumUI,}
        for key, ui in uiMap.items():
            NLTA_UI.FillUI(ui, attrInfo.get(key, None))

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)]) #--

    cmds.textField(text='Objects',editable=False)
    itemData['objects'] = cmds.scrollField(wordWrap=True,height=150,text=data.get("objects", ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['objects']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData['objects']))
    cmds.setParent("..")

    cmds.textField(text='Attr Name',editable=False)
    itemData['attrName'] = cmds.textField(text=data.get('attrName', ""))
    buttonGetInfo = cmds.button(label="->",w=30)

    cmds.textField(text='Attr Type',editable=False)
    itemData["attrType"] = cmds.optionMenu()
    array = ["bool","byte","short","long","float","double","doubleAngle","doubleLinear","time","enum","string",
                            "message","float2","float3","double2","double3","matrix"]
    for key in array:
        cmds.menuItem(label=key)
    cmds.optionMenu(itemData["attrType"], e=True, value=data.get("attrType", "bool"))
    cmds.text(label="")

    cmds.textField(text='Keyable',editable=False)
    itemData['keyable'] = cmds.checkBox("keyable", value=data.get("keyable",True))
    cmds.text(label="")

    cmds.textField(text='Lock',editable=False)
    itemData['lock'] = cmds.checkBox("lock", value=data.get("lock",True))
    cmds.text(label="")

    cmds.textField(text='Channel Box',editable=False)
    itemData['channelBox'] = cmds.checkBox("channelBox", value=data.get("channelBox",True))
    cmds.text(label="")

    cmds.textField(text='Min',editable=False)
    itemData['min'] = cmds.textField(text=data.get('min', ""))
    cmds.text(label="")

    cmds.textField(text='Max',editable=False)
    itemData['max'] = cmds.textField(text=data.get('max', ""))
    cmds.text(label="")

    cmds.textField(text='Default',editable=False)
    itemData['default'] = cmds.textField(text=data.get('default', ""))
    cmds.text(label="")

    cmds.textField(text='Enum',editable=False)
    itemData['enum'] = cmds.textField(text=data.get('enum', ""))
    cmds.text(label="")

    cmds.button(buttonGetInfo,e=True,c=partial(PickAttrInfo,
        itemData['attrName'],
        itemData['attrType'],
        itemData['keyable'],
        itemData['lock'],
        itemData['channelBox'],
        itemData['min'],
        itemData['max'],
        itemData['default'],
        itemData['enum'],
    ))
    


    cmds.setParent("..") #--
    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










