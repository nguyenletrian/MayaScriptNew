import os
import shutil
import importlib
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import xml.dom.minidom as xd
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

########### SCRIPT JOB

import NLTA_General, NLTA_Mesh, NLTA_OpenMaya
for module in [NLTA_General, NLTA_Mesh, NLTA_OpenMaya]:
    try:
        importlib.reload(module)
    except:
        reload(module)


skinSession = {
    'mesh':None,
    'skinCluster':None,
    'joints':None,
}

def DetectCurrentSkin():
    global skinSession    
    selection = cmds.ls(selection=True)
    if not selection:
        return    
    obj = selection[0]    
    obj = obj.split('.')[0]
    shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
    if not shapes:
        return    
    shape = shapes[0]
    history = cmds.listHistory(shape) or []
    skins = cmds.ls(history, type='skinCluster')    
    if not skins:
        return    
    skin = skins[0]
    skinSession['mesh'] = obj
    skinSession['skinCluster'] = skin
    skinSession['joints'] = cmds.skinCluster(skin, q=True, inf=True)


def OpenSkinToolListen():
    jobs = cmds.scriptJob(listJobs=True)
    for job in jobs:
        if 'DetectCurrentSkin' in job:
            jobID = int(job.split(":")[0])
            cmds.scriptJob(kill=jobID, force=True)
    cmds.scriptJob(event=["ToolChanged",DetectCurrentSkin], protected=True)
    cmds.scriptJob(event=["SelectionChanged",DetectCurrentSkin], protected=True)
OpenSkinToolListen()


def GetSkinCluster(node):
    history = cmds.listHistory(node)
    skins = cmds.ls(history, type="skinCluster")
    return skins[0] if skins else None 


def getSkinClusterFn(skinCluster):
    sel = om.MSelectionList()
    sel.add(skinCluster)
    obj = sel.getDependNode(0)
    return oma.MFnSkinCluster(obj)

def GetVertexWeights(skinCluster, vert):
    infls = cmds.skinCluster(skinCluster, q=True, influence=True)
    weights = cmds.skinPercent(skinCluster, vert, q=True, value=True)
    return dict(zip(infls, weights))

def SetVertexWeights(skinCluster, vert, weightDict):
    influences = list(weightDict.keys())
    values = list(weightDict.values())
    cmds.skinPercent(
        skinCluster,
        vert,
        transformValue=list(zip(influences, values))
    )

def GetJointsWeight(data):
    skinCluster = data["skinCluster"]
    vert = data["vert"]
    joints = data["joints"]
    if not joints:
        return {}
    values = [
        cmds.skinPercent(skinCluster, vert, q=True, transform=j)
        for j in joints
    ]
    total = sum(values)
    result = {}
    for j, w in zip(joints, values):
        ratio = (w / total) if total != 0 else 0.0
        result[j] = {
            "weight": w,
            "ratio": ratio
        }
    return result

def GetJointsTotalWeight(skinCluster, vert, joints):
    if not joints:
        return 0.0
    values = cmds.skinPercent(
        skinCluster,
        vert,
        q=True,
        transformValue=joints
    )
    if not isinstance(values, (list, tuple)):
        values = [values]
    return sum(values)

def ActiveSkin(mesh,*arr):
    skinData = NLTA_General.GetSkinData(mesh)
    skinCluster = skinData["skinCluster"]
    if skinCluster:
        cmds.setAttr(skinCluster + ".envelope",1)

def DeactiveSkin(mesh,*arr):
    skinData = NLTA_General.GetSkinData(mesh)
    skinCluster = skinData["skinCluster"]
    if skinCluster:
        cmds.setAttr(skinCluster + ".envelope",0)

def component(*arr):    
    mel.eval("ComponentEditor;")
    
def pruneSmallWeights(*arr):    
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")
    mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 0;")
    mel.eval("PruneSmallWeights;")
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")
    mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 1;")  

def unlockAll(*arr):
    mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 0;")
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")

def lockAll(*arr):
    mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 1;")
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 1;")

def singleUnlock(objs,*arr):
    for joint in skinSession['joints']:
        cmds.setAttr(joint+'.liw',1)
    for obj in objs:
        cmds.setAttr(obj+'.liw',0)

def unlock(*arr):
    objs = cmds.ls(selection=True,type='joint')
    if objs:
        joints = []
        for obj in objs:
            print(obj)
            if obj in skinSession['joints']:
                joints.append(obj)
        cmds.select(skinSession['mesh'])
        singleUnlock(joints)
        mel.eval('ArtPaintSkinWeightsTool;')
        mel.eval('setSmoothSkinInfluence '+joints[0]+';')
    else:
        mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")
        mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 1;")

def UnlockJoints(mesh,jnts):
    skinJnts = NLTA_General.GetSkinData(mesh)["joints"]
    for jnt in skinJnts:
        if jnt in jnts:
            cmds.setAttr(jnt+".liw",0)
        else:
            cmds.setAttr(jnt+".liw",1)

