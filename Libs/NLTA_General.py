import os
import re
import json
import subprocess
import importlib
import hashlib
import ctypes
import ctypes.wintypes
from functools import partial

import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om
from math import sqrt



if not cmds.pluginInfo('objExport', query=True, loaded=True):
    cmds.loadPlugin('objExport')

for camera in ["persp","top","front","side"]:
    cmds.setAttr(camera+'Shape.nearClipPlane',0.1)
    cmds.setAttr(camera+'Shape.farClipPlane',50000)

"""
def RunScriptFile(url,*arr):
    print(url)
    if os.path.exists(url):
        filePath = cmds.encodeString(url)
        myFile =  open(filePath,'r')
        myObject = myFile.read()
        myFile.close()
        exec(myObject)
    else:
        print('The link is not exist.')
"""
def RunScriptFile(url, *arr):
    print(url)

    if os.path.exists(url):
        filePath = cmds.encodeString(url)
        with open(filePath, "r", encoding="utf-8") as myFile:
            myObject = myFile.read()
        script_globals = {
            "__file__": filePath,
            "__name__": "__main__",
            "__builtins__": __builtins__,
        }
        exec(
            compile(myObject, filePath, "exec"),
            script_globals,
            script_globals
        )

    else:
        print("The link is not exist.")

def runScript(var,*arr):
    if cmds.scrollField(var,query=True,text=True)!="":
        script_file = cmds.scrollField(var,query=True,text=True)
        lineData = script_file.splitlines()
        for a in lineData:
            if os.path.exists(a):
                filePath = cmds.encodeString(a)
                myFile =  open(filePath,'r')
                myObject = myFile.read()
                myFile.close()
                exec(myObject)
            else:
                exec(a)    
    else:
        print("No script for "+var+".")

def runPostScript(*arr):
    folder_temp = os.path.dirname(pm.sceneName())
    if not folder_temp:
        folder_temp = pm.mel.eval("SaveSceneAs;")
    folder_temp = os.path.dirname(pm.sceneName())
    postScriptUrl = folder_temp+"/"+"postScript.py"
    if os.path.exists(postScriptUrl):
        filePath = cmds.encodeString(postScriptUrl)
        myFile =  open(filePath,'r')
        myObject = myFile.read()
        myFile.close()
        exec(myObject)
    else:
        writeTxtFile(postScriptUrl,"")


def checkNegPosAxis(obj,axis,*arr):
    cmds.select(clear=True)
    jointChild = cmds.joint()
    cmds.select(clear=True)
    jointParent = cmds.joint()
    cmds.matchTransform(jointChild,obj,position=True)
    cmds.matchTransform(jointParent,obj,position=True)
    cmds.setAttr(jointParent+".t"+axis,0)
    cmds.parent(jointChild,jointParent)
    axisValue = cmds.getAttr(jointChild+".t"+axis)
    cmds.delete(jointParent)
    if axisValue > 0:
        return("+")
    else:
        return("-")

def addMinusAdd(name,*arr):
    arrayCurrent = cmds.scrollField(name,query=True,text=True)
    arrayCurrent = arrayCurrent.split(";")
    arrayJoint = cmds.ls(selection=True,ap=True)
    jointString = ""
    if arrayJoint :     
        for a in arrayJoint:
            if a not in arrayCurrent:
                arrayCurrent.append(a)
        jointString = (";").join(arrayCurrent)
        cmds.scrollField(name,edit=True,text=jointString)
        
def addMinusMinus(name,*arr):
    arrayCurrent = cmds.scrollField(name,query=True,text=True)
    arrayCurrent = arrayCurrent.split(";")
    arrayJoint = cmds.ls(selection=True,ap=True)
    jointString = ""
    if arrayJoint :     
        for a in arrayJoint:
            if a in arrayCurrent:
                arrayCurrent.remove(a)
        jointString = (";").join(arrayCurrent)
        cmds.scrollField(name,edit=True,text=jointString)


def allParents(name,*arr):
    rootTemp = name
    arrayTemp = []
    while (True):
        parentTemp = cmds.listRelatives(rootTemp,parent=True,type='joint',path=True)
        if not parentTemp:
            break;
        rootTemp = parentTemp[0]
        arrayTemp.insert(0,parentTemp[0])
    return(arrayTemp)
    
