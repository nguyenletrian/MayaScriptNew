import json
import importlib
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

import NLTA_General,NLTA_Mesh,NLTA_Axis
for module in [NLTA_General,NLTA_Mesh,NLTA_Axis]:
    try:
        importlib.reload(module)
    except:
        reload(module)
        

session = {}
def singleProxy(*arr):
    selection = cmds.ls(selection=True)
    if cmds.objectType(selection[0]) == "mesh":
        mel.eval('ConvertSelectionToFaces;')
        face = cmds.ls(selection=True)
        meshTransform = selection[0].split(".")[0]
        skinCluster = mel.eval('findRelatedSkinCluster '+meshTransform)
        if skinCluster:
            joint = cmds.skinCluster(skinCluster,query=True,inf=True)

        meshNew =  cmds.ls(cmds.duplicate(meshTransform)[0],uuid=True)[0]
        meshNew =  cmds.ls(meshNew,ap=True)[0]
        faceNew = cmds.ls(meshNew+".f[*]")
        arrayTemp = []
        for a in face:
            faceName = a.replace(meshTransform,meshNew)
            arrayTemp.append(faceName)
        cmds.select(faceNew)
        cmds.select(arrayTemp,deselect=True)
        cmds.delete()
        cmds.delete(meshNew,constructionHistory=True)
        if skinCluster:
            cmds.select(joint)
            cmds.select(meshNew,add=True)
            NLTA_General.bindSkin()
            cmds.select(meshTransform)
            cmds.select(meshNew,add=True)
            newSkinCluster = mel.eval('findRelatedSkinCluster '+meshNew)
            mel.eval('copySkinWeights -ss '+skinCluster+' -ds '+newSkinCluster+' -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint;')
            cmds.select(meshNew)            
        else:
            cmds.select(meshNew)
        copyProxy()
        cmds.warning("Done!!!")

def createProxy(axis,*arr):
    selection = cmds.ls(selection=True)
    if cmds.objectType(selection[0]) == "mesh":
        mel.eval('ConvertSelectionToFaces;')
        face = cmds.ls(selection=True)
        meshTransform = selection[0].split(".")[0]
        skinCluster = mel.eval('findRelatedSkinCluster '+meshTransform)
        if skinCluster:
            joint = cmds.skinCluster(skinCluster,query=True,inf=True)

        meshNew =  cmds.ls(cmds.duplicate(meshTransform)[0],uuid=True)[0]
        meshNew =  cmds.ls(meshNew,ap=True)[0]
        faceNew = cmds.ls(meshNew+".f[*]")
        arrayTemp = []
        for a in face:
            faceName = a.replace(meshTransform,meshNew)
            arrayTemp.append(faceName)

        cluster = cmds.cluster(arrayTemp)
        axisNegPos = NLTA_General.checkNegPosAxis(cluster,axis)
        if axisNegPos == "-":
            direction = str(0)
        else:
            direction = str(1)
        cmds.delete(cluster)

        axisArray = ["x","y","z"]
        axisIndex = str(axisArray.index(axis))

        cmds.select(faceNew)
        cmds.select(arrayTemp,deselect=True)
        cmds.delete()

        mel.eval('polyMirrorFace  -cutMesh 1 -axis '+axisIndex+' -axisDirection '+direction+' -mergeMode 0 -mergeThresholdType 0.001 '+meshNew+';')#-mergeThreshold 0.001 
        cmds.delete(meshNew,constructionHistory=True)
        cmds.select(joint)
        cmds.select(meshNew,add=True)
        NLTA_General.bindSkin()
        cmds.select(meshTransform)
        cmds.select(meshNew,add=True)
        
        #mel.eval('copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation oneToOne -influenceAssociation closestJoint -normalize;')
        #copySkinWeights -ss skinCluster1 -ds skinCluster16 -noMirror -surfaceAssociation closestComponent -influenceAssociation closestJoint;
        newSkinCluster = mel.eval('findRelatedSkinCluster '+meshNew)
        mel.eval('copySkinWeights -ss '+skinCluster+' -ds '+newSkinCluster+' -noMirror -surfaceAssociation closestComponent -influenceAssociation closestJoint;')
        cmds.select(meshNew)
        copyProxy()
        cmds.warning("Done!!!")

