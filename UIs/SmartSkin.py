import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import pymel.core as pm

import importlib
import math
import json
from functools import partial

import NLTA_General
importlib.reload(NLTA_General)


loftAttr = 'NLTA_LoftData'

UIs = {}

def CreateUI(data):
    global UIs
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data)
  
    titles, buttons, inputs = [], [], []
    parent = data['parent']
    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)#*
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    titles.append(cmds.textField(text=data['title'],editable=False))

    cmds.rowColumnLayout(numberOfColumns=1)#+
    #titles.append(cmds.textField(text='Curve tools',editable=False))
    cmds.rowColumnLayout(numberOfColumns=1)#---

    cmds.rowColumnLayout(numberOfColumns=1)
    UIs["ratioCurve"] = cmds.gradientControlNoAttr("myGradient",width=350,height=120,enable=True,asString="0,0,2,1,1,2",
        changeCommand=lambda *args: print(
            cmds.gradientControlNoAttr("myGradient", q=True, asString=True)
        )
    )
    #buttons.append(cmds.button(label="Skin Skirt",c=partial(AutoSkin,"skirt")))
    buttons.append(cmds.button(label="Test",c=Test))
    cmds.setParent("..")

    cmds.setParent("..")#---

    cmds.setParent("..")#-
    cmds.setParent("..")#*

    for title in titles:
        cmds.textField(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)

def GetGradientValue(ctrl, x):
    s = cmds.gradientControlNoAttr(ctrl, q=True, asString=True)
    data = list(map(float, s.split(",")))
    points = []
    for i in range(0, len(data), 3):
        pos = data[i]
        val = data[i+1]
        interp = int(data[i+2])
        points.append((pos, val, interp))
    points.sort(key=lambda p: p[0])
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for i in range(len(points)-1):
        p0, v0, interp = points[i]
        p1, v1, _ = points[i+1]
        if p0 <= x <= p1:
            t = (x - p0) / (p1 - p0)
            if interp == 0:  # none
                return v0
            elif interp == 1:  # linear
                return v0 + (v1 - v0) * t
            elif interp == 2:  # smooth
                t = t * t * (3 - 2 * t)
                return v0 + (v1 - v0) * t

def GetDagPath(node):
    sel = om.MSelectionList()
    sel.add(node)
    return sel.getDagPath(0)

def EdgeDirection(mesh, edgeIndex):
    mesh_path = GetDagPath(mesh)
    edge_it = om.MItMeshEdge(mesh_path)
    edge_it.setIndex(edgeIndex)
    p1 = edge_it.point(0, om.MSpace.kWorld)
    p2 = edge_it.point(1, om.MSpace.kWorld)
    v = om.MVector(p2 - p1)
    return v.normal()

def CheckEdgeBorder(mesh, edgeId):
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    it = om.MItMeshEdge(dag)
    it.setIndex(edgeId)
    return(it.onBoundary())

def JointPos(j):
    return om.MVector(cmds.xform(j, q=True, ws=True, t=True))

def GetID(component):
    if isinstance(component, (int, float)):
        return(component)
    else:
        return(
            int(component.split("[")[-1].replace("]", ""))
        )

def GetJointAxis(joint):
    m = cmds.xform(joint, q=True, ws=True, m=True)
    axis = om.MVector(m[0], m[1], m[2])
    return axis.normal()

def GetClosestVertex(mesh, joint):
    mesh_path = GetDagPath(mesh)
    mesh_fn = om.MFnMesh(mesh_path)
    JointPos = cmds.xform(joint, q=True, ws=True, t=True)
    point = om.MPoint(JointPos)
    closest_point, face_id = mesh_fn.getClosestPoint(point, om.MSpace.kWorld)
    vertices = mesh_fn.getPoints(om.MSpace.kWorld)
    min_dist = float("inf")
    closest_index = -1
    for i, v in enumerate(vertices):
        dist = (v - closest_point).length()
        if dist < min_dist:
            min_dist = dist
            closest_index = i
    return closest_index

def GetEdgeLoop(mesh, start_edge):
    returnData = []
    edges = cmds.polySelect(mesh, edgeLoop=GetID(start_edge), noSelection=True)
    for edge in edges:
        returnData.append(f"{mesh}.e[{edge}]")
    return(returnData)

