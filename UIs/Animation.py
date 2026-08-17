import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import importlib
import math
import json
from functools import partial
import maya.api.OpenMaya as om
import NLTA_General
importlib.reload(NLTA_General)


########### SCRIPT JOB
session = {
    'timeClipboard':None
} 
def DetectASRig():
    global session
    objs = cmds.ls(selection=True)
    if objs:
        node = pm.PyNode(objs[0])
        if node.namespace() != "":
            session['namespace'] =  node.namespace()+ ":"
            session['bodyControls'] =  node.namespace()+ ":" + "ControlSet"
            session['faceControls'] =  node.namespace()+ ":" + "FaceControlSet"
        else:
            session['namespace'] = ""
            session['bodyControls'] = "ControlSet"
            session['faceControls'] = "FaceControlSet"


def OpenSkinToolListen():
    jobs = cmds.scriptJob(listJobs=True)
    for job in jobs:
        if 'DetectCurrentSkin' in job:
            jobID = int(job.split(":")[0])
            cmds.scriptJob(kill=jobID, force=True)
    cmds.scriptJob(event=["SelectionChanged",DetectASRig], protected=True)
OpenSkinToolListen()
###################



def CreateUI(data):  
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
    cmds.rowColumnLayout(numberOfColumns=1)#--

    #####

    
    cmds.button(label="Select Controls",c=SelectControls,width=98)
    cmds.button(label="Create Keyframe",c=CreateKeyframe,width=98)
    cmds.button(label="Copy Pose",c=CopyPose,width=98)
    cmds.button(label="Paste Pose",c=PastePose,width=98)
    cmds.button(label="Create Overlap",c=CreateOverLap,width=98)
    cmds.button(label="Delete Current Keyframe",c=DeleteCurrentKeyframe,width=98)
    cmds.button(label="Delete all Keyframe",c=DeleteAllKeyframe,width=98)  
    cmds.button(label="Back Origin",c=BackOrigin,width=98)
    cmds.button(label="Loop",c=LoopAnim,width=98)
    """
    cmds.rowColumnLayout(numberOfColumns=4,w=450)#item
    cmds.button(label="Create Anim Ref",c=MatchFbxAnimToAsFbx,width=98)
    cmds.button(label="Match Anim Ref",c=MatchAsToAnimRef,width=98)
    
    cmds.button(label="CopyPose",c=CopyPose,width=98)
    cmds.button(label="PastPose",c=PastePose,width=98)
    cmds.button(label="DeleteCurrentKey",c=DeleteCurrentKey,width=98)
    cmds.button(label="Loop Anim",c=LoopAnim,width=98)
    cmds.button(label="Origin",c=OriginPose,width=98)

    cmds.button(label="Copy Fbx Keys",c=partial(CopyFbxKeys,5),width=98)
    cmds.button(label="Clear All Fbxs",c = ClearAnimFbxFiles,width=98)
    #cmds.button(label="Fix Anim Rang",c = NLTA_skinning.fitRangeAnim,w=98)
    cmds.button(label="Rename NLTA",c = RenameNLTA,w=98) 
    cmds.setParent('..')
    
    cmds.rowColumnLayout(numberOfColumns=4,w=450)
    cmds.button(label="Previous File",c = PreviousFile,w=98)          
    cmds.button(label="Match & Create Key",c = MatchAndCreateKey,w=98) 
    cmds.button(label="Next File",c = NextFile,w=98)
    cmds.button(label="Stop",c = Stop,w=98)   
    cmds.setParent('..')
    cmds.rowColumnLayout(numberOfColumns=4,w=450)#item
    cmds.button(label="Middle Keys",c = CreateMiddleKeys,w=98)  
    cmds.setParent('..')
    cmds.rowColumnLayout(numberOfColumns=4,w=450)#item
    cmds.textField('fileName',width=170)
    cmds.setParent('..')
    """

    cmds.setParent("..")#-

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

def GetCurveInSet(name,*arr):
    if not cmds.objExists(name):
        print(f"Set '{name}' does not exist.")
        return []
    members = cmds.sets(name, q=True)
    curves = []
    for obj in members:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.objectType(shape) == 'nurbsCurve':
                curves.append(obj)
                break  # Chỉ cần 1 shape là nurbsCurve thì lấy object
    return curves

def SelectControls(*arr):
    bodyControls = GetCurveInSet(session['bodyControls'])
    faceControls = GetCurveInSet(session['faceControls'])
    cmds.select(bodyControls)
    cmds.select(faceControls,add=True)

