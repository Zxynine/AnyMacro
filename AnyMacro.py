#Author-ZXYNINE
#Description-Shows a menu that let you assign macros from last run commands.

# This file is part of AnyMacro, a Fusion 360 add-in for assigning
# macros from last run commands.
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

from os import name
import adsk.core, adsk.fusion, adsk.cam

from collections import deque
from typing import Deque, Union
import os.path as path,json


# Import relative path to avoid namespace pollution
from .AddinLib import utils, events, manifest, error, settings, geometry, AppObjects
utils.ReImport_List(AppObjects, events, manifest, error, settings, geometry, utils)


NAME = 'AnyMacro'
VERSION = manifest.getVersion()
FILE_DIR = path.dirname(path.realpath(__file__))
VERSION_INFO = f'({NAME} v {VERSION})'
CMD_DESCRIPTION = 'Enables or disables the tracking of commands to create a macro.'
COMMAND_DATA = CMD_DESCRIPTION + '\n\n' + VERSION_INFO + '\n'

ENABLE_CMD_DEF_ID = 'zxynine_anyMacroList'
PANEL_ID = 'zxynine_anyMacroPanel'
NO_MACROS_ID = 'zxynine_anyMacroListEmpty'
TRACKING_DROPDOWN_ID = 'zxynine_anyMacroDropdown'
MACRO_DROPDOWN_ID = 'zxynine_anyMacroPremadeMacrosDropdown'
CONSECUTIVE_TOGGLE_ID = 'zxynine_anyMacroBlockConsecutive'
BUILD_MACRO_CMD_DEF_ID = 'zxynine_anyMacroBuildMacro'
CLEAR_RECORD_CMD_ID = 'zxynine_anyMacroClearRecord'
ADD_MACRO_CUSTOM_ID = 'AnyMacro_Add_Macro'

app_:adsk.core.Application = None
ui_:adsk.core.UserInterface = None
error_catcher_ = error.ErrorCatcher()
events_manager_ = events.EventsManager(error_catcher_)
manifest_ = manifest.read()
add_macro_event:adsk.core.CustomEvent=None
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#Commands/Settings

MAX_TRACK = 10
MACRO_DATA_PATH = path.join(FILE_DIR,'macros')
MACRO_FILE_DATA_PATH = path.join(MACRO_DATA_PATH, 'SavedMacros.json')

allMacros = []

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#Simple functions
def exists(obj):return obj is not None
def getDelete(collection:adsk.core.CommandDefinitions,objId): utils.ifDelete(collection.itemById(objId))
def deleteAll(*objs): return all(map(utils.ifDelete,objs))

def UpdateButton(cmdDef: adsk.core.CommandDefinition,Title,Icon): cmdDef.resourceFolder = Icon; cmdDef.controlDefinition.name = Title
def FullPromote(cmdCtrl:adsk.core.CommandControl): cmdCtrl.isPromoted=cmdCtrl.isPromotedByDefault = True
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#Specific Functions

# Commands without icons cannot have shortcuts, so add one if needed. 
# Maybe because the "Pin to" options in the same menu would fail? Creds to u/lf_1 on reddit.
def checkIcon(cmdDef:adsk.core.CommandDefinition, noIconPath:str = './resources/noicon'):
	try: 
		if not cmdDef.resourceFolder: cmdDef.resourceFolder = noIconPath
	except: cmdDef.resourceFolder = noIconPath
	return cmdDef

def update_enable_text(curCount=0):
	if curCount > MAX_TRACK: currentMacro.stopTracking()
	if not CommandTracker.tracking_: text,icon = 	f'Start recording (Auto-stop after {MAX_TRACK} unique commands)',		'./resources/record'
	else: text,icon = 								f'Stop recording (Auto-stop after {MAX_TRACK-curCount} more commands)',	'./resources/stop'
	UpdateButton(enable_cmd.definition, text, icon)




def MessagePromptCast(messageText, messageBoxTitle, buttonType=adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType, iconType=adsk.core.MessageBoxIconTypes.QuestionIconType):
	dialogResult = ui_.messageBox(messageText, messageBoxTitle, buttonType, iconType) 
	return {adsk.core.DialogResults.DialogYes:True,adsk.core.DialogResults.DialogNo:False}.get(dialogResult, None)

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

