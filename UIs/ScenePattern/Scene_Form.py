import maya.cmds as cmds
from functools import partial

import NLTA_General,NLTA_UI
for module in [NLTA_General,NLTA_UI]:
    try:
        importlib.reload(module)
    except:
        from importlib import reload
        reload(module)


def Create(data,*arr):
    def ChangeName(data,*arr):
        value = cmds.textField(nameUI,query=True,text=True)
        sceneDatas = NLTA_General.readJsonFile(data["sceneDataPath"]+"/ScenePatternData.json")
        NLTA_General.JsonUpdateByID({
            "path":data["sceneDataPath"]+"/ScenePatternData.json",
            "id":data["id"],
            "values":{
                "name":value
            }
        })
    def Browser(data,*arr):
        value = cmds.fileDialog2(dialogStyle=2, fileMode=1, okCaption='Select File')
        if value:
            cmds.scrollField(pathUI,text=value[0],edit=True)
            NLTA_General.JsonUpdateByID({
                "path":data["sceneDataPath"]+"/ScenePatternData.json",
                "id":data["id"],
                "values":{
                    "path":value[0]
                }
            })
            module = NLTA_General.LoadModule(data["moduleName"])
            if hasattr(module, "Load"):
                module.Load(data, listUI)

    def Edit(*arr):
        path = cmds.scrollField(pathUI,query=True,text=True)
        NLTA_General.OpenSublime(path)



    #################################
    newestData = NLTA_General.JsonGetByID({
        "path":data["sceneDataPath"]+"/ScenePatternData.json",
        "id":data["id"]
    })

    if cmds.window(data["moduleName"], exists=True):
        cmds.deleteUI(data["moduleName"])

    cmds.window(data["moduleName"], title=data["title"],closeCommand=partial(data["SceneLoadFunction"],data["SceneLoadUI"],data["sceneDataPath"]))#    

    cmds.rowColumnLayout(numberOfColumns=1)

    cmds.rowColumnLayout(numberOfColumns=4)
    browserButton = cmds.button(label="Brower",width=200)
    editButton = cmds.button(label="Edit",width=200)
    cmds.setParent("..")
    
    
    cmds.rowColumnLayout(numberOfColumns=2)

    cmds.textField(text='Name',editable=False,width=100)    
    nameUI = cmds.textField(text=newestData["name"],width=300)
    cmds.textField(nameUI,edit=True,cc=partial(ChangeName,data)) 
    
    cmds.textField(text='Path',editable=False)       
    pathUI = cmds.scrollField(text=newestData['path'],wordWrap=True,height=60,editable=False)
    cmds.setParent("..")

    cmds.scrollLayout(horizontalScrollBarThickness=4,w=400,h=700)
    listUI = cmds.rowColumnLayout(nc=1,backgroundColor=(0.2, 0.2, 0.2),w=385)
    cmds.setParent("..")
    cmds.setParent("..")

    buttonUI = cmds.rowColumnLayout(nc=1,backgroundColor=(0.2, 0.2, 0.2))
    cmds.setParent("..")

    cmds.button(browserButton,edit=True,c=partial(Browser,data))
    cmds.button(editButton,edit=True,c=Edit)

    cmds.setParent("..")

    cmds.setParent("..")
    cmds.showWindow(data["moduleName"])
    return({
        "listUI":listUI,
        "buttonUI":buttonUI,
    })   