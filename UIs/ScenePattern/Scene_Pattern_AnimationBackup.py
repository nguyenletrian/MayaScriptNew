import os
import json
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
    name = "Animation Backup"
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
    global sceneDataPath
    def Save(data, *arr):
        itemData = NLTA_General.JsonGetByID({
            "path":data["sceneDataPath"]+"/ScenePatternData.json",
            "id":data["id"]
        })          
        returnData = NLTA_UI.GetData(ITEMS['items'])
        NLTA_General.writeJsonFile(itemData["path"],returnData)
    sceneDataPath = data["sceneDataPath"]

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

def Run(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if datas:
        for i in range(len(datas)):
            data = datas[i]
            objs = data['objects'].split("\n")

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)


    def Export(ui, *arr):
        objs = cmds.scrollField(ui,query=True,text=True).splitlines()
        objs = [obj.strip() for obj in objs if obj.strip() ]
        fileID = NLTA_General.CreateObjectsHex(objs)
        filePath = sceneDataPath + fileID + "_animation.json"
        data = {}
        for obj in objs:
            if not cmds.objExists(obj):
                continue
            longName = cmds.ls(obj,long=True)[0]
            animationData = {}
            attrs = cmds.listAttr(longName,keyable=True) or []
            for attr in attrs:
                plug = "{}.{}".format(longName,attr)
                curves = cmds.listConnections(plug,source=True,destination=False,type="animCurve") or []
                if not curves:
                    continue
                curve = curves[0]
                times = cmds.keyframe(curve,query=True,timeChange=True) or []
                values = cmds.keyframe(curve,query=True,valueChange=True) or []
                if not times:
                    continue
                animationData[attr] = {"times": times,"values": values}
            if animationData:
                data[obj] = animationData
        with open(filePath, "w") as f:
            json.dump(data,f,indent=4)

    def Import(ui, *arr):
        objs = cmds.scrollField(ui,query=True,text=True).splitlines()
        objs = [obj.strip() for obj in objs if obj.strip()]
        fileID = NLTA_General.CreateObjectsHex(objs)
        filePath = sceneDataPath + fileID + "_animation.json"
        if not os.path.exists(filePath):
            cmds.warning("File not found: {}".format(filePath))
            return
        with open(filePath, "r") as f:
            data = json.load(f)
        for obj, animationData in data.items():
            if not cmds.objExists(obj):
                continue
            for attr, attrData in animationData.items():
                plug = "{}.{}".format(obj,attr)
                if not cmds.objExists(plug):
                    continue
                times = attrData.get("times",[])
                values = attrData.get("values",[])
                if not times:
                    continue
                cmds.cutKey(plug,clear=True)
                for time, value in zip(times,values):
                    cmds.setKeyframe(plug,time=time,value=value)


    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)]) #--

    cmds.textField(text='Objects',editable=False)
    itemData['objects'] = cmds.scrollField(wordWrap=True,height=300,text=data.get("objects", ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['objects']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData['objects']))
    cmds.setParent("..")

    cmds.setParent("..") #--
    cmds.rowColumnLayout(nc=4)
    cmds.button(label="X",width=90,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.button(label="Export",width=90,c=partial(Export,itemData['objects']))
    cmds.button(label="Import",width=90,c=partial(Import,itemData['objects']))
    cmds.setParent("..")
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