class ReferenceBase:
	def __init__(self,cmdDef:adsk.core.CommandDefinition=None, cmdCtrl: Union[adsk.core.CommandControl,adsk.core.DropDownControl]=None):
		self.definition = cmdDef
		self.control = cmdCtrl
		self.id = cmdCtrl.id if exists(cmdCtrl) else cmdDef.id if exists(cmdDef) else None
	def deleteMe(self):	utils.ifDelete(self.control); self.definition=self.control=None

class CommandRef(ReferenceBase):
	def __init__(self,parentControls:adsk.core.ToolbarControls,newId,newName,newIcon='./resources/noicon',newToolTip=''):
		getDelete(ui_.commandDefinitions, newId)
		cmdDef = ui_.commandDefinitions.addButtonDefinition(newId, newName, newToolTip, newIcon)
		super().__init__(cmdDef, parentControls.addCommand(checkIcon(cmdDef)))

class DropdownRef(ReferenceBase):
	def __init__(self,parentControls:adsk.core.ToolbarControls,newId,newName,newIcon='./resources/noicon',newToolTip=''):
		getDelete(parentControls, newId)
		cmdCtrl:adsk.core.DropDownControl = parentControls.addDropDown(newName, newIcon, newId)
		self.dropdownControls = cmdCtrl.controls
		super().__init__(None, cmdCtrl)
	
class ToggleRef(ReferenceBase):
	def __init__(self,parentControls:adsk.core.ToolbarControls,newId,newName,startValue,newToolTip=''):
		getDelete(ui_.commandDefinitions, newId)
		cmdDef = ui_.commandDefinitions.addCheckBoxDefinition(newId, newName, newToolTip, startValue)
		self.controlDefinition:adsk.core.CheckBoxControlDefinition = cmdDef.controlDefinition
		super().__init__(cmdDef, parentControls.addCommand(cmdDef))
	@property
	def value(self):return self.controlDefinition.isChecked

# def MakeSeperator(parentControls:adsk.core.ToolbarControls):parentControls.addSeparator
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

panel_:adsk.core.ToolbarPanel = None
tracking_dropdown_:DropdownRef = None
macro_dropdown_:DropdownRef = None
macro_dropdown_empty:CommandRef = None
enable_cmd:CommandRef = None
build_macro_cmd:CommandRef = None
clear_record_cmd:CommandRef = None
consecutive_block_tgl:ToggleRef=None

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def getQueuedEvents(executeList:deque):
	def initialCreate(args: adsk.core.CommandCreatedEventArgs):
		currentCommand = None
		commandOrder = deque(executeList)
		def stopHandlers():
			nonlocal currentCommand; currentCommand = None
			startingInfo.remove(); terminatedInfo.remove()

		def CmdStartingHandler(args:adsk.core.ApplicationCommandEventArgs):
			if args.commandId == commandOrder[0]:
				nonlocal currentCommand; currentCommand = commandOrder.popleft()
			if len(commandOrder) == 0: stopHandlers()
		def CmdTerminatedHandler(args:adsk.core.ApplicationCommandEventArgs):
			if args.commandId == currentCommand:
				if len(commandOrder) == 0: stopHandlers()
				else: utils.executeCommand(commandOrder[0])
				
		startingInfo = events_manager_.add_handler(ui_.commandStarting, CmdStartingHandler)
		terminatedInfo = events_manager_.add_handler(ui_.commandTerminated, CmdTerminatedHandler)
		utils.executeCommand(commandOrder[0])
	return initialCreate

