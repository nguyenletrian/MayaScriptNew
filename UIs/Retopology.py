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
    cmds.rowColumnLayout(numberOfColumns=1)#--

    #####
    cmds.rowColumnLayout(numberOfColumns=2)

    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=2)
    buttons.append(cmds.button(label="Curve From Edge",c=ConvertEdgeToCurve,width=160))
    buttons.append(cmds.button(label="Create Curve",c=CreateCurve,width=160))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=4)
    buttons.append(cmds.button(label="Create Plane",c=CreatePlane,width=80))
    buttons.append(cmds.button(label="Make Live",c=MakeLive,width=80))
    buttons.append(cmds.button(label="Exit Live",c=ExitLive,width=80))
    buttons.append(cmds.button(label="Draw Curve",c=DrawCurve,width=80))
    cmds.setParent("..")
    cmds.setParent("..")
    
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Close Curve",c=CloseCurve))
    cmds.separator(height=4, style='none')
    buttons.append(cmds.button(label="Correct Curve Axis",c=CorrectCurrentCurveAxis))
    cmds.setParent("..")

    cmds.setParent("..")
    #####    

    cmds.rowColumnLayout(numberOfColumns=3)
    buttons.append(cmds.button(label="Create Loft",c=CreateLoft,width=142))
    buttons.append(cmds.button(label="Add Loft Curve",c=AddLoftCurve,width=142))  
    buttons.append(cmds.button(label="Flip Loft Normal",c=FlipLoftNormal,width=142))       
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=4)
    #buttons.append(cmds.button(label="Select Vertex Near",c=SelectNearPlane))    
    buttons.append(cmds.button(label="RotateCVs +",c=RotateCVsPositive,width=142))
    buttons.append(cmds.button(label="RotateCVs -",c=RotateCVsNegative,width=142))
    buttons.append(cmds.button(label="Flip Curve Normal",c=FlipCurveNormal,width=142))
    cmds.setParent("..")

    cmds.separator(height=3, style='none')


    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Lock Curves",c=partial(DisplayObjects,'curves','lock'),width=105))
    buttons.append(cmds.button(label="Lock Meshs",c=partial(DisplayObjects,'meshs','lock')))    
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Unlock Curves",c=partial(DisplayObjects,'curves','unlock'),width=105))
    buttons.append(cmds.button(label="Unlock Meshs",c=partial(DisplayObjects,'meshs','unlock')))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Hide Curves",c=partial(DisplayObjects,'curves','hide'),width=105))
    buttons.append(cmds.button(label="Hide Meshs",c=partial(DisplayObjects,'meshs','hide')))    
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Show Curves",c=partial(DisplayObjects,'curves','show'),width=105))
    buttons.append(cmds.button(label="Show Meshs",c=partial(DisplayObjects,'meshs','show')))
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    buttons.append(cmds.button(label="Clean Scene",c=ClearAllLoft,width=105))
    cmds.setParent("..")

    cmds.rowColumnLayout(numberOfColumns=1)
    UIs["ratioCurve"] = cmds.gradientControlNoAttr("myGradient",width=350,height=120,enable=True,asString="0,0,2,1,1,2",
        changeCommand=lambda *args: print(
            cmds.gradientControlNoAttr("myGradient", q=True, asString=True)
        )
    )
    buttons.append(cmds.button(label="Skin Skirt",c=partial(AutoSkin,"skirt")))
    cmds.setParent("..")

    cmds.setParent("..")#--

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