def CreateKeyframe(*arr):
    for control in cmds.ls(selection=True):
        cmds.setKeyframe(control)

poseData = {}
def CopyPose(*arr):
    global poseData
    ikData = {
        ':IKArm_R':':FKScapula_R',
        ':IKArm_L':':FKScapula_L',
        ':IKLeg_L':':RootX_M',
        ':IKLeg_R':':RootX_M',
    }
    selection = cmds.ls(selection=True)
    for control in cmds.ls(selection=True):
        if not NLTA_General.checkSubString([control,[':IKLeg_R',':IKLeg_L',':IKArm_R',':IKArm_L']]):
            poseData[control] = {}
            for attr in cmds.listAttr(control, keyable=True, unlocked=True) or []: 
                poseData[control][attr] = cmds.getAttr(control+'.'+attr)
        else:
            poseData[control] = {}
            for ik in ikData:
                if ik in control:
                    parent = cmds.ls('*'+ikData[ik])[0]
                    cmds.select(clear=True)
                    parentJoint = cmds.joint(n='NLTA_JointParentTemp')
                    childJoint = cmds.joint(n='NLTA_JointChildTemp')
                    cmds.matchTransform(parentJoint,parent,pos=True,rot=True)
                    cmds.matchTransform(childJoint,control,pos=True,rot=True)
                    for attr in ['tx','ty','tz','rx','ry','rz']:
                        poseData[control][attr] = cmds.getAttr(childJoint+'.'+attr)
                    cmds.delete(parentJoint)
    cmds.select(selection)

def PastePose(*arr):
    ikData = {
        ':IKArm_R':':FKScapula_R',
        ':IKArm_L':':FKScapula_L',
        ':IKLeg_L':':RootX_M',
        ':IKLeg_R':':RootX_M',
    }
    selection = cmds.ls(selection=True)
    for control in cmds.ls(selection=True):
        if control in poseData:
            if not NLTA_General.checkSubString([control,[':IKLeg_R',':IKLeg_L',':IKArm_R',':IKArm_L']]):
                for attr in poseData[control]:
                    cmds.setAttr(control+"."+attr,poseData[control][attr])
                    cmds.setKeyframe(control+'.'+attr)
            else:
                for ik in ikData:
                    if ik in control:
                        parent = cmds.ls('*'+ikData[ik])[0]
                        cmds.select(clear=True)
                        parentJoint = cmds.joint(n='NLTA_JointParentTemp')
                        childJoint = cmds.joint(n='NLTA_JointChildTemp')
                        cmds.matchTransform(parentJoint,parent,pos=True,rot=True)
                        for attr in ['tx','ty','tz','rx','ry','rz']:                            
                            cmds.setAttr(childJoint+'.'+attr,poseData[control][attr])
                        cmds.matchTransform(control,childJoint,pos=True,rot=True)
                        cmds.delete(parentJoint)
    cmds.select(selection)

def CreateOverLap(*arr):    
    offset_frame = 3
    velocity_scale = .0001
    #offset_frame = 3
    #velocity_scale = 1
    current_frame = cmds.currentTime(q=True)
    selected = cmds.ls(selection=True)

    if not selected:
        print("⚠️ Không có object nào được chọn.")
        return

    for obj in selected:
        keyable_attrs = cmds.listAttr(obj, keyable=True, unlocked=True) or []

        for attr in keyable_attrs:
            # Bỏ qua scale và visibility

            full_attr = f"{obj}.{attr}"
            try:
                # Lấy giá trị tại các frame quanh hiện tại để tính velocity
                val_prev = cmds.getAttr(full_attr, time=current_frame - 1)
                val_next = cmds.getAttr(full_attr, time=current_frame + 1)
                val_now  = cmds.getAttr(full_attr, time=current_frame)
            except:
                continue  # Bỏ qua nếu không lấy được giá trị

            # Bỏ qua nếu không có sự thay đổi
            if val_prev == val_next == val_now:
                continue

            # Tính velocity-based offset
            velocity = (val_next - val_prev) / 2.0
            offset = velocity * velocity_scale

             # Đặt keyframe trước và sau với offset
            cmds.setKeyframe(full_attr, time=(current_frame - offset_frame,), value=val_now + offset)
            cmds.setKeyframe(full_attr, time=(current_frame,), value=val_now)
            cmds.setKeyframe(full_attr, time=(current_frame + offset_frame,), value=val_now - offset)

            # Sửa tangent để mượt hơn
            cmds.keyTangent(full_attr, time=(current_frame - offset_frame,), outTangentType='spline')
            cmds.keyTangent(full_attr, time=(current_frame + offset_frame,), inTangentType='spline')

            print(f"✅ {full_attr}: Offset ±{round(offset, 3)}")

    print("🎉 Đã tạo overlap keyframes.")