def sortHierachy(array,*arr):
    returnArray = []
    for i in array:
        parentTemp = cmds.listRelatives(i,parent=True)[0]
        if parentTemp in returnArray:
            indexTemp = returnArray.index(parentTemp)
            returnArray.insert(0,parentTemp)
        else:
            returnArray.append(parentTemp)
    returnArray.remove(returnArray[0])
    lastChild = list(set(array) - set(returnArray))
    returnArray.append(lastChild[0])
    return(returnArray)
    
def hierachyBetween(array,*arr):
    if len(array)==2:
        obj1 = array[0]
        obj2 = array[1]
        obj1Children = cmds.listRelatives(obj1,path=True)
        if not obj1Children:
            obj1Children = []  
        obj2Children = cmds.listRelatives(obj2,path=True)
        if not obj2Children:
            obj2Children = []
        if obj1 in obj2Children:
            parentObj = obj2
            childrenObj = obj1
        else:
            parentObj = obj1
            childrenObj = obj2
        hierachyArray = []
        flag = 0
        childrenTemp = childrenObj
        while flag < 1:
            parentTemp =  cmds.listRelatives(childrenTemp,p=True,pa=True)[0]
            if parentTemp.endswith(parentObj):
                flag = 1
            else:
                hierachyArray.insert(0,parentTemp)
                childrenTemp = parentTemp
        hierachyArray.insert(0,parentObj)
        hierachyArray.append(childrenObj)
        return (hierachyArray)


def MatchJoint(array,*arr):#create a match between 2 hierachy [source_begin,source_end,destination_begin,destination_and,name]
    if array !=None:
        returnArray = []
        sourceBegin = array[2]
        sourceEnd = array[3]        
        destinationBegin = array[0]
        destinationEnd = array[1]
        sourceBeginUuid = cmds.ls(sourceBegin,uuid=True)
        sourceEndUuid = cmds.ls(sourceEnd,uuid=True)
        destinationBeginUuid = cmds.ls(destinationBegin,uuid=True)

        cmds.matchTransform(destinationBegin,sourceBegin,pos=True)
        cmds.matchTransform(destinationEnd,sourceEnd,pos=True)
        needCreate = hierachyBetween([sourceBegin,sourceEnd])
        needCreate.remove(sourceBegin)
        needCreate.remove(sourceEnd)
        needDelete = hierachyBetween([destinationBegin,destinationEnd])
        
        if len(needDelete)>2:
            destinationEnd = cmds.parent(destinationEnd,destinationBegin)[0]
            cmds.delete(needDelete[1])
            
        if len(needCreate)>0:
            parentTemp = None
            stt = 1
            for i in needCreate:
                iUuid = cmds.ls(i,uuid=True)
                cmds.ls(cmds.ls(selection=True,uuid=True))
                jntName = cmds.createNode("joint")
                if array[4]:
                    jntName = cmds.rename(jntName,array[4]+str(stt))
                else:
                    jntName = cmds.rename(jntName,i+"_copy")
                cmds.matchTransform(jntName,i,pos=True)
                cmds.matchTransform(jntName,cmds.ls(destinationBeginUuid)[0],rot=True)  
                pm.makeIdentity(jntName, apply=True, translate=True, rotate=True, scale=True)
                if parentTemp:
                    parentTemp = cmds.parent(jntName,parentTemp)[0] 
                else:
                    parentTemp = cmds.parent(jntName,destinationBegin)[0]
                returnArray.append([parentTemp,cmds.ls(iUuid)[0]])
                stt +=1

            destinationEnd = cmds.parent(destinationEnd,parentTemp)[0]
        returnArray.append([destinationEnd,cmds.ls(sourceEndUuid)[0]])
        returnArray.insert(0,[cmds.ls(destinationBeginUuid)[0],cmds.ls(sourceBeginUuid)[0]])
        return(returnArray)


def checkOnly(array,*arr):
    name = array[0]
    stringExist = array[1]
    if len(cmds.ls(name,r=True)) > 1:
        for a in cmds.ls(name,r=True):
            longPath = cmds.ls(a,long=True)[0]
            if stringExist in longPath:
                return(a)
    else:
        return(name)        
            
