import os
import sys
import json
import datetime
import importlib
from functools import partial
import maya.cmds as cmds
import pymel.core as pm

import NLTA_General
import NLTA_Control

for module in [NLTA_General, NLTA_Control]:
    try:
        importlib.reload(module)
    except:
        reload(module)

cmds.selectPref(trackSelectionOrder=1)


def CreateUI(data):  
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data) 

    ###
    titles, buttons, inputs = [], [], []
    parent = data['parent']
    layoutTempt = cmds.rowColumnLayout(data["module"], parent=parent)
    cmds.rowColumnLayout(layoutTempt, edit=True, **layoutFlags)
    titles.append(cmds.textField(text=data['title'], editable=False))

    cmds.rowColumnLayout(numberOfColumns=4)  #
    buttons.append(cmds.button(label="Export Cur Data", width=133, c=exportCurveShapeNew))
    buttons.append(cmds.button(label="import Cur Data", width=133, c=importCurveShapeNew))
    buttons.append(cmds.button(label="Mirror Shape", width=133, c=MirrorShape))
    buttons.append(cmds.button(label="Copy Shape", width=133, c=partial(CopyShape, 'Copy')))
    cmds.setParent("..")  #
  
    cmds.rowColumnLayout(numberOfColumns=3)  #  
    cmds.rowColumnLayout(numberOfColumns=1)
    titles.append(cmds.textField(text='Basic', editable=False))  
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Create Joint", c=CreateJoint, width=100))
    buttons.append(cmds.button(label="Create Joints", c=CreateJoints, width=100))
    buttons.append(cmds.button(label="Freeze", c=freeze))
    buttons.append(cmds.button(label="Freeze Scale", c=freezeScale))
    buttons.append(cmds.button(label="Show Axis", c=showAxis))
    buttons.append(cmds.button(label="Joint Orient", c=JointOrient))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=2)
    buttons.append(cmds.button(label="Match 3 Point", width=110, c=matchThreeVertex))
    buttons.append(cmds.button(label="Match All", width=110, c=matchAll))
    buttons.append(cmds.button(label="Match T", c=matchT))
    buttons.append(cmds.button(label="Match R", c=matchR))
    buttons.append(cmds.button(label="Copy Transform All", c=CopyTransform))
    buttons.append(cmds.button(label="Past Transform All", c=PastTransform))
    buttons.append(cmds.button(label="Mirror Track On", c=MirrorTrack, width=100))
    buttons.append(cmds.button(label="Match Mirror Track", c=MatchMirrorTrack))
    buttons.append(cmds.button(label="Match Hierachy", c=matchHierachy))
    buttons.append(cmds.button(label="Match Preference", c=matchPreference))
    buttons.append(cmds.button(label="Joint From Fbx", c=AddJointFromFbx))
    buttons.append(cmds.button(label="Hierachy To Jnts", c=HierarchyToJoints))
    cmds.setParent("..")
    cmds.setParent("..")  
    cmds.setParent("..")
  
    cmds.rowColumnLayout(numberOfColumns=1)
    titles.append(cmds.textField(text='Copy Attribute', editable=False))  
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Translate X", width=100, c=partial(CopyAttr, 'tx')))
    buttons.append(cmds.button(label="Translate Y", c=partial(CopyAttr, 'ty')))
    buttons.append(cmds.button(label="Translate Z", c=partial(CopyAttr, 'tz')))
    buttons.append(cmds.button(label="Rotate X", c=partial(CopyAttr, 'rx')))
    buttons.append(cmds.button(label="Rotate Y", c=partial(CopyAttr, 'ry')))
    buttons.append(cmds.button(label="Rotate Z", c=partial(CopyAttr, 'rz')))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Scale X", width=100, c=partial(CopyAttr, 'sx')))
    buttons.append(cmds.button(label="Scale Y", c=partial(CopyAttr, 'sy')))
    buttons.append(cmds.button(label="Scale Z", c=partial(CopyAttr, 'sz')))
    buttons.append(cmds.button(label="Visibility", c=partial(CopyAttr, 'visibility')))
    buttons.append(cmds.button(label="Radius", c=partial(CopyAttr, 'radius')))
    cmds.setParent("..")
    cmds.setParent("..")  
    cmds.setParent("..")
  
    cmds.setParent("..")  #

    cmds.rowColumnLayout(numberOfColumns=2)  #
    cmds.rowColumnLayout(numberOfColumns=1)
    titles.append(cmds.textField(text='NameSpaces', editable=False))  
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=2)
    inputs.append(cmds.textField("CreateNamespaceText", placeholderText="New NameSpace", width=120))
    buttons.append(cmds.button(label="Create", command=CreateNamespace, width=50))
    cmds.setParent("..")
    buttons.append(cmds.button(label="Delete Namespace", c=DeleteNamespace))
    cmds.setParent("..")  
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    titles.append(cmds.textField(text='Attributes', editable=False, width=355))
    cmds.rowColumnLayout(numberOfColumns=3)
    inputs.append(cmds.textField("connectAttrFrom", placeholderText="Attribute from", width=145))
    inputs.append(cmds.textField("connectAttrTo", placeholderText="Attribute to", width=150))
    buttons.append(cmds.button(label="Connect", width=60, command=defaultConnect))
    cmds.setParent("..")
    buttons.append(cmds.button(label="Clipboar Attr", c=ClipboarAttribute))
    cmds.rowColumnLayout(numberOfColumns=2)
    inputs.append(cmds.textField("NewAttributeName", placeholderText="Attribute Name", width=255))
    buttons.append(cmds.button(label="Create Attribute", c=CreateAttribute, width=100))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=4)  
    buttons.append(cmds.button(label="Direct Connect", c=partial(ConnectAttribute, "direct"), width=89))
    buttons.append(cmds.button(label="Smart Connect", c=partial(ConnectAttribute, "smart"), width=89))
    buttons.append(cmds.button(label="Unlock Attr", c=unlockAttribute, width=89))
    buttons.append(cmds.button(label="Show Attr", c=partial(showAttr, ["rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz"]), width=89))
    cmds.setParent("..")  
    cmds.setParent("..")

    cmds.setParent("..")  #

    cmds.rowColumnLayout(numberOfColumns=1)  #
    titles.append(cmds.textField(text='Names', editable=False))  
    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Clear joint name", c=cleanName, width=131))
    buttons.append(cmds.button(label="Restore joint name", c=restoreName))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Save name temp", c=saveNameTemp, width=131))
    buttons.append(cmds.button(label="Restore name temp", c=restoreNameTemp))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Export joint name", c=exportJointName, width=131))
    buttons.append(cmds.button(label="Import joint name", c=importJointName))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Export Names", c=ExportNames, width=131))
    buttons.append(cmds.button(label="Import Names", c=ImportNames))
    cmds.setParent("..")
    cmds.setParent("..")  
    cmds.setParent("..")  #

    cmds.rowColumnLayout(numberOfColumns=1)  #
    titles.append(cmds.textField(text='Patterns', editable=False))  
    cmds.rowColumnLayout(numberOfColumns=4)
    buttons.append(cmds.button(label="Rotate Order", c=rotateOrder, width=133))
    buttons.append(cmds.button(label="Obj on Curve", c=objectOnCurve, width=133))
    buttons.append(cmds.button(label="Pytago", c=pytago, width=133))
    buttons.append(cmds.button(label="Create Point On Plane", c=PointOnPlane, width=133))
    cmds.setParent("..")  
    cmds.setParent("..")  #

    cmds.rowColumnLayout(numberOfColumns=1)  #
    titles.append(cmds.textField(text='Others', editable=False, width=535))
    cmds.rowColumnLayout(numberOfColumns=4)
    buttons.append(cmds.button(label="Clear Fbx", c=clearFbx, width=133)) 
    buttons.append(cmds.button(label="Check Ngon", c=checkNgon, width=133))
    buttons.append(cmds.button(label="Note Parent Const", c=NoteParentConstraint, width=133))
    buttons.append(cmds.button(label="Save Parent Const Data", c=SaveParentConstraintData, width=133))
    buttons.append(cmds.button(label="Clear Parent Const Attr", c=ClearParentConstraintData, width=133))
    buttons.append(cmds.button(label="Import Current Data", c=ImportParentConstraintData, width=133))
    buttons.append(cmds.button(label="Clear AI attribute", c=ClearAIAttribute, width=133))
    buttons.append(cmds.button(label="Turn Off OCIO", c=TurnOffOCIO, width=133))

    cmds.setParent("..")
    cmds.setParent("..")  #
  
    cmds.setParent("..")
  
    for title in titles:
        cmds.textField(title, edit=True, **titleFlags)
    for button in buttons:
        cmds.button(button, edit=True, **buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_, edit=True, **inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_, edit=True, **inputFlags)