def BackOrigin(*arr):
    for control in cmds.ls(selection=True):
        for attr in cmds.listAttr(control, keyable=True, unlocked=True) or []:
            defaultValue = cmds.attributeQuery(attr.split('.')[-1], node=control, listDefault=True)[0]
            cmds.setAttr(control+'.'+attr,defaultValue)

def DeleteCurrentKeyframe(*arr):
    selected = cmds.ls(selection=True)
    if not selected:
        print("⚠️ Không có object nào được chọn.")
        return

    current_time = cmds.currentTime(q=True)

    for obj in selected:
        anim_attrs = cmds.listAnimatable(obj)
        if not anim_attrs:
            continue

        for attr in anim_attrs:
            try:
                # Kiểm tra xem có key tại frame hiện tại không
                key_times = cmds.keyframe(attr, time=(current_time,), query=True, timeChange=True)
                if key_times:
                    cmds.cutKey(attr, time=(current_time,))
            except:
                continue

def DeleteAllKeyframe(*arr):
    for control in cmds.ls(selection=True):
        for attr in cmds.listAttr(control, keyable=True, unlocked=True) or []:
            defaultValue = cmds.attributeQuery(attr.split('.')[-1], node=control, listDefault=True)[0]
            cmds.setAttr(control+'.'+attr,defaultValue)
            cmds.cutKey(control+'.'+attr, clear=True)

def LoopAnim(*arr):
    selection = cmds.ls(selection=True)
    for control in selection:
        for attr in cmds.listAttr(control, keyable=True, unlocked=True) or []:
            cmds.setInfinity(control, attribute=attr,poi='cycle',pri='cycle')   