def addUnlock(*arr):
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")    

def addUnlockUp(*arr):
    jointActive = cmds.connectionInfo(skinSession['skinCluster']+".paintTrans",sourceFromDestination=True).split(".")[0]
    parentJoint =  cmds.listRelatives(jointActive,parent=True)
    if parentJoint:
        parentJoint = parentJoint[0]
        singleUnlock([jointActive,parentJoint])
        mel.eval('ArtPaintSkinWeightsTool;')
        mel.eval('setSmoothSkinInfluence '+parentJoint+';')

def UnlockTwoJoints(*arr):
    sel = cmds.ls(sl=True, fl=True)
    if not sel:
        cmds.error("Please select one vertex.")
    vertex = sel[0]
    mesh = vertex.split(".")[0]
    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster")
    if not skins:
        cmds.error("No skinCluster found.")
    skin = skins[0]
    influences = cmds.skinCluster(skin, q=True, influence=True)
    weights = cmds.skinPercent(skin, vertex, q=True, value=True)
    data = [
        (joint, weight)
        for joint, weight in zip(influences, weights)
        if weight > 0.0
    ]
    if len(data) < 2:
        cmds.warning("Vertex has fewer than two influences.")
        return
    data.sort(key=lambda x: x[1], reverse=True)

    jointA = data[0][0]
    jointB = data[1][0]
    singleUnlock([jointA, jointB])
    cmds.select(clear=True)
    cmds.select(mesh)
    mel.eval("ArtPaintSkinWeightsTool;")
    mel.eval('setSmoothSkinInfluence "{}";'.format(jointB))
    return jointA, jointB


def addUnlockDown(*arr):
    print(skinSession)
    jointActive = cmds.connectionInfo(skinSession['skinCluster']+".paintTrans",sourceFromDestination=True).split(".")[0]
    childrenJoint =  cmds.listRelatives(jointActive,children=True)
    if childrenJoint:
        childJoint = childrenJoint[0]
        singleUnlock([jointActive,childJoint])
        mel.eval('ArtPaintSkinWeightsTool;')
        mel.eval('setSmoothSkinInfluence '+childJoint+';')

def ActiveJoint(mesh,joint,*arr):
    skinData = NLTA_General.GetSkinData(mesh)
    skinCluster = skinData["skinCluster"]
    cmds.connectAttr(joint+".message",skinCluster+".paintTrans",f=True)

def switchJoint(*arr):
    objName = cmds.ls(sl=True)[0]
    skinName = mel.eval('findRelatedSkinCluster '+objName)
    allJoints = cmds.skinCluster(objName,inf=True,q=True)
    jointCurrent = []
    for a in allJoints:
        if cmds.getAttr(a+".liw")!=1:
            jointCurrent.append(a)
    joint_active = cmds.connectionInfo(skinName+".paintTrans",sourceFromDestination=True).split(".")[0]
    if joint_active not in jointCurrent:
        index = 0
    else:
        index = jointCurrent.index(joint_active)
        if index < (len(jointCurrent) - 1):
            index = index + 1
        else:
            index = 0
    mel.eval('setSmoothSkinInfluence '+jointCurrent[index]+';artSkinRevealSelected artAttrSkinPaintCtx;')

def goToBindPose(*arr):
    mel.eval('GoToBindPose;')
    
def GetJointVertexs(mesh, joints, threshold=0.0001):
    skins = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
    if not skins:
        return []
    skin = skins[0]
    sel = om.MSelectionList()
    sel.add(mesh)
    dagPath = sel.getDagPath(0)
    sel.add(skin)
    skinObj = sel.getDependNode(1)
    fnSkin = oma.MFnSkinCluster(skinObj)
    infPaths = fnSkin.influenceObjects()
    jointSet = set(joints)
    infIndices = [i for i, inf in enumerate(infPaths)
                  if inf.partialPathName() in jointSet]
    if not infIndices:
        return []
    itVert = om.MItMeshVertex(dagPath)
    vtxIds = []
    while not itVert.isDone():
        vtxIds.append(itVert.index())
        itVert.next()
    compFn = om.MFnSingleIndexedComponent()
    comp = compFn.create(om.MFn.kMeshVertComponent)
    compFn.addElements(vtxIds)
    weights, infCount = fnSkin.getWeights(dagPath, comp)
    result = []
    for i, vId in enumerate(vtxIds):
        base = i * infCount
        for infId in infIndices:
            if weights[base + infId] > threshold:
                result.append("{}.vtx[{}]".format(mesh, vId))
                break
    return result