def copyProxy(*arr):
    global session
    selection = cmds.ls(selection=True)
    if cmds.objectType(selection[0]) == "mesh":
        mel.eval('ConvertSelectionToVertices;')
        vertex = cmds.ls(selection=True,flatten=True)
        parentName = selection[0].split(".")[0]
        cmds.select(parentName)
    elif cmds.objectType(selection[0]) == "transform":
        vertex = cmds.ls(selection[0]+".vtx[*]",flatten=True)
        parentName = selection[0]
    session["vertex"] = vertex
    session["mesh"] = parentName

def pastProxy(*arr):
    selection = cmds.ls(selection=True)
    if cmds.objectType(selection[0]) == "mesh":
        mel.eval('ConvertSelectionToVertices;')
        vertex = cmds.ls(selection=True)
        parentName = selection[0].split(".")[0]
        cmds.select(session["vertex"])
        cmds.select(vertex,add=True)
        mel.eval('copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne -selectedComponents;')
    elif cmds.objectType(selection[0]) == "transform":
        for aSelect in selection:
            vertex = cmds.ls(aSelect+".vtx[*]")            
            cmds.select(clear=True)
            cmds.select(session["vertex"])
            cmds.select(vertex,add=True)
            sourceSkinCluster = mel.eval('findRelatedSkinCluster '+session["mesh"])            
            targetSkinCluster = mel.eval('findRelatedSkinCluster '+aSelect)
            mel.eval('copySkinWeights  -ss '+sourceSkinCluster+' -ds '+targetSkinCluster+'  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne;')
    cmds.select(selection)
    cmds.warning("Done!!!")

def SelectClosetFaces(*arr):
    def get_mesh_fn(mesh):
        sel = om.MSelectionList()
        sel.add(mesh)
        dag = sel.getDagPath(0)
        return om.MFnMesh(dag)

    def get_face_centroids(mesh):
        fn = get_mesh_fn(mesh)
        centroids = {}
        for i in range(fn.numPolygons):
            points = fn.getPolygonVertices(i)
            verts = [om.MVector(fn.getPoint(v, om.MSpace.kWorld)) for v in points]
            c = sum(verts, om.MVector()) / len(verts)
            centroids[i] = c
        return centroids

    def FindMatchingFaces(source,target, tolerance=0.001):
        centA = get_face_centroids(source)
        centB = get_face_centroids(target)
        matches = []
        for fA, cA in centA.items():
            for fB, cB in centB.items():
                if (cA - cB).length() < tolerance:
                    matches.append(fB)
        return matches
    objs = cmds.ls(selection=True)
    source = objs[0]
    targets = objs[1:]
    faces = []
    for target in targets:
        facesID = FindMatchingFaces(source,target)
        for faceID in facesID:
            faces.append("%s.f[%s]" % (target, faceID))
    cmds.select(faces)



#### RETOPOLOGY
loftAttr = 'NLTA_LoftData'

def GetPositions(objs):
    return([om.MVector(cmds.pointPosition(v, w=True)) for v in objs])

def GetCenter(objs):
    positions = GetPositions(objs)
    center = sum(positions, om.MVector(0, 0, 0)) / len(positions)
    return(center)

def GetFarthest(objs):
    positions = GetPositions(objs)
    center = GetCenter(objs)
    farIndex, farDist = 0,0
    for i, pos in enumerate(positions):
        dist = (pos - center).length()
        if dist > farDist:
            farIndex,farDist = i,dist
    vertexVector = positions[farIndex]
    vectorFromCenter = (vertexVector - center).normalize()
    return({
        'vertexVector':vertexVector,
        'obj':objs[farIndex],
        'distance':farDist,
        'vectorFromCenter':vectorFromCenter,
    })

