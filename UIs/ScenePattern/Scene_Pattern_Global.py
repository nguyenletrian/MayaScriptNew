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
    name = "Global"
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
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if datas:
        for i in range(len(datas)):
            data = datas[i]
            ctrls = data['child'].split("\n")
            parent = data['parent']
            for ctrl in ctrls:
                if cmds.objExists(ctrl):  
                    if not cmds.attributeQuery(data['attrSlide'], node=ctrl, exists=True):
                        cmds.addAttr(ctrl, ln=data['attrSlide'], at='double', min=0, max=1, dv=float(data['defaultValue']))
                        cmds.setAttr(ctrl+'.'+data['attrSlide'], e=True, keyable=True)
                    ctrlParent = cmds.listRelatives(ctrl,parent=True)
                    
                    if ctrlParent:
                        rootParent = ctrlParent[0]
                    else:
                        print("Can't file parent of Child")                        
                    offset = NLTA_General.CreateOffsetGroup(ctrl,"{}_GlobalGrp".format(ctrl))
                    if rootParent == offset:
                        parent = cmds.listRelatives(offset, parent=True)
                        if not parent:
                            continue
                        rootParent = parent[0]

                    blend = cmds.shadingNode("blendColors", asUtility=True)
                    parentConstr = cmds.parentConstraint(rootParent,offset,mo=data['maintain'])[0]                   
                    cmds.setAttr(parentConstr+'.interpType',2)            
                    attrs = ["rx","ry","rz"]
                    for attr in attrs:
                        for src in cmds.listConnections(offset+'.'+attr, s=True, d=False, plugs=True) or []:
                            cmds.disconnectAttr(src,offset+'.'+attr)
                    orientConstr = cmds.orientConstraint(parent,offset,mo=data['maintain'])[0]
                    for attr in attrs:
                        for src in cmds.listConnections(offset+'.'+attr, s=True, d=False, plugs=True) or []:
                            cmds.disconnectAttr(src,offset+'.'+attr)
                    cmds.connectAttr(parentConstr+".constraintRotate",blend+".color2", force=True)
                    cmds.connectAttr(orientConstr+".constraintRotate",blend+".color1", force=True)
                    cmds.connectAttr(blend+".output",offset+".rotate", force=True)
                    cmds.connectAttr(ctrl+"."+data['attrSlide'],blend+".blender", force=True)
            

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


    cmds.textField(text='Parent',editable=False)
    itemData['Parent'] = cmds.textField(text=data.get("parent", ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['Parent']))

    cmds.textField(text='Child',editable=False)
    itemData['Child'] = cmds.scrollField(wordWrap=True,height=350,text=data.get("child", ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['Child']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData['Child']))
    cmds.setParent("..")

    cmds.textField(text='Attr Slide',editable=False)
    itemData['AttrSlide'] = cmds.textField(text=data.get("attrSlide", "Global"))
    cmds.text(label="")

    cmds.textField(text='Default Value',editable=False)
    itemData['DefaultValue'] = cmds.textField(text=data.get("defaultValue", "0"))
    cmds.text(label="")

    cmds.textField(text='Maintain',editable=False)
    itemData['Maintain'] = cmds.checkBox("Maintain", value=data.get("maintain",True))
    cmds.text(label="")

    cmds.setParent("..") #--

    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










