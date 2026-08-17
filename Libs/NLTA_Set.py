import maya.cmds as cmds

### SET ####
def GetSetPrefix(*arr):
    selection = cmds.ls(selection=True)
    selection0 = selection[0]
    setNamePrefix = selection0.split(".")[0]
    setNamePrefix = setNamePrefix.split(":")[-1]
    setNamePrefix = "NLTA"+setNamePrefix
    setNamePrefix = setNamePrefix.replace("|","_")
    setNamePrefix = setNamePrefix.replace(":","_")
    return(setNamePrefix)

def GetSameSetNumber(prefix,*arr):
    sets = cmds.ls(type='objectSet')
    returnNumber = 0
    for set_ in sets:
        if prefix in set_:
            returnNumber +=1
    return(returnNumber)

def CreateSet(*arr):
    selection = cmds.ls(selection=True)
    prefix = GetSetPrefix()
    order = []
    sets = cmds.ls(type='objectSet')
    for set_ in sets:
        if prefix in set_:
            order.append(int(set_.replace(prefix,"")))

    if len(order)!=0:
        newName = prefix+ str(max(order) + 1)        
    else:
        newName = prefix+ str(0)
    newSet = cmds.sets(name=newName, empty=True)
    cmds.sets(selection, add=newSet)

setIndex = 0
def NextSet(*arr):
    global setIndex
    prefix =  GetSetPrefix()
    maxNumber = GetSameSetNumber(prefix)
    if setIndex >= (maxNumber - 1):
        currentIndex = 0
    else:
        currentIndex = setIndex + 1
    sets = cmds.ls(type='objectSet')
    for set_ in sets:
        if prefix in set_:
            members = cmds.sets(set_, query=True)
            if members:
                cmds.showHidden(members)
    for set_ in sets:
        if prefix in set_:          
            members = cmds.sets(set_, query=True)
            if set_ == prefix + str(currentIndex):
                if members:
                    cmds.showHidden(members)                
            else:
                if members:
                    cmds.hide(members)
    setIndex = currentIndex

def BackSet(*arr):
    global setIndex
    prefix =  GetSetPrefix()
    maxNumber = GetSameSetNumber(prefix)
    if setIndex <= 0:
        currentIndex = (maxNumber - 1)
    else:
        currentIndex = setIndex - 1
    sets = cmds.ls(type='objectSet')
    for set_ in sets:
        if prefix in set_:
            members = cmds.sets(set_, query=True)
            if members:
                cmds.showHidden(members)                
    for set_ in sets:
        if prefix in set_:
            members = cmds.sets(set_, query=True)
            if set_ == prefix + str(currentIndex):
                if members:
                    cmds.showHidden(members)
            else:
                if members:
                    cmds.hide(members)
    setIndex = currentIndex
def DeleteSets(*arr):
    sets = cmds.ls(type='objectSet')
    for set_ in sets:
        if "NLTA" in set_:
            members = cmds.sets(set_, query=True)
            cmds.showHidden(members)
            cmds.delete(set_)