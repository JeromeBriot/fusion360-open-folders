#Author-Jerome Briot
#Description-

import adsk.core, adsk.fusion, traceback  # pylint: disable=import-error
import platform
import os
import plistlib
import subprocess
import json
import re

thisAddinName = 'OpenFolders'
thisAddinTitle = 'Open Folders'
thisAddinVersion = '0.2.0'
thisAddinAuthor = 'Jerome Briot'
thisAddinContact = 'jbtechlab@gmail.com'

thisFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)))

app = adsk.core.Application.get()
ui  = app.userInterface

# https://forums.autodesk.com/t5/fusion-360-api-and-scripts/api-bug-cannot-click-menu-items-in-nested-dropdown/m-p/9669144#M10876
nestedMenuBugFixed = False

controls = {
            'titles': [],
            'ids': [],
            'parentsIds': [],
            'types': [],
            'paths': [],
            'separators': [],
            'icons': []
            }

undocumentedControls = []

handlers = []

def getDefaultControls():

    global controls

    if platform.system() == 'Windows':

        desktopPath = os.path.join(os.getenv('USERPROFILE'), 'Desktop')

        # https://stackoverflow.com/questions/2014554/find-the-newest-folder-in-a-directory-in-python
        directory = os.path.join(os.getenv('LOCALAPPDATA'), 'Autodesk', 'webdeploy', 'production')
        fusion360Install = max([os.path.join(directory,d) for d in os.listdir(directory)], key=os.path.getctime)

        fusion360Cpp = os.path.join(fusion360Install, 'CPP')
        fusion360Python = os.path.join(fusion360Install, 'Python')

        autodeskLocal = os.path.join(os.getenv('LOCALAPPDATA'), 'Autodesk')
        autodeskRoaming = os.path.join(os.getenv('APPDATA'), 'Autodesk')

        controls = {
                    'titles': [
                        'Install',
                        'API',
                        'C++',
                        'Python',
                        'Autodesk (Roaming)',
                        'Autodesk (Local)',
                        'Desktop',
                        'Appdata (Roaming)',
                        'Appdata (Local)',
                        'Temp',
                        'Preferences'
                        ],
                    'ids': [
                        'Fusion360Install',
                        'Fusion360Api',
                        'Fusion360Cpp',
                        'Fusion360Python',
                        'AutodeskRoaming',
                        'AutodeskLocal',
                        'WindowsDesktop',
                        'WindowsAppdataRoaming',
                        'WindowsAppdataLocal',
                        'WindowsTemp',
                        'Preferences'
                        ],
                    'parentsIds': [
                        'root',
                        'root',
                        'Fusion360Api',
                        'Fusion360Api',
                        'root',
                        'root',
                        'root',
                        'root',
                        'root',
                        'root',
                        'root'
                    ],
                    'types': [
                        'command',
                        'dropdown',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command'
                    ],
                    'paths': [
                        fusion360Install,
                        None,
                        fusion360Cpp,
                        fusion360Python,
                        autodeskRoaming,
                        autodeskLocal,
                        os.path.join(os.getenv('USERPROFILE'), 'Desktop'),
                        os.path.join(os.getenv('APPDATA')),
                        os.path.join(os.getenv('LOCALAPPDATA')),
                        os.path.join(os.getenv('TMP')),
                        getUserDataPath()
                        ],
                    'separators': [False, False, False, False, False, True, False, False, False, True, True],
                    'icons': [
                        'fusion360',
                        'fusion360',
                        'fusion360',
                        'fusion360',
                        'autodesk',
                        'autodesk',
                        'windows',
                        'windows',
                        'windows',
                        'windows',
                        ''
                    ]}

        if not nestedMenuBugFixed:
            controls['separators'][1] = True

    else:

        userPath = os.path.expanduser('~')

        desktopPath = os.path.join(userPath, 'Desktop')

        autodeskPath = os.path.join(userPath, 'Library', 'Application Support', 'Autodesk')

        fusionAppPath = os.path.realpath(os.path.join(autodeskPath, 'webdeploy', 'production', 'Autodesk Fusion 360.app'))

        fusion360Install = os.path.join(fusionAppPath, 'Contents')

        fusion360Cpp = os.path.join(fusion360Install, 'Libraries', 'Neutron', 'CPP')
        fusion360Python = os.path.join(fusion360Install, 'Frameworks', 'Python.framework', 'Versions')

        controls = {
                    'titles': [
                        'Install',
                        'API',
                        'C++',
                        'Python',
                        'Autodesk',
                        'Desktop',
                        'Preferences'
                        ],
                    'ids': [
                        'Fusion360Install',
                        'Fusion360Api',
                        'Fusion360Cpp',
                        'Fusion360Python',
                        'Autodesk',
                        'Desktop',
                        'Preferences'
                        ],
                    'parentsIds': [
                        'root',
                        'root',
                        'Fusion360Api',
                        'Fusion360Api',
                        'root',
                        'root',
                        'root'
                    ],
                    'types': [
                        'command',
                        'dropdown',
                        'command',
                        'command',
                        'command',
                        'command',
                        'command'
                    ],
                    'paths': [
                        fusion360Install,
                        None,
                        fusion360Cpp,
                        fusion360Python,
                        autodeskPath,
                        desktopPath,
                        getUserDataPath()
                    ],
                    'separators': [False, False, False, False, True, True, True],
                    'icons': [
                        'fusion360',
                        'fusion360',
                        'fusion360',
                        'fusion360',
                        'autodesk',
                        'macos',
                        ''
                    ]
                    }

        if not nestedMenuBugFixed:
            controls['separators'][1] = True

