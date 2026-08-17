import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import importlib


import NLTA_General, NLTA_Mesh, NLTA_Skinning, NLTA_GraphSkinning
for module in [NLTA_General, NLTA_Mesh, NLTA_Skinning, NLTA_GraphSkinning]:
    try:
        importlib.reload(module)
    except:
        reload(module)


def loadUi(*arr):   
    mel.eval('artAttrSkinPaintCtx -e -minvalue -1 -useColorRamp 1 -colorRamp "1,0,0,1,1,1,0.5,0,0.8,1,1,0.7,0,0.6,1,0,.5,0,0.4,1,0,0,1,0,1"  -rampMaxColor .57 .57 .57  artAttrSkinContext;')
    cmds.artAttrSkinPaintCtx("artAttrSkinContext", e=True, opacity=1)
    mel.eval('setObjectPickMask "Joint" false;')

def ChangeOpacity(ui,*arr):
    value = cmds.floatSliderGrp(ui,query=True,value=True)
    ctx = cmds.currentCtx()
    try:
        cmds.artAttrSkinPaintCtx(ctx, e=True, opacity=value)
    except:pass

def ChangeOpacityValue(ui,value,*arr):
    cmds.floatSliderGrp(ui,edit=True,value=value)
    ChangeOpacity(ui)      
    
def ReplaceWeight(value,*arr):
    pm.mel.eval("artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;")
    pm.mel.eval("artAttrPaintOperation artAttrSkinPaintCtx Replace;")
    pm.mel.eval("artSkinSetSelectionValue "+str(value)+" false artAttrSkinPaintCtx artAttrSkin;")
    
def AddWeight(value,*arr):
    pm.mel.eval("artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;")
    pm.mel.eval("artAttrPaintOperation artAttrSkinPaintCtx Add;")
    pm.mel.eval("artSkinSetSelectionValue "+str(value)+" false artAttrSkinPaintCtx artAttrSkin;")

def smooth(value,*arr):
    pm.mel.eval("artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;")
    pm.mel.eval("artUpdateStampProfile "+value+" artAttrSkinPaintCtx;")
    pm.mel.eval("artAttrPaintOperation artAttrSkinPaintCtx Smooth;")

def pickValue(*arr):
    pm.mel.eval("artAttrPaintOperation artAttrSkinPaintCtx Replace;")
    pm.mel.eval("artAttrSkinPaintCtx -e -pickValue `currentCtx`;")
    ctx = cmds.currentCtx()
    cmds.artAttrSkinPaintCtx(ctx, e=True, opacity=1)   

def flood(*arr):
    pm.mel.eval("artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;")
    pm.mel.eval('artAttrSkinPaintCtx -e -clear `currentCtx`;')
    
def CopyWeight(*arr):
    mel.eval(r'''
        if (!`exists NLTA_CopyWeight`)
        {
            global proc NLTA_CopyWeight()
            {
                string $sel[] = `ls -os -fl`;
                if (size($sel) < 2)
                {
                    warning "Select one source vertex and one or more destination vertices.";
                    return;
                }
                string $source = $sel[0];
                select -r $source;
                CopyVertexSkinWeights;

                select -cl;
                for ($i = 1; $i < size($sel); $i++)
                {
                    select -add $sel[$i];
                }
                PasteVertexSkinWeights;
            }
        }
        NLTA_CopyWeight();
        repeatLast
            -ac "NLTA_CopyWeight"
            -acl "Copy Vertex Weight";
    ''')


def SwitchBrush(*arr):
    ctx = cmds.currentCtx()
    if cmds.contextInfo(ctx, c=True) == "artAttrSkin":
        value = cmds.artAttrSkinPaintCtx(ctx,q=True,value=True)
        newValue =  value * (-1)
        AddWeight(newValue)
        cmds.artAttrSkinPaintCtx(ctx,e=True,value=newValue)        
        
def CopyRatio(*arr):
    sels = cmds.ls(orderedSelection=True,flatten=True)
    if len(sels) >= 2:
        vertSource = sels[0]
        vertTarget = sels[1:]
        mesh = NLTA_Mesh.GetMesh()[0]        
        skinData = NLTA_General.GetSkinData(mesh)
        jointsWeight = NLTA_Skinning.GetJointsWeight({
            "skinCluster":skinData["skinCluster"],
            "vert":vertSource,
            "joints":skinData["jointsUnlock"]
        })
        ratios = []
        for jointUnlock in skinData["jointsUnlock"]:
            ratios.append(jointsWeight[jointUnlock]["ratio"])
        for vertTemp in vertTarget:
            NLTA_GraphSkinning.WeightFromRatio({
                "skinCluster":skinData["skinCluster"],
                "vert":vertTemp,
                "joints":skinData["jointsUnlock"],
                "ratios":ratios
            })
        cmds.skinCluster(skinData["skinCluster"], e=True, forceNormalizeWeights=True)
        NLTA_GraphSkinning.UpdateView()

