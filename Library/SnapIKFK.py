__authors__ = "PhucHoang"

import json
# import cPickle
import pymel.all as pm
from functools import partial

if float(pm.about(version=True)) >= 2022:
    unicode = str


class UIsnapIKFK(object):
    """docstring for snapIKFK_newVer"""

    def __init__(self):
        super(UIsnapIKFK, self).__init__()
        self.ui_snapIKFK()

    def ui_snapIKFK(self, *arg):
        if (pm.window('ui_snapIKFK', query=True, exists=True)):
            pm.deleteUI('ui_snapIKFK')

        pm.window('ui_snapIKFK', t='Snap IK FK Tool', s=1)
        pm.window('ui_snapIKFK', e=True, w=400, h=210)
        pm.columnLayout(adj=True, rs=5)
        pm.separator(st='shelf')
        pm.textFieldButtonGrp("TF_ctrlParentUI", ekf=False, l='Control Parent UI: ', bl='Choose', adj=2,
                              cw3=(110, 230, 50), cl3=('left', 'left', 'left'))
        pm.radioButtonGrp('TF_ctrlTypeUI', numberOfRadioButtons=2, label='Controller Type: ', adj=3,
                          labelArray2=['Add Attribute', 'New Ctrl'], cl3=('left', 'left', 'left'), select=0)
        pm.textFieldButtonGrp("TF_ctrlSwitchMode", l='Control Switch IK/FK: ', bl='Choose', adj=2, cw3=(110, 230, 50),
                              cl3=('left', 'left', 'left'), pht='Switch IK/FK')

        pm.rowLayout(nc=5, adj=1, cl3=('left', 'both', 'right'), ct3=('left', 'both', 'right'))
        pm.textFieldGrp('TF_handAttr', l='Attribute IkFk: ', adj=2, cl2=('left', 'right'), cw=(1, 110))
        pm.intFieldGrp('IF_fkValue', l='FK: ', cw2=(20, 25))
        pm.intFieldGrp('IF_ikValue', l='IK: ', cw2=(15, 25), v1=1)
        pm.button('buttonAssist', l='Assist')
        pm.setParent('..')

        pm.textFieldButtonGrp("TF_ctrlUpper", ekf=False, l='Control Upper Limb: ', bl='Choose', adj=2,
                              cw3=(110, 230, 50), cl3=('left', 'left', 'left'), pht='Upper Limb Controller')

        pm.textFieldButtonGrp("TF_ctrlFK", ekf=False, l='Control FK: ', bl='Choose', adj=2, cw3=(110, 230, 50),
                              cl3=('left', 'left', 'left'), pht='Shoulder -> Elbow -> Wrist')
        pm.textFieldButtonGrp("TF_ctrlIK", ekf=False, l='Control IK: ', bl='Choose', adj=2, cw3=(110, 230, 50),
                              cl3=('left', 'left', 'left'), pht='WristIK -> Pole Vector')
        pm.textFieldButtonGrp("TF_ctrlRollToes", ekf=False, l='Control Roll Toes: ', bl='Choose', adj=2,
                              cw3=(110, 230, 50), cl3=('left', 'left', 'left'), pht='Roll Toes')
        pm.textFieldButtonGrp("TF_jointIK", ekf=False, l='Joint IK: ', bl='Choose', adj=2, cw3=(110, 230, 50),
                              cl3=('left', 'left', 'left'), pht='Shoulder_IKJnt -> Elbow_IKJnt -> Wrist_IKJnt')

        pm.separator(st='out')
        pm.button("TF_ctrlFK_autoPick",
                  label="Auto Pick The Parts (Only AdvancedSkeleton)\n Select any object related to limb")
        pm.separator(st='out')

        pm.rowLayout(nc=4, adj=1, ca=True, cl4=('left', 'right', 'right', 'right'),
                     ct4=('left', 'right', 'right', 'right'))
        pm.checkBox('CB_mirror', l='Mirror', v=True)
        pm.button('buttonSetup', l='Setup', h=40, w=120, bgc=(0, 1, 0))
        pm.button('buttonReload', l='Reload', h=40, w=120, bgc=(1, 1, 0))
        pm.button('button_deleteSetup', l='Delete', h=40, w=120, bgc=(1, 0, 0))
        pm.setParent('..')

        pm.separator(st='shelf')

        pm.rowLayout(nc=2)
        pm.button('btIKFK_export', l='Export Data', w=250, h=40)
        pm.button('btIKFK_import', l='Import Data', w=250, h=40)
        pm.setParent('..')

        pm.showWindow('ui_snapIKFK')


