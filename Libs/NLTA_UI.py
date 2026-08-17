import maya.cmds as cmds

def FillUI(ui,value,*arr):
    ui_type = cmds.objectTypeUI(ui)
    if ui_type in ["textField", "textFieldGrp","field"]:
        cmds.textField(ui, e=True, text=value)
    elif ui_type == "cmdScrollField":
        cmds.scrollField(ui, e=True, text=value)
    elif ui_type in ["intField", "intFieldGrp"]:
        cmds.intField(ui, e=True, value=value)
    elif ui_type in ["floatField", "floatFieldGrp"]:
        cmds.floatField(ui, e=True, value=float(value))
    elif ui_type == "text":
        cmds.text(ui, e=True, label=value)
    elif ui_type == "checkBox":
        cmds.checkBox(ui, e=True, value=value)
    elif ui_type == "scrollField":
        cmds.scrollField(ui, e=True, text=value)
    elif ui_type == "radioButtonGrp":
        cmds.radioButtonGrp(ui, e=True, select=value)
    elif ui_type == "popupMenu":
        cmds.optionMenu(ui,e=True,value=value)        
    else:
        print(f"UI type '{ui_type}' chưa support")

def PickObject(ui, *args):
    objs = cmds.ls(flatten=True,os=True)
    if not objs:
        return
    string = "\n".join(objs)
    FillUI(ui,string)

def PickObjectAdd(ui,*args):
    objs = cmds.ls(flatten=True,os=True)
    if not objs:
        return
    oldValue = GetUIValue(ui)
    oldObjs = [x.strip() for x in oldValue.split("\n") if x.strip()]
    result = oldObjs[:]
    for obj in objs:
        if obj not in result:
            result.append(obj)
    FillUI(
        ui,
        "\n".join(result)
    )

def PickPos(ui, *args):
    objs = cmds.ls(os=True, flatten=True)
    if not objs:
        return
    positions = []
    for obj in objs:
        pos = cmds.xform(obj, q=True, ws=True, t=True)
        positions.append("{:.6f} {:.6f} {:.6f}".format(*pos))

    FillUI(ui, "\n".join(positions))


def PickPosAdd(ui, *args):
    objs = cmds.ls(os=True, flatten=True)
    if not objs:
        return
    oldValue = GetUIValue(ui)
    result = [line.strip() for line in oldValue.splitlines() if line.strip()]

    for obj in objs:
        pos = cmds.xform(obj, q=True, ws=True, t=True)
        posStr = "{:.6f} {:.6f} {:.6f}".format(*pos)

        if posStr not in result:
            result.append(posStr)

    FillUI(ui, "\n".join(result))

def PickObjectSemi(ui, *args):
    objs = cmds.ls(flatten=True,os=True)
    if not objs:
        return
    string = ";".join(objs)
    FillUI(ui,string)

def PickObjectSemiAdd(ui,*args):
    objs = cmds.ls(flatten=True,os=True)
    if not objs:
        return
    oldValue = GetUIValue(ui)
    string = oldValue+"\n"+";".join(objs)
    FillUI(
        ui,string
    )


def AddObject(ui, *args):
    objs = cmds.ls(flatten=True,os=True)
    if not objs:
        return
    ui_type = cmds.objectTypeUI(ui)
    if ui_type in ["textField", "textFieldGrp", "field"]:
        current = cmds.textField(ui, q=True, text=True)
        values = [x for x in current.split("\n") if x]
        values.extend(objs)
        values = list(dict.fromkeys(values))
        cmds.textField(ui, e=True, text="\n".join(values))
    elif ui_type in ["scrollField", "cmdScrollField"]:
        current = cmds.scrollField(ui, q=True, text=True)
        values = [x for x in current.split("\n") if x]
        values.extend(objs)
        values = list(dict.fromkeys(values))
        cmds.scrollField(ui, e=True, text="\n".join(values))
    elif ui_type == "optionMenu":
        items = cmds.optionMenu(ui, q=True, itemListLong=True) or []
        values = [cmds.menuItem(item, q=True, label=True) for item in items]
        values.extend(objs)
        values = list(dict.fromkeys(values))
        for item in items:
            cmds.deleteUI(item)
        for value in values:
            cmds.menuItem(label=value, parent=ui)
        if values:
            cmds.optionMenu(ui, e=True, value=values[0])
    else:
        print("UI type '{}' chưa support".format(ui_type))