class Macro:
	@staticmethod
	def fromJson(JsonObject: object):
		if type(JsonObject) is str: return Macro.fromJson(json.loads(JsonObject))
		MacroMethod = {dict:Macro.fromDict, list:Macro.fromList}.get(type(JsonObject),None)
		if MacroMethod is None: raise TypeError('Object type must be a: JsonDict, or a JsonList')
		return MacroMethod(JsonObject)

	@classmethod
	def fromList(cls, macroList:list): return [cls.fromDict(dict) for dict in macroList]
	@classmethod
	def fromDict(cls, macroDict:dict):
		MacroName = macroDict['name']
		MacroId = macroDict['id']
		executeList = macroDict['executeList']
		parentControl:adsk.core.ToolbarControls = macro_dropdown_.control.controls
		return Macro(executeList,parentControl,MacroId,MacroName,True)

	@classmethod
	def toList(cls): return [cls.toDict(macro) for macro in allMacros]
	def toDict(self):
		macroDict = {}
		macroDict['name']=self.name
		macroDict['id']=self.id
		macroDict['executeList']=self.executeList
		return macroDict

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def __init__(self,CommandIdList:list,parentControls:adsk.core.ToolbarControls=None,macroId=None,macroName=None, isBuilt = False):
		allMacros.append(self)
		self.executeList = list(CommandIdList)
		self.parentControls = parentControls or macro_dropdown_.dropdownControls
		self.isBuilt = isBuilt
		self.initialise()
		self.updateIdentity(macroId,macroName)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def updateIdentity(self,MacroId=None,MacroName=None):
		if MacroName is None:
			MacroName, cancelled = ui_.inputBox('Enter macro name:','Naming Macro','')
			if cancelled: return False
		self.name = MacroName
		self.id = MacroId or f'AnyMacro_{utils.toIdentifier(MacroName)}'
		self.updateCommands(self.parentControls)
		return True
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def updateCommands(self, parentControls:adsk.core.ToolbarControls):
		self.removeCommands()
		self.parentControls = parentControls
		self.Dropdown = DropdownRef(parentControls, f'{self.id}_group', self.name, './resources/anymacro')
		self.Command = CommandRef(self.Dropdown.dropdownControls, self.id, self.name, './resources/anymacro')
		self.Delete =CommandRef(self.Dropdown.dropdownControls, f'{self.id}_delete', f'Delete {self.name}', './resources/delete')
		self.updateHandlers(self.executeList)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def updateHandlers(self,CommandIdList:list = None):
		self.removeHandlers()
		self.executeList = list(CommandIdList)
		def MacroRemoveHandler(args:adsk.core.CommandCreatedEventArgs):
			result = MessagePromptCast(f'Are you sure you wish to delete the macro "{self.name}"?', 'Confirm Macro Deletion')
			if result is not True: return #Cancels the deletion
			self.removeAll()
			if self.isBuilt: macrosToJson() #Updates the save file
			else: currentMacro.clear() #Removes the history along with it
		self.createInfo = events_manager_.add_handler(self.Command.definition.commandCreated, getQueuedEvents(self.executeList))
		self.removeInfo = events_manager_.add_handler(self.Delete.definition.commandCreated, MacroRemoveHandler)
		if self.isBuilt: macrosToJson()
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def initialise(self):
		self.Dropdown:DropdownRef=None
		self.Command:CommandRef=None
		self.Delete:CommandRef=None
		self.createInfo = None
		self.removeInfo = None
	def removeCommands(self):
		if exists(self.Dropdown):self.Dropdown.deleteMe()
		if exists(self.Command):self.Command.deleteMe()
		if exists(self.Delete):self.Delete.deleteMe()
	def removeHandlers(self):
		if exists(self.createInfo):self.createInfo.remove()
		if exists(self.removeInfo):self.removeInfo.remove()
	def removeAll(self): 
		self.removeHandlers()
		self.removeCommands()
		allMacros.remove(self)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

