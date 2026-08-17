panel = cmds.getPanel(withFocus=True)
cmds.isolateSelect(panel, state=True)

cmds.select("pSphere1")
cmds.isolateSelect(panel, addSelected=True)

cmds.select("pSphere1")
cmds.isolateSelect(panel, removeSelected=True)

cmds.isolateSelect(panel, state=False)

cmds.isolateSelect(panel, q=True, state=True)

setName = cmds.isolateSelect(panel, q=True, viewObjects=True)
print(setName)

setName = cmds.isolateSelect(panel, q=True, viewObjects=True)
print(cmds.sets(setName, q=True))

setName = cmds.isolateSelect(panel, q=True, viewObjects=True)
cmds.sets("pCylinder1", add=setName)

panel = cmds.getPanel(withFocus=True)

if cmds.isolateSelect(panel, q=True, state=True):
    isolateSet = cmds.isolateSelect(panel, q=True, viewObjects=True)
    objs = cmds.sets(isolateSet, q=True) or []
    print(objs)