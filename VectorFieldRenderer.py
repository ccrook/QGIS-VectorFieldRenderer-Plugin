#
# Render a vector point layer using arrows to represent the a vector 
# quantity.
# 

import math
import inspect
from os import path
from qgis.core import *
from qgis import utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from VectorArrowMarker import VectorArrowMarker

class VectorFieldRenderer(QgsFeatureRendererV2):

    scaleGroups={}

    rendererName = "VectorFieldRenderer"
    iface = None
    plugin = None

    Cartesian = 0
    Polar = 1
    Height = 2

    def __init__(self):
        QgsFeatureRendererV2.__init__(self,VectorFieldRenderer.rendererName)

        # Attributes of the renderer 

        self._degrees = True
        self._mode = VectorFieldRenderer.Cartesian
        self._angleFromNorth = True
        self._scale = 1.0
        self._xfieldname = ""
        self._yfieldname = ""
        self._useMapUnit = False
        self._xfieldno = -1
        self._yfieldno = -1
        self._legendText = ''
        self._showInScaleBox = True
        self._scaleBoxText = ''
        self._scaleGroup = ''
        self._scaleGroupFactor = 1.0

        # Field used in processing ..

        self._xfieldno = -1
        self._yfieldno = -1
        self._isvalid = True

        # Fields used to generate statistics for autoscaling

        self._nFeatures = 0
        self._maxLength = 0.0
        self._sumLength = 0.0
        self._sumLength2 = 0.0
        self._vectorscale = 1.0
        self._pixelScaleFactor = 1.0
        self._vectorUnitsPerPixel = 1.0
        self._mapUnitsPerPixel = 1.0

        self._renderingStarted = False;
        self._rendering = False;
        
        # Preferred code, but currently existing symbol layers not 
        # defined in SIP..  However I do get a simple marker by
        # default in the QgsMarkSymbolV2 default constructor.. though
        # I can't access its borderColor..
        # Could make this part of the arrow as an alternative...

        # black = QColor(0,0,0)
        # base = QgsSimpleMarkerSymbolLayerV2( "circle", black, black, 5.0, 0.0 )
        #        QgsSimpleMarkerSymbolLayerV2
        # arrow = VectorArrowMarker()
        # symbol = QgsMarkerSymbolV2( base, arrow )

        arrow = VectorArrowMarker()
        symbol = QgsMarkerSymbolV2()
        symbol.setOutputUnit(QgsSymbolV2.MM)
        self._symbol = symbol
        self.setupArrowMarker(None)

    # Accessor functions - get and set members

    def degrees(self):
        return self._degrees
    def setDegrees(self,degrees):
        self._degrees = degrees

    def mode(self):
        return self._mode
    def setMode(self,mode):
        self._mode = mode

    def angleFromNorth(self):
        return self._angleFromNorth
    def setAngleFromNorth(self,angleFromNorth):
        self._angleFromNorth = angleFromNorth

    def scale(self):
        return self._scale
    def setScale(self,scale):
        self._scale = scale
        self.setGroupScale()

    def useMapUnit(self):
        return self._useMapUnit
    def setUseMapUnit(self,usemapunit):
        self._useMapUnit = usemapunit
        self.setGroupScale()

    def xFieldName(self):
        return self._xfieldname
    def setXFieldName(self,xfieldname):
        self._xfieldname = xfieldname

    def yFieldName(self):
        return self._yfieldname
    def setYFieldName(self,yfieldname):
        self._yfieldname = yfieldname

    def setFields( self, xfieldname, yfieldname ):
        self._xfieldname = xfieldname
        self._yfieldname = yfieldname

    def legendText(self):
        return self._legendText
    def setLegendText(self,legendText ):
        self._legendText = legendText  

    def showInScaleBox(self):
        return self._showInScaleBox
    def setShowInScaleBox(self,showInScaleBox):
        self._showInScaleBox = showInScaleBox

    def scaleBoxText(self):
        return self._scaleBoxText
    def setScaleBoxText(self,scaleBoxText):
        self._scaleBoxText=scaleBoxText

    def scaleGroup(self):
        return self._scaleGroup
    def setScaleGroup(self,scaleGroup):
        self._scaleGroup = scaleGroup
        self.setGroupScale()

    def scaleGroupFactor(self):
        return self._scaleGroupFactor
    def setScaleGroupFactor(self,scaleGroupFactor):
        self._scaleGroupFactor = scaleGroupFactor
        self.setGroupScale()

    def outputUnit(self):
        return self._symbol.outputUnit()
    def setOutputUnit(self,unit):
        self._symbol.setOutputUnit(unit)

    def arrow(self):
        return self._symbol.symbolLayer(0)

    def setupArrowMarker(self,arrow):
        arrow = arrow or VectorArrowMarker()
        while self._symbol.symbolLayerCount():
            self._symbol.deleteSymbolLayer(0)
        self._symbol.appendSymbolLayer(arrow)

    def setGroupScale(self):
        groups = VectorFieldRenderer.scaleGroups
        if self._scaleGroup and self._scaleGroupFactor > 0:
            groupScale = self._scale/self._scaleGroupFactor 
            groups[self._scaleGroup] = [groupScale,self.useMapUnit]

    def getGroupScale(self):
        newScale = False
        groups = VectorFieldRenderer.scaleGroups
        if self._scaleGroup in groups and self._scaleGroupFactor > 0:
          scale, umu = groups[self._scaleGroup]
          scale *= self._scaleGroupFactor
          if scale != self._scale or umu != self._useMapUnit:
               self._scale = scale
               self._useMapUnit = umu
               newScale = True
        return newScale

    def clone(self):
        clone = VectorFieldRenderer()
        clone.setDegrees(self.degrees())
        clone.setMode(self.mode())
        clone.setAngleFromNorth(self.angleFromNorth())
        clone.setScale(self.scale())
        clone.setUseMapUnit(self.useMapUnit())
        clone.setXFieldName(self.xFieldName())
        clone.setYFieldName(self.yFieldName())
        clone.setScaleGroup(self.scaleGroup())
        clone.setScaleGroupFactor(self.scaleGroupFactor())
        clone.setLegendText(self.legendText())
        clone.setScaleBoxText(self.scaleBoxText())
        clone.setShowInScaleBox(self.showInScaleBox())
        clone._symbol = self._symbol.clone()
        return clone

    def usedAttributes(self):
        if self._mode == VectorFieldRenderer.Height:
            return [self._xfieldname]
        return [self._xfieldname, self._yfieldname]

    def symbols(self):
        return [self._symbol]

    def save(self, doc):
        re = doc.createElement("renderer-v2")
        re.setAttribute("type",VectorFieldRenderer.rendererName)
        re.setAttribute("degrees",str(self._degrees))
        re.setAttribute("mode",str(self._mode))
        re.setAttribute("angleFromNorth",str(self._angleFromNorth))
        re.setAttribute("scale",str(self._scale))
        re.setAttribute("usemapunit",str(self._useMapUnit))
        re.setAttribute("xfieldname",self._xfieldname)
        re.setAttribute("yfieldname",self._yfieldname)
        re.setAttribute("scalegroup",self._scaleGroup)
        re.setAttribute("scalegroupfactor",str(self._scaleGroupFactor))
        re.setAttribute("legendtext",self._legendText)
        re.setAttribute("scaleboxtext",self._scaleBoxText)
        re.setAttribute("showonscalebox",str(self._showInScaleBox))
        re.setAttribute("outputunit", "MapUnit" 
            if self._symbol.outputUnit() == QgsSymbolV2.MapUnit 
            else "MM" )
        arrow = self.arrow()
        re.setAttribute("baseColor",arrow.baseColor().name())
        re.setAttribute("baseBorderColor",arrow.baseBorderColor().name())
        re.setAttribute("baseSize",str(arrow.baseSize()))
        re.setAttribute("arrowColor",arrow.color().name())
        re.setAttribute("arrowWidth",str(arrow.width()))
        re.setAttribute("arrowHeadSize",str(arrow.headSize()))
        re.setAttribute("arrowMaxHeadSize",str(arrow.maxHeadSize()))
        if( VectorFieldRenderer.plugin ):
            re.appendChild(VectorFieldRenderer.plugin.save(doc))
        return re
        # TODO: as far as I can tell the tag name renderer-v2 is not
        # defined in the Python interface (RENDERER_TAG_NAME in C++),
        # so manually coded
        # TODO: using QColor.name() here .. would be perhaps better to
        # use QGIS convention, which appears to be comma separated 
        # RGB values?  Ideally will find a utility function for this
        # TODO: Use utility function for saving symbol definition

    def reload(self, element):
        try:
           self._scaleGroup = ""
           self.setMode( int(element.attribute("mode")) )
           self.setDegrees( element.attribute("degrees") == "True" )
           self.setAngleFromNorth( element.attribute("angleFromNorth") == "True" )
           self.setScale( float( element.attribute("scale")))
           self.setUseMapUnit( element.attribute("usemapunit") == "True" )
           self.setXFieldName( element.attribute("xfieldname"))
           self.setYFieldName( element.attribute("yfieldname"))

           self._symbol.setOutputUnit( QgsSymbolV2.MapUnit
                if element.attribute("outputunit") == "MapUnit" 
                else QgsSymbolV2.MM )

           arrow = self.arrow()
           color = QColor()
           color.setNamedColor( element.attribute("baseColor"))
           arrow.setBaseColor( color )
           color = QColor()
           color.setNamedColor( element.attribute("baseBorderColor"))
           arrow.setBaseBorderColor( color )
           arrow.setBaseSize( float( element.attribute("baseSize")))

           color = QColor()
           color.setNamedColor( element.attribute("arrowColor"))
           arrow.setColor( color )
           arrow.setWidth( float( element.attribute("arrowWidth")))
           arrow.setHeadSize( float( element.attribute("arrowHeadSize")))
           arrow.setMaxHeadSize( float( element.attribute("arrowMaxHeadSize")))

           # Placed at end as not present in old project files
           self.setScaleGroup(element.attribute("scalegroup"))
           self.setScaleGroupFactor(float(element.attribute("scalegroupfactor")))
           self.setLegendText(element.attribute("legendtext"))
           self.setScaleBoxText(element.attribute("scaleboxtext"))
           self.setShowInScaleBox( element.attribute("showonscalebox") == "True" )
        except:
           pass

    # startRender - looks up the field numbers in the layer for the
    # fields used to generate the arrow

    def setMapRenderingStarting(self):
        self._renderingStarted = True
        self._rendering = True

    def setMapRenderingFinished(self):
        self._renderingStarted = False
        self._rendering = False

    def startRender(self, context, layer):

        self.getGroupScale()
        self._xfieldno = -1
        self._yfieldno = -1
        self._isvalid = True

        if self._renderingStarted:
            self._nFeatures = 0
            self._maxLength = 0
            self._sumLength = 0
            self._sumLength2 = 0
            self._renderingStarted = False

        try:
          if layer: 
             self._xfieldno = layer.fieldNameIndex(self._xfieldname)
             if self._xfieldno == -1:
                self._isvalid = False
             if self._mode != VectorFieldRenderer.Height:
                 self._yfieldno = layer.fieldNameIndex(self._yfieldname)
                 if self._xfieldno == -1:
                    self._isvalid = False
        except:
          self._isvalid = False 

        # Scale factors
        # _vectorscale        is factor to multiply vector when calling arrow symbol
        # _pixelScaleFactor   is the pixel scale factor for plotting the symbol
        # _vectorpixelscale   is the vector to pixel conversion
        # _scaleConversion    is relationship between the scale and a map units scale

        self._vectorscale = self._scale 
        self._pixelScaleFactor = self.pixelSizeScaleFactor(context,self.outputUnit())
        self._vectorUnitsPerPixel = 1.0/self._pixelScaleFactor
        self._mapUnitsPerPixel = context.mapToPixel().mapUnitsPerPixel()

        if self.useMapUnit() and self.outputUnit() != QgsSymbolV2.MapUnit:
            self._vectorUnitsPerPixel = 1.0/self.pixelSizeScaleFactor(context,QgsSymbolV2.MapUnit)
            self._vectorscale = self._scale/(self._vectorUnitsPerPixel*self._pixelScaleFactor)

        self._symbol.startRender(context)

    def stopRender(self,context):
        self._symbol.stopRender(context)

    # Calculate symbol output scale factor, as needed for plotting 
    # scale bar.  Copied from code in qgssymbollayerv2utils.cpp. 

    def pixelSizeScaleFactor(self,context,outputUnit):
        if outputUnit == QgsSymbolV2.MM:
            return context.scaleFactor()*context.rasterScaleFactor()
        mup = context.mapToPixel().mapUnitsPerPixel()
        if mup > 0:
            return context.rasterScaleFactor()/mup
        return

    # prepares the symbol to plot a feature (calculates arrow
    # size and direction) and returns the symbol

    def symbolForFeature( self, feature ):
        am = feature.attributeMap()
        r = 0.0
        a = 0.0
        if self._isvalid:
          try:
             x = am[self._xfieldno].toDouble()[0]
             if self._mode == VectorFieldRenderer.Height:
                 r = x
                 a = math.pi/2.0
                 if r < 0.0:
                     r = -r
                     a = -a
             else:
                 y = am[self._yfieldno].toDouble()[0]
                 if self._mode == VectorFieldRenderer.Polar:
                     r = x
                     a = y
                     if self._degrees:
                         a = a * math.pi/180.0
                     if self._angleFromNorth:
                         a = math.pi/2.0 - a
                 else:
                     r = math.sqrt(x*x+y*y)
                     if r > 0.0:
                         a = math.atan2(y,x)
          except:
             r = 0.0
             a = 0.0

        self.arrow().setVector( r * self._vectorscale, a )

        if self._rendering:
            self._nFeatures += 1
            self._sumLength += r
            self._sumLength2 += r*r
            self._maxLength = max(self._maxLength,r)

        return self._symbol

    def stats(self):
        mean = 0.0
        self.setGroupScale()
        rms = 0.0
        if self._nFeatures > 0:
           mean = self._sumLength/self._nFeatures
           rms = math.sqrt(self._sumLength2/self._nFeatures)
        return { 
           'count': self._nFeatures,
           'mean': mean,
           'rms': rms,
           'max': self._maxLength
            }

    def renderedCount(self):
        return self._nFeatures;

    def autoRescale(self, mapextent):
        if self._nFeatures == 0:
            return False

        # Compute a representative arrow length trying to ignore
        # outliers

        arrlen = math.sqrt(self._sumLength2/self._nFeatures)
        arrlen = min(arrlen*2,self._maxLength)
        if arrlen <= 0.0:
            return False

        # Compute the desired length on the map

        mapsize = math.sqrt(mapextent.width()*mapextent.height())
        maplen = mapsize / math.sqrt(16.0+self._nFeatures)
        maplen = max(min(maplen,mapsize/10),mapsize/100)
        
        # Set the scale - the scale conversion is required if not
        # using map units for rendering the arrow, as we have 
        # calculated the scale in map units

        scale = (maplen*self._vectorUnitsPerPixel)/(arrlen*self._mapUnitsPerPixel)
        if self.scale() == scale:
            return False 

        self.setScale(scale)
        return True

    # Functions used by the scale box - assume that the layers have
    # been rendered, so scale information is available.
    #
    # Get the length of the arrow - not including head, base, etc.
    def arrowPixelLength(self,veclen):
        return veclen * self._vectorscale * self._pixelScaleFactor

    # Get the actual plot size of the arrow
    def arrowSize(self,veclen):
        arrow = self.arrow()
        arrow.setVector(veclen*self._vectorscale,0.0)
        return arrow.arrowSize(self._pixelScaleFactor)

    def renderScaleBoxSymbol(self,veclen,point,painter):
        arrow = self.arrow()
        arrow.setVector(veclen*self._vectorscale,0.0)
        arrow.renderArrow(point,painter,self._pixelScaleFactor)

    def legendSymbologyItems( self, size ):
        icon = self.arrow().legendIcon(size)
        return [[self._legendText,icon]]

    # Display the help information for this renderer
    @staticmethod
    def showHelp():
        iface = VectorFieldRenderer.iface
        if iface:
            file = inspect.getsourcefile(VectorFieldRenderer) 
            file = 'file://' + path.join(path.dirname(file),'index.html')
            file = file.replace("\\","/")
            iface.openURL(file,False)      

