import maya.cmds as cmds
import os
import sys
import base64
import importlib

import json
from datetime import datetime

try:
    import urllib.request as urllib2
    import urllib.error as urllib_error
except ImportError:
    import urllib2
    import urllib2 as urllib_error

setting = {
    'token':'',
    'headers':{'Authorization':''},
    'owner':'nguyenletrian',
    'repo':'MayaScripts',
}

def convertISO2Time(ISOString):
    dt = datetime.strptime(ISOString, "%Y-%m-%dT%H:%M:%SZ")
    return int((dt - datetime(1970, 1, 1)).total_seconds())

def GetToolFiles(toolFolder, recursive=True):

    result = {}

    for root, _, files in os.walk(toolFolder):

        for file in files:

            if file.endswith('.py'):

                full_path = os.path.join(root, file)
                mod_time = os.path.getmtime(full_path)

                relative_path = os.path.relpath(full_path, toolFolder)

                result[relative_path.replace('\\', '/')] = int(mod_time)

        if not recursive:
            break

    return result

def make_request(url):

    req = urllib2.Request(url)

    for k, v in setting['headers'].items():
        req.add_header(k, v)

    try:

        response = urllib2.urlopen(req)

        status = response.getcode()
        data = response.read()

        return status, data

    except urllib2.HTTPError as e:

        print("HTTP Error: {}-{}".format(e.code, e.reason))

        return e.code, e.read()

    except urllib2.URLError as e:

        print("HTTP Error: {}".format(e.reason))

        return None, None

def GetRepoFiles():

    url = "https://api.github.com/repos/{}/{}/git/trees/main?recursive=1".format(
        setting['owner'],
        setting['repo']
    )

    status, data = make_request(url)

    if status == 200:

        tree_data = json.loads(data)

        return [
            item['path']
            for item in tree_data.get('tree', [])
            if item['type'] == 'blob'
        ]

    else:

        print("Failed to fetch file list:", status)

        return None

def GetFileCommits(linkArray):

    returnArray = {}

    for link in linkArray:

        url = "https://api.github.com/repos/{}/{}/commits?path={}".format(
            setting['owner'],
            setting['repo'],
            urllib.quote(link)
        )

        status, data = make_request(url)

        if status == 200:

            commits = json.loads(data)

            if commits:

                dateCommits = commits[0]['commit']['committer']['date']

                returnArray[link] = int(convertISO2Time(dateCommits))

        else:

            print("Failed to fetch commit info:", status)

    return returnArray

def LoadGHFile(data):

    fileName = data['fileName']
    toolFolder = data['toolFolder']

    url = "https://api.github.com/repos/{}/{}/contents/{}?ref=main".format(
        setting['owner'],
        setting['repo'],
        urllib.quote(fileName)
    )

    status, data_bytes = make_request(url)

    if status == 200:

        content = json.loads(data_bytes)

        encoded = content['content']

        decoded = base64.b64decode(encoded)

        full_path = os.path.join(toolFolder, fileName)

        folder = os.path.dirname(full_path)

        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(full_path, "wb") as f:
            f.write(decoded)

        print(fileName + " downloaded and saved!")

    else:

        print("Failed:", status)

def SyschronizeGH(data):

    toolFolder = data['toolFolder']

    repoFiles = GetRepoFiles()

    if repoFiles:

        toolFiles = GetToolFiles(toolFolder)

        commitFiles = GetFileCommits(repoFiles)

        folders = []

        for f in commitFiles:

            if '/' in f:

                folder, _ = f.rsplit('/', 1)

                if folder not in folders:
                    folders.append(folder)

            if not os.path.exists(os.path.join(toolFolder, f)):

                LoadGHFile({
                    'toolFolder': toolFolder,
                    'fileName': f
                })

            else:

                if commitFiles[f] > toolFiles.get(f, 0):

                    LoadGHFile({
                        'toolFolder': toolFolder,
                        'fileName': f
                    })

    else:

        folders = [
            f for f in os.listdir(data['toolFolder'])
            if os.path.isdir(os.path.join(data['toolFolder'], f))
        ]

    for folder in folders:

        path = os.path.join(toolFolder, folder)

        if path not in sys.path:
            sys.path.append(path)

def DictToFlags(dict):

    return [
        '{}="{}"'.format(k, v)
        if isinstance(v, basestring)
        else '{}={}'.format(k, v)
        for k, v in dict.items()
    ]

def LoadUI(data):
    module = __import__(data['module'], fromlist=['*'])
    try:
        importlib.reload(module)
    except:
        reload(module)

    module.CreateUI(data)

def CreateTool(data):
    if 'paths' in data:

        for path in data['paths']:

            if path not in sys.path:
                sys.path.append(path)

    SyschronizeGH(data)

    UIData = data['UI']

    if cmds.window(UIData['windowName'], exists=True):
        cmds.deleteUI(UIData['windowName'])

    cmds.window(
        UIData['windowName'],
        title=UIData['windowTitle']
    )

    cmds.rowColumnLayout(
        'MainLayout',
        nc=UIData['column']
    )

    cmds.setParent("..")

    cmds.showWindow(UIData['windowName'])

    for layoutData in UIData['layouts']:
        LoadUI(layoutData)