#
# Render a vector point layer using arrows to represent the a vector
# quantity.
#

import math
import sys
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


#
# Symbol layer class to draw an arrow of a specified size and orientation
#

class VectorArrowMarker(QgsMarkerSymbolLayerV2):

    symbolLayerName = "VectorArrowMarker"
    minEllipseRatio = 0.001

    IconArrow=0
    IconEllipse=1
    IconCircle=2
    IconTickVertical=3
    IconTickHorizontal=4

    DrawBasePart=0
    DrawArrowPart=1
    DrawEllipsePart=2

    def __init__(self):
        QgsMarkerSymbolLayerV2.__init__(self)
        self.setWidth(0.7)
        self.setRelativeHeadSize(0.3)
        self.setHeadWidth(0.0)
        self.setHeadFillColor(QColor(0,0,0))
        self.setFillHead(True)
        self.setHeadShape((0.0,-1.0,-0.7))
        self.setMaxHeadSize(3.0)
        self.setBaseSize(2.0)
        self.setEllipseTickSize(2.0)
        self.setColor( QColor(0,0,0))
        self.setFillBase( True )
        self.setBaseFillColor( QColor(0,0,0))
        self.setBaseBorderWidth(0.0)
        self.setBaseBorderColor( QColor(0,0,0))
        self.setEllipseBorderWidth(0.7)
        self.setEllipseBorderColor( QColor(0,0,0))
        self.setEllipseFillColor( QColor(0,0,0))
        self.setFillEllipse( False )
        self.setDrawEllipse( True )
        self.setDrawEllipseAxes( False )

        self.setVector( 10.0, 0.0, True )
        self.setEllipse( 0.0, 0.0, 0.0, False )

    def width( self ):
        return self._width
    def setWidth( self, width ):
        self._width = width;
    # More meaningful alias
    def shaftWidth( self ):
        return self._width
    def setShaftWidth( self, width ):
        self.setWidth(width)

    def headSize( self ):
        return self._headSize
    def setHeadSize( self, headSize ):
        self._headSize = headSize
    # More meaningful alias
    def relativeHeadSize( self ):
        return self._headSize
    def setRelativeHeadSize( self, headSize ):
        self._headSize = headSize

    def headShape( self ):
        return self._headshape
    def headShapeStr( self ):
        return ' '.join((str(x) for x in self._headshape))
    def setHeadShape( self, *values ):
        if len(values) == 1:
            values=values[0]
        if type(values) == str:
            values = [float(x) for x in values.split()]
        if len(values) != 3:
            raise ValueError("Invalid value for arrow head shape")
        self._headshape = values

    def headWidth( self ):
        return self._headWidth
    def setHeadWidth( self, headWidth ):
        self._headWidth = headWidth

    def headFillColor(self):
        return self._headColor
    def setHeadFillColor(self,color):
        self._headColor = color

    def fillHead(self):
        return self._fillHead
    def setFillHead(self,fillHead):
        self._fillHead = fillHead

    def maxHeadSize( self ):
        return self._maxHeadSize
    def setMaxHeadSize(self,maxHeadSize):
        self._maxHeadSize = maxHeadSize

    def baseSize(self):
        return self._baseSize
    def setBaseSize(self,size):
        self._baseSize = size

    def baseBorderWidth(self):
        return self._baseBorderWidth
    def setBaseBorderWidth(self,baseBorderWidth):
        self._baseBorderWidth = baseBorderWidth

    def fillBase( self ):
        return self._fillBase
    def setFillBase( self, fillBase ):
        self._fillBase = fillBase

    def baseFillColor(self):
        return self._baseColor
    def setBaseFillColor(self,color):
        self._baseColor = color

    def baseBorderColor(self):
        return self._baseBorderColor
    def setBaseBorderColor(self,color):
        self._baseBorderColor = color

    def ellipseBorderColor(self):
        return self._ellipseBorderColor
    def setEllipseBorderColor(self,color):
        self._ellipseBorderColor = color

    def ellipseFillColor(self):
        return self._ellipseFillColor
    def setEllipseFillColor(self,color):
        self._ellipseFillColor = color

    def ellipseTickSize( self ):
        return self._ellipseTickSize
    def setEllipseTickSize( self, size ):
        self._ellipseTickSize = size;

    def ellipseBorderWidth( self ):
        return self._ellipseBorderWidth
    def setEllipseBorderWidth( self, width ):
        self._ellipseBorderWidth = width;

    def fillEllipse( self ):
        return self._fillEllipse
    def setFillEllipse( self, fill ):
        self._fillEllipse = fill

    def drawEllipse( self ):
        return self._drawEllipse
    def setDrawEllipse( self, drawEllipse):
        self._drawEllipse = drawEllipse

    def drawEllipseAxes( self ):
        return self._drawEllipseAxes
    def setDrawEllipseAxes( self, drawEllipseAxes):
        self._drawEllipseAxes = drawEllipseAxes

    def baseBorderColor(self):
        return self._baseBorderColor
    def setBaseBorderColor(self,color):
        self._baseBorderColor = color

    def baseBorderColor(self):
        return self._baseBorderColor
    def setBaseBorderColor(self,color):
        self._baseBorderColor = color

    def setupMarker(self):
        front, back, centre = self._headshape
        small = 0.001
        if abs(front - centre) > small:
            self._head = ( (front,0.0),(back,0.5),(centre,0.0),(back,-0.5) )
            self._headpoly = True
        else:
            self._head = ( (back,0.5),(front,0.0),(back,-0.5) )
            self._headpoly = False
        # If we want to have the tip of the arrow at the measurement point
        # then we need to apply an offset to account for mitring the width
        # of the arrow border.
        self._mitreWidthOffset = 0.0
        if abs(front) < small and back < -small:
            self._mitreWidthOffset = -math.sqrt(back*back+0.25)

        # Arrow shaft will need to end before the point to avoid squaring off
        # the end.  Only applies if the
        self._shaftBack = centre
        self._shaftFront = front
        self._shaftFrontOffset = 0.0
        if back < front:
            self._shaftFrontOffset = back-front

        # If drawing the ellipse

        parts = []
        ellipse = self._drawEllipse or self._drawEllipseAxes
        if self._drawEllipse and self._fillEllipse:
            parts.append(self.DrawEllipsePart)
            ellipse = False
        if self._baseSize > 0:
            parts.append(self.DrawBasePart)
        parts.append(self.DrawArrowPart)
        if ellipse:
            parts.append(self.DrawEllipsePart)
        self._drawparts = parts

    def startRender( self, context ):
        self.setupMarker()

    def stopRender( self, context ):
        pass

    def setVector( self, size, angle, drawArrow=True ):
        self._vectorSize = size
        self._vectorAngle = angle
        self._drawCurrentArrow = drawArrow

    def setEllipse( self, emax, emin, eangle, drawEllipse=True ):
        self._ellipseEmax = emax
        self._ellipseEmin = emin
        self._ellipseAngle = eangle
        self._drawCurrentEllipse = drawEllipse

    def legendIcon( self, size, iconType):
        print("legendIcon called")
        self.setupMarker()
        px = QPixmap(size)
        px.fill(Qt.transparent)
        y = size.height()/2
        msize = size.width()/5
        if iconType == self.IconArrow:
            xb = msize
        else:
            xb = size.width()/2

        xa = size.width()-xb
        p = QPainter()
        p.begin(px)
        p.setRenderHint(QPainter.Antialiasing)

        if iconType != self.IconArrow:
            p.setPen(QPen( self.ellipseBorderColor()))
            if iconType == self.IconTickVertical:
                p.drawLine(xb-msize,0,xb+msize,0)
                p.drawLine(xb-msize,size.height(),xb+msize,size.height())
                p.drawLine(xb,0,xb,size.height())
            elif iconType == self.IconTickHorizontal:
                p.drawLine(0,y-msize,0,y+msize,0)
                p.drawLine(size.width(),y-msize,size.width(),y+msize)
                p.drawLine(0,y,size.width(),y)
            else:
                if self.fillEllipse():
                    p.setBrush(QBrush(self.ellipseFillColor()))
                else:
                    p.setBrush(Qt.NoBrush)
                height = size.width()/2.0
                if iconType == self.IconEllipse:
                    height *= 0.6
                p.drawEllipse(QPointF(y,xb),size.width()/2.0,height)

        if self.baseSize() > 0:
            p.setPen(QPen( self.baseBorderColor()))
            if self.fillBase():
                p.setBrush(QBrush(self.baseFillColor()))
            else:
                p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(xb,y),msize,msize)

        if iconType == self.IconArrow:
            p.setPen(QPen(self.color()))
            p.setBrush(QBrush(self.color()))
            if self.relativeHeadSize() > 0 or self.maxHeadSize() > 0:
                pts = [ QPointF( xa + pt[0]*msize*2, y+pt[1]*msize*2 )
                       for pt in self._head ]
                p.drawPolygon(*pts)

            p.setPen(QPen(self.color(),1))
            p.drawLine(xb,y,xa,y)
        p.end()
        self._icon=px
        print("Icon built")
        return px

    def calcHeadSize( self, length, pixelFactor ):
        headsize = 0.0
        if self._maxHeadSize > 0.0:
            headsize = self._maxHeadSize*pixelFactor
        if self._headSize > 0.0:
            relsize = self._headSize*length
            headsize = relsize if headsize <= 0 else min(headsize,relsize)
        return headsize

    def arrowSize( self, pixelFactor ):
        self.setupMarker()
        basesize = (self._baseSize+self._baseBorderWidth)*pixelFactor/2.0
        left = -basesize
        right = basesize
        bottom = -basesize
        top = basesize
        if self._drawCurrentArrow:
            length = self._vectorSize*pixelFactor
            headsize = self.calcHeadSize( length, pixelFactor )
            hw = self._headWidth*pixelFactor
            left = min(left,headsize*min([p[0] for p in self._head])-hw)
            right = max(right,length+hw+headsize*max([p[0] for p in self._head]))
            bottom = min(bottom,-0.5*self._width*pixelFactor,headsize*min([p[1] for p in self._head])-hw)
            top = max(top,0.5*self._width*pixelFactor,headsize*max([p[1] for p in self._head])+hw)
        if self._drawCurrentEllipse:
            emax = abs(self._ellipseEmax * pixelFactor)
            emin = abs(self._ellipseEmin * pixelFactor)
            if emin <= emax*self.minEllipseRatio:
                ticksize = self.ellipseTickSize()*pixelFactor/2.0
                emin=ticksize
            emin += self._ellipseBorderWidth*0.5*pixelFactor
            emax += self._ellipseBorderWidth*0.5*pixelFactor
            left = min(left,-emax)
            right = max(right,emax)
            bottom = min(bottom,-emin)
            top = max(top,emin)
        return QRectF(left,bottom,right-left,top-bottom)

    def renderPoint( self, point, context ):
        # Test selected to support earlier builds of 1.5 dev stream
        selColor = None
        if 'selected' in dir(context):
            selected = context.selected()
            if selected:
                selColor = context.selectionColor()
        painter = context.renderContext().painter()
        pixelFactor = context.outputPixelSize(1.0)/context.renderContext().rasterScaleFactor()
        self.renderArrow( point, painter, pixelFactor, selColor )

    def renderArrow( self, point, painter, pixelFactor, selColor=None ):
        drawArrow = self._drawCurrentArrow
        if drawArrow:
            length = self._vectorSize*pixelFactor
            cosangle = math.cos(self._vectorAngle)
            sinangle = math.sin(self._vectorAngle)
            px = point.x()
            py = point.y()
            endpoint = QPointF( px+length*cosangle, py-length*sinangle)
            headsize = self.calcHeadSize( length, pixelFactor )

            pts = None
            shaftwidth = self._width*pixelFactor
            headwidth = self._headWidth*pixelFactor
            if headsize > shaftwidth:
                length += self._mitreWidthOffset*headwidth
                ch=cosangle*headsize
                sh=sinangle*headsize
                ex = px+length*cosangle
                ey = py-length*sinangle
                pts = [ QPointF( ex + p[0]*ch - p[1]*sh, ey - p[0]*sh - p[1]*ch )
                       for p in self._head ]
                length += min(self._shaftBack*headsize,
                              self._shaftFront*headsize+self._shaftFrontOffset*shaftwidth )
                if length > 0:
                    lineend=QPointF(px+length*cosangle,py-length*sinangle)
                else:
                    lineend=None
            else:
                headsize=0
                lineend = endpoint
        else:
            endpoint = point

        for p in self._drawparts:

            if p == self.DrawBasePart:
                pen = QPen( selColor or self._baseBorderColor)
                pen.setWidth(self._baseBorderWidth*pixelFactor)
                painter.setPen(pen)
                if self._fillBase:
                    brush = QBrush(selColor or self._baseColor)
                    painter.setBrush(brush)
                else:
                    painter.setBrush(Qt.NoBrush)
                radius = self._baseSize*pixelFactor/2.0
                painter.drawEllipse(point,radius,radius)

            if p == self.DrawArrowPart and drawArrow:
                pen = QPen( selColor or self.color())
                pen.setJoinStyle( Qt.MiterJoin )
                pen.setCapStyle( Qt.FlatCap )
                if lineend:
                    pen.setWidth(shaftwidth)
                    painter.setPen(pen)
                    painter.drawLine(point, lineend)
                if pts:
                    pen.setWidth(headwidth)
                    painter.setPen(pen)
                    if self._headpoly:
                        if self._fillHead:
                            brush = QBrush(selColor or self._headColor)
                            painter.setBrush(brush)
                        else:
                            painter.setBrush(Qt.NoBrush)
                        painter.drawPolygon(*pts)
                    else:
                        painter.drawPolyline(*pts)

            if p == self.DrawEllipsePart and self._drawCurrentEllipse:
                pen = QPen( selColor or self._ellipseBorderColor)
                pen.setWidth(self._ellipseBorderWidth*pixelFactor)
                painter.setPen(pen)
                painter.save()
                painter.translate(endpoint.x(),endpoint.y())
                angle=-math.degrees(self._ellipseAngle)
                painter.rotate(angle)
                emax = self._ellipseEmax * pixelFactor
                emin = self._ellipseEmin * pixelFactor
                if emin > emax*self.minEllipseRatio:
                    if self._drawEllipse:
                        if self._fillEllipse:
                            brush = QBrush(selColor or self._ellipseFillColor)
                            painter.setBrush(brush)
                        else:
                            painter.setBrush(Qt.NoBrush)
                        painter.drawEllipse( QPointF(0.0,0.0),
                            self._ellipseEmax*pixelFactor, self._ellipseEmin*pixelFactor )
                    if self._drawEllipseAxes:
                        painter.drawLine(QPointF(-emax,0.0),QPointF(emax,0.0))
                        painter.drawLine(QPointF(0.0,-emin),QPointF(0.0,emin))
                else:
                    ticksize = self._ellipseTickSize*pixelFactor/2.0
                    painter.drawLine(QPointF(-emax,0.0),QPointF(emax,0.0))
                    painter.drawLine(QPointF(-emax,-ticksize),QPointF(-emax,ticksize))
                    painter.drawLine(QPointF(emax,-ticksize),QPointF(emax,ticksize))
                painter.restore()


    def layerType(self):
        return VectorArrowMarker.symbolLayerName

    def clone(self):
        clone = VectorArrowMarker()
        clone.setColor(self.color())
        clone.setSize(self.size())
        clone.setAngle(self.angle())
        clone.setWidth(self.width())
        clone.setRelativeHeadSize(self.relativeHeadSize())
        clone.setMaxHeadSize(self.maxHeadSize())
        clone.setHeadWidth(self.headWidth())
        clone.setFillHead(self.fillHead())
        clone.setHeadFillColor(self.headFillColor())
        clone.setHeadShape(self.headShape())
        clone.setBaseSize(self.baseSize())
        clone.setFillBase(self.fillBase())
        clone.setBaseFillColor(self.baseFillColor())
        clone.setBaseBorderWidth(self.baseBorderWidth())
        clone.setBaseBorderColor(self.baseBorderColor())
        clone.setEllipseBorderWidth(self.ellipseBorderWidth())
        clone.setEllipseTickSize(self.ellipseTickSize())
        clone.setEllipseBorderColor(self.ellipseBorderColor())
        clone.setFillEllipse(self.fillEllipse())
        clone.setEllipseFillColor(self.ellipseFillColor())
        clone.setDrawEllipse(self.drawEllipse())
        clone.setDrawEllipseAxes(self.drawEllipseAxes())
        return clone

    def properties(self):
        sm = {
           "color": self.color().name(),
           "size": str(self.size()),
           "angle": str(self.angle()),
           "width": str(self.width()),
           "headsize": str(self.relativeHeadSize()),
           "maxheadsize": str(self.maxHeadSize()),
           "headwidth": str(self.headWidth()),
           "fillhead": str( self.fillHead()),
           "headcolor": self.headFillColor().name(),
           "headshape": self.headShapeStr(),
           "basesize": str(self.baseSize()),
           "baseborderwidth": str(self.baseBorderWidth()),
           "basebordercolor": self.baseBorderColor().name(),
           "fillbase": str( self.fillBase()),
           "basecolor": self.baseFillColor().name(),
           "drawellipse": str(self.drawEllipse()),
           "drawellipseaxes": str(self.drawEllipseAxes()),
           "ellipseborderwidth": str(self.ellipseBorderWidth()),
           "ellipsebordercolor": self.ellipseBorderColor().name(),
           "fillellipse": str(self.fillEllipse()),
           "ellipsefillcolor": self.ellipseFillColor().name(),
           "ellipseticksize": str(self.ellipseTickSize()),
            }
        return sm;

    def setProperties(self,props):
        try:
            # Note properties here are ordered as they have been added
            # to the symbol with each version, so that old versions can
            # still be read (won't hit exceptions until old values have
            # been read)
            self.setSize(float(props["size"]))
            self.setAngle(float(props["angle"]))
            self.setWidth(float(props["width"]))
            self.setRelativeHeadSize(float(props["headsize"]))
            self.setMaxHeadSize(float(props["maxheadsize"]))
            self.setBaseSize(float(props["basesize"]))
            self.setColor(QColor(str(props["color"])))
            # For backward compatibility
            self.setHeadFillColor(QColor(str(props["color"])))
            self.setBaseFillColor(QColor(str(props["basecolor"])))
            self.setBaseBorderColor(QColor(str(props["basebordercolor"])))
            self.setEllipseBorderWidth(float(props["ellipseborderwidth"]))
            self.setEllipseBorderColor(QColor(str(props["ellipsebordercolor"])))
            self.setEllipseFillColor(QColor(str(props["ellipsefillcolor"])))
            self.setFillEllipse(bool(str(props["fillellipse"])))
            self.setEllipseTickSize(float(props["ellipseticksize"]))
            self.setDrawEllipse(bool(str(props["drawellipse"])))
            self.setDrawEllipseAxes(bool(str(props["drawellipseaxes"])))
            self.setBaseBorderWidth(float(props["baseborderwidth"]))
            self.setHeadWidth(float(props["headwidth"]))
            self.setHeadFillColor(QColor(str(props["headcolor"])))
            self.setFillHead(bool(str(props["fillhead"])))
            self.setHeadShape(str(props["headshape"]))
            self.setFillBase(bool(str(props["fillbase"])))
        except:
            pass

    def saveToXmlElement( self, element ):
        element.setAttribute("baseSize",str(self.baseSize()))
        element.setAttribute("baseBorderWidth",str(self.baseBorderWidth()))
        element.setAttribute("baseBorderColor",self.baseBorderColor().name())
        element.setAttribute("fillBase",str(self.fillBase()))
        element.setAttribute("baseColor",self.baseFillColor().name())
        element.setAttribute("arrowColor",self.color().name())
        element.setAttribute("arrowWidth",str(self.width()))
        element.setAttribute("arrowHeadSize",str(self.relativeHeadSize()))
        element.setAttribute("arrowHeadWidth",str(self.headWidth()))
        element.setAttribute("arrowHeadShape",self.headShapeStr())
        element.setAttribute("arrowFillHead",str(self.fillHead()))
        element.setAttribute("arrowHeadColor",self.headFillColor().name())
        element.setAttribute("arrowMaxHeadSize",str(self.maxHeadSize()))
        element.setAttribute("drawEllipse",str(self.drawEllipse()))
        element.setAttribute("drawEllipseAxes",str(self.drawEllipseAxes()))
        element.setAttribute("ellipseBorderColor",self.ellipseBorderColor().name())
        element.setAttribute("ellipseBorderWidth",str(self.ellipseBorderWidth()))
        element.setAttribute("ellipseTickSize",str(self.ellipseTickSize()))
        element.setAttribute("ellipseFillColor",self.ellipseFillColor().name())
        element.setAttribute("fillEllipse",str(self.fillEllipse()))


    def readFromXmlElement( self, element ):
       # Note properties here are ordered as they have been added
       # to the symbol with each version, so that old versions can
       # still be read (won't hit exceptions until old values have
       # been read)
        try:
            color = QColor()
            color.setNamedColor( element.attribute("baseColor"))
            self.setBaseFillColor( color )
            color = QColor()
            color.setNamedColor( element.attribute("baseBorderColor"))
            self.setBaseBorderColor( color )
            self.setBaseSize( float( element.attribute("baseSize")))
            self.setBaseBorderWidth( float( element.attribute("baseBorderWidth","0.0")))
            self.setFillBase( element.attribute("fillBase","True") == "True" )

            color = QColor()
            color.setNamedColor( element.attribute("arrowColor"))
            self.setColor( color )
            self.setWidth( float( element.attribute("arrowWidth")))
            self.setRelativeHeadSize( float( element.attribute("arrowHeadSize")))
            self.setHeadWidth( float( element.attribute("arrowHeadWidth","0.0")))
            self.setFillHead( element.attribute("arrowFillHead","True") == "True" )
            color = QColor()
            # Use color for compatibility with old XML (without head colour)
            color.setNamedColor( element.attribute("arrowHeadColor",self.color().name()))
            self.setHeadFillColor( color )
            self.setMaxHeadSize( float( element.attribute("arrowMaxHeadSize")))
            self.setHeadShape(str(element.attribute("arrowHeadShape",self.headShapeStr())))

            color = QColor()
            color.setNamedColor( element.attribute("ellipseBorderColor","black"))
            self.setEllipseBorderColor( color )
            color = QColor()
            color.setNamedColor( element.attribute("ellipseFillColor","black"))
            self.setEllipseFillColor( color )
            self.setDrawEllipse( element.attribute("drawEllipse","True") == "True" )
            self.setDrawEllipseAxes( element.attribute("drawEllipseAxes","False") == "True" )
            self.setFillEllipse( element.attribute("fillEllipse","False") == "True" )
            self.setEllipseBorderWidth( float( element.attribute("ellipseBorderWidth","0.0")))
            self.setEllipseTickSize( float( element.attribute("ellipseTickSize","2.0")))
        except:
            pass
