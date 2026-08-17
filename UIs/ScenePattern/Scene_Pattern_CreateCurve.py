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
    name = "Create Curve"
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
    curves = []
    for data in datas:
        points = []
        for line in data["points"].splitlines():
            line = line.strip()
            if not line:
                continue
            points.append(tuple(map(float, line.split())))
        if len(points) < 2:
            cmds.warning("{}: Need at least 2 points.".format(data["curveName"]))
            continue
        degree = min(3, len(points) - 1)
        curve = cmds.curve(p=points,d=degree,name=data["curveName"])
        cmds.setAttr(curve+".v",0)
        if cmds.objExists(data["parent"]):
            cmds.parent(curve,data["parent"])
        
        # Rebuild curve
        rebuild = int(data.get("rebuild", 0))
        result = cmds.rebuildCurve(curve,ch=True,rpo=False,rt=0,end=True,kr=False,kcp=False,kep=True,kt=False,s=100,d=3,tol=0.01)
        rebuildNode = result[0]
        newCurve = cmds.rename(rebuildNode, curve + "_Rebuild")
        cmds.setAttr(newCurve+".v",0)

        if cmds.objExists(data["parent"]):
            cmds.parent(newCurve, data["parent"])
        curves.append(curve)
    return curves

                

def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def PickChild(ui,*arr):
        NLTA_UI.PickObject(ui)
        offsetGroup = cmds.textField(itemData["Child"],query=True,text=True)+"_Offset"
        cmds.textField(itemData["OffsetName"],edit=True,text=offsetGroup)

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)]) #--

    cmds.textField(text='Points',editable=False)
    itemData['points'] = cmds.scrollField(text=data.get('points', ""))
    cmds.rowColumnLayout(2)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickPos,itemData['points']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickPosAdd,itemData['points']))
    cmds.setParent("..")

    cmds.textField(text='Parent',editable=False)
    itemData['parent'] = cmds.textField(text=data.get('parent', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['parent']))

    cmds.textField(text='CurveName',editable=False)
    itemData['curveName'] = cmds.textField(text=data.get('curveName', ""))
    cmds.text(label="")

    cmds.textField(text='Rebuild',editable=False)
    itemData['rebuild'] = cmds.textField(text=data.get('rebuild', "0"))
    cmds.text(label="")

    cmds.setParent("..") #--
    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










