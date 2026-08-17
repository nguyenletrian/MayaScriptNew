import importlib
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma


import NLTA_General,NLTA_Graph,NLTA_Mesh,NLTA_Skinning
for module in [NLTA_General,NLTA_Graph,NLTA_Mesh,NLTA_Skinning]:
    try:
        importlib.reload(module)
    except:
        reload(module)

def UpdateView(*arr):
    mesh = NLTA_Mesh.GetMesh()
    skinData = NLTA_General.GetSkinData(mesh[0])
    if skinData["skinCluster"]:
        cmds.skinCluster(skinData["skinCluster"], e=True, forceNormalizeWeights=True)
        cmds.dgdirty(mesh)
        cmds.refresh()

def GradientActiveJoint(*args):
    NLTA_Graph.Clamp()
    currentTime = cmds.currentTime(query=True)
    verts = cmds.ls(sl=True, fl=True)
    if not verts:
        cmds.warning("No vertices selected")
        return
    mesh = verts[0].split(".")[0]
    skinData = NLTA_General.GetSkinData(mesh)
    jointA = skinData["jointActive"]
    joints = skinData["jointsUnlock"]
    skinCluster = skinData["skinCluster"]
    oldEnv = cmds.getAttr(skinCluster + ".envelope")
    cmds.setAttr(skinCluster + ".envelope", 0)
    try:
        distances = []
        validVerts = []
        for v in verts:
            if ".vtx[" not in v:
                continue
            d = NLTA_General.GetDistance(v, jointA)
            if d is None:
                continue
            distances.append(d)
            validVerts.append(v)
        if not distances:
            return
        minDist = min(distances)
        maxDist = max(distances)        
        if abs(maxDist - minDist) < 1e-8:
            maxDist = minDist + 1e-8    
        for v in validVerts:
            d = NLTA_General.GetDistance(v, jointA)
            ratio = (d - minDist) / (maxDist - minDist)
            ratio = 1-(max(0.0, min(1.0, ratio)))
            val = NLTA_Graph.GetValue(ratio)
            if val is None:
                val = ratio * 100.0
            totalW = 0.0
            for j in joints:
                totalW += cmds.skinPercent(skinCluster, v, q=True, transform=j)
            if totalW == 0:
                continue
            newA = totalW * val
            cmds.skinPercent(skinCluster,v,transformValue=[(jointA, newA)],normalize=True)
    finally:
        cmds.setAttr(skinCluster + ".envelope", oldEnv)
    cmds.skinCluster(skinCluster, e=True, forceNormalizeWeights=True)
    UpdateView()
    cmds.currentTime(currentTime)