def checkSubString(array,*arr):
    string = array[0]
    array_temp =  array[1]
    for i in array_temp:
        if i in string:
            return(True)
    return(False)

def correctCharacter(string,*arr):
    currentString = string 
    for b in ["FBXASC046","FBXASC045","FBXASC032","[","]","."]:            
        if b in currentString:   
            currentString = currentString.replace(b,"_")
    return(currentString)
    
def readJsonFile(url,*arr):
    if os.path.exists(url):
        filePath = cmds.encodeString(url)
        myFile =  open(filePath,'r')
        myObject = myFile.read()
        myFile.close()
        if int(cmds.about(version=True)) < 2022:
            data = json.loads(myObject,'utf-8')
        else:
            data = json.loads(myObject)
        return(data)

    else:
        print("!: File is not exists!")

def writeJsonFile(url, data):
    folder = os.path.dirname(url)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(url, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False, sort_keys=False)

    print("Url export:", url)

def JsonUpdateByID(data,*arr):    
    path = data["path"]
    values = data["values"]
    itemID = data["id"]
    currentData = readJsonFile(path)
    if currentData:
        for dataTemp in currentData:
            if dataTemp.get('id') == itemID:
                for value in values:
                    dataTemp[value] = values[value]
                break
    writeJsonFile(path,currentData)

def JsonGetByID(data,*arr):    
    path = data["path"]
    itemID = data["id"]
    currentData = readJsonFile(path)
    if currentData:
        for dataTemp in currentData:
            if dataTemp.get('id') == itemID:
                return(dataTemp)
    return(None)

def JsonAdd(data, *arr):
    path = data["path"]
    values = data["values"]
    currentData = readJsonFile(path)
    if not currentData:
        currentData = []
    currentData.append(values)
    writeJsonFile(path, currentData)
    return values
    
def readTxtFile(url,*arr):
    if os.path.exists(url):
        filePath = cmds.encodeString(url)
        myFile =  open(filePath,'r')
        myObject = myFile.read()
        myFile.close()
        return(myObject)
    else:
        print("!: File is not exists!")

def writeTxtFile(url,data,*arr):
    with open(url,"w") as text_file:
        text_file.write(data)        
    print("Url export: " + url)
    


def CreateNamespace(nameSpace,*arr):
    if not cmds.namespace(exists=nameSpace):
        cmds.namespace(add=nameSpace)
    objs = cmds.ls(selection=True)
    for obj in objs:
        newName = nameSpace + ":" + obj
        cmds.rename(obj,newName)

def DeleteNamespace(nameSpace,*arr):
    if cmds.namespace(exists=nameSpace):
        cmds.namespace(moveNamespace=(nameSpace, ":"), force=True)
        cmds.namespace(removeNamespace=nameSpace)
        
def GetSubFolders(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    
def GetFolders(url):
    stringArray = []
    for folder in sorted(os.scandir(url),key=os.path.getmtime)[::-1]:
        if folder.is_dir():
            stringArray.append(folder.path.split("\\")[-1])
    return(stringArray)

def GetFiles(url,fileType):
    files = os.listdir(url)
    nameArray = []
    for file in files:
        if file.endswith("."+fileType):
            fileName = file.split(".")[0]
            nameArray.append(fileName)
    return(nameArray)

def CreateLayer(layerName):
    if not pm.objExists(LayerName):
        DisplayLayer = pm.createDisplayLayer(name=LayerName, empty=True)
        
def DeleteLayers(*arr):
    layers = cmds.ls(type='displayLayer') 
    layers = [layer for layer in layers if layer not in ['defaultLayer', 'defaultRenderLayer']]
    for layer in layers:
        objs = cmds.editDisplayLayerMembers(layer, query=True)
        cmds.select(objs)
        pm.mel.eval('layerEditorRemoveObjects '+layer+';')
        cmds.delete(layer)

def ClearScene(*arr):
    pm.mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
    unknown_nodes = cmds.ls(type='unknown')
    unknown_dag_nodes = cmds.ls(type='unknownDag')
    all_unknown_nodes = unknown_nodes + unknown_dag_nodes
    for node in all_unknown_nodes:
        if cmds.objExists(node):
            cmds.lockNode(node, lock=False)
            cmds.delete(node)

def ExportFbx(link,*arr):
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("No objects selected for export.")
        return
    cmds.file(link,force=True,options='v=0',typ="FBX export",pr=True,es=True)

def Repath(link,*arr):
    nodes = cmds.filePathEditor(query=True,listFiles="",unresolved=True,withAttribute=True)
    attribute = []
    if nodes:
        for i in range(len(nodes)):
            if i % 2!=0:
                node = nodes[i]
                attribute.append('"'+node+'"')
        attributeString = ",".join(attribute)
        exec('cmds.filePathEditor('+attributeString+',repath = "'+link+'",force=True,recursive=True)')

def GetPosition(obj):
    if isinstance(obj, (list, tuple)):
        return obj
    if "." in obj:
        return cmds.pointPosition(obj, w=True)
    return cmds.xform(obj, q=True, ws=True, t=True)

def GetDistance(obj1, obj2):
    pos1 = GetPosition(obj1)
    pos2 = GetPosition(obj2)
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]
    return sqrt(dx*dx + dy*dy + dz*dz)

