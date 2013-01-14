#
# Render a vector point layer using arrows to represent the a vector 
# quantity.
# 

import math
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


#
# Symbol layer class to draw an arrow of a specified size and orientation
#

class VectorArrowMarker(QgsMarkerSymbolLayerV2):

    symbolLayerName = "VectorArrowMarker"

    def __init__(self):
        QgsMarkerSymbolLayerV2.__init__(self)
        self.setWidth(0.7)
        self.setHeadSize(0.3)
        self.setMaxHeadSize(3.0)
        self.setBaseSize(2.0)
        self.setColor( QColor(0,0,0))
        self.setBaseColor( QColor(0,0,0))
        self.setBaseBorderColor( QColor(0,0,0))
        self.setEllipseBorderWidth(0.7)
        self.setEllipseBorderColor( QColor(0,0,0))
        self.setEllipseFillColor( QColor(0,0,0))
        self.setFillEllipse( False )

        self.setVector( 10.0, 0.0, True )
        self.setEllipse( 0.0, 0.0, 0.0, False )
        self._head = [ [0.5,0.0], [-0.4, 0.4], [-0.1,0.0], [-0.4, -0.4] ]

    def width( self ):
        return self._width
    def setWidth( self, width ):
        self._width = width;

    def headSize( self ):
        return self._headSize
    def setHeadSize( self, headSize ):
        self._headSize = headSize

    def maxHeadSize( self ):
        return self._maxHeadSize
    def setMaxHeadSize(self,maxHeadSize):
        self._maxHeadSize = maxHeadSize
    
    def setVector( self, size, angle, drawVector=True ):
        self._vectorSize = size
        self._vectorAngle = angle
        self._drawVector = drawVector
    
    def setEllipse( self, emax, emin, eangle, drawEllipse=True ):
        self._ellipseEmax = emax
        self._ellipseEmin = emin
        self._ellipseAngle = eangle
        self._drawEllipse = drawEllipse

    def baseSize(self):
        return self._baseSize
    def setBaseSize(self,size):
        self._baseSize = size

    def baseColor(self):
        return self._baseColor
    def setBaseColor(self,color):
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

    def ellipseBorderWidth( self ):
        return self._ellipseBorderWidth
    def setEllipseBorderWidth( self, width ):
        self._ellipseBorderWidth = width;

    def fillEllipse( self ):
        return self._fillEllipse
    def setFillEllipse( self, fill ):
        self._fillEllipse = fill

    def baseBorderColor(self):
        return self._baseBorderColor
    def setBaseBorderColor(self,color):
        self._baseBorderColor = color

    def baseBorderColor(self):
        return self._baseBorderColor
    def setBaseBorderColor(self,color):
        self._baseBorderColor = color

    def startRender( self, context ):
        pass

    def stopRender( self, context ):
        pass

    def legendIcon( self, size ):
        px = QPixmap(size)
        px.fill(Qt.transparent)
        y = size.height()/2
        xb = size.width()/5
        xa = size.width()-xb
        size = xb
        p = QPainter()
        p.begin(px)
        p.setRenderHint(QPainter.Antialiasing)
        if self.baseSize() > 0:
           p.setPen(QPen( self.baseBorderColor()))
           p.setBrush(QBrush(self.baseColor()))
           p.drawEllipse(QPoint(xb,y),size,size)

        p.setPen(QPen(self.color()))
        p.setBrush(QBrush(self.color()))
        if self.headSize() > 0 and self.maxHeadSize() > 0:
           pts = [ QPointF( xa + pt[0]*size*2, y+pt[1]*size*2 )
                  for pt in self._head ]
           p.drawPolygon(*pts)
        
        p.setPen(QPen(self.color(),1))
        p.drawLine(xb,y,xa,y)
        p.end()
        return px
         
    def arrowSize( self, pixelFactor ):
        length = self._vectorSize*pixelFactor
        headsize = min(self.headSize()*length, self.maxHeadSize()*pixelFactor)
        basesize = self._baseSize*pixelFactor
        left = min(-basesize,headsize*min([p[0] for p in self._head]))
        right = max(basesize,length+headsize*max([p[0] for p in self._head]))
        width = max(basesize,headsize*max([p[1] for p in self._head]))
        return QRectF(left,-width,right-left,width*2)

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

        if self._drawVector:
            length = self._vectorSize*pixelFactor
            cosangle = math.cos(self._vectorAngle)
            sinangle = math.sin(self._vectorAngle)
            endpoint = QPointF( 
               point.x()+length*cosangle, 
               point.y()-length*sinangle 
               )
        else:
            endpoint = point

        if self._drawEllipse:
           pen = QPen( selColor or self.ellipseBorderColor())
           pen.setWidth(self.ellipseBorderWidth()*pixelFactor)
           pen.setWidth(1.0)
           painter.setPen(pen)
           if self._fillEllipse:
               brush = QBrush(selColor or self.ellipseFillColor())
               painter.setBrush(brush)
           else:
               painter.setBrush(Qt.NoBrush)
           painter.translate(endpoint.x(),endpoint.y())
           painter.rotateRadians(self._ellipseAngle)
           painter.drawEllipse( QPointF(0.0,0.0), self._ellipseEmax*pixelFactor, self._ellipseEmin*pixelFactor )
           painter.rotateRadians(-self._ellipseAngle)
           painter.translate(-endpoint.x(),-endpoint.y())
    
        if self.baseSize() > 0:
           pen = QPen( selColor or self.baseBorderColor())
           pen.setWidth(1.0)
           painter.setPen(pen)
           brush = QBrush(selColor or self.baseColor())
           painter.setBrush(brush)
           radius = self.baseSize()*pixelFactor/2.0
           painter.drawEllipse(point,radius,radius)

        if self._drawVector:
            if length <= 0:
               return
            pen = QPen( selColor or self.color())
            pen.setWidth(self.width()*pixelFactor)
            painter.setPen(pen)
            width = self.width()
            headsize = min(self.headSize()*length, self.maxHeadSize()*pixelFactor)
            painter.drawLine(point, endpoint)
            if headsize > width:
               pts = [ QPointF(
                        endpoint.x() + p[0]*cosangle*headsize - p[1]*sinangle*headsize,
                        endpoint.y() - p[0]*sinangle*headsize - p[1]*cosangle*headsize )
                      for p in self._head ]
               pen.setWidth(0)
               painter.setPen(pen)
               brush = QBrush(selColor or self.color())
               painter.setBrush(brush)
               painter.drawPolygon(*pts)
              

    def layerType(self):
        return VectorArrowMarker.symbolLayerName

    def clone(self):
        clone = VectorArrowMarker()
        clone.setColor(self.color())
        clone.setSize(self.size())
        clone.setAngle(self.angle())
        clone.setWidth(self.width())
        clone.setHeadSize(self.headSize())
        clone.setMaxHeadSize(self.maxHeadSize())
        clone.setBaseSize(self.baseSize())
        clone.setBaseColor(self.baseColor())
        clone.setBaseBorderColor(self.baseBorderColor())
        clone.setEllipseBorderWidth(self.ellipseBorderWidth())
        clone.setEllipseBorderColor(self.ellipseBorderColor())
        clone.setFillEllipse(self.fillEllipse())
        clone.setEllipseFillColor(self.ellipseFillColor())
        return clone

    def properties(self):
        sm = {
           "size": str(self.size()),
           "angle": str(self.angle()),
           "width": str(self.width()),
           "headsize": str(self.headSize()),
           "maxheadsize": str(self.maxHeadSize()),
           "basesize": str(self.baseSize()),
           "color": self.color().name(),
           "basecolor": self.baseColor().name(),
           "basebordercolor": self.baseBorderColor().name()
            }
        return sm;

    def setProperties(self,props):
        try:
            self.setSize(float(props[QString("size")]))
            self.setAngle(float(props[QString("angle")]))
            self.setWidth(float(props[QString("width")]))
            self.setHeadSize(float(props[QString("headsize")]))
            self.setMaxHeadSize(float(props[QString("maxheadsize")]))
            self.setBaseSize(float(props[QString("basesize")]))
            self.setColor(QColor(str(props[QString("color")])))
            self.setBaseColor(QColor(str(props[QString("basecolor")])))
            self.setBaseBorderColor(QColor(str(props[QString("basebordercolor")])))
        except:
            pass
                 

