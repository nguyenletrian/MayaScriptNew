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

def ResetSkinSession():
    skinSession.update({"mesh": None, "skinCluster": None, "joints": None})
    return skinSession


def GetSkinData(node=None):
    if node is None:
        selection = cmds.ls(sl=True, fl=True) or []
        if not selection:
            return {"mesh": None, "skinCluster": None, "joints": []}
        node = selection[0]

    mesh = node.split(".")[0]
    if not cmds.objExists(mesh):
        return {"mesh": None, "skinCluster": None, "joints": []}

    shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True, fullPath=True) or []
    search_node = shapes[0] if shapes else mesh
    history = cmds.listHistory(search_node, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster") or []
    skin = skins[0] if skins else None
    joints = cmds.skinCluster(skin, q=True, inf=True) or [] if skin else []
    return {"mesh": mesh if skin else None, "skinCluster": skin, "joints": joints}


def EnsureSkinSession(node=None, warn=True):
    data = GetSkinData(node)
    if data["skinCluster"]:
        skinSession.update(data)
        return skinSession

    # If nothing useful is selected, preserve a still-valid cached session.
    cached_skin = skinSession.get("skinCluster")
    if cached_skin and cmds.objExists(cached_skin):
        cached_mesh = skinSession.get("mesh")
        cached_joints = cmds.skinCluster(cached_skin, q=True, inf=True) or []
        skinSession.update({"mesh": cached_mesh, "skinCluster": cached_skin, "joints": cached_joints})
        return skinSession

    ResetSkinSession()
    if warn:
        cmds.warning("No skinned mesh found. Select a skinned mesh or one of its vertices.")
    return None


def GetActivePaintJoint(skinCluster=None):
    if not skinCluster:
        session = EnsureSkinSession(warn=False)
        skinCluster = session["skinCluster"] if session else None
    if not skinCluster or not cmds.objExists(skinCluster):
        return None

    plug = skinCluster + ".paintTrans"
    source = cmds.connectionInfo(plug, sourceFromDestination=True) or ""
    return source.split(".", 1)[0] if source else None


def GetSkinApi(mesh, skinCluster=None):
    skinCluster = skinCluster or GetSkinCluster(mesh)
    if not skinCluster:
        return None, None, None

    dagPath = NLTA_OpenMaya.GetDagPath(mesh)
    sel = om.MSelectionList()
    sel.add(skinCluster)
    skinFn = oma.MFnSkinCluster(sel.getDependNode(0))
    return dagPath, skinFn, skinCluster


def CreateVertexComponent(vertexIds):
    compFn = om.MFnSingleIndexedComponent()
    comp = compFn.create(om.MFn.kMeshVertComponent)
    compFn.addElements(vertexIds)
    return comp


def DetectCurrentSkin(*args):
    selection = cmds.ls(sl=True, fl=True) or []
    if not selection:
        return

    data = GetSkinData(selection[0])
    if data["skinCluster"]:
        skinSession.update(data)


def OpenSkinToolListen():
    for job in cmds.scriptJob(listJobs=True) or []:
        if "DetectCurrentSkin" in job:
            try:
                cmds.scriptJob(kill=int(job.split(":", 1)[0]), force=True)
            except (TypeError, ValueError, RuntimeError):
                pass

    cmds.scriptJob(event=["ToolChanged", DetectCurrentSkin], protected=True)
    cmds.scriptJob(event=["SelectionChanged", DetectCurrentSkin], protected=True)
    DetectCurrentSkin()
OpenSkinToolListen()


def GetSkinCluster(node):
    if not node or not cmds.objExists(node.split(".")[0]):
        return None
    return GetSkinData(node)["skinCluster"]


def getSkinClusterFn(skinCluster):
    if not skinCluster or not cmds.objExists(skinCluster):
        return None
    sel = om.MSelectionList()
    sel.add(skinCluster)
    return oma.MFnSkinCluster(sel.getDependNode(0))

def GetVertexWeights(skinCluster, vert):
    if not skinCluster or not cmds.objExists(skinCluster):
        return {}
    influences = cmds.skinCluster(skinCluster, q=True, influence=True) or []
    weights = cmds.skinPercent(skinCluster, vert, q=True, value=True) or []
    return dict(zip(influences, weights))

def SetVertexWeights(skinCluster, vert, weightDict):
    if not skinCluster or not weightDict:
        return
    cmds.skinPercent(skinCluster, vert, transformValue=list(weightDict.items()))

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

def singleUnlock(objs, *arr):
    session = EnsureSkinSession()
    if not session:
        return []

    joints = session["joints"] or []
    unlock_set = set(objs or [])
    for joint in joints:
        if cmds.objExists(joint + ".liw"):
            cmds.setAttr(joint + ".liw", 0 if joint in unlock_set else 1)
    return [joint for joint in joints if joint in unlock_set]

def unlock(*arr):
    selected_joints = cmds.ls(sl=True, type="joint") or []
    session = EnsureSkinSession()
    if not session:
        return

    if not selected_joints:
        mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")
        mel.eval("artSkinInvLockInf artAttrSkinPaintCtx 1;")
        return

    joints = [joint for joint in selected_joints if joint in (session["joints"] or [])]
    if not joints:
        cmds.warning("Selected joints are not influences of the active skinCluster.")
        return

    cmds.select(session["mesh"], r=True)
    singleUnlock(joints)
    mel.eval("ArtPaintSkinWeightsTool;")
    mel.eval('setSmoothSkinInfluence "{}";'.format(joints[0]))

def UnlockJoints(mesh, jnts):
    skinJnts = GetSkinData(mesh)["joints"] or []
    target = set(jnts or [])
    for jnt in skinJnts:
        if cmds.objExists(jnt + ".liw"):
            cmds.setAttr(jnt + ".liw", 0 if jnt in target else 1)

def addUnlock(*arr):
    mel.eval("artSkinLockInf artAttrSkinPaintCtx 0;")    

def addUnlockUp(*arr):
    session = EnsureSkinSession()
    if not session:
        return

    jointActive = GetActivePaintJoint(session["skinCluster"])
    if not jointActive:
        cmds.warning("No active paint influence found.")
        return

    parentJoint = cmds.listRelatives(jointActive, parent=True, type="joint") or []
    if not parentJoint:
        cmds.warning("{} has no parent joint.".format(jointActive))
        return

    parentJoint = parentJoint[0]
    singleUnlock([jointActive, parentJoint])
    mel.eval("ArtPaintSkinWeightsTool;")
    mel.eval('setSmoothSkinInfluence "{}";'.format(parentJoint))

def UnlockTwoJoints(*arr):
    selection = cmds.ls(sl=True, fl=True) or []
    if not selection or ".vtx[" not in selection[0]:
        cmds.warning("Please select one vertex.")
        return

    vertex = selection[0]
    mesh = vertex.split(".")[0]
    skin = GetSkinCluster(mesh)
    if not skin:
        cmds.warning("No skinCluster found.")
        return

    weights = GetVertexWeights(skin, vertex)
    data = sorted(
        ((joint, weight) for joint, weight in weights.items() if weight > 0.0),
        key=lambda item: item[1],
        reverse=True
    )
    if len(data) < 2:
        cmds.warning("Vertex has fewer than two influences.")
        return

    jointA, jointB = data[0][0], data[1][0]
    skinSession.update(GetSkinData(mesh))
    singleUnlock([jointA, jointB])
    cmds.select(mesh, r=True)
    mel.eval("ArtPaintSkinWeightsTool;")
    mel.eval('setSmoothSkinInfluence "{}";'.format(jointB))
    return jointA, jointB


def addUnlockDown(*arr):
    session = EnsureSkinSession()
    if not session:
        return

    jointActive = GetActivePaintJoint(session["skinCluster"])
    if not jointActive:
        cmds.warning("No active paint influence found.")
        return

    children = cmds.listRelatives(jointActive, children=True, type="joint") or []
    if not children:
        cmds.warning("{} has no child joint.".format(jointActive))
        return

    childJoint = children[0]
    singleUnlock([jointActive, childJoint])
    mel.eval("ArtPaintSkinWeightsTool;")
    mel.eval('setSmoothSkinInfluence "{}";'.format(childJoint))

def ActiveJoint(mesh, joint, *arr):
    data = GetSkinData(mesh)
    skinCluster = data["skinCluster"]
    if not skinCluster:
        cmds.warning("No skinCluster found on {}.".format(mesh))
        return False
    if joint not in (data["joints"] or []):
        cmds.warning("{} is not an influence of {}.".format(joint, skinCluster))
        return False
    cmds.connectAttr(joint + ".message", skinCluster + ".paintTrans", f=True)
    skinSession.update(data)
    return True

def switchJoint(*arr):
    selection = cmds.ls(sl=True, fl=True) or []
    if not selection:
        cmds.warning("Select a skinned mesh or component.")
        return

    data = GetSkinData(selection[0])
    skinName = data["skinCluster"]
    if not skinName:
        cmds.warning("No skinCluster found.")
        return

    joints = data["joints"] or []
    unlocked = [joint for joint in joints if cmds.objExists(joint + ".liw") and not cmds.getAttr(joint + ".liw")]
    if not unlocked:
        cmds.warning("No unlocked influences found.")
        return

    jointActive = GetActivePaintJoint(skinName)
    index = (unlocked.index(jointActive) + 1) % len(unlocked) if jointActive in unlocked else 0
    mel.eval('setSmoothSkinInfluence "{}"; artSkinRevealSelected artAttrSkinPaintCtx;'.format(unlocked[index]))

def goToBindPose(*arr):
    mel.eval('GoToBindPose;')
    
def GetJointVertexs(mesh, joints, threshold=0.0001):
    dagPath, skinFn, skin = GetSkinApi(mesh)
    if skinFn is None:
        return []

    jointSet = set(joints or [])
    if not jointSet:
        return []

    influences = skinFn.influenceObjects()
    influenceIndices = []
    for i, influence in enumerate(influences):
        name = influence.partialPathName()
        full = influence.fullPathName()
        if name in jointSet or full in jointSet:
            influenceIndices.append(i)

    if not influenceIndices:
        return []

    meshFn = om.MFnMesh(dagPath)
    vertexIds = list(range(meshFn.numVertices))
    component = CreateVertexComponent(vertexIds)
    weights, influenceCount = skinFn.getWeights(dagPath, component)

    result = []
    for row, vertexId in enumerate(vertexIds):
        offset = row * influenceCount
        if any(weights[offset + influenceId] > threshold for influenceId in influenceIndices):
            result.append("{}.vtx[{}]".format(mesh, vertexId))
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




def ClearWeight(JointActive=None):
    verts = NLTA_Mesh.GetVertexsSelected() or []
    if not verts:
        return

    mesh = verts[0].split(".")[0]
    verts = [vert for vert in verts if vert.split(".")[0] == mesh]
    dagPath, skinFn, skin = GetSkinApi(mesh)
    if skinFn is None:
        cmds.warning("Haven't skinCluster")
        return

    jointActive = JointActive or GetActivePaintJoint(skin)
    if not jointActive:
        cmds.warning("No active paint influence found.")
        return

    influences = skinFn.influenceObjects()
    names = [influence.partialPathName() for influence in influences]
    fullNames = [influence.fullPathName() for influence in influences]
    sourceIndex = names.index(jointActive) if jointActive in names else (
        fullNames.index(jointActive) if jointActive in fullNames else -1
    )
    if sourceIndex < 0:
        cmds.warning("{} is not an influence of {}.".format(jointActive, skin))
        return

    vertexIds = [int(vert.rsplit("[", 1)[1].rstrip("]")) for vert in verts]
    component = CreateVertexComponent(vertexIds)
    weights, influenceCount = skinFn.getWeights(dagPath, component)
    newWeights = om.MDoubleArray(weights)
    changed = False

    for row in range(len(vertexIds)):
        offset = row * influenceCount
        sourceWeight = weights[offset + sourceIndex]
        if sourceWeight <= 0.0:
            continue

        dominantIndex = max(
            (i for i in range(influenceCount) if i != sourceIndex),
            key=lambda i: weights[offset + i],
            default=None
        )
        if dominantIndex is None:
            continue

        newWeights[offset + dominantIndex] += sourceWeight
        newWeights[offset + sourceIndex] = 0.0
        changed = True

    if changed:
        skinFn.setWeights(
            dagPath,
            component,
            om.MIntArray(range(influenceCount)),
            newWeights,
            False
        )
        cmds.skinCluster(skin, e=True, forceNormalizeWeights=True)

    return changed

def setMiddleWeight(*arr):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True, fl=True) or []
    joints = cmds.ls(selection, type="joint") or []
    vertices = [item for item in selection if ".vtx[" in item]

    if not joints or not vertices:
        cmds.warning("Select the middle joint, optional extra joints, and vertices.")
        return

    middleJoint = joints[0]
    jointArray = joints[1:]
    mesh = vertices[0].split(".")[0]
    vertices = [vertex for vertex in vertices if vertex.split(".")[0] == mesh]
    skinCluster = GetSkinCluster(mesh)
    if not skinCluster:
        cmds.warning("No skinCluster found on {}.".format(mesh))
        return

    skinJoints = cmds.skinCluster(skinCluster, q=True, inf=True) or []
    lockState = {joint: cmds.getAttr(joint + ".liw") for joint in skinJoints if cmds.objExists(joint + ".liw")}

    try:
        for joint in skinJoints:
            if cmds.objExists(joint + ".liw"):
                cmds.setAttr(joint + ".liw", 0)

        averageWeight = 1.0 / float(len(jointArray) + 1)
        values = [(middleJoint, averageWeight)] + [(joint, averageWeight) for joint in jointArray]
        for vertex in vertices:
            cmds.skinPercent(skinCluster, vertex, transformValue=values, normalize=True)
    finally:
        for joint, state in lockState.items():
            if cmds.objExists(joint + ".liw"):
                cmds.setAttr(joint + ".liw", state)

    cmds.select(jointArray or [middleJoint], r=True)
    component()
    cmds.select(vertices, r=True)