def IsolateEffectVertex(*args):
    selection = cmds.ls(selection=True)
    if selection:
        mesh = selection[0]
        currentData = NLTA_General.GetSkinData(mesh)
        jointActive = currentData["jointActive"]
        jointsUnlock = currentData["jointsUnlock"]
        vertexs = GetJointVertexs(mesh,[jointActive])
        cmds.setToolTo('selectSuperContext')
        cmds.select(clear=True)
        cmds.select(vertexs, add=True)
        panelCurrent = cmds.getPanel(withFocus=True)
        state = cmds.isolateSelect(panelCurrent, q=True, state=True)
        if state == 1:
            mel.eval('ToggleIsolateSelect;')
            mel.eval('ToggleIsolateSelect;')
        elif state == 0:
            mel.eval('ToggleIsolateSelect;')
        cmds.select(clear=True)
        cmds.select(mesh)
        try:
            cmds.ArtPaintSkinWeightsTool()
        except:
            pass

def clearMesh(*arr):
    for mesh in cmds.ls(selection=True):
        cmds.select(mesh)
        mel.eval('DeleteHistory;')
        cmds.setAttr(mesh+".translate",e=True,lock=0)
        cmds.setAttr(mesh+".rotate",e=True,lock=0)
        cmds.setAttr(mesh+".scale",e=True,lock=0)
        cmds.setAttr(mesh+".visibility",e=True,lock=0)
        mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')
        mel.eval('ResetTransformations;')




def ClearWeight(JointActive):
    verts = NLTA_Mesh.GetVertexsSelected()
    if verts:
        mesh = verts[0].split(".")[0]
        skinData = NLTA_General.GetSkinData(mesh)    
        skin = skinData["skinCluster"]
        jointActive = skinData["jointActive"]
        if not skin:
            cmds.warning("Haven't skinCluster")
            return
        for v in verts:
            influences = cmds.skinPercent(skin, v, q=True, transform=None)
            weights    = cmds.skinPercent(skin, v, q=True, value=True)        
            if not influences or not weights:
                continue
            weightMap = dict(zip(influences, weights))
            if jointActive not in weightMap:
                print("not in weight map")
                continue
            sourceW = weightMap[jointActive]
            if sourceW <= 0.0:
                continue        
            dominantJoint = None
            max_w = -1        
            for j, w in weightMap.items():
                if j == jointActive:
                    continue            
                if w > max_w:
                    max_w = w
                    dominantJoint = j
            if not dominantJoint:
                continue        
            # transfer
            new_dom_w = weightMap.get(dominantJoint, 0.0) + sourceW        
            cmds.skinPercent(skin,v,transformValue=[
                    (dominantJoint, new_dom_w),
                    (jointActive, 0.0)
                ]
            )
        
        cmds.skinCluster(skin, e=True, forceNormalizeWeights=True)    
        print("Done transfer on selected vertices")

def setMiddleWeight(*arr):
    cmds.currentTime(0)
    selection = cmds.ls(selection=True)
    middleJoint = selection[0]
    vertexArray = []
    jointArray = []
    for a in selection:
        if cmds.objectType(a) == "joint":
            if a != middleJoint:
                jointArray.append(a)
        elif ".vtx[" in a :
            vertexArray.append(a)
    mesh = vertexArray[0].split(".")[0]
    skinCluster = mel.eval('findRelatedSkinCluster '+mesh)
    if skinCluster:
        jointBindArray = cmds.skinCluster(skinCluster,query=True,inf=True)
        for jointBind in jointBindArray:
            cmds.setAttr(jointBind+".liw",0)
        for ver in vertexArray:
            cmds.skinPercent(skinCluster,ver, transformValue=[middleJoint,1])
        for jointBind in jointBindArray:
            cmds.setAttr(jointBind+".liw",1)
    averageWeight = float(1.0/(len(jointArray)+1))
    for joint in jointArray:
        cmds.setAttr(joint+".liw",0)
        cmds.setAttr(middleJoint+".liw",0)
        for ver in vertexArray:
            cmds.skinPercent(skinCluster,ver, transformValue=[joint,averageWeight])
        cmds.setAttr(joint+".liw",1)
        cmds.setAttr(middleJoint+".liw",1)
    for joint in jointArray:
        cmds.setAttr(joint+".liw",0)
    cmds.setAttr(middleJoint+".liw",0)

    cmds.select(jointArray)
    component()
    cmds.select(vertexArray)

def mirrorSkin(axis,neg_pos,*arr):
    selection = cmds.ls(selection=True)
    component = ";"
    if ".vtx[" in selection[0]:
        component = " -selectedComponents;"
        mesh = selection[0].split(".")[0]
        if axis == "x":
            mel.eval("reflectionSetMode objectx;")
        else:
            mel.eval("reflectionSetMode objectx;")        
        mel.eval("reflectionSetMode none;")
    else:
        mesh = selection[0]

    currentSkinCluster = mel.eval('findRelatedSkinCluster '+mesh)  
    if axis == "x":
        face = "YZ"
    if neg_pos == "-":
        mel.eval("copySkinWeights -ss "+currentSkinCluster+" -ds "+currentSkinCluster+" -mirrorMode "+face+" -mirrorInverse -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne"+component)
    elif neg_pos == "+":  
        mel.eval("copySkinWeights -ss "+currentSkinCluster+" -ds "+currentSkinCluster+" -mirrorMode "+face+" -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne"+component)

