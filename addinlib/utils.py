# Utility functions.
#
# This file is part of a modified version of thomasa88lib, a library of useful 
# Fusion 360 add-in/script functions.
#
# Copyright (c) 2021 ZXYNINE
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import adsk.core, adsk.fusion, adsk.cam

import inspect
import os, re, json
import importlib

from . import AppObjects

def short_class(obj:adsk.core.Base):
    '''Returns shortened name of Object class'''
    return obj.classType().split('::')[-1]

_DEPLOY_FOLDER_PATTERN = re.compile(r'.*/webdeploy/production/[^/]+')
def get_fusion_deploy_folder():
    ''' Get the Fusion 360 deploy folder.

    Typically:
     * Windows: C:/Users/<user>/AppData/Local/Autodesk/webdeploy/production/<hash>
     * Mac: /Users/<user>/Library/Application Support/Autodesk/webdeploy/production/<hash>

    NOTE! The structure within the deploy folder is not the same on Windows and Mac!
    E.g. see the examples for get_fusion_ui_resource_folder().
    '''
    # Strip the suffix from the UI resource folder, i.e.:
    # Windows: /Fusion/UI/FusionUI/Resources
    # Mac: /Autodesk Fusion 360.app/Contents/Libraries/Applications/Fusion/Fusion/UI/FusionUI/Resources
    return _DEPLOY_FOLDER_PATTERN.match(get_fusion_ui_resource_folder()).group(0)

_resFolder = None
def get_fusion_ui_resource_folder():
    '''
    Get the Fusion UI resource folder. Note: Not all resources reside here.

    Typically:
     * Windows: C:/Users/<user>/AppData/Local/Autodesk/webdeploy/production/<hash>/Fusion/UI/FusionUI/Resources
     * Mac: /Users/<user>/Library/Application Support/Autodesk/webdeploy/production/<hash>/Autodesk Fusion 360.app/Contents/Libraries/Applications/Fusion/Fusion/UI/FusionUI/Resources
    '''
    global _resFolder
    if not _resFolder:
        _resFolder = AppObjects.GetUi().workspaces.itemById('FusionSolidEnvironment').resourceFolder.replace('/Environment/Model', '')
    return _resFolder

def get_caller_path():
    '''Gets the filename of the file calling the function
    that called this function. That is, is nested in "two steps". '''
    caller_file = os.path.abspath(inspect.stack(0)[2][1])
    return caller_file

def get_file_path():
    '''Gets the filename of the function that called this
    function.'''
    caller_file = os.path.abspath(inspect.stack(0)[1][1])
    return caller_file

def get_file_dir():
    '''Gets the directory containing the file which function
    called this function.'''
    caller_file = os.path.dirname(os.path.abspath(inspect.stack(0)[1][1]))
    return caller_file

# Allows for re-import of multiple modules
def ReImport_List(*args):
	for module in args: importlib.reload(module)

def clear_ui_items(*items):
	"""Attempts to call 'deleteMe()' on every item provided. Returns True if all deletions are a success"""
	return all([item.deleteMe() for item in items if item is not None])


def is_parametric_mode():
	# Checking workspace type in DocumentActivated handler fails since Fusion 360 v2.0.10032
	# UserInterface.ActiveWorkspace throws when it is called from DocumentActivatedHandler
	# during Fusion 360 start-up(?). Checking for app_.isStartupComplete does not help.
	try:
		app_, ui_ = AppObjects.GetAppUI()
		if ui_.activeWorkspace.id == 'FusionSolidEnvironment':
			design = adsk.fusion.Design.cast(app_.activeProduct)
			return bool(design and design.designType == adsk.fusion.DesignTypes.ParametricDesignType)
	except: return False


#This is a context manager that just ignores what happens
class Ignore:__enter__=lambda cls:cls;__exit__=lambda *args:True

# def AppObjects(): return GetApp(),GetUi()
# def GetApp(): return adsk.core.Application.cast(adsk.core.Application.get())
# def GetUi(): return GetApp().userInterface



class CustomEvents:
	def Create(CustomEventID:str):
		app = AppObjects.GetApp()
		app.unregisterCustomEvent(CustomEventID)
		return app.registerCustomEvent(CustomEventID)
		
	def Fire(CustomEventID:str, additionalInfo='', toJsonStr=False):
		if not toJsonStr: strInfo = additionalInfo
		else: strInfo = json.dumps(additionalInfo)
		return AppObjects.GetApp().fireCustomEvent(CustomEventID, strInfo)

	def Remove(CustomEventID:str):
		return AppObjects.GetApp().unregisterCustomEvent(CustomEventID)







def toIdentifier(toId: str, toUnder:set={'-',' '}): return ''.join(['_'*(c in toUnder) or c*(c.isidentifier()) for c in toId])

def exists(obj):return obj is not None
def ifDelete(obj:adsk.core.CommandControl): return obj.deleteMe() if exists(obj) and obj.isValid else False
def getDelete(collection:adsk.core.CommandDefinitions,objId): ifDelete(collection.itemById(objId))
def deleteAll(*objs): return all(map(ifDelete,objs))

def executeCommand(cmdName):  AppObjects.GetUi().commandDefinitions.itemById(cmdName).execute()

def doEvents(): return adsk.doEvents()


class camera:
	def get(): return AppObjects.GetApp().activeViewport.camera
	
	def viewDirection(camera_copy:adsk.core.Camera):
		camera_copy = camera_copy or camera.get()
		return camera_copy.eye.vectorTo(camera_copy.target)

	def updateCamera(camera_copy:adsk.core.Camera, smoothTransition=True):
		camera_copy.isSmoothTransition = smoothTransition
		AppObjects.GetApp().activeViewport.camera = camera_copy
		doEvents()
