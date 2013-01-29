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
    NoArrow = 3

    NArrowFields={Cartesian:2,Polar:2,Height:1,NoArrow:0}

    NoEllipse = 0
    CovarianceEllipse = 1
    AxesEllipse = 2
    CircularEllipse = 3
    HeightEllipse = 4
    
    NEllipseFields={NoEllipse:0,CovarianceEllipse:3,AxesEllipse:3,CircularEllipse:1,HeightEllipse:1}

    EllipseField0=2
    NFields=5

    XField=0
    YField=1
    RField=0
    AngleField=1
    HeightField=0
    CxxField=2
    CxyField=3
    CyyField=4
    EmaxField=2
    EminField=3
    EAngleField=4
    ERadiusField=2
    EHeightField=2

    def __init__(self):
        QgsFeatureRendererV2.__init__(self,VectorFieldRenderer.rendererName)

        # Attributes of the renderer 

        self._degrees = True
        self._mode = VectorFieldRenderer.Cartesian
        self._angleFromNorth = True
        self._scale = 1.0
        self._fieldname=[""]*self.NFields
        self._useMapUnit = False
        self._xfieldno = -1
        self._yfieldno = -1
        self._legendText = ''
        self._showInScaleBox = True
        self._scaleBoxText = ''
        self._scaleGroup = ''
        self._scaleGroupFactor = 1.0
        self._ellipseMode = VectorFieldRenderer.NoEllipse
        self._ellipseAngleFromNorth = True
        self._ellipseDegrees = True
        self._ellipseScale = 1.0

        # Field used in processing ..

        self._fieldno=[-1]*self.NFields
        self._usedfield = [False]*self.NFields
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

    def mode(self):
        return self._mode
    def setMode(self,mode):
        self._mode = mode

    def ellipseMode(self):
        return self._ellipseMode
    def setEllipseMode(self,mode):
        self._ellipseMode = mode

    def degrees(self):
        return self._degrees
    def setDegrees(self,degrees):
        self._degrees = degrees

    def angleFromNorth(self):
        return self._angleFromNorth
    def setAngleFromNorth(self,angleFromNorth):
        self._angleFromNorth = angleFromNorth

    def ellipseDegrees(self):
        return self._ellipseDegrees
    def setEllipseDegrees(self,degrees):
        self._ellipseDegrees = degrees

    def ellipseAngleFromNorth(self):
        return self._ellipseAngleFromNorth
    def setEllipseAngleFromNorth(self,angleFromNorth):
        self._ellipseAngleFromNorth = angleFromNorth

    def scale(self):
        return self._scale
    def setScale(self,scale):
        self._scale = scale
        self.setGroupScale()

    def ellipseScale(self):
        return self._ellipseScale
    def setEllipseScale(self,scale):
        self._ellipseScale = scale
        self.setGroupScale()

    def useMapUnit(self):
        return self._useMapUnit
    def setUseMapUnit(self,usemapunit):
        self._useMapUnit = usemapunit
        self.setGroupScale()

    def xFieldName(self):
        return self._fieldname[self.XField]
    def setXFieldName(self,xfieldname):
        self._fieldname[self.XField] = xfieldname

    def yFieldName(self):
        return self._fieldname[self.YField]
    def setYFieldName(self,yfieldname):
        self._fieldname[self.YField] = yfieldname

    def cxxFieldName(self):
        return self._fieldname[self.CxxField]
    def setCxxFieldName(self,cxxfieldname):
        self._fieldname[self.CxxField] = cxxfieldname

    def cxyFieldName(self):
        return self._fieldname[self.CxyField]
    def setCxyFieldName(self,cxyfieldname):
        self._fieldname[self.CxyField] = cxyfieldname

    def cyyFieldName(self):
        return self._fieldname[self.CyyField]
    def setCyyFieldName(self,cyyfieldname):
        self._fieldname[self.CyyField] = cyyfieldname

    def setFields( self, xfieldname, yfieldname ):
        self._fieldname[self.XField] = xfieldname
        self._fieldname[self.YField] = yfieldname

    def setEllipseFields( self, cxxfieldname, cxyfieldname="", cyyfieldname="" ):
        self._fieldname[self.CxxField] = cxxfieldname
        self._fieldname[self.CxyField] = cxyfieldname
        self._fieldname[self.CyyField] = cyyfieldname

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
        clone.setEllipseMode(self.ellipseMode())
        clone.setEllipseDegrees(self.ellipseDegrees())
        clone.setEllipseAngleFromNorth(self.ellipseAngleFromNorth())
        clone.setEllipseScale(self.ellipseScale())
        clone.setUseMapUnit(self.useMapUnit())
        clone.setXFieldName(self.xFieldName())
        clone.setYFieldName(self.yFieldName())
        clone.setCxxFieldName(self.cxxFieldName())
        clone.setCxyFieldName(self.cxyFieldName())
        clone.setCyyFieldName(self.cyyFieldName())
        clone.setScaleGroup(self.scaleGroup())
        clone.setScaleGroupFactor(self.scaleGroupFactor())
        clone.setLegendText(self.legendText())
        clone.setScaleBoxText(self.scaleBoxText())
        clone.setShowInScaleBox(self.showInScaleBox())
        clone._symbol = self._symbol.clone()
        return clone

    def setUsedFields( self ):
        self._usedfield=[False]*self.NFields
        narrow = self.NArrowFields[self._mode]
        nellipse = self.NEllipseFields[self._ellipseMode]
        for i in range(narrow): self._usedfield[i]=True
        for i in range(nellipse): self._usedfield[i+self.EllipseField0]=True

    def usedAttributes(self):
        self.setUsedFields()
        return [self._fieldname[i] for i in range(self.NFields) if self._usedfield[i]]

    def symbols(self):
        return [self._symbol]

    def save(self, doc):
        re = doc.createElement("renderer-v2")
        re.setAttribute("type",VectorFieldRenderer.rendererName)
        re.setAttribute("degrees",str(self._degrees))
        re.setAttribute("mode",str(self._mode))
        re.setAttribute("angleFromNorth",str(self._angleFromNorth))
        re.setAttribute("scale",str(self._scale))
        re.setAttribute("ellipseDegrees",str(self._ellipseDegrees))
        re.setAttribute("ellipseAngleFromNorth",str(self._ellipseAngleFromNorth))
        re.setAttribute("ellipseScale",str(self._ellipseScale))
        re.setAttribute("ellipseMode",str(self._ellipseMode))
        re.setAttribute("usemapunit",str(self._useMapUnit))
        re.setAttribute("xfieldname",self._fieldname[self.XField])
        re.setAttribute("yfieldname",self._fieldname[self.YField])
        re.setAttribute("cxxfieldname",self._fieldname[self.CxxField])
        re.setAttribute("cxyfieldname",self._fieldname[self.CxyField])
        re.setAttribute("cyyfieldname",self._fieldname[self.CyyField])
        re.setAttribute("scalegroup",self._scaleGroup)
        re.setAttribute("scalegroupfactor",str(self._scaleGroupFactor))
        re.setAttribute("legendtext",self._legendText)
        re.setAttribute("scaleboxtext",self._scaleBoxText)
        re.setAttribute("showonscalebox",str(self._showInScaleBox))
        re.setAttribute("outputunit", "MapUnit" 
            if self._symbol.outputUnit() == QgsSymbolV2.MapUnit 
            else "MM" )

        self.arrow().saveToXmlElement(re)

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
           self.setEllipseAngleFromNorth( element.attribute("ellipseAngleFromNorth","True") == "True" )
           self.setEllipseDegrees( element.attribute("ellipseDegrees","True") == "True" )
           self.setScale( float( element.attribute("scale")))
           self.setEllipseMode( int(element.attribute("ellipseMode","0")) )
           self.setEllipseScale( float( element.attribute("ellipseScale","1.0")))
           self.setUseMapUnit( element.attribute("usemapunit") == "True" )
           self.setXFieldName( element.attribute("xfieldname"))
           self.setYFieldName( element.attribute("yfieldname"))
           self.setCxxFieldName( element.attribute("cxxfieldname",""))
           self.setCxyFieldName( element.attribute("cxyfieldname",""))
           self.setCyyFieldName( element.attribute("cyyfieldname",""))

           self._symbol.setOutputUnit( QgsSymbolV2.MapUnit
                if element.attribute("outputunit") == "MapUnit" 
                else QgsSymbolV2.MM )

           self.arrow().readFromXmlElement(element)

           # Placed at end as not present in old project files
           self.setScaleGroup(element.attribute("scalegroup"))
           self.setScaleGroupFactor(float(element.attribute("scalegroupfactor")))
           self.setLegendText(element.attribute("legendtext"))
           self.setScaleBoxText(element.attribute("scaleboxtext"))
           self.setShowInScaleBox( element.attribute("showonscalebox") == "True" )
        except:
           raise
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
        self._isvalid = True

        if self._renderingStarted:
            self._nFeatures = 0
            self._maxLength = 0
            self._sumLength = 0
            self._sumLength2 = 0
            self._renderingStarted = False

        self._fieldno=[-1]*self.NFields
        try:
          if layer: 
              for i in range(self.NFields):
                  if self._usedfield[i]:
                      self._fieldno[i]=layer.fieldNameIndex(self._fieldname[i])
                      if self._fieldno[i] == -1:
                          self._isvalid=False
        except:
            self._isvalid = False 


        self._pixelScaleFactor,self._vectorscale,self._mapUnitsPerPixel,self._vectorUnitsPerPixel = self.scaleFactors(context)

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

    def scaleFactors(self,context):

        # Scale factors
        # _vectorscale        is factor to multiply vector when calling arrow symbol
        # _pixelScaleFactor   is the pixel scale factor for plotting the symbol
        # _vectorpixelscale   is the vector to pixel conversion

        vectorscale = self._scale 
        pixelScaleFactor = self.pixelSizeScaleFactor(context,self.outputUnit())
        vectorUnitsPerPixel = 1.0/pixelScaleFactor
        mapUnitsPerPixel = context.mapToPixel().mapUnitsPerPixel()

        if self.useMapUnit() and self.outputUnit() != QgsSymbolV2.MapUnit:
            vectorUnitsPerPixel = 1.0/self.pixelSizeScaleFactor(context,QgsSymbolV2.MapUnit)
            vectorscale = self._scale/(vectorUnitsPerPixel*pixelScaleFactor)

        return pixelScaleFactor,vectorscale,mapUnitsPerPixel,vectorUnitsPerPixel,

    # prepares the symbol to plot a feature (calculates arrow
    # size and direction) and returns the symbol

    def calcErrorEllipse( self, cxx, cxy, cyy ):
        v1 =(cxx+cyy)/2.0
        v2 =(cxx-cyy)/2.0
        v3 = cxy
        v4 = math.sqrt(v2*v2+v3*v3)
        if cxx < 0.0 or cyy < 0.0 or v4 > 1.0000001 * v1:
            return 0.0,0.0,0.0,False
        eangle = math.atan2(v3,v2)/2.0 if (v1 > 0.0 and v4 > 0.0001*v1) else 0.0
        emax = math.sqrt(max(v1+v4,0.0))
        emin = math.sqrt(max(v1-v4,0.0))
        return emax, emin, eangle, True

    def symbolForFeature( self, feature ):
        am = feature.attributeMap()
        r = 0.0
        a = 0.0
        emax = 0.0
        emin = 0.0
        eangle= 0.0
        value=[0.0]*self.NFields
        drawEllipse = self._ellipseMode != self.NoEllipse
        if self._isvalid:
          try:
             for i in range(self.NFields):
                 if self._usedfield[i]:
                     value[i] = am[self._fieldno[i]].toDouble()[0]
             if self._mode == self.Cartesian:
                  x=value[self.XField]
                  y=value[self.YField]
                  r = math.sqrt(x*x+y*y)
                  if r > 0.0:
                      a = math.atan2(y,x)
             elif self._mode == self.Polar:
                 r = value[self.RField] 
                 a = value[self.AngleField]
                 if self._degrees:
                    a = a * math.pi/180.0
                 if self._angleFromNorth:
                    a = math.pi/2.0 - a
             elif self._mode == self.Height:
                 r = value[self.HeightField]
                 a = math.pi/2.0
                 if r < 0.0:
                     r = -r
                     a = -a

    
             if self._ellipseMode == self.NoEllipse:
                 pass
             elif self._ellipseMode == self.CovarianceEllipse:
                 emax, emin, eangle, drawEllipse = self.calcErrorEllipse(
                     value[self.CxxField],
                     value[self.CxyField],
                     value[self.CyyField])
                 emax *= self._ellipseScale
                 emin *= self._ellipseScale
             elif self._ellipseMode == self.AxesEllipse:
                 emax = abs(value[self.EmaxField]*self._ellipseScale)
                 emin = abs(value[self.EminField]*self._ellipseScale)
                 eangle = value[self.EAngleField]
                 if self._ellipseDegrees:
                    eangle = eangle * math.pi/180.0
                 if self._ellipseAngleFromNorth:
                    eangle = math.pi/2.0 - eangle
                 if emax < emin:
                    temp=emax
                    emax=emin
                    emin=temp
                    eangle += math.pi/2.0
             elif self._ellipseMode == self.HeightEllipse:
                 emax = abs(value[self.EHeightField]*self._ellipseScale)
                 emin = 0.0
                 eangle = math.pi/2.0
             elif self._ellipseMode == self.CircularEllipse:
                 emax = abs(value[self.ERadiusField]*self._ellipseScale)
                 emin = emax

          except:
             raise
             r = 0.0
             a = 0.0
             emax = 0.0
             emin = 0.0
             eangle= 0.0

        vscale = self._vectorscale
        self.arrow().setVector( r * vscale, a, self._mode != self.NoArrow )
        self.arrow().setEllipse( emax*vscale, emin*vscale, eangle, drawEllipse )

        if self._rendering:
            vlen = r + emax
            self._nFeatures += 1
            self._sumLength += vlen
            self._sumLength2 += vlen*vlen
            self._maxLength = max(self._maxLength,vlen)

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
    def arrowPixelLength(self,veclen,context):
        pixelScaleFactor,vectorscale,mupp,vupp = self.scaleFactors(context)
        pixelFactor = pixelScaleFactor/context.rasterScaleFactor()
        return veclen * vectorscale * pixelFactor

    # Get the actual plot size of the arrow
    def arrowSize(self,veclen,context):
        pixelScaleFactor,vectorscale,mupp,vupp = self.scaleFactors(context)
        pixelFactor = pixelScaleFactor/context.rasterScaleFactor()
        arrow = self.arrow()
        if self._mode != self.NoArrow:
            arrow.setVector(veclen*vectorscale,0.0,True)
            arrow.setEllipse(0.0,0.0,0.0,False)
        else:
            arrow.setVector(0.0,0.0,False)
            arrow.setEllipse(veclen*vectorscale,0.0,0.0,True)
        return arrow.arrowSize(pixelFactor)

    def renderScaleBoxSymbol(self,veclen,point,context):
        pixelScaleFactor,vectorscale,mupp,vupp = self.scaleFactors(context)
        arrow = self.arrow()
        if self._mode != self.NoArrow:
            arrow.setVector(veclen*vectorscale,0.0,True)
            arrow.setEllipse(0.0,0.0,0.0,False)
        else:
            arrow.setVector(0.0,0.0,False)
            arrow.setEllipse(veclen*vectorscale,0.0,0.0,True)
        arrow.setupMarker()
        pixelFactor = pixelScaleFactor/context.rasterScaleFactor()
        arrow.renderArrow(point,context.painter(),pixelFactor)

    def legendSymbologyItems( self, size ):
        iconType = VectorArrowMarker.IconArrow
        if self._mode == self.NoArrow:
            if self._ellipseMode == self.CircularEllipse:
                iconType = VectorArrowMarker.IconCircle
            elif self._ellipseMode == self.HeightEllipse:
                iconType = VectorArrowMarker.IconTickVertical
            else:
                iconType = VectorArrowMarker.IconEllipse
        icon = self.arrow().legendIcon(size,iconType)
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