def PickNamespace(ui, *args):
    objs = cmds.ls(flatten=True,os=True)
    if objs:
        obj = objs[0]
        parts = obj.split(":")
        if len(parts) <= 1:
            namespace = ""
        else:
            namespace = ":".join(parts[:-1])
        count = len(objs)
        ui_type = cmds.objectTypeUI(ui)

        if ui_type in ["textField", "textFieldGrp","field"]:
            cmds.textField(ui, e=True, text=namespace)
        elif ui_type in ["intField", "intFieldGrp"]:
            cmds.intField(ui, e=True, value=count)
        elif ui_type in ["floatField", "floatFieldGrp"]:
            cmds.floatField(ui, e=True, value=float(count))
        elif ui_type == "text":
            cmds.text(ui, e=True, label=namespace)
        elif ui_type == "optionMenu":
            items = cmds.optionMenu(ui, q=True, itemListLong=True) or []
            for item in items:
                cmds.deleteUI(item)
            namespaces = []
            for o in objs:
                p = o.split(":")
                ns = ":".join(p[:-1]) if len(p) > 1 else ""
                namespaces.append(ns)
            namespaces = list(set(namespaces))
            for ns in namespaces:
                cmds.menuItem(label=ns, parent=ui)
            if namespaces:
                cmds.optionMenu(ui, e=True, value=namespaces[0])
        elif ui_type == "checkBox":
            cmds.checkBox(ui, e=True, value=bool(namespace))
        elif ui_type == "scrollField":
            cmds.scrollField(ui, e=True, text=namespace)

        else:
            print(f"UI type '{ui_type}' chưa support")

def ClearUI(ui,*arr):
    children = cmds.rowColumnLayout(ui, q=True, childArray=True)
    if children:
        for child in children:
            cmds.deleteUI(child)

def GetData(inputDict,*arr):
    uiQuery = {
        "field": lambda ui: cmds.textField(ui, q=True, text=True),
        "textField": lambda ui: cmds.textField(ui, q=True, text=True),
        "scrollField": lambda ui: cmds.scrollField(ui, q=True, text=True),
        "cmdScrollField": lambda ui: cmds.scrollField(ui, q=True, text=True),
        "checkBox": lambda ui: cmds.checkBox(ui, q=True, value=True),
        "intField": lambda ui: cmds.intField(ui, q=True, value=True),
        "floatField": lambda ui: cmds.floatField(ui, q=True, value=True),
        "popupMenu": lambda ui: cmds.optionMenu(ui, q=True, value=True),
        "radioButtonGrp":lambda ui: cmds.radioButtonGrp(ui, e=True, select=True)
    }
    returnData = []
    for item in inputDict:
        itemData = {}
        for key, ui in inputDict[item].items():
            uiType = cmds.objectTypeUI(ui)
            if uiType in uiQuery:
                value = uiQuery[uiType](ui)
            else:
                print("Unsupported UI Type:", uiType)
                value = None
            itemData[key[0].lower() + key[1:]] = value
        returnData.append(itemData)
    return returnData

