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
    name = "Rope Straight"
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
            objStart = data["objStart"]
            objEnd = data["objEnd"]
            objs = data["objsRun"].split("\n")
            dests = data["destinations"].split("\n")
            attrContent = data["attrContent"]
            attr = data["attr"]
            constraintContent = data["constraintContent"]
            orientReference = data["orientReference"]
            offset = int(data.get("offset",0))
            objsCount = len(objs)

            if not cmds.attributeQuery(attr, node=attrContent, exists=True):
                cmds.addAttr(attrContent,ln=attr,at="long",min=0,max=max(objsCount - offset,0),dv=0,k=True)

            offsetPma = cmds.createNode("plusMinusAverage",n="{}_{}_offset".format(attrContent, attr))
            cmds.setAttr(offsetPma + ".operation",1)
            cmds.connectAttr("{}.{}".format(attrContent, attr),offsetPma + ".input1D[0]")
            cmds.setAttr(offsetPma + ".input1D[1]",offset)

            plus = cmds.createNode("plusMinusAverage",n="{}_{}_plus".format(attrContent, attr))
            cmds.setAttr(plus + ".operation",1)
            cmds.connectAttr(offsetPma + ".output1D",plus + ".input1D[0]")
            cmds.setAttr(plus + ".input1D[1]",1)

            invMd = cmds.createNode("multiplyDivide",n="{}_{}_inv".format(attrContent, attr))
            cmds.setAttr(invMd + ".operation",2)
            cmds.setAttr(invMd + ".input1X",1)
            cmds.connectAttr(plus + ".output1D",invMd + ".input2X")

            for i, (obj, dest) in enumerate(zip(objs, dests), start=1):
                con = cmds.pointConstraint(objStart,objEnd,dest,obj,mo=False)[0]
                ocon = cmds.orientConstraint(orientReference,dest,obj,mo=False)[0]
                if constraintContent:
                    cmds.parent(con,constraintContent)
                    cmds.parent(ocon,constraintContent)

                weights = cmds.pointConstraint(con,q=True,weightAliasList=True)
                startW = "{}.{}".format(con, weights[0])
                endW = "{}.{}".format(con, weights[1])
                destW = "{}.{}".format(con, weights[2])

                oweights = cmds.orientConstraint(ocon,q=True,weightAliasList=True)
                orientRefW = "{}.{}".format(ocon,oweights[0])
                orientDestW = "{}.{}".format(ocon,oweights[1])

                cond = cmds.createNode("condition",n="{}_rollCond".format(obj))
                cmds.setAttr(cond + ".operation",3)
                cmds.connectAttr(offsetPma + ".output1D",cond + ".firstTerm")
                cmds.setAttr(cond + ".secondTerm",i)
                cmds.setAttr(cond + ".colorIfTrueR",1)
                cmds.setAttr(cond + ".colorIfFalseR",0)

                startPma = cmds.createNode("plusMinusAverage",n="{}_startPma".format(obj))
                cmds.setAttr(startPma + ".operation",2)
                cmds.connectAttr(offsetPma + ".output1D",startPma + ".input1D[0]")
                cmds.setAttr(startPma + ".input1D[1]",i - 1)

                startMd = cmds.createNode("multiplyDivide",n="{}_startMd".format(obj))
                cmds.setAttr(startMd + ".operation",1)
                cmds.connectAttr(startPma + ".output1D",startMd + ".input1X")
                cmds.connectAttr(invMd + ".outputX",startMd + ".input2X")

                endMd = cmds.createNode("multiplyDivide",n="{}_endMd".format(obj))
                cmds.setAttr(endMd + ".operation",1)
                cmds.setAttr(endMd + ".input1X",i)
                cmds.connectAttr(invMd + ".outputX",endMd + ".input2X")

                startBlend = cmds.createNode("multiplyDivide",n="{}_startBlend".format(obj))
                cmds.connectAttr(startMd + ".outputX",startBlend + ".input1X")
                cmds.connectAttr(cond + ".outColorR",startBlend + ".input2X")

                endBlend = cmds.createNode("multiplyDivide",n="{}_endBlend".format(obj))
                cmds.connectAttr(endMd + ".outputX",endBlend + ".input1X")
                cmds.connectAttr(cond + ".outColorR",endBlend + ".input2X")

                rev = cmds.createNode("reverse",n="{}_destRev".format(obj))
                cmds.connectAttr(cond + ".outColorR",rev + ".inputX")
                cmds.connectAttr(cond + ".outColorR",orientRefW)
                cmds.connectAttr(rev + ".outputX",orientDestW)


                cmds.connectAttr(startBlend + ".outputX",startW)
                cmds.connectAttr(endBlend + ".outputX",endW)
                cmds.connectAttr(rev + ".outputX",destW)


            

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


    cmds.textField(text='Object Start',editable=False)
    itemData['objStart'] = cmds.textField(text=data.get('objStart', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['objStart']))

    cmds.textField(text='Object End',editable=False)
    itemData['objEnd'] = cmds.textField(text=data.get('objEnd', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['objEnd']))

    cmds.textField(text='Objects Run',editable=False)
    itemData['objsRun'] = cmds.scrollField(text=data.get('objsRun', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['objsRun']))

    cmds.textField(text='Objects Ref',editable=False)
    itemData['destinations'] = cmds.scrollField(text=data.get('destinations', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['destinations']))

    cmds.textField(text='Attribute Content',editable=False)
    itemData['attrContent'] = cmds.textField(text=data.get('attrContent', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['attrContent']))

    cmds.textField(text='Attribute',editable=False)
    itemData["attr"] = cmds.textField(text=data.get("attr", ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickAttrOnly,itemData["attr"]))

    cmds.textField(text="constraintContent",editable=False)
    itemData["constraintContent"] = cmds.textField(text=data.get("constraintContent", ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData["constraintContent"]))
    
    cmds.textField(text="orientReference",editable=False)
    itemData["orientReference"] = cmds.textField(text=data.get("orientReference", ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData["orientReference"]))


    cmds.textField(text="offset",editable=False)
    itemData["offset"] = cmds.textField(text=data.get("offset","0"))
    cmds.text(label="")


    cmds.setParent("..") #--
    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