def HierarchyToJoints(namespace="MyNewJoints"):
    if not cmds.namespace(exists=namespace):
        cmds.namespace(add=namespace)

    root = cmds.ls(selection=True)[0]
    objs = cmds.listRelatives(root, ad=True, fullPath=True)[::-1]
    objs.insert(0, root)

    newJoints = []

    for obj in objs:
        objParent = cmds.listRelatives(obj, parent=True, fullPath=True)
        jointName = "{}:{}".format(
            namespace,
            cmds.ls(obj, shortNames=True)[0]
        )
        cmds.select(clear=True)
        jointNew = cmds.joint(name=jointName)
        constraint = cmds.parentConstraint(obj, jointNew, maintainOffset=False)[0]
        cmds.delete(constraint)
        cmds.makeIdentity(jointNew, apply=True, t=1, r=1, s=1, n=0, pn=1)
        newJoints.append(jointNew)
        if objParent:
            parentName = "{}:{}".format(
                namespace,
                cmds.ls(objParent[0], shortNames=True)[0]
            )
            if cmds.objExists(parentName):
                cmds.parent(jointNew, parentName)
    return newJoints


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


def CopyShape(type, *arr):
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
            cmds.select(clear=True)
            cmds.select(shape_new, add=True)
            cmds.select(i, add=True)
            pm.mel.eval("parent -r -s")
            all_shapes = cmds.listRelatives(i, shapes=True, fullPath=True) or []
            shape_new_array = [s for s in all_shapes if s not in old_shapes]

            connsData = []
            attrsReconns = ['visibility']
            for attr in attrsReconns:
                src = cmds.connectionInfo(shapes[0] + "." + attr, sourceFromDestination=True)
                if src:
                    connsData.append([src, attr])
                    
            for shape in old_shapes:
                cmds.lockNode(shape, lock=False)
                cmds.delete(shape)

            for a in range(len(connsData)):
                conn = connsData[a]
                for shapeNew in shape_new_array:
                    cmds.connectAttr(conn[0], shapeNew + '.' + conn[1], force=True)
            
            cmds.xform(i, a=True, rp=object_pivot, ws=True)
            cmds.delete(group_temp)
            cmds.select(i)
    else:
        cmds.confirmDialog(title="Confirm", message="Please more than two shape", button=["Yes"], defaultButton="Yes", cancelButton="Yes")


def CreateSpace(*arr):
    pass


def CopyAttr(attr, *arr):
    objs = cmds.ls(selection=True)
    source = objs[0]
    targets = objs[1:]
    attrValue = cmds.getAttr(source + "." + attr)
    for target in targets:
        cmds.setAttr(target + "." + attr, attrValue)


CopyTransformSession = []


def CopyTransform(*arr):
    global CopyTransformSession
    returnArray = []
    objs = cmds.ls(selection=True)
    for obj in objs:
        translation = cmds.xform(obj, query=True, worldSpace=True, t=True)
        rotation = cmds.xform(obj, query=True, worldSpace=True, ro=True)
        returnArray.append([translation, rotation])
    CopyTransformSession = returnArray


def PastTransform(*arr):
    objs = cmds.ls(selection=True)
    for i in range(len(CopyTransformSession)):
        obj = objs[i]
        cmds.xform(obj, worldSpace=True, t=CopyTransformSession[i][0])
        cmds.xform(obj, worldSpace=True, ro=CopyTransformSession[i][1])
        

def JointOrient(*arr):
    pm.mel.eval('OrientJointOptions;')


def CreateNamespace(*arr):
    nameSpace = cmds.textField("CreateNamespaceText", query=True, text=True)
    NLTA_General.CreateNamespace(nameSpace)


def DeleteNamespace(*arr):
    selection = cmds.ls(selection=True)[0]
    nameSpace = selection.split(":")[0]
    NLTA_General.DeleteNamespace(nameSpace)


def clearFbx(*arr):
    folder_temp = os.path.dirname(pm.sceneName())
    if not folder_temp:
        folder_temp = pm.mel.eval("SaveSceneAs;")
    folder_temp = os.path.dirname(pm.sceneName())
    if folder_temp:
        skinData = {}

        mesh = cmds.ls(type="mesh")
        array_minus = []    
        for i in mesh:
            if "ShapeOrig" in i:
                array_minus.append(i)
        mesh = list(set(mesh) - set(array_minus))
        meshTransformArray = []        
        for i in mesh:
            skinName = pm.mel.eval('findRelatedSkinCluster ' + i)
            if skinName:               
                meshTransform = cmds.listRelatives(i, parent=True)[0]
                skinData[meshTransform] = {}
                skinData[meshTransform]["skinName"] = skinName
                meshTransformArray.append(meshTransform)

        # FIND BONE WILL REMOVE
        boneHasWeight = []
        for meshTransform in meshTransformArray:            
            allBoneBind = cmds.skinCluster(meshTransform, inf=True, q=True)       
            skinData[meshTransform]["allBoneBind"] = allBoneBind
            vertexAll = cmds.ls(meshTransform + ".vtx[*]")
            for vertex in vertexAll:
                for bone in allBoneBind:
                    boneWeight = cmds.skinPercent(skinData[meshTransform]["skinName"], vertex, transform=bone, query=True)
                    if boneWeight != 0:
                        if bone not in boneHasWeight:
                            boneHasWeight.append(bone)
        allBoneInScene = cmds.ls(type="joint")
        boneWillRemove = list(set(allBoneInScene) - set(boneHasWeight))

        deleteJoint = []
        # REMOVE BONE
        for meshTransform in skinData:
            for bone in boneWillRemove:
                if bone in skinData[meshTransform]["allBoneBind"]:
                    pm.mel.eval("skinCluster -e  -ri " + bone + " " + skinData[meshTransform]["skinName"] + ";")

        for bone in boneWillRemove:                             
            boneChildAll = cmds.listRelatives(bone, ad=True, type="joint")
            flag = 0
            if boneChildAll is not None:
                for boneChild in boneChildAll:
                    if boneChild in boneHasWeight:
                        flag = 1
            if flag == 0:
                deleteJoint.append(bone)
        cmds.delete(deleteJoint)


def cleanName(*arr):
    if cmds.ls(selection=True)[0]:
        selection = cmds.listRelatives(cmds.ls(selection=True)[0], ad=True, type="joint", pa=True)
        selection.append(cmds.ls(selection=True)[0])
        for a in selection:        
            newName = NLTA_General.correctCharacter(a)
            try:
                pm.mel.eval('addAttr -ln "realName"  -dt "string"  ' + a + ';')
                pm.mel.eval('setAttr -type "string" ' + a + '.realName "' + a + '";')        
            except:
                pass
            pm.mel.eval('rename "' + a + '" "' + newName + '";')
    else:
        print("Select root object!")


def restoreName(*arr):
    selection = cmds.listRelatives(cmds.ls(selection=True)[0], ad=True, type="joint", pa=True)
    selection.append(cmds.ls(selection=True)[0])
    for a in selection:
        if cmds.attributeQuery("realName", node=a, exists=True):
            originName = cmds.getAttr(a + '.realName')
            if originName is not None:
                print('rename "' + a + '" "' + originName + '";')
                pm.mel.eval('rename "' + a + '" "' + originName + '";')


def saveNameTemp(*arr):
    if cmds.ls(selection=True)[0]:
        selection = cmds.listRelatives(cmds.ls(selection=True)[0], ad=True, type="joint", pa=True)
        selection.append(cmds.ls(selection=True)[0])
        for a in selection:        
            try:
                pm.mel.eval('addAttr -ln "nameTemp"  -dt "string"  ' + a + ';')
                pm.mel.eval('setAttr -type "string" ' + a + '.nameTemp "' + a + '";')
            except:
                pass
    else:
        print("Select root object!")


def restoreNameTemp(*arr):
    selection = cmds.listRelatives(cmds.ls(selection=True)[0], ad=True, type="joint", pa=True)
    selection.append(cmds.ls(selection=True)[0])
    for a in selection:
        if cmds.attributeQuery("nameTemp", node=a, exists=True):
            originName = cmds.getAttr(a + '.nameTemp')
            if originName is not None:
                pm.mel.eval('rename "' + a + '" "' + originName + '";')


def exportJointName(*arr):
    data = {}
    for jointName in cmds.ls(type="joint"):
        if cmds.attributeQuery("nameTemp", node=jointName, exists=True) or cmds.attributeQuery("realName", node=jointName, exists=True):
            data[jointName] = {}
            if cmds.attributeQuery("nameTemp", node=jointName, exists=True):
                data[jointName]["nameTemp"] = cmds.getAttr(jointName + '.nameTemp')
            if cmds.attributeQuery("realName", node=jointName, exists=True):
                data[jointName]["realName"] = cmds.getAttr(jointName + '.realName')
    folderTemp = os.path.join(os.path.dirname(pm.sceneName()), 'NltaAsData')
    folderTemp = cmds.encodeString(folderTemp)
    if not os.path.exists(folderTemp):
        os.makedirs(folderTemp)
    filePath = os.path.dirname(pm.sceneName()) + "/NltaAsData/" + "jointNameAttr.txt"
    NLTA_General.writeJsonFile(filePath, data)


