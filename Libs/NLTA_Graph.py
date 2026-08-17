import maya.cmds as cmds
import maya.mel as mel

defaultGraph = "NLTA_Graph"

def CreateCurve(name="NLTA_Graph"):
    if cmds.objExists(name):
        cmds.delete(name)
    if not cmds.objExists(name):
        sel = cmds.ls(sl=True)
        curve = cmds.createNode('animCurveTU', name=name)
        cmds.setKeyframe(curve, time=0, value=0)
        cmds.setKeyframe(curve, time=100, value=100)
        cmds.keyTangent(curve, itt='flat', ott='flat')
        cmds.select(sel)
CreateCurve()

def CreateUneedKey(exceptKeys,*arr):
    keys = cmds.keyframe(defaultGraph, q=True, tc=True) or []
    for t in keys:
        if t not in exceptKeys:
            cmds.cutKey(defaultGraph, time=(t, t), clear=True)


def SkirtCurve(*arr):
    if not cmds.objExists(defaultGraph):
        cmds.createNode('animCurveTU', name=defaultGraph)
    cmds.keyTangent(defaultGraph, time=(0, 0), ott='flat')
    cmds.keyTangent(defaultGraph, time=(100, 100), itt='flat')
    CreateUneedKey([0,100])

def SkirtEndCurve(*arr):
    if not cmds.objExists(defaultGraph):
        cmds.createNode('animCurveTU', name=defaultGraph)
    cmds.keyTangent(defaultGraph, time=(0, 0), ott='linear')
    cmds.keyTangent(defaultGraph, time=(100, 100), itt='flat')
    CreateUneedKey([0,100])



def GetValue(ratio,name=defaultGraph):
    if 0 <= ratio <= 1:
        time = ratio * 100
        return(cmds.getAttr(name+".output", time=time)/100)


def OpenGraph(name="NLTA_Graph", *args):
    CreateCurve()
    if cmds.window("MyGraphWin", exists=True):
        cmds.deleteUI("MyGraphWin")
    win = cmds.window("MyGraphWin", title="Custom Graph Editor", widthHeight=(500, 400))
    form = cmds.formLayout()
    panel = cmds.scriptedPanel(type="graphEditor", parent=form)
    cmds.formLayout(form, e=True,
        attachForm=[
            (panel, 'top', 0),
            (panel, 'bottom', 0),
            (panel, 'left', 0),
            (panel, 'right', 0)
        ]
    )
    cmds.showWindow(win)
    graphEd = panel + "GraphEd"    
    conn = cmds.selectionConnection(object=name)
    cmds.animCurveEditor(graphEd, e=True, autoFit=True)
    cmds.selectionConnection(conn, e=True, lock=True)
    cmds.animCurveEditor(graphEd, e=True, mainListConnection=conn)  
    cmds.animCurveEditor(graphEd, e=True, lookAt="all")

def FlipY(name=defaultGraph, *arr):
    times  = cmds.keyframe(name, q=True, tc=True) or []
    values = cmds.keyframe(name, q=True, vc=True) or []

    for t, v in zip(times, values):
        cmds.keyframe(name, e=True, time=(t,), valueChange=-v)

def FlipX(name=defaultGraph, *arr):
    times = cmds.keyframe(name, q=True, tc=True) or []
    if not times:
        return
    t_min = min(times)
    t_max = max(times)
    center = (t_min + t_max) / 2.0
    cmds.scaleKey(name, time=(t_min, t_max), timeScale=-1, timePivot=center)


def Clamp(name=defaultGraph, min_val=0, max_val=100):
    times  = cmds.keyframe(name, q=True, tc=True) or []
    values = cmds.keyframe(name, q=True, vc=True) or []
    for t, v in zip(times, values):
        new_t = t
        new_v = v

        if t < min_val:
            new_t = min_val
        elif t > max_val:
            new_t = max_val

        if v < min_val:
            new_v = min_val
        elif v > max_val:
            new_v = max_val
        if new_t != t or new_v != v:
            cmds.cutKey(name, time=(t,))
            cmds.setKeyframe(name, time=new_t, value=new_v)