def getUndocumentedControls():

    global undocumentedControls

    if not nestedMenuBugFixed:
        undocumentedControls = {
                                'titles': [],
                                'ids' : [],
                                'parentsIds': [],
                                'types': [],
                                'paths': [],
                                'separators': [],
                                'icons': []
                                }
    else:
        idx = 4

    pathsDict = json.loads(app.executeTextCommand('Paths.Get'))

    if nestedMenuBugFixed:
        controls['titles'].insert(idx, 'Undocumented')
        controls['ids'].insert(idx, thisAddinName + 'Undocumented')
        controls['parentsIds'].insert(idx, 'root')
        controls['types'].insert(idx, 'dropdown')
        controls['paths'].insert(idx, None)
        controls['separators'].insert(idx, True)
        controls['icons'].insert(idx, 'fusion360')

    for key in pathsDict.keys():

        if key != 'isInstalledBuild':

            pn = ' '.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', key[0].upper() + key[1:]))

            if pathsDict[key].startswith('Auto-save location is '):
                pp = pathsDict[key].replace('Auto-save location is ', '')
            else:
                pp = pathsDict[key]

            if key == 'AppLogFilePath':
                pp = os.path.dirname(pp)

            if not pp.endswith('/'):
                pp += '/'

            if nestedMenuBugFixed:
                idx += 1
                controls['titles'].insert(idx, pn)
                controls['ids'].insert(idx, thisAddinName + pn.replace(' ', ''))
                controls['parentsIds'].insert(idx, thisAddinName + 'Undocumented')
                controls['types'].insert(idx, 'command')
                controls['paths'].insert(idx, pp)
                controls['separators'].insert(idx, False)
                controls['icons'].insert(idx, 'fusion360')
            else:
                undocumentedControls['titles'].append(pn)
                undocumentedControls['ids'].append(thisAddinName + pn.replace(' ', ''))
                undocumentedControls['parentsIds'].append('root')
                undocumentedControls['types'].append('command')
                undocumentedControls['paths'].append(pp)
                undocumentedControls['separators'].append(False)
                undocumentedControls['icons'].append('fusion360')


def getCustomControls():

    userDataPath = getUserDataPath()

    customPathFile = os.path.join(userDataPath, 'customPaths.json')

    if not os.path.exists(customPathFile):
        createJsonFiles(customPathFile)
    else:
        with open(customPathFile, 'r') as file:
            customControls = json.load(file)

        controls['titles'] = controls['titles'][0:-1] + customControls['titles'] + [controls['titles'][-1]]
        controls['ids'] = controls['ids'][0:-1] + customControls['ids'] + [controls['ids'][-1]]
        controls['parentsIds'] = controls['parentsIds'][0:-1] + customControls['parentsIds'] + [controls['parentsIds'][-1]]
        controls['types'] = controls['types'][0:-1] + customControls['types'] + [controls['types'][-1]]
        controls['paths'] = controls['paths'][0:-1] + customControls['paths'] + [controls['paths'][-1]]
        controls['separators'] = controls['separators'][0:-1] + customControls['separators'] + [controls['separators'][-1]]
        controls['icons'] = controls['icons'][0:-1] + customControls['icons'] + [controls['icons'][-1]]