def mirrorSkin(axis, neg_pos, *arr):
    selection = cmds.ls(sl=True, fl=True) or []
    if not selection:
        cmds.warning("Select a skinned mesh or vertices.")
        return

    first = selection[0]
    mesh = first.split(".")[0]
    skin = GetSkinCluster(mesh)
    if not skin:
        cmds.warning("No skinCluster found on {}.".format(mesh))
        return

    planes = {"x": "YZ", "y": "XZ", "z": "XY"}
    face = planes.get(axis.lower())
    if face is None:
        cmds.warning("Axis must be x, y, or z.")
        return

    component = " -selectedComponents;" if ".vtx[" in first else ";"
    inverse = " -mirrorInverse" if neg_pos == "-" else ""
    command = (
        'copySkinWeights -ss "{0}" -ds "{0}" -mirrorMode {1}{2} '
        '-surfaceAssociation closestPoint -influenceAssociation closestJoint '
        '-influenceAssociation oneToOne{3}'
    ).format(skin, face, inverse, component)
    mel.eval(command)

def ExportAllSkinUrl(folder, *arr):
    jsonData = {}
    jsonPath = os.path.join(folder, "skinData.json")
    selection = cmds.ls(sl=True) or []

    if selection:
        meshTransforms = list(dict.fromkeys(item.split(".")[0] for item in selection))
    else:
        meshTransforms = cmds.listRelatives(cmds.ls(type="mesh", ap=True), parent=True, pa=True) or []
        meshTransforms = list(dict.fromkeys(meshTransforms))

    version = cmds.about(version=True)
    for transform in meshTransforms:
        skin = GetSkinCluster(transform)
        if not skin:
            continue

        transformName = transform.replace("|", "&").replace(":", "%")
        jsonData[transformName] = {"skinName": skin}

        if version == "2018":
            mel.eval('deformerWeights -export -deformer "{}" -path "{}" "{}.xml";'.format(skin, folder, transformName))
        else:
            mel.eval('deformerWeights -export -deformer "{}" -format "XML" -path "{}" "{}.xml";'.format(skin, folder, transformName))

    NLTA_General.writeJsonFile(jsonPath, jsonData)
    return jsonData

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

