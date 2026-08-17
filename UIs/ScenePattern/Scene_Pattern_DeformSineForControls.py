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
    name = "Deform Sine Offset"
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

def Run(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"] + "/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return

    for data in datas:

        curve = data["curve"]
        parent = data["parent"]
        controls = [x for x in data["controls"].splitlines() if x]
        translates = data.get("translates", "xyz").lower()
        holder = data["attrHolder"]
        attrName = data["attrName"]
        
        curveShape = cmds.listRelatives(curve, s=True, ni=True)[0]
        count = len(controls)
        refs = []
        offsets = []

        root = cmds.group(em=True, n=controls[0] + "_SplineRefs")

        for ctrl in controls:
            ref = cmds.group(em=True, n=ctrl + "_Ref")
            cmds.matchTransform(ref, ctrl)
            cmds.setAttr(ref+".inheritsTransform",0)

            poc = cmds.createNode("pointOnCurveInfo", n=ctrl + "_POC")
            cmds.connectAttr(curveShape + ".worldSpace[0]", poc + ".inputCurve", f=True)
            cmds.setAttr(poc + ".turnOnPercentage", 0)
            pos = cmds.xform(ctrl, q=True, ws=True, t=True)
            npc = cmds.createNode("nearestPointOnCurve", n=ctrl + "_NPC")
            cmds.connectAttr(curveShape + ".worldSpace[0]", npc + ".inputCurve", f=True)
            cmds.setAttr(npc + ".inPosition", *pos, type="double3")
            parameter = cmds.getAttr(npc + ".parameter")
            cmds.delete(npc)
            cmds.setAttr(poc + ".parameter", parameter)


            # Chỉ RefPos nhận translate từ curve
            cmds.connectAttr(poc + ".position", ref + ".translate", f=True)
            cmds.parent(ref, root)
            refPos = cmds.group(em=True, n=ctrl + "_RefPos")
            refPos2 = cmds.group(em=True, n=ctrl + "_RefPos2")
            cmds.matchTransform(refPos,ref)
            cmds.matchTransform(refPos2,ref)
            cmds.parent(refPos,root)
            cmds.parent(refPos2,refPos)

            cmds.pointConstraint(ref, refPos2, mo=True)
            refs.append(refPos2)

        # Parent cả root sau cùng
        if cmds.objExists(parent):
            cmds.parent(root, parent)

        for ctrl, refPos in zip(controls, refs):
            if not cmds.objExists(ctrl + "_SineDeformOffset"):
                offset = NLTA_General.CreateOffsetGroup(ctrl, ctrl + "_SineDeformOffset")
            else:
                offset = ctrl + "_SineDeformOffset"

            for axis in translates:
                cmds.connectAttr(
                    "{}.translate{}".format(refPos, axis.upper()),
                    "{}.translate{}".format(offset, axis.upper()),
                    f=True
                )
            offsets.append(offset)
        
        # Create sine
        sineHandle, sineNode = cmds.nonLinear(curve,type="sine",name=curve + "_Sine")
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

    cmds.textField(text='Curve',editable=False)
    itemData['curve'] = cmds.textField(text=data.get('curve', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['curve']))

    cmds.textField(text='Controls',editable=False)
    itemData['controls'] = cmds.scrollField(text=data.get('controls', ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['controls']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd, itemData['controls']))
    cmds.setParent("..")

    cmds.textField(text='Parent',editable=False)
    itemData['parent'] = cmds.textField(text=data.get('parent', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['parent']))

    cmds.textField(text='Translates',editable=False)
    itemData['translates'] = cmds.textField(text=data.get('translate', "xyz"))
    cmds.text(label="")

    cmds.textField(text='Attr Holder',editable=False)
    itemData['attrHolder'] = cmds.textField(text=data.get('attrHolder', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['attrHolder']))

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










