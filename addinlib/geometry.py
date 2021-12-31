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

finiteGometry = (adsk.fusion.BRepEdge, adsk.fusion.SketchLine)
infiniteGeometry = (adsk.fusion.ConstructionAxis,)


class lines:
	def getEndpoints(line):
		if isinstance(line, adsk.fusion.BRepEdge):
			start,end = line.startVertex.geometry, line.endVertex.geometry
		elif isinstance(line, adsk.fusion.SketchLine):
			start,end = line.startSketchPoint.geometry, line.endSketchPoint.geometry
		elif isinstance(line, adsk.fusion.ConstructionAxis):
			start = line.geometry.origin
			end = start.copy(); end.translateBy(line.geometry.direction)
		return start,end

	def getDirection(line):
		if isinstance(line, (*finiteGometry, *infiniteGeometry)):
			start,end = lines.getEndpoints(line)
			return start.vectorTo(end)
		else: raise TypeError('Incorrect line Type.')

class vectors:
	def project(fromVec:adsk.core.Vector3D,toVec:adsk.core.Vector3D, normalised=False):
		projection = toVec.copy()
		projection.scaleBy(fromVec.dotProduct(toVec) / fromVec.length**2)
		if normalised: projection.normalize()
		return projection 

	def normalOf(unNormVec:adsk.core.Vector3D,scale=1):
		newVec = unNormVec.copy()
		newVec.normalize()
		newVec.scaleBy(scale)
		return newVec