def checkResources():

    global controls

    for i in range(0, len(controls['icons'])):

        if controls['icons'][i] != '':
            resourcePath = os.path.join(thisFilePath, 'resources', controls['icons'][i])

            if os.path.exists(resourcePath):
                controls['icons'][i] = 'resources/' + controls['icons'][i]
            else:
                controls['icons'][i] = ''


class commandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):

    def __init__(self):
        super().__init__()

    def notify(self, args):

        try:

            if args.firingEvent.sender.name in controls['titles']:
                idx = controls['titles'].index(args.firingEvent.sender.name)
                if controls['paths'][idx]:
                    path = os.path.realpath(controls['paths'][idx])
            else:
                idx = undocumentedControls['titles'].index(args.firingEvent.sender.name)
                if undocumentedControls['paths'][idx]:
                    path = os.path.realpath(undocumentedControls['paths'][idx])

            if path:

                if os.path.exists(path):
                    if platform.system() == 'Windows':
                        os.startfile(path)
                    else:
                        subprocess.check_call(["open", "--", path])
                else:
                    ui.messageBox('Path not found: ' + path, '{} v{}'.format(thisAddinTitle, thisAddinVersion), adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), '{} v{}'.format(thisAddinTitle, thisAddinVersion), adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)


def getUserDataPath():

    if platform.system() == 'Windows':
        dataPath = os.path.join(os.getenv('APPDATA'), thisAddinName + 'ForFusion360')
    else:
        dataPath = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', thisAddinName + 'ForFusion360')

    if not os.path.exists(dataPath):
        os.mkdir(dataPath)

    userDataPath = os.path.join(dataPath, app.userId)

    if not os.path.exists(userDataPath):
        os.mkdir(userDataPath)

    return userDataPath


def createJsonFiles(customPathFile):

    emptyControls = {
                'titles': [],
                'ids': [],
                'parentsIds': [],
                'types': [],
                'paths': [],
                'separators': [],
                'icons': []
                }

    with open(customPathFile, 'w') as f:
        json.dump(emptyControls, f, indent=2)


def cleanUI():

    solidScripts = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    cntrls = solidScripts.controls

    separator = cntrls.itemById(thisAddinName + 'separator')
    if separator:
        separator.deleteMe()

    cmdDefs = ui.commandDefinitions

    for i in range(0, len(controls['titles'])):
        cmdDef = cmdDefs.itemById(thisAddinName + controls['ids'][i])
        if cmdDef:
            cmdDef.deleteMe()

    if not nestedMenuBugFixed:
        for i in range(0, len(undocumentedControls['titles'])):
            cmdDef = cmdDefs.itemById(thisAddinName + undocumentedControls['ids'][i])
            if cmdDef:
                cmdDef.deleteMe()

    dropdownCntr = cntrls.itemById(thisAddinName + 'root' + 'Dropdown')
    if dropdownCntr:
        for i in range(0, len(controls['titles'])):
            cntrl = dropdownCntr.controls.itemById(thisAddinName + controls['ids'][i])
            if cntrl:
                cntrl.isPromoted = False
                cntrl.deleteMe()
            if controls['separators'][i]:
                cntrl = dropdownCntr.controls.itemById(thisAddinName + controls['ids'][i] + 'separator')
                if cntrl:
                    cntrl.isPromoted = False
                    cntrl.deleteMe()

        dropdownCntr.deleteMe()

    if not nestedMenuBugFixed:
        dropdownCntr = cntrls.itemById(thisAddinName + 'root' + 'Dropdown' + 'Undoc')
        if dropdownCntr:
            for i in range(0, len(undocumentedControls['titles'])):
                cntrl = dropdownCntr.controls.itemById(thisAddinName + undocumentedControls['ids'][i])
                if cntrl:
                    cntrl.isPromoted = False
                    cntrl.deleteMe()
                if undocumentedControls['separators'][i]:
                    cntrl = dropdownCntr.controls.itemById(thisAddinName + undocumentedControls['ids'][i] + 'separator')
                    if cntrl:
                        cntrl.isPromoted = False
                        cntrl.deleteMe()

            dropdownCntr.deleteMe()

