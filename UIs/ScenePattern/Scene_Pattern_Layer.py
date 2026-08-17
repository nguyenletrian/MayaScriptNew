import os
import maya.cmds as cmds
import pymel.core as pm
from functools import partial
from datetime import datetime

import NLTA_General,NLTA_UI,NLTA_Control
for module in [NLTA_General,NLTA_UI,NLTA_Control]:
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
    name = "Layer"
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
        for data in datas:
            layerName = data["layerName"]
            children = data["children"].split("\n")
            visibility = data["visibility"]
            display = data["display"]
            displayMap = {"Normal":0,"Template":1,"Reference":2}
            if cmds.objExists(layerName):
                cmds.delete(layerName)
            cmds.createDisplayLayer(name=layerName,empty=True)            
            cmds.setAttr(layerName+ ".visibility",visibility)
            cmds.setAttr(layerName+ ".displayType",displayMap[display])
            try:
                cmds.editDisplayLayerMembers(layerName,children,noRecurse=True)            
            except:pass
            
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

    cmds.textField(text='Layer Name',editable=False)
    itemData['layerName'] = cmds.textField(text=data.get("layerName", ""))
    cmds.text(label="")

    cmds.textField(text='Children',editable=False)
    itemData['children'] = cmds.scrollField(wordWrap=True,height=100,text=data.get("children", ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['children']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData['children']))
    cmds.setParent("..")

    cmds.textField(text='Display Type',editable=False)
    itemData["display"] = cmds.optionMenu()
    cmds.menuItem(label="Normal")
    cmds.menuItem(label="Template")
    cmds.menuItem(label="Reference")
    cmds.optionMenu(itemData["display"], e=True, value=data.get("display", "Normal"))
    cmds.text(label="")

    cmds.textField(text='Visibility',editable=False)
    itemData['visibility'] = cmds.checkBox(label="",value=data.get("visibility",True))
    cmds.text(label="")



    cmds.setParent("..") #--

    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