"""
def WeightFromRatio(data):
    skinCluster = data["skinCluster"]
    vert = data["vert"]
    joints = data["joints"]
    ratios = data["ratios"]
    if not joints or not ratios or len(joints) != len(ratios):
        return
    values = [cmds.skinPercent(skinCluster, vert, q=True, transform=j) for j in joints]
    totalWeight = sum(values)
    if totalWeight == 0:
        return
    newWeights = [totalWeight * r for r in ratios]
    cmds.skinPercent(skinCluster,vert,transformValue=list(zip(joints, newWeights)))


def WeightFromRatio(data):
    skinCluster = data["skinCluster"]
    vert = data["vert"]
    joints = data["joints"]
    ratios = data["ratios"]
    if not joints or len(joints) != len(ratios):
        return

    # -----------------------------
    # Get SkinCluster
    # -----------------------------
    sel = om.MSelectionList()
    sel.add(skinCluster)
    skinObj = sel.getDependNode(0)
    fnSkin = oma.MFnSkinCluster(skinObj)

    # -----------------------------
    # Vertex Component
    # -----------------------------
    mesh = vert.split(".vtx[")[0]
    vtxId = int(vert.split("[")[-1].split("]")[0])

    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)

    compFn = om.MFnSingleIndexedComponent()
    comp = compFn.create(om.MFn.kMeshVertComponent)
    compFn.addElement(vtxId)

    # -----------------------------
    # Influences
    # -----------------------------
    influences = fnSkin.influenceObjects()
    influenceIndex = {}

    for i, inf in enumerate(influences):
        influenceIndex[inf.partialPathName()] = i

    # -----------------------------
    # Current Weights
    # -----------------------------
    weights, influenceCount = fnSkin.getWeights(dag, comp)

    weights = list(weights)

    total = 0.0
    indices = []

    for j in joints:
        if j not in influenceIndex:
            continue

        idx = influenceIndex[j]
        indices.append(idx)
        total += weights[idx]

    if total <= 1e-8:
        return

    # -----------------------------
    # Apply Ratio
    # -----------------------------
    for ratio, idx in zip(ratios, indices):
        weights[idx] = total * ratio

    # API 2.0
    weights = om.MDoubleArray(weights)

    fnSkin.setWeights(
        dag,
        comp,
        om.MIntArray(indices),
        om.MDoubleArray([weights[i] for i in indices]),
        False
    )

def CopyRatioWeight(*arr):
    verts = cmds.ls(selection=True,flatten=True)
    if verts:
        mesh = verts[0].split(".")[0]
        skinData = NLTA_General.GetSkinData(mesh)
        skinCluster = skinData["skinCluster"]
        oldEnv = cmds.getAttr(skinCluster + ".envelope")
        cmds.setAttr(skinCluster + ".envelope", 0)
        data = NLTA_Mesh.ListToPerVerts(verts)
        for vert in data:
            jointsWeight = NLTA_Skinning.GetJointsWeight({
                "skinCluster":skinData["skinCluster"],
                "vert":vert,
                "joints":skinData["jointsUnlock"]
            })
            ratios = []
            for jointUnlock in skinData["jointsUnlock"]:
                ratios.append(jointsWeight[jointUnlock]["ratio"])
            verts = cmds.ls(data[vert],flatten=True)
            for vertTemp in verts:
                WeightFromRatio({
                    "skinCluster":skinCluster,
                    "vert":vertTemp,
                    "joints":skinData["jointsUnlock"],
                    "ratios":ratios
                })
        cmds.setAttr(skinCluster + ".envelope",oldEnv)
        cmds.skinCluster(skinCluster, e=True, forceNormalizeWeights=True)
        UpdateView()
"""

def CopyRatioWeight(*args):
    verts = cmds.ls(sl=True, fl=True)
    if not verts:
        return
    mesh = verts[0].split(".")[0]
    skinData = NLTA_General.GetSkinData(mesh)
    skinCluster = skinData["skinCluster"]
    unlockJoints = skinData["jointsUnlock"]
    oldEnv = cmds.getAttr(skinCluster + ".envelope")
    cmds.setAttr(skinCluster + ".envelope", 0)
    sel = om.MSelectionList()
    sel.add(skinCluster)
    skinObj = sel.getDependNode(0)
    fnSkin = oma.MFnSkinCluster(skinObj)
    sel.clear()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    influenceIndex = {}
    for i, inf in enumerate(fnSkin.influenceObjects()):
        influenceIndex[inf.partialPathName()] = i

    # ----------------------------------------------------
    # Data
    # ----------------------------------------------------
    data = NLTA_Mesh.ListToPerVerts(verts)
    for sourceVert in data:
        jointsWeight = NLTA_Skinning.GetJointsWeight({
            "skinCluster": skinCluster,
            "vert": sourceVert,
            "joints": unlockJoints
        })
        ratios = [
            jointsWeight[j]["ratio"]
            for j in unlockJoints
        ]
        targetVerts = cmds.ls(data[sourceVert], fl=True)
        for vert in targetVerts:
            vtxId = int(vert.split("[")[-1].split("]")[0])
            compFn = om.MFnSingleIndexedComponent()
            comp = compFn.create(om.MFn.kMeshVertComponent)
            compFn.addElement(vtxId)
            weights, influenceCount = fnSkin.getWeights(dag, comp)
            weights = list(weights)
            total = 0.0
            indices = []
            for j in unlockJoints:
                if j not in influenceIndex:
                    continue
                idx = influenceIndex[j]
                indices.append(idx)
                total += weights[idx]
            if total <= 1e-8:
                continue
            values = []
            for ratio, idx in zip(ratios, indices):
                value = total * ratio
                weights[idx] = value
                values.append(value)
            for idx, value in zip(indices, values):
                fnSkin.setWeights(dag,comp,idx,value,False)
    cmds.setAttr(skinCluster + ".envelope", oldEnv)
    cmds.skinCluster(skinCluster,e=True,forceNormalizeWeights=True)
    UpdateView()