def run(context):

    try:

        getDefaultControls()

        if nestedMenuBugFixed:
            getUndocumentedControls()

        getCustomControls()

        cmdDefs = ui.commandDefinitions

        commandCreated = commandCreatedEventHandler()

        solidScripts = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        solidScripts.controls.addSeparator(thisAddinName + 'separator', '')

        solidScripts.controls.addDropDown(thisAddinTitle, '', thisAddinName + 'root' + 'Dropdown', '', False)

        for i in range(0, len(controls['icons'])):

            if controls['icons'][i] != '':
                resourcePath = os.path.join(thisFilePath, 'resources', controls['icons'][i])

                if os.path.exists(resourcePath):
                    controls['icons'][i] = 'resources/' + controls['icons'][i]
                else:
                    controls['icons'][i] = ''

        for i in range(0, len(controls['titles'])):

            if controls['types'][i] == 'command':

                button = cmdDefs.addButtonDefinition(thisAddinName + controls['ids'][i], controls['titles'][i], controls['paths'][i], controls['icons'][i])

                button.commandCreated.add(commandCreated)
                handlers.append(commandCreated)

                if controls['parentsIds'][i] == 'root':
                    dropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown')
                else:
                    rootDropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown')
                    dropdown = rootDropdown.controls.itemById(thisAddinName + controls['parentsIds'][i])

                dropdown.controls.addCommand(button)

            else:

                dropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown')
                dropdown.controls.addDropDown(controls['titles'][i], controls['icons'][i], thisAddinName + controls['ids'][i], '', False)

            if controls['separators'][i]:
                dropdown.controls.addSeparator(thisAddinName + controls['ids'][i] + 'separator', '')

        if not nestedMenuBugFixed:

            getUndocumentedControls()

            for i in range(0, len(undocumentedControls['icons'])):

                if undocumentedControls['icons'][i] != '':
                    resourcePath = os.path.join(thisFilePath, 'resources', undocumentedControls['icons'][i])

                    if os.path.exists(resourcePath):
                        undocumentedControls['icons'][i] = 'resources/' + undocumentedControls['icons'][i]
                    else:
                        undocumentedControls['icons'][i] = ''

            solidScripts.controls.addDropDown(thisAddinTitle + ' (undocumented)', '', thisAddinName + 'root' + 'Dropdown' + 'Undoc', '', False)

            for i in range(0, len(undocumentedControls['titles'])):

                if undocumentedControls['types'][i] == 'command':

                    button = cmdDefs.addButtonDefinition(thisAddinName + undocumentedControls['ids'][i], undocumentedControls['titles'][i], undocumentedControls['paths'][i], undocumentedControls['icons'][i])

                    button.commandCreated.add(commandCreated)
                    handlers.append(commandCreated)

                    if undocumentedControls['parentsIds'][i] == 'root':
                        dropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown' + 'Undoc')
                    else:
                        rootDropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown' + 'Undoc')
                        dropdown = rootDropdown.controls.itemById(thisAddinName + undocumentedControls['parentsIds'][i])

                    dropdown.controls.addCommand(button)

                else:

                    dropdown = solidScripts.controls.itemById(thisAddinName + 'root' + 'Dropdown' + 'Undoc')
                    dropdown.controls.addDropDown(undocumentedControls['titles'][i], undocumentedControls['icons'][i], thisAddinName + undocumentedControls['ids'][i], '', False)

                if undocumentedControls['separators'][i]:
                    dropdown.controls.addSeparator(thisAddinName + undocumentedControls['ids'][i] + 'separator', '')

        if context['IsApplicationStartup'] is False:
            ui.messageBox("The '{}' command has been added\nto the ADD-INS panel of the DESIGN workspace.".format(thisAddinTitle), '{} v{}'.format(thisAddinTitle, thisAddinVersion))

    except:
        if ui:
            cleanUI()
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), '{} v{}'.format(thisAddinTitle, thisAddinVersion))


def stop(context):

    try:

        cleanUI()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), '{} v{}'.format(thisAddinTitle, thisAddinVersion))
