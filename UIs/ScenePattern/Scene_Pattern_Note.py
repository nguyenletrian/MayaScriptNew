import os
import pymel.core as pm
from datetime import datetime
def DefaultSetting(path,*arr):
    moduleName = os.path.basename(__file__).replace(".py","")
    return({
        "moduleName":moduleName,
        "order":0,
        "name":"",
        "path":"",
        "id":datetime.now().strftime("%Y%m%d%H%M%S")
    })