def ExportFolderSkinSingle(url, *arr):
    if not url:
        return False

    meshes = cmds.ls(sl=True, long=True) or []
    if not meshes:
        cmds.warning("Select one or more meshes.")
        return False

    if not os.path.isdir(url):
        os.makedirs(url)

    data = {}
    originalSelection = cmds.ls(sl=True, long=True) or []

    try:
        for mesh in meshes:
            uuid = (cmds.ls(mesh, uuid=True) or [None])[0]
            if not uuid:
                continue

            parent = cmds.listRelatives(mesh, parent=True, fullPath=True) or []
            shortName = mesh.split("|")[-1]
            tempName = shortName if "NLTA_" in shortName else "NLTA_" + shortName

            data[uuid] = {
                "originalName": shortName,
                "parent": parent[0] if parent else None,
                "tempName": tempName
            }

            if parent:
                mesh = cmds.parent(mesh, world=True)[0]
            if mesh.split("|")[-1] != tempName:
                cmds.rename(mesh, tempName)

        cmds.select(clear=True)
        for uuid in data:
            nodes = cmds.ls(uuid) or []
            if nodes:
                cmds.select(nodes[0], add=True)

        if not cmds.ls(sl=True):
            cmds.warning("No valid meshes to export.")
            return False

        cmds.file(
            os.path.join(url, "mesh.obj"),
            force=True,
            options="groups=1;ptgroups=0;materials=0;smoothing=0;normals=1",
            type="OBJexport",
            exportSelected=True
        )
        ExportAllSkinUrl(url)
        return True

    finally:
        for uuid, item in data.items():
            nodes = cmds.ls(uuid, long=True) or []
            if not nodes:
                continue
            node = nodes[0]
            if node.split("|")[-1] != item["originalName"]:
                node = cmds.rename(node, item["originalName"])
            if item["parent"] and cmds.objExists(item["parent"]):
                try:
                    cmds.parent(node, item["parent"])
                except RuntimeError:
                    pass

        existing = [node for node in originalSelection if cmds.objExists(node)]
        if existing:
            cmds.select(existing, r=True)