def GetFirstKey(*arr):
    minFrame = None
    for member in cmds.ls(selection=True):
        keys = cmds.keyframe(member, query=True, timeChange=True)
        if keys:
            firstFrame = min(keys)
            if minFrame !=None:
                if firstFrame < minFrame:
                    minFrame = firstFrame
            else:
                minFrame = firstFrame
    return(minFrame)

def GetLastKey(*arr):
    maxFrame = 0
    for member in cmds.ls(selection=True):
        keys = cmds.keyframe(member, query=True, timeChange=True)
        if keys:
            lastFrame = max(keys)
            if lastFrame > maxFrame:
                maxFrame = lastFrame
    return(maxFrame)


def FitRangeAnim(*arr):    
    anim_curves = cmds.ls(type='animCurve') or []    
    if not anim_curves:
        cmds.warning("No datas")
        return
    key_times = cmds.keyframe(anim_curves, q=True)    
    if not key_times:
        cmds.warning("No Keyframes")
        return
    start = min(key_times)
    end   = max(key_times)
    cmds.playbackOptions(min=start, max=end)
    cmds.playbackOptions(ast=start, aet=end)    

def GetAllKeytime(*arr):
    objs = cmds.ls(selection=True)
    keyData = []
    for obj in objs:
        keyTimes = cmds.keyframe(obj,query=True,timeChange=True) or []
        if keyTimes:
            keyData.extend(keyTimes)
    return(sorted(set(keyData)))

