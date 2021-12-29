# Persistent settings.
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

import json
import os

# Avoid Fusion namespace pollution
from . import utils

class SettingsManager:
	def __init__(self, default_values, writeOnValueSet=True, fileNamedPath='settings.json'):
		self.default_values = default_values
		self.writeOnValueSet = writeOnValueSet
		self.settings = None

		caller_dir = os.path.dirname(utils.get_caller_path())
		self.file_path = os.path.join(caller_dir, fileNamedPath)
		self.read()

	def __getitem__(self, key):
		return self.settings[key]

	def __setitem__(self, key, value):
		self.settings[key] = value
		if self.writeOnValueSet: self.write()

	def write(self):
		with open(self.file_path, 'w+', encoding='utf-8') as f:
			json.dump(self.settings, f, indent=2)

	def read(self):
		if not os.path.exists(self.file_path): return
		with open(self.file_path, 'r', encoding='utf-8') as f:
			self.settings = json.load(f)


def writeDataToFile(customPathFile, data, isJson = False):
	with open(customPathFile, 'w', encoding='utf-8') as f: 
		json.dump(data, f, indent=2) if isJson else f.write(data)

def readDataFromFile(customPathFile, isJson = False):
	if not os.path.exists(customPathFile):return None
	with open(customPathFile, 'r', encoding='utf-8') as f:
		return json.load(f) if isJson else f.read()




# class SettingsManager:
#     def __init__(self, default_values, write_through=True, filename='settings.json'):
#         self.default_values = default_values
#         self.write_through = write_through
#         self.settings = None

#         caller_file = utils.get_caller_path()
#         caller_dir = os.path.dirname(caller_file)
#         self.file_path = os.path.join(caller_dir, filename)

#         self._read()

#     def __getitem__(self, key):
#         return self.settings[key]

#     def __setitem__(self, key, value):
#         self.settings[key] = value
#         if self.write_through:
#             self.write()

#     def write(self):
#         with open(self.file_path, 'w+', encoding='utf-8') as f:
#             json.dump(self.settings, f)

#     def _read(self):
#         try:
#             with open(self.file_path, 'r', encoding='utf-8') as f:
#                 self.settings = json.load(f)
#         except FileNotFoundError:
#             self.settings = self.default_values
#             self.write()
