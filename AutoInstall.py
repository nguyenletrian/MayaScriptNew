import maya.cmds as cmds

toolFolder = 'D:/code/Github'
#toolFolder = 'D:/3D_WORK/code/Github/UIs/MayaScripts'

shelf = cmds.tabLayout("ShelfLayout", q=True, selectTab=True)

toolCommand = """
toolFolder = r"{toolFolder}"

import os
import sys
import importlib

if toolFolder not in sys.path:
    sys.path.append(toolFolder)

import Github as GH

try:
    importlib.reload(GH)
except:
    reload(GH)

titleFlags = {{
    'backgroundColor': (0.25, 0.25, 0.25),
    'height': 25,
}}

layoutFlags = {{
    'backgroundColor': (0.3, 0.3, 0.3)
}}

buttonFlags = {{
    'height': 33
}}

inputFlags = {{
    'height': 33
}}

GH.CreateTool({{
    'toolFolder': toolFolder,
    'paths': [],
    'UI': {{
        'windowName': 'NLTA_Form',
        'windowTitle': 'NLTA Tools',
        'column': 4,
        'layouts': [
            {{
                'module': '{moduleName}',
                'title': '{moduleName}',
                'parent': 'MainLayout',
                'titleFlags': titleFlags,
                'inputFlags': inputFlags,
                'buttonFlags': buttonFlags,
            }},
        ]
    }}
}})
"""

colors = {
    "Scene_": (0.25, 0.35, 0.25),
    "Skinning": (0.35, 0.25, 0.25),
    "Setup": (0.25, 0.25, 0.35),
}

for tool in ["Skinning", "Setup","Scene","SceneU","SceneUNew","Research"]:
    command = toolCommand.format(
        toolFolder=toolFolder,
        moduleName=tool
    )    
    cmds.shelfButton(
        parent=shelf,
        label=tool,
        imageOverlayLabel=tool,
        image1="commandButton.png",
        image="commandButton.png",
        style="iconAndTextHorizontal",
        sourceType="python",
        command=command,
        backgroundColor=(0.25, 0.35, 0.25),
        enableBackground=True,
    )