class SetupSnapIKFK(UIsnapIKFK):
    def __init__(self):
        super(SetupSnapIKFK, self).__init__()
        self.nameAttrTransform = ['_trans', '_rot']
        self.namDataAttr = ['fkMode', 'ikMode', 'attrBlend']
        self.nameListIK = ['mainIK', 'poleIK']
        self.nameListIK_jnt = ['startJnt', 'middleJnt', 'endJnt']
        self.nameListFK = ['startFK', 'middleFK', 'endFK']
        self.nameUpper = 'upperLimb'
        self.nameRollToes = 'rollToes'
        self.nameRollToesOffset = "rollToesOffset"

        self.snap_total_list = dict()
        self.dict_query_select = dict()
        self.alphaList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                          't', 'u', 'v', 'w', 'x', 'y', 'z', 'ab', 'cd', 'ef', 'gh', 'ij', 'kl']
        self.list_check_LR = {'l_': 'r_', '_l_': '_r_', '_l': '_r', 'L_': 'R_', '_L_': '_R_', '_L': '_R',
                              'r_': 'l_', '_r_': '_l_', '_r': '_l', 'R_': 'L_', '_R_': '_L_', '_R': '_L',
                              'LF_': 'RT_', '_LF_': '_RT_', '_LF': '_RT', 'RT_': 'LF_', '_RT_': '_LF_', '_RT': '_LF'}
        self.define_commandUI()

    def define_commandUI(self, *arg):

        pm.textFieldButtonGrp("TF_ctrlParentUI", e=True,
                              bc=partial(self.updateTextField, "TF_ctrlParentUI", "parentUI"))
        pm.textFieldButtonGrp("TF_ctrlSwitchMode", e=True,
                              bc=partial(self.updateTextField, "TF_ctrlSwitchMode", "ctrlSw"))

        pm.textFieldButtonGrp("TF_ctrlUpper", e=True, bc=partial(self.updateTextField, "TF_ctrlUpper", "ctrlUpper"))

        pm.textFieldButtonGrp("TF_ctrlFK", e=True, bc=partial(self.updateTextField, "TF_ctrlFK", "ctrlFK"))
        pm.textFieldButtonGrp("TF_ctrlIK", e=True, bc=partial(self.updateTextField, "TF_ctrlIK", "ctrlIK"))
        pm.textFieldButtonGrp("TF_ctrlRollToes", e=True,
                              bc=partial(self.updateTextField, "TF_ctrlRollToes", "RollToes"))
        pm.textFieldButtonGrp("TF_jointIK", e=True, bc=partial(self.updateTextField, "TF_jointIK", "jointIK"))

        pm.intFieldGrp('IF_fkValue', e=True, cc=partial(self.changeValueMode_IKFK, 'IF_fkValue', 'fkMode'))
        pm.intFieldGrp('IF_ikValue', e=True, cc=partial(self.changeValueMode_IKFK, 'IF_ikValue', 'ikMode'))

        pm.button('buttonAssist', edit=True, c=self.assist_switchIKFK)

        pm.button('buttonSetup', e=True, c=self.setupIKFK)
        pm.button('button_deleteSetup', e=True, c=self.deleteSnap_IKFK)
        pm.button('buttonReload', e=True, c=self.reloadSnap_IKFK)

        pm.button('btIKFK_export', e=True, c=self.snapIKFK_exportData)
        pm.button('btIKFK_import', e=True, c=self.snapIKFK_importData)

        pm.button("TF_ctrlFK_autoPick", edit=True, command=self.autoPickTheParts)

    def autoPickTheParts(self, *args):
        currentSl = pm.ls(sl=True)
        if not currentSl: return
        ctrl_switchIKFK = self.getControlSwitchIKFK(currentSelect=currentSl[0])
        if (ctrl_switchIKFK.name().find("Spline") > -1) or (ctrl_switchIKFK.name().find("Spine") > -1):
            return

        pm.textFieldButtonGrp("TF_ctrlSwitchMode", edit=True, text=ctrl_switchIKFK.name())
        pm.textFieldGrp('TF_handAttr', edit=True, text="FKIKBlend")
        pm.intFieldGrp('IF_fkValue', e=True, value1=0)
        pm.intFieldGrp('IF_ikValue', e=True, value1=10)

        self.dict_query_select['ctrlSw'] = [ctrl_switchIKFK.name()]
        self.dict_query_select['attrBlend'] = "FKIKBlend"
        self.dict_query_select['fkMode'] = 0
        self.dict_query_select['ikMode'] = 10

        nameSpace = ''
        if len(ctrl_switchIKFK.split(":")) > 1:
            nameSpace = ctrl_switchIKFK.split(":")[0]
            nameSpace += ":"
        name = ctrl_switchIKFK.split(":")[-1]
        tempString = name.split("_")
        side = "_" + tempString[-1]
        IK = tempString[0].split("FKIK")[-1]

        poleCurve = nameSpace + "Pole" + IK + side
        startJoint = pm.getAttr(ctrl_switchIKFK + ".startJoint")
        middleJoint = pm.getAttr(ctrl_switchIKFK + ".middleJoint")
        endJoint = pm.getAttr(ctrl_switchIKFK + ".endJoint")

        self.dict_query_select["ctrlFK"] = [
            "FK%s%s" % (startJoint, side),
            "FK%s%s" % (middleJoint, side),
            "FK%s%s" % (endJoint, side)]

        self.dict_query_select["ctrlIK"] = [
            "IK%s%s" % (IK, side),
            "Pole%s%s" % (IK, side)]

        self.dict_query_select["jointIK"] = [
            "IKX%s%s" % (startJoint, side),
            "IKX%s%s" % (middleJoint, side),
            "IKX%s%s" % (endJoint, side)]

        pm.textFieldButtonGrp("TF_ctrlFK", e=True, text=self.nameListField(self.dict_query_select["ctrlFK"]))
        pm.textFieldButtonGrp("TF_ctrlIK", e=True, text=self.nameListField(self.dict_query_select["ctrlIK"]))
        pm.textFieldButtonGrp("TF_jointIK", e=True, text=self.nameListField(self.dict_query_select["jointIK"]))

    def getControlSwitchIKFK(self, currentSelect):
        foundIK = False
        ctrl_blendIKFK = False

        if currentSelect.find("FKIK") > -1:
            ctrl_blendIKFK = currentSelect
            foundIK = True

        if not foundIK:
            tempString = currentSelect
            for i in range(99):
                tempString = pm.listRelatives(tempString, parent=True)
                if not tempString: break
                tempString2 = pm.listConnections(tempString[0].v, source=True, destination=False)
                if not tempString2: continue
                if not isinstance(tempString2[0], pm.Condition): continue
                tempString2 = pm.listConnections(tempString2[0].firstTerm, source=True, destination=False)
                if not tempString2: continue
                ctrl_blendIKFK = tempString2[0]
                foundIK = True
                break

        if not foundIK:
            tempString = pm.listRelatives(currentSelect, shapes=True)
            if tempString: tempString = pm.listConnections(tempString[0].v, source=True, destination=False)
            if not tempString: return False
            if isinstance(tempString[0], pm.PlusMinusAverage):
                tempString = pm.listConnections(tempString[0].input1D[0], source=True, destination=False,
                                                skipConversionNodes=True)
            if isinstance(tempString[0], pm.Condition):
                tempString2 = pm.listConnections(tempString[0].firstTerm, source=True, destination=False,
                                                 skipConversionNodes=True)
                ctrl_blendIKFK = tempString2[0]
                foundIK = True

        if not foundIK: return False
        return ctrl_blendIKFK

    def assist_switchIKFK(self, *args):
        ctrl_switch = pm.textFieldButtonGrp("TF_ctrlSwitchMode", query=True, text=True) or ""
        attr_switch = pm.textFieldGrp('TF_handAttr', query=True, text=True) or ""
        ctrl_attr_switch = "%s.%s" % (ctrl_switch, attr_switch)
        value_fk = pm.intFieldGrp('IF_fkValue', query=True, value1=True)
        value_ik = pm.intFieldGrp('IF_ikValue', query=True, value1=True)

        if pm.objExists(ctrl_attr_switch):
            get_value = pm.getAttr(ctrl_attr_switch)
            if get_value == value_fk:
                pm.setAttr(ctrl_attr_switch, value_ik)
            elif get_value == value_ik:
                pm.setAttr(ctrl_attr_switch, value_fk)
            else:
                pm.setAttr(ctrl_attr_switch, value_fk)
        else:
            pm.warning("%s: \"%s\" does not exist" % (__name__, ctrl_attr_switch))

    def snapIKFK_exportData(self, *arg):
        nodeMain = pm.ls('*pRig_trickRig', r=True)

        if not nodeMain:
            pm.displayInfo('No Node: pRig_trickRig')
            return

        self.nameAttrTransform = ['_trans', '_rot']

        nameListFK_4Leg = self.nameListFK[:]
        nameListFK_4Leg.insert(2, 'middleFK2')
        nameListIK_jnt_4Leg = self.nameListIK_jnt[:]
        nameListIK_jnt_4Leg.insert(2, 'middleJnt2')

        listCtrl_FK_attrTransform = []
        for i in nameListFK_4Leg:
            for a in self.nameAttrTransform:
                listCtrl_FK_attrTransform.append(i + a)

        listCtrl_IK_attrTransform = []
        for i in self.nameListIK:
            for a in self.nameAttrTransform:
                listCtrl_IK_attrTransform.append(i + a)

        attrName = ['ctrlSwitch', 'ctrlUpper']

        listAllData = self.namDataAttr + self.nameListIK + attrName + nameListIK_jnt_4Leg + nameListFK_4Leg + listCtrl_FK_attrTransform + listCtrl_IK_attrTransform

        dictData = dict()
        dataList = pm.listConnections(nodeMain[0].nodeDataSnapIKFK)
        dataList.sort()

        check_ctrl_type = nodeMain[0].UI.get().hasAttr("snapIkFk_addAttr")
        if not check_ctrl_type:
            get_parent = nodeMain[0].UI.get().listRelatives(parent=True)
            if get_parent:
                get_parent = get_parent[0].name()
            else:
                get_parent = ""

        dictData["mainData"] = {
            "parentUI": nodeMain[0].UI.get().name() if check_ctrl_type else get_parent,
            "ctrlType": int(check_ctrl_type)
        }

        for nodeData in dataList:
            quantity = nodeData.split('_')[1]
            dictData[quantity] = dict()
            for attr in listAllData:
                if not nodeData.hasAttr(attr):
                    continue
                queryData = pm.getAttr(nodeData + '.{0}'.format(attr))
                if isinstance(queryData, tuple):
                    queryData = list(queryData)
                elif isinstance(queryData, unicode):
                    queryData = queryData
                else:
                    queryData = queryData.name()

                dictData[quantity][attr] = queryData

        self.exportData(dictData)

    def snapIKFK_importData(self, *arg):
        dataImport = self.importSkin()

        if pm.objExists('pRig_trickRig'):
            transformNode_Snap = pm.PyNode('pRig_trickRig')
        else:
            transformNode_Snap = self.createNode_mainPRig()

        self.addScriptUI(transformNode_Snap)
        self.create_controlUI(ctrlParent=dataImport["mainData"]["parentUI"],
                              ctrlType=dataImport["mainData"]["ctrlType"], transformNode_Snap=transformNode_Snap)
        self.define_scriptNode(transformNode_Snap)

        if not transformNode_Snap.hasAttr('nodeDataSnapIKFK'):
            pm.addAttr(transformNode_Snap, ln='nodeDataSnapIKFK', at='message')

        for i in dataImport:
            if i == "mainData":
                continue
            str_dataNode = 'snapIKFK_{}_dataNode'.format(i)
            if pm.objExists(str_dataNode):
                nodeSaveData = pm.PyNode(str_dataNode)
            else:
                nodeSaveData = pm.createNode('network', n=str_dataNode)
                pm.addAttr(nodeSaveData, ln='nodeData', type='message')

            if not nodeSaveData.hasAttr('mainNodePRig'):
                pm.addAttr(nodeSaveData, ln='mainNodePRig', at='message')
            transformNode_Snap.nodeDataSnapIKFK >> nodeSaveData.mainNodePRig

            # nodeSaveData.setParent(transformNode_Snap)
            for attr in dataImport[i]:
                if not nodeSaveData.hasAttr(attr):
                    if ('trans' in attr) or ('rot' in attr):
                        pm.addAttr(nodeSaveData, ln=attr, type='float3')
                    elif ('Mode' in attr) or ('Blend' in attr):
                        pm.addAttr(nodeSaveData, ln=attr, dt='string')
                    else:
                        pm.addAttr(nodeSaveData, ln=attr, at='message')

                if pm.attributeQuery(attr, n=str_dataNode, at=True) == 'message':
                    nodeConnect = pm.nt.Transform(dataImport[i][attr])
                    if not nodeConnect.hasAttr('nodeData') and (not attr.find('Jnt') > -1):
                        nodeConnect.addAttr('nodeData', at='message')

                    pm.connectAttr(nodeConnect.message, nodeSaveData + '.{}'.format(attr), f=True)

                    if nodeConnect.hasAttr('nodeData'):
                        pm.connectAttr(nodeSaveData.nodeData, nodeConnect.nodeData, f=True)
                else:
                    pm.setAttr(nodeSaveData + '.{}'.format(attr), lock=False)
                    pm.setAttr(nodeSaveData + '.{}'.format(attr), dataImport[i][attr], lock=True)

            pm.displayInfo('Setup data: {} DONE !!!'.format(nodeSaveData))

    def chooseFile(self, mode, fileMode=0, *arg):
        basicFilter = "*.json"
        dir = pm.fileDialog2(fileFilter=basicFilter, fm=fileMode, dialogStyle=2, cap=mode + ' Data', okc=mode)
        return dir

    def importSkin(self, *arg):
        dir = self.chooseFile('Import', fileMode=1)

        if dir != None:
            dir = dir[0]
            with open(dir) as f:
                myData = json.load(f)
                myDict = myData
                # myDict = self.deserializePickleData(myData)
                return myDict

    def exportData(self, dictData, *arg):
        dir = self.chooseFile('Export')
        if dir:
            dir = dir[0]
            with open(dir, "w") as f:
                dataExport = dictData
                # dataExport = self.serializePickleData(dictData)
                json.dump(dataExport, f, indent=4)

            pm.displayInfo('Save Data SnapIKFK ended successfully; \nLocation: {};'.format(dir))

    def replacePybrary(self, objAttrDataStr):
        """
        Replaces pybrary imports from `objAttrDataStrIn`

        Args:
            objAttrDataStrIn (str): Data Pickle String

        Returns:
            (str): Data string with replaced pybrary imports
        """

        # Replace all the pybrary component in serialized string.
        subbedStr = objAttrDataStr.replace('\(cpybrary\.snapIKFK.', '')

        return subbedStr

    def deserializePickleData(self, objAttr):
        """
        Reads `objAttr`'s pickle data

        Args:
            objAttr (str): Attribute to retrieve pickle data on

        Returns:
            (void): Read Pickle Data
        """
        attrData = self.replacePybrary(objAttr)
        loadedData = cPickle.loads(str(attrData))
        return loadedData

    def serializePickleData(self, data):
        """
        Pickle `data` to `objAttr`

        Args:
            objAttr (str): Object Attribute
            data (void): Data to Dump

        Returns:
            none
        """
        stringData = cPickle.dumps(data)
        stringData = '\(cpybrary\.snapIKFK.' + stringData + '\(cpybrary\.snapIKFK.'
        return stringData

    def nameListField(self, bien1):
        myName = ''
        for i, val in enumerate(bien1):
            if isinstance(val, pm.PyNode):
                ten = val.name()
            else:
                ten = val[:]
            if i == 0:
                myName += ten
            else:
                myName += ', ' + ten
        return myName

    def updateTextField(self, TF_ui, name, *arg):
        mySelect = pm.ls(sl=True)

        myNameSelect = self.nameListField(mySelect)
        pm.textFieldButtonGrp(TF_ui, e=True, tx=myNameSelect)

        if name != 'parentUI':
            if TF_ui == 'TF_ctrlSwitchMode':
                nameAttr = self.search_attr_switch_IkFk(mySelect[0])
                if not nameAttr == '':
                    pm.textFieldGrp('TF_handAttr', e=True, tx=nameAttr)
                else:
                    nameAttr = pm.textFieldGrp('TF_handAttr', q=True, tx=True)
                self.dict_query_select['attrBlend'] = nameAttr

                fkMode = pm.intFieldGrp('IF_fkValue', q=True, v1=True)
                ikMode = pm.intFieldGrp('IF_ikValue', q=True, v1=True)

                self.dict_query_select['fkMode'] = fkMode
                self.dict_query_select['ikMode'] = ikMode

            if name in self.dict_query_select.keys():
                self.dict_query_select.pop(name)

            self.dict_query_select[name] = [i.name() for i in mySelect]
        else:
            self.ctrlParentUI = mySelect[0].name()

    def changeValueMode_IKFK(self, ui_IKFK_value, mode, *arg):
        valueMode = pm.intFieldGrp(ui_IKFK_value, q=True, v1=True)
        self.dict_query_select[mode] = valueMode

    def search_attr_switch_IkFk(self, bien1):
        name_attr_switch = ['IkFk', 'IKFK', 'ikfk', 'FKIK', 'FkIk', 'fkik', 'iKfK', 'fKiK', 'ikBlend', 'fkBlend',
                            'FKIKBlend', 'FK_IK', 'IK_FK_switch']
        attr_list = pm.listAttr(bien1, ud=True)

        nameAttr_ikfk = ''
        breakLoop = False
        for i in attr_list:
            for a in name_attr_switch:
                if i.find(a) > -1:
                    nameAttr_ikfk = i
                    breakLoop = True
                    break
            if breakLoop:
                break
        return nameAttr_ikfk

    # ************************************************** DEF query Selection Mirror ******************************************************************

    def query_mirror(self, *arg):
        self.snap_total_list = dict()
        listNoRun = ['fkMode', 'ikMode', 'attrBlend']
        nameSelect = ''
        nameMirror = ''
        for a in self.dict_query_select:
            if not a in listNoRun:
                for b in self.dict_query_select[a]:
                    for key in self.list_check_LR.keys():
                        nameSelect = key
                        nameMirror = self.list_check_LR[key]
                        if b.find(nameSelect) > -1:
                            newName = b[:]
                            newName = newName.replace(nameSelect, nameMirror)
                            if not pm.objExists(newName):
                                continue
                            newNameNode = pm.nt.Transform(newName)

                            if not nameMirror in self.snap_total_list.keys():
                                self.snap_total_list[nameMirror] = {}

                            if not a in self.snap_total_list[nameMirror].keys():
                                self.snap_total_list[nameMirror][a] = []

                            self.snap_total_list[nameMirror][a].append(newNameNode)
                            break

        if self.snap_total_list:
            for a in listNoRun:
                self.snap_total_list[nameMirror][a] = self.dict_query_select[a]

        self.snap_total_list[nameSelect] = self.dict_query_select

        return nameSelect, nameMirror

    # ************************************************** DEF addAttr & Connect Message ******************************************************************

    def addAttr_connectMessage(self, ctrlAddAttr, nameAttr, ctrlMessage):
        pm.addAttr(ctrlAddAttr, ln=nameAttr, at='message')
        pm.connectAttr(pm.PyNode(ctrlMessage).message, ctrlAddAttr + '.{}'.format(nameAttr))

    # ************************************************** DEF add Data String ******************************************************************

    def addAttr_dataString(self, ctrlAddAttr, nameAttr, dataString):
        pm.addAttr(ctrlAddAttr, ln=nameAttr, dt='string')
        pm.setAttr(ctrlAddAttr + '.{}'.format(nameAttr), dataString, typ='string', l=True)

    # ************************************************** DEF Query Trans, Rot offset & Set Attr ******************************************************************

    def query_transRot_setAttr(self, ctrlQuery, nodeSaveData, longname, *arg):
        trans, rot = self.queryData_Trans_Rot(ctrlQuery, spaceTrans='object', spaceRot='object')

        valueTransform = [trans, rot]

        for i, val in enumerate(self.nameAttrTransform):
            pm.addAttr(nodeSaveData, ln=longname + val, type='float3')
            pm.setAttr(nodeSaveData + '.' + longname + val, valueTransform[i], l=True)

    # ************************************************** DEF Query Data Translation & Rotation ******************************************************************

    def queryData_Trans_Rot(self, ctrl, spaceTrans='world', spaceRot='world', *arg):
        get_pos = ctrl.getTranslation(space=spaceTrans)
        get_rot = ctrl.getRotation(space=spaceRot)

        return get_pos, get_rot

    # ************************************************** DEF Lock & Hide Attribute ******************************************************************

    def lockHideAttr(self, ctrl, lock, hide, *arg):
        attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
        for i in attr:
            valueHide = (int(hide) - 1) * -1
            pm.setAttr(ctrl + '.' + i, lock=lock, k=valueHide)

    def createNode_mainPRig(self):
        transformNode_Snap = pm.createNode('network', n='pRig_trickRig')
        pm.addAttr(transformNode_Snap, ln='script_node', at='message')
        pm.addAttr(transformNode_Snap, ln='nodeDataSnapIKFK', at='message')
        return transformNode_Snap

    def create_controlUI(self, ctrlParent=None, ctrlType=None, transformNode_Snap=None):
        if ctrlType is None:
            ctrl_type = pm.radioButtonGrp('TF_ctrlTypeUI', query=True, select=True)
        else:
            ctrl_type = ctrlType
        if ctrl_type == 1:
            ctrlParent = pm.PyNode(ctrlParent)
            if not ctrlParent.hasAttr("UI"): ctrlParent.addAttr('UI', at='message')
            if not ctrlParent.hasAttr("snapIkFk"): ctrlParent.addAttr('snapIkFk', at='bool', keyable=True,
                                                                      niceName='Snap IK/FK')
            if not ctrlParent.hasAttr("snapIkFk_addAttr"): ctrlParent.addAttr('snapIkFk_addAttr', at='bool',
                                                                              hidden=True)
            ctrlParent.snapIkFk.set(keyable=False, cb=True)
            ctrlUI = ctrlParent
        else:
            if not (pm.objExists('Rig_UI')):
                ctrlUI = self.ctrlUI()
                if ctrlParent:
                    pm.delete(pm.parentConstraint(ctrlParent, ctrlUI))
                    ctrlUI.setParent(ctrlParent)
                self.lockHideAttr(ctrlUI, lock=True, hide=True)
                pm.addAttr(ctrlUI, ln='UI', at='message')

                pm.addAttr(ctrlUI, ln='snapIkFk', at='bool', keyable=True, niceName='Snap IK/FK')
                pm.setAttr(ctrlUI.snapIkFk, cb=True)
            else:
                ctrlUI = pm.PyNode('Rig_UI')

        if not transformNode_Snap.hasAttr('UI'):
            pm.addAttr(transformNode_Snap, ln='UI', at='message')

        transformNode_Snap.UI >> ctrlUI.UI
        return ctrlUI

    # *********************************************** DEF Setup IKFK *****************************************

    def setupIKFK(self, *arg):
        list_dataString = ['attrBlend', 'fkMode', 'ikMode']

        nameListFK_4Leg = self.nameListFK[:]
        nameListFK_4Leg.insert(2, 'middleFK2')
        nameListIK_jnt_4Leg = self.nameListIK_jnt[:]
        nameListIK_jnt_4Leg.insert(2, 'middleJnt2')

        index_alphaList = 0
        listSetup = []
        checkMirror = pm.checkBox('CB_mirror', q=True, v=True)
        nameSelect, nameMirror = self.query_mirror()
        listSetup = [nameSelect]

        if checkMirror:
            listSetup.append(nameMirror)

        for i in listSetup:
            if self.snap_total_list[i]['attrBlend'] == '':
                nameAttr = pm.textFieldGrp('TF_handAttr', q=True, tx=True)
                self.snap_total_list[i]['attrBlend'] = nameAttr

        if not (pm.objExists('pRig_trickRig')):
            transformNode_Snap = self.createNode_mainPRig()
        else:
            transformNode_Snap = pm.ls('pRig_trickRig')[0]
            if transformNode_Snap.hasAttr('nodeDataSnapIKFK'):
                allNode_connect = pm.listConnections(transformNode_Snap.nodeDataSnapIKFK, s=True)
                index_alphaList = len(allNode_connect)
            else:
                pm.addAttr(transformNode_Snap, ln='nodeDataSnapIKFK', at='message')

        self.addScriptUI(transformNode_Snap)
        self.create_controlUI(ctrlParent=self.ctrlParentUI, transformNode_Snap=transformNode_Snap)

        for i in listSetup:
            nodeSaveData = pm.createNode('network', n='snapIKFK_{}_dataNode'.format(self.alphaList[index_alphaList]))
            index_alphaList += 1
            # self.lockHideAttr(nodeSaveData, lock = True, hide = True)
            # nodeSaveData.setParent(transformNode_Snap)

            pm.addAttr(nodeSaveData, ln='mainNodePRig', at='message')
            transformNode_Snap.nodeDataSnapIKFK >> nodeSaveData.mainNodePRig

            if not nodeSaveData.hasAttr('nodeData'):
                pm.addAttr(nodeSaveData, ln='nodeData', at='message')

            ctrlSwitch_IKFK = pm.PyNode(self.snap_total_list[i]['ctrlSw'][0])

            if not ctrlSwitch_IKFK.hasAttr('nodeData'):
                pm.addAttr(ctrlSwitch_IKFK, ln='nodeData', at='message')
            nodeSaveData.nodeData >> ctrlSwitch_IKFK.nodeData

            pm.addAttr(nodeSaveData, ln='ctrlSwitch', at='message')
            ctrlSwitch_IKFK.message >> nodeSaveData.ctrlSwitch

            if 'ctrlUpper' in self.snap_total_list[i]:
                if self.snap_total_list[i]['ctrlUpper']:
                    ctrlUpper = pm.PyNode(self.snap_total_list[i]['ctrlUpper'][0])
                    if not ctrlUpper.hasAttr('nodeData'):
                        pm.addAttr(ctrlUpper, ln='nodeData', at='message')
                    nodeSaveData.nodeData >> ctrlUpper.nodeData

                    pm.addAttr(nodeSaveData, ln='ctrlUpper', at='message')
                    ctrlUpper.message >> nodeSaveData.ctrlUpper

            if 'RollToes' in self.snap_total_list[i]:
                ctrlRollToes = pm.PyNode(self.snap_total_list[i]['RollToes'][0])
                if not ctrlRollToes.hasAttr('nodeData'):
                    pm.addAttr(ctrlRollToes, ln='nodeData', at='message')
                nodeSaveData.nodeData >> ctrlRollToes.nodeData

                pm.addAttr(nodeSaveData, ln='RollToes', at='message')
                ctrlRollToes.message >> nodeSaveData.RollToes

                if not nodeSaveData.hasAttr('AimAxis'):
                    pm.addAttr(nodeSaveData, ln='AimAxis', dt='string')
                get_axis = self.check_jointOrient(parent=self.snap_total_list[i]['jointIK'][-2],
                                                  child=self.snap_total_list[i]['jointIK'][-1])
                str_axis = "{}, {}, {}".format(
                    1 if get_axis.lower().find("x") > -1 else 0,
                    1 if get_axis.lower().find("y") > -1 else 0,
                    1 if get_axis.lower().find("z") > -1 else 0)
                str_axis = str_axis.replace("1", "-1" if get_axis.find("-") > -1 else "1")
                nodeSaveData.AimAxis.set(str_axis, lock=True)

                # query data Locator offset
                newLoc = pm.spaceLocator()
                pm.matchTransform(newLoc, self.snap_total_list[i]['ctrlFK'][-2], pos=True, rot=True)
                pm.matchTransform(newLoc, self.snap_total_list[i]['ctrlFK'][-1], pos=True)

                ## newLoc parent FKCtrl
                newLoc.setParent(self.snap_total_list[i]['ctrlFK'][-1])

                ## query Translate & Rotate -> saveData in nodeData
                self.query_transRot_setAttr(newLoc, nodeSaveData, self.nameRollToesOffset)

            listCtrlFK = [pm.PyNode(a) for a in self.snap_total_list[i]['ctrlFK']]
            listJointIK = [pm.PyNode(a) for a in self.snap_total_list[i]['jointIK']]

            listName_fkSetup = nameListFK_4Leg if (len(self.snap_total_list[i]['ctrlFK']) == 4 and len(
                self.snap_total_list[i]['jointIK']) == 4) else self.nameListFK

            for b, val in enumerate(listName_fkSetup):
                self.addAttr_connectMessage(nodeSaveData, val, listCtrlFK[b])
                if not listCtrlFK[b].hasAttr('nodeData'):
                    pm.addAttr(listCtrlFK[b], ln='nodeData', at='message')
                nodeSaveData.nodeData >> listCtrlFK[b].nodeData

                # query data Locator offset
                newLoc = pm.spaceLocator()
                pm.delete(pm.parentConstraint(listCtrlFK[b], newLoc))

                ## newLoc parent FKCtrl
                newLoc.setParent(listJointIK[b])

                ## query Translate & Rotate -> saveData in nodeData
                self.query_transRot_setAttr(newLoc, nodeSaveData, val)

                pm.delete(newLoc)

            ctrlFK_end_middle = [listCtrlFK[-1], listCtrlFK[1]]
            listCtrlIK = [pm.PyNode(a) for a in self.snap_total_list[i]['ctrlIK']]
            for c, val in enumerate(self.nameListIK):
                if not listCtrlIK[c].hasAttr('nodeData'):
                    pm.addAttr(listCtrlIK[c], ln='nodeData', at='message')
                nodeSaveData.nodeData >> listCtrlIK[c].nodeData
                self.addAttr_connectMessage(nodeSaveData, val, listCtrlIK[c])

                # query data Locator offset
                newLoc = pm.spaceLocator()
                pm.delete(pm.parentConstraint(listCtrlIK[c], newLoc))

                ## newLoc parent FKCtrl
                newLoc.setParent(ctrlFK_end_middle[c])

                ## query Translate & Rotate -> saveData in nodeData
                self.query_transRot_setAttr(newLoc, nodeSaveData, val)

                pm.delete(newLoc)

            listName_ikSetup = nameListIK_jnt_4Leg if (len(self.snap_total_list[i]['ctrlFK']) == 4 and len(
                self.snap_total_list[i]['jointIK']) == 4) else self.nameListIK_jnt
            listJointIK = self.snap_total_list[i]['jointIK']
            for b, val in enumerate(listName_ikSetup):
                self.addAttr_connectMessage(nodeSaveData, val, listJointIK[b])

            for c in list_dataString:
                self.addAttr_dataString(nodeSaveData, c, self.snap_total_list[i][c])

        self.define_scriptNode(transformNode_Snap)

    # ************************************************** DEF Delete Setup ******************************************************************

    def deleteSnap_IKFK(self, *arg):

        myList_snapFollow = pm.ls('*pRig_trickRig', r=True)[0]
        list_scriptJob = pm.scriptJob(lj=True)
        nodeUI = pm.listConnections(myList_snapFollow.UI, s=True)

        allNode_connect = pm.listConnections(myList_snapFollow.nodeDataSnapIKFK, s=True)

        for i, val in enumerate(allNode_connect):
            nodeData = pm.listConnections(val.nodeData, s=True)
            for node in nodeData:
                node.deleteAttr('nodeData')
            pm.delete(val)
        myList_snapFollow.deleteAttr('nodeDataSnapIKFK')

        if myList_snapFollow.hasAttr('ui_scriptSnapParentSpace') and myList_snapFollow.hasAttr(
                'func_scriptSnapParentSpace'):
            myList_snapFollow.ui_scriptSnapIKFK.set(lock=False)
            myList_snapFollow.deleteAttr('ui_scriptSnapIKFK')
            myList_snapFollow.func_scriptSnapIKFK.set(lock=False)
            myList_snapFollow.deleteAttr('func_scriptSnapIKFK')
            pm.displayInfo(
                'Node Data: {} --->>> Delete Attr: ui_scriptSnapIKFK, func_scriptSnapIKFK'.format(myList_snapFollow))
        else:
            script_node = pm.listConnections(myList_snapFollow.script_node, d=True)[0]
            pm.displayInfo('Delete ' + script_node + ' DONE!!!')
            pm.delete(script_node)

            for c in list_scriptJob:
                if c.find(nodeUI[0] + '.snapIkFk') > -1:
                    indexSJ = c.partition(':')[0]
                    pm.scriptJob(k=int(indexSJ))
                    pm.displayInfo('Delete ScriptJob: ' + nodeUI[0] + '.snapIkFk' + ' DONE!!!')

            if not nodeUI[0].hasAttr("snapIkFk_addAttr"):
                pm.deleteAttr(nodeUI, at='UI')
                pm.delete(nodeUI)
            else:
                pm.deleteAttr(nodeUI[0], at='snapIkFk_addAttr')
                pm.deleteAttr(nodeUI[0], at='snapIkFk')
                pm.deleteAttr(nodeUI[0], at='UI')

            pm.displayInfo('Delete TransformNode: ' + myList_snapFollow + ' DONE!!!')
            pm.delete(myList_snapFollow)

            if (pm.window('ui_pRig_trickRig', ex=True)):
                pm.deleteUI('ui_pRig_trickRig')
                if pm.windowPref('ui_pRig_trickRig', ex=True):
                    pm.windowPref('ui_pRig_trickRig', e=True, r=True)
            if (pm.dockControl('dock_pRig_trickRig', ex=True)):
                pm.deleteUI('dock_pRig_trickRig', ctl=True)

    def reloadSnap_IKFK(self, *arg):
        myList_snapFollow = pm.ls('*pRig_trickRig', r=True)[0]
        list_scriptJob = pm.scriptJob(lj=True)
        nodeUI = pm.listConnections(myList_snapFollow.UI, s=True)
        script_node = pm.listConnections(myList_snapFollow.script_node, d=True)[0]

        for c in list_scriptJob:
            if c.find(nodeUI[0] + '.snapIkFk') > -1:
                indexSJ = c.partition(':')[0]
                pm.scriptJob(k=int(indexSJ))

        script_node.sourceType.set(1)

        pm.scriptNode(script_node, eb=True)

        script_node.scriptType.set(2)

    def ctrlUI(self):
        """
        shape3=[[[0.6059257415014999, -2.9587857790914936e-16, -1.9930478136223144], [0.003676841782389804, -2.9587857790914936e-16, -1.9930478136223144], [0.003676841782389804, -8.004305389083088e-17, -0.0034925836244670515], [0.2832854867789044, -8.004305389083088e-17, -0.0034925836244670515], [0.2832854867789044, -2.9587857790914936e-16, -0.8450167209669935], [0.5459899401003014, -2.9587857790914936e-16, -0.8450167209669935], [1.1128335514736154, -8.004305389083088e-17, -0.0034925836244670515], [1.4595636732297537, -8.004305389083088e-17, -0.0034925836244670515], [0.7954518208704121, 0.0, -0.935071805786463], [0.8855619467304667, -2.9587857790914936e-16, -0.9790119500914564], [0.9650175408867254, 0.0, -1.0315418325476333], [1.0337908842581716, -2.9587857790914936e-16, -1.0926064121143637], [1.0918820562690588, -2.9587857790914936e-16, -1.162260729832281], [1.1380521966727153, -2.9587857790914936e-16, -1.2387980368975724], [1.1710347261413743, -2.9587857790914936e-16, -1.3205661490012208], [1.190802322715506, -2.9587857790914936e-16, -1.4075102633755388], [1.1974097891627724, -2.9587857790914936e-16, -1.4996853416368126], [1.1878839562002308, -2.9587857790914936e-16, -1.6128668767189287], [1.1592789765044902, -2.9587857790914936e-16, -1.7117596623572189], [1.1115945323783156, 0.0, -1.7963633808545116], [1.044830941518911, -2.9587857790914936e-16, -1.8666786676052078], [0.9601719437081471, -2.9587857790914936e-16, -1.9219616346062867], [0.8588014375764008, -2.9587857790914936e-16, -1.961469188097797], [0.7407193436994308, -5.917571558182987e-16, -1.9851462076148498], [0.6059257415014999, -2.9587857790914936e-16, -1.9930478136223144]], [[2.6098791223651645, -2.9587857790914936e-16, -1.29412889675215], [2.7104414068101046, -2.9587857790914936e-16, -1.2828700255422087], [2.8071687683064486, -2.9587857790914936e-16, -1.2490388474175491], [2.900060571459778, -2.9587857790914936e-16, -1.1926898474486753], [2.989090447402188, -2.9587857790914936e-16, -1.1137960213732625], [2.989090447402188, -2.2190893343186254e-16, -0.5113258852637588], [2.8862544040687395, -7.396964447728734e-17, -0.4067092285266022], [2.780048864190467, -1.1095446671593127e-16, -0.332006563245778], [2.6705014674240504, -1.4793928895457468e-16, -0.2871630270853377], [2.557639218031895, -1.1095446671593127e-16, -0.2722060809973689], [2.410480284687029, -7.396964447728734e-17, -0.3017638743198582], [2.305397804424611, -7.396964447728734e-17, -0.39043737342374357], [2.2423374510228076, -2.2190893343186254e-16, -0.5381990975009084], [2.221299224481582, -2.9587857790914936e-16, -0.7451038890311821], [2.22776404488428, -2.9587857790914936e-16, -0.8670058946638762], [2.2471041798705214, -2.9587857790914936e-16, -0.9748550410266673], [2.2793463160054324, -2.9587857790914936e-16, -1.0687058926143667], [2.3244914063806235, -2.9587857790914936e-16, -1.1485312068916855], [2.381004338106716, -2.9587857790914936e-16, -1.212221633273196], [2.44740686609384, -2.9587857790914936e-16, -1.2577225445167817], [2.523698354947596, 0.0, -1.2850341788953574], [2.6098791223651645, -2.9587857790914936e-16, -1.29412889675215]], [[3.8518117195568906, -2.9587857790914936e-16, -1.9930478136223144], [3.569505031055991, -2.9587857790914936e-16, -1.9930478136223144], [3.569505031055991, 0.0, -0.7401497188331339], [3.580627610165455, -2.2190893343186254e-16, -0.5512018086632262], [3.6140233048478367, -1.4793928895457468e-16, -0.3889594063189254], [3.6696914797086873, -7.396964447728734e-17, -0.2534224323759728], [3.747605448182884, -1.2944687783525305e-16, -0.14461843713871406], [3.849168796517396, -9.246205559660926e-17, -0.06111576283388289], [3.9756478657670664, -7.281386878232981e-17, -0.0014827929515327139], [4.127097935245365, -5.5477233357965635e-17, 0.03430799768240919], [4.3034913652955815, -5.5477233357965635e-17, 0.04622908885787549], [4.441533659676566, -7.396964447728734e-17, 0.037997204340796696], [4.563938262285877, -7.396964447728734e-17, 0.013301556994627562], [4.670732495083042, -9.246205559660926e-17, -0.02785785442165304], [4.7618890361085136, -1.0170826115627033e-16, -0.08548102866706854], [4.823311342726902, -1.2944687783525305e-16, -0.1406814440353318], [4.874492362279479, -1.4793928895457468e-16, -0.20009415699025684], [4.915404137412356, -1.1095446671593127e-16, -0.26369163708354537], [4.946073990085018, -1.4793928895457468e-16, -0.3315014246915372], [4.9684290715365185, -7.396964447728734e-17, -0.40894716705537365], [4.984369846440768, -1.4793928895457468e-16, -0.5015352119696133], [4.993950958716777, -1.4793928895457468e-16, -0.6092654998659887], [4.997144451010642, -2.9587857790914936e-16, -0.7320829897039456], [4.997144451010642, -2.9587857790914936e-16, -1.9930478136223144], [4.7484536213544475, -2.9587857790914936e-16, -1.9930478136223144], [4.7484536213544475, -2.9587857790914936e-16, -0.7280634052555549], [4.7422864832318385, -7.396964447728734e-17, -0.5859464059613259], [4.723785704258367, -2.2190893343186254e-16, -0.4660748031589214], [4.692950331342445, -7.396964447728734e-17, -0.368503598176818], [4.6497809998784785, -1.1095446671593127e-16, -0.2931777499743701], [4.591854950989326, -7.396964447728734e-17, -0.23701372920250074], [4.51674974349502, -1.4793928895457468e-16, -0.19690050584778068], [4.424409462687704, -7.396964447728734e-17, -0.17281055938993317], [4.31488938788085, -7.396964447728734e-17, -0.16479893086952974], [4.2022587397503495, -1.1095446671593127e-16, -0.1733336478362112], [4.1060088771515275, -1.4793928895457468e-16, -0.19891031792804909], [4.026085473862469, -7.396964447728734e-17, -0.24155640209715085], [3.962542856105081, -1.4793928895457468e-16, -0.3012444393914335], [3.9140876785621987, -7.396964447728734e-17, -0.3796813374633121], [3.8794806044412447, -1.4793928895457468e-16, -0.4785190026367318], [3.8587219514394686, -1.4793928895457468e-16, -0.597784915719837], [3.8518117195568906, 0.0, -0.7374791561369429], [3.8518117195568906, -2.9587857790914936e-16, -1.9930478136223144]], [[5.436159428368164, -2.9587857790914936e-16, -1.9930478136223144], [5.15385242217007, -2.9587857790914936e-16, -1.9930478136223144], [5.15385242217007, -8.004305389083088e-17, -0.0034925836244670515], [5.436159428368164, -8.004305389083088e-17, -0.0034925836244670515], [5.436159428368164, -2.9587857790914936e-16, -1.9930478136223144]], [[1.8375968181860005, 0.0, -1.4633990789445042], [1.5727725302714124, 0.0, -1.4633990789445042], [1.5727725302714124, -8.004305389083088e-17, -0.0034925836244670515], [1.8375968181860005, -8.004305389083088e-17, -0.0034925836244670515], [1.8375968181860005, 0.0, -1.4633990789445042]], [[2.569706628625846, -2.9587857790914936e-16, -1.4956656777641275], [2.4361794469070714, -2.9587857790914936e-16, -1.482560826950755], [2.3156473516177067, -2.9587857790914936e-16, -1.443218476005288], [2.208027106090344, -2.9587857790914936e-16, -1.3776937453926013], [2.11340178814378, -2.9587857790914936e-16, -1.2859592337288972], [2.036258870783507, -2.9587857790914936e-16, -1.1733559075579325], [1.9811685871365965, -2.9587857790914936e-16, -1.04530749354517], [1.9481032975463073, -2.9587857790914936e-16, -0.9018139122662939], [1.9370631608612474, -2.9587857790914936e-16, -0.7428477623374956], [1.9467543552184259, -1.4793928895457468e-16, -0.5886169686575216], [1.9757723412792962, -7.396964447728734e-17, -0.45129048578913883], [2.024145076397769, -1.1095446671593127e-16, -0.33086821445194964], [2.0918722428766876, -7.396964447728734e-17, -0.22729517317363204], [2.1761731959386226, -7.396964447728734e-17, -0.14409533876441594], [2.2742676085034534, -7.396964447728734e-17, -0.08462755498479889], [2.386155162873977, -9.246205559660926e-17, -0.048974418143753085], [2.5118358590501777, -7.396964447728734e-17, -0.03708086486263934], [2.58809780206395, -7.396964447728734e-17, -0.04211910816527133], [2.6607256067620253, -7.396964447728734e-17, -0.05726136603948659], [2.7297465951039266, -7.396964447728734e-17, -0.08245257510661863], [2.7951614024840232, -1.1095446671593127e-16, -0.11774780619135539], [2.855096886188039, -9.246205559660926e-17, -0.1621008476530363], [2.907737088998246, -7.396964447728734e-17, -0.21454812883618088], [2.9530260962068193, -1.4793928895457468e-16, -0.2750345789160867], [2.991019504824423, -1.4793928895457468e-16, -0.3435877184130324], [2.991019504824423, -1.1095446671593127e-16, -0.11370069129464014], [2.963075176464229, -7.396964447728734e-17, 0.09385837777103699], [2.879269513343209, 0.0, 0.24216989671567696], [2.7396028331585267, 0.0, 0.331151343690555], [2.544047496253492, 0.0, 0.3608026194152841], [2.4313066071932488, 0.0, 0.35408495175041593], [2.317877268292068, 0.0, 0.3339044282354639], [2.203787119206713, -3.698482223864367e-17, 0.30031618919144865], [2.089036477634418, -3.698482223864367e-17, 0.2532650545852283], [2.0580637006778053, -7.396964447728734e-17, 0.4817755195750834], [2.1762008355953633, 0.0, 0.5158869066336028], [2.2966779692684396, 0.0, 0.5402520980064945], [2.4195232178996013, 0.0, 0.554871292254539], [2.544708306437682, 7.396964447728734e-17, 0.5597443305291239], [2.716696864755424, 7.396964447728734e-17, 0.5482362258626767], [2.8643199537152286, 7.396964447728734e-17, 0.5137119118633783], [2.9875778910142876, 0.0, 0.45617130910687315], [3.086443354693053, 0.0, 0.37558697649721656], [3.1316221209718704, 0.0, 0.31942293586926174], [3.1689547194052565, -3.698482223864367e-17, 0.25577041473539286], [3.1984961116095905, -7.396964447728734e-17, 0.18465685419161612], [3.220218022533668, -7.396964447728734e-17, 0.1060547734297764], [3.2358010703863105, -6.472343891762652e-17, 0.012585741759018254], [3.2469236494957654, -9.246205559660926e-17, -0.10312864172741848], [3.2536137172160373, -1.1095446671593127e-16, -0.24111591492390252], [3.2558439515876145, -2.2190893343186254e-16, -0.4014036057967417], [3.2558439515876145, 0.0, -1.4633990789445042], [2.991019504824423, 0.0, -1.4633990789445042], [2.991019504824423, -2.9587857790914936e-16, -1.2966965255542928], [2.898541661127818, 0.0, -1.38375064258547], [2.7975012423909624, 0.0, -1.445916519509625], [2.687898884008284, 0.0, -1.4832214782863153], [2.569706628625846, -2.9587857790914936e-16, -1.4956656777641275]], [[1.8375968181860005, -2.9587857790914936e-16, -1.9930478136223144], [1.5727725302714124, -2.9587857790914936e-16, -1.9930478136223144], [1.5727725302714124, -2.9587857790914936e-16, -1.728223366859107], [1.8375968181860005, -2.9587857790914936e-16, -1.728223366859107], [1.8375968181860005, -2.9587857790914936e-16, -1.9930478136223144]], [[0.46178429619953554, -5.917571558182987e-16, -1.7801773437088515], [0.6564988474543787, -5.917571558182987e-16, -1.760946973106565], [0.7955493539120366, 0.0, -1.7032557024511221], [0.8790180197239947, -2.9587857790914936e-16, -1.6071311713992324], [0.9068226407387358, -2.9587857790914936e-16, -1.4725458991427767], [0.8983580752859308, -2.9587857790914936e-16, -1.376969078070462], [0.8729640612302597, -2.9587857790914936e-16, -1.2936374191776892], [0.8306681588041925, -2.9587857790914936e-16, -1.2224958814239026], [0.77144296662387, -2.9587857790914936e-16, -1.163544623657648], [0.6959458796285254, -2.9587857790914936e-16, -1.1173313558585733], [0.6048890955250906, -2.9587857790914936e-16, -1.0842946590166256], [0.4982179703944475, -2.9587857790914936e-16, -1.064488938778036], [0.37598718786783725, 0.0, -1.0578870320318428], [0.28484823932502484, 0.0, -1.0578870320318428], [0.28484823932502484, -5.917571558182987e-16, -1.7801773437088515], [0.46178429619953554, -5.917571558182987e-16, -1.7801773437088515]]]
        """
        shape3 = [[[-1.0, 0.0, -1.0],
                   [-1.0, 0.0, -3.0],
                   [1.0, 0.0, -3.0],
                   [1.0, 0.0, -1.0],
                   [3.0, 0.0, -1.0],
                   [3.0, 0.0, 1.0],
                   [1.0, 0.0, 1.0],
                   [1.0, 0.0, 3.0],
                   [-1.0, 0.0, 3.0],
                   [-1.0, 0.0, 1.0],
                   [-3.0, 0.0, 1.0],
                   [-3.0, 0.0, -1.0],
                   [-1.0, 0.0, -1.0]]]
        # degreeList = [1, 1, 1, 1, 1, 1, 1, 1]
        degreeList = [1]
        firstShape = None

        for index, pos in enumerate(shape3):
            newCurve = pm.curve(n='Rig_UI', d=degreeList[index], p=pos)
            shape = newCurve.getShape()
            shape.isHistoricallyInteresting.set(0)
            shape.overrideEnabled.set(1)
            shape.overrideColor.set(17)

            if index == 0:
                firstShape = newCurve
            else:
                pm.parent(shape, firstShape, s=True, r=True)
                pm.delete(newCurve)
        pm.select(cl=True)

        return firstShape

    # *********************************************** DEF Define Script IKFK *****************************************

    def addScriptUI(self, ctrl, *arg):
        if not ctrl.hasAttr('__authors__'):
            ctrl.addAttr('__authors__', dt='string')
            ctrl.__authors__.set(__authors__, type='string', lock=True)

        scripCreateUI = """__authors__ = "PhucHoang"

float = 1
if(cmds.window('ui_pRig_trickRig',ex=True)):
    cmds.deleteUI('ui_pRig_trickRig')
    if cmds.windowPref('ui_pRig_trickRig', ex=True) and float:
        cmds.windowPref('ui_pRig_trickRig', e=True, r=True)

if(cmds.dockControl('dock_pRig_trickRig',ex=True)):
    cmds.deleteUI('dock_pRig_trickRig', ctl =True)

mywin = cmds.window('ui_pRig_trickRig',t='Snap IK/FK Window')
cmds.window('ui_pRig_trickRig',e=True, w= 205, h=40)
cmds.columnLayout('ui_pRig_column', p ='ui_pRig_trickRig', adj=True, rs= 5)
cmds.paneLayout('paneLOPRig', parent='ui_pRig_column', configuration='vertical2', paneSize=[1, 50, 100], staticWidthPane=1, staticHeightPane=2)
#cmds.separator(p='ui_pRig_column', style='double')
#cmds.iconTextButton('ui_pRig_btAuthor',style = 'textOnly', l='PhucHoang - hoangducphuc0106@gmail.com', p='ui_pRig_column', ann = 'Trick Rig - PhucHoang', c = ('pm.showHelp("https://www.linkedin.com/in/phuchoang1694/", a=True)'))
cmds.dockControl('dock_pRig_trickRig', fl=float ,content='ui_pRig_trickRig', label='Snap IK/FK Dock', allowedArea=['right', 'left','top','bottom'], area='top', w=10)"""

        scriptAdd = """
__authors__ = "PhucHoang"

cmds.button('btPRig_trickRig_snapIKFK', l='Snap IK/FK', p='paneLOPRig', w= 100, h=40)
cmds.button('btPRig_trickRig_snapIKFK', e=True, c= snapIKFK)"""

        if not ctrl.hasAttr('ui_scriptCreateUI'):
            ctrl.addAttr('ui_scriptCreateUI', dt='string')
            ctrl.ui_scriptCreateUI.set(scripCreateUI, type='string', lock=True)

        if not ctrl.hasAttr('ui_scriptSnapIKFK'):
            ctrl.addAttr('ui_scriptSnapIKFK', dt='string')
            ctrl.ui_scriptSnapIKFK.set(scriptAdd, type='string', lock=True)

        scriptDefineFunc = """__authors__ = "PhucHoang"

def set_Transform(tranform_Ctrl, posTrans=[0,0,0], posRot=[0,0,0], *arg):

    for index, attr in enumerate("xyz"):
        cmds.setAttr("%s.t%s" % (tranform_Ctrl, attr), posTrans[index])
        cmds.setAttr("%s.r%s" % (tranform_Ctrl, attr), posRot[index])

def snapIKFK(*arg):
    keySelect = cmds.currentTime(q=True)
    aTimerSlider = mel.eval('$tmpVar=$gPlayBackSlider')
    timeRange = cmds.timeControl(aTimerSlider, q=True, ra=True)

    if (timeRange[1] - timeRange[0]) == 1.0:
        run_snap()
    else:
        nodeSelect = cmds.ls(sl=True)
        listNode_switchDone = []
        for i in nodeSelect:
            if not cmds.attributeQuery("nodeData", node=i, exists=True):
                continue
            dataNode = cmds.listConnections("%s.nodeData" % i)[0]
            if dataNode in listNode_switchDone:
                continue
            listNode_switchDone.append(dataNode)
            switchNode = cmds.listConnections("%s.ctrlSwitch" % dataNode)[0]
            attrSwitch = cmds.getAttr("%s.attrBlend" % dataNode)

            listKeyFrame = cmds.keyframe('%s.%s' % (switchNode, attrSwitch), q=True, tc=True)

            for i in listKeyFrame:
                if not timeRange[0] <= i <= timeRange[1]:
                    continue
                cmds.currentTime(i)
                cmds.select(switchNode)
                run_snap()
        cmds.select(nodeSelect)
    cmds.currentTime(keySelect)

def run_snap(*arg):
    nameListIK = ['mainIK', 'poleIK']
    orig_nameListIK_jnt = ['startJnt', 'middleJnt', 'endJnt']
    orig_nameListFK = ['startFK', 'middleFK', 'endFK']
    nameAttr = ['_trans', '_rot']
    nameRollOffset = "rollToesOffset"

    nodeSelect = cmds.ls(sl=True)
    listNode_switchDone = []
    for i in nodeSelect:
        nameListFK = orig_nameListFK[:]
        nameListIK_jnt = orig_nameListIK_jnt[:]

        if not cmds.attributeQuery("nodeData", node=i, exists=True):
            continue

        dataNode = cmds.listConnections("%s.nodeData" % i)[0]
        if dataNode in listNode_switchDone:
            continue

        listNode_switchDone.append(dataNode)
        switchNode = switchNode = cmds.listConnections("%s.ctrlSwitch" % dataNode)[0]

        upperNode = False
        if cmds.attributeQuery("ctrlUpper", node=dataNode, exists=True):
            upperNode = cmds.listConnections("%s.ctrlUpper" % dataNode)[0]

        attrSwitch = cmds.getAttr("%s.attrBlend" % dataNode)
        fkMode = int(cmds.getAttr("%s.fkMode" % dataNode))
        ikMode = int(cmds.getAttr("%s.ikMode" % dataNode))
        getStatic = int(cmds.getAttr('%s.%s' % (switchNode, attrSwitch)))

        if cmds.attributeQuery("middleFK2", node=dataNode, exists=True) and cmds.attributeQuery("middleJnt2", node=dataNode, exists=True):
            nameListIK_jnt.insert(2, 'middleJnt2')
            nameListFK.insert(2, 'middleFK2')

        listFKCtrl = []
        listFK_transformLoc = []
        for b in nameListFK:
            nodeQuery = cmds.listConnections('%s.%s' % (dataNode, b), s=True)
            listFKCtrl.extend(nodeQuery)
            listTrans = []
            for c in nameAttr:
                if not cmds.attributeQuery('%s%s' % (b, c), node = dataNode, ex=True):
                    listTrans.append([0,0,0])
                    continue
                value = cmds.getAttr('%s.%s%s' % (dataNode, b, c))
                listTrans.append(value)
            listFK_transformLoc.append(listTrans)

        listIKCtrl = []
        list_transformLoc = []
        for b in nameListIK:
            nodeQuery = cmds.listConnections('%s.%s' % (dataNode, b), s=True)
            listIKCtrl.extend(nodeQuery)
            listTrans = []
            for c in nameAttr:
                value = cmds.getAttr('%s.%s%s' % (dataNode, b, c))
                listTrans.append(value)
            list_transformLoc.append(listTrans)

        listIKJnt = []
        for b in nameListIK_jnt:
            nodeQuery = cmds.listConnections('%s.%s' % (dataNode, b), s=True)
            listIKJnt.extend(nodeQuery)

        list_loc = []
        if upperNode:
            loc_upper = cmds.spaceLocator()[0]
            cmds.matchTransform(loc_upper, upperNode, pos=True, rot=True)

        if getStatic == ikMode:
            if upperNode:
                list_loc = [loc_upper]

            for i,val in enumerate(listFKCtrl):
                newLoc = cmds.spaceLocator()[0]
                cmds.parent(newLoc, listIKJnt[i])
                set_Transform(newLoc, listFK_transformLoc[i][0][0], listFK_transformLoc[i][1][0])
                cmds.parent(newLoc, w=True)
                list_loc.append(newLoc)

            cmds.setAttr('%s.%s' % (switchNode , attrSwitch), fkMode)
            list_snap = listFKCtrl

            if upperNode:
                list_snap.insert(0, upperNode)

            for i,val in enumerate(list_snap):
                cmds.matchTransform(val, list_loc[i], pos=True, rot=True)
            cmds.delete(list_loc)

        else:
            ctrlFK_end_middle = [listFKCtrl[-1], listFKCtrl[1]]
            for i,val in enumerate(listIKCtrl):
                newLoc = cmds.spaceLocator()[0]
                cmds.parent(newLoc, ctrlFK_end_middle[i])
                set_Transform(newLoc, list_transformLoc[i][0][0], list_transformLoc[i][1][0])
                cmds.parent(newLoc, w=True)
                list_loc.append(newLoc)

            if upperNode:
                list_loc.append(loc_upper)

            cmds.setAttr('%s.%s' % (switchNode , attrSwitch), ikMode)
            list_snap = listIKCtrl[:]

            if upperNode:
                list_snap.append(upperNode)

            for i,val in enumerate(list_snap):
                cmds.matchTransform(val, list_loc[i], pos=True, rot=True)

            cmds.delete(list_loc)

            if cmds.attributeQuery("AimAxis", node = dataNode, ex=True):
                ctrlRollToes = cmds.listConnections("%s.RollToes" % dataNode)
                get_str_aimAxis = cmds.getAttr("%s.AimAxis" % dataNode)
                loc_ankleAim = cmds.spaceLocator()[0]
                cmds.matchTransform(loc_ankleAim, listFKCtrl[-2], pos=True, rot=True)
                cmds.parent(loc_ankleAim, listFKCtrl[-2])

                listRollToes_transformLoc = []
                for c in nameAttr:
                    if not cmds.attributeQuery("%s%s" % (nameRollOffset, c), node = dataNode, ex=True):
                        listRollToes_transformLoc.append([0,0,0])
                        continue
                    value = cmds.getAttr('%s.%s%s' % (dataNode, nameRollOffset, c))
                    listRollToes_transformLoc.append(value)

                loc_drivenAim = cmds.spaceLocator()[0]
                cmds.parent(loc_drivenAim, listFKCtrl[-1])
                set_Transform(loc_drivenAim, listRollToes_transformLoc[0][0], listRollToes_transformLoc[1][0])

                loc_toesUpAim = cmds.spaceLocator()[0]
                cmds.matchTransform(loc_toesUpAim, listFKCtrl[-2], rot=True)
                cmds.matchTransform(loc_toesUpAim, listFKCtrl[-1], pos=True)
                cmds.parent(loc_toesUpAim, listFKCtrl[-1])

                aimAxis_split = get_str_aimAxis.split(", ")
                aimAxis_split = [float(i) for i in aimAxis_split]
                aimAxis_reverseValue = [i*-1 for i in aimAxis_split]
                upAxis = aimAxis_split.index(0)
                str_upAxis = ["X", "Y", "Z"][upAxis]
                list_value_upAxis = [0, 0, 0]
                list_value_upAxis[upAxis] = 1
                list_upAxis = list_value_upAxis[:]
                list_value_upAxis = [i*10 for i in list_value_upAxis]
                cmds.move(loc_toesUpAim, list_value_upAxis, relative = True, os = True, wd = True)

                loc_toeMatch = cmds.spaceLocator()[0]
                cmds.parent(loc_toeMatch, listFKCtrl[-1])
                set_Transform(loc_toeMatch, list_transformLoc[0][0][0], list_transformLoc[0][1][0])
                cmds.parent(loc_toeMatch, loc_drivenAim)
                cmds.aimConstraint(loc_ankleAim, loc_drivenAim, aimVector = (aimAxis_reverseValue[:]), upVector = (list_upAxis[:]), worldUpType = "object", worldUpObject = loc_toesUpAim)
                cmds.matchTransform(ctrlRollToes, loc_toeMatch, rot = True)
                cmds.delete(loc_ankleAim, loc_drivenAim, loc_toesUpAim, loc_toeMatch)

    cmds.select(nodeSelect)"""

        if not ctrl.hasAttr('func_scriptSnapIKFK'):
            ctrl.addAttr('func_scriptSnapIKFK', dt='string')
            ctrl.func_scriptSnapIKFK.set(scriptDefineFunc, type='string', lock=True)

    def define_scriptNode(self, transformNode_Snap, *arg):
        strScript = """__authors__ = "PhucHoang"

import maya.cmds as cmds
from functools import partial

def pRig_createUI(nodeTrickRig, uictrl, *arg):
    createUI = cmds.getAttr("%s.snapIkFk" % uictrl)

    if createUI:
        listAttr = cmds.listAttr(nodeTrickRig, ud=True)
        listAttr_UI = [attr for attr in listAttr if attr.find('ui_') > -1 ]
        strScript = cmds.getAttr("%s.ui_scriptCreateUI" % nodeTrickRig)

        for i in listAttr_UI:
            if not i.find('ui_scriptCreateUI') > -1:
                strScript += cmds.getAttr("%s.%s" % (nodeTrickRig, i))
        cmds.setAttr("%s.snapIkFk" % uictrl, 0)
        # exec(strScript)
        newScriptNode = cmds.createNode('script', n='pRig_trickRig_run_ui')
        cmds.setAttr("%s.sourceType" % newScriptNode, 1)
        cmds.setAttr("%s.before" % newScriptNode, strScript, type="string")
        cmds.scriptNode(newScriptNode, eb=True)
        cmds.delete(newScriptNode)        

nodeTrickRigList = cmds.ls('*pRig_trickRig',r=True)
srcJob_list = cmds.scriptJob(lj=True)

for nodeTrickRig in nodeTrickRigList:
    uictrl = cmds.listConnections("%s.UI" % nodeTrickRig)[0]
    listAttr = cmds.listAttr(nodeTrickRig, ud=True)
    listAttr_func = [attr for attr in listAttr if attr.find('func_') > -1 ]

    for a in listAttr_func:
        strScript = cmds.getAttr("%s.%s" % (nodeTrickRig, a))
        newScriptNode = cmds.createNode('script', n='pRig_trickRig_Func')
        cmds.setAttr("%s.sourceType" % newScriptNode, 1)
        cmds.setAttr("%s.before" % newScriptNode, strScript, type="string")
        cmds.scriptNode(newScriptNode, eb=True)
        cmds.delete(newScriptNode)

    for c in srcJob_list:
        if c.find('%s.snapIkFk' % uictrl) > -1:
            indexSJ = c.partition(':')[0]
            cmds.scriptJob(k = int(indexSJ))

    cmds.scriptJob(kws=True, ac = ["%s.snapIkFk" % uictrl, partial(pRig_createUI, nodeTrickRig, uictrl)])
"""

        if not (pm.objExists('pRig_trickRig_scriptNode')):
            newScriptNode = pm.createNode('script', n='pRig_trickRig_scriptNode')
            newScriptNode.addAttr("mainNode_snapIKFK", at="message")
            transformNode_Snap.script_node >> newScriptNode.mainNode_snapIKFK

        else:
            newScriptNode = pm.ls('pRig_trickRig_scriptNode')[0]

        newScriptNode.sourceType.set(1)

        newScriptNode.before.set(strScript)

        pm.scriptNode(newScriptNode, eb=True)

        newScriptNode.scriptType.set(2)

    def check_jointOrient(self, parent, child):
        parent = pm.PyNode(parent)
        child = pm.PyNode(child)
        deleteOffset = []

        if not isinstance(parent, pm.Joint):
            pm.select(cl=True)
            jntOffset = pm.joint()
            pm.matchTransform(parent, jntOffset, pos=True)
            pm.matchTransform(parent, jntOffset, rot=True)
            deleteOffset.append(jntOffset)
            parent = jntOffset

        if not isinstance(child, pm.Joint):
            pm.select(cl=True)
            jntOffset = pm.joint()
            pm.matchPosition(child, jntOffset, pos=True)
            pm.matchRotation(child, jntOffset, rot=True)
            deleteOffset.append(jntOffset)
            child = jntOffset

        selectedJoint = parent
        childJoint = child

        selectedPos = pm.dt.Vector(pm.joint(selectedJoint, q=True, a=True, p=True))
        childPos = pm.dt.Vector(pm.joint(childJoint, q=True, a=True, p=True))

        aimVector = -1 * (selectedPos - childPos)
        normalizedAimVector = pm.dt.normal(aimVector)

        newLoc = pm.spaceLocator(position=selectedPos)
        newLoc.setParent(selectedJoint)
        pm.makeIdentity(newLoc, a=True, t=True, r=True, s=True, n=False)
        pm.mel.eval('CenterPivot');

        posBase = pm.pointPosition(newLoc, w=True)

        # Move
        newLoc.translate.set(1, 0, 0)
        tempPosX = pm.pointPosition(newLoc, w=True)
        normalizedVectorX = tempPosX - posBase

        newLoc.translate.set(0, 1, 0)
        tempPosY = pm.pointPosition(newLoc, w=True)
        normalizedVectorY = tempPosY - posBase

        newLoc.translate.set(0, 0, 1)
        tempPosZ = pm.pointPosition(newLoc, w=True)
        normalizedVectorZ = tempPosZ - posBase

        pm.delete(newLoc, deleteOffset)

        normalizedVectorX = pm.dt.Vector(round(normalizedVectorX.x, 3), round(normalizedVectorX.y, 3),
                                         round(normalizedVectorX.z, 3))
        normalizedVectorY = pm.dt.Vector(round(normalizedVectorY.x, 3), round(normalizedVectorY.y, 3),
                                         round(normalizedVectorY.z, 3))
        normalizedVectorZ = pm.dt.Vector(round(normalizedVectorZ.x, 3), round(normalizedVectorZ.y, 3),
                                         round(normalizedVectorZ.z, 3))
        normalizedAimVector = pm.dt.Vector(round(normalizedAimVector.x, 3), round(normalizedAimVector.y, 3),
                                           round(normalizedAimVector.z, 3))

        if normalizedVectorY == normalizedAimVector:
            return "Y"
        elif normalizedVectorY == -1 * normalizedAimVector:
            return "-Y"
        elif normalizedVectorZ == 1 * normalizedAimVector:
            return "Z"
        elif normalizedVectorZ == -1 * normalizedAimVector:
            return "-Z"

        elif normalizedVectorX == 1 * normalizedAimVector:
            return "X"
        elif normalizedVectorX == -1 * normalizedAimVector:
            return "-X"
        else:
            return False
