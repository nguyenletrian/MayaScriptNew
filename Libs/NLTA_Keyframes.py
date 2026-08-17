import importlib
import maya.cmds as cmds

import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)



session = {}

### KEYFRAMES
def CreateKeyframe(keyInput,*arr):
    animationDistance = cmds.intSliderGrp(
        keyInput["ui"],
        query=True,
        value=True,
    )

    originTime = cmds.currentTime(query=True)
    currentTool = cmds.currentCtx()
    if currentTool == 'artAttrSkinContext':
        objs = [cmds.connectionInfo(skinSession['skinCluster']+".paintTrans",sourceFromDestination=True).split(".")[0]]
    else:
        objs = cmds.ls(selection=True)
    if objs:
        jointAddKey = []        
        keySpace = keyInput['space']
        keyType = keyInput['type']
        keyInturn = keyInput['inturn']           
        for obj in objs:
            parent = cmds.listRelatives(obj,parent=True)
            if parent:
                parent = parent[0]
            cmds.select(clear=True)
            jointSpace = cmds.joint()
            cmds.addAttr(jointSpace,longName="NLTA_worldKeyframe",dt='string')
            cmds.setAttr(jointSpace+'.overrideEnabled',1)
            cmds.setAttr(jointSpace+'.overrideVisibility',0)
            cmds.setAttr(jointSpace+'.hiddenInOutliner',True)
            if parent:
                cmds.parent(jointSpace,parent)
            jointChild = cmds.joint()
            if not cmds.attributeQuery("NLTA_SourceJoint",node=obj, exists=True):
              cmds.addAttr(obj,longName="NLTA_SourceJoint",dt='string')
            cmds.setAttr(obj+".NLTA_SourceJoint",jointSpace, type="string")
      
            jointAddKey.append(jointChild)
            if keySpace == 'world':
                cmds.matchTransform(jointSpace,obj,pos=True)
            elif keySpace == 'local':
                cmds.matchTransform(jointSpace,obj,pos=True,rot=True)
            constraint = cmds.parentConstraint(jointChild,obj,mo=True)
            cmds.setAttr(jointSpace+'.visibility',0)
        if keyType == 'rotate':
            keyData = {
                "rx":[0,-90,0,90,0],
                "ry":[0,-90,0,90,0],
                "rz":[0,-90,0,90,0],
            }
        elif keyType == 'translate':
            keyData = {
                    "tx":[0,animationDistance*(-1),0,animationDistance,0],
                    "ty":[0,animationDistance*(-1),0,animationDistance,0],
                    "tz":[0,animationDistance*(-1),0,animationDistance,0],
            }
        for jointChild in jointAddKey:
            if keyInput['inturn'] == False:
                currentTime = originTime
            else:
                currentTime = cmds.currentTime(query=True)
            for key in keyData:
                keyArray = keyData[key]
                for keyValue in keyArray:
                    currentTime += 30
                    cmds.currentTime(currentTime)              
                    cmds.setKeyframe(jointChild, attribute=key,value=keyValue)

    cmds.select(jointAddKey)
    NLTA_General.FitRangeAnim()
    cmds.currentTime(originTime)
    cmds.playbackOptions(min=0)
    if currentTool == 'artAttrSkinContext':
        cmds.select(skinSession['mesh'])
    else:
        cmds.select(objs)
 
    
def ZoomRangeAnim(*arr):
    anim_curves = cmds.ls(type='animCurve') or []    
    if not anim_curves:
        cmds.warning("Haven't anim curve")
        return
    key_times = cmds.keyframe(anim_curves, q=True)
    
    if not key_times:
        cmds.warning("Haven't keyframe")
        return
    key_times = sorted(set(key_times))
    current = cmds.currentTime(q=True)
    start = None
    end = None    
    for i in range(len(key_times) - 1):
        if key_times[i] <= current <= key_times[i + 1]:
            start = key_times[i]
            end = key_times[i + 1]
            break    
    if start is None and len(key_times) > 1:
        if current < key_times[0]:
            start, end = key_times[0], key_times[1]
        elif current > key_times[-1]:
            start, end = key_times[-2], key_times[-1]    
    if start is not None and end is not None:
        cmds.playbackOptions(min=start, max=end)
        cmds.currentTime(current)
    else:
        cmds.warning("Can't find frame range")

def deleteSenceKeyframe(*attr):
    objs = cmds.ls()
    for i in objs:
        try:
            if cmds.attributeQuery("NLTA_SourceJoint",node=i,ex=True):
                cmds.deleteAttr(i+'.NLTA_SourceJoint')
        except:pass
        try:
            if cmds.attributeQuery("NLTA_worldKeyframe",node=i,ex=True):
                cmds.delete(i)
        except:pass
    cmds.currentTime(0)

def DeleteAttrKeyframes(*arr):
    sel = cmds.ls(selection=True)
    if sel:
        cmds.cutKey(sel, clear=True)