def ExportAllSkinUrl(folder,*arr):
    jsonData = {}
    jsonPath = folder+'/skinData.json'
    if len(cmds.ls(selection=True))!=0:
        meshTransform = cmds.ls(selection=True)
    else:
        meshTransform = cmds.listRelatives(cmds.ls(type = "mesh",ap=True),parent=True,pa=True)
        meshTransform = list(set(meshTransform))
    for transform in meshTransform:
        skin_name = mel.eval('findRelatedSkinCluster '+transform)
        transformName = transform
        transformName = transformName.replace("|","&")
        transformName = transformName.replace(":","%")
        if skin_name:
            jsonData[transformName] = {
                'skinName':skin_name
            }
            version = cmds.about(version=True)
            if version in ["2018"]:
                mel.eval('deformerWeights -export -deformer "'+skin_name+'" -path "'+folder+'" "'+transformName+'.xml";')
            else:
                mel.eval('deformerWeights -export -deformer "'+skin_name+'" -format "XML" -path "'+folder+'" "'+transformName+'.xml";')
            NLTA_General.writeJsonFile(jsonPath,jsonData)

def ExportAllSkin(*arr):
    folder_temp = os.path.dirname(pm.sceneName())
    if not folder_temp:
        folder_temp = mel.eval("SaveSceneAs;")
    folder_temp = os.path.dirname(pm.sceneName())
    if folder_temp:
        folder_temp = os.path.join(os.path.dirname(pm.sceneName()), 'bnlta_all_skins_export')
        folder_temp = cmds.encodeString(folder_temp)
        if os.path.exists(folder_temp):
            shutil.rmtree(folder_temp)
        if not os.path.exists(folder_temp):
            os.makedirs(folder_temp)
        ExportAllSkinUrl(folder_temp)
        cmds.warning("Done!!!")

def ExportFolderSkinSingle(url,*arr):
    dataTemp = {}
    meshs = cmds.ls(selection=True)
    for mesh in meshs:
        dataTemp[mesh] = {}
        dataTemp[mesh]["uuid"] = cmds.ls(mesh,uuid=True)
        meshParent =  cmds.listRelatives(mesh,parent=True)
        if meshParent:
            dataTemp[mesh]["parent"] =  meshParent[0]
            cmds.parent(mesh, world=True)
        else:
            dataTemp[mesh]["parent"] = None
        if "NLTA_" not in mesh:
            cmds.rename(mesh,"NLTA_"+mesh)
            dataTemp[mesh]["nameTemp"] = "NLTA_"+mesh
        else:
            dataTemp[mesh]["nameTemp"] = mesh
    cmds.select(clear=True)
    for mesh in dataTemp:
        cmds.select(cmds.ls(dataTemp[mesh]["uuid"]),add=True)
    cmds.file(url +'/mesh.obj', force=True, options="groups=1;ptgroups=0;materials=0;smoothing=0;normals=1", type='OBJexport', exportSelected=True)
    ExportAllSkinUrl(url)
    for mesh in dataTemp:
        if dataTemp[mesh]["parent"]!=None:
            cmds.parent(dataTemp[mesh]["nameTemp"],dataTemp[mesh]["parent"])
        cmds.rename(cmds.ls(dataTemp[mesh]["uuid"])[0],mesh)

def ExportFolderSkin(*arr):
    url = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="Select Folder")[0]
    ExportFolderSkinSingle(url)

def ExportFolderSkinQuick(*arr):
    scenePath = cmds.file(q=True, sn=True)
    if not scenePath:
        cmds.warning("Please save scene first")
        return
    sceneFolder = os.path.dirname(scenePath)
    exportFolder = os.path.join(
        sceneFolder,
        "NLTA_Data",
        "MeshExport"
    )
    exportFolder = exportFolder.replace("\\", "/")
    if not os.path.exists(exportFolder):
        os.makedirs(exportFolder)
    ExportFolderSkinSingle(exportFolder)
    cmds.warning("Done!!!")