def ExportFolderSkin(*arr):
    result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="Select Folder") or []
    if result:
        ExportFolderSkinSingle(result[0])

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
                        if jsonData and transformName in jsonData:
                            cmds.rename(skin_name, jsonData[transformName]["skinName"])
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

def ImportFolderSkinSingle(url, *arr):
    if not url or not os.path.isdir(url):
        cmds.warning("Import folder not found.")
        return False

    files = NLTA_General.GetFiles(url, "obj") or []
    for file_ in files:
        filePath = os.path.join(url, file_ + ".obj")
        cmds.file(
            filePath,
            i=True,
            type="OBJ",
            ignoreVersion=True,
            ra=True,
            mergeNamespacesOnClash=False,
            namespace=":",
            options="mo=1",
            pr=True
        )

    ImportAllSkinUrl(url, False)
    cmds.warning("Done!!!")
    return True

def ImportFolderSkin(*arr):
    result = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="Select Folder") or []
    if result:
        ImportFolderSkinSingle(result[0])

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


def fixMaxInfluence(*arr):
    maxInfluence = cmds.intField("maxInfluent", q=True, value=True)

    if maxInfluence < 1:
        cmds.warning("maxInfluence must be at least 1.")
        return

    meshes = cmds.ls(sl=True, dag=True, type="mesh", noIntermediate=True) or []
    if not meshes:
        meshes = cmds.ls(type="mesh", noIntermediate=True) or []

    for shape in meshes:
        mesh = (cmds.listRelatives(shape, parent=True, fullPath=True) or [shape])[0]

        dagPath, skinFn, skin = GetSkinApi(mesh)
        if skinFn is None:
            continue

        vertexCount = om.MFnMesh(dagPath).numVertices
        component = CreateVertexComponent(range(vertexCount))
        weights, influenceCount = skinFn.getWeights(dagPath, component)
        newWeights = list(weights)

        for i in range(vertexCount):
            start = i * influenceCount
            end = start + influenceCount
            vertexWeights = list(weights[start:end])

            active = [(j, w) for j, w in enumerate(vertexWeights) if w > 0.0]
            if len(active) <= maxInfluence:
                continue

            active.sort(key=lambda item: item[1], reverse=True)
            keep = {index for index, _ in active[:maxInfluence]}

            for j in range(influenceCount):
                if j not in keep:
                    vertexWeights[j] = 0.0

            total = sum(vertexWeights)
            if total > 0.0:
                vertexWeights = [w / total for w in vertexWeights]

            newWeights[start:end] = vertexWeights

        skinFn.setWeights(
            dagPath,
            component,
            om.MIntArray(range(influenceCount)),
            om.MDoubleArray(newWeights),
            True
        )

    cmds.warning("Done!!!")