######################################################################
"""
poseData = {}
def CopyPose(*arr):
    global poseData
    ikData = {
        ':IKArm_R':':FKScapula_R',
        ':IKArm_L':':FKScapula_L',
        ':IKLeg_L':':RootX_M',
        ':IKLeg_R':':RootX_M',
    }
    selection = cmds.ls(selection=True)
    for control in cmds.ls(selection=True):
        if not NLTA_General.checkSubString([control,[':IKLeg_R',':IKLeg_L',':IKArm_R',':IKArm_L']]):
            poseData[control] = {}
            for attr in ['tx','ty','tz','rx','ry','rz']:
                keyable = cmds.getAttr(control+'.'+attr,k=True)
                if cmds.getAttr(control+'.'+attr,k=True) and cmds.getAttr(control+'.'+attr)!=0:
                    poseData[control][attr] = cmds.getAttr(control+'.'+attr)
        else:
            poseData[control] = {}
            for ik in ikData:
                if ik in control:
                    parent = cmds.ls('*'+ikData[ik])[0]
                    cmds.select(clear=True)
                    parentJoint = cmds.joint(n='NLTA_JointParentTemp')
                    childJoint = cmds.joint(n='NLTA_JointChildTemp')
                    cmds.matchTransform(parentJoint,parent,pos=True,rot=True)
                    cmds.matchTransform(childJoint,control,pos=True,rot=True)
                    for attr in ['tx','ty','tz','rx','ry','rz']:
                        poseData[control][attr] = cmds.getAttr(childJoint+'.'+attr)
                    cmds.delete(parentJoint)
    cmds.select(selection)

def PastePose(*arr):
    ikData = {
        ':IKArm_R':':FKScapula_R',
        ':IKArm_L':':FKScapula_L',
        ':IKLeg_L':':RootX_M',
        ':IKLeg_R':':RootX_M',
    }
    selection = cmds.ls(selection=True)
    for control in cmds.ls(selection=True):
        if control in poseData:
            if not NLTA_General.checkSubString([control,[':IKLeg_R',':IKLeg_L',':IKArm_R',':IKArm_L']]):
                for attr in poseData[control]:
                    cmds.setAttr(control+"."+attr,poseData[control][attr])
                    cmds.setKeyframe(control+'.'+attr)
            else:
                for ik in ikData:
                    if ik in control:
                        parent = cmds.ls('*'+ikData[ik])[0]
                        cmds.select(clear=True)
                        parentJoint = cmds.joint(n='NLTA_JointParentTemp')
                        childJoint = cmds.joint(n='NLTA_JointChildTemp')
                        cmds.matchTransform(parentJoint,parent,pos=True,rot=True)
                        for attr in ['tx','ty','tz','rx','ry','rz']:                            
                            cmds.setAttr(childJoint+'.'+attr,poseData[control][attr])
                        cmds.matchTransform(control,childJoint,pos=True,rot=True)
                        cmds.delete(parentJoint)
    cmds.select(selection)

def DeleteCurrentKey(*arr):
    currentTime = cmds.currentTime(query=True)
    for control in cmds.ls(selection=True):
        for attr in ['tx','ty','tz','rx','ry','rz']:
            cmds.cutKey(control, attribute=attr, time=(currentTime, currentTime))

def LoopAnim(*arr):
    selection = cmds.ls(selection=True)
    for control in selection:
        for attr in ['tx','ty','tz','rx','ry','rz']:
            cmds.setInfinity(control, attribute=attr,poi='cycle',pri='cycle')   
        if NLTA_General.checkSubString([control,[':RootX_M',':IKLeg_R',':IKLeg_L',':IKArm_R',':IKArm_L']]):
            cmds.setInfinity(control, attribute='tz',poi='cycleRelative',pri='cycleRelative')

def OriginPose(*arr):
    selection = cmds.ls(selection=True)
    for control in selection:
        for attr in ['tx','ty','tz','rx','ry','rz']:
            if cmds.getAttr(control+'.'+attr,k=True):
                cmds.setAttr(control+'.'+attr,0)

def DeleteKeyframe(*arr):
    selection = cmds.ls(selection=True)
    for control in selection:
        for attr in ['tx','ty','tz','rx','ry','rz']:
            if cmds.getAttr(control+'.'+attr,k=True):
                cmds.cutKey(control, attribute=attr)



def Stop(*arr):
    cmds.play(state=False)

def CreateMiddleKeys(*arr):
    selection =  cmds.ls(selection=True)
    keyArray = []
    for control in selection:
        keys = cmds.keyframe(control, query=True, timeChange=True)
        if keys:
            for key in keys:
                if key not in keyArray:
                    keyArray.append(key)
    sorted(keyArray)
    if keyArray:
        for key in keyArray:
            currentIndex = keyArray.index(key)
            nextIndex = (keyArray.index(key) + 1)
            if len(keyArray) > nextIndex:
                frameAverage = math.ceil((keyArray[currentIndex] + keyArray[nextIndex])/2)
                cmds.currentTime(frameAverage)
                MatchAsToAnimRef()
                for control in selection:
                    cmds.select(control)
                    CreateKeyframe()

    cmds.select(selection)


################################################################    

def ImportDataForAnimation(url,*arr):
    pattern = "D:/MIXAMO/MixamoRig_asPattern.txt"
    global animationSession
    if url == None:
        url = pattern
    else:
        url = pm.fileDialog2(fileMode=1)
        if url:
            url = url[0]
        else:
            url = pattern
        
    if url:
        myFile = open(url,'r')
        myObject = myFile.read()
        myFile.close()
        data = json.loads(myObject)
        if int(cmds.about(version=True)) < 2022:
            data = json.loads(myObject,'utf-8')
        else:
            data = json.loads(myObject)
        for a in data:
            animationSession[a] = data[a]
        print('Đã nhập dữ liệu')

def MatchFbxAnimToAsFbx(*arr):
    ImportDataForAnimation(None)
    selection = cmds.ls(selection=True)[0]
    nameSpace = selection.split(":")[0]
    if 'connectAsFbx' in animationSession:
        for a in range(len(animationSession['connectAsFbx'])):
            rigFbx = nameSpace+":"+animationSession["connectAsFbx"][a][1]
            animationFbx = (animationSession["connectAsFbx"][a][1]).replace("NLTA_",'')
            if cmds.objExists(rigFbx) and cmds.objExists(animationFbx):
                cmds.matchTransform(animationFbx,rigFbx,pos=True,rot=True)

    CreateObjectRefFromAnim()

def CreateObjectRefFromAnim(*arr):
    selection = cmds.ls(selection=True)[0]
    nameSpace = selection.split(":")[0]
    if "connectAsFbx" in animationSession:
        if not cmds.objExists('GroupContentObjectRef'):
            groupContent = cmds.group(n='GroupContentObjectRef',empty=True)
        else:
            cmds.delete('GroupContentObjectRef')
            groupContent = cmds.group(n='GroupContentObjectRef',empty=True)
        prefix = 'GroupObjectRef'
        stringArray = []
        poleData = {
            'RightLeg':['PoleLeg_R'],
            'LeftLeg':['PoleLeg_L'],
            'RightForeArm':['PoleArm_R'],
            'LeftForeArm':['PoleArm_L'],
        }
        for a in range(len(animationSession["connectFbxAs"]["pair"])):
            animationFbx = (animationSession["connectFbxAs"]["pair"][a][0]).replace("NLTA_",'')
            controlOrigin = animationSession["connectFbxAs"]["pair"][a][1]
            rigControl = nameSpace+":"+controlOrigin
            if cmds.objExists(rigControl) and cmds.objExists(animationFbx):                
                group_parent = (prefix+"_"+animationFbx+"_"+rigControl+"_"+"parent").replace(':','')
                if cmds.objExists(prefix+"_"+animationFbx+"_"+rigControl+"_"+"parent"):
                    cmds.delete(prefix+"_"+animationFbx+"_"+rigControl+"_"+"parent")
                group_parent = (prefix+"_"+animationFbx+"_"+rigControl+"_"+"parent").replace(':','')
                group_offset = (prefix+"_"+animationFbx+"_"+rigControl+"_"+"offset").replace(':','')
                locator1 = (prefix+"_"+animationFbx+"_"+rigControl+"_"+"loc1").replace(':','')
                group_parent = cmds.group(n=group_parent,empty=True)

                cmds.matchTransform(group_parent,animationFbx,rot=True,pos=True)
                cmds.select(clear=True)
                locator1 = cmds.group(n=locator1,empty=True)
                group_offset = cmds.group(locator1,n=group_offset)
                cmds.matchTransform(group_offset,rigControl,rot=True,pos=True)
                cmds.parent(group_offset,group_parent)
                parentConstraint = cmds.parentConstraint(animationFbx,group_parent,mo=True)             
                cmds.parent(parentConstraint,groupContent)
                cmds.parent(group_parent,groupContent)
                stringArray.append(locator1+';'+rigControl)
                if controlOrigin in poleData:
                    poleData[controlOrigin].append(animationFbx)
        for key in poleData:
            control = nameSpace+":"+poleData[key][0]
            animationFbx = key
            if cmds.objExists(control):
                locator = cmds.group(n=control+'_poleVector',empty=True)
                offset = cmds.group(n=control+'_poleVector_offset',empty=True)
                cmds.matchTransform(locator,control,rot=True,pos=True)
                cmds.matchTransform(offset,animationFbx,rot=True,pos=True)
                parentConstaintTemp = cmds.parentConstraint(animationFbx,offset,mo=True)
                cmds.parent(locator,offset)
                cmds.parent(parentConstaintTemp,groupContent)
                cmds.parent(offset,groupContent)
                stringArray.append(locator+';'+control)

        MainCtrl = cmds.ls('*:Main')[0]
        if not cmds.attributeQuery('AS_Ctrl',exists=True,node=MainCtrl):
            pm.mel.eval('addAttr -ln "AS_Ctrl"  -dt "string"  '+MainCtrl+';')
        pm.mel.eval('setAttr -type "string" '+MainCtrl+'.AS_Ctrl "'+("|").join(stringArray)+'";')

def GetMatchData(*arr):
    returnData = []
    MainCtrl = cmds.ls('*:Main')[0]
    if cmds.attributeQuery('AS_Ctrl',exists=True,node=MainCtrl):
        string = cmds.getAttr(MainCtrl+'.AS_Ctrl')
        pairs = string.split("|")
        for pair in pairs:
            pairTemp = pair.split(';')
            joint_ = pairTemp[0]
            control = pairTemp[1]
            returnData.append([joint_,control])
    return(returnData)

def MatchAsToAnimRef(*arr):
    MainCtrl = cmds.ls('*:Main')[0]
    if cmds.attributeQuery('AS_Ctrl',exists=True,node=MainCtrl):
        string = cmds.getAttr(MainCtrl+'.AS_Ctrl')
        pairs = string.split("|")
        for pair in pairs:
            pairTemp = pair.split(';')
            joint_ = pairTemp[0]
            control = pairTemp[1]
            if cmds.objExists(control) and cmds.objExists(joint_):
                if NLTA_General.checkSubString([control,[":RootX_M",':PoleArm_R',':PoleArm_L',':PoleLeg_R',':PoleLeg_L']]):
                    cmds.matchTransform(control,joint_,pos=True)
                elif NLTA_General.checkSubString([control,[':IKLeg_L',':IKLeg_R',':IKArm_R',':IKArm_L']]):
                    cmds.matchTransform(control,joint_,pos=True,rot=True)
                elif NLTA_General.checkSubString([control,[':Main']]):
                    pass
                else:
                    cmds.matchTransform(control,joint_,rot=True)


def GetFbxAnimRange(*arr):
    selection =  cmds.ls(selection=True)[0]
    if selection:
        joint = selection
        keyframes = cmds.keyframe(joint, attribute='rx', query=True, timeChange=True)
        maxFrame = max(keyframes) if keyframes else None
        minFrame = min(keyframes) if keyframes else None
        return([int(minFrame),int(maxFrame)])

def CopyFbxKeys(increase,*arr):
    frameRange = GetFbxAnimRange()
    SelectControls()
    for frame in range(frameRange[0],frameRange[1],increase):
        cmds.currentTime(frame)
        MatchAsToAnimRef()
        CreateKeyframe()
    cmds.currentTime(frameRange[1])
    MatchAsToAnimRef()
    CreateKeyframe()

def ClearAnimFbxFiles(*arr):
    workFolder = "D:/MIXAMO/"
    fbxsFolder = workFolder+"AnimationFbx/"
    rigFile = workFolder+"MixamoRig.mb"
    namespace = 'MixamoRig'
    fbxAnimationRoot = 'mixamorig:Hips'
    files = os.listdir(fbxsFolder)
    for file in files:
        if os.path.exists(fbxsFolder+file):
            if 'fbx_exists' in file:
                oldFile = fbxsFolder+file
                newFile = oldFile.replace('fbx_exists','fbx')
                os.rename(oldFile,newFile)
                oldName =  newFile
            else:
                oldName = fbxsFolder+file
            newName = fbxsFolder+(((file.replace("(","_")).replace(')','')).replace(' ','_')).replace('__','_')
            if not os.path.exists(newName):
                os.rename(oldName,newName)
    files = os.listdir(fbxsFolder)
    for file in files:
        cmds.file(new=True, force=True)
        cmds.file(rename=workFolder+"Animation/"+file+'.ma')
        cmds.file(save=True, type='mayaAscii')
        cmds.currentUnit(time='ntsc')
        cmds.file(rigFile, reference=True, namespace=namespace)
        fbxPath  = fbxsFolder+file
        cmds.file(fbxPath, i=True, type='FBX', ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace=':', options='fbx')
        cmds.select(fbxAnimationRoot)
        NLTA_setup.DeleteNamespace()
        cmds.select(namespace+':Main')
        MatchFbxAnimToAsFbx()
        cmds.select('Hips')
        CopyFbxKeys(5)
        cmds.file(save=True, type='mayaAscii')


def RenameNLTA(*arr):
    joints = cmds.ls(selection=True)
    for joint in joints:
        newName = 'NLTA_'+joint
        cmds.rename(joint,newName)

def MatchAndCreateKey(*arr):
    MatchAsToAnimRef()
    CreateKeyframe()
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(current_time + 1)

def NextFile(*arr):
    cmds.play(state=False)
    cmds.file(save=True, type='mayaAscii')
    url = "D:/MIXAMO/Animation/"
    filePath = cmds.file(query=True, sceneName=True)
    fileName = os.path.basename(filePath)
    files = os.listdir(url)
    index = files.index(fileName)
    if index < len(files):
        cmds.file(url+files[index+1], open=True, force=True)
        cmds.textField('fileName',edit=True,text=files[index+1].split('.')[0])
        SelectControls()
        cmds.viewFit(cmds.ls(selection=True), all=False)
        NLTA_skinning.fitRangeAnim()        
        cmds.play(forward=True)

def PreviousFile(*arr):
    cmds.play(state=False)
    cmds.file(save=True, type='mayaAscii')
    cmds.play(state=False)
    url = "D:/MIXAMO/Animation/"
    filePath = cmds.file(query=True, sceneName=True)
    fileName = os.path.basename(filePath)
    files = os.listdir(url)
    index = files.index(fileName)
    if index > 0:
        cmds.file(url+files[index-1], open=True, force=True)
        cmds.textField('fileName',edit=True,text=files[index-1].split('.')[0])
        SelectControls()
        cmds.viewFit(cmds.ls(selection=True), all=False)
        NLTA_skinning.fitRangeAnim()
        
        cmds.play(forward=True)

"""