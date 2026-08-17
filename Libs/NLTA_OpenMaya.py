import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

def GetDagPath(obj):
    sel = om.MSelectionList()
    sel.add(obj)
    return sel.getDagPath(0)