def MakeLive(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        cmds.makeLive(objs)

def ExitLive(*arr):
    cmds.makeLive(none=True)

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
        CorrectCurveAxis(obj)
    cmds.select(objs)

def DrawCurve(*arr):
    d = 3
    bez=False
    ctx_name = "myCurveEPContext"    
    if not cmds.contextInfo(ctx_name, exists=True):
        cmds.curveEPCtx(name=ctx_name, d=d, bez=bez)
    else:
        cmds.curveEPCtx(ctx_name, edit=True, d=d, bez=bez)    
    cmds.setToolTo(ctx_name)

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

def GetPerpendicular(data):
    center = data['center']
    positions = data['positions']
    vector = data['vector']
    best_dot = float('inf')
    best_index = None
    for i, pos in enumerate(positions):
        vec = (pos - center).normalize()
        dot = abs(vec * vector)
        if dot < best_dot:
            best_dot = dot
            best_index = i
    return(positions[best_index])

def GetNormalFromVectors(data):
    vector1 = data['v1']
    vertor2 = data['v2']
    vector3 = data['v3']
    cmds.select(clear=True)
    jnt_center = cmds.joint(name="joint_center", position=(vector1.x,vector1.y,vector1.z))
    cmds.select(clear=True)
    jnt_far = cmds.joint(name="joint_far", position=(vertor2.x,vertor2.y,vertor2.z))
    cmds.select(clear=True)
    jnt_best = cmds.joint(name="joint_best", position=(vector3.x,vector3.y,vector3.z))
    cmds.aimConstraint(
        jnt_far,        
        jnt_center,     
        aimVector=[0,0, 1],         
        upVector=[1, 0, 0],          
        worldUpType="object",       
        worldUpObject=jnt_best      # hướng up theo joint_best
    )
    transform = cmds.xform(jnt_center, q=True, ws=True, m=True) 
    cmds.delete([jnt_far,jnt_center,jnt_best])
    return(transform)

def GetNormalFromObjs(verts):
    positions = GetPositions(verts)
    center = GetCenter(verts)
    farthestVertex = GetFarthest(verts)
    farVertexVector = farthestVertex['vertexVector']
    perpendicularVertexVector = GetPerpendicular({
        'vector':farthestVertex['vectorFromCenter'],
        'positions':positions,
        'center':center,
    })
    return(GetNormalFromVectors({'v1':center,'v2':farVertexVector,'v3':perpendicularVertexVector}))

def CreatePlane(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        martrix = GetNormalFromObjs(objs)
        farthestVertexSource = GetFarthest(objs)['distance']
        plane, poly_node = cmds.polyPlane(name="myPlane", w=farthestVertexSource+1, h=farthestVertexSource+1, sx=1, sy=1)
        cmds.xform(plane, ws=True, matrix=martrix)
        


def CorrectCurveAxis(curve):    
    cvs = cmds.ls(curve+".cv[*]", fl=True)
    matrix = GetNormalFromObjs(cvs)
    original_positions = [cmds.xform(cv, worldSpace=True,query=True, translation=True) for cv in cvs]
    cmds.xform(curve, ws=True, m=matrix)
    for cv, pos in zip(cvs, original_positions):
        cmds.xform(cv, ws=True, t=pos)
    cmds.makeIdentity(curve, apply=True, t=True, r=False, s=False, n=0)
    return(curve)

def CorrectCurrentCurveAxis(*arr):
    objs = cmds.ls(selection=True)
    for obj in objs:
        CorrectCurveAxis(obj)
    cmds.select(objs)

def CreateCurve(*arr):
    raw_sel = cmds.ls(flatten=True, orderedSelection=True)
    objs = cmds.filterExpand(raw_sel, selectionMask=31)
    count = len(objs)
    positions = GetPositions(objs)    
    curve = cmds.circle(name='NLTA_Curve' + "#", radius=1, sections=count)[0]
    cvs = [f"{curve}.cv[{i}]" for i in range(count)]
    for i in range(count):
        cmds.xform(cvs[i], worldSpace=True, translation=positions[i])
    CorrectCurveAxis(curve)

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




def SelectNearPlane(*arr):
    objs =  cmds.ls(selection=True)
    meshA = objs[1]
    meshB = objs[0]
    threshold=1
    close_curve=True
    # Step 1: Get vertex of meshA near meshB
    cpm = cmds.createNode("closestPointOnMesh")
    shapeB = cmds.listRelatives(meshB, shapes=True, fullPath=True)[0]
    cmds.connectAttr(f"{shapeB}.worldMesh[0]", f"{cpm}.inMesh", force=True)
    cmds.connectAttr(f"{meshB}.worldMatrix[0]", f"{cpm}.inputMatrix", force=True)

    verts = cmds.ls(f"{meshA}.vtx[*]", fl=True)
    close_verts = []

    for v in verts:
        pos = cmds.pointPosition(v, world=True)
        cmds.setAttr(f"{cpm}.inPosition", *pos, type="double3")
        closest = cmds.getAttr(f"{cpm}.position")[0]
        dist = math.sqrt(sum((pos[i] - closest[i]) ** 2 for i in range(3)))
        if dist <= threshold:
            close_verts.append((v, pos))
    
    cmds.delete(cpm)

    if len(close_verts) < 3:
        cmds.warning("Không tìm được đủ điểm giao để tạo curve.")
        return None

    # Step 2: Tính tâm & normal để sắp theo góc
    positions = [om.MVector(p[1]) for p in close_verts]
    center = sum(positions, om.MVector(0,0,0)) / len(positions)

    # Ước lượng normal từ mặt B
    shapeFn = om.MFnMesh(om.MSelectionList().add(meshB).getDagPath(0))
    normal = om.MVector(0, 0, 0)
    for p in positions:
        p = om.MPoint(p)  # ép kiểu nếu chưa phải MPoint
        point, faceId = shapeFn.getClosestPoint(p, space=om.MSpace.kWorld)
        face_normal = shapeFn.getPolygonNormal(faceId, om.MSpace.kWorld)
        normal += face_normal
    normal.normalize()

    # Xây hệ trục trên mặt phẳng
    x_axis = normal ^ om.MVector(0, 1, 0)
    if x_axis.length() < 1e-3:
        x_axis = normal ^ om.MVector(1, 0, 0)
    x_axis.normalize()
    y_axis = normal ^ x_axis
    y_axis.normalize()

    # Sắp điểm theo góc
    angle_point = []
    for v, pos in close_verts:
        vec = om.MVector(pos) - center
        x = vec * x_axis
        y = vec * y_axis
        angle = math.atan2(y, x)
        angle_point.append((angle, pos))

    angle_point.sort()
    ordered_points = [p for a, p in angle_point]

    # Step 3: Tạo curve
    curve = cmds.curve(p=[(p[0], p[1], p[2]) for p in ordered_points], d=3)
    if close_curve:
        cmds.closeCurve(curve, preserveShape=True, replaceOriginal=True)
    return curve

def ConvertEdgeToCurve(*arr):
    cmds.polyToCurve(form=0,degree=3,conformToSmoothMeshPreview=True)

def FlipLoftNormal(*arr):
    objs = cmds.ls(selection=True)
    if objs:
        lofData = GetLoftData(objs[0])
        cmds.reverseSurface(cmds.ls(lofData['loft'])[0], direction=0, ch=1)

def DisplayObjects(type,action,*arr):
    attrData = None
    if action == 'hide':
        attrData = {'visibility':0,}
    elif action == 'show':
        attrData = {'visibility':1,}
    elif action == 'lock':
        attrData = {'overrideEnabled':1,'overrideDisplayType':2}
    elif action == 'unlock':
        attrData = {'overrideEnabled':1,'overrideDisplayType':0}
    if attrData:
        objs = cmds.ls(type='loft')
        for obj in objs:
            if cmds.attributeQuery(loftAttr, node=obj, exists=True):
                data = GetLoftData(obj)
                poly = cmds.ls(data['poly'])
                curves = cmds.ls(data['curves'])
                if type == 'curves':
                    targetObjs = curves
                elif type == 'meshs':
                    targetObjs = poly
                for targetObj in targetObjs:
                    for key in attrData:
                        cmds.setAttr(targetObj+'.'+key,attrData[key])

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

def RebuildCurves(curves):
    spans=16
    for c in curves:
        cmds.delete(c, ch=True)  # ✅ Xóa history trước khi rebuild
        cmds.rebuildCurve(c, ch=False, rpo=True, rt=0,
                          end=1, kr=0, kcp=0, kep=1, d=3, s=spans)

def AlignCurvesDirection(curves):
    def get_tangent(curve):
        p0 = om.MVector(cmds.pointPosition(f"{curve}.cv[0]", w=True))
        p1 = om.MVector(cmds.pointPosition(f"{curve}.cv[1]", w=True))
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
    
def CreateLoft(*arr):
    ClearAllLoft()
    curves = cmds.ls(selection=True, type='transform')
    objsSave = curves.copy()
    if len(curves) < 2:
        cmds.warning("Chọn ít nhất 2 curve.")
        return
    CleanCurve(curves)
    result = cmds.loft(curves,ch=True,u=False,c=False,ar=False,d=3,ss=1,rn=False,po=0)
    surface = result[0]
    cmds.setAttr(surface+".hiddenInOutliner", 1)
    cmds.setAttr(surface+".visibility",0)
    objsSave.extend(result)
    poly = cmds.nurbsToPoly(
        surface,
        mnd=1,     # Match Normal Direction
        ch=1,      # Keep history
        f=2,       # Format: quads by number
        pt=1,      # Polygon type: quads
        pc=200,    # Polygon count target (for control)
        chr=0.99,  # chord height ratio
        ft=1,      # fit tolerance
        mel=1,     # merge edge length
        d=1,       # Use chord height
        ut=1,      # Use U divisions
        un=20,     # U number
        vt=1,      # Use V divisions
        vn=20,     # V number
        uch=0,     # use chord height in U (off)
        ucr=0,     # uniform chord ratio in U (off)
        cht=0.2,   # chord height
        es=0,      # edge swap (off)
        ntr=0,     # not trim
        mrt=0,     # merge trimmed surface (off)
        uss=1      # use surface span
    )[0]
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




##################################################### AUTO SKIN



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
    """
    # SMOOTH CHILDREN
    for jnt in jnts:
        children = data["edgePerpendicularChildrenOrder"][jnt]
        
        for child in children:            
            parent =  cmds.listRelatives(child,parent=True)[0]
            grandChild = cmds.listRelatives(child,children=True)[0]
            if grandChild not in data["edgePerpendicularChildrenOrder"]:
                edgeEnd = data["edgePerpendicularEnd"][jnt]
            else:
                edgeEnd = data["edgePerpendicularChildren"][jnt][grandChild]
            edgeStart = data["edgePerpendicularChildren"][jnt][parent]
            between = EdgesBetween(mesh,edgeStart,edgeEnd)
            
            LockJoint(mesh,[child,parent])
            
            for edge in between:
                verts = VertexFromEdges(mesh,GetEdgeLoop(mesh,edge))
                ratio = EdgeRatioBetweenEdges(mesh,edge,edgeStart,edgeEnd)
                ratio = GetGradientValue(UIs["ratioCurve"],ratio)   
                for vert in verts:
                    jntWeight = cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transform=parent,
                        query=True
                    )
                    jntTargetWeight = cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transform =child,
                        query=True
                    )
                    totalWeight =  jntWeight + jntTargetWeight
                    jntWeightValue = totalWeight * ratio
                    jntTargetWeightValue = totalWeight * (1 - ratio)
                    cmds.skinPercent(
                        skinData["skinCluster"],
                        vert,
                        transformValue=[
                            (parent,jntTargetWeightValue),
                            (child,jntWeightValue)
                        ]
                    )
    """     
                   
           