def fixMaxInfluenceAll(maxValue,*arr):
    cmds.select(clear=True)
    for a in cmds.ls(type="mesh"):
        if a.endswith("Orig")!=True:
            for b in cmds.listHistory(a) or []:
                if cmds.objExists(b) and cmds.objectType(b) == "skinCluster":
                    cmds.select(cmds.listRelatives(a,parent=True)[0],add=True)
    fixMaxInfluence(maxValue)
    cmds.warning("Done!!!")

def checkMaxInfluentNumber(val, *arr):
    return checkMaxInfluenceNumber(val)


def checkMaxInfluenceNumber(maxValue, *args):
    selection = cmds.ls(sl=True, fl=True) or []
    if not selection:
        cmds.warning("No object selected")
        return []

    mesh = selection[0].split(".")[0]
    dagPath, skinFn, skin = GetSkinApi(mesh)
    if skinFn is None:
        cmds.warning("No skinCluster found")
        return []

    vertexCount = om.MFnMesh(dagPath).numVertices
    component = CreateVertexComponent(list(range(vertexCount)))
    weights, influenceCount = skinFn.getWeights(dagPath, component)

    result = []
    for vertexIndex in range(vertexCount):
        offset = vertexIndex * influenceCount
        count = sum(1 for i in range(influenceCount) if weights[offset + i] > 0.0001)
        if count > maxValue:
            result.append("{}.vtx[{}]".format(mesh, vertexIndex))

    if cmds.objExists("vertexOverMaxInfluence"):
        cmds.delete("vertexOverMaxInfluence")

    if result:
        cmds.select(result, r=True)
        cmds.sets(result, name="vertexOverMaxInfluence")
    else:
        cmds.select(clear=True)

    cmds.warning("Done!!!")
    return result