def GetEdgeRing(mesh, start_edge):
    returnData = []
    edges = cmds.polySelect(mesh, edgeRing=GetID(start_edge), noSelection=True)
    for edge in edges:
        returnData.append(f"{mesh}.e[{edge}]")
    return(returnData)

def VertexFromEdges(mesh, edges):
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    it = om.MItMeshEdge(dag)
    verts = set()
    for edge in edges:
        eid = GetID(edge)
        it.setIndex(eid)

        v1 = it.vertexId(0)
        v2 = it.vertexId(1)

        verts.add(v1)
        verts.add(v2)
    return [f"{mesh}.vtx[{v}]" for v in verts]

def GetConnectedEdges(mesh,vertex_index):
    mesh_path = GetDagPath(mesh)
    vert_it = om.MItMeshVertex(mesh_path)
    vert_it.setIndex(vertex_index)
    return vert_it.getConnectedEdges()

def GetBestEdge(mesh, joint, vertex_index):
    joint_axis = GetJointAxis(joint)
    edges = GetConnectedEdges(mesh, vertex_index)
    best_edge = None
    best_dot = -1
    for e in edges:
        dir_vec = EdgeDirection(mesh, e)
        dot = abs(dir_vec * joint_axis)
        if dot > best_dot:
            best_dot = dot
            best_edge = e
    return best_edge

def GetBestEdgeLoop(mesh, joint,vtxIndex):
    best_edge = GetBestEdge(mesh, joint, vtxIndex)
    if best_edge is None:
        cmds.warning("No edge found")
        return
    return(GetEdgeLoop(mesh, best_edge))

def GetPerpendicularEdge(mesh, joint, vertex_index):
    joint_axis = GetJointAxis(joint)
    edges = GetConnectedEdges(mesh, vertex_index)
    best_edge = None
    best_dot = 999
    for e in edges:
        dir_vec = EdgeDirection(mesh, e)
        dot = abs(dir_vec * joint_axis)
        if dot < best_dot:
            best_dot = dot
            best_edge = e
    return best_edge

def GetPerpendicularEdgeLoop(mesh, joint,vtxIndex):
    best_edge = GetPerpendicularEdge(mesh, joint, vtxIndex)
    if best_edge is None:
        cmds.warning("No edge found")
        return
    return(GetEdgeLoop(mesh, best_edge))

def GetDistance(source,target):
    sourcePos = om.MVector(cmds.xform(source, q=True, ws=True, t=True))
    pos = om.MVector(cmds.xform(target, q=True, ws=True, t=True))
    dist = (pos - sourcePos).length()
    return(dist)

def GetTwoClosestJoints(targetJoint, joints):
    distances = []
    for j in joints:
        if j == targetJoint:
            continue
        dist = GetDistance(targetJoint,j)
        distances.append((j, dist))
    distances.sort(key=lambda x: x[1])
    return distances[:2]

def SelectVerticesWithinRadius(mesh,joint,verts,radius):
    p0 = JointPos(joint)
    result = []
    for v in verts:
        pos = om.MVector(cmds.pointPosition(v, w=True))
        d = (pos - p0).length()
        if d <= radius:
            result.append(v)
    return(result)
    
def SelectLoopRegion(mesh, joint,joints,verts):
    closest = GetTwoClosestJoints(joint, joints)
    d1 = closest[0][1]
    d2 = closest[1][1]
    radius = min(d1, d2) * 0.7
    verts = SelectVerticesWithinRadius(mesh, joint,verts,radius)
    return(verts)

def GetSkinData(mesh):
    skinCluster = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
    if skinCluster:
        return({
            "mesh":mesh,
            "skinCluster":skinCluster[0],
            "joints":cmds.skinCluster(skinCluster, query=True, influence=True)
        })

def LockJoint(mesh,jnts):
    skinJnts = GetSkinData(mesh)["joints"]
    for jnt in skinJnts:
        if jnt in jnts:
            cmds.setAttr(jnt+".liw",0)
        else:
            cmds.setAttr(jnt+".liw",1)

def EdgesBetween(mesh, edgeSource,edgeTarget):
    id1 = GetID(edgeSource)
    id2 = GetID(edgeTarget)
    edges = cmds.polySelect(mesh, edgeRingPath=(id1, id2),noSelection=True)
    if edges:
        return [f"{mesh}.e[{i}]" for i in edges]
    return []

