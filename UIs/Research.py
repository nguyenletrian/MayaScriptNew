import os
import json
import importlib
import maya.cmds as cmds
from functools import partial

"""

import shutil

import maya.utils

import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import xml.dom.minidom as xd
import xml.etree.ElementTree as ET

from math import pow,sqrt

"""
import NLTA_General
for module in [NLTA_General]:
    try:
        importlib.reload(module)
    except:
        reload(module)

session = {
    "currentPaths":[],
    "currentFiles":[],
    "pinnedPaths":[],
    "pinnedFiles":[],
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

    cmds.rowColumnLayout( numberOfColumns=2)
    cmds.rowColumnLayout( numberOfColumns=2)
    titles.append(cmds.textField(text="Data Name",editable=False,width=110))
    inputs.append(cmds.textField("researchDataName",text="",width=300))
    titles.append(cmds.textField(text="Folder",editable=False,width=110))
    inputs.append(cmds.textField("researchFolder",text=r"C:\Users\an.nguyen_g\Desktop\ResearcheTest",width=300))
    titles.append(cmds.textField(text="Text",editable=False,width=110))
    inputs.append(cmds.textField("researchText",text="Trian1",width=300))
    titles.append(cmds.textField(text="Exts '.py' or ['.py']",editable=False,width=110))
    inputs.append(cmds.textField("researchExts"))
    cmds.setParent("..")
    cmds.scrollLayout("dataList",height=100,width=150,bgc=(0.2, 0.2, 0.2))
    cmds.rowColumnLayout("dataListContent",nc=1)
    cmds.setParent("..")
    cmds.setParent("..")
    cmds.rowColumnLayout( numberOfColumns=4)
    buttons.append(cmds.button("SearchOK",label="Check"))
    buttons.append(cmds.button("SearchSave",label="Save Search",c=SaveResearchData))
    buttons.append(cmds.button("SearchClear",label="Pin Current Folder"))
    buttons.append(cmds.button("LoadAllPaths",label="All Paths",))
    buttons.append(cmds.button("LoadPinnedPaths",label="Pinned Paths"))
    buttons.append(cmds.button("LoadPinnedFiles",label="Pinned Files"))
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.rowColumnLayout( numberOfColumns=1)
    inputs.append(cmds.textField("researchSearchText",text="",width=300))
    itemList = cmds.scrollLayout("researchItemList",height=400,width=560)#START SCROLL    
    itemListContent = cmds.rowColumnLayout("researchItemListContent",nc=1)
    cmds.setParent("..")
    cmds.setParent("..")#END SCROLL
    cmds.setParent("..")


    cmds.setParent("..")
    cmds.setParent("..")

    #Add Command
    cmds.button("SearchOK",edit=True,command =CheckItems)
    cmds.button("LoadAllPaths",edit=True,command =LoadAllPaths)
    cmds.button("LoadPinnedPaths",edit=True,command=LoadPinnedPaths)
    cmds.button("LoadPinnedFiles",edit=True,command=LoadPinnedFiles)

    for title in titles:
        cmds.textField(title,edit=True,**titleFlags)
    for button in buttons:
        cmds.button(button,edit=True,**buttonFlags)
    for input_ in inputs:
        if cmds.objectTypeUI(input_) == 'textField':
            cmds.textField(input_,edit=True,**inputFlags)
        if cmds.objectTypeUI(input_) == 'intField':
            cmds.intField(input_,edit=True,**inputFlags)
    LoadResearchData()

#search_string,folder=r'E:\Projects\ELT',exts=None,*arr

#"E:\Projects\ELT\mechanical-arts\Python\framework\packages\mca-maya\mca\mya\tools\rigchecklist\ui\checklist.py"
#E:\Projects\ELT\mechanical-arts\Python\framework\packages\mca-maya\mca\mya\tools
"""
import sys
sys.path.append(
    r"E:\Projects\ELT\mechanical-arts\Python\framework\packages\mca-maya"
)
from mca.mya.tools.rigchecklist.actions import tpose
tpose.fk_to_tpose()
"""
"""
exts:
    None                -> tất cả file
    ".py"               -> chỉ py
    (".py", ".mel")     -> nhiều đuôi
"""

def GetDataPath(*arr):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Data","Research")
    return(path)

def LoadResearchData(*arr):    
    def DeleteData(name,*arr):
        folder = GetDataPath()
        file_name = name
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        LoadResearchData()

    def LoadData(fileName,*arr):
        global session
        folder = GetDataPath()
        filePath = os.path.join(folder, fileName)
        with open(filePath, "r", encoding="utf-8") as f:
            data = json.load(f)
            session = data
            cmds.textField("researchDataName",text=fileName.split(".")[0],edit=True)
            cmds.textField("researchFolder",edit=True,text=data["folder"])
            cmds.textField("researchText",edit=True,text=data["text"])
            cmds.textField("researchExts",edit=True,text=data["exts"])


    children = cmds.layout("dataListContent", q=True, ca=True) or []
    for child in children:
        cmds.deleteUI(child)

    folder = GetDataPath()
    for fileName in os.listdir(folder):
        if fileName.lower().endswith(".json"):
            cmds.rowColumnLayout(nc=2,parent="dataListContent")
            cmds.button(label=fileName.split(".")[0],c=partial(LoadData,fileName))
            cmds.button(label="X",c=partial(DeleteData,fileName))
            cmds.setParent("..")        

def SaveResearchData(*arr):
    global session
    folder = GetDataPath()
    dataName = cmds.textField("researchDataName",query=True,text=True)
    if dataName == "":
        
        result = cmds.promptDialog(
            title='Save Research',
            message='Enter Data Name:',
            button=['Save', 'Cancel'],
            defaultButton='Save',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result != 'Save':
            return
        data_name = cmds.promptDialog(query=True, text=True).strip()
        if not data_name:
            cmds.warning("Please enter a valid name.")
            return
    else:
        data_name = dataName

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "{}.json".format(data_name))
    session["folder"] =  cmds.textField("researchFolder",query=True,text=True)
    session["text"] = cmds.textField("researchText",query=True,text=True)
    session["exts"] = cmds.textField("researchExts",query=True,text=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=4, ensure_ascii=False)
    cmds.inViewMessage(
        amg=f'Data saved: <hl>{data_name}</hl>',
        pos='midCenter',
        fade=True
    )
    cmds.textField("researchDataName",edit=True,text=data_name)
    LoadResearchData()

def ClearList(*arr):
    children = cmds.layout("researchItemListContent", q=True, ca=True) or []
    for child in children:
        cmds.deleteUI(child)

def LoadPaths(*arr):
    def GetPath(scrollField,*arr):
        text = cmds.scrollField(scrollField,query=True,text=True)
        cmds.textField("researchFolder",edit=True,text=text)

    def PinPath(ui,*arr):
        global session
        text = cmds.scrollField(ui,query=True,text=True)
        if text not in session["pinnedPaths"]:
            session["pinnedPaths"].append(text)
        LoadPaths()

    def UnpinPath(ui, *arr):
        global session
        text = cmds.scrollField(ui, query=True, text=True)
        session["pinnedPaths"] = [
            path for path in session["pinnedPaths"]
            if path != text
        ]
        LoadPaths()
    def OpenPath(ui,*arr):
        text = cmds.scrollField(ui, query=True, text=True)
        os.startfile(text)
    ClearList()
    paths = session["currentPaths"]
    for p in paths:
        cmds.rowColumnLayout( numberOfColumns=2,parent="researchItemListContent")
        text = cmds.scrollField(text=p,h=60,ww=True,width=500)
        cmds.rowColumnLayout() 
        cmds.button(label="->",c=partial(GetPath,text))
        if p in session["pinnedPaths"]:
            cmds.button(label="Unpin",c=partial(UnpinPath, text))
        else:
            cmds.button(label="Pin",c=partial(PinPath, text))
        cmds.button(label="Open",c=partial(OpenPath, text))
        cmds.setParent("..")
        cmds.setParent("..")

def LoadPinnedPaths(*arr):
    global session
    session["currentPaths"] = session["pinnedPaths"]
    LoadPaths()

def LoadAllPaths(listUI,*arr):
    global session
    session["currentPaths"] = []
    import sys
    for p in sys.path:
        session["currentPaths"].append(p)
    LoadPaths()


#searchText = cmds.textField("researchSearchText",query=True,text=True)
def PinFile(data,*arr):
    global session
    file = data['file']
    exist = any(item["file"] == file for item in session["pinnedFiles"])
    if not exist:
        session["pinnedFiles"].append(data)
    LoadFiles()

def UnpinFile(data, *arr):
    global session
    file = data["file"]
    session["pinnedFiles"] = [
        item for item in session["pinnedFiles"]
        if item["file"] != file
    ]
    LoadFiles()

def LoadFiles(*arr):
    ClearList()
    items = session["currentFiles"]
    for item in items:
        cmds.rowColumnLayout(numberOfColumns=2,parent="researchItemListContent")
        cmds.rowColumnLayout(nc=1)
        text = cmds.scrollField(text=item["file"],h=60,ww=True)
        cmds.scrollField(text=item["text"],h=60,ww=True)
        cmds.scrollField(text=item["line"],h=60,ww=True)
        cmds.setParent("..")

        cmds.rowColumnLayout(nc=1)
        pinned = any(
            pinnedItem["file"] == item["file"]
            for pinnedItem in session["pinnedFiles"]
        )
        if pinned:
            cmds.button(label="Unpin",c=partial(UnpinFile, item))
        else:
            cmds.button(label="Pin",c=partial(PinFile, item))
        cmds.button(label="Open",c=partial(NLTA_General.OpenSublime,item["file"]))
        cmds.setParent("..")

def LoadPinnedFiles(*arr):
    global session
    session["currentFiles"] = session["pinnedFiles"]
    LoadFiles()

def CheckItems(listUI,*arr):
    global session
    folder = cmds.textField("researchFolder",query=True, text=True)
    search_string = cmds.textField("researchText",query=True, text=True)
    exts = cmds.textField("researchExts",query=True, text=True)
    session["currentFiles"] = []
    if isinstance(exts, str):
        exts = (exts.lower(),)
    elif exts:
        exts = tuple(e.lower() for e in exts)
    for root, dirs, files in os.walk(folder):
        dirs[:] = [
            d for d in dirs
            if d not in {".git","__pycache__",".idea",".vs"}
        ]
        for file in files:
            lower_file = file.lower()
            if exts and not lower_file.endswith(exts):
                continue
            full_path = os.path.join(root, file)
            try:
                found = False
                try:
                    with open(full_path,"r",encoding="utf-8",errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if search_string in line:
                                data = {"file": full_path,"line": line_num,"text": line.strip()}
                                session["currentFiles"].append(data)
                                found = True
                                break
                except:
                    pass
                if not found:
                    try:
                        with open(full_path, "rb") as f:
                            content = f.read()
                            if search_string.encode() in content:
                                data = {"file": full_path,"line": None,"text": "FOUND IN BINARY"}
                                session["currentFiles"].append(data)
                    except:
                        pass
            except Exception as e:
                print("\nERROR:")
                print(full_path)
                print(e)
    LoadFiles()