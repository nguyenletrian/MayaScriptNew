import os
import sys
import SnapIKFK
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
    name = "Default Switch IK FK"
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
    cmds.rowColumnLayout(numberOfColumns=2,parent=buttonUI)
    cmds.button(label="Add",width=130,c=partial(Add,listUI,{}))
    cmds.button(label="Save", width=130,c=partial(Save,data))
    cmds.button(label="Run",width=130, c=partial(Run,data))
    cmds.setParent("..")
    Load(data,listUI)

def Run(data,*args):
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"]+"/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])   
    
    tool = SnapIKFK.SetupSnapIKFK()

    controlExist = False
    for itemData in datas:
        cmds.textFieldButtonGrp("TF_ctrlParentUI",e=True,text=itemData.get("controlParent", ""))
        print(controlExist)
        if controlExist == False:
            cmds.radioButtonGrp('TF_ctrlTypeUI',e=True,select=2)
            controlExist = True
        else:
            cmds.radioButtonGrp('TF_ctrlTypeUI',e=True,select=1)


        cmds.textFieldButtonGrp("TF_ctrlSwitchMode",e=True,text=itemData.get("controlSwitch", ""))
        cmds.textFieldGrp('TF_handAttr',e=True,text=itemData.get("attributeSwitch", ""))
        cmds.intFieldGrp('IF_fkValue',e=True,value1=int(itemData.get("fkActive", 0)))
        cmds.intFieldGrp('IF_ikValue',e=True,value1=int(itemData.get("ikActive", 1)))
        cmds.textFieldButtonGrp("TF_ctrlUpper",e=True,text=itemData.get("controlUpper", ""))
        cmds.textFieldButtonGrp("TF_ctrlFK",e=True,text=itemData.get("controlFK", "").replace("\n", ", "))
        cmds.textFieldButtonGrp("TF_ctrlIK",e=True,text=itemData.get("controlIK", "").replace("\n", ", "))
        cmds.textFieldButtonGrp("TF_ctrlRollToes",e=True,text=itemData.get("controlRoll", ""))
        cmds.textFieldButtonGrp("TF_jointIK",e=True,text=itemData.get("jointIK", "").replace("\n", ", "))
        cmds.checkBox('CB_mirror',e=True,value=itemData.get("mirror", False) )

        tool.ctrlParentUI = itemData.get("controlParent", "")
        tool.dict_query_select = {
            "attrBlend": itemData.get("attributeSwitch", ""),
            "fkMode": int(itemData.get("fkActive", 0)),
            "ikMode": int(itemData.get("ikActive", 1)),
        }
        # Control Upper
        if itemData.get("controlUpper"):
            tool.dict_query_select["ctrlUpper"] = [
                itemData["controlUpper"]
            ]
        # FK Controls
        fk_list = [
            x.strip()
            for x in itemData.get("controlFK", "").split("\n")
            if x.strip()
        ]
        if fk_list:
            tool.dict_query_select["ctrlFK"] = fk_list

        # IK Controls
        ik_list = [
            x.strip()
            for x in itemData.get("controlIK", "").split("\n")
            if x.strip()
        ]

        if ik_list:
            tool.dict_query_select["ctrlIK"] = ik_list

        # IK Joints
        joint_list = [
            x.strip()
            for x in itemData.get("jointIK", "").split("\n")
            if x.strip()
        ]

        if joint_list:
            tool.dict_query_select["jointIK"] = joint_list

        # Roll Toes
        if itemData.get("controlRoll"):
            tool.dict_query_select["RollToes"] = [
                itemData["controlRoll"]
            ]

        # Switch Control
        switch_ctrl = (
            itemData.get("controlSwitch")
            or itemData.get("controlParent")
        )

        if switch_ctrl:
            tool.dict_query_select["ctrlSw"] = [switch_ctrl]
        
        tool.setupIKFK()
        
    #cmds.deleteUI('ui_snapIKFK')
        

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

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control Parent",editable=False)
    itemData["controlParent"] = cmds.textField(text=data.get("controlParent",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlParent"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control Switch",editable=False)
    itemData["controlSwitch"] = cmds.textField(text=data.get("controlSwitch",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlSwitch"]))
    cmds.setParent("..")
    
    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Attribute Switch",editable=False)
    itemData["attributeSwitch"] = cmds.textField(text=data.get("attributeSwitch",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickAttrOnly,itemData["attributeSwitch"]))
    cmds.setParent("..")


    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="FK Active",editable=False)
    itemData["fkActive"] = cmds.textField(text=data.get("fkActive",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["fkActive"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="IK Active",editable=False)
    itemData["ikActive"] = cmds.textField(text=data.get("ikActive",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["ikActive"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control Upper",editable=False)
    itemData["controlUpper"] = cmds.textField(text=data.get("controlUpper",""))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlUpper"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control FK",editable=False)
    itemData["controlFK"] = cmds.scrollField(text=data.get("controlFK",""),height=65)
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlFK"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control IK",editable=False)
    itemData["controlIK"] = cmds.scrollField(text=data.get("controlIK",""),height=65)
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlIK"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Control Roll",editable=False)
    itemData["controlRoll"] = cmds.scrollField(text=data.get("controlRoll",""),height=65)
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["controlRoll"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,235),(3,32)])
    cmds.textField(text="Joint IK",editable=False)
    itemData["jointIK"] = cmds.scrollField(text=data.get("jointIK",""),height=65)
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObject,itemData["jointIK"]))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=3,columnWidth=[(1,100),(2,245),(3,32)])
    cmds.textField(text="Mirror",editable=False)
    itemData["mirror"] = cmds.checkBox(value=data.get("mirror", True),label="")
    cmds.setParent("..")

    cmds.button(label="X",w=380,bgc=(0.5,0.2,0.2),c=partial(Delete,itemUI))
    cmds.setParent("..")
    cmds.setParent("..")

    ITEMS["items"][itemUI] = itemData
    ITEMS["order"].append(itemUI)