class CommandTracker:
	deleteID = 0
	tracking_ = False
	@classmethod
	def toggle(cls,value):
		cls.tracking_ = value
		update_enable_text()
		checkQueue()
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(self,): 
		self.executeList: Deque[ReferenceBase] = deque()
		self.cmdIds: dict = {}
		self.currentMacro:Macro=None
		self.startTracking()

	def startTracking(self):
		self.lastID = ''
		self.getHandler()
		CommandTracker.toggle(True)

	def stopTracking(self):
		CommandTracker.toggle(False)
		self.removeHandler()
		if self.count == 0: return
		self.currentMacro = Macro(self.cmdIds.values(), tracking_dropdown_.dropdownControls, 'TestMacroId', 'Test Macro')

	@property
	def count(self):return len(self.executeList)

	def log(self, cmdDef: adsk.core.CommandDefinition):
		self.lastID = cmdDef.id
		newId = f'{cmdDef.id}_Macro_Fragment_{CommandTracker.deleteID}'
		CommandTracker.deleteID +=1
		self.cmdIds[newId] = cmdDef.id

		getDelete(ui_.commandDefinitions, newId)
		newCmdDef = checkIcon(ui_.commandDefinitions.addButtonDefinition(newId, cmdDef.name,'Click to remove from Macro', cmdDef.resourceFolder))
		newCmdCtrl = tracking_dropdown_.dropdownControls.addCommand(newCmdDef)

		def removeHandler(args: adsk.core.CommandCreatedEventArgs):	
			getDelete(tracking_dropdown_.dropdownControls, newCmdDef.id)
			removeInfo.remove()
			self.cmdIds.pop(newId)
			self.currentMacro.updateHandlers(self.cmdIds.values())

		removeInfo = events_manager_.add_handler(newCmdDef.commandCreated,removeHandler)
		self.executeList.append(ReferenceBase(newCmdDef,newCmdCtrl))
		update_enable_text(self.count)

	def build(self):
		if self.count == 0: return
		self.currentMacro.isBuilt = True #Enables the remove handler to update the json
		self.currentMacro.parentControls = macro_dropdown_.dropdownControls
		if self.currentMacro.updateIdentity(): #Forces the macro to ask for a name and update
			macrosToJson() #Saves all current macros
			self.clear()

	def clear(self): 
		self.currentMacro = None
		self.executeList=[cmd.deleteMe() for cmd in self.executeList][:0]
		self.cmdIds.clear()
		checkQueue()

	def getHandler(self):
		def command_starting_handler(args:adsk.core.ApplicationCommandEventArgs):
			cmdDef = args.commandDefinition
			if cmdDef.id in {enable_cmd.id,'SelectCommand'}:return # Skip ourselves/Select
			elif cmdDef.id != self.lastID: self.log(cmdDef) #Commands start twice? Dont log that.
			elif not consecutive_block_tgl.value: self.lastID = ''
		self.starting_handler = events_manager_.add_handler(ui_.commandStarting, command_starting_handler)

	def removeHandler(self): self.starting_handler.remove()

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

currentMacro : CommandTracker = None

def checkQueue(): #This determines whether the save button is visible (only visible after recording)
	viewValue = exists(currentMacro) and currentMacro.count > 0
	build_macro_cmd.control.isVisible = viewValue
	clear_record_cmd.control.isVisible = viewValue

	

def enable_cmd_def__created_handler(args: adsk.core.CommandCreatedEventArgs):
	def enable_command_execute_handler(args:adsk.core.CommandEventArgs):
		global currentMacro
		if currentMacro is None: currentMacro = CommandTracker()
		else: currentMacro.startTracking() if (not CommandTracker.tracking_) else currentMacro.stopTracking()
	events_manager_.add_handler(args.command.execute, callback=enable_command_execute_handler)


def build_macro_handler(args:adsk.core.CommandCreatedEventArgs):
	if exists(currentMacro): currentMacro.build()

def clear_record_handler(args:adsk.core.CommandCreatedEventArgs):
	if exists(currentMacro): 
		currentMacro.currentMacro.removeAll()
		currentMacro.clear()

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||




@error_catcher_
def run(context):
	global app_, ui_, panel_
	app_,ui_ = AppObjects.GetAppUI()
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Add the command to the tab.
	panels = ui_.allToolbarTabs.itemById('ToolsTab').toolbarPanels
	getDelete(panels,PANEL_ID)
	panel_ = panels.add(PANEL_ID, NAME)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	add_primary_commands(panel_)
	update_enable_text()
	checkQueue()
	jsonToMacros() #Loads the saved macros
	createAddMacroCustomEvent()
	createBuiltInCommands()

@error_catcher_
def stop(context):
	removeAddMacroCustomEvent()
	removeBuiltInCommands()
	events_manager_.clean_up()
	deleteAll(tracking_dropdown_.control, macro_dropdown_.control, panel_)



#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