def ImportAllSkinUrl(folder,keepHistory,*arr):
    if os.path.exists(folder):
        jsonData = {}
        jsonPath = folder+'/skinData.json'
        if os.path.exists(jsonPath):
            jsonData = NLTA_General.readJsonFile(jsonPath)
        cmds.currentTime(0)
        if len(cmds.ls(selection=True))!=0:
            meshTransform = cmds.ls(selection=True)
        else:
            meshTransform = cmds.listRelatives(cmds.ls(type = "mesh",ap=True),parent=True,pa=True)
            meshTransform = list(set(meshTransform))
        for transform in meshTransform:
            transformName = transform
            transformName = transformName.replace("|","&")
            transformName = transformName.replace(":","%")
            
            each_file = ""
            fileLink = cmds.encodeString(folder + "/" + transformName + ".xml")
            print(fileLink)
            if os.path.exists(fileLink):
                each_file = fileLink            
            fileLinkSame = cmds.encodeString(folder + "/" + transformName + ".xml")
            if os.path.exists(fileLinkSame):
                each_file = fileLinkSame

            if each_file!="":
                print(transformName)
                joints = []
                xFile = xd.parse(each_file)
                elements = xFile.getElementsByTagName("weights")
                for e in elements:
                    attrs = e.attributes.keys()
                    for a in attrs:
                        if a == "source":
                            pair = e.attributes[a]
                            joints.append(pair.value)

                if not keepHistory:
                    cmds.select(transform)
                    mel.eval('DeleteHistory;')
                    for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
                        cmds.setAttr(transform+"."+attr,lock=False)
                    mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')
                    mel.eval('ResetTransformations;')

                if len(joints)!=0:
                    cmds.select(clear=True)
                    for b in joints:
                        if len(cmds.ls(b))>1:
                            print("More than one joint name is "+b)
                        else:
                            if cmds.objExists(b):                            
                                cmds.select(b,add=True)
                            else:
                                print("Cant find joint name "+b)
                    jointSelection = cmds.ls(selection=True)
                    shapes = cmds.listRelatives(transform,children=True,type='mesh')
                    
                    connsData = []
                    attrsReconns = ['visibility']
                    for shape in shapes:
                        for attr in attrsReconns:
                            print(shape)
                            print(attr)
                            src = cmds.connectionInfo(shape+"."+attr, sourceFromDestination=True)
                            if src:
                                connsData.append([src,shape+'.'+attr])

                    for i in range(len(connsData)):
                        conn = connsData[i]
                        cmds.disconnectAttr(conn[0],conn[1])

                    for shape in shapes:
                        cmds.setAttr(shape+'.visibility',1)
                        
                    if jointSelection:
                        cmds.select(transform,add=True)
                        if not keepHistory:
                            skin_name = cmds.skinCluster(cmds.ls(selection=True),toSelectedBones=True,bindMethod=0,skinMethod=0,normalizeWeights=1,maximumInfluences=1)[0]
                        else:
                            skinData = NLTA_General.GetSkinData(transformName)
                            skin_name = skinData["skinCluster"] 
                        mel.eval('deformerWeights -import -method "index" -deformer "'+skin_name+'" -path "'+folder+'/" "'+transformName+'.xml"; skinCluster -e -forceNormalizeWeights "'+skin_name+'";')
                        if jsonData !={} and (transform in jsonData):
                            cmds.rename(skin_name,jsonData[transform]['skinName'])
                    for i in range(len(connsData)):
                        conn = connsData[i]
                        cmds.connectAttr(conn[0],conn[1], force=True)                        
    else:
        cmds.confirmDialog(title="Confirm",message="Dont have data!",button=["Yes"],defaultButton="Yes",cancelButton="Yes") 

def ImportAllSkin(*arr):
    folder = os.path.dirname(pm.sceneName())+"/"+'bnlta_all_skins_export'
    ImportAllSkinUrl(folder,False)
    cmds.warning("Done!!!")

def ImportAllSkinExist(*arr):
    folder = os.path.dirname(pm.sceneName())+"/"+'bnlta_all_skins_export'
    ImportAllSkinUrl(folder,True)
    cmds.warning("Done!!!")

def ImportFolderSkinSingle(url,*arr):
    if url:
        files = NLTA_General.GetFiles(url,'obj')
        for file_ in files:
            filePath =  url+"/"+file_+".obj"
            cmds.file(filePath, i=True, type="OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace=":", options="mo=1", pr=True)
    ImportAllSkinUrl(url,False)
    cmds.warning("Done!!!")

def ImportFolderSkin(*arr):
    url = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="Select Folder")[0]
    ImportFolderSkinSingle(url)

def ImportFolderSkinQuick(*arr):
    scenePath = cmds.file(q=True, sn=True)
    if not scenePath:
        cmds.warning("Please save scene first")
        return
    sceneFolder = os.path.dirname(scenePath)
    importFolder = os.path.join(
        sceneFolder,
        "NLTA_Data",
        "MeshExport"
    )
    importFolder = importFolder.replace("\\", "/")
    if not os.path.exists(importFolder):
        cmds.warning("Import folder not found:\n" + importFolder)
        return
    ImportFolderSkinSingle(importFolder, False)
    cmds.warning("Import Done!!!")


