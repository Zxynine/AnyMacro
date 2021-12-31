# Timeline querying and manipulation.
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
from enum import IntEnum
from . import AppObjects

class TimelineStatus(IntEnum):
	OK = 0
	PRODUCT_NOT_READY = 1
	NOT_PARAMETRIC = 2

class OccurrenceType(IntEnum):
	NOT_OCCURRENCE = -1
	UNKNOWN_COMP = 0
	NEW_COMP = 1
	COPY_COMP = 2
	SHEET_METAL = 3
	BODIES_COMP = 4

def get_timeline():
	app:adsk.core.Application = adsk.core.Application.get()

	# activeProduct throws if start-up is not completed
	if not app.isStartupComplete: # Backup solution: app.documents.count == 0:
		return (TimelineStatus.PRODUCT_NOT_READY, None)

	product:adsk.fusion.Design = app.activeProduct
	if not product or product.classType() != adsk.fusion.Design.classType():
		return (TimelineStatus.PRODUCT_NOT_READY, None)

	if product.designType != adsk.fusion.DesignTypes.ParametricDesignType:
		return (TimelineStatus.NOT_PARAMETRIC, None)
		
	return (TimelineStatus.OK, product.timeline)
		

def flatten_timeline(timeline_collection):
	'''
	A flat timeline representation, with all objects except any group objects.
	(Groups disappear when expanded - The icon is no longer there in the timeline.)
	'''
	flat_collection = []
	def MapFunc(obj:adsk.fusion.TimelineObject):
		if not obj.isGroup: flat_collection.append(obj)
			# Groups only appear in the timeline if they are collapsed
			# In that case, the features inside the group are only listed within the group
			# and not as part of the top-level timeline. So timeline essentially gives us
			# what is literally shown in the timeline control in Fusion.

			# Flatten the group
		else: flat_collection.extend(flatten_timeline(obj))
	map(MapFunc, timeline_collection)
	return flat_collection

def get_occurrence_type(timeline_obj:adsk.fusion.TimelineObject):
	'''Heuristics to determine component creation feature'''
	
	if timeline_obj.entity.classType() != adsk.fusion.Occurrence.classType():
		return OccurrenceType.NOT_OCCURRENCE

	# When prefixed with a "type prefix", we can be sure of the occurence type.
	# In that case, the name of the timeline object cannot be edited.
	# This, of course, assumes that the user does not create a component starting
	# with such a string.
	potential_type_prefix = timeline_obj.name.split(' ', maxsplit=1)[0]
	# User can have input spaces, so a length of split_name > 1 does not automatically
	# mean that we have a type prefix. So let's try.
	# TODO: We can probably compare with the component name to find out if this is
	#       indeed a prefix.
	if potential_type_prefix == '':
		return OccurrenceType.NEW_COMP
		# I have not found any way to determine if a component is a sheet metal component.
		# Solid features are allowed in sheet metal components and sheet metal features are
		# allowed in "normal" components, so cannot use the content as a differentiator.
		#return OCCURRENCE_SHEET_METAL
	if potential_type_prefix == 'CopyPaste':
		return OccurrenceType.COPY_COMP

	if hasattr(timeline_obj.entity, 'bRepBodies'):
		return OccurrenceType.BODIES_COMP

	return OccurrenceType.UNKNOWN_COMP


class GroupManager:
	"""A context manager that lets you easily group timeline actions. Just use "with Groupmanager('GroupName'):" before any actions"""
	def __init__(self, groupName, timeline:adsk.fusion.Timeline = None):
		self.isParametric = AppObjects.is_parametric_mode()
		if not self.isParametric: return
		self.timeline = timeline or AppObjects.GetDesign().timeline
		self.groupName = str(groupName)
	def __enter__(self):
		if not self.isParametric: return
		self.startIndex = self.timeline.markerPosition
		return self.timeline
	def __exit__(self, ExType, ExVal, ExTrace):
		if not (self.isParametric and ExType is None): return False
		timelineObj = self.timeline.timelineGroups.add(int(self.startIndex), int(self.timeline.markerPosition)-1)
		timelineObj.name = self.groupName