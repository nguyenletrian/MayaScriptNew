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
    name = "Transfer Attribute"
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
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"]+"/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    deleteObject = []
    for item in datas:
        src_plug = item["attribute"]
        if "." not in src_plug:
            continue
        source, attr = src_plug.split(".", 1)
        target = item["target"]
        new_name = item.get("newName", attr)
        delete = item.get("delete", False)
        if not (cmds.objExists(src_plug) and cmds.objExists(target)):
            continue
        dst_plug = "{}.{}".format(target, new_name)

        if not cmds.attributeQuery(new_name, node=target, exists=True):
            attr_type = cmds.getAttr(src_plug, type=True)
            kwargs = {
                "ln": new_name,
                "k": True
            }
            if attr_type == "enum":
                kwargs["at"] = "enum"
                kwargs["en"] = cmds.attributeQuery(attr,node=source,listEnum=True)[0]
            else:
                kwargs["at"] = attr_type
            cmds.addAttr(target, **kwargs)

        cmds.setAttr(dst_plug, cmds.getAttr(src_plug))
        for conn in cmds.listConnections(src_plug, s=True, d=False, p=True) or []:
            cmds.connectAttr(conn, dst_plug, force=True)
        for conn in cmds.listConnections(src_plug, s=False, d=True, p=True) or []:
            cmds.connectAttr(dst_plug, conn, force=True)
        if delete:
            deleteObject.append(source)
    cmds.delete(deleteObject)


def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def PickAttribute(attributeUI,*arr):
        data = NLTA_UI.GetSelectedAttribute()
        if data["main"]:
            fullAttr = data["objs"][0]+"."+data["main"][0]
            cmds.textField(attributeUI,edit=True,text=fullAttr)
        else:
            Print("Please select a attribute")

    def SelectObject(attributeUI,*arr):
        text = cmds.textField(attributeUI,query=True,text=True)
        if text:
            obj = text.split(".")[0]
            cmds.select(obj)

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI)

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout( numberOfColumns=3,columnWidth=[(1,80),(2,260),(3,35)]) #--

    cmds.textField(text='Attribute',editable=False)
    itemData['attribute'] = cmds.textField(text=data.get('attribute',""),height=30)
    cmds.button(label="->",w=30,c=partial(PickAttribute,itemData['attribute']))

    cmds.textField(text='Target',editable=False)
    itemData['target'] = cmds.textField(text=data.get("target",""),width=255,height=30)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['target']))

    cmds.textField(text='New Name',editable=False)
    itemData['newName'] = cmds.textField(text=data.get("newName",""),width=255,height=30)
    cmds.text(label="")

    cmds.textField(text='Delete',editable=False)
    itemData['delete'] = cmds.checkBox('delete', value=data.get('delete',False))
    cmds.text(label="")


    cmds.setParent("..") #--    
    cmds.button(label="X",w=30,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