def fixMaxInfluence(maxInfluence,*arr):
    maxInfluence = cmds.intField("maxInfluent",value=True,query=True)
    meshes = cmds.ls(selection=True, type="mesh")
    if not meshes:
        meshes = cmds.ls(type="mesh")
    for mesh in meshes:
        skin = GetSkinCluster(mesh)
        if not skin:
            continue
        dagPath = NLTA_OpenMaya.GetDagPath(mesh)
        mfnMesh = om.MFnMesh(dagPath)
        sel = om.MSelectionList()
        sel.add(skin)
        skinObj = sel.getDependNode(0)
        skinFn = oma.MFnSkinCluster(skinObj)
        infPaths = skinFn.influenceObjects()
        infCount = len(infPaths)
        comp = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
        vtxCount = mfnMesh.numVertices
        om.MFnSingleIndexedComponent(comp).addElements(range(vtxCount))
        weights, infCount = skinFn.getWeights(dagPath, comp)
        newWeights = list(weights)
        for i in range(vtxCount):
            start = i * infCount
            end = start + infCount
            w = list(weights[start:end])
            indexed = [(j, w[j]) for j in range(len(w)) if w[j] > 0]
            if len(indexed) > maxInfluence:
                indexed.sort(key=lambda x: x[1], reverse=True)
                keep = indexed[:maxInfluence]
                keep_indices = [k[0] for k in keep]
                for j in range(len(w)):
                    if j not in keep_indices:
                        w[j] = 0.0
                total = sum(w)
                if total > 0:
                    w = [val / total for val in w]
                newWeights[start:end] = w
        infIndices = om.MIntArray(range(infCount))
        newWeightsArray = om.MDoubleArray(newWeights)
        skinFn.setWeights(dagPath, comp, infIndices, newWeightsArray, True)
    cmds.warning("Done (OpenMaya)!!!")


def fixMaxInfluenceAll(maxValue,*arr):
    cmds.select(clear=True)
    for a in cmds.ls(type="mesh"):
        if a.endswith("Orig")!=True:
            for b in cmds.listHistory(a):
                if cmds.objExists(b) and cmds.objectType(b) == "skinCluster":
                    cmds.select(cmds.listRelatives(a,parent=True)[0],add=True)
    fixMaxInfluence(maxValue)
    cmds.warning("Done!!!")

def checkMaxInfluentNumber(val,*arr):
    if len(cmds.ls(sl=True)) !=0:
        maxValue = val
        objName = cmds.ls(sl=True)[0]
        vertex = cmds.ls(objName+'.vtx[*]',fl=True)
        skinName = mel.eval('findRelatedSkinCluster '+objName)
        cmds.select(clear=True)
        arrayTemp = []
        for a in vertex:
            joints = cmds.skinPercent(skinName,a,query=True,transform=None)
            values = cmds.skinPercent(skinName,a,query=True,value=True)
            jointsTemp = []
            for b in range(len(joints)):
                if values[b]>0:
                    jointsTemp.append(joints[b])
            if len(jointsTemp) > maxValue:
                arrayTemp.append(a)
        if cmds.objExists("vertexOverMaxInfluence"):
            cmds.delete("vertexOverMaxInfluence")
        cmds.select(arrayTemp)
        #mel.eval('sets -name "vertexOverMaxInfluence";')
    cmds.warning("Done!!!")


def checkMaxInfluenceNumber(maxValue, *args):
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("No object selected")
        return
    obj = sel[0]
    skin = GetSkinCluster(obj)
    if not skin:
        cmds.warning("No skinCluster found")
        return
    dag = NLTA_Mesh.GetDagpath(obj)
    mfn_mesh = om.MFnMesh(dag)
    sel_list = om.MSelectionList()
    sel_list.add(skin)
    skin_obj = sel_list.getDependNode(0)
    skin_fn = om.MFnSkinCluster(skin_obj)
    vert_count = mfn_mesh.numVertices
    comp_fn = om.MFnSingleIndexedComponent()
    comp = comp_fn.create(om.MFn.kMeshVertComponent)
    comp_fn.addElements(list(range(vert_count)))
    weights, influence_count = skin_fn.getWeights(dag, comp)
    result = []
    for i in range(vert_count):
        start = i * influence_count
        end = start + influence_count
        w = weights[start:end]
        count = sum(1 for val in w if val > 0.0001)
        if count > maxValue:
            result.append("{}.vtx[{}]".format(obj, i))
    if cmds.objExists("vertexOverMaxInfluence"):
        cmds.delete("vertexOverMaxInfluence")
    cmds.select(result)
    if result:
        cmds.sets(result, name="vertexOverMaxInfluence")
    cmds.warning("Done!!!")


def checkMaxInfluent(*arr):
    if len(cmds.ls(sl=True)) !=0:
        maxValue = cmds.intField("maxInfluent",query=True,value=True)
        print(maxValue)
        checkMaxInfluentNumber(maxValue)