def checkMaxInfluent(*arr):
    if not cmds.ls(sl=True):
        cmds.warning("No object selected")
        return []
    maxValue = cmds.intField("maxInfluent", q=True, value=True)
    return checkMaxInfluenceNumber(maxValue)


def TransferTopWeight(vertex=None):
    if not vertex:
        selection = cmds.ls(sl=True, fl=True) or []
        if not selection:
            cmds.warning("Select one vertex.")
            return False
        vertex = selection[0]

    if ".vtx[" not in vertex:
        cmds.warning("Select one vertex.")
        return False

    amount = cmds.artAttrSkinPaintCtx("artAttrSkinContext", q=True, value=True)
    mesh = vertex.split(".")[0]
    skin = GetSkinCluster(mesh)
    if not skin:
        raise RuntimeError("No skinCluster found.")

    influences = cmds.skinCluster(skin, q=True, influence=True) or []
    weights = cmds.skinPercent(skin, vertex, q=True, value=True) or []
    data = sorted(zip(influences, weights), key=lambda item: item[1], reverse=True)

    if len(data) < 2:
        cmds.warning("Vertex has fewer than two influences.")
        return False

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
            transformValue=[(jointA, newWeightA), (jointB, newWeightB)],
            normalize=False
        )
    finally:
        cmds.setAttr(skin + ".normalizeWeights", normalize)

    return jointA, jointB, newWeightA, newWeightB
        


def clearSkin(*arr):
    transforms = cmds.listRelatives(cmds.ls(type="mesh", noIntermediate=True), parent=True, fullPath=True) or []
    transforms = list(dict.fromkeys(transforms))

    count = 0
    for transform in transforms:
        if GetSkinCluster(transform):
            cmds.delete(transform, constructionHistory=True)
            count += 1

    cmds.warning("Done!!! Cleared skin history on {} mesh(es).".format(count))
    return count

def removeUnneedJoint(*arr):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True, long=True) or []
    if selection:
        transforms = list(dict.fromkeys(item.split(".")[0] for item in selection))
    else:
        transforms = cmds.listRelatives(cmds.ls(type="mesh", noIntermediate=True), parent=True, fullPath=True) or []
        transforms = list(dict.fromkeys(transforms))

    removed = {}
    for transform in transforms:
        dagPath, skinFn, skin = GetSkinApi(transform)
        if skinFn is None:
            continue

        influences = skinFn.influenceObjects()
        if len(influences) <= 1:
            continue

        vertexCount = om.MFnMesh(dagPath).numVertices
        component = CreateVertexComponent(list(range(vertexCount)))
        weights, influenceCount = skinFn.getWeights(dagPath, component)

        used = [False] * influenceCount
        for vertexIndex in range(vertexCount):
            offset = vertexIndex * influenceCount
            for influenceIndex in range(influenceCount):
                if not used[influenceIndex] and weights[offset + influenceIndex] > 0.0:
                    used[influenceIndex] = True

        removeJoints = [
            influences[i].partialPathName()
            for i, isUsed in enumerate(used)
            if not isUsed
        ]

        # Keep at least one influence.
        if len(removeJoints) >= len(influences):
            removeJoints = removeJoints[:-1]

        for joint in removeJoints:
            if cmds.objExists(joint):
                cmds.skinCluster(skin, e=True, removeInfluence=joint)

        if removeJoints:
            removed[transform] = removeJoints
            print("Remove Joint " + " - ".join(removeJoints))

    if transforms:
        existing = [transform for transform in transforms if cmds.objExists(transform)]
        if existing:
            cmds.select(existing, r=True)

    cmds.warning("Done!!!")
    return removed

