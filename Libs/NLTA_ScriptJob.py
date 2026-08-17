import maya.cmds as cmds

prefix = "NLTA_ScriptJob_"

def SkillAll(*arr):
    for job in cmds.scriptJob(listJobs=True):
        if prefix in job:
            jobId = int(job.split(":")[0])
            cmds.scriptJob(kill=jobId, force=True)

def AddAttributeChange(data, *arr):
    functionName = prefix + data["functionName"]
    functionContent = data["functionContent"]
    obj = data["obj"]
    attr = data["attr"]
    functionContent = "\n".join(
        "\t" + line
        for line in functionContent.splitlines()
    )
    source = '''
def {}(*arr):
{}

jobId = cmds.scriptJob(
    attributeChange=["{}.{}", {}]
)
'''.format(functionName,functionContent,obj,attr,functionName)
    exec(source, globals())