def EdgesToCurve(*args):
    sel = cmds.filterExpand(sm=32)
    if not sel:
        cmds.warning("Please select edges.")
        return
    curve = cmds.polyToCurve(form=0,degree=3,conformToSmoothMeshPreview=True)[0]
    cvs = cmds.ls(curve + ".cv[*]", fl=True)
    cvWorldPos = [cmds.pointPosition(cv, w=True) for cv in cvs]
    mesh = sel[0].split(".")[0]
    vertIndices = set()
    for edge in sel:
        ids = cmds.polyInfo(edge, edgeToVertex=True)[0].split()[2:]
        vertIndices.update(map(int, ids))
    avgPos = om.MVector()
    avgNormal = om.MVector()
    selList = om.MSelectionList()
    selList.add(mesh)
    dag = selList.getDagPath(0)
    fnMesh = om.MFnMesh(dag)
    for index in vertIndices:
        p = om.MVector(fnMesh.getPoint(index, om.MSpace.kWorld))
        n = om.MVector(fnMesh.getVertexNormal(index, True, om.MSpace.kWorld))
        avgPos += p
        avgNormal += n
    count = len(vertIndices)
    avgPos /= count
    if avgNormal.length() < 1e-6:
        avgNormal = om.MVector(0, 1, 0)
    else:
        avgNormal.normalize()
    zAxis = avgNormal
    up = om.MVector(0, 1, 0)
    if abs(zAxis * up) > 0.999:
        up = om.MVector(1, 0, 0)
    xAxis = up ^ zAxis
    xAxis.normalize()
    yAxis = zAxis ^ xAxis
    yAxis.normalize()
    matrix = [
        xAxis.x, xAxis.y, xAxis.z, 0,
        yAxis.x, yAxis.y, yAxis.z, 0,
        zAxis.x, zAxis.y, zAxis.z, 0,
        avgPos.x, avgPos.y, avgPos.z, 1
    ]
    cmds.xform(curve, ws=True, matrix=matrix)
    for cv, pos in zip(cvs, cvWorldPos):
        cmds.xform(cv, ws=True, t=pos)
    return curve

def VertsToCurve(*args):
    sel = cmds.ls(sl=True, fl=True)
    verts = cmds.filterExpand(sel, sm=31)
    if not verts or len(verts) < 2:
        cmds.warning("Please select at least two vertices.")
        return
    positions = []
    avgPos = om.MVector()
    avgNormal = om.MVector()
    for v in verts:
        pos = cmds.pointPosition(v, w=True)
        positions.append(pos)
        selList = om.MSelectionList()
        selList.add(v)
        dagPath, comp = selList.getComponent(0)
        it = om.MItMeshVertex(dagPath, comp)
        avgPos += om.MVector(it.position(om.MSpace.kWorld))
        avgNormal += om.MVector(it.getNormal(om.MSpace.kWorld))
    avgPos /= len(verts)
    if avgNormal.length() < 1e-6:
        avgNormal = om.MVector(0, 1, 0)
    else:
        avgNormal.normalize()
    degree = 3 if len(positions) >= 4 else 1
    curve = cmds.curve(d=degree,p=positions)
    cmds.rebuildCurve(curve,ch=False,rpo=True,rt=0,end=True,kr=False,kcp=False,kep=False,kt=False,s=0,d=degree,tol=0.01)
    cvs = cmds.ls(curve + ".cv[*]", fl=True)
    cvWorldPos = [cmds.pointPosition(cv, w=True) for cv in cvs]
    zAxis = avgNormal
    worldUp = om.MVector(0, 1, 0)
    if abs(zAxis * worldUp) > 0.999:
        worldUp = om.MVector(1, 0, 0)
    xAxis = worldUp ^ zAxis
    xAxis.normalize()
    yAxis = zAxis ^ xAxis
    yAxis.normalize()
    matrix = [
        xAxis.x, xAxis.y, xAxis.z, 0,
        yAxis.x, yAxis.y, yAxis.z, 0,
        zAxis.x, zAxis.y, zAxis.z, 0,
        avgPos.x, avgPos.y, avgPos.z, 1
    ]
    cmds.xform(curve,ws=True,matrix=matrix)
    for cv, pos in zip(cvs, cvWorldPos):
        cmds.xform(cv,ws=True,t=pos)
    cmds.select(curve)
    return curve

def DrawCurve(*arr):
    mel.eval(r'''
        global string $ctx = "myCurveEPContext";
        if (!`contextInfo -exists $ctx`)
        {
            curveEPCtx -name $ctx -d 3 -bez false;
        }
        else
        {
            curveEPCtx -e -d 3 -bez false $ctx;
        }
        setToolTo $ctx;
    ''')