def AddMeshJoint(*arr):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True, long=True) or []
    if len(selection) < 2:
        cmds.warning("Select source mesh then destination mesh(es).")
        return

    source = selection[0]
    destinations = selection[1:]
    sourceSkin = GetSkinCluster(source)
    if not sourceSkin:
        cmds.warning("Source has no skinCluster.")
        return

    sourceJoints = set(cmds.skinCluster(sourceSkin, q=True, inf=True) or [])
    for destination in destinations:
        destinationSkin = GetSkinCluster(destination)
        if not destinationSkin:
            continue

        destinationJoints = set(cmds.skinCluster(destinationSkin, q=True, inf=True) or [])
        jointsAdd = sorted(sourceJoints - destinationJoints)
        if jointsAdd:
            cmds.skinCluster(destinationSkin, e=True, addInfluence=jointsAdd, weight=0)
            print("Add Joint " + " - ".join(jointsAdd))

    cmds.warning("Done!!!")

def AddJoint(*arr):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True, long=True) or []
    if len(selection) < 2:
        cmds.warning("Select joint(s) and mesh(es).")
        return

    joints = cmds.ls(selection, type="joint", long=True) or []
    if not joints:
        cmds.warning("No joints selected.")
        return

    meshes = []
    for item in selection:
        if item in joints:
            continue
        shape = (cmds.listRelatives(item, shapes=True, noIntermediate=True, type="mesh", fullPath=True) or [])
        if shape:
            meshes.append(item)

    for mesh in list(dict.fromkeys(meshes)):
        skin = GetSkinCluster(mesh)
        if not skin:
            continue
        existing = set(cmds.skinCluster(skin, q=True, inf=True) or [])
        jointsAdd = [joint for joint in joints if joint not in existing and joint.split("|")[-1] not in existing]
        if jointsAdd:
            cmds.skinCluster(skin, e=True, addInfluence=jointsAdd, weight=0)
            print("Add Joint " + " - ".join(jointsAdd))

    cmds.warning("Done!!!")

def RemoveJoint(*args):
    cmds.currentTime(0)
    selection = cmds.ls(sl=True, long=True) or []
    if len(selection) < 2:
        cmds.warning("Select one or more joints and one or more meshes.")
        return

    joints = cmds.ls(selection, type="joint", long=True) or []
    if not joints:
        cmds.warning("No joints selected.")
        return

    meshes = []
    for item in selection:
        if item in joints:
            continue
        if cmds.listRelatives(item, shapes=True, noIntermediate=True, type="mesh"):
            meshes.append(item)

    for mesh in list(dict.fromkeys(meshes)):
        skin = GetSkinCluster(mesh)
        if not skin:
            continue

        for joint in joints:
            influences = cmds.skinCluster(skin, q=True, inf=True) or []
            shortJoint = joint.split("|")[-1]
            sourceName = joint if joint in influences else (shortJoint if shortJoint in influences else None)
            if sourceName is None:
                continue
            if len(influences) <= 1:
                cmds.warning("{} only has one influence.".format(mesh))
                break

            parent = cmds.listRelatives(joint, parent=True, type="joint", fullPath=True) or []
            if not parent:
                cmds.warning("{} has no parent. Skip.".format(joint))
                continue

            parent = parent[0]
            parentShort = parent.split("|")[-1]
            if parent not in influences and parentShort not in influences:
                cmds.skinCluster(skin, e=True, addInfluence=parent, lockWeights=False, weight=0)

            dagPath, skinFn, _ = GetSkinApi(mesh, skin)
            influencesApi = skinFn.influenceObjects()
            names = [item.partialPathName() for item in influencesApi]
            fullNames = [item.fullPathName() for item in influencesApi]

            sourceIndex = names.index(shortJoint) if shortJoint in names else (
                fullNames.index(joint) if joint in fullNames else -1
            )
            parentIndex = names.index(parentShort) if parentShort in names else (
                fullNames.index(parent) if parent in fullNames else -1
            )
            if sourceIndex < 0 or parentIndex < 0:
                continue

            vertexCount = om.MFnMesh(dagPath).numVertices
            component = CreateVertexComponent(list(range(vertexCount)))
            weights, influenceCount = skinFn.getWeights(dagPath, component)
            newWeights = om.MDoubleArray(weights)

            for vertexIndex in range(vertexCount):
                offset = vertexIndex * influenceCount
                sourceWeight = newWeights[offset + sourceIndex]
                if sourceWeight > 0.0:
                    newWeights[offset + parentIndex] += sourceWeight
                    newWeights[offset + sourceIndex] = 0.0

            skinFn.setWeights(
                dagPath,
                component,
                om.MIntArray(range(influenceCount)),
                newWeights,
                False
            )
            cmds.skinCluster(skin, e=True, removeInfluence=sourceName)

    cmds.select(clear=True)
    cmds.warning("Done!")
