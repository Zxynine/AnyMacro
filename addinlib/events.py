# Event managing.
# 
# Allows catching events with functions instead of classes.
# Tracks registered events and allows clean-up with one function call.
# All event callbacks are also wrapped in an error.ErrorCatcher().
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
import sys, time
import threading
from typing import List
# Avoid Fusion namespace pollution
from . import error, utils, AppObjects






#Data Containers
class LinkedHandler:
	def __init__(self, event: adsk.core.CommandEvent, handler:type,callback:callable=None):
		self.event = event
		self.handler = handler
		self.callback = callback
		if not event.add(handler): raise Exception(f'Failed to add the "{callback.__name__}" handler ')
	def remove(self):
		with utils.Ignore(): self.event.remove(self.handler)



# Try to resolve base class automatically
AUTO_HANDLER_CLASS = None

class EventsManager:
	def __init__(self, error_catcher=None):
		#Declared in init to allow multiple commands to use a single lib
		self.handlers: List[LinkedHandler] = []
		self.custom_event_names = []
		self.app, self.ui = AppObjects.GetAppUI()

		self.next_delay_id = 0
		self.delayed_funcs = {}
		self.delayed_event = None
		self.delayed_event_id = f'{utils.get_caller_path()}_delay_event'
		self.error_catcher = error_catcher or error.ErrorCatcher()
	
	#Assigning
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def add_handler(self, event:adsk.core.CommandEvent, callback=None, base_class=AUTO_HANDLER_CLASS):
		"""`AUTO_HANDLER_CLASS` results in:
		  1: Getting the classType
		  2: Adding 'Handler' to the end and Splitting at '::'
		  3: Getting the module using the first segment
		  4: sets baseClass to the return of getattr using the base and all subsequent segments"""
		if base_class == AUTO_HANDLER_CLASS:
			handler_class_parts = f'{event.classType()}Handler'.split('::')
			base_class = sys.modules[handler_class_parts.pop(0)]
			for cls in handler_class_parts: base_class = getattr(base_class, cls)

		handler_name = f'{base_class.__name__}_{callback.__name__}'
		handler_class = type(handler_name, (base_class,), {"notify": self.error_catcher(callback,True)})
		handler_class.__init__ = lambda self: super(handler_class, self).__init__()
		handler = handler_class()

		handler_info = LinkedHandler(event, handler,callback)
		self.handlers.append(handler_info)# Avoid garbage collection
		return handler_info
	
	def register_event(self, name):
		# Clears and then starts the event (makes sure there is not an old event registered due to a bad stop)
		self.app.unregisterCustomEvent(name)
		event = self.app.registerCustomEvent(name)
		if event: self.custom_event_names.append(name)
		return event

	def find_handler_by_event(self, findevent:adsk.core.Event):
		eventName = findevent.name
		for linkedHandler in self.handlers:
			if eventName == linkedHandler.event.name: 
				return linkedHandler

	#Timing
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def delay(self, func, secs=0):
		'''Puts a function at the end of the event queue, and optionally delays it. '''
		if self.delayed_event is None:# Register the event. Will be removed when user runs clean_up()
			self.delayed_event = self.register_event(self.delayed_event_id)
			self.add_handler(self.delayed_event, callback=self._delayed_event_handler)
		delay_id = self.next_delay_id
		self.next_delay_id += 1

		def waiter():
			time.sleep(secs)
			self.app.fireCustomEvent(self.delayed_event_id, str(delay_id))
		self.delayed_funcs[delay_id] = func

		if secs > 0:
			thread = threading.Thread(target=waiter)
			thread.isDaemon = True
			thread.start()
		else: self.app.fireCustomEvent(self.delayed_event_id, str(delay_id))    

	def _delayed_event_handler(self, args: adsk.core.CustomEventArgs):
		delay_id = int(args.additionalInfo)
		self.delayed_funcs.pop(delay_id, None)()


	#Removing
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def remove_handler(self, *handler_infos: LinkedHandler):
		for handler_info in handler_infos:
			handler_info.remove()
			self.handlers.remove(handler_info)

	def remove_handler_by_event(self, event: adsk.core.CommandEvent):
		handler = self.find_handler_by_event(event)
		self.remove_handler((handler, event))

	def remove_all_handlers(self):
		for linkedHandler in self.handlers: linkedHandler.remove()
		self.handlers.clear()

	def unregister_all_events(self):
		map(self.app.unregisterCustomEvent, self.custom_event_names)
		self.custom_event_names.clear()

	def clean_up(self, oldControl = None):
		"""`oldControl` is an optional variable that, if/when provided, the function: \\
		`utils.clear_ui_items(oldControl)`  is called, which attempts to remove the control after cleanup"""
		self.remove_all_handlers()
		self.unregister_all_events()
		if oldControl is not None: utils.clear_ui_items(oldControl)



