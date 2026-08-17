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
    name = "Control Shape"
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

    def MirrorShape(*arr):
        sel = cmds.ls(sl=True)     
        sel01 = cmds.listRelatives(sel[0])
        sel02 = cmds.listRelatives(sel[1])     
        length = len(sel02)     
        for i in range(length):
            shape01 = cmds.ls(sel01[i] + ".cv[*]", fl=True)
            shape02 = cmds.ls(sel02[i] + ".cv[*]", fl=True)        
            y = 0               
            for a in shape02:
                ListXYZ = cmds.pointPosition(shape01[y], w=True)
                cmds.move(-ListXYZ[0], ListXYZ[1], ListXYZ[2], a, ws=True)
                y = y + 1

    def CopyShape(*arr):
        selection = cmds.ls(selection=True, allPaths=True)
        if len(selection) > 1:
            shape_from = selection[0]
            shape_from_pivot = cmds.xform(shape_from, q=True, r=True, rp=True, ws=True)
            selection.remove(selection[0])
            shape_to = selection
            for i in shape_to:            
                object_pivot = cmds.xform(i, q=True, r=True, rp=True, ws=True)
                
                cmds.select(i + ".cv[*]")
                cluster_name = cmds.cluster()
                pivot_temp = cmds.xform(cluster_name, q=True, r=True, rp=True, ws=True)
                cmds.xform(i, a=True, rp=pivot_temp, ws=True)
                cmds.delete(cluster_name)
                
                copy = cmds.duplicate(shape_from, rr=True)[0]
                
                group_temp = cmds.group(em=True)
                contraint_temp = cmds.parentConstraint(i, group_temp, mo=False)
                cmds.matchTransform(copy, i, pos=True)
                cmds.parent(copy, group_temp)
                if cmds.listRelatives(copy, ad=True, type="transform", path=True):
                    cmds.delete(cmds.listRelatives(copy, ad=True, type="transform", path=True))                
                try:
                    cmds.makeIdentity(copy, apply=True, t=1, r=0, s=0, n=0)
                except (Exception):
                    pass
                    
                try:
                    cmds.makeIdentity(copy, apply=True, t=0, r=1, s=0, n=0)
                except (Exception):
                    pass
                    
                try:
                    cmds.makeIdentity(copy, apply=True, t=0, r=0, s=1, n=0)
                except (Exception):
                    pass
                    
                shape_new = cmds.listRelatives(copy, shapes=True, fullPath=True)
                for a in shape_new:
                    array_connection = cmds.listConnections(a, plugs=True, connections=True)
                    if array_connection:
                        b = 0
                        while (b < len(array_connection)):
                            cmds.disconnectAttr(array_connection[b], array_connection[b + 1])
                            b += 2

                old_shapes = cmds.listRelatives(i, shapes=True, fullPath=True) or []
                old_shape_names = [cmds.ls(s, sn=True)[0] for s in old_shapes]
                cmds.select(clear=True)
                cmds.select(shape_new, add=True)
                cmds.select(i, add=True)
                pm.mel.eval("parent -r -s")

                all_shapes = cmds.listRelatives(i, shapes=True, fullPath=True) or []
                shape_new_array = [s for s in all_shapes if s not in old_shapes]

                # Lưu các connection cần reconnect
                connsData = []
                attrsReconns = ['visibility']

                for attr in attrsReconns:
                    if old_shapes:
                        src = cmds.connectionInfo(
                            old_shapes[0] + "." + attr,
                            sourceFromDestination=True
                        )
                        if src:
                            connsData.append([src, attr])

                # Xóa shape cũ
                for shape in old_shapes:
                    cmds.lockNode(shape, lock=False)
                    cmds.delete(shape)

                # Đổi tên shape mới thành tên shape cũ
                for new_shape, old_name in zip(shape_new_array, old_shape_names):
                    cmds.rename(new_shape, old_name)

                # Lấy lại shape sau khi rename
                shape_new_array = cmds.listRelatives(i, shapes=True, fullPath=True) or []

                # Reconnect
                for src, attr in connsData:
                    for shapeNew in shape_new_array:
                        cmds.connectAttr(src, shapeNew + "." + attr, force=True)
                
                cmds.xform(i, a=True, rp=object_pivot, ws=True)
                cmds.delete(group_temp)
                cmds.select(i)
        else:
            cmds.confirmDialog(title="Confirm", message="Please more than two shape", button=["Yes"], defaultButton="Yes", cancelButton="Yes")

    def QuickExportCurve(*arr):
        folder_temp = os.path.dirname(pm.sceneName())
        if not folder_temp:
            folder_temp = pm.mel.eval("SaveSceneAs;")
        folder_temp = os.path.dirname(pm.sceneName())
        if folder_temp: 
            data_temp = {}
            selection = cmds.ls(selection=True, long=True)
            allAsCtrl = []
            if selection:
                for obj in selection:
                    if cmds.nodeType(obj) == "transform":
                        if cmds.listRelatives(obj, children=True, type="nurbsCurve"):
                            if obj not in allAsCtrl:
                                allAsCtrl.append(obj)
            else:
                allAsCtrlTemp = cmds.ls(type="nurbsCurve", ap=True)
                for a in allAsCtrlTemp:
                    transformNode = cmds.listRelatives(a,parent=True,pa=True)[0]
                    if transformNode not in allAsCtrl:
                        allAsCtrl.append(transformNode)
            for ctrl in allAsCtrl:
                data_temp[ctrl] = {}
                data_temp[ctrl]["overrideEnabled"] = cmds.getAttr(ctrl+".overrideEnabled")
                data_temp[ctrl]["overrideRGBColors"] = cmds.getAttr(ctrl+".overrideRGBColors")
                data_temp[ctrl]["visibility"] = cmds.getAttr(ctrl+".visibility")
                if cmds.getAttr(ctrl+".overrideRGBColors") == 1:
                    data_temp[ctrl]["overrideColorR"] = cmds.getAttr(ctrl+".drawOverride.overrideColorR")
                    data_temp[ctrl]["overrideColorG"] = cmds.getAttr(ctrl+".drawOverride.overrideColorG")
                    data_temp[ctrl]["overrideColorB"] = cmds.getAttr(ctrl+".drawOverride.overrideColorB")
                else:
                    data_temp[ctrl]["overrideColor"] = cmds.getAttr(ctrl+".overrideColor")

                if cmds.listRelatives(ctrl,children=True,type="nurbsCurve"):
                    curveData = {}
                    for curveChild in cmds.listRelatives(ctrl,children=True,type="nurbsCurve",pa=True): 
                        if "Orig" not in curveChild:
                            curveChildName = curveChild.split("|")[-1]
                            curveData[curveChildName] = {}
                            pointData = {}
                            for point in cmds.ls(curveChild+".controlPoints[*]",flatten=True):
                                if cmds.objExists(point):
                                    pointName = point.split("|")[-1]
                                    pointName = pointName.split(".")[-1]
                                    pointData[pointName] = cmds.xform(point,q=True,os=True,t=True)
                            curveData[curveChildName]["pointData"] = pointData
                            curveData[curveChildName]["overrideEnabled"] = cmds.getAttr(curveChild+".overrideEnabled")
                            curveData[curveChildName]["overrideRGBColors"] = cmds.getAttr(curveChild+".overrideRGBColors")
                            curveData[curveChildName]["visibility"] = cmds.getAttr(curveChild+".visibility")
                            if cmds.getAttr(curveChild+".overrideRGBColors") == 1:
                                curveData[curveChildName]["overrideColorR"] = cmds.getAttr(curveChild+".drawOverride.overrideColorR")
                                curveData[curveChildName]["overrideColorG"] = cmds.getAttr(curveChild+".drawOverride.overrideColorG")
                                curveData[curveChildName]["overrideColorB"] = cmds.getAttr(curveChild+".drawOverride.overrideColorB")
                            else:
                                curveData[curveChildName]["overrideColor"] = cmds.getAttr(curveChild+".overrideColor")
                    data_temp[ctrl]["curveData"] = curveData                    
                if ctrl == "HipSwinger_M":
                    offsetGroup = cmds.listRelatives(ctrl,parent=True)[0]
                    data_temp[ctrl]["translate"] = (
                        cmds.getAttr(offsetGroup+".translateX"),
                        cmds.getAttr(offsetGroup+".translateY"),
                        cmds.getAttr(offsetGroup+".translateZ")
                    )
            folder_temp = os.path.dirname(pm.sceneName())
            folder_temp = cmds.encodeString(folder_temp)+"/SceneData"        
            file_path = folder_temp+"/dataCurveShape.json"
            NLTA_General.writeJsonFile(file_path,data_temp)
            print("Url export: " + file_path)

    def QuickImportCurve(*arr):
        folderTemp = os.path.dirname(pm.sceneName())
        if not folderTemp:
            folderTemp = pm.mel.eval("SaveSceneAs;")
        if folderTemp:
            folderTemp = os.path.dirname(pm.sceneName())+"/SceneData"
            filePath = folderTemp+"/dataCurveShape.json"
            if os.path.exists(filePath):
                dataTemp = NLTA_General.readJsonFile(filePath)
                
                selection = cmds.ls(selection=True)
                if selection:
                    ctrls = selection
                else:
                    ctrls = list(dataTemp.keys())

                for ctrl in ctrls:
                    if ctrl in dataTemp:
                        if cmds.objExists(ctrl):
                            try:
                                cmds.setAttr(ctrl+".overrideEnabled",dataTemp[ctrl]["overrideEnabled"])
                                cmds.setAttr(ctrl+".overrideRGBColors",dataTemp[ctrl]["overrideRGBColors"])
                            except:pass
                            """
                            try:
                                cmds.setAttr(ctrl+".visibility",dataTemp[ctrl]["visibility"])
                            except:pass
                            """
                            if dataTemp[ctrl]["overrideRGBColors"] == 1:
                                cmds.setAttr(ctrl+".drawOverride.overrideColorR",dataTemp[ctrl]["overrideColorR"])
                                cmds.setAttr(ctrl+".drawOverride.overrideColorG",dataTemp[ctrl]["overrideColorG"])
                                cmds.setAttr(ctrl+".drawOverride.overrideColorB",dataTemp[ctrl]["overrideColorB"])
                            else:
                                try:
                                    cmds.setAttr(ctrl+".overrideColor",dataTemp[ctrl]["overrideColor"])
                                except:pass
                        if dataTemp[ctrl]["curveData"]:
                            for curveChild in dataTemp[ctrl]["curveData"]:
                                curveChildPath = ctrl+"|"+curveChild
                                if cmds.objExists(curveChildPath):
                                    curveChildData = dataTemp[ctrl]["curveData"][curveChild]
                                    try:                  
                                        cmds.setAttr(curveChildPath+".overrideEnabled",curveChildData["overrideEnabled"])
                                        cmds.setAttr(curveChildPath+".overrideRGBColors",curveChildData["overrideRGBColors"])
                                    except:pass
                                    """
                                    try:
                                        cmds.setAttr(curveChildPath+".visibility",curveChildData["visibility"])
                                    except:pass
                                    """
                                    if curveChildData["overrideRGBColors"] == True:
                                        cmds.setAttr(curveChildPath+".drawOverride.overrideColorR",curveChildData["overrideColorR"])
                                        cmds.setAttr(curveChildPath+".drawOverride.overrideColorG",curveChildData["overrideColorG"])
                                        cmds.setAttr(curveChildPath+".drawOverride.overrideColorB",curveChildData["overrideColorB"])
                                    else:
                                        try:
                                            cmds.setAttr(curveChildPath+".overrideColor",curveChildData["overrideColor"])
                                        except:pass
                                    for point in curveChildData["pointData"]:
                                        pointPath = curveChildPath+"."+point
                                        if cmds.objExists(pointPath):
                                            cmds.xform(pointPath,q=True,os=True,t=True)
                                            cmds.xform(pointPath,os=True, translation=curveChildData["pointData"][point])
    def ImportCurveFromFile(*arr):
        result = cmds.fileDialog2(fileMode=1,caption="Select Curve Shape JSON",fileFilter="JSON Files (*.json)")
        if not result:
            return
        filePath = result[0]
        dataTemp = NLTA_General.readJsonFile(filePath)
        for ctrl in dataTemp:
            if cmds.objExists(ctrl):
                try:
                    cmds.setAttr(ctrl+".overrideEnabled",dataTemp[ctrl]["overrideEnabled"])
                    cmds.setAttr(ctrl+".overrideRGBColors",dataTemp[ctrl]["overrideRGBColors"])
                except:pass
                try:
                    cmds.setAttr(ctrl+".visibility",dataTemp[ctrl]["visibility"])
                except:pass
                if dataTemp[ctrl]["overrideRGBColors"] == 1:
                    cmds.setAttr(ctrl+".drawOverride.overrideColorR",dataTemp[ctrl]["overrideColorR"])
                    cmds.setAttr(ctrl+".drawOverride.overrideColorG",dataTemp[ctrl]["overrideColorG"])
                    cmds.setAttr(ctrl+".drawOverride.overrideColorB",dataTemp[ctrl]["overrideColorB"])
                else:
                    try:
                        cmds.setAttr(ctrl+".overrideColor",dataTemp[ctrl]["overrideColor"])
                    except:pass
            if dataTemp[ctrl]["curveData"]:
                for curveChild in dataTemp[ctrl]["curveData"]:
                    curveChildPath = ctrl+"|"+curveChild
                    if cmds.objExists(curveChildPath):
                        curveChildData = dataTemp[ctrl]["curveData"][curveChild]
                        try:                  
                            cmds.setAttr(curveChildPath+".overrideEnabled",curveChildData["overrideEnabled"])
                            cmds.setAttr(curveChildPath+".overrideRGBColors",curveChildData["overrideRGBColors"])
                        except:pass
                        try:
                            cmds.setAttr(curveChildPath+".visibility",curveChildData["visibility"])
                        except:pass
                        if curveChildData["overrideRGBColors"] == True:
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorR",curveChildData["overrideColorR"])
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorG",curveChildData["overrideColorG"])
                            cmds.setAttr(curveChildPath+".drawOverride.overrideColorB",curveChildData["overrideColorB"])
                        else:
                            try:
                                cmds.setAttr(curveChildPath+".overrideColor",curveChildData["overrideColor"])
                            except:pass
                        for point in curveChildData["pointData"]:
                            pointPath = curveChildPath+"."+point
                            if cmds.objExists(pointPath):
                                cmds.xform(pointPath,q=True,os=True,t=True)
                                cmds.xform(pointPath,os=True, translation=curveChildData["pointData"][point])


    mainForm = NLTA_General.LoadModule("Scene_Form")
    dataBack = mainForm.Create(data)
    buttonUI = dataBack["buttonUI"]
    listUI = dataBack["listUI"]

    cmds.rowColumnLayout(numberOfColumns=1,parent=buttonUI)
    cmds.rowColumnLayout(nc=4)    
    cmds.button(label="Add",c=partial(Add,listUI,{}),width=100)
    cmds.button(label="Save",c=partial(Save,data),width=100)
    cmds.button(label="Run",width=100, c=partial(Run,data))
    cmds.button(label="Mirror",c=MirrorShape,width=100)
    cmds.button(label="Copy",c=CopyShape,width=100)
    cmds.button(label="Quick Export",c=QuickExportCurve)
    cmds.button(label="Quick Import",c=QuickImportCurve)
    cmds.button(label="Import File",c=ImportCurveFromFile)
    cmds.setParent("..")
    colorParent = cmds.rowColumnLayout(nc=1)
    colorPick = NLTA_Control.IndexColorPick({"parent":colorParent,"width":400,"height":100})
    cmds.setParent("..")
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
            objs = data["object"].split("\n")
            shape = data["shape"]
            NLTA_Control.ShapeChangeSingle({"objs":objs,"shape":shape})
    cmds.warning("Change control shapes done!~")         

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
    cmds.textField(text='Object',editable=False)
    itemData['object'] = cmds.scrollField(wordWrap=True,height=100,text=data.get("object", ""))
    cmds.rowColumnLayout(nc=1)
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['object']))
    cmds.button(label="+",w=30,c=partial(NLTA_UI.PickObjectAdd,itemData['object']))
    cmds.setParent("..")
    cmds.textField(text='Shape',editable=False)
    itemData["shape"] = cmds.optionMenu()
    shapeData = NLTA_Control.ShapeData()
    for key in shapeData:
        cmds.menuItem(label=key)
    cmds.optionMenu(itemData["shape"], e=True, value=data.get("shape", "circle"))
    cmds.text(label="")

    cmds.setParent("..") #--

    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