def TransferInfluenceWeight(skinCluster, verts, sourceJoint, targetJoint):
    if not verts:
        return
    sel = om.MSelectionList()
    sel.add(skinCluster)
    skinObj = sel.getDependNode(0)
    fnSkin = oma.MFnSkinCluster(skinObj)
    mesh = verts[0].split(".")[0]
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    compFn = om.MFnSingleIndexedComponent()
    comp = compFn.create(om.MFn.kMeshVertComponent)
    ids = [int(v.split("[")[-1].split("]")[0]) for v in verts]
    compFn.addElements(ids)
    influences = fnSkin.influenceObjects()
    sourceIndex = None
    targetIndex = None
    for i, inf in enumerate(influences):
        name = om.MFnDagNode(inf).fullPathName()
        if name.endswith(sourceJoint):
            sourceIndex = i
        if name.endswith(targetJoint):
            targetIndex = i
    if sourceIndex is None:
        raise RuntimeError("Source joint not found.")
    if targetIndex is None:
        raise RuntimeError("Target joint not found.")
    weights, influenceCount = fnSkin.getWeights(dag, comp)
    for v in range(len(ids)):
        offset = v * influenceCount
        s = offset + sourceIndex
        t = offset + targetIndex
        weights[t] += weights[s]
        weights[s] = 0.0
    influenceIds = om.MIntArray(range(influenceCount))
    fnSkin.setWeights(dag,comp,influenceIds,weights,False)

def SkirtParentRun(data,*arr):
    jointParent = data["jointParent"]
    joints = NLTA_Mesh.SortCircularJoints(data["joints"])
    mesh = data["mesh"]
    skinData = NLTA_General.GetSkinData(mesh)

    #Get closest vertex
    closestVert = NLTA_Mesh.GetClosestVertex(mesh,joints[0])
    rootLoop = NLTA_Mesh.GetPerpendicularEdgeLoop(mesh,joints[0],closestVert)
    checkClosed = NLTA_Mesh.CheckEdgeLoopClosed(mesh,rootLoop)

    rootVerts = NLTA_Mesh.VertexFromEdges(mesh,rootLoop)
    for joint in joints:
        closestJoint = NLTA_Mesh.GetClosestJoint(joint,joints)
        distance = closestJoint[0][1]
        radius = distance*.6
        vertsEffect = NLTA_Mesh.SelectVerticesWithinRadius(mesh,joint,rootVerts,radius)
        vertsTransfer =  NLTA_Mesh.ListToPerVerts(vertsEffect)
        for v in vertsTransfer:
            TransferInfluenceWeight(skinData["skinCluster"],cmds.ls(vertsTransfer[v],flatten=True),jointParent,joint)

    NLTA_Graph.SkirtCurve()
    # Smooth Parents
    for stt in range(len(joints)-1):
        jointFrom = joints[stt]
        jointTo = joints[stt+1]
        NLTA_Skinning.UnlockJoints(mesh,[jointFrom,jointTo])
        NLTA_Skinning.ActiveJoint(mesh,jointTo)
        jointFromEdge = NLTA_Mesh.GetClosestEdge(mesh,rootLoop,jointFrom)
        jointToEdge = NLTA_Mesh.GetClosestEdge(mesh,rootLoop,jointTo)
        edgesBetween = NLTA_Mesh.EdgesBetween(mesh,jointFromEdge,jointToEdge)
        vertsBetween = NLTA_Mesh.VertexFromEdges(mesh,edgesBetween)                            
        cmds.select(vertsBetween)
        GradientActiveJoint()
        CopyRatioWeight()

    if checkClosed:
        jointFrom = joints[0]
        jointTo = joints[-1]
        NLTA_Skinning.UnlockJoints(mesh,[jointFrom,jointTo])
        NLTA_Skinning.ActiveJoint(mesh,jointTo)
        jointFromEdge = NLTA_Mesh.GetClosestEdge(mesh,rootLoop,jointFrom)
        jointToEdge = NLTA_Mesh.GetClosestEdge(mesh,rootLoop,jointTo)
        edgesBetween = NLTA_Mesh.EdgesBetween(mesh,jointFromEdge,jointToEdge)
        vertsBetween = NLTA_Mesh.VertexFromEdges(mesh,edgesBetween)                            
        cmds.select(vertsBetween)
        GradientActiveJoint()
        CopyRatioWeight()


