import os
import json
import shutil
import importlib
import maya.utils
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import xml.dom.minidom as xd
import xml.etree.ElementTree as ET
from functools import partial
from math import pow,sqrt


import NLTA_General, NLTA_Mesh, NLTA_Graph, NLTA_Brush,NLTA_GraphSkinning,NLTA_Set,NLTA_Proxy,NLTA_Skinning,NLTA_Keyframes,NLTA_BlendShape
for module in [NLTA_General, NLTA_Mesh, NLTA_Graph, NLTA_Brush,NLTA_GraphSkinning,NLTA_Set,NLTA_Proxy,NLTA_Skinning,NLTA_Keyframes,NLTA_BlendShape]:
    try:
        importlib.reload(module)
    except:
        reload(module)


###################
UIs = {
    "animationDistance":None,
}

def CreateUI(data):
    global UI 
    def ModifyData(data):
        global titleFlags, layoutFlags, buttonFlags, inputFlags
        titleFlags = data.get('titleFlags', {})
        layoutFlags = data.get('layoutFlags', {})
        buttonFlags = data.get('buttonFlags', {})
        inputFlags = data.get('inputFlags', {})
    ModifyData(data) 

    titles, buttons, inputs = [], [], []
    parent = data['parent']

    layoutTempt = cmds.rowColumnLayout(data["module"],parent=parent)
    cmds.rowColumnLayout(layoutTempt,edit=True,**layoutFlags)
    cmds.rowColumnLayout(numberOfColumns=1)


    cmds.rowColumnLayout( numberOfColumns=2)#***
    cmds.rowColumnLayout( numberOfColumns=1)#<*
    animationDistance = cmds.intSliderGrp(label="Distance",field=True,minValue=0,maxValue=10000,value=50,width=270,columnWidth=[(1, 60)])    
    UIs["animationDistance"] = animationDistance
    cmds.rowColumnLayout( numberOfColumns=2)#<
    cmds.rowColumnLayout( numberOfColumns=1)
    titles.append(cmds.textField(text="Local",editable=False))
    cmds.rowColumnLayout( numberOfColumns=2)
    buttons.append(cmds.button( label='Rotate',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'local','type':'rotate','inturn':True,"ui":animationDistance}),width=120))
    buttons.append(cmds.button( label='Translate',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'local','type':'translate','inturn':True,"ui":animationDistance}),width=120))
    buttons.append(cmds.button( label='Rotate Together',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'local','type':'rotate','inturn':False,"ui":animationDistance})))
    buttons.append(cmds.button( label='Translate Together',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'local','type':'translate','inturn':False,"ui":animationDistance})))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.rowColumnLayout( numberOfColumns=1)
    titles.append(cmds.textField(text="Global",editable=False))
    cmds.rowColumnLayout( numberOfColumns=2)
    buttons.append(cmds.button( label='Rotate',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'world','type':'rotate','inturn':True,"ui":animationDistance}),width=120))
    buttons.append(cmds.button( label='Translate',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'world','type':'translate','inturn':True,"ui":animationDistance}),width=120))
    buttons.append(cmds.button( label='Rotate Toget',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'world','type':'rotate','inturn':False,"ui":animationDistance})))
    buttons.append(cmds.button( label='Translate Together',command = partial(NLTA_Keyframes.CreateKeyframe,{'space':'world','type':'translate','inturn':False,"ui":animationDistance})))
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")#>
    cmds.setParent("..")#*>
    cmds.rowColumnLayout( numberOfColumns=2)
    buttons.append(cmds.button( label='Delete',command = NLTA_Keyframes.deleteSenceKeyframe,width=95))
    buttons.append(cmds.button( label='Zoom',command = NLTA_Keyframes.ZoomRangeAnim,width=95))
    buttons.append(cmds.button( label='Delete Attr',command = NLTA_Keyframes.DeleteAttrKeyframes,width=95)) 
    buttons.append(cmds.button( label='Fit',command = NLTA_General.FitRangeAnim,width=95))
    buttons.append(cmds.button(label='Bind pose',c = NLTA_Skinning.goToBindPose))        
    cmds.setParent("..")
    cmds.setParent("..")#***


    ############################
    
    cmds.separator(height=10, style='in')
    titles.append(cmds.textField(text="Paint Skin Tools",editable=False))

    cmds.rowColumnLayout( numberOfColumns=1)#Open    

    cmds.rowColumnLayout(numberOfColumns=1)#-
    cmds.rowColumnLayout(numberOfColumns=2)#--

    cmds.rowColumnLayout(numberOfColumns=2)
    buttons.append(cmds.button( label='Unlock',c = NLTA_Skinning.unlock,width=80))
    buttons.append(cmds.button( label='Add unlock',c =NLTA_Skinning.addUnlock,width=80))
    

    buttons.append(cmds.button( label='Add Down',c = NLTA_Skinning.addUnlockDown))
    buttons.append(cmds.button( label='Add Up',c = NLTA_Skinning.addUnlockUp))
    buttons.append(cmds.button( label='Unlock all',c = NLTA_Skinning.unlockAll))
    buttons.append(cmds.button( label='Unlock 2 Jnts',c =NLTA_Skinning.UnlockTwoJoints))
    buttons.append(cmds.button( label='Isolate',c = NLTA_Skinning.IsolateEffectVertex))
    cmds.text(label="")
    cmds.separator(height=10, style='in')
    cmds.separator(height=10, style='in')
    buttons.append(cmds.button(label="Smooth", c = partial(NLTA_Brush.smooth,"solid")))
    buttons.append(cmds.button(label='Pick value',c = NLTA_Brush.pickValue))
    buttons.append(cmds.button(label="Copy Weight",c = NLTA_Brush.CopyWeight))
    buttons.append(cmds.button(label="Copy Ratio",c = NLTA_Brush.CopyRatio))    
    buttons.append(cmds.button(label="Flood", c = NLTA_Brush.flood))
    cmds.text(label="")
    cmds.separator(height=10, style='in')
    cmds.separator(height=10, style='in')
    buttons.append(cmds.button( label='Switch Joint',c = NLTA_Skinning.switchJoint)) 
    buttons.append(cmds.button(label="Switch Brush", c = NLTA_Brush.SwitchBrush))
    cmds.separator(height=10, style='in')
    cmds.separator(height=10, style='in')
    buttons.append(cmds.button(label="Middle",c=NLTA_Skinning.setMiddleWeight,width=95))
    buttons.append(cmds.button(label="Prune",c=NLTA_Skinning.pruneSmallWeights))
    cmds.setParent("..")


    cmds.rowColumnLayout(numberOfColumns=2)#---

    cmds.rowColumnLayout( numberOfColumns=1)#<-
    buttons.append(cmds.button(label="0", c = partial(NLTA_Brush.ReplaceWeight,0)))
    cmds.rowColumnLayout( numberOfColumns=2,mar=0)
    cmds.rowColumnLayout(numberOfColumns=1,mar=0)
    buttons.append(cmds.button(label="-0.0001",width=50, c = partial(NLTA_Brush.AddWeight,-0.0001)))
    buttons.append(cmds.button(label="-0.0005", c = partial(NLTA_Brush.AddWeight,-0.0005)))
    buttons.append(cmds.button(label="-0.001", c = partial(NLTA_Brush.AddWeight,-0.001)))
    buttons.append(cmds.button(label="-0.005", c = partial(NLTA_Brush.AddWeight,-0.005)))
    buttons.append(cmds.button(label="-0.01", c = partial(NLTA_Brush.AddWeight,-0.01)))
    buttons.append(cmds.button(label="-0.03", c = partial(NLTA_Brush.AddWeight,-0.03)))
    buttons.append(cmds.button(label="-0.05", c = partial(NLTA_Brush.AddWeight,-0.05)))
    buttons.append(cmds.button(label="-0.1", c = partial(NLTA_Brush.AddWeight,-0.1)))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=1,mar=0)
    buttons.append(cmds.button(label="0.0001",width=50, c = partial(NLTA_Brush.AddWeight,0.0001)))
    buttons.append(cmds.button(label="0.0005", c = partial(NLTA_Brush.AddWeight,0.0005)))
    buttons.append(cmds.button(label="0.001", c = partial(NLTA_Brush.AddWeight,0.001)))
    buttons.append(cmds.button(label="0.005", c = partial(NLTA_Brush.AddWeight,0.005)))
    buttons.append(cmds.button(label="0.01", c = partial(NLTA_Brush.AddWeight,0.01)))
    buttons.append(cmds.button(label="0.03", c = partial(NLTA_Brush.AddWeight,0.03)))
    buttons.append(cmds.button(label="0.05", c = partial(NLTA_Brush.AddWeight,0.05)))
    buttons.append(cmds.button(label="0.1", c = partial(NLTA_Brush.AddWeight,0.1)))    
    cmds.setParent("..")    
    cmds.setParent("..")
    buttons.append(cmds.button(label="1",width=100, c = partial(NLTA_Brush.AddWeight,1)))
    cmds.setParent("..")#>-

    cmds.rowColumnLayout( numberOfColumns=1)#<
    cmds.rowColumnLayout( numberOfColumns=4)#<--
    cmds.rowColumnLayout( numberOfColumns=1)
    buttons.append(cmds.button(label="Miror +X ",c=partial(NLTA_Skinning.mirrorSkin,"x","+"),width=95))
    buttons.append(cmds.button(label="Miror -X ",c=partial(NLTA_Skinning.mirrorSkin,"x","-")))
    buttons.append(cmds.button(label="Proxy",c=NLTA_Proxy.singleProxy))
    buttons.append(cmds.button(label="Proxy X",c=partial(NLTA_Proxy.createProxy,"x")))
    buttons.append(cmds.button(label="Copy Proxy",c=NLTA_Proxy.copyProxy))    
    buttons.append(cmds.button(label="Past Proxy",c=NLTA_Proxy.pastProxy))
    buttons.append(cmds.button(label="Closet Faces",c=NLTA_Proxy.SelectClosetFaces))
    cmds.setParent("..")
    cmds.rowColumnLayout( numberOfColumns=1)
    buttons.append(cmds.button(label="Copy Skin",c = NLTA_General.copyJointBind,width=95))
    buttons.append(cmds.button(label='Export Skin',c = NLTA_Skinning.ExportAllSkin))
    buttons.append(cmds.button(label='Import Skin',c = NLTA_Skinning.ImportAllSkin))
    buttons.append(cmds.button(label="Bind Skin",c = NLTA_General.bindSkin))
    buttons.append(cmds.button(label="Add joint",c=NLTA_Skinning.AddJoint))
    buttons.append(cmds.button(label="Remove joint",c=NLTA_Skinning.RemoveJoint))
    buttons.append(cmds.button(label="Add Mesh jnt",c=NLTA_Skinning.AddMeshJoint))    
    buttons.append(cmds.button(label="Clr Unneed",c=NLTA_Skinning.removeUnneedJoint))
    buttons.append(cmds.button(label="Clear Skins",c = NLTA_Skinning.clearSkin))
    cmds.setParent("..")
    cmds.rowColumnLayout( numberOfColumns=1)
    buttons.append(cmds.button(label='Import Skin Exist',c = NLTA_Skinning.ImportAllSkinExist))   
    buttons.append(cmds.button(label="Export Folder",c = NLTA_Skinning.ExportFolderSkin))  
    buttons.append(cmds.button(label="Import Folder",c = NLTA_Skinning.ImportFolderSkin))
    buttons.append(cmds.button(label="Quick Export Folder",c = NLTA_Skinning.ExportFolderSkinQuick))  
    buttons.append(cmds.button(label="Quick Import Folder",c = NLTA_Skinning.ImportFolderSkinQuick))
    buttons.append(cmds.button(label="Export FBX",c =NLTA_Skinning.ExportSkinFbx))
    buttons.append(cmds.button(label="Export Scene",c =NLTA_Skinning.ObjToNewScene))
    cmds.setParent("..")
    cmds.rowColumnLayout( numberOfColumns=1)
    buttons.append(cmds.button(label='Component',c=NLTA_Skinning.component,width=95))    
    buttons.append(cmds.button(label="Load UI", c=NLTA_Brush.loadUi))  
    buttons.append(cmds.button(label="Fix Quad",c=NLTA_Mesh.ShowQuardraw))
    buttons.append(cmds.button(label="Fix Initial",c=NLTA_General.fixInitial))
    buttons.append(cmds.button(label="Clear Weight ",c = NLTA_Skinning.ClearWeight))
    cmds.setParent("..")    
    cmds.setParent("..")#>--
    cmds.separator(height=10, style='in')

    cmds.rowColumnLayout( numberOfColumns=4)
    buttons.append(cmds.button( label="Create Set", command = NLTA_Set.CreateSet,width=100))
    buttons.append(cmds.button( label="Next Set",command = NLTA_Set.NextSet,width=100))
    buttons.append(cmds.button( label="Back Set",command = NLTA_Set.BackSet,width=100))
    buttons.append(cmds.button( label="Delete Sets",command = NLTA_Set.DeleteSets,width=100))
    cmds.setParent("..")
    cmds.rowColumnLayout(numberOfColumns=4)
    titles.append(cmds.textField(text="Max Influent",editable=False,width=100))
    inputs.append(cmds.intField("maxInfluent",value=4,width=100))
    buttons.append(cmds.button(label="Check",command =partial(NLTA_Skinning.checkMaxInfluent,cmds.intField("maxInfluent",value=True,query=True)),width=100))
    buttons.append(cmds.button(label="Fix",command = partial(NLTA_Skinning.fixMaxInfluence),width=100))
    cmds.setParent("..")

    cmds.setParent("..")#>-

    
    cmds.setParent("..")#---
    cmds.setParent("..")#--
    cmds.setParent("..")#-

    cmds.setParent("..")#End

    cmds.separator(height=10, style='in')
    titles.append(cmds.textField(text="Graph Skinning",editable=False))
    cmds.rowColumnLayout(nc=2)#Open

    cmds.rowColumnLayout(nc=1)#<-
    cmds.rowColumnLayout(nc=4)
    buttons.append(cmds.button(label="Edges > Curve ",c=NLTA_Proxy.EdgesToCurve,width=95))
    buttons.append(cmds.button(label="Verts > Curve ",c=NLTA_Proxy.VertsToCurve,width=95))
    buttons.append(cmds.button(label="Create Circle",c=NLTA_Proxy.CreateCircle,width=95))
    buttons.append(cmds.button(label="Draw Curve",c=NLTA_Proxy.DrawCurve,width=95))
    buttons.append(cmds.button(label="Close Curve",c=NLTA_Proxy.CloseCurve,width=95))
    buttons.append(cmds.button(label="Fit To Mesh",c=partial(NLTA_Proxy.FitCurveToMesh,"surface"),width=95))      
    cmds.setParent("..")
    cmds.separator(height=10, style='in')
    cmds.rowColumnLayout(nc=4)
    buttons.append(cmds.button(label="Create Loft",c=NLTA_Proxy.CreateLoft,width=95))
    buttons.append(cmds.button(label="Flip Loft",c=NLTA_Proxy.FlipLoftNormal,width=95))
    buttons.append(cmds.button(label="Flip Curve",c=NLTA_Proxy.FlipCurveNormal,width=95))        
    buttons.append(cmds.button(label="RotateCVs +",c=NLTA_Proxy.RotateCVsPositive,width=95))
    buttons.append(cmds.button(label="RotateCVs -",c=NLTA_Proxy.RotateCVsNegative,width=95))    
    buttons.append(cmds.button(label="Add Loft Curve",c=NLTA_Proxy.AddLoftCurve))
    buttons.append(cmds.button(label="Clear Scene",c=NLTA_Proxy.ClearAllLoft,width=95))      
    cmds.setParent("..")  
    cmds.setParent("..")#>-

    cmds.rowColumnLayout(nc=1)#<-
    cmds.rowColumnLayout(nc=4)
    buttons.append(cmds.button(label="Open",c=partial(NLTA_Graph.OpenGraph,"NLTA_Graph"),width=80))
    buttons.append(cmds.button(label="Skirt",c=NLTA_Graph.SkirtCurve,width=80))
    buttons.append(cmds.button(label="Skirt End",c=NLTA_Graph.SkirtEndCurve,width=80))
    buttons.append(cmds.button(label="Flip",c=partial(NLTA_Graph.FlipX,"NLTA_Graph"),width=80))
    cmds.setParent("..")
    cmds.rowColumnLayout(nc=3)
    buttons.append(cmds.button(label="Smooth",c=NLTA_GraphSkinning.GradientActiveJoint,width=80))
    buttons.append(cmds.button(label="Copy Ratio",c=NLTA_GraphSkinning.CopyRatioWeight,width=80))
    buttons.append(cmds.button(label="Skirt Parent",c=NLTA_GraphSkinning.SkirtParent,width=80))
    buttons.append(cmds.button(label="Skirt Chains",c=NLTA_GraphSkinning.SkirtChains,width=80))
    cmds.setParent("..")
    cmds.rowColumnLayout(nc=1) 
    buttons.append(cmds.button(label="Vertex Intersect",c=NLTA_GraphSkinning.SelectVertexIntersect,width=95))    
    cmds.setParent("..")

    cmds.setParent("..")#>-

    cmds.setParent("..")#End

    
    cmds.separator(height=10, style='in')
    titles.append(cmds.textField(text="Blend Shape",editable=False))
    cmds.rowColumnLayout( numberOfColumns=7)#<- 
    buttons.append(cmds.button(label="Import BS",c = NLTA_BlendShape.ImportBlendShape))
    buttons.append(cmds.button(label="Export BS",c = NLTA_BlendShape.ExportBlendShape))
    buttons.append(cmds.button(label="Export BS XML",c = NLTA_BlendShape.ExportBSToXML))
    buttons.append(cmds.button(label="Export Verts Pos",c = NLTA_BlendShape.ExportVertexsPosition))
    buttons.append(cmds.button(label="Import Verts Pos",c = NLTA_BlendShape.ImportVertexsPosition))
    buttons.append(cmds.button(label="Mirror Vert by UV",c = NLTA_Mesh.MirrorVertexByUv))
    buttons.append(cmds.button(label="Mirror Vert pos",c = NLTA_Mesh.MirrorVertPos))
    cmds.setParent("..")#>-

    cmds.setParent("..")
    cmds.setParent("..")

    for title in titles:
        cmds.textField(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)