def CheckEdgesBetween(mesh, edgeSource, edges):
    id1 = GetID(edgeSource)
    for edge in edges:        
        id2 = GetID(edge)
        edges = cmds.polySelect(mesh, edgeRingPath=(id1, id2),noSelection=True)
        if edges:
            return(edge)
    return []

def EdgeCenter(mesh, edgeId):
    edgeId = GetID(edgeId)
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    it = om.MItMeshEdge(dag)
    it.setIndex(edgeId)
    p1 = om.MVector(it.point(0, om.MSpace.kWorld))
    p2 = om.MVector(it.point(1, om.MSpace.kWorld))
    return (p1 + p2) * 0.5

def EdgeRatioBetweenJoints(mesh, edgeId, jointA, jointB):
    pA = JointPos(jointA)
    pB = JointPos(jointB)
    edgeC = EdgeCenter(mesh, edgeId)
    boneVec = pB - pA
    edgeVec = edgeC - pA
    t = (edgeVec * boneVec) / boneVec.length()**2
    return max(0, min(1, t))

def EdgeRatioBetweenEdges(mesh, edgeMid, edgeA, edgeB):
    pA = EdgeCenter(mesh, edgeA)
    pB = EdgeCenter(mesh, edgeB)
    pC = EdgeCenter(mesh, edgeMid)
    vecAB = pB - pA
    vecAC = pC - pA
    t = (vecAC * vecAB) / vecAB.length()**2
    return max(0, min(1, t))

def GetFarthestEdge(mesh, baseEdge, edges):
    baseId = GetID(baseEdge)
    baseCenter = EdgeCenter(mesh, baseId)
    maxDist = -1
    farEdge = None
    for edge in edges:
        eid = GetID(edge)
        center = EdgeCenter(mesh, eid)
        dist = (center - baseCenter).length()
        if dist > maxDist:
            maxDist = dist
            farEdge = edge
    return farEdge

def GetClosestEdge(mesh, edges, joint):
    jointPos = om.MVector(cmds.xform(joint, q=True, ws=True, t=True))
    minDist = 1e10
    closestEdge = None
    for edge in edges:
        edgeId = GetID(edge)
        center = EdgeCenter(mesh, edgeId)
        dist = (center - jointPos).length()
        if dist < minDist:
            minDist = dist
            closestEdge = edge
    return closestEdge

def SmoothRatio(t):
    return(t*t*t*(t*(t*6 - 15) + 10))