def importJointName(*arr):
    filePath = os.path.dirname(pm.sceneName()) + "/NltaAsData/" + "jointNameAttr.txt"
    if os.path.exists(filePath):
        data = NLTA_General.readJsonFile(filePath)
        for joint in data:
            try:
                pm.mel.eval('addAttr -ln "realName"  -dt "string"  ' + joint + ';')
                pm.mel.eval('setAttr -type "string" ' + joint + '.realName "' + data[data]["realName"] + '";')
                pm.mel.eval('addAttr -ln "nameTemp"  -dt "string"  ' + joint + ';')
                pm.mel.eval('setAttr -type "string" ' + joint + '.nameTemp "' + data[data]["nameTemp"] + '";')
            except:
                pass


def matchPreference(*arr):
    if len(cmds.ls(selection=True, type="joint")) != 0:
        jointRoot = cmds.ls(selection=True, type="joint")[0]
        url = pm.fileDialog2(fileMode=1)
        if url:
            cmds.file(url, r=True, ns="Temp")
        jointHierachy = cmds.listRelatives(jointRoot, ad=True)[::-1]
        jointHierachy.insert(0, jointRoot)
        for a in jointHierachy:
            jointFrom = a
            jointTo = "Temp:" + a
            cmds.matchTransform(jointFrom, jointTo, pos=True, rot=True)
        cmds.file(url, rr=True)
    else:
        cmds.warning("Please select root joint!")


def CreateJoint(*arr):
    selection = cmds.ls(selection=True)
    if len(selection) != 0:
        if cmds.objectType(selection[0]) == "mesh" or cmds.objectType(selection[0]) == "nurbsCurve":
            cluster_name = cmds.cluster()
            cmds.select(clear=True)
            joint_name = cmds.joint()
            cmds.matchTransform(joint_name, cluster_name, pos=True)
            cmds.delete(cluster_name)
        else:
            cmds.select(clear=True)
            joint_name = cmds.joint()
            cmds.select(clear=True)
            for i in selection:
                cmds.select(i, add=True)
                cmds.select(joint_name, add=True)
                pm.mel.eval('doCreateParentConstraintArgList 1 { "0","0","0","0","0","0","0","0","1","","1" };')
                contraint = pm.mel.eval('parentConstraint -weight 1;')
                cmds.delete(contraint)       
    else:
        cmds.joint(p=(0, 0, 0,))


def CreateJoints(*arr):
    selection = cmds.ls(selection=True, flatten=True)
    if len(selection) != 0:
        if '.vtx[' in selection[0] or '.cv[' in selection[0]:
            for obj in selection:
                cmds.select(clear=True)
                position = cmds.pointPosition(obj, world=True)
                cmds.joint(position=position, name=obj.replace(".", "_").replace("[", "_").replace("]", "") + "_JNT")
        else:
            for obj in selection:
                cmds.select(clear=True)
                joint_name = cmds.joint(name=obj + "_JNT")
                constraint = cmds.parentConstraint(obj, joint_name, maintainOffset=False)[0]
                cmds.delete(constraint)       
    else:
        cmds.joint(p=(0, 0, 0,))


def showAxis(*arr):
    list_ = cmds.ls(selection=True)
    state_show = 0
    state_hide = 0
    for i in list_:
        state = cmds.getAttr(i + ".displayLocalAxis")
        if state == True:
            state_show = state_show + 1
        else:
            state_hide = state_hide + 1    
    if state_show >= state_hide:
        for i in list_:
            cmds.setAttr(i + ".displayLocalAxis", 0)
    else:
        for i in list_:
            cmds.setAttr(i + ".displayLocalAxis", 1)   
            

def unlockAttribute(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    attr_list = [
        "translateX",
        "translateY",
        "translateZ",
        "rotateX",
        "rotateY",
        "rotateZ",
        "scaleX",
        "scaleY",
        "scaleZ",
        "visibility",
    ]       
    for a in list_:
        cmds.select(a)
        for b in attr_list:            
            cmds.setAttr(a + "." + b, lock=False)
    

def freeze(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    for i in list_:
        cmds.makeIdentity(i, apply=True, t=1, r=1, s=1, n=0)


def freezeScale(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    for i in list_:
        cmds.makeIdentity(i, apply=True, t=0, r=0, s=1, n=0)
        

def reset(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    for i in list_:
        cmds.setAttr("{}.tx".format(i), 0)
        cmds.setAttr("{}.ty".format(i), 0)
        cmds.setAttr("{}.tz".format(i), 0)
        cmds.setAttr("{}.rx".format(i), 0)
        cmds.setAttr("{}.ry".format(i), 0)
        cmds.setAttr("{}.rz".format(i), 0)
        

def centerPivot(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    for i in list_:
        center = cmds.objectCenter(i, gl=True)
        cmds.xform(i, pivots=center)
        

def deleteHistory(*arr):
    list_ = cmds.ls(selection=True, type="transform")
    for i in list_:
        cmds.delete(i, constructionHistory=True)
        

def rotateOrder(array, *arr):
    jointSource = cmds.ls(selection=True)[0]
    jointDest = cmds.ls(selection=True)[1]
    if cmds.objExists(jointSource) and cmds.objExists(jointDest):
        groupParent = "grp-" + jointSource + "-" + jointDest + "-" + "parent"
        groupOffset = "grp-" + jointSource + "-" + jointDest + "-" + "offset"
        locator1 = "grp-" + jointSource + "-" + jointDest + "-" + "loc1"
        groupParent = cmds.group(n=groupParent, empty=True)
        cmds.matchTransform(groupParent, jointSource, rot=True, pos=True)        
        constraint1 = cmds.parentConstraint(jointSource, groupParent, mo=True)
        cmds.select(clear=True)        
        locator1 = cmds.group(n=locator1, empty=True)
        groupOffset = cmds.group(locator1, n=groupOffset)  
        cmds.matchTransform(groupOffset, jointDest, rot=True, pos=True)              
        cmds.parent(groupOffset, groupParent)
        constraint2 = cmds.parentConstraint(locator1, jointDest, mo=True)
        pm.mel.eval('connectAttr -f ' + jointSource + '.scale ' + groupParent + '.scale;')            
        cmds.setAttr(jointDest + ".sx", lock=False)
        cmds.setAttr(jointDest + ".sy", lock=False)
        cmds.setAttr(jointDest + ".sz", lock=False)
        constaintScale = cmds.scaleConstraint(locator1, jointDest)
        return ({
            "jointSource": jointSource,
            "jointDest": jointDest,
            "groupParent": groupParent,
            "groupOffset": groupOffset,
            "locator": locator1,
            "constraintParentSource": constraint1,
            "constraintParentDest": constraint2,
            "constraintScale": constaintScale
        })
    

def mediumFat(*arr):
    selection = cmds.ls(type="joint")
    for i in selection:
        if cmds.attributeQuery('fat', node=i, exists=True):
            cmds.setAttr(i + ".fat", 7)


def matchThreeVertex(*arr):
    list_object = cmds.ls(fl=1, os=True)
    if len(list_object) != 3:
        print("Please select three vertex or three vertex and one object")
    else: 
        cluster_array = []
        joint_array = []
        for i in list_object:
            cmds.select(i)
            new_cluster = cmds.cluster()[1]
            cluster_array.append(new_cluster)
        for i in cluster_array:
            new_joint = cmds.joint(i)
            joint_array.append(new_joint)           
            cmds.parent(new_joint, w=True)
            cmds.matchTransform(new_joint, i, pos=True)
        cmds.select(joint_array[0])
        cmds.select(joint_array[1], add=True)
        pm.mel.eval('doCreateAimConstraintArgList 1 { "0","0","0","0","0","1","0","0","0","-1","0","0","1","1","object","' + joint_array[2] + '","0","0","0","","1" };')
        constraint_arm = pm.mel.eval('aimConstraint -offset 0 0 0 -weight 1 -aimVector 0 1 0 -upVector 0 0 -1 -worldUpType "object" -worldUpObject ' + joint_array[2] + ';')
        cmds.delete(constraint_arm)
        cmds.delete(cluster_array)
        cmds.delete(joint_array[0], joint_array[2])
        cmds.makeIdentity(joint_array[1], apply=True, t=1, r=1, s=1, n=0)


def matchHierachy(*arr):
    source = cmds.ls(selection=True, ap=True)[0]
    sourceChildren = cmds.listRelatives(source, ad=True, pa=True)
    sourceChildren.append(source)
    sourceChildren = sourceChildren[::-1]
    for destination in cmds.ls(selection=True, ap=True)[1:]:
        destinationChildren = cmds.listRelatives(destination, ad=True, pa=True)
        destinationChildren.append(destination)
        destinationChildren = destinationChildren[::-1]
        for order in range(len(sourceChildren)):
            try:
                cmds.makeIdentity(sourceChildren[order], apply=True, t=1, r=1, s=1, n=0)
                cmds.makeIdentity(destinationChildren[order], apply=True, t=1, r=1, s=1, n=0)
                cmds.matchTransform(destinationChildren[order], sourceChildren[order])
                cmds.makeIdentity(sourceChildren[order], apply=True, t=1, r=1, s=1, n=0)
                cmds.makeIdentity(destinationChildren[order], apply=True, t=1, r=1, s=1, n=0)
            except:
                pass


def matchAll(*arr):
    pm.mel.eval("matchTransform;")
    

def matchT(*arr): 
    pm.mel.eval("matchTransform -pos;")
    

def matchR(*arr):    
    pm.mel.eval("matchTransform -rot;")


def makeJointBetween(*arr):
    count = cmds.intField("joint_between_insert", query=True, value=True)
    if count != 0:  
        joint_list = []
        object_ = cmds.ls(selection=True)
        if len(object_) != 2:
            "Vui long chon 2 doi tuong"
        else:
            count = int(count) + 2
            steps = 1.0 / (count - 1)
            perc = 0
            for i in range(count):
                jnt = cmds.createNode("joint")
                constraint = cmds.parentConstraint(object_[1], jnt, weight=1.0 - perc)[0]
                cmds.parentConstraint(object_[0], jnt, weight=perc)
                cmds.delete(constraint)        
                perc += steps
                joint_list.append(jnt)
            for i in range(len(joint_list) - 2):
                cmds.parent(joint_list[i], joint_list[i + 1])
            joint_list.reverse()
            cmds.joint(joint_list[0], secondaryAxisOrient="yup", oj="xyz", children=True, zeroScaleOrient=True, edit=True)
            cmds.joint(joint_list[len(joint_list) - 1], oj="none", children=True, zeroScaleOrient=True, edit=True)
            cmds.delete(joint_list[0])
            cmds.delete(joint_list[len(joint_list) - 1])
            cmds.intField("joint_between_insert", edit=True, value=0)
    else:
        cmds.confirmDialog(title="Confirm", message="Joint between input must greater than 0!", button=["Yes"], defaultButton="Yes", cancelButton="Yes")


def checkNgon(*arr):
    selection = cmds.ls(selection=True, type="transform")
    array = []
    for a in selection:
        for b in cmds.ls(a + ".f[*]", flatten=True):
            vertex_temp = cmds.ls(cmds.polyListComponentConversion(b, ff=True, tv=True, vertexFaceAllEdges=True), flatten=True)
            if len(vertex_temp) > 4:
                array.append(b)
    cmds.select(array)
    pm.mel.eval('sets -name "Check_N-gon";')


def mirrorJoint(*arr):
    if cmds.ls(selection=True):
        selected = cmds.ls(selection=True)[0]
        prefix = [
            ["_r_", "_l_"],
            ["R_", "L_"],
            ["_right_", "_left_"],
            ["_RIGHT_", "_LEFT_"],
            ["_Right_", "_Left_"],
        ]
        array_left = list(list(zip(*prefix))[0])
        array_right = list(list(zip(*prefix))[1])
        array_left.extend(array_right)
        search_for = ""
        for a in array_left:
            if a in selected:
                for b in range(len(prefix)):
                    if prefix[b][0] == a:
                        search_for = a
                        replace_with = prefix[b][1]
                    elif prefix[b][1] == a:
                        search_for = prefix[b][0] 
                        replace_with = a
        if search_for != "":
            pm.mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "' + search_for + '" "' + replace_with + '";')
        else:
            pm.mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior ')   
    else:
        cmds.confirmDialog(title="Confirm", message="Please select joint!", button=["Yes"], defaultButton="Yes", cancelButton="Yes") 
        

def namespaceEditor(*arr):
    pm.mel.eval("NamespaceEditor;")
    

def referenceEditor(*arr):
    pm.mel.eval("ReferenceEditor;")
    

def optimizeEditor(*arr):    
    pm.mel.eval("OptimizeSceneOptions;")


def defaultConnect(type, *arr):
    attr_from = cmds.textField("connectAttrFrom", query=True, text=True)
    attr_to = cmds.textField("connectAttrTo", query=True, text=True)
    selection = cmds.ls(selection=True)
    if len(selection) >= 2:
        object_1 = selection[0]
        selection.remove(object_1) 
        for i in selection:             
            cmds.connectAttr(object_1 + "." + attr_from, i + "." + attr_to, force=True)
    else:
        print("Please select at least two object")  
    

def objectOnCurve(*arr):
    selection = cmds.ls(selection=True)
    curveName = cmds.listRelatives(selection, s=True, type='nurbsCurve')
    curveName = cmds.listRelatives(curveName, p=True)
    selection = list(set(selection) - set(curveName))
    curveName = curveName[0]
    nearestNode = pm.mel.eval('createNode "nearestPointOnCurve" ')
    pm.mel.eval('connectAttr -f ' + curveName + '.worldSpace[0] ' + nearestNode + '.inputCurve; ')
    for a in selection:
        pm.mel.eval('connectAttr -f ' + a + '.translate ' + nearestNode + '.inPosition;')
        pointOnCurveNode = pm.mel.eval('createNode "pointOnCurveInfo" ')        
        pm.mel.eval('connectAttr -f ' + curveName + '.local ' + pointOnCurveNode + '.inputCurve; ')         
        pm.mel.eval('connectAttr -f ' + nearestNode + '.parameter ' + pointOnCurveNode + '.parameter; ')        
        pm.mel.eval('disconnectAttr ' + nearestNode + '.parameter ' + pointOnCurveNode + '.parameter; ')
        pm.mel.eval('disconnectAttr ' + a + '.translate ' + nearestNode + '.inPosition;')       
        pm.mel.eval('connectAttr -f ' + pointOnCurveNode + '.position ' + a + '.translate; ')
    cmds.delete(nearestNode)


def pytago(*arr):
    selection = cmds.ls(selection=True)
    pointA = selection[0]
    pointB = selection[1]
    pointC = selection[2]
    distance1 = pm.mel.eval('shadingNode -asUtility distanceBetween;')
    pm.mel.eval('connectAttr -force ' + pointA + '.worldMatrix[0] ' + distance1 + '.inMatrix1;')
    pm.mel.eval('connectAttr -force ' + pointC + '.worldMatrix[0] ' + distance1 + '.inMatrix2;')
    distance2 = pm.mel.eval('shadingNode -asUtility distanceBetween;')
    pm.mel.eval('connectAttr -force ' + pointB + '.worldMatrix[0] ' + distance2 + '.inMatrix1;')
    pm.mel.eval('connectAttr -force ' + pointC + '.worldMatrix[0] ' + distance2 + '.inMatrix2;')
    
    multil_1 = pm.mel.eval('shadingNode -asUtility multiplyDivide;')
    pm.mel.eval('setAttr "' + multil_1 + '.operation" 3;')
    pm.mel.eval('setAttr "' + multil_1 + '.input2X" 2;')
    pm.mel.eval('setAttr "' + multil_1 + '.input2Y" 2;')
    pm.mel.eval('connectAttr -f ' + distance1 + '.distance ' + multil_1 + '.input1X;')
    pm.mel.eval('connectAttr -f ' + distance2 + '.distance ' + multil_1 + '.input1Y;')
    
    minus = pm.mel.eval('shadingNode -asUtility plusMinusAverage;')
    pm.mel.eval('setAttr "' + minus + '.operation" 2;')
    pm.mel.eval('connectAttr -f ' + multil_1 + '.outputX ' + minus + '.input1D[0];')    
    pm.mel.eval('connectAttr -f ' + multil_1 + '.outputY ' + minus + '.input1D[1];')
    
    multil_2 = pm.mel.eval('shadingNode -asUtility multiplyDivide;')
    pm.mel.eval('connectAttr -f ' + minus + '.output1D ' + multil_2 + '.input1X;')
    pm.mel.eval('setAttr "' + multil_2 + '.operation" 3;')
    pm.mel.eval('setAttr "' + multil_2 + '.input2X" 0.5;')
    
    pm.mel.eval('disconnectAttr ' + multil_1 + '.outputX ' + minus + '.input1D[0];')
    cmds.delete(distance1)
    
    axis_value = 0
    axis_max = ""
    axis_dict = {"X": cmds.getAttr(pointA + '.translateX'), "Y": cmds.getAttr(pointA + '.translateY'), "Z": cmds.getAttr(pointA + '.translateZ')}
    for a in axis_dict:
        if axis_dict[a] > axis_value:
            axis_value = axis_dict[a]
            axis_max = a
    pm.mel.eval('connectAttr -f ' + multil_2 + '.outputX ' + pointA + '.translate' + axis_max + ';')


def exportCurveShapeNew(*arr):
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
                transformNode = cmds.listRelatives(
                    a,
                    parent=True,
                    pa=True
                )[0]
                if transformNode not in allAsCtrl:
                    allAsCtrl.append(transformNode)

        for ctrl in allAsCtrl:
            data_temp[ctrl] = {}
            data_temp[ctrl]["overrideEnabled"] = cmds.getAttr(ctrl + ".overrideEnabled")
            data_temp[ctrl]["overrideRGBColors"] = cmds.getAttr(ctrl + ".overrideRGBColors")
            data_temp[ctrl]["visibility"] = cmds.getAttr(ctrl + ".visibility")
            if cmds.getAttr(ctrl + ".overrideRGBColors") == 1:
                data_temp[ctrl]["overrideColorR"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorR")
                data_temp[ctrl]["overrideColorG"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorG")
                data_temp[ctrl]["overrideColorB"] = cmds.getAttr(ctrl + ".drawOverride.overrideColorB")
            else:
                data_temp[ctrl]["overrideColor"] = cmds.getAttr(ctrl + ".overrideColor")

            if cmds.listRelatives(ctrl, children=True, type="nurbsCurve"):
                curveData = {}
                for curveChild in cmds.listRelatives(ctrl, children=True, type="nurbsCurve", pa=True): 
                    if "Orig" not in curveChild:
                        curveChildName = curveChild.split("|")[-1]
                        curveData[curveChildName] = {}
                        pointData = {}
                        for point in cmds.ls(curveChild + ".controlPoints[*]", flatten=True):
                            if cmds.objExists(point):
                                pointName = point.split("|")[-1]
                                pointName = pointName.split(".")[-1]
                                pointData[pointName] = cmds.xform(point, q=True, os=True, t=True)
                        curveData[curveChildName]["pointData"] = pointData
                        curveData[curveChildName]["overrideEnabled"] = cmds.getAttr(curveChild + ".overrideEnabled")
                        curveData[curveChildName]["overrideRGBColors"] = cmds.getAttr(curveChild + ".overrideRGBColors")
                        curveData[curveChildName]["visibility"] = cmds.getAttr(curveChild + ".visibility")
                        if cmds.getAttr(curveChild + ".overrideRGBColors") == 1:
                            curveData[curveChildName]["overrideColorR"] = cmds.getAttr(curveChild + ".drawOverride.overrideColorR")
                            curveData[curveChildName]["overrideColorG"] = cmds.getAttr(curveChild + ".drawOverride.overrideColorG")
                            curveData[curveChildName]["overrideColorB"] = cmds.getAttr(curveChild + ".drawOverride.overrideColorB")
                        else:
                            curveData[curveChildName]["overrideColor"] = cmds.getAttr(curveChild + ".overrideColor")
                data_temp[ctrl]["curveData"] = curveData                    
            if ctrl == "HipSwinger_M":
                offsetGroup = cmds.listRelatives(ctrl, parent=True)[0]
                data_temp[ctrl]["translate"] = (
                    cmds.getAttr(offsetGroup + ".translateX"),
                    cmds.getAttr(offsetGroup + ".translateY"),
                    cmds.getAttr(offsetGroup + ".translateZ")
                )
        folder_temp = os.path.dirname(pm.sceneName())
        folder_temp = cmds.encodeString(folder_temp)        
        file_path = folder_temp + "/dataCurveShape.json"

        NLTA_General.writeJsonFile(file_path, data_temp)
        print("Url export: " + file_path)


def importCurveShapeNew(*arr):
    folderTemp = os.path.dirname(pm.sceneName())
    if not folderTemp:
        folderTemp = pm.mel.eval("SaveSceneAs;")
    if folderTemp:
        folderTemp = os.path.dirname(pm.sceneName())
        filePath = folderTemp + "/dataCurveShape.json"
        if os.path.exists(filePath):
            dataTemp = NLTA_General.readJsonFile(filePath)
            for ctrl in dataTemp:
                if cmds.objExists(ctrl):
                    try:
                        cmds.setAttr(ctrl + ".overrideEnabled", dataTemp[ctrl]["overrideEnabled"])
                        cmds.setAttr(ctrl + ".overrideRGBColors", dataTemp[ctrl]["overrideRGBColors"])
                    except:
                        pass
                    try:
                        cmds.setAttr(ctrl + ".visibility", dataTemp[ctrl]["visibility"])
                    except:
                        pass
                    if dataTemp[ctrl]["overrideRGBColors"] == 1:
                        cmds.setAttr(ctrl + ".drawOverride.overrideColorR", dataTemp[ctrl]["overrideColorR"])
                        cmds.setAttr(ctrl + ".drawOverride.overrideColorG", dataTemp[ctrl]["overrideColorG"])
                        cmds.setAttr(ctrl + ".drawOverride.overrideColorB", dataTemp[ctrl]["overrideColorB"])
                    else:
                        try:
                            cmds.setAttr(ctrl + ".overrideColor", dataTemp[ctrl]["overrideColor"])
                        except:
                            pass
                if dataTemp[ctrl]["curveData"]:
                    for curveChild in dataTemp[ctrl]["curveData"]:
                        curveChildPath = ctrl + "|" + curveChild
                        if cmds.objExists(curveChildPath):
                            curveChildData = dataTemp[ctrl]["curveData"][curveChild]
                            try:                  
                                cmds.setAttr(curveChildPath + ".overrideEnabled", curveChildData["overrideEnabled"])
                                cmds.setAttr(curveChildPath + ".overrideRGBColors", curveChildData["overrideRGBColors"])
                            except:
                                pass
                            try:
                                cmds.setAttr(curveChildPath + ".visibility", curveChildData["visibility"])
                            except:
                                pass
                            if curveChildData["overrideRGBColors"] == True:
                                cmds.setAttr(curveChildPath + ".drawOverride.overrideColorR", curveChildData["overrideColorR"])
                                cmds.setAttr(curveChildPath + ".drawOverride.overrideColorG", curveChildData["overrideColorG"])
                                cmds.setAttr(curveChildPath + ".drawOverride.overrideColorB", curveChildData["overrideColorB"])
                            else:
                                try:
                                    cmds.setAttr(curveChildPath + ".overrideColor", curveChildData["overrideColor"])
                                except:
                                    pass
                            for point in curveChildData["pointData"]:
                                pointPath = curveChildPath + "." + point
                                if cmds.objExists(pointPath):
                                    cmds.xform(pointPath, q=True, os=True, t=True)
                                    cmds.xform(pointPath, os=True, translation=curveChildData["pointData"][point])


def clearOffset(*arr):
    for a in cmds.ls(selection=True):
        groupNew = cmds.group(n=a + "_fixOffset", empty=True)
        parentName = cmds.listRelatives(a, parent=True)[0]
        cmds.matchTransform(groupNew, a, rot=True, pos=True)
        cmds.parent(groupNew, parentName)
        cmds.parent(a, groupNew)
        

def restoreClearOffset(*arr):
    fixOffset = cmds.ls("*fixOffset*", type='transform')
    for a in fixOffset:
        parentName = cmds.listRelatives(a, parent=True)[0]
        childrenName = cmds.listRelatives(a, children=True)[0]
        cmds.parent(childrenName, parentName)
        cmds.delete(a)


def showAttr(array, *arr):
    for objectNode in cmds.ls(selection=True, ap=True):
        for attr in array:
            pm.mel.eval("setAttr -k on " + objectNode + "." + attr + ";")


def connectSingle(array, *arr):
    group_content = array["content"]
    joint_source = array["source"]
    joint_dest = array["dest"]
    if cmds.objExists(joint_source) and cmds.objExists(joint_dest):
        if cmds.objExists("grp-" + joint_source + "-" + joint_dest + "-" + "parent"):
            cmds.delete("grp-" + joint_source + "-" + joint_dest + "-" + "parent")
        group_parent = "grp-" + joint_source + "-" + joint_dest + "-" + "parent"
        group_offset = "grp-" + joint_source + "-" + joint_dest + "-" + "offset"
        locator1 = "grp-" + joint_source + "-" + joint_dest + "-" + "loc1"
        group_parent = cmds.group(n=group_parent, empty=True)
        cmds.matchTransform(group_parent, joint_source, rot=True, pos=True)
        cmds.select(clear=True)
        locator1 = cmds.group(n=locator1, empty=True)
        group_offset = cmds.group(locator1, n=group_offset)
        cmds.matchTransform(group_offset, joint_dest, rot=True, pos=True)
        cmds.parent(group_offset, group_parent)
        cmds.parentConstraint(joint_source, group_parent, mo=True)          
        constaint = cmds.parentConstraint(locator1, joint_dest, mo=True)
        cmds.parent(constaint, group_parent)
        pm.mel.eval('connectAttr -f ' + joint_source + '.scale ' + group_parent + '.scale;')            
        cmds.setAttr(joint_dest + ".sx", lock=False)
        cmds.setAttr(joint_dest + ".sy", lock=False)
        cmds.setAttr(joint_dest + ".sz", lock=False)
        constaintScale = cmds.scaleConstraint(locator1, joint_dest)
        cmds.parent(constaintScale, group_parent)
        try:
            cmds.parent(group_parent, group_content)        
        except:
            pass


def spaceNum(array, *arr):
    arrayTemp = array
    driven = arrayTemp[-1]
    drivenOffset = cmds.listRelatives(driven, parent=True)[0]
    arrayTemp.remove(driven)
    driver = arrayTemp
    option = ""
    for b in driver:
        if option != "":
            option += ":" + b
        else:
            option = b

    if cmds.objExists(driven):
        cmds.select(clear=True)
        for a in driver:
            cmds.select(a, add=True)
        cmds.select(drivenOffset, add=True)
        constraintName = cmds.parentConstraint(cmds.ls(selection=True), w=1, mo=1)[0]
        if cmds.attributeQuery("space", node=driven, ex=True):
            cmds.deleteAttr(driven + ".space")
        pm.mel.eval('addAttr -ln "space"  -at "enum" -en "' + option + '" ' + driven + ';')
        pm.mel.eval('setAttr -e-keyable true ' + driven + '.space;')    

        nameTemp = {}
        for b in driver:
            for c in range(len(driver)):
                if cmds.attributeQuery(b + 'W' + str(c), node=constraintName, ex=True):
                    nameTemp[b] = constraintName + '.' + b + 'W' + str(c)
        for b in driver:
            index = driver.index(b)
            pm.mel.eval('setAttr "' + driven + '.space" ' + str(index) + ';')
            for c in nameTemp:
                if b == c:
                    pm.mel.eval('setAttr "' + nameTemp[c] + '" 1;')
                else:
                    pm.mel.eval('setAttr "' + nameTemp[c] + '" 0;')
                pm.mel.eval('setDrivenKeyframe -currentDriver ' + driven + '.space ' + nameTemp[c] + ';')
        pm.mel.eval('setAttr "' + driven + '.space" 0;')
    return constraintName


def spaceFloat(array, *arr): 
    arrayTemp = array
    driven = arrayTemp[-1]
    drivenOffset = cmds.listRelatives(driven, parent=True)[0]
    arrayTemp.remove(driven)
    driver = arrayTemp
    if cmds.attributeQuery(driver[1] + "_space", node=driven, ex=True):
        cmds.deleteAttr(driven + "." + driver[1] + "_space")
    pm.mel.eval('addAttr -ln "' + driver[1] + '_space"  -at double  -min 0 -max 10 -dv 0 ' + driven + ';')
    pm.mel.eval('setAttr -e-keyable true ' + driven + '.' + driver[1] + '_space;')
    if cmds.objExists(driven):
        cmds.select(clear=True)
        for a in driver:
            cmds.select(a, add=True)
        cmds.select(drivenOffset, add=True)
        constraintName = cmds.parentConstraint(cmds.ls(selection=True), w=1, mo=1)[0]     
        setRangeNode = pm.mel.eval("shadingNode -asUtility setRange;")
        pm.mel.eval('connectAttr -f ' + driven + '.' + driver[1] + '_space ' + setRangeNode + '.valueX;')  
        pm.mel.eval("setAttr " + setRangeNode + ".minX 0;")
        pm.mel.eval("setAttr " + setRangeNode + ".maxX 1;")
        pm.mel.eval("setAttr " + setRangeNode + ".oldMinX 0;")
        pm.mel.eval("setAttr " + setRangeNode + ".oldMaxX 10;")
        reverseNode = pm.mel.eval("shadingNode -asUtility reverse;")
        pm.mel.eval("connectAttr -f " + setRangeNode + ".outValueX " + constraintName + "." + driver[0] + "W0;")
        pm.mel.eval("connectAttr -f " + setRangeNode + ".outValueX " + reverseNode + ".inputX;")       
        pm.mel.eval("connectAttr -f " + reverseNode + ".outputX " + constraintName + "." + driver[1] + "W1;")
    return constraintName


def modifyLayer(*arr):
    LayerName = 'JointBindLayer'
    if pm.objExists(LayerName):
        pm.delete(LayerName)
    DisplayLayer = pm.createDisplayLayer(name=LayerName, empty=True)
    if cmds.objExists("DeformationSystem"):
        pm.editDisplayLayerMembers(DisplayLayer, 'DeformationSystem', noRecurse=True)
    DisplayLayer.displayType.set(2)
    DisplayLayer.visibility.set(0)

    LayerName = 'ControlsLayer'
    if pm.objExists(LayerName):
        pm.delete(LayerName)
    DisplayLayer = pm.createDisplayLayer(name=LayerName, empty=True)
    if cmds.objExists("MotionSystem"):
        pm.editDisplayLayerMembers(DisplayLayer, 'MotionSystem', noRecurse=True)
    DisplayLayer.color.set(29)

    LayerName = 'GeoLayer'
    if pm.objExists(LayerName):
        pm.delete(LayerName)
    DisplayLayer = pm.createDisplayLayer(name=LayerName, empty=True)
    DisplayLayer.displayType.set(2)
    DisplayLayer.visibility.set(1)
    for a in cmds.ls(type="mesh"):
        if a.endswith("Orig") != True:
            for b in cmds.listHistory(a):
                if cmds.objExists(b) and cmds.objectType(b) == "skinCluster":
                    cmds.editDisplayLayerMembers('GeoLayer', cmds.listRelatives(a, parent=True)[0], noRecurse=True)


def ExportNames(*arr):
    path = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="Select Folder")
    if path:
        filePath = path[0] + '/NamesData.txt'  
        objs = cmds.ls(selection=True)
        names = []
        for obj in objs:
            names.append(obj)
        data = (";").join(names)
        NLTA_General.writeTxtFile(filePath, data, *arr)


def ImportNames(*arr):
    url = cmds.fileDialog2(dialogStyle=2, fileMode=1, caption="Select File")
    if url:
        data = NLTA_General.readTxtFile(url[0])
        arrayTemp = data.split(";")
        objs = cmds.ls(selection=True)
        matchNumber = max(len(arrayTemp), len(objs))
        for i in range(matchNumber):
            cmds.rename(objs[i], arrayTemp[i])


def MirrorTrackSingle(data, *arr):
    obj0 = data['obj0']
    obj1 = data['obj1']
    cmds.select(clear=True)
    jointCenter = cmds.joint() 
    content = data['content']
    
    # OBJ0
    mirrorPlane = NLTA_General.checkNegPosAxis(obj0, "x")
    cmds.select(clear=True)
    jointTemp = cmds.joint()
    cmds.matchTransform(jointTemp, obj0, pos=True, rot=True)
    cmds.parent(jointTemp, jointCenter)
    groupTemp = cmds.group(empty=True)
    cmds.matchTransform(groupTemp, obj1, pos=True, rot=True)
    if mirrorPlane == '+':
        cmds.select(jointTemp)
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior;')[0]
    else:
        cmds.select(jointTemp)
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ;')[0]
    cmds.parent(jointMirror, groupTemp)
    cmds.hide(groupTemp)
    cmds.parentConstraint(obj1, groupTemp, mo=True)
    pm.mel.eval('addAttr -ln "MirrorTrack"  -dt "string" ' + jointMirror + ';')
    pm.mel.eval('setAttr -type "string" ' + jointMirror + '.MirrorTrack "' + cmds.ls(obj0, uuid=True)[0] + '";')
    cmds.delete(jointTemp)
    cmds.parent(groupTemp, content)
    
    # OBJ1
    mirrorPlane = NLTA_General.checkNegPosAxis(obj1, "x")
    cmds.select(clear=True)
    jointTemp = cmds.joint()
    cmds.matchTransform(jointTemp, obj1, pos=True, rot=True)
    cmds.parent(jointTemp, jointCenter)
    groupTemp = cmds.group(empty=True)
    cmds.matchTransform(groupTemp, obj0, pos=True, rot=True)
    if mirrorPlane == '+':
        cmds.select(jointTemp)
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior;')[0]
    else:
        cmds.select(jointTemp)
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ;')[0]
    cmds.parent(jointMirror, groupTemp)
    cmds.hide(groupTemp)
    cmds.parentConstraint(obj0, groupTemp, mo=True)
    pm.mel.eval('addAttr -ln "MirrorTrack"  -dt "string"  ' + jointMirror + ';')
    pm.mel.eval('setAttr -type "string" ' + jointMirror + '.MirrorTrack "' + cmds.ls(obj1, uuid=True)[0] + '";')
    cmds.parent(groupTemp, content)

    cmds.delete(jointCenter)


def MirrorTrack(*arr):
    objs = cmds.ls(selection=True, ap=True)
    obj0 = objs[0]
    obj1 = objs[1]

    if cmds.listRelatives(obj0, ad=True, pa=True):
        obj0Children = cmds.listRelatives(obj0, ad=True, pa=True)
    else:
        obj0Children = []
    if cmds.listRelatives(obj1, ad=True, pa=True):
        obj1Children = cmds.listRelatives(obj1, ad=True, pa=True)
    else:
        obj1Children = []
    obj0Children.insert(0, obj0)
    obj1Children.insert(0, obj1)
    maxNumber = min(len(obj0Children), len(obj1Children))
    groupContent = "NLTA_MirrorTrack"
    if not cmds.objExists(groupContent):
        cmds.group(n="NLTA_MirrorTrack", empty=True)
    cmds.select(clear=True)
    for i in range(maxNumber):
        obj0Temp = obj0Children[i]
        obj1Temp = obj1Children[i]
        MirrorTrackSingle({
            'obj0': obj0Temp,
            'obj1': obj1Temp,
            'content': groupContent
        })


def MatchMirroTrackSingle(source, target, *arr):
    cmds.select(clear=True)
    jointCenter = cmds.joint()     
    mirrorPlane = NLTA_General.checkNegPosAxis(source, "x")
    cmds.select(clear=True)
    jointTemp = cmds.joint()
    cmds.matchTransform(jointTemp, source, pos=True, rot=True) 
    cmds.parent(jointTemp, jointCenter)
    cmds.select(jointTemp)
    if mirrorPlane == '-':     
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior;')[0]
    else:
        jointMirror = pm.mel.eval('mirrorJoint -mirrorYZ;')[0]
    cmds.matchTransform(target, jointMirror, pos=True, rot=True)
    cmds.delete([jointTemp, jointCenter, jointMirror])
    

def MatchMirrorTrack(*arr):
    objs = cmds.ls(selection=True)
    joints = cmds.ls(type='joint', ap=True)
    for obj in objs:
        objUUID = cmds.ls(obj, uuid=True)[0]
        for joint in joints:
            if cmds.attributeQuery('MirrorTrack', node=joint, exists=True):
                if cmds.getAttr(joint + '.MirrorTrack') == objUUID:
                    MatchMirroTrackSingle(joint, obj)        
                    break


def AddJointFromFbx(*arr):
    fbxFile = cmds.fileDialog2(fileMode=1, caption="Open Fbx File")[0]
    if fbxFile:
        nameSpaceTemp = 'NLTA_Temp'     
        nameSpaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for nameSpace in nameSpaces:
            if nameSpaceTemp in nameSpace:
                cmds.namespace(removeNamespace=nameSpace, deleteNamespaceContent=True)
        cmds.file(fbxFile, i=True, type='FBX', ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=False, namespace=nameSpaceTemp)
        roots = cmds.ls(assemblies=True)
        for root in roots:
            if nameSpaceTemp in root:
                fbxRoot = root
        fbxJoints = cmds.listRelatives(fbxRoot, ad=True, children=True)
        fbxJoints.reverse()
        fbxJoints.insert(0, root)
        for fbxJoint in fbxJoints:
            sceneJointName = fbxJoint.split(':')[-1]
            fbxJointParent = cmds.listRelatives(fbxJoint, parent=True)
            if fbxJointParent:
                sceneJointParent = (fbxJointParent[0]).split(':')[-1]
            if not cmds.objExists(sceneJointName):
                cmds.select(clear=True)
                fbxJointTransform = cmds.xform(fbxJoint, query=True, translation=True, worldSpace=True)
                fbxJointRadius = cmds.getAttr(fbxJoint + ".radius")
                sceneJointNew = cmds.joint(n=sceneJointName, position=fbxJointTransform)
                cmds.setAttr(sceneJointNew + ".radius", fbxJointRadius)
                if fbxJointParent:
                    cmds.parent(sceneJointNew, sceneJointParent)
        for nameSpace in nameSpaces:
            if nameSpaceTemp in nameSpace:
                cmds.namespace(removeNamespace=nameSpace, deleteNamespaceContent=True)


def PointOnPlane(*arr):
    objs = cmds.ls(selection=True)
    if len(objs) == 3:
        prefix = 'NLTA_PointOnPlan_'
        containGroup = prefix + 'ContaintGroup'
        cmds.delete([n for n in cmds.ls() if n.startswith(prefix)])    
        if not cmds.objExists(containGroup):
            cmds.select(clear=True)
            cmds.group(empty=True, name=containGroup)
        else:
            cmds.delete(containGroup)
            cmds.select(clear=True)
            cmds.group(empty=True, name=containGroup)

        loc1 = prefix + 'Loc1'
        if not cmds.objExists(loc1):
            cmds.select(clear=True)
            cmds.joint(name=loc1)
            cmds.matchTransform(loc1, objs[0], pos=True, rot=True)
            cmds.makeIdentity(loc1, apply=True, t=1, r=1, s=1, n=0)
            cmds.parent(loc1, containGroup)

        loc2 = prefix + 'Loc2'
        if not cmds.objExists(loc2):
            cmds.select(clear=True)
            cmds.joint(name=loc2)
            cmds.matchTransform(loc2, objs[1], pos=True, rot=True)
            cmds.makeIdentity(loc2, apply=True, t=1, r=1, s=1, n=0)
            cmds.parent(loc2, containGroup)

        loc3 = prefix + 'Loc3'
        if not cmds.objExists(loc3):
            cmds.select(clear=True)
            cmds.joint(name=loc3)
            cmds.matchTransform(loc3, objs[2], pos=True, rot=True)
            cmds.makeIdentity(loc3, apply=True, t=1, r=1, s=1, n=0)
            cmds.parent(loc3, containGroup)

        ctrl = prefix + 'Control'
        if not cmds.objExists(ctrl):
            cmds.select(clear=True)
            cmds.circle(name=ctrl, normal=(0, 1, 0), radius=1)
            cmds.matchTransform(ctrl, loc1, pos=True, rot=True)
            cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
            cmds.parent(ctrl, containGroup)
        
        projected = prefix + 'Projected'
        if not cmds.objExists(projected):
            cmds.select(clear=True)
            cmds.spaceLocator(name=projected)
            cmds.matchTransform(projected, loc1, pos=True, rot=True)
            cmds.makeIdentity(projected, apply=True, t=1, r=1, s=1, n=0)
            cmds.parent(projected, containGroup)

        def create_world_decomp(obj):
            node = cmds.createNode(
                'decomposeMatrix',
                name=prefix + '{}_worldDecomp'.format(obj)
            )

            cmds.connectAttr(
                '{}.worldMatrix[0]'.format(obj),
                '{}.inputMatrix'.format(node)
            )
            return node

        decomp1 = create_world_decomp(loc1)
        decomp2 = create_world_decomp(loc2)
        decomp3 = create_world_decomp(loc3)

        v1 = cmds.createNode('plusMinusAverage', name=prefix + 'v1_vector')
        cmds.setAttr('{}.operation'.format(v1), 2)
        cmds.connectAttr('{}.outputTranslate'.format(decomp2), '{}.input3D[0]'.format(v1))
        cmds.connectAttr('{}.outputTranslate'.format(decomp1), '{}.input3D[1]'.format(v1))

        v2 = cmds.createNode('plusMinusAverage', name=prefix + 'v2_vector')
        cmds.setAttr('{}.operation'.format(v2), 2)
        cmds.connectAttr('{}.outputTranslate'.format(decomp3), '{}.input3D[0]'.format(v2))
        cmds.connectAttr('{}.outputTranslate'.format(decomp1), '{}.input3D[1]'.format(v2))

        normal = cmds.createNode('vectorProduct', name=prefix + 'planeNormal')
        cmds.setAttr('{}.operation'.format(normal), 2)  # cross product
        cmds.setAttr('{}.normalizeOutput'.format(normal), 1)
        cmds.connectAttr('{}.output3D'.format(v1), '{}.input1'.format(normal))
        cmds.connectAttr('{}.output3D'.format(v2), '{}.input2'.format(normal))

        decomp_ctrl = create_world_decomp(ctrl)

        v_ctrl = cmds.createNode('plusMinusAverage', name=prefix + 'vecCtrlToPlane')
        cmds.setAttr('{}.operation'.format(v_ctrl), 2)
        cmds.connectAttr('{}.outputTranslate'.format(decomp_ctrl), '{}.input3D[0]'.format(v_ctrl))
        cmds.connectAttr('{}.outputTranslate'.format(decomp1), '{}.input3D[1]'.format(v_ctrl))

        dot = cmds.createNode('vectorProduct', name=prefix + 'dotVector')
        cmds.setAttr('{}.operation'.format(dot), 1)
        cmds.connectAttr('{}.output3D'.format(v_ctrl), '{}.input1'.format(dot))
        cmds.connectAttr('{}.output'.format(normal), '{}.input2'.format(dot))

        scaleVec = cmds.createNode('multiplyDivide', name=prefix + 'offsetVector')
        cmds.setAttr('{}.operation'.format(scaleVec), 1)
        cmds.connectAttr('{}.output'.format(normal), '{}.input1'.format(scaleVec))

        for axis in ['X', 'Y', 'Z']:
            cmds.connectAttr('{}.outputX'.format(dot), '{}.input2{}'.format(scaleVec, axis))

        projectedPos = cmds.createNode('plusMinusAverage', name=prefix + 'projectedPos')
        cmds.setAttr('{}.operation'.format(projectedPos), 2)
        cmds.connectAttr('{}.outputTranslate'.format(decomp_ctrl), '{}.input3D[0]'.format(projectedPos))
        cmds.connectAttr('{}.output'.format(scaleVec), '{}.input3D[1]'.format(projectedPos))

        cmds.connectAttr('{}.output3D'.format(projectedPos), '{}.translate'.format(projected))

        cmds.aimConstraint(
            ctrl,
            projected,
            aimVector=(1, 0, 0),       
            upVector=(0, 1, 0),        
            worldUpType="scene"       
        )


def GetAttrSelected(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        returnData = {
            "allAttr": []
        }
        mainAttr = cmds.channelBox("mainChannelBox", query=True, sma=True)
        if mainAttr:
            returnData["main"] = mainAttr
            returnData["allAttr"].extend(mainAttr)
        shapeAttr = cmds.channelBox("mainChannelBox", query=True, ssa=True)
        if shapeAttr:
            returnData["shape"] = shapeAttr
            returnData["allAttr"].extend(shapeAttr)
        inputAttr = cmds.channelBox("mainChannelBox", query=True, sha=True)
        if inputAttr:
            returnData["input"] = inputAttr
            returnData["allAttr"].extend(inputAttr)
        outputAttr = cmds.channelBox("mainChannelBox", query=True, soa=True)
        if outputAttr:
            returnData["output"] = outputAttr
            returnData["allAttr"].extend(outputAttr)
        for obj in objs:
            maxIncrease = len(returnData["allAttr"])
            numberIncrease = 0
            for attr in returnData["allAttr"]:
                if cmds.attributeQuery(attr, node=obj, ex=True):
                    numberIncrease += 1
            if maxIncrease == numberIncrease:
                returnData["obj"] = obj
        return (returnData)
    return (None)


def GetAttrSetting(data, *arr):
    returnData = {
        "obj": data["obj"],
        "attr": data["attr"],
        "key": cmds.getAttr(data["obj"] + "." + data["attr"], keyable=True),
        "hide": cmds.addAttr(data["obj"] + "." + data["attr"], query=True, hidden=True),
        "type": cmds.getAttr(data["obj"] + "." + data["attr"], typ=True),
        "defaultValue": cmds.addAttr(data["obj"] + "." + data["attr"], query=True, dv=True),
    }
    if cmds.addAttr(data["obj"] + "." + data["attr"], query=True, max=True):
        returnData["max"] = cmds.addAttr(data["obj"] + "." + data["attr"], query=True, max=True)
    if cmds.addAttr(data["obj"] + "." + data["attr"], query=True, min=True):
        returnData["min"] = cmds.addAttr(data["obj"] + "." + data["attr"], query=True, min=True)
    return (returnData)


currentAttribute = None


def ClipboarAttribute(*arr):
    global currentAttribute
    selected = GetAttrSelected()
    if selected:
        if selected["allAttr"]:
            currentAttribute = GetAttrSetting({
                "obj": selected["obj"],
                "attr": selected["allAttr"][0]
            })
            return (currentAttribute)
        else:
            print("No Attibute selected")


def SmartConnect(sourceSetting, targetSetting, *arr):
    if ("max" in sourceSetting) and ("max" in targetSetting) and ("min" in sourceSetting) and ("min" in targetSetting):
        if (sourceSetting["max"] != targetSetting["max"]) or (sourceSetting["min"] != targetSetting["min"]):
            remap = cmds.createNode('remapValue', name=sourceSetting["obj"] + "_" + targetSetting["obj"] + '_Remap')
            cmds.connectAttr(sourceSetting["obj"] + "." + sourceSetting["attr"], remap + ".inputValue", f=True)
            cmds.setAttr(remap + ".inputMin", sourceSetting["min"])
            cmds.setAttr(remap + ".inputMax", sourceSetting["max"])
            cmds.setAttr(remap + ".outputMin", targetSetting["min"])
            cmds.setAttr(remap + ".outputMax", targetSetting["max"])
            cmds.connectAttr(remap + ".outValue", targetSetting["obj"] + "." + targetSetting["attr"], f=True)
        else:
            cmds.connectAttr(sourceSetting["obj"] + "." + sourceSetting["attr"], targetSetting["obj"] + "." + targetSetting["attr"], f=True)
    else:
        cmds.connectAttr(sourceSetting["obj"] + "." + sourceSetting["attr"], targetSetting["obj"] + "." + targetSetting["attr"], f=True)


def DirectConnectAttribute(sourceSetting, targetSetting, *arr):
    cmds.connectAttr(sourceSetting["obj"] + "." + sourceSetting["attr"], targetSetting["obj"] + "." + targetSetting["attr"], f=True)


def ConnectAttribute(connectType, *arr):
    if currentAttribute:
        source = currentAttribute
        target = ClipboarAttribute()
        if connectType == "direct":
            DirectConnectAttribute(source, target)
        elif connectType == "smart":
            SmartConnect(source, target)


def CreateAttribute(*arr):
    attributeName = cmds.textField("NewAttributeName", width=100, query=True, text=True)
    selected = GetAttrSelected()
    attributeArray = []
    if "min" in currentAttribute:
        attributeArray.append("minValue=" + str(currentAttribute["min"]))
    if "max" in currentAttribute:
        attributeArray.append("maxValue=" + str(currentAttribute["max"]))
    if "key" in currentAttribute:
        attributeArray.append("keyable=" + str(currentAttribute["key"]))
    if "defaultValue" in currentAttribute:
        attributeArray.append("defaultValue=" + str(currentAttribute["defaultValue"]))
    if "hide" in currentAttribute:
        attributeArray.append("h=" + str(currentAttribute["hide"]))
    exec("cmds.addAttr('" + selected["obj"] + "',sn='" + attributeName + "'," + (",").join(attributeArray) + ")")


def ZeroTransform(*arr):
    sel = cmds.ls(sl=True)
    if sel:
        for obj in sel:
            keyable_attrs = cmds.listAttr(obj, keyable=True) or []            
            for attr in keyable_attrs:
                if attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
                    fullAttr = obj + "." + attr
                    cmds.setAttr(fullAttr, 0)


def getBoneMainAxis(parentBone, childBone):
    startPos = om.MVector(*cmds.xform(parentBone, q=True, ws=True, t=True))
    endPos = om.MVector(*cmds.xform(childBone, q=True, ws=True, t=True))

    boneDir = (endPos - startPos).normalize()

    mtx = cmds.xform(parentBone, q=True, ws=True, m=True)
    m = om.MMatrix(mtx)

    xAxis = om.MVector(m[0], m[1], m[2]).normalize()
    yAxis = om.MVector(m[4], m[5], m[6]).normalize()
    zAxis = om.MVector(m[8], m[9], m[10]).normalize()

    dotX = abs(boneDir * xAxis)
    dotY = abs(boneDir * yAxis)
    dotZ = abs(boneDir * zAxis)

    if dotX > dotY and dotX > dotZ:
        return "X"
    elif dotY > dotX and dotY > dotZ:
        return "Y"
    else:
        return "Z"


def NoteParentConstraint(*arr):
    sel = cmds.ls(selection=True)
    count = len(sel)
    if count < 2:
        cmds.warning("Please select a least 2 object.")
        return
    mid = count // 2
    drivers = sel[:mid]
    drivens = sel[mid:]

    if len(drivers) != len(drivens):
        cmds.warning("Drivers and Driverns not equal.")
        return
    for driver, driven in zip(drivers, drivens):
        attr_name = "NLTA_ConstraintBy"
        if not cmds.attributeQuery(attr_name, node=driven, exists=True):
            cmds.addAttr(driven, longName=attr_name, dataType="string")
            cmds.setAttr("{}.{}".format(driven, attr_name), driver, type="string")
        else:
            cmds.setAttr("{}.{}".format(driven, attr_name), driver, type="string")


def GetParentConstraintData(*arr):
    result = []
    attr_name = "NLTA_ConstraintBy"    
    all_transforms = cmds.ls(type="transform")
    for obj in all_transforms:
        if cmds.attributeQuery(attr_name, node=obj, exists=True):
            driver = cmds.getAttr("{}.{}".format(obj, attr_name))
            result.append([driver, obj])
    return result


def SaveParentConstraintData(*arr):
    data = GetParentConstraintData()
    path = ("/").join(os.path.dirname(pm.sceneName()).split('/')) + '/ParentConstraint.py'
    NLTA_General.writeJsonFile(path, data)


def ImportParentConstraintData(*arr):
    data = GetParentConstraintData()
    path = ("/").join(os.path.dirname(pm.sceneName()).split('/')) + '/ParentConstraint.py'
    pairs = NLTA_General.readJsonFile(path)
    if not pairs:
        pm.warning("Have no data to  import.")
        return

    attr_name = "NLTA_ConstraintBy"
    created = []
    for driver, driven in pairs:
        if not pm.objExists(driven):
            pm.warning("Driven object not exist")
            continue

        try:
            if not pm.attributeQuery(attr_name, node=driven, exists=True):
                pm.addAttr(driven, ln=attr_name, dt="string")
            pm.setAttr("{}.{}".format(driven, attr_name), driver, type="string")
            created.append((driver, driven))
        except Exception as e:
            pm.warning("Error to add attribute for {}: {}".format(driven, e))


def ClearParentConstraintData(*arr):
    attr_name = "NLTA_ConstraintBy"
    all_transforms = cmds.ls(selection=True)
    for obj in all_transforms:
        if cmds.attributeQuery(attr_name, node=obj, exists=True):
            cmds.deleteAttr("{}.{}".format(obj, attr_name))


def ClearAIAttribute(*arr):
    shading_engines = cmds.ls(type='shadingEngine')
    for se in shading_engines:
        for attr in cmds.listAttr(se, st='ai_*') or []:
            try:
                cmds.setAttr("{}.{}".format(se, attr), lock=False)
                cmds.deleteAttr("{}.{}".format(se, attr))
            except:
                pass


def TurnOffOCIO(*arr):
    cmds.colorManagementPrefs(e=True, cmEnabled=False)


def SaveGameExportSetting(*arr):
    exportPath = NLTA_General.GetCurrentPath() + "/NLTA_Data/ExportSetting.fbxexportpreset"
    os.makedirs(exportPath, exist_ok=True)
    cmds.FBXSaveExportPresetFile(presetFile=preset_path)


def LoadGameExportSetting(*arr):
    pass