def FlipLoftNormal(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        lofData = GetLoftData(objs[0])
        cmds.reverseSurface(cmds.ls(lofData['loft'])[0], direction=0, ch=1)

def FlipCurveNormal(*arr):
    objs= cmds.ls(selection=True)
    if objs:
        for obj in objs:
            cmds.reverseCurve(obj, ch=False, rpo=True)
    cmds.select(objs)

def RotateCVsPositive(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        obj = objs[0]
        cvs = cmds.ls(obj+".cv[*]", fl=True)
        count = len(cvs)
        originPos = [cmds.xform(cv, worldSpace=True,query=True, translation=True) for cv in cvs]
        for i in range(count):
            cmds.xform(cvs[i], ws=True, t=originPos[i-1])

def RotateCVsNegative(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        obj = objs[0]
        cvs = cmds.ls(obj+".cv[*]", fl=True)
        count = len(cvs) 
        originPos = [cmds.xform(cv, worldSpace=True,query=True, translation=True) for cv in cvs]
        for i in range(len(originPos)):
            increaseI = i + 1
            if increaseI !=  len(originPos):
                cvIndex = i
                posIndex = increaseI
            else:
                cvIndex = i
                posIndex = 0
            cmds.xform(cvs[cvIndex], ws=True, t=originPos[posIndex])

def CloseCurve(*arr):
    objs = cmds.ls(selection=True)
    for obj in objs:
        dup = cmds.duplicate(obj, rr=True)[0]
        closed = cmds.closeCurve(dup, ch=False, replaceOriginal=True, preserveShape=False)[0]
        new_shape = cmds.listRelatives(closed, s=True, f=True)[0]
        old_shapes = cmds.listRelatives(obj, s=True, f=True) or []
        cmds.parent(new_shape, obj, shape=True, relative=True)
        for s in old_shapes:
            cmds.delete(s)
        if closed != obj:
            cmds.delete(closed)
    cmds.select(objs)

def RebuildCurves(curves):
    spans=16
    for c in curves:
        cmds.delete(c, ch=True) 
        cmds.rebuildCurve(c, ch=False, rpo=True, rt=0,
                          end=1, kr=0, kcp=0, kep=1, d=3, s=spans)
def AlignCurvesDirection(curves):
    def get_tangent(curve):
        p0 = om.MVector(cmds.pointPosition("%s.cv[0]" % curve, w=True))
        p1 = om.MVector(cmds.pointPosition("%s.cv[1]" % curve, w=True))
        return (p1 - p0).normalize()
    base_vec = get_tangent(curves[0])
    for c in curves[1:]:
        this_vec = get_tangent(c)
        dot = base_vec * this_vec
        if dot < 0:
            cmds.reverseCurve(c, ch=False, rpo=True)

def CleanCurve(curves):
    RebuildCurves(curves)
    AlignCurvesDirection(curves)

def SetLoftData(obj,data):
    data = {
        'curves':cmds.ls(data['curves'],uuid=True),
        'loft':cmds.ls(data['loft'],uuid=True)[0],
        'poly':cmds.ls(data['poly'],uuid=True)[0],
    }
    dataStr = json.dumps(data)
    if not cmds.attributeQuery(loftAttr, node=obj, exists=True):
        cmds.addAttr(obj, longName=loftAttr, dataType="string")
    cmds.setAttr(obj+"."+loftAttr, dataStr, type="string")

def GetLoftData(obj):
    if cmds.attributeQuery(loftAttr, node=obj, exists=True):
        raw = cmds.getAttr(obj+"."+loftAttr)
        data = json.loads(raw)
        return(data)
    return(None)

def ClearLoftData(obj):
    if cmds.attributeQuery(loftAttr, node=obj, exists=True):
        cmds.deleteAttr(obj+"."+loftAttr)
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.objectType(shape) == "nurbsCurve":
                cmds.setAttr(obj + ".overrideColor",0)
                cmds.setAttr(obj+".overrideDisplayType",0)
                break

def ClearAllLoft(*arr):
    objs = cmds.ls(type='loft')
    for obj in objs:
        if cmds.attributeQuery(loftAttr, node=obj, exists=True):
            data = GetLoftData(obj)
            if cmds.ls(data['poly']) == []:
                cmds.delete(cmds.ls(data['loft'])[0])
                for curve in data['curves']:
                    if cmds.ls(curve):
                        ClearLoftData(cmds.ls(curve)[0])
            else:
                loft = cmds.ls(data['loft'])[0]
                poly = cmds.ls(data['poly'])[0] 
                curves = GetLoftInputCurves(loft)
                for objTemp in  [loft]+[poly]+curves:
                    SetLoftData(objTemp,{
                        'loft':loft,
                        'poly':poly,
                        'curves':curves
                    })

def GetLoftNode(loft):
    history = cmds.listHistory(loft)
    node = next((h for h in history if cmds.nodeType(h) == "loft"), None)
    if node:
        return(node)
    return(None)

def GetLoftInputCurves(loft):
    node = GetLoftNode(loft)
    if node:
        curves = []
        i = 0
        while True:
            plug = node+".inputCurve["+str(i)+"]"
            conn = cmds.connectionInfo(plug,sfd=True)       
            if conn:
                shapeName = conn.split('.')[0]
                transformName = cmds.listRelatives(shapeName,parent=True)[0]
                curves.append(transformName)
            else:
                break
            i += 1
        return(curves)
    return(None)

def ChangeOutlinerOrder(*arr):
    sel = cmds.ls(long=True, orderedSelection=True)
    if len(sel) < 2:
        cmds.warning("Select at least two sibling objects.")
        return
    parents = []
    for obj in sel:
        p = cmds.listRelatives(obj, p=True, fullPath=True)
        parents.append(p[0] if p else "")
    if len(set(parents)) != 1:
        cmds.warning("Selected objects must have the same parent.")
        return
    for obj in sel:
        cmds.reorder(obj, back=True)


def CreateLoft(*arr):
    ChangeOutlinerOrder()    
    ClearAllLoft()
    curves = cmds.ls(selection=True, type='transform')
    objsSave = curves.copy()
    if len(curves) < 2:
        cmds.warning("Select at least 2 curve.")
        return
    CleanCurve(curves)
    result = cmds.loft(curves,ch=True,u=False,c=False,ar=False,d=3,ss=1,rn=False,po=0)
    surface = result[0]
    cmds.setAttr(surface+".hiddenInOutliner", 1)
    cmds.setAttr(surface+".visibility",0)
    objsSave.extend(result)
    poly = cmds.nurbsToPoly(surface,mnd=1,ch=1,f=2,pt=1,pc=200,chr=0.99,ft=1,mel=1,d=1,ut=1,un=20,vt=1,
        vn=20,uch=0,ucr=0,cht=0.2,es=0,ntr=0,mrt=0,uss=1)[0]
    objsSave.append(poly) 
    data = {
        'curves':curves,
        'loft':surface,
        'poly':poly,
    }
    for curve in curves:
        cmds.setAttr(curve + ".overrideColor",17)
    for obj in objsSave:
        SetLoftData(obj,data)

    return(poly)

def AddLoftCurve(*arr):
    ChangeOutlinerOrder()
    ClearAllLoft()    
    objs = cmds.ls(selection=True,ap=True)
    if objs:
        curveReference = None
        for obj in objs:
            if cmds.attributeQuery(loftAttr, node=obj, exists=True):
                curveReference = obj
                data = GetLoftData(curveReference)
                break
        if curveReference:
            loft = cmds.ls(data['loft'])[0]
            poly = cmds.ls(data['poly'])[0]
            curves = cmds.ls(data['curves'])
            loftNode = GetLoftNode(loft)
            
            currentIndex = objs.index(curveReference)
            oldIndex = curves.index(curveReference)             
            if currentIndex == 0:
                oldIndex = curves.index(curveReference) + 1
                addObjs = objs[1:]
            elif currentIndex == (len(objs)-1):
                oldIndex = curves.index(curveReference)
                addObjs = objs[:-1]
                if oldIndex <= 0:
                    oldIndex = 0
            CleanCurve(addObjs)
            finalOrder = curves[:oldIndex] + addObjs + curves[oldIndex:]
            i = 0
            for curve in finalOrder:
                shape = cmds.listRelatives(curve,children=True,f=True)[0]
                cmds.connectAttr(shape+'.worldSpace[0]',loftNode+'.inputCurve['+str(i)+']',f=True)
                i += 1
            data['curves'] = finalOrder
            for obj in (finalOrder+[loft]+[poly]):
                SetLoftData(obj,{
                    'curves':finalOrder,
                    'poly':poly,
                    'loft':loft
                })

def ClearAllLoft(*arr):
    objs = cmds.ls(type='loft')
    for obj in objs:
        if cmds.attributeQuery(loftAttr, node=obj, exists=True):
            data = GetLoftData(obj)
            if cmds.ls(data['poly']) == []:
                cmds.delete(cmds.ls(data['loft'])[0])
                for curve in data['curves']:
                    if cmds.ls(curve):
                        ClearLoftData(cmds.ls(curve)[0])
            else:
                loft = cmds.ls(data['loft'])[0]
                poly = cmds.ls(data['poly'])[0] 
                curves = GetLoftInputCurves(loft)
                for objTemp in  [loft]+[poly]+curves:
                    SetLoftData(objTemp,{
                        'loft':loft,
                        'poly':poly,
                        'curves':curves
                    })


#### SKIN FINGURE SOLUTION
def CreateCircle(*args):
    sel = cmds.ls(sl=True, fl=True)
    if not sel:
        cmds.warning("Nothing selected.")
        return
    obj = sel[0]
    if cmds.nodeType(obj) == "joint":
        children = cmds.listRelatives(obj, c=True, type="joint") or []
        circle = cmds.circle(n=obj + "_Proxy",nr=(1, 0, 0),r=1)[0]
        cmds.delete(cmds.parentConstraint(obj, circle))
        if children:
            cmds.delete(cmds.aimConstraint(children[0],circle,aimVector=(1, 0, 0),upVector=(0, 1, 0),worldUpType="objectrotation",worldUpObject=obj))
        return circle

    if ".vtx[" in obj:
        pos = cmds.pointPosition(obj, w=True)
        selList = om.MSelectionList()
        selList.add(obj)
        dag, comp = selList.getComponent(0)
        it = om.MItMeshVertex(dag, comp)
        normal = om.MVector(it.getNormal(om.MSpace.kWorld))
        normal.normalize()
        circle = cmds.circle(n="Vertex_Proxy#",nr=(1, 0, 0),r=1)[0]
        cmds.xform(circle, ws=True, t=pos)
        quat = om.MVector(1, 0, 0).rotateTo(normal)
        euler = quat.asEulerRotation()
        cmds.xform(circle,ws=True,rotation=(om.MAngle(euler.x).asDegrees(),om.MAngle(euler.y).asDegrees(),om.MAngle(euler.z).asDegrees()))
        return circle

    if ".e[" in obj:
        cmds.select(obj)
        cluster = cmds.cluster()[1]
        circle = cmds.circle(n="Edge_Proxy#",nr=(1, 0, 0),r=1)[0]
        cmds.delete(cmds.parentConstraint(cluster, circle))
        cmds.delete(cluster)
        return circle

    if cmds.objExists(obj):
        circle = cmds.circle(n=obj + "_Proxy",nr=(1, 0, 0),r=1)[0]
        cmds.matchTransform(circle, obj)
        return circle

def FitCurveToMesh(mode="surface", *args):
    objs = cmds.ls(sl=True)
    if len(objs) < 2:
        cmds.warning("Select a curve, then a mesh.")
        return
    curve = objs[0]
    mesh = objs[1]
    sel = om.MSelectionList()
    sel.add(mesh)
    dag = sel.getDagPath(0)
    fnMesh = om.MFnMesh(dag)
    center = om.MPoint(cmds.xform(curve, q=True, ws=True, rp=True))
    cvs = cmds.ls(curve + ".cv[*]", fl=True)
    meshVerts = None
    if mode == "vertex":
        meshVerts = fnMesh.getPoints(om.MSpace.kWorld)
    for cv in cvs:
        cvPos = om.MPoint(cmds.xform(cv, q=True, ws=True, t=True))
        if mode == "surface":
            point, normal, faceId = fnMesh.getClosestPointAndNormal(cvPos,om.MSpace.kWorld)
            cmds.xform(cv,ws=True,t=(point.x, point.y, point.z))
        elif mode == "vertex":
            closest = None
            closestDist = 1e20
            for p in meshVerts:
                dist = (om.MVector(p) - om.MVector(cvPos)).length()
                if dist < closestDist:
                    closestDist = dist
                    closest = p
            if closest:
                cmds.xform(cv,ws=True,t=(closest.x, closest.y, closest.z))
        elif mode == "ray":
            rayDir = cvPos - center
            if rayDir.length() < 1e-8:
                continue
            rayDir.normalize()
            hit = fnMesh.closestIntersection(om.MFloatPoint(center),om.MFloatVector(rayDir),om.MSpace.kWorld,999999,False)
            if hit:
                p = hit[0]
                cmds.xform(cv,ws=True,t=(p.x, p.y, p.z))
        else:
            cmds.warning("Unknown mode : {}".format(mode))
            return