def GetUIValue(ui):
    uiType = cmds.objectTypeUI(ui)
    queryMap = {
        "field": lambda x: cmds.textField(x, q=True, text=True),
        "textField": lambda x: cmds.textField(x, q=True, text=True),
        "scrollField": lambda x: cmds.scrollField(x, q=True, text=True),
        "cmdScrollField": lambda x: cmds.scrollField(x, q=True, text=True),
        "checkBox": lambda x: cmds.checkBox(x, q=True, value=True),
        "intField": lambda x: cmds.intField(x, q=True, value=True),
        "floatField": lambda x: cmds.floatField(x, q=True, value=True),
        "optionMenu": lambda x: cmds.optionMenu(x, q=True, value=True),
        "textFieldGrp": lambda x: cmds.textFieldGrp(x, q=True, text=True),
        "intFieldGrp": lambda x: cmds.intFieldGrp(x, q=True, value1=True),
        "floatFieldGrp": lambda x: cmds.floatFieldGrp(x, q=True, value1=True),
        "radioButtonGrp":lambda ui: cmds.radioButtonGrp(ui, e=True, select=True)
    }
    if uiType not in queryMap:
        raise RuntimeError("Unsupported UI Type: {}".format(uiType))
    return queryMap[uiType](ui)

def GetSelectedAttribute(*arr):
    objs =  cmds.ls(flatten=True,os=True)
    if objs:
        returnData = {
            "allAttr":[]
        }
        mainAttr = cmds.channelBox("mainChannelBox",query=True,sma=True)
        if mainAttr:
            returnData["main"] = mainAttr
            returnData["allAttr"].extend(mainAttr)
        shapeAttr = cmds.channelBox("mainChannelBox",query=True,ssa=True)
        if shapeAttr:
            returnData["shape"] = shapeAttr
            returnData["allAttr"].extend(shapeAttr)
        inputAttr = cmds.channelBox("mainChannelBox",query=True,sha=True)
        if inputAttr:
            returnData["input"] = inputAttr
            returnData["allAttr"].extend(inputAttr)
        outputAttr = cmds.channelBox("mainChannelBox",query=True,soa=True)
        if outputAttr:
            returnData["output"] = outputAttr
            returnData["allAttr"].extend(outputAttr)
        returnData["objs"] = objs
        return(returnData)
    return(None)

def GetAttributeInfo(node, attr):
    full = "{}.{}".format(node, attr)
    data = {}
    data["name"] = attr
    data["type"] = cmds.getAttr(full, type=True)
    data["keyable"] = cmds.getAttr(full, k=True)
    data["lock"] = cmds.getAttr(full, l=True)
    data["channelBox"] = cmds.getAttr(full, cb=True)
    if cmds.attributeQuery(attr, node=node, minExists=True):
        data["min"] = cmds.attributeQuery(attr, node=node, minimum=True)[0]
    if cmds.attributeQuery(attr, node=node, maxExists=True):
        data["max"] = cmds.attributeQuery(attr, node=node, maximum=True)[0]
    if cmds.attributeQuery(attr, node=node, listDefault=True):
        default = cmds.attributeQuery(attr, node=node, listDefault=True)
        if default:
            data["default"] = default[0]
    if data["type"] == "enum":
        enum = cmds.attributeQuery(attr, node=node, listEnum=True)
        if enum:
            data["enum"] = enum[0]
    return data

def PickAttrs(ui,*arr):
    attrData = GetSelectedAttribute()
    returnData = []
    if attrData:
        for obj in attrData["objs"]:         
            for attr in attrData["allAttr"]:
                returnData.append(obj+"."+attr)
        FillUI(ui,("\n").join(returnData))

def PickAttr(ui,*arr):
    attrData = GetSelectedAttribute()
    if attrData and attrData["main"]:
        FillUI(
            ui,
            attrData["objs"][0]+"."+attrData["main"][0]
        )

def PickAttrOnly(ui,*arr):
    attrData = GetSelectedAttribute()
    if attrData and attrData["main"]:
        FillUI(
            ui,
            attrData["main"][0]
        )

def PickAttrsAdd(ui,*arr):
    attrData = GetSelectedAttribute()
    returnData = GetUIValue(ui).split("\n")
    if attrData:
        for obj in attrData["objs"]:         
            for attr in attrData["allAttr"]:
                returnData.append(obj+"."+attr)
        FillUI(ui,("\n").join(returnData))