def SkirtParent(*arr):
    SkirtParentRun({
        "jointParent":cmds.ls(orderedSelection=True,type="joint")[0],
        "joints":cmds.ls(orderedSelection=True,type="joint")[1:-1],
        "mesh":cmds.ls(orderedSelection=True)[-1],
    }) 

   
def SkirtChains(*arr):
    meshs = NLTA_Mesh.GetMesh()    
    if meshs:
        mesh = meshs[0]
        skinData = NLTA_General.GetSkinData(mesh)
        if skinData:
            unlockJoints = skinData["jointsUnlock"]
            bindJoints = skinData["joints"]
            skinCluster = skinData["skinCluster"]

            # FIND HIERARCHY ARRAY
            def Walk(joint, chain):
                chain.append(joint)
                children = cmds.listRelatives(joint, c=True, type="joint") or []
                children = [c for c in children if c in unlockJoints]
                if not children:
                    hierarchyArray.append(chain[:])
                    return
                for child in children:
                    Walk(child, chain[:])
            hierarchyArray = []
            roots = []
            for joint in unlockJoints:
                parent = cmds.listRelatives(joint, p=True, type="joint")
                if not parent or parent[0] not in unlockJoints:
                    roots.append(joint)
            for root in roots:
                Walk(root, [])

            for joints in hierarchyArray:
                vertPinID =  NLTA_Mesh.GetClosestVertex(mesh,joints[0])
                edgePin =  NLTA_Mesh.GetJointEdgeLoop(mesh,joints[0],vertPinID)
                closestEdge = NLTA_Mesh.GetClosestEdge(mesh,edgePin,joints[0])
                farthestEdge = NLTA_Mesh.GetFarthestEdge(mesh,closestEdge,edgePin)

                jointChildren = joints[1:]
                for stt in range(len(jointChildren)):
                    parentJoint = joints[stt]
                    parentEdge = NLTA_Mesh.GetClosestEdge(mesh,edgePin,parentJoint)
                    currentJoint = jointChildren[stt]
                    currentEdge = NLTA_Mesh.GetClosestEdge(mesh,edgePin,currentJoint)
                    NLTA_Skinning.UnlockJoints(mesh,[parentJoint,currentJoint])
                    edgeBetween = NLTA_Mesh.EdgesBetween(mesh,currentEdge,farthestEdge)
                    vertsBetween = NLTA_Mesh.VertexFromEdges(mesh,edgeBetween)
                    vertsSubtract =  NLTA_Mesh.ListToPerVerts(vertsBetween)
                    for v in vertsSubtract:
                        TransferInfluenceWeight(skinData["skinCluster"],cmds.ls(vertsSubtract[v],flatten=True),parentJoint,currentJoint)

                    """
                    #Smooth
                    childIndex = stt + 1

                    if childIndex >= len(jointChildren):
                        childEdge = farthestEdge
                        NLTA_Graph.SkirtEndCurve()
                        #NLTA_Graph.SkirtCurve()                       
                    else:
                        childEdge = NLTA_Mesh.GetClosestEdge(mesh,edgePin,jointChildren[childIndex])
                        NLTA_Graph.SkirtCurve()
                    NLTA_Skinning.ActiveJoint(mesh,parentJoint)
                    edgeBetween = NLTA_Mesh.EdgesBetween(mesh,parentEdge,childEdge)
                    vertsBetween = NLTA_Mesh.VertexFromEdges(mesh,edgeBetween)                    
                    cmds.select(vertsBetween)
                    GradientActiveJoint()
                    CopyRatioWeight()
                    """

