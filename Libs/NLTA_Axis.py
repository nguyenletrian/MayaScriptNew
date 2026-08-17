import maya.cmds as cmds
import maya.api.OpenMaya as om

def GetNormalFromAxis(axis):
    normalMap = {
        "+X": (1, 0, 0),
        "-X": (-1, 0, 0),
        "+Y": (0, 1, 0),
        "-Y": (0, -1, 0),
        "+Z": (0, 0, 1),
        "-Z": (0, 0, -1),
    }
    return normalMap[axis]

def GetArmAxis(objA, objB):
    posA = om.MVector(cmds.xform(objA, q=True, ws=True, t=True))
    posB = om.MVector(cmds.xform(objB, q=True, ws=True, t=True))
    direction = (posB - posA).normalize()
    m = om.MMatrix(cmds.getAttr(objA + ".worldMatrix[0]"))
    xAxis = om.MVector(m[0], m[1], m[2]).normalize()
    yAxis = om.MVector(m[4], m[5], m[6]).normalize()
    zAxis = om.MVector(m[8], m[9], m[10]).normalize()
    axes = {
        "+X": xAxis,
        "-X": -xAxis,
        "+Y": yAxis,
        "-Y": -yAxis,
        "+Z": zAxis,
        "-Z": -zAxis,
    }
    bestAxis = None
    bestDot = -999
    for axisName, axisVector in axes.items():
        dot = axisVector * direction
        if dot > bestDot:
            bestDot = dot
            bestAxis = axisName
    return bestAxis

def GetAxisMapping(objA, objB):
    def get_axes(obj):
        m = cmds.xform(obj, q=True, ws=True, m=True)
        m = om.MMatrix(m)
        return {
            "X": om.MVector(m[0], m[1], m[2]).normalize(),
            "Y": om.MVector(m[4], m[5], m[6]).normalize(),
            "Z": om.MVector(m[8], m[9], m[10]).normalize()
        }
    a = get_axes(objA)
    b = get_axes(objB)
    mapping = {}
    for axisA, vecA in a.items():
        best_axis = None
        best_dot = -1
        sign = ""

        for axisB, vecB in b.items():

            dot = vecA * vecB

            if abs(dot) > best_dot:
                best_dot = abs(dot)
                best_axis = axisB

                sign = "-" if dot < 0 else ""

        mapping[axisA] = f"{sign}{best_axis}"

    return mapping

def AlignAxis(objA, axisA, objB, axisB):
    axis_map = {
        "X": (0, 1, 2),
        "Y": (4, 5, 6),
        "Z": (8, 9, 10)
    }
    def get_vec(obj, axis):
        m = cmds.xform(obj, q=True, ws=True, m=True)
        m = om.MMatrix(m)
        i, j, k = axis_map[axis.upper()]
        v = om.MVector(m[i], m[j], m[k])
        # support negative axis
        if axis.startswith("-"):
            v *= -1

        return v.normalize()
    # source vector (A)
    vA = get_vec(objA, axisA)

    # target vector (B)
    vB = get_vec(objB, axisB)

    # rotation
    quat = vA.rotateTo(vB)
    euler = quat.asEulerRotation()

    cmds.xform(objA, ws=True, rotation=(
        om.MAngle(euler.x).asDegrees(),
        om.MAngle(euler.y).asDegrees(),
        om.MAngle(euler.z).asDegrees()
    ))