def GetDestopAppRealPath(name, *arr):
    name = name.lower()
    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None,
        CSIDL_DESKTOP,
        None,
        SHGFP_TYPE_CURRENT,
        buf
    )
    desktop_path = buf.value
    for file in os.listdir(desktop_path):
        fileLower = file.lower()
        if fileLower.startswith(name) and fileLower.endswith(".lnk"):
            lnk_path = os.path.join(desktop_path, file)
            powershell_command = [
                "powershell",
                "-NoProfile",
                "-Command",
                "(New-Object -ComObject WScript.Shell).CreateShortcut('{}').TargetPath".format(lnk_path)
            ]
            process = subprocess.Popen(
                powershell_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            try:
                stdout = stdout.decode("utf-8")
            except:
                pass

            try:
                stderr = stderr.decode("utf-8")
            except:
                pass

            if process.returncode != 0:
                print(stderr)
                continue

            path = stdout.strip()

            if os.path.isfile(path):
                return path

def OpenSublime(path,*arr):
    sublimePath = GetDestopAppRealPath('Sublime')
    subprocess.Popen([sublimePath,path])

def GetRootJoint(joint,*arr):
    if not cmds.objExists(joint) or cmds.nodeType(joint) != 'joint':
        cmds.error(
            "{} It isn't a joint.".format(joint)
        )  
    current = joint
    while True:
        parent = cmds.listRelatives(current, parent=True, type='joint')
        if not parent:
            return current
        current = parent[0]

def GetUniqueName(name,*arr):
    if not cmds.objExists(name):
        return(name)
    i = 1
    while True:
        newName = name+'_'+str(i)
        if not cmds.objExists(newName):
            return(newName)
        i += 1
        
def ZeroTransform(obj,*arr):
    for attr in ["tx","ty","tz","rx","ry","rz"]:
        cmds.setAttr(obj + "." + attr,0)
    for attr in ["sx","sy","sz"]:
        cmds.setAttr(obj + "." + attr,1)


def GetCurrentPath(*arr):
    folder_temp = os.path.dirname(pm.sceneName())
    if not folder_temp:
        folder_temp = pm.mel.eval("SaveSceneAs;")
    folderTemp = os.path.dirname(pm.sceneName())
    if folderTemp:
        return(folderTemp)

def GetSkinData(mesh, *args):
    skinCluster = pm.mel.eval('findRelatedSkinCluster ' + mesh)
    if not skinCluster:
        return None
    joints = cmds.skinCluster(skinCluster, q=True, inf=True)
    conn = cmds.connectionInfo(skinCluster + ".paintTrans", sourceFromDestination=True)
    jointActive = conn.split(".")[0] if conn else None
    unlockedJoints = [j for j in joints if not cmds.getAttr(j + ".liw")]
    return {
        "skinCluster": skinCluster,
        "joints": joints,
        "jointActive": jointActive,
        "jointsUnlock": unlockedJoints
    }

def bindSkin(*arr):
    joints = cmds.ls(sl=True, type="joint")
    meshs = []
    for obj in cmds.ls(sl=True, type="transform"):
        shapes = cmds.listRelatives(obj, s=True, ni=True) or []
        if not shapes:
            continue
        if cmds.nodeType(shapes[0]) == "mesh":
            meshs.append(obj)
    for mesh in meshs:
        cmds.select(mesh)
        cmds.select(joints,add=True)
        cmds.skinCluster(
            joints,
            mesh,
            toSelectedBones=True,
            bindMethod=3,
            normalizeWeights=1,
            weightDistribution=0,
            mi=4,
            dr=4,
            rui=False
        )
        #pm.mel.eval('newSkinCluster "-toSelectedBones -bindMethod 3  -normalizeWeights 1 -weightDistribution 0 -mi 4  -dr 4 -rui false    -heatmapFalloff 0.2 -geodesicResolution 256 -geodesicPostVoxelCheck 1, multipleBindPose, 0";')

    
def copyJointBind(*arr):
    currentSelection = cmds.ls(selection=True)
    sourceMesh = cmds.ls(selection=True)[0]
    targetMesh = cmds.ls(selection=True)[1:]
    skinCluster = pm.mel.eval('findRelatedSkinCluster '+sourceMesh)
    bindJoint = cmds.skinCluster(skinCluster,query=True,inf=True)
    for mesh in targetMesh:
        cmds.select(clear=True)
        cmds.select(mesh)
        pm.mel.eval('DeleteHistory;')
        for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
            cmds.setAttr(mesh+"."+attr,lock=False)
        pm.mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')
        pm.mel.eval('ResetTransformations;')
        cmds.select(bindJoint,add=True)
        bindSkin()
        cmds.select(clear=True)
        cmds.select(sourceMesh)
        cmds.select(mesh,add=True)
        currentSkinCluster = pm.mel.eval('findRelatedSkinCluster '+mesh)

        pm.mel.eval('copySkinWeights -ss '+skinCluster+' -ds '+currentSkinCluster+' -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne -normalize;')

        cmds.select(currentSelection)

def fixInitial(*arr):
    cmds.lockNode('initialShadingGroup', l=0, lockUnpublished=0)


def GetWorldPos(node):
    sel = om.MSelectionList()
    sel.add(node)
    dag = sel.getDagPath(0)
    matrix = dag.inclusiveMatrix()
    transform = om.MTransformationMatrix(matrix)
    return transform.translation(om.MSpace.kWorld)

def GetProjectFunctionPath(*arr):
    path = cmds.file(q=True, sn=True)
    if path:
        projectPath = ("/").join(os.path.dirname(path).split("/")[:-2])+"/ProjectFunction/"
        if not os.path.exists(projectPath):
            os.makedirs(projectPath)
        return(projectPath)
    else:
        cmds.warning("Please save file first!~ ")

def SetAttrValue(attr,value,*arr):
    attrType = cmds.getAttr(attr, type=True)
    if attrType in ("double", "float"):
        cmds.setAttr(attr,float(value))
        value = float(value)
    elif attrType in ("long", "short", "byte", "bool"):
        cmds.setAttr(attr,int(value))
    elif attrType in ("string", "enum"):
        cmds.setAttr(attr,str(value))

def GroupMatchObject(obj,name):
    grp = cmds.group(em=True, name=name)
    cmds.delete(cmds.parentConstraint(obj, grp, mo=False))
    cmds.delete(cmds.scaleConstraint(obj, grp, mo=False))
    return(grp)
"""
def CreateOffsetGroup(obj,offsetName,*arr):
    offsetName = GetUniqueName(offsetName)
    offset = GroupMatchObject(obj,offsetName)
    ctrlParent = cmds.listRelatives(obj,parent=True)
    if ctrlParent:
        rootParent = ctrlParent[0]
        cmds.parent(offset,rootParent)
    else:
        rootParent = GroupMatchObject(offset,offset+'Parent')
        cmds.parent(offset,rootParent)
    cmds.parent(obj,offset)
    return(offset)
"""
def CreateOffsetGroup(obj,offsetName,*args):
    parent = cmds.listRelatives(obj,parent=True)
    if parent and parent[0] == offsetName:
        return offsetName
    if cmds.objExists(offsetName):
        children = cmds.listRelatives(offsetName,children=True,fullPath=False) or []
        if obj in children:
            return offsetName
        offsetName = GetUniqueName(offsetName)
    offset = GroupMatchObject(obj,offsetName)
    if parent:
        cmds.parent(offset,parent[0])
    cmds.parent(obj,offset)
    return offset

def LoadModule(name,*arr):
    module = importlib.import_module(name)
    try:
        importlib.reload(module)
    except:
        from importlib import reload
        reload(module)
    return(module)

import re

def GetMirrorName(name):
    swap = {
        "L": "R", "R": "L",
        "l": "r", "r": "l",
        "Left": "Right", "Right": "Left",
        "left": "right", "right": "left",
        "LEFT": "RIGHT", "RIGHT": "LEFT",
        "Lf": "Rt", "Rt": "Lf",
        "lf": "rt", "rt": "lf",
        "LF": "RT", "RT": "LF",
    }
    patterns = [
        # _L_  _R_
        r'(?<=_)(L|R|l|r)(?=_)',
        # Hand_L
        r'(?<=_)(L|R|l|r)$',
        # L_Hand
        r'^(L|R|l|r)(?=_)',
        # _Left_
        r'(?<=_)(Left|Right|left|right|LEFT|RIGHT)(?=_)',
        # Hand_Left
        r'(?<=_)(Left|Right|left|right|LEFT|RIGHT)$',
        # Left_Hand
        r'^(Left|Right|left|right|LEFT|RIGHT)(?=_)',
        # _Lf_ _Rt_
        r'(?<=_)(Lf|Rt|lf|rt|LF|RT)(?=_)',
        # Hand_Lf
        r'(?<=_)(Lf|Rt|lf|rt|LF|RT)$',
        # Lf_Hand
        r'^(Lf|Rt|lf|rt|LF|RT)(?=_)',
        # RigRArm RigLArm
        r'(?<=Rig)(L|R|l|r)',
        # RigRightArm
        r'(?<=Rig)(Left|Right|left|right|LEFT|RIGHT)',
        # RigLfArm
        r'(?<=Rig)(Lf|Rt|lf|rt|LF|RT)',
        # RightArm LeftArm (camelCase/PascalCase)
        r'^(Left|Right|left|right|LEFT|RIGHT)',
        # LArm RArm
        r'^(L|R|l|r)(?=[A-Z])',
        # LfArm RtArm
        r'^(Lf|Rt|lf|rt|LF|RT)(?=[A-Z])',
    ]
    for pattern in patterns:
        m = re.search(pattern, name)
        if m:
            value = m.group(1)
            start, end = m.span(1)
            return name[:start] + swap[value] + name[end:]
    return name

def CreateObjectsHex(objects):
    objects = sorted(objects)
    data = "|".join(objects)
    return hashlib.sha1(
        data.encode("utf-8")
    ).hexdigest()[:12]