def add_primary_commands(parent:adsk.core.ToolbarPanel):
	global tracking_dropdown_
	tracking_dropdown_ = DropdownRef(parent.controls, TRACKING_DROPDOWN_ID, 'Macro Recorder', './resources/tracker')
	add_record_dropdown(tracking_dropdown_.control.controls)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	global macro_dropdown_
	macro_dropdown_ = DropdownRef(parent.controls, MACRO_DROPDOWN_ID, 'Custom Macros', './resources/allmacros')
	add_macro_dropdown(macro_dropdown_.control.controls)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	global consecutive_block_tgl
	consecutive_block_tgl = ToggleRef(parent.controls, CONSECUTIVE_TOGGLE_ID, 'Block Consecutive Fires', False)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def add_record_dropdown(parent:adsk.core.ToolbarControls):
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Cannot get checkbox to play nicely (won't update without collapsing the menu and the default checkbox icon is not showing...).  See checkbox-test branch.
	global enable_cmd
	enable_cmd = CommandRef(parent, ENABLE_CMD_DEF_ID, f'Loading...',newToolTip=COMMAND_DATA)
	events_manager_.add_handler(event=enable_cmd.definition.commandCreated, callback=enable_cmd_def__created_handler)
	FullPromote(enable_cmd.control)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	global clear_record_cmd
	clear_record_cmd = CommandRef(parent, CLEAR_RECORD_CMD_ID, 'Reset Recording', './resources/repeat')
	events_manager_.add_handler(event=clear_record_cmd.definition.commandCreated, callback=clear_record_handler)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	global build_macro_cmd
	build_macro_cmd = CommandRef(parent, BUILD_MACRO_CMD_DEF_ID, 'Save Macro', './resources/save')
	events_manager_.add_handler(event=build_macro_cmd.definition.commandCreated, callback=build_macro_handler)
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	parent.addSeparator(f'{ENABLE_CMD_DEF_ID}_Seperator')#|||||||||||||||||||||||||||||||||||||||||||||||||||||||


def add_macro_dropdown(parent:adsk.core.ToolbarControls):
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	global macro_dropdown_empty
	macro_dropdown_empty = CommandRef(parent, NO_MACROS_ID, 'All Custom Macros', './resources/noicon', 
													'Start by recording a new macro and saving it')
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	parent.addSeparator(f'{NO_MACROS_ID}_Seperator')#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||






#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#json data

def jsonToMacros():	Macro.fromList(settings.readDataFromFile(MACRO_FILE_DATA_PATH,True))
def macrosToJson():	settings.writeDataToFile(MACRO_FILE_DATA_PATH,Macro.toList(),True)

# Custom event so other addins can create macros
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

add_macro_event_Handler:events.LinkedHandler = None
def createAddMacroCustomEvent():
	global add_macro_event, add_macro_event_Handler
	def AddMacroEventHandler(args:adsk.core.CustomEventArgs):
		Macro.fromJson(args.additionalInfo)

	add_macro_event = utils.CustomEvents.Create(ADD_MACRO_CUSTOM_ID)
	add_macro_event_Handler = events_manager_.add_handler(add_macro_event,AddMacroEventHandler)

def removeAddMacroCustomEvent():
	add_macro_event_Handler.remove()
	utils.CustomEvents.Remove(ADD_MACRO_CUSTOM_ID)


















class ViewOrientations:
	class Direction:
		YAxisUp =  adsk.core.DefaultModelingOrientations.YUpModelingOrientation
		ZAxisUp =  adsk.core.DefaultModelingOrientations.ZUpModelingOrientation
		def GetCurrentOrientation(self): return app_.preferences.generalPreferences.defaultModelingOrientation
		def __init__(self, Yup,Zup):
			self.direction = { self.YAxisUp:Yup, self.ZAxisUp:Zup}
		def __get__(self,instance,owner):
			return adsk.core.Vector3D.create(*self.direction.get(self.GetCurrentOrientation()))
		def __set__(self,instance,value): return False
	
	Top:adsk.core.Vector3D= Direction((0,1,0), (0,0,1))
	Bottom:adsk.core.Vector3D= Direction((0,-1,0), (0,0,-1))
	Left:adsk.core.Vector3D= Direction((-1,0,0), (-1,0,0))
	Right:adsk.core.Vector3D= Direction((1,0,0), (1,0,0))
	Front:adsk.core.Vector3D= Direction((0,0,-1), (0,-1,0))
	Back:adsk.core.Vector3D= Direction((0,0,1), (0,1,0))
	
	OrientationToUp = {
		Top:Front,
		Bottom:Back,
		Left:Top,
		Right:Top,
		Front:Top,
		Back:Top}

def TryViewOrientation(args, orientation=None, localView = True):
	camera = utils.camera.get()
	eyeVector= utils.camera.viewDirection(camera)

	orientation = ViewOrientations.Front
	upDirection = ViewOrientations.OrientationToUp.get(orientation)

	orientation.scaleBy(eyeVector.length)
	newEye = camera.target.copy()
	newEye.translateBy(orientation)

	camera.upVector = upDirection
	camera.eye = newEye

	utils.camera.updateCamera(camera)












#Built in commands for built in macros
	
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def reAssignCamera(cameraCopy:adsk.core.Camera):
	utils.camera.updateCamera(cameraCopy,True)
	ui_.activeSelections.clear()

def getLineDirection(prompt):
	try: line = ui_.selectEntity(prompt,'LinearEdges,SketchLines,ConstructionLines')
	except: return None
	if line: return geometry.lines.getDirection(line.entity)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def alignViewHandler(args: adsk.core.CommandCreatedEventArgs):
	args.command.isRepeatable = False
	args.command.isExecutedWhenPreEmpted = False
	lineDirection = getLineDirection('Please select a line represinting the "up" direction')
	if not lineDirection: return
	camera_copy = utils.camera.get()
	upDirection = camera_copy.upVector.copy()

	orintatedVector = geometry.vectors.project(upDirection,lineDirection,True)

	camera_copy.upVector = orintatedVector
	reAssignCamera(camera_copy)


def changeViewAxis(args: adsk.core.CommandCreatedEventArgs):
	args.command.isRepeatable = False
	args.command.isExecutedWhenPreEmpted = False
	lineDirection = getLineDirection('Please select a line represinting the "forwards" direction')
	if not lineDirection: return
	camera_copy = utils.camera.get()
	cameraDirection = utils.camera.viewDirection(camera_copy)

	if cameraDirection.isPerpendicularTo(lineDirection):#Prevents perpendicular angles from failing
		orintatedVector = geometry.vectors.normalOf(lineDirection)
		if camera_copy.upVector.isParallelTo(lineDirection):
			camera_copy.upVector = geometry.vectors.normalOf(cameraDirection)
	else: orintatedVector = geometry.vectors.project(cameraDirection,lineDirection,True)
	orintatedVector.scaleBy(cameraDirection.length)

	newEye = camera_copy.target.asVector()
	newEye.subtract(orintatedVector)
	camera_copy.eye = newEye.asPoint()
	reAssignCamera(camera_copy)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createBuiltInCommands():
	inspectPanel = ui_.allToolbarPanels.itemById('ToolsInspectPanel')

	AlignView= CommandRef(inspectPanel.controls,
			'zxynine_anymacro_BuiltinAlignView',
			'Change Cameras Up',
			'./resources/noicon','')
	events_manager_.add_handler(AlignView.definition.commandCreated, alignViewHandler)

	ChangeView= CommandRef(inspectPanel.controls,
			'zxynine_anymacro_BuiltinChangeView',
			'Change Cameras Forwards',
			'./resources/noicon','')
	events_manager_.add_handler(ChangeView.definition.commandCreated, changeViewAxis)
	
	# ChangeView= CommandRef(inspectPanel.controls,
	# 		'zxynine_anymacro_BuiltinChangeViewOrientation',
	# 		'Change Cameras View Orientation',
	# 		'./resources/save','')
	# events_manager_.add_handler(ChangeView.definition.commandCreated, TryViewOrientation)


def removeBuiltInCommands():
	inspectPanel = ui_.allToolbarPanels.itemById('ToolsInspectPanel')
	getDelete(inspectPanel.controls,'zxynine_anymacro_BuiltinAlignView')
	getDelete(inspectPanel.controls,'zxynine_anymacro_BuiltinChangeView')
	# getDelete(inspectPanel.controls,'zxynine_anymacro_BuiltinChangeViewOrientation')
	# getDelete(ui_.commandDefinitions,'zxynine_anymacro_BuiltinChangeViewOrientation')
	getDelete(ui_.commandDefinitions,'zxynine_anymacro_BuiltinAlignView')
	getDelete(ui_.commandDefinitions,'zxynine_anymacro_BuiltinChangeView')