def AutoSkin(type,*arr):
    selection =cmds.ls(selection=True)
    """
    selection = [
        "CMBone_Pelvis",
        "Bone_BR_SkirtT_01",
        "Bone_R_SkirtT_01",
        "Bone_FR_SkirtT_01",
        "Bone_B_SkirtT_01",
        "Bone_BL_SkirtT_01",
        "Bone_L_SkirtT_01",
        "Bone_FL_SkirtT_01",
        "Bone_F_SkirtT_01",
        "nurbsToPoly1",
    ]
    """
    root = selection[0]
    mesh = selection[-1]
    jnts = selection[1:-1]
    standardJnt = selection[1]
    skinData = GetSkinData(mesh)

    data = {
        "edgeLoop":{},
        "edgeOrigin":{},
        "edgePerpendicularOrigin":{},
        "edgePerpendicularEnd":{},
        "edgePerpendicularChildren":{},
        "edgePerpendicularChildrenOrder":{},
    }

    # GET EDGE LOOP
    for jnt in jnts:
        closestVert = GetClosestVertex(mesh,jnt)
        if jnt == standardJnt:
            edgeOriginIndex = GetBestEdge(mesh,jnt,closestVert)
            edgeStandard = f"{mesh}.e[{edgeOriginIndex}]"
            data["edgeOrigin"][jnt] = edgeStandard
        data["edgeLoop"][jnt] = GetBestEdgeLoop(mesh,jnt,closestVert)        

    # GET EDGE ORIGIN
    for jnt in jnts:
        if jnt != standardJnt:
            edge = CheckEdgesBetween(mesh,edgeStandard,data["edgeLoop"][jnt])
            if edge:
                data["edgeOrigin"][jnt] = edge


    # GET PERPENDICULAR DATA
    for jnt in jnts:
        closestVert = GetClosestVertex(mesh,jnt)              
        edgeIndex = GetPerpendicularEdge(mesh,jnt,closestVert)
        edgeName = f"{mesh}.e[{edgeIndex}]"

        ############
        edges =  GetEdgeRing(mesh,edgeName)
        farthestEdge = GetFarthestEdge(mesh,edgeName,edges)
        data["edgePerpendicularOrigin"][jnt] = edgeName
        data["edgePerpendicularEnd"][jnt] = farthestEdge

        data["edgePerpendicularChildren"][jnt] = {}
        data["edgePerpendicularChildren"][jnt][jnt] = edgeName
        data["edgePerpendicularChildrenOrder"][jnt] = []
        children = cmds.listRelatives(jnt,ad=True)[::-1]
        for child in children:
            closestEdge = GetClosestEdge(mesh,edges,child)
            if closestEdge != farthestEdge:
                data["edgePerpendicularChildrenOrder"][jnt].append(child)
                data["edgePerpendicularChildren"][jnt][child] = closestEdge

    
    
    # DEVIDE SKIN FOR PARENT
    for jnt in jnts:
        closestVert = GetClosestVertex(mesh,jnt)
        edges = GetPerpendicularEdgeLoop(mesh,jnt,closestVert)        
        verts = VertexFromEdges(mesh,edges)
        verts = SelectLoopRegion(mesh,jnt,jnts,verts)
        edgesLoop = []
        for vert in verts:
            vertID = GetID(vert)            
            edgesLoop.extend(GetBestEdgeLoop(mesh,jnt,vertID))

        verts = VertexFromEdges(mesh,edgesLoop)        
        LockJoint(mesh,[root,jnt])
        for vert in verts:
            cmds.skinPercent(
                skinData["skinCluster"],
                vert,
                transformValue=[
                    (root,0)
                ]
            )           

    # SMOOTH PARRENT
    doneJoint = []
    for jnt in jnts:
        twoJoint = GetTwoClosestJoints(jnt,jnts)
        jnt1 = twoJoint[0][0]
        jnt2 = twoJoint[1][0]
        for jntTarget in [jnt1,jnt2]:
            
            between = EdgesBetween(mesh,data["edgeOrigin"][jnt],data["edgeOrigin"][jntTarget])
            for edge in between:
                loop = GetEdgeLoop(mesh,edge)
                verts = VertexFromEdges(mesh,loop)
                ratio = EdgeRatioBetweenJoints(mesh,GetID(edge),jntTarget,jnt)
                ratio = SmoothRatio(ratio)
                for vert in verts:
                    jntWeight = cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transform=jnt,
                        query=True
                    )
                    jntTargetWeight = cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transform = jntTarget,
                        query=True
                    )
                    totalWeight =  jntWeight + jntTargetWeight
                    jntWeightValue = totalWeight * ratio
                    jntTargetWeightValue = totalWeight * (1 - ratio)
                    LockJoint(mesh,[jnt,jntTarget])
                    cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transformValue=[
                            (jnt,jntWeightValue),
                            (jntTarget,jntTargetWeightValue)
                        ]
                    )


def GetDistance(objA, objB):
    posA = om.MFnTransform(GetDagPath(objA)).translation(om.MSpace.kWorld)
    posB = om.MFnTransform(GetDagPath(objB)).translation(om.MSpace.kWorld)
    return (posA - posB).length()

def GetVerticesInRadius(mesh, joint, radius):
    dagPath = GetDagPath(mesh)
    meshFn = om.MFnMesh(dagPath)
    jointPos = cmds.xform(joint, q=True, ws=True, t=True)
    jointPos = om.MVector(jointPos)
    points = meshFn.getPoints(om.MSpace.kWorld)
    result = []
    for i, p in enumerate(points):
        dist = (om.MVector(p) - jointPos).length()
        if dist <= radius:
            result.append(f"{mesh}.vtx[{i}]")
    return result

def Test(*arr):    
    distance = GetDistance("joint1", "joint2")
    vertsA = set(GetVerticesInRadius("pCylinder1", "joint2", distance))
    vertsB = set(GetVerticesInRadius("pCylinder1", "joint3", distance))
    middleVerts = list(vertsA.intersection(vertsB))
    cmds.select(middleVerts)