def ExportSkinFbx(*arr):
    objects = cmds.ls(sl=True, long=True) or []
    if not objects:
        cmds.warning("Nothing is selected.")
        return None

    scenePath = cmds.file(q=True, sn=True)
    if not scenePath:
        cmds.warning("Please save the scene first.")
        return None

    originalSelection = cmds.ls(sl=True, long=True) or []
    disconnected = []
    attrStates = {}
    layerStates = {}

    def ForceVisible(node):
        attr = node + ".visibility"
        if not cmds.objExists(attr):
            return
        if attr not in attrStates:
            attrStates[attr] = cmds.getAttr(attr)
        sources = cmds.listConnections(attr, source=True, destination=False, plugs=True) or []
        for source in sources:
            disconnected.append((source, attr))
            cmds.disconnectAttr(source, attr)
        if not cmds.getAttr(attr, lock=True):
            cmds.setAttr(attr, 1)

    try:
        for obj in objects:
            shapes = cmds.listRelatives(obj, ad=True, type="mesh", fullPath=True) or []
            transforms = set()
            for shape in shapes:
                ForceVisible(shape)
                parent = cmds.listRelatives(shape, parent=True, fullPath=True) or []
                if parent:
                    transforms.add(parent[0])
            for transform in transforms:
                ForceVisible(transform)

        for layer in cmds.ls(type="displayLayer") or []:
            if layer == "defaultLayer":
                continue
            layerStates[layer] = (
                cmds.getAttr(layer + ".visibility"),
                cmds.getAttr(layer + ".displayType")
            )
            cmds.setAttr(layer + ".visibility", 1)
            cmds.setAttr(layer + ".displayType", 0)

        sceneDir = os.path.dirname(scenePath)
        sceneName = os.path.splitext(os.path.basename(scenePath))[0]
        exportPath = os.path.join(sceneDir, sceneName + "_SkinFbx.fbx").replace("\\", "/")

        if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
            cmds.loadPlugin("fbxmaya", quiet=True)

        mel.eval("FBXExportShapes -v false")
        mel.eval("FBXExportInputConnections -v false")
        mel.eval("FBXExportEmbeddedTextures -v false")
        mel.eval("FBXExportSkins -v true")
        mel.eval("FBXExportSmoothMesh -v true")
        mel.eval("FBXExportSmoothingGroups -v true")
        mel.eval("FBXExportConstraints -v false")
        mel.eval('FBXExport -f "{}" -s'.format(exportPath))
        return exportPath

    finally:
        for layer, (visibility, displayType) in layerStates.items():
            if cmds.objExists(layer):
                cmds.setAttr(layer + ".visibility", visibility)
                cmds.setAttr(layer + ".displayType", displayType)

        for attr, value in attrStates.items():
            if cmds.objExists(attr) and not cmds.getAttr(attr, lock=True):
                try:
                    cmds.setAttr(attr, value)
                except RuntimeError:
                    pass

        for source, destination in disconnected:
            if cmds.objExists(source) and cmds.objExists(destination):
                if not cmds.isConnected(source, destination):
                    try:
                        cmds.connectAttr(source, destination, force=True)
                    except RuntimeError:
                        pass

        existing = [node for node in originalSelection if cmds.objExists(node)]
        if existing:
            cmds.select(existing, r=True)

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

