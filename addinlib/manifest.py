# Manifest reader.
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
import pathlib

# Avoid Fusion namespace pollution
from . import utils

def read(directory=None):
	directoryPath = directory or pathlib.Path(utils.get_caller_path()).parent
	manifest_path = next(pathlib.Path(directoryPath).glob('*.manifest'))
	with open(manifest_path, encoding='utf-8') as file:	return json.load(file)

def getVersion(directory=None):
	directoryPath = directory or pathlib.Path(utils.get_caller_path()).parent
	return str(read(directoryPath)['version'])