import os
import maya.cmds as cmds
import pymel.core as pm
from functools import partial
from datetime import datetime

import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        from importlib import reload
        reload(module)

def DefaultSetting(*arr):
    moduleName = os.path.basename(__file__).replace(".py","")
    ext = "py"
    name = "Up AfterScript"
    return({
        "ext":ext,
        "path":("/").join(os.path.dirname(pm.sceneName()).split('/')[0:-1])+"/SceneData/"+moduleName+"."+ext,
        "moduleName":moduleName,
        "order":0,
        "title":name,
        "name":name,
        "id":datetime.now().strftime("%Y%m%d%H%M%S")
    })

def Form(data,*arr):
    mainForm = NLTA_General.LoadModule("Scene_Form")
    dataBack = mainForm.Create(data)

def Run(data,*arr):
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })
    NLTA_General.RunScriptFile(newestData["path"])
    







