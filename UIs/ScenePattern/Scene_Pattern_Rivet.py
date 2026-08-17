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
    name = "Rivet"
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
        vertexs = [
            x.strip()
            for x in itemData["vertexs"].split("\n")
            if x.strip()
        ]
        if len(vertexs) < 3:
            cmds.warning("Need at least 3 vertexs")
            continue

        mesh = vertexs[0].split(".")[0]
        name = itemData["name"]
        copyTransform = itemData["copyTransform"]
        child = itemData["child"]
        parent = itemData["parent"]

        positions = [cmds.pointPosition(v,w=True)for v in vertexs]
        plane = cmds.polyCreateFacet(p=positions,n=name+"_Plane")[0]

        cmds.select( plane+".e[0]",plane+".e[2]")
        sel_edges = cmds.filterExpand(sm=32)

        cfme1 = cmds.createNode("curveFromMeshEdge")
        cfme2 = cmds.createNode("curveFromMeshEdge")
        loft = cmds.createNode("loft")
        posi = cmds.createNode("pointOnSurfaceInfo")
        e1 = 0
        e2 = 2
        cmds.setAttr(cfme1+".ei[0]",e1)
        cmds.setAttr(cfme2+".ei[0]",e2)

        cmds.setAttr(posi+".turnOnPercentage",1)
        cmds.setAttr(posi+".parameterU",0.5)
        cmds.setAttr(posi+".parameterV",0.5)

        cmds.connectAttr(plane+".worldMesh[0]",cfme1+".inputMesh",f=True)
        cmds.connectAttr(plane+".worldMesh[0]",cfme2+".inputMesh",f=True)
        cmds.connectAttr(cfme1+".outputCurve",loft+".inputCurve[0]",f=True)
        cmds.connectAttr(cfme2+".outputCurve",loft+".inputCurve[1]",f=True)
        cmds.connectAttr(loft+".outputSurface",posi+".inputSurface",f=True)

        loc = cmds.spaceLocator(n=name+"_Loc")[0]
        ac = cmds.createNode("aimConstraint",p=loc)

        cmds.setAttr(ac+".a",0,1,0,type="double3")
        cmds.setAttr(ac+".u",0,0,1,type="double3")
        cmds.connectAttr(posi+".position",loc+".translate",f=True)
        cmds.connectAttr(posi+".n",ac+".tg[0].tt",f=True)
        cmds.connectAttr(posi+".tv",ac+".wu",f=True)
        cmds.connectAttr(ac+".crx",loc+".rx",f=True)
        cmds.connectAttr(ac+".cry",loc+".ry",f=True)
        cmds.connectAttr(ac+".crz",loc+".rz",f=True)
        if copyTransform:
            grp = NLTA_General.GroupMatchObject(copyTransform,name+"_CopyTransform")
            cmds.parent(grp,loc)

        if child:
            offset = NLTA_General.CreateOffsetGroup(child,child+"_RivetOffset")
            cmds.parentConstraint(loc,offset,mo=True)
        cmds.select(mesh)
        cmds.select(plane,add=True)
        NLTA_General.copyJointBind()
        if parent:
            cmds.parent([plane,loc],parent)
            

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
    cmds.textField(text="Vertexs",editable=False)
    itemData["vertexs"] = cmds.scrollField(text=data.get("vertexs",""),h=80)
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["vertexs"]))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2,columnWidth=[(1,80),(2,297)])
    cmds.textField(text="Name",editable=False)
    itemData["name"] = cmds.textField(text=data.get("name",""))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Copy Trans",editable=False)
    itemData["copyTransform"] = cmds.textField(text=data.get("copyTransform",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["copyTransform"]))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Child",editable=False)
    itemData["child"] = cmds.textField(text=data.get("child",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["child"]))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,80),(2,265),(3,32)])
    cmds.textField(text="Parent",editable=False)
    itemData["parent"] = cmds.textField(text=data.get("parent",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["parent"]))
    cmds.setParent("..")

    cmds.button(label="X",w=380,bgc=(0.5,0.2,0.2),c=partial(Delete,itemUI))
    cmds.setParent("..")
    cmds.setParent("..")

    ITEMS["items"][itemUI] = itemData
    ITEMS["order"].append(itemUI)










