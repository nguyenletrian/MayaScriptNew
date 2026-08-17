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
    name = "Driven Key"
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
        global ITEMS
        itemData = NLTA_General.JsonGetByID({
            "path":data["sceneDataPath"]+"/ScenePatternData.json",
            "id":data["id"]
        })
        saveData = []
        for itemUI in ITEMS["order"]:
            item = ITEMS["items"][itemUI]
            itemDict = {
                "driverAttr":cmds.textField(item["driverAttr"],q=True,text=True),
                "drivenAttrs":cmds.scrollField(item["drivenAttrs"],q=True,text=True),
                "keyData":[]
            }
            for keyUI in item["keyUI"]:
                keyDict = {
                    "driverValue":cmds.textField(keyUI["driverValue"],q=True,text=True),
                    "drivenValues":{}
                }
                for obj,attrUIs in keyUI["drivenValues"].items():
                    keyDict["drivenValues"][obj] = {}
                    for attr,valueUI in attrUIs.items():
                        keyDict["drivenValues"][obj][attr] = cmds.textField(valueUI,q=True,text=True)
                itemDict["keyData"].append(keyDict)
            saveData.append(itemDict)
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
        driverAttr = itemData["driverAttr"]
        if not cmds.objExists(driverAttr):
            cmds.warning("Driver attr not found : {}".format(driverAttr))
            continue
        offsetDict = {}
        drivenObjects = set()
        for keyData in itemData["keyData"]:
            drivenObjects.update(keyData["drivenValues"].keys())

        for obj in drivenObjects:
            parent = cmds.listRelatives(obj,parent=True)
            if parent and parent[0].endswith("_SDKGrp"):
                offsetDict[obj] = parent[0]
            else:
                offsetDict[obj] = (NLTA_General.CreateOffsetGroup(obj,obj+"_SDKGrp"))
            NLTA_General.CreateOffsetGroup(obj+"_SDKGrp",obj+"_ZeloSDKGrp")

        for keyData in itemData["keyData"]:
            driverValue = float(keyData["driverValue"])
            for obj,attrData in keyData["drivenValues"].items():
                offsetObj = offsetDict[obj]
                for attr, value in attrData.items():
                    sdkAttr = "{}.{}".format(offsetObj, attr)
                    if not cmds.attributeQuery(attr, node=offsetObj, exists=True):
                        cmds.addAttr(offsetObj,ln=attr,at="double",keyable=True)
                        childAttr = "{}.{}".format(obj, attr)
                        cmds.connectAttr(sdkAttr,childAttr,force=True)
                    cmds.setDrivenKeyframe(sdkAttr,currentDriver=driverAttr,driverValue=driverValue,value=float(value))
                    cmds.keyTangent(sdkAttr,itt="linear",ott="linear")
            

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def AddKeyItem(itemUI,data,listKey,*arr):
        global ITEMS

        def DeleteKeyItem(itemUI, keyName, *args):
            global ITEMS
            cmds.deleteUI(keyName)
            ITEMS["items"][itemUI]["keyUI"] = [
                x for x in ITEMS["items"][itemUI]["keyUI"]
                if x["keyName"] != keyName
            ]
        def GetDirectValue(itemUI, obj, attrData, attrUIs, *args):
            for attr, ui in attrUIs.items():
                fullAttr = obj + "." + attr
                if not cmds.objExists(fullAttr):
                    continue
                try:
                    value = cmds.getAttr(fullAttr)
                    cmds.textField(ui, e=True, text=str(value))
                except:
                    pass

        def GetSelectedDrivenValue(attrUIs,*args):
            sel = cmds.ls(sl=True)
            if not sel:
                return
            obj = sel[0]
            for attr,valueUI in attrUIs.items():
                fullAttr = obj+"."+attr
                if not cmds.objExists(fullAttr):
                    continue
                try:
                    value = cmds.getAttr(fullAttr)
                    cmds.textField(valueUI,e=True,text=str(value))
                except:
                    pass

        def GetValue(itemUI, keyName, *args):
            global ITEMS
            item = ITEMS["items"][itemUI]
            for keyUI in item["keyUI"]:
                if keyUI["keyName"] != keyName:
                    continue
                for obj, attrDict in keyUI["drivenValues"].items():
                    for attr, ui in attrDict.items():
                        drivenAttr = obj + "." + attr
                        if cmds.objExists(drivenAttr):
                            value = cmds.getAttr(drivenAttr)
                            cmds.textField(ui, e=True, text=str(value))
                break

        if data == {}:
            keyData = {
                "driverValue":cmds.getAttr(cmds.textField(ITEMS["items"][itemUI]["driverAttr"],q=True,text=True)),
                "drivenValues":{}
            }
            drivenAttrs = cmds.scrollField(ITEMS["items"][itemUI]["drivenAttrs"],q=True,text=True).split("\n")
            for drivenAttr in drivenAttrs:
                if "." not in drivenAttr:
                    continue
                obj,attr = drivenAttr.rsplit(".",1)
                if obj not in keyData["drivenValues"]:
                    keyData["drivenValues"][obj] = {}
                keyData["drivenValues"][obj][attr] = cmds.getAttr(drivenAttr)
        else:
            keyData = data

        keyUI = {} 
        keyUI["keyName"] = cmds.frameLayout(label=str(keyData["driverValue"]),parent=listKey,collapsable=True,collapse=True,w=360)
        cmds.rowColumnLayout(numberOfColumns=1)

        cmds.rowColumnLayout(numberOfColumns=4)
        cmds.textField(text='Value',editable=False,bgc=(0.216, 0.216, 0.216),w=50)                  
        keyUI["driverValue"] = cmds.textField(text=keyData["driverValue"],w=150)
        cmds.button(label="X",c=partial(DeleteKeyItem,itemUI,keyUI["keyName"]),w=60)
        cmds.button(label="Get All",c=partial(GetValue,itemUI,keyUI["keyName"]),w=60)
        cmds.setParent('..')

        keyUI["drivenValues"] = {}
        for obj,attrData in keyData["drivenValues"].items():
            cmds.rowColumnLayout(nc=1,width=380)
            cmds.text(label="  " + obj,width=380,bgc=(0.1, 0.1, 0.1),align="left",height=30)
            cmds.rowColumnLayout(numberOfColumns=2)

            cmds.rowColumnLayout(numberOfColumns=3)
            attrUIs = {}
            for attr,value in attrData.items():
                cmds.rowColumnLayout(nc=2)
                cmds.textField(text=attr,editable=False,w=25)
                valueUI = cmds.textField(text=str(value),w=50)
                attrUIs[attr] = valueUI
                cmds.setParent("..")            
            cmds.setParent("..")

            cmds.rowColumnLayout(numberOfColumns=2)
            cmds.button(label="Name",c=partial(GetDirectValue, itemUI, obj, attrData, attrUIs))
            cmds.button(label="Selected",c=partial(GetSelectedDrivenValue,attrUIs))            
            cmds.setParent("..") 

            cmds.setParent("..") 
            cmds.setParent("..")

            keyUI["drivenValues"][obj] = attrUIs


        cmds.setParent('..')
        cmds.setParent('..') 

        ITEMS["items"][itemUI]["keyUI"].append(keyUI)


    itemData = {}
    itemUI = cmds.frameLayout(label=data.get("driverAttr", ""),parent=listUI,collapsable=True,collapse=True,w=380)

    #itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))
    cmds.rowColumnLayout(numberOfColumns=1)





    cmds.rowColumnLayout(nc=2)

    cmds.text(label="",width=20)

    cmds.frameLayout(label="Detail",collapsable=True,collapse=True,w=380)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)]) #--
    cmds.textField(text='Driver Attr',editable=False)
    itemData['driverAttr'] = cmds.textField(text=data.get("driverAttr", ""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickAttrs,itemData['driverAttr']))
    
    cmds.textField(text='Driven Attrs',editable=False)
    itemData['drivenAttrs'] = cmds.scrollField(text=data.get("drivenAttrs", ""),height=100)
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickAttrs,itemData['drivenAttrs']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickAttrsAdd,itemData['drivenAttrs']))
    cmds.setParent("..")
    cmds.setParent("..") #--

    cmds.rowColumnLayout(nc=2)
    addButton = cmds.button(label="Add Values",w=189)
    cmds.button(label="X",w=189,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.setParent("..")

    cmds.setParent("..")
    


    cmds.text(label="",width=20)
    listKey = cmds.scrollLayout(horizontalScrollBarThickness=4,w=380,h=300)
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.setParent("..")    
    cmds.setParent("..")

    cmds.button(addButton,edit=True,c=partial(AddKeyItem,itemUI,{},listKey) )

    itemData["keyUI"] = []
    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)

    if data and ('keyData' in data):
        for i in range(len(data['keyData'])):
            AddKeyItem(itemUI,data['keyData'][i],listKey)
