import os
import maya.cmds as cmds
import pymel.core as pm
from functools import partial
from datetime import datetime

import NLTA_General,NLTA_UI,NLTA_Mesh
for module in [NLTA_General,NLTA_UI,NLTA_Mesh]:
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
    name = "Mesh Vertex"
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
    cmds.button(label="Get Topo pair",w=35,c=partial(GetTopoPair,data))
    cmds.button(label="Get Mirror pair",w=35)
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
            #ctrls = data['child'].split("\n")
            #parent = data['parent']

def GetTopoPair(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if datas:
        for i in range(len(datas)):
            data = datas[i]
            sources = data['sources'].split("\n")
            targets = data['targets'].split("\n")
            mesh = (sources[0].split("."))[0]
            sourceVerts = []
            targetVerts = []
            for i in range(len(sources)):
                sourceVerts.append(int(NLTA_Mesh.GetID(sources[i])))
                targetVerts.append(int(NLTA_Mesh.GetID(targets[i])))
            pairs = NLTA_Mesh.FindSymmetricVertexPairs(mesh,sourceVerts,targetVerts)
            stringTemp = 'cmds.select("'+mesh+'.vtx[{}]","'+mesh+'.vtx[{}]")'
            for pair in pairs:
                print(stringTemp.format(pair[0],pair[1]))
            NLTA_Mesh.MirrorVertexPositionsByPairs(mesh,pairs)


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

    cmds.textField(text='Sources',editable=False)
    itemData['sources'] = cmds.scrollField(wordWrap=True,height=80,text=data.get('sources', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['sources']))

    cmds.textField(text='Targets',editable=False)
    itemData['targets'] = cmds.scrollField(wordWrap=True,height=80,text=data.get('targets', ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['targets']))
    cmds.setParent("..")

    cmds.setParent("..") #--

    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))

    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










