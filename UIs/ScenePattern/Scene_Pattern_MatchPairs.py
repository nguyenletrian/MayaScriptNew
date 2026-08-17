import os
import maya.cmds as cmds
import pymel.core as pm
from functools import partial
from datetime import datetime
from maya.api import OpenMaya as om
import xml.etree.ElementTree as ET

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
    name = "Match Pairs"
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

PAIR_INDEX = 0
def Add(listUI,data,*arr):
    global ITEMS
    def Delete(ui,*arr):
        global ITEMS
        cmds.deleteUI(ui)
        del ITEMS['items'][ui]
        ITEMS['order'].remove(ui)

    def MatchByDistance(sourcesUI, targetsUI, *arr):
        text = cmds.scrollField(sourcesUI, q=True, text=True)
        sources = [x.strip() for x in text.splitlines() if x.strip()]
        targets = cmds.ls(sl=True)
        if not sources or not targets:
            return
        result = []
        for source in sources:
            if not cmds.objExists(source):
                result.append("")
                continue
            srcPos = cmds.xform(source, q=True, ws=True, t=True)
            nearest = None
            nearestDist = None
            for target in targets:
                if not cmds.objExists(target):
                    continue
                src = om.MVector(cmds.xform(source, q=True, ws=True, t=True))
                tar = om.MVector(cmds.xform(target, q=True, ws=True, t=True))
                dist = (src - tar).length()
                if nearestDist is None or dist < nearestDist:
                    nearestDist = dist
                    nearest = target
            result.append(nearest.rsplit(":", 1)[-1] if nearest else "")
        cmds.scrollField(targetsUI,e=True,text="\n".join(result))
    
    def SelectPair(sourcesUI, targetsUI, *args):
        global PAIR_INDEX
        sourceText = cmds.scrollField(sourcesUI, q=True, text=True)
        sources = [x.strip() for x in sourceText.splitlines() if x.strip()]
        targetText = cmds.scrollField(targetsUI, q=True, text=True)
        targets = [x.strip() for x in targetText.splitlines() if x.strip()]
        count = min(len(sources), len(targets))
        if count == 0:
            return
        if PAIR_INDEX >= count:
            PAIR_INDEX = 0
        source = sources[PAIR_INDEX]
        target = targets[PAIR_INDEX]
        selects = []
        if cmds.objExists(source):
            selects.append(source)
        if cmds.objExists(target):
            selects.append(target)
        if selects:
            cmds.select(selects, r=True)
        print("[{}] {}  <-->  {}".format(
            PAIR_INDEX,
            source,
            target
        ))
        PAIR_INDEX += 1

    def TransferSkinXML(sourcesUI, targetsUI, *args):
        paths = cmds.fileDialog2(fileMode=1,caption="Select Skin XML",fileFilter="Skin XML (*.xml)")
        if not paths:
            return
        xmlPath = paths[0]
        sourceText = cmds.scrollField(sourcesUI, q=True, text=True)
        sources = [x.strip() for x in sourceText.splitlines() if x.strip()]
        targetText = cmds.scrollField(targetsUI, q=True, text=True)
        targets = [x.strip() for x in targetText.splitlines() if x.strip()]
        if len(sources) != len(targets):
            cmds.error("Sources and Targets must have the same number of lines.")
        replaceDict = dict(zip(sources, targets))

        tree = ET.parse(xmlPath)
        root = tree.getroot()
        for elem in root.iter():
            for attr, value in list(elem.attrib.items()):
                if value in replaceDict:
                    elem.set(attr, replaceDict[value])
            if elem.text:
                text = elem.text.strip()
                if text in replaceDict:
                    elem.text = replaceDict[text]
        base, ext = os.path.splitext(xmlPath)
        newPath = base + "_transferred" + ext
        tree.write(newPath, encoding="utf-8", xml_declaration=True)
        print("Saved:", newPath)

    itemData = {}   
    itemUI = cmds.rowColumnLayout(numberOfColumns=1,parent=listUI,backgroundColor=(0.15, 0.15, 0.15))
    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=2)#-

    cmds.rowColumnLayout( numberOfColumns=2,columnWidth=[(1,150),(2,32)]) #--
    itemData['sources'] = cmds.scrollField(height=300,text=data.get('sources', ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['sources']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd, itemData['sources']))
    cmds.setParent("..")
    cmds.setParent("..") #--


    cmds.rowColumnLayout( numberOfColumns=2,columnWidth=[(1,150),(2,32)]) #--
    itemData['targets'] = cmds.scrollField(height=300,text=data.get('targets', ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['targets']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd, itemData['targets']))
    cmds.setParent("..")
    cmds.setParent("..") #--

    cmds.setParent("..") #-

    cmds.rowColumnLayout(nc=4)
    cmds.button(label="X",w=100,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.button(label="Match By Distance",c=partial(MatchByDistance,itemData['sources'],itemData["targets"]))
    cmds.button(label="Select pair",c=partial(SelectPair,itemData['sources'],itemData["targets"]))
    cmds.button(label="Transfer XML",c=partial(TransferSkinXML,itemData['sources'],itemData["targets"]))
    cmds.separator(height=10, style='none')
    
    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










