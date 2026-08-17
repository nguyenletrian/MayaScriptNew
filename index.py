toolFolder = 'D:/code/Github'
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

titleFlags = {
    'backgroundColor':(0.25, 0.25, 0.25),
    'height':25,
}
layoutFlags = {'backgroundColor':(0.3, 0.3, 0.3)}
buttonFlags = {'height':30}
inputFlags = {'height':30}

GH.CreateTool({
    'toolFolder':toolFolder,
    'paths':[],
    'UI':{
        'windowName':'NLTA_Form',
        'windowTitle':'NLTA Tools',
        'column':4,
        'layouts':[
            {
                'module':'Setup',
                'title':'Setup',
                'parent':'MainLayout',
                'titleFlags':titleFlags,            
                #'layoutFlags':layoutFlags,
                'inputFlags':inputFlags,
                'buttonFlags':buttonFlags,
            },
        ]
    }
})
'''
GH.CreateTool({
    'toolFolder':toolFolder,
    'paths':[],
    'UI':{
        'windowName':'NLTA_Form',
        'windowTitle':'NLTA Tools',
        'column':4,
        'layouts':[
            {
                'module':'Skinning',
                'title':'Skining',
                'parent':'MainLayout',
                'titleFlags':titleFlags,            
                #'layoutFlags':layoutFlags,
                'inputFlags':inputFlags,
                'buttonFlags':buttonFlags,
            },
            {
                'module':'Setup',
                'title':'Setup',
                'parent':'MainLayout',
                'titleFlags':titleFlags,            
                #'layoutFlags':layoutFlags,
                'inputFlags':inputFlags,
                'buttonFlags':buttonFlags,
            },
            {
                'module':'Scene',
                'title':'Scene',
                'parent':'MainLayout',
                'titleFlags':titleFlags,            
                #'layoutFlags':layoutFlags,
                'inputFlags':inputFlags,
                'buttonFlags':buttonFlags,
            },

            {
                'module':'Retopology',
                'title':'Retopology',
                'parent':'MainLayout',
                'titleFlags':titleFlags,            
                #'layoutFlags':layoutFlags,
                'inputFlags':inputFlags,
                'buttonFlags':buttonFlags,
            },              
        ]
    }
})
'''
