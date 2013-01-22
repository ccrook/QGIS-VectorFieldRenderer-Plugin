
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from VectorFieldRenderer import VectorFieldRenderer

class VectorFieldRendererScaleBox:

    class Layer:
        def __init__(self,renderer):
           self._r = renderer
    
        def setup(self,arrowlen,font):
           r = self._r
    
           veclen = max(0.0,r.arrowPixelLength(1.0))
           if veclen > 0:
               preflen = arrowlen/veclen
               veclen = 1.0
               while veclen < preflen:
                   veclen *= 10.0
               while veclen > preflen:
                   veclen /= 10.0
               for x in (5,2):
                   if veclen*x < preflen:
                       veclen *= x
                       break
           if veclen >= 1:
               veclen = int(veclen)
           self._veclen = veclen
           self._label = str(veclen) + r.scaleBoxText()
           self._arrowBox = r.arrowSize(veclen)
           self._textBox = QFontMetrics(font).boundingRect(self._label)
    
        def arrowBox(self):
           return self._arrowBox
    
        def textBox(self):
           return self._textBox
        
        def height(self):
           return max(self._arrowBox.height(),self._textBox.height())
    
        def render(self,arrowx,textx,topy,painter):
           arrowx -= self._arrowBox.left()
           arrowy = topy + self.height()/2.0
           painter.save()
           self._r.renderScaleBoxSymbol(self._veclen,QPointF(arrowx,arrowy),painter)
           painter.restore()
           topy += (self.height() - self._textBox.height())/2.0 - self._textBox.top()
           painter.drawText(QPointF(textx,topy),self._label)
    

    def __init__(self,iface):
       self._iface = iface
       self.reset()

    def reset(self):
       self._arrowSizePercent = 5.0
       self._titleFont = QFont("Arial",12)
       self._scaleFont = QFont("Arial",10)
       self._title = "Vector scale"
       self._offsetX = 15
       self._offsetY = 15
       self._align = 3
       self._brushColor = QColor(255,255,255)
       self._penColor = QColor(0,0,0)
       self._boxPenWidth = 1
       self._showBox = True
       self._fillBox = True
       self.readSettings()

    def arrowSizePercent(self):
       return self._arrowSizePercent
    def setArrowSizePercent(self,arrowSizePercent):
       self.writeSetting("arrowSizePercent",arrowSizePercent)
       self._arrowSizePercent=arrowSizePercent

    def titleFont(self):
       return self._titleFont
    def setTitleFont(self,titleFont):
       self.writeSetting("titleFont",titleFont.toString())
       self._titleFont=titleFont

    def scaleFont(self):
       return self._scaleFont
    def setScaleFont(self,scaleFont):
       self.writeSetting("scaleFont",scaleFont.toString())
       self._scaleFont=scaleFont

    def title(self):
       return self._title
    def setTitle(self,title):
       self.writeSetting("title",title)
       self._title=title

    def offsetX(self):
       return self._offsetX
    def setOffsetX(self,offsetX):
       self.writeSetting("offsetX",offsetX)
       self._offsetX=offsetX

    def offsetY(self):
       return self._offsetY
    def setOffsetY(self,offsetY):
       self.writeSetting("offsetY",offsetY)
       self._offsetY=offsetY

    def align(self):
       return self._align
    def setAlign(self,align):
       self.writeSetting("align",align)
       self._align=align

    def brushColor(self):
       return self._brushColor
    def setBrushColor(self,brushColor):
       self.writeSetting("brushColor",brushColor.name())
       self._brushColor=brushColor

    def penColor(self):
       return self._penColor
    def setPenColor(self,penColor):
       self.writeSetting("penColor",penColor.name())
       self._penColor=penColor

    def boxPenWidth(self):
       return self._boxPenWidth
    def setBoxPenWidth(self,boxPenWidth):
       self.writeSetting("penBoxWidth",penBoxWidth)
       self._boxPenWidth=boxPenWidth

    def showBox(self):
       return self._showBox
    def setShowBox(self,showBox):
       self.writeSetting("showBox",showBox)
       self._showBox=showBox

    def fillBox(self):
       return self._fillBox
    def setFillBox(self,fillBox):
       self.writeSetting("fillBox",fillBox)
       self._fillBox=fillBox


    def writeSetting(self,attribute,value):
       QgsProject.instance().writeEntry("VectorFieldRenderer","/ScaleBox/"+attribute, value )

    def readSetting(self,func,attribute,value):
       v,ok = func("VectorFieldRenderer","/ScaleBox/"+attribute)
       if ok:
           value = v
       return value
       
    def readSettings(self):
       prj = QgsProject.instance()
       rs = prj.readEntry
       rn = prj.readNumEntry
       rf = prj.readDoubleEntry
       rb = prj.readBoolEntry
    
       self._align = self.readSetting(rn,"align",self._align)
       self._arrowSizePercent = self.readSetting(rf,"arrowSizePercent",self._arrowSizePercent)
       self._offsetX = self.readSetting(rf,"offsetX",self._offsetX)
       self._offsetY = self.readSetting(rf,"offsetY",self._offsetY)
       self._boxPenWidth = self.readSetting(rf,"boxPenWidth",self._boxPenWidth)
       self._title = self.readSetting(rs,"title",self._title)
       self._showBox = self.readSetting(rb,"showBox",self._showBox)
       self._fillBox = self.readSetting(rb,"fillBox",self._fillBox)
       self._titleFont.fromString(self.readSetting(rs,"titleFont",self._titleFont.toString()))
       self._scaleFont.fromString(self.readSetting(rs,"scaleFont",self._scaleFont.toString()))
       self._penColor.setNamedColor(self.readSetting(rs,"penColor",self._penColor.name()))
       self._brushColor.setNamedColor(self.readSetting(rs,"brushColor",self._brushColor.name()))


    def render(self, painter):
       try:
          painter.save()
          self._render2(painter)
       finally:
          painter.restore() 
       
    def _render2(self,painter):
       painter.setRenderHint(QPainter.Antialiasing)
       layers = self.getVectorLayers()
       if len(layers) == 0:
          return
       
       height = painter.device().height()
       width = painter.device().width()
       arrowlen = width*(self._arrowSizePercent/100.0)
       for l in layers:
           l.setup(arrowlen,self._scaleFont)
       textwidth = max(l.textBox().width() for l in layers)
       arrowwidth = (
            max(l.arrowBox().right() for l in layers) - 
            min(l.arrowBox().left() for l in layers)
            )

       spacing = QFontMetricsF(self._scaleFont).boundingRect("M").height()/3
       arrowwidth += spacing

       titlesize = QRectF()
       if self._title:
           titlesize = QFontMetricsF(self._titleFont).boundingRect(self._title)

       boxwidth = max(titlesize.width(),textwidth+arrowwidth) + 2*spacing

       boxheight = spacing/2
       if self._title:
           boxheight += titlesize.height() + spacing
       for l in layers:
           boxheight += l.height() + spacing
       boxheight -= spacing/2

       if self._align & 1:
          boxx = width - boxwidth - self._offsetX
       else:
          boxx = self._offsetX

       if self._align & 2:
          boxy = height - boxheight - self._offsetY 
       else:
          boxy = self._offsetY

       if self._showBox:
          painter.save()
          if self._fillBox:
             painter.setBrush(QBrush(self._brushColor))
          else:
             painter.setBrush(Qt.NoBrush)
          painter.setPen(QPen(self._penColor))
          painter.drawRect(QRectF(boxx,boxy,boxwidth,boxheight))
          painter.restore()

       boxy += spacing/2

       if self._title:
          painter.setFont(self._titleFont)
          position = QPointF(boxx + (boxwidth-titlesize.width())/2.0,boxy-titlesize.top())
          painter.drawText(position,self._title)
          boxy += titlesize.height()+spacing

       painter.setFont(self._scaleFont)
       arrowx = boxx + (boxwidth - (arrowwidth+textwidth))/2.0
       textx = arrowx + arrowwidth

       for l in layers:
          l.render(arrowx,textx,boxy,painter)
          boxy += l.height() + spacing

       
    def getVectorLayers(self):
       layers = []
       mc = self._iface.mapCanvas()
       for i in range(mc.layerCount()):
           l = mc.layer(i)
           if l.type() != QgsMapLayer.VectorLayer:
               continue
           if (l.hasScaleBasedVisibility()
               and (mc.scale() < l.minimumScale() 
               or mc.scale() > l.maximumScale())):
                   continue
           v = l.rendererV2()
           if (not v 
               or v.type() != VectorFieldRenderer.rendererName 
               or not v.showInScaleBox()
               or not v.renderedCount()): 
               continue
           layers.append(self.Layer(v))
       return layers

       

   
