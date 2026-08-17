import maya.cmds as cmds

def CreateColorButtons(*arr):
    return({
        "Gray":0,
        "Black":1,
        "Dark Gray":2,
        "Light Gray":3,
        "Dark Red":4,
        "Dark Blue":5,
        "Blue":6,
        "Dark Green":7,
        "Dark purple":8,
        "Pink":9,
        "Brown":10,
        "Dark Brown":11,
        "Light Brown":12,
        "Red":13,
        "Light Green":14,
        "Dark Blue":15,
        "White":16,
        "Yellow":17,
        "Cyan":18,
        "Jade":19,
        "Soft Pink":20,
        "Latte":21,
        "Light Yellow":22,
        "Middle Green":23,
        "Middle Brown":24,
        "Middle Yellow":25,
        "Little Green":26,
        "Little Jade":27,
        "Little Cyan":28,
        "Little Blue":29,
        "Little Purple":30,
        "Little Pink":31,
    })

def changeColor(color,*arr):
    objs = cmds.ls(selection=True)        
    for obj in objs:
        objectType = cmds.objectType(obj)
        if objectType == "mesh" or objectType == "nurbsCurve" or objectType == "transform":
            shapes = cmds.listRelatives(obj,shapes=True,path=True)
            for shape in shapes:
                cmds.setAttr(shape+".overrideEnabled",True)
                cmds.setAttr(shape+".overrideColor",color)
        else:
            cmds.setAttr(obj+".overrideEnabled",True)
            cmds.setAttr(obj+".overrideColor",color)