def SelectVertexIntersect(data):
    def get_mesh_fn(mesh):
        sel = om.MSelectionList()
        sel.add(mesh)
        dag = sel.getDagPath(0)
        return om.MFnMesh(dag), dag
    def is_vertex_inside_mesh(point, fnMeshB):
        direction = om.MFloatVector(1, 0.37, 0.21).normalize()
        hits = fnMeshB.allIntersections(om.MFloatPoint(point),direction,om.MSpace.kWorld,1e10,False)
        if not hits or len(hits[0]) == 0:
            return False
        hit_count = len(hits[0])
        return (hit_count % 2) == 1
    objs = cmds.ls(os=True)
    if len(objs)==2:
        meshA = objs[1]
        meshB = objs[0]
        fnA, dagA = get_mesh_fn(meshA)
        fnB, dagB = get_mesh_fn(meshB)
        it = om.MItMeshVertex(dagA)
        inside_vertices = []
        while not it.isDone():
            pos = it.position(om.MSpace.kWorld)
            if is_vertex_inside_mesh(pos, fnB):
                index = it.index()
                inside_vertices.append(meshA+(".vtx[{}]".format(index)))
            it.next()
        cmds.select(inside_vertices)

"""
def FindOddVertex(mesh, vertices):
    if len(vertices) != 5:
        raise RuntimeError("Need exactly 5 vertices.")

    # -------------------------------------------------------
    # Find skinCluster
    # -------------------------------------------------------

    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
    skins = cmds.ls(history, type="skinCluster")

    if not skins:
        raise RuntimeError("No skinCluster found.")

    skin = skins[0]

    # -------------------------------------------------------
    # Rest Position
    # -------------------------------------------------------

    env = cmds.getAttr(skin + ".envelope")

    cmds.setAttr(skin + ".envelope", 0)

    rest = [
        om.MPoint(*cmds.xform(v, q=True, ws=True, t=True))
        for v in vertices
    ]

    cmds.setAttr(skin + ".envelope", env)

    # -------------------------------------------------------
    # Current Position
    # -------------------------------------------------------

    current = [
        om.MPoint(*cmds.xform(v, q=True, ws=True, t=True))
        for v in vertices
    ]

    # -------------------------------------------------------
    # Displacement
    # -------------------------------------------------------

    disp = []

    for r, c in zip(rest, current):
        disp.append((c - r).length())

    # -------------------------------------------------------
    # Predict by neighbours
    # -------------------------------------------------------

    errors = [0.0] * 5

    # v1 should lie between v0 and v2
    predict = (disp[0] + disp[2]) * 0.5
    errors[1] = abs(disp[1] - predict)

    # v2 should lie between v1 and v3
    predict = (disp[1] + disp[3]) * 0.5
    errors[2] = abs(disp[2] - predict)

    # v3 should lie between v2 and v4
    predict = (disp[2] + disp[4]) * 0.5
    errors[3] = abs(disp[3] - predict)

    # Ignore endpoints
    errors[0] = -1
    errors[4] = -1

    index = max(range(5), key=lambda i: errors[i])

    return (
        vertices[index],
        disp,
        errors
    ) 
oddVertex, errors, stretches = FindOddVertex(
    "nurbsToPoly1",cmds.ls(os=True,fl=True)
)

print("Odd Vertex :", oddVertex)
print("Errors     :", errors)
print("Stretch    :", stretches)
"""