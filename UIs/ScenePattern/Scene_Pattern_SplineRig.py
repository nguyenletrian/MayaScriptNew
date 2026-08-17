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
    name = "Spline Rig"
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

def Run(data, *arr):
    newestData = NLTA_General.JsonGetByID({
        "path": data["sceneDataPath"] + "/ScenePatternData.json",
        "id": data["id"]
    })
    datas = NLTA_General.readJsonFile(newestData["path"])
    if not datas:
        return

    for splineData in datas:
        parent = splineData["parent"]
        controls = splineData["controls"].split("\n")
        numberCtrls = int(splineData["numberCtrls"])
        rebuild = splineData["rebuild"]

        # CREATE CONTROL OFFSET
        for ctrl in controls:
            if not cmds.objExists(ctrl + "_SplineOffset"):
                NLTA_General.CreateOffsetGroup(ctrl,ctrl + "_SplineOffset")

        # CREATE SPLINE JOINTS
        splineJoints = []
        for ctrl in controls:
            pos = cmds.xform(ctrl,q=True, ws=True,t=True)
            cmds.select(cl=True)
            jnt = cmds.joint(p=pos,n=ctrl + "_SplineJnt")
            splineJoints.append(jnt)
        for i in range(1, len(splineJoints)):
            cmds.parent(splineJoints[i],splineJoints[i - 1])
        cmds.joint(splineJoints[0],e=True,oj="xyz",sao="yup",ch=True,zso=True)
        cmds.joint(splineJoints[-1],e=True,oj="none")

        # FOLLOW GROUPS
        followGroups = []
        for ctrl, jnt in zip(controls, splineJoints):
            grp = NLTA_General.GroupMatchObject(ctrl,ctrl + "_SplineRef")
            cmds.parent(grp,jnt)
            followGroups.append(grp)

        # CREATE CURVE
        points = []
        for jnt in splineJoints:
            points.append(cmds.xform(jnt,q=True,ws=True,t=True))
        degree = min(3, len(points) - 1)
        curve = cmds.curve(d=degree,p=points,n=splineJoints[0] + "_SplineCurve")
        cmds.setAttr(curve+".inheritsTransform",0)
        
        # Rebuild curve
        result = cmds.rebuildCurve(curve,ch=True,rpo=False,rt=0,end=True,kr=False,kcp=False,kep=True,kt=False,s=100,d=3,tol=0.01)
        newCurve = next((x for x in result if curve in x), None)
        newCurve = cmds.rename(newCurve, curve + "_Rebuild")
        print(newCurve)

        # CREATE IK
        ikHandle = cmds.ikHandle(sj=splineJoints[0],ee=splineJoints[-1],sol="ikSplineSolver",c=newCurve,ccv=False,pcv=False)[0]

        # CREATE CONTROL JOINTS
        controlJoints = []
        total = numberCtrls + 2
        for i in range(total):
            u = float(i) / float(total - 1)
            poc = cmds.createNode("pointOnCurveInfo")
            cmds.connectAttr(curve + ".worldSpace[0]",poc + ".inputCurve")
            cmds.setAttr(poc + ".turnOnPercentage",1)
            cmds.setAttr(poc + ".parameter",u)
            pos = cmds.getAttr(poc + ".position")[0]
            cmds.delete(poc)
            cmds.select(cl=True)
            jnt = cmds.joint(p=pos,n="{}_CtrlJnt_{:02d}".format(curve,i + 1))
            controlJoints.append(jnt)

        # BIND SKIN
        cmds.skinCluster(controlJoints,curve,tsb=True,mi=2)



        # SPINE CONTROLS
        splineCtrls = []
        for jnt in controlJoints:
            ctrl = cmds.curve(d=1,p=[(-1,0,-1),(-1,0,1),(1,0,1),(1,0,-1),(-1,0,-1)],n=jnt.replace("_CtrlJnt","_Ctrl"))
            length = cmds.arclen(curve)
            size = length * 0.03
            cmds.scale(size,size,size,ctrl)
            cmds.makeIdentity(ctrl,apply=True)

            zero = cmds.group(ctrl,n=ctrl + "_Zero")
            matrix = cmds.xform(jnt,q=True,ws=True,m=True)
            cmds.xform(zero,ws=True,m=matrix)
            cmds.parentConstraint(ctrl,jnt,mo=False)
            splineCtrls.append(ctrl)

        # CONSTRAINT
        constraints = []
        for ctrl, grp in zip(controls,followGroups):
            con = cmds.parentConstraint(grp,ctrl + "_SplineOffset",mo=True)[0]
            constraints.append(con)

        # CLEAN
        rigGrp = cmds.group(em=True, n=controls[0] + "_SplineRig")
        visibleGrp = cmds.group(em=True, n=controls[0] + "_SplineRigVisible", p=rigGrp)
        hiddenGrp = cmds.group(em=True, n=controls[0] + "_SplineRigHidden", p=rigGrp)
        cmds.setAttr(hiddenGrp + ".visibility", 0)

        ctrlZeros = [cmds.listRelatives(c, p=True)[0] for c in splineCtrls]

        # Global Group (match spline control đầu tiên)
        globalGrp = NLTA_General.GroupMatchObject(
            splineCtrls[0],
            splineCtrls[0] + "_SplineControls_GlobalGrp"
        )

        cmds.parent(globalGrp, visibleGrp)
        cmds.parent(ctrlZeros, globalGrp)

        cmds.parent(curve, ikHandle, splineJoints[0], controlJoints,newCurve, hiddenGrp)
        cmds.parent(rigGrp, parent)


        # ATTRIBUTE
        master = controls[0]

        # -----------------------------
        # GLOBAL
        # -----------------------------
        masterSplineCtrl = splineCtrls[0]
        if not cmds.attributeQuery("Global", node=masterSplineCtrl, exists=True):
            cmds.addAttr(masterSplineCtrl,ln="Global",at="double",min=0,max=1,dv=0,k=True)
        blend = cmds.shadingNode("blendColors", asUtility=True)
        rootParent = splineData["parentGlobal"]
        parentCon = cmds.parentConstraint(rootParent,globalGrp,mo=True)[0]
        cmds.setAttr(parentCon + ".interpType", 2)
        for attr in ("rx", "ry", "rz"):
            for src in cmds.listConnections(globalGrp + "." + attr,s=True,d=False,p=True) or []:
                cmds.disconnectAttr(src, globalGrp + "." + attr)
        orientCon = cmds.orientConstraint(parent,globalGrp,mo=True)[0]
        for attr in ("rx", "ry", "rz"):
            for src in cmds.listConnections(globalGrp + "." + attr,s=True,d=False,p=True) or []:
                cmds.disconnectAttr(src, globalGrp + "." + attr)
        cmds.connectAttr(parentCon + ".constraintRotate",blend + ".color1",f=True)
        cmds.connectAttr(orientCon + ".constraintRotate",blend + ".color2",f=True)

        cmds.connectAttr(blend + ".output",globalGrp + ".rotate",f=True)
        cmds.connectAttr(masterSplineCtrl + ".Global",blend + ".blender",f=True)

        if not cmds.attributeQuery("SplineControls", node=master, exists=True):
            cmds.addAttr(master,ln="SplineControls",at="bool",dv=1,k=True)
        cmds.connectAttr(master + ".SplineControls",visibleGrp + ".visibility",f=True)
        for con in constraints:
            weight = cmds.parentConstraint(con, q=True, wal=True)[0]
            cmds.connectAttr(master + ".SplineControls",con + "." + weight,f=True)

        # Proxy attribute
        proxyCtrls = controls[1:] + splineCtrls
        for ctrl in proxyCtrls:
            if ctrl == master:
                continue
            if not cmds.attributeQuery("SplineControls", node=ctrl, exists=True):
                cmds.addAttr(ctrl,ln="SplineControls",proxy=master + ".SplineControls")



                

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

    cmds.textField(text='Parent',editable=False)
    itemData['parent'] = cmds.textField(text=data.get('parent', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['parent']))

    cmds.textField(text='Parent Global',editable=False)
    itemData['parentGlobal'] = cmds.textField(text=data.get('parentGlobal', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['parentGlobal']))

    cmds.textField(text='Controls',editable=False)
    itemData['controls'] = cmds.scrollField(text=data.get('controls', ""))
    cmds.button(label="->",w=30,c=partial(NLTA_UI.PickObject,itemData['controls']))

    cmds.textField(text='Number Ctrls',editable=False)
    itemData['numberCtrls'] = cmds.textField(text=data.get('numberCtrls', "1"))
    cmds.text(label="")

    cmds.textField(text='Rebuild',editable=False)
    itemData['rebuild'] = cmds.textField(text=data.get('rebuild', "100"))
    cmds.text(label="")


    cmds.setParent("..") #--
    cmds.button(label="X",w=35,backgroundColor=(.5,.2,.2),c=partial(Delete,itemUI))
    cmds.separator(height=10, style='none')

    cmds.setParent("..")    
    cmds.setParent("..")

    ITEMS['items'][itemUI] = itemData
    ITEMS['order'].append(itemUI)










