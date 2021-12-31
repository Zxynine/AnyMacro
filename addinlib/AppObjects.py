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





def GetAppUI(): return GetApp(),GetUi()
def GetApp(): return adsk.core.Application.cast(adsk.core.Application.get())
def GetUi(): return GetApp().userInterface



def GetDesign()->adsk.fusion.Design: return adsk.fusion.Design.cast(GetApp().activeProduct)

def is_parametric_mode():
	# Checking workspace type in DocumentActivated handler fails since Fusion 360 v2.0.10032
	# UserInterface.ActiveWorkspace throws when it is called from DocumentActivatedHandler
	# during Fusion 360 start-up(?). Checking for app_.isStartupComplete does not help.
	try:
		if GetUi().activeWorkspace.id == 'FusionSolidEnvironment':
			design = GetDesign()
			return bool(design and design.designType == adsk.fusion.DesignTypes.ParametricDesignType)
	except: return False


# class Application(adsk.core.Application):
# 	def __init__(self): self.__dict__ = GetApp().__dict__
# 	@property
# 	def design(self)->adsk.fusion.Design:
# 		return self.activeDocument.products.itemByProductType('DesignProductType')
# 	@property
# 	def cam(self)->adsk.cam.CAM:
# 		return self.activeDocument.products.itemByProductType('CAMProductType')