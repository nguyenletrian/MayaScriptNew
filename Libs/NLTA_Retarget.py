import maya.cmds as cmds
import maya.api.OpenMaya as om

### FUNCTIONS
def GetKey(attr, time):
    if not cmds.keyframe(attr, query=True, time=(time, time)):
        return None
    data = {}
    data["value"] = cmds.keyframe(attr, q=True, time=(time, time), valueChange=True)[0]
    data["inTangentType"] = cmds.keyTangent(attr, q=True, time=(time, time), inTangentType=True)[0]
    data["outTangentType"] = cmds.keyTangent(attr, q=True, time=(time, time), outTangentType=True)[0]
    data["inAngle"] = cmds.keyTangent(attr, q=True, time=(time, time), inAngle=True)[0]
    data["outAngle"] = cmds.keyTangent(attr, q=True, time=(time, time), outAngle=True)[0]
    data["inWeight"] = cmds.keyTangent(attr, q=True, time=(time, time), inWeight=True)[0]
    data["outWeight"] = cmds.keyTangent(attr, q=True, time=(time, time), outWeight=True)[0]
    data["weightedTangents"] = cmds.keyTangent(attr, q=True, weightedTangents=True)[0]


    return data

def GetKeyRange(objects=None):
    if not objects:
        objects = cmds.ls(dag=True, long=True) or []
    allKeys = []
    for obj in objects:
        keys = cmds.keyframe(obj, query=True, timeChange=True)
        if keys:
            allKeys.extend(keys)
    if not allKeys:
        return None
    return({"min":min(allKeys),"max":max(allKeys)})
    
def GetAllTimes(objects=None):
    if not objects:
        objects = cmds.ls(dag=True, long=True) or []
    keys = cmds.keyframe(objects, query=True, timeChange=True)
    if not keys:
        return []
    return sorted(set(keys))
    
def SimilarAxes(obj1, obj2, tolerance=0.999):
    def get_axes(obj):
        m = cmds.xform(obj, q=True, ws=True, matrix=True)
        m = om.MMatrix(m)
        return {
            "x": om.MVector(m[0], m[1], m[2]).normalize(),
            "y": om.MVector(m[4], m[5], m[6]).normalize(),
            "z": om.MVector(m[8], m[9], m[10]).normalize()
        }
    axes1 = get_axes(obj1)
    axes2 = get_axes(obj2)
    mapping = {}
    for a1_name, a1_vec in axes1.items():
        best_match = None
        best_dot = -1
        for a2_name, a2_vec in axes2.items():
            dot = a1_vec * a2_vec
            abs_dot = abs(dot)
            if abs_dot > best_dot:
                best_dot = abs_dot
                sign = 1 if dot >= 0 else -1
                best_match = [a2_name, sign]
        mapping[a1_name] = best_match
    return mapping

def BakeTransfromKeys(data):
    obj1 = data["obj1"]
    obj2 = data["obj2"]
    time = data["time"]
    mapping = SimilarAxes(obj1, obj2)
    for attr in ["translate","rotate","scale"]:
        for axis in ["x", "y", "z"]:
            src_attr = f"{obj1}.{attr}{axis.upper()}"
            target_axis, sign = mapping[axis]
            dst_attr = f"{obj2}.{attr}{target_axis.upper()}"
            key_data = GetKey(src_attr, time)
            if not key_data:
                continue
            value = key_data["value"] * sign
            cmds.setKeyframe(dst_attr, time=time, value=value)
            
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                weightedTangents=key_data["weightedTangents"]
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                inWeight=key_data["inWeight"],
                outWeight=key_data["outWeight"],
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),            
                inAngle=key_data["inAngle"] * sign,
                outAngle=key_data["outAngle"] * sign,
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                inTangentType=key_data["inTangentType"],
                outTangentType=key_data["outTangentType"],
            )    

def BakeTransformSameKeys(data):
    obj1 = data["obj1"]
    obj2 = data["obj2"]
    time = data["time"]
    mapping = SimilarAxes(obj1, obj2)
    cmds.matchTransform(obj2,obj1)
    for attr in ["translate","rotate","scale"]:
        for axis in ["x", "y", "z"]:
            src_attr = f"{obj1}.{attr}{axis.upper()}"
            target_axis, sign = mapping[axis]
            dst_attr = f"{obj2}.{attr}{target_axis.upper()}"            
            key_data = GetKey(src_attr, time)
            if not key_data:
                continue
            cmds.setKeyframe(dst_attr, time=time)           
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                weightedTangents=key_data["weightedTangents"]
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                inWeight=key_data["inWeight"],
                outWeight=key_data["outWeight"],
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),            
                inAngle=key_data["inAngle"] * sign,
                outAngle=key_data["outAngle"] * sign,
            )
            cmds.keyTangent(
                dst_attr,
                time=(time,time),
                inTangentType=key_data["inTangentType"],
                outTangentType=key_data["outTangentType"],
            )
            
"""
def BakeAttrsKeys(data):
    obj1 = data["obj1"]
    obj2 = data["obj2"]
    attrs = data["attrs"]
    time = data["time"]
    times = GetAllTimes([obj1])
    if not times:
        return
    mapping = SimilarAxes(obj1, obj2)
    for t in times:
        for attr in attrs:
            for axis in ["x", "y", "z"]:
                src_attr = f"{obj1}.{attr}{axis.upper()}"
                target_axis, sign = mapping[axis]
                dst_attr = f"{obj2}.{attr}{target_axis.upper()}"
                key_data = GetKey(src_attr, t)
                if not key_data:
                    continue                    
                value = key_data["value"] * sign
                cmds.setKeyframe(dst_attr, time=t, value=value)                
                cmds.keyTangent(
                    dst_attr,
                    time=(t, t),
                    inTangentType=key_data["inTangentType"],
                    outTangentType=key_data["outTangentType"],
                    inAngle=key_data["inAngle"],
                    outAngle=key_data["outAngle"],
                    inWeight=key_data["inWeight"],
                    outWeight=key_data["outWeight"],
                    weightedTangents=key_data["weightedTangents"]
                )
"""
def HierarchyToJoints(root, namespace="BakeAnimationJoints"):
    if not cmds.namespace(exists=namespace):
        cmds.namespace(add=namespace)
    rootName = root.split(":")[-1]
    objs = cmds.listRelatives(root, ad=True, fullPath=True) or []
    objs = objs[::-1]
    objs.insert(0, root)
    valid_objs = []
    for obj in objs:
        if cmds.nodeType(obj) == "mesh":
            continue
        if "Constraint" in cmds.nodeType(obj):
            continue
        valid_objs.append(obj)
    for obj in valid_objs:
        objParent = cmds.listRelatives(obj, parent=True, fullPath=True)
        objName = obj.split(":")[-1]
        jointName = f"{namespace}:{objName}"
        cmds.select(clear=True)
        jointNew = cmds.joint(name=jointName)
        constraint = cmds.parentConstraint(obj, jointNew, maintainOffset=False)[0]
        cmds.delete(constraint)
        cmds.makeIdentity(jointNew, apply=True, t=1, r=1, s=1, n=0, pn=1)
        if objParent:
            objParentName = objParent[0].split(":")[-1]
            parentName = f"{namespace}:{objParentName}"
            if cmds.objExists(parentName):
                cmds.parent(jointNew, parentName)
    return f"{namespace}:{rootName}"


def RotateOrderConnect(data,*arr):
    source = data["source"]
    target = data["target"]

    if cmds.objExists(source) and cmds.objExists(target):
        grpParentName = "grp_"+source+"_"+target+"_rotateOrderParent"
        if cmds.objExists(grpParentName):
            cmds.delete(grpParentName)
        grpOffsetName = "grp_"+source+"_"+target+"_rotateOrderOffset"
        refName = "grp_"+source+"_"+target+"_rotateOrderRef"       

        grpParent = cmds.group(n=grpParentName,empty=True)
        cmds.matchTransform(grpParentName,source,rot=True,pos=True)

        ref = cmds.group(n=refName,empty=True)
        grpOffset = cmds.group(ref,n=grpOffsetName)
        cmds.matchTransform(grpOffset,target,rot=True,pos=True)
        cmds.parent(grpOffset,grpParent)

        cons = cmds.parentConstraint(source,grpParent,mo=True)
        #cmds.parent(cons,grpParent)
        return(refName)

def FindParent(obj,targets):
    targets_set = set(targets)
    current = obj
    while True:
        parent = cmds.listRelatives(current, parent=True, fullPath=True)
        if not parent:
            return None
        parent = parent[0]
        if parent in targets_set:
            return parent
        current = parent

def GetChildren(data,*arr):
    root = data["root"]
    ctrlType = data["type"]
    returnData = []
    if ctrlType == "nurbsCurve":        
        children = cmds.listRelatives(root,ad=True,type=ctrlType)
        for child in children:
            parent = cmds.listRelatives(child,parent=True)[0]
            if cmds.objectType(parent)!="ikEffector":
                if parent not in returnData:
                    returnData.append(parent)     
    else:
        children = cmds.listRelatives(root,ad=True,type=ctrlType)
        for child in children:
            returnData.append(child)
    return(returnData)     