def TransferTopWeight(vertex):    
    vertex = cmds.ls(sl=True, fl=True)[0]
    amount = cmds.artAttrSkinPaintCtx(
        "artAttrSkinContext",
        q=True,
        value=True
    )
    mesh = vertex.split(".")[0]

    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster")

    if not skins:
        raise RuntimeError("No skinCluster found.")

    skin = skins[0]

    influences = cmds.skinCluster(skin, q=True, influence=True)
    weights = cmds.skinPercent(skin, vertex, q=True, value=True)

    data = list(zip(influences, weights))
    data.sort(key=lambda x: x[1], reverse=True)

    jointA, weightA = data[0]
    jointB, weightB = data[1]

    if weightA <= 0.0:
        return False

    transfer = min(amount, weightA)

    newWeightA = weightA - transfer
    newWeightB = weightB + transfer

    normalize = cmds.getAttr(skin + ".normalizeWeights")
    cmds.setAttr(skin + ".normalizeWeights", 0)

    try:
        cmds.skinPercent(
            skin,
            vertex,
            transformValue=[
                (jointA, newWeightA),
                (jointB, newWeightB)
            ],
            normalize=False
        )
    finally:
        cmds.setAttr(skin + ".normalizeWeights", normalize)
    return jointA, jointB, newWeightA, newWeightB
        


def clearSkin(*arr):
    for a in cmds.ls(type="mesh"):
        if cmds.objExists(a):
            for b in cmds.listHistory(a):
                if cmds.objExists(b) and cmds.objectType(b) == "skinCluster":
                    cmds.select(a)
                    mel.eval('DeleteHistory;')
    cmds.warning("Done!!!")

def removeUnneedJoint(*arr):
    cmds.currentTime(0)
    if len(cmds.ls(selection=True))!=0:
        meshTransform = cmds.ls(selection=True)
    else:
        meshTransform = cmds.listRelatives(cmds.ls(type = "mesh",ap=True),parent=True,pa=True)
        meshTransform = list(set(meshTransform))
    for transform in meshTransform:
        skinCluster = mel.eval('findRelatedSkinCluster '+transform)
        if skinCluster:
            joints = cmds.skinCluster(skinCluster,query=True,inf=True)
            removeJoints = []
            for joint in joints:
                flag = False
                cmds.select(clear=True)
                mel.eval('skinCluster -e -selectInfluenceVerts '+joint+' '+skinCluster+';')
                selection = cmds.ls(selection=True)
                if len(selection) == 1:
                    if '.vtx[' not in selection[0]:
                        flag = True
                if flag == True:
                    removeJoints.append(joint)            
            cmds.skinCluster(skinCluster, e=True, removeInfluence=removeJoints)
            print('Remove Joint '+ (' - ').join(removeJoints))
    cmds.select(meshTransform)
    cmds.warning("Done!!!")

def AddMeshJoint(*arr):
    cmds.currentTime(0)
    sel = cmds.ls(selection=True)
    if len(cmds.ls(selection=True)) >= 2:
        selection =  cmds.ls(selection=True)
        source = selection[0]
        destinations =  selection[1:]        
        skinClusterSource = mel.eval('findRelatedSkinCluster '+ source)
        for destination in destinations:            
            skinClusterDestination =  mel.eval('findRelatedSkinCluster '+ destination)
            if skinClusterSource and skinClusterDestination:
                jointsSource = cmds.skinCluster(skinClusterSource,query=True,inf=True)
                jointsDestination =  cmds.skinCluster(skinClusterDestination,query=True,inf=True)
                jointsAdd = []
                for joint in jointsSource:
                    if joint not in jointsDestination:
                        jointsAdd.append(joint)
                cmds.skinCluster(skinClusterDestination, edit=True, addInfluence=jointsAdd, weight=0)
                print('Add Joint '+ (' - ').join(jointsAdd))
                cmds.warning("Done!!!")

def AddJoint(*arr):
    cmds.currentTime(0)
    if len(cmds.ls(selection=True)) >= 2:
        selection =  cmds.ls(selection=True)
        jnts = cmds.ls(selection=True,type="joint")
        meshs =  cmds.listRelatives(cmds.ls(type ="mesh",ap=True),parent=True,pa=True)
        meshBind = []
        for mesh in meshs:
            if (mesh in selection) and (mesh not in jnts):
                if mesh not in meshBind:
                    skinCluster =  mel.eval('findRelatedSkinCluster '+mesh)
                    if skinCluster:
                        meshJoints = cmds.skinCluster(skinCluster,query=True,inf=True)
                        jointsAdd = []
                        for joint in jnts:
                            if joint not in meshJoints:
                                jointsAdd.append(joint)
                        cmds.skinCluster(skinCluster, edit=True, addInfluence=jointsAdd, weight=0)
                        print('Add Joint '+ (' - ').join(jointsAdd))
                meshBind.append(mesh)
        cmds.warning("Done!!!")

def RemoveJoint(*args):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True)
    if len(selection) < 2:
        cmds.warning("Select one or more joints and one or more meshes.")
        return
    joints = cmds.ls(selection, type="joint")
    if not joints:
        cmds.warning("No joints selected.")
        return
    meshes = cmds.listRelatives(cmds.ls(type="mesh", ap=True),p=True,pa=True) or []
    processed = []
    for mesh in meshes:
        if mesh not in selection:
            continue
        if mesh in processed:
            continue
        skinCluster = mel.eval("findRelatedSkinCluster {}".format(mesh))
        if not skinCluster:
            continue
        influences = cmds.skinCluster(skinCluster,q=True,inf=True)
        for joint in joints:
            if joint not in influences:
                continue
            if len(influences) <= 1:
                cmds.warning("{} only has one influence.".format(mesh))
                continue
            parent = cmds.listRelatives(joint,p=True,type="joint")
            if not parent:
                cmds.warning("{} has no parent. Skip.".format(joint))
                continue
            parent = parent[0]
            if parent not in influences:
                cmds.skinCluster(skinCluster,e=True,ai=parent,lw=True,wt=0)
                influences.append(parent)
            cmds.select(clear=True)
            cmds.skinCluster(skinCluster,e=True,selectInfluenceVerts=joint)
            verts = cmds.filterExpand(sm=31) or []
            verts = cmds.ls(verts, fl=True)
            if verts:
                cmds.select(verts)
                for v in verts:
                    w = cmds.skinPercent(skinCluster,v,transform=joint,q=True)
                    if w <= 0:
                        continue
                    parentWeight = cmds.skinPercent(skinCluster,v,transform=parent,q=True)
                    cmds.skinPercent(skinCluster,v,tv=[(parent, parentWeight + w),(joint, 0)])
            cmds.skinCluster(skinCluster,e=True,ri=joint)
            influences.remove(joint)
        processed.append(mesh)
    cmds.select(clear=True)

    cmds.warning("Done!")
def ExportSkinFbx(*arr):
    objs = cmds.ls(selection=True)
    for obj in objs:
        meshTransform = []                
        children = cmds.listRelatives(obj,ad=True,type='mesh')
        if children:
            for child in children:
                childVisAttr = child+ '.visibility'
                childVisConns = cmds.listConnections(childVisAttr, source=True, destination=False, plugs=True)
                if childVisConns:
                    for conn in childVisConns:
                        cmds.disconnectAttr(conn,childVisAttr)
                cmds.setAttr(childVisAttr,1)
                parentTransform = cmds.listRelatives(child,parent=True)
                if parentTransform:
                    parentName = parentTransform[0]
                    if parentName not in meshTransform:
                        meshTransform.append(parentName)
        for transform in meshTransform:                
            transformVisAttr = transform + '.visibility' 
            transformVisConns = cmds.listConnections(transformVisAttr, source=True, destination=False, plugs=True)
            if transformVisConns:
                for conn in transformVisConns:
                    cmds.disconnectAttr(conn,transformVisAttr)
            print(transformVisAttr)
            cmds.setAttr(transformVisAttr,1)
            
    layers = cmds.ls(type='displayLayer')
    for layer in layers:
        if layer == 'defaultLayer':
            continue
        cmds.setAttr(layer+".visibility", 1)
        cmds.setAttr(layer+".displayType", 0)
        
    
    scenePath = cmds.file(q=True, sn=True)
    sceneDir = os.path.dirname(scenePath)
    sceneName = os.path.splitext(os.path.basename(scenePath))[0]
    exportPath = sceneDir+'/'+sceneName+"_SkinFbx.fbx"

    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya', quiet=True)
    mel.eval('FBXExportShapes -v false')
    mel.eval('FBXExportInputConnections -v false')
    mel.eval('FBXExportEmbeddedTextures -v false')
    mel.eval('FBXExportSkins -v true')
    mel.eval('FBXExportSmoothMesh -v true')
    mel.eval('FBXExportSmoothingGroups -v true')
    mel.eval('FBXExportConstraints -v false')    
    mel.eval('FBXExport -f "{0}" -s'.format(exportPath))

def ObjToNewScene(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        result = cmds.promptDialog(
            title='New scene name',
            message='Input new sence name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result != 'OK':            
            return
        ExportSkinFbx()
        scenePath = cmds.file(q=True, sn=True)
        sceneDir = os.path.dirname(scenePath)
        sceneName = os.path.splitext(os.path.basename(scenePath))[0]
        exportPath = sceneDir+'/'+sceneName+"_SkinFbx.fbx"
        newSceneName = cmds.promptDialog(query=True, text=True)
        if not newSceneName.strip():
            cmds.error("Scene name not correct.")
        newScenePath = sceneDir+'/'+newSceneName+'.ma'
        cmds.file(new=True, force=True)
        cmds.file(rename=newScenePath)
        cmds.file(save=True, type='mayaAscii')
        cmds.file(exportPath, i=True, type="FBX", ignoreVersion=True, options="fbx", ra=True, mergeNamespacesOnClash=False)
    else:
        print('Nothing is selected')

