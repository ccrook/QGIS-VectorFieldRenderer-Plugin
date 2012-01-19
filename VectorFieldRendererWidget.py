import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from VectorFieldRenderer import VectorFieldRenderer
from Ui_VectorFieldRendererWidget import Ui_VectorFieldRendererWidget

# Color button class - connects up QgsColorButton with a color dialog

class ColorButton:
   def __init__(self,button):
      self._button = button
      QObject.connect(button,SIGNAL("clicked()"),self.clicked)

   def color(self):
      return self._button.color()

   def setColor(self,color):
      if color.isValid():
         self._button.setColor(color)

   def clicked(self):
      self.setColor(QColorDialog.getColor(self.color()))

class UnitButton:
   def __init__(self,button,mmtext="Millimetres"):
      self._button = button
      self._mmLabel = mmtext
      self.setUnits(QgsSymbolV2.MM)
      QObject.connect(button,SIGNAL("clicked()"),self.clicked)

   def units(self):
      return self._units

   def setUnits(self,units):
      if units == QgsSymbolV2.MM:
         self._units = QgsSymbolV2.MM
         self._button.setText(self._mmLabel)
      else:
         self._units = QgsSymbolV2.MapUnit
         self._button.setText("Map units")

   def isMapUnit( self ):
       return self._units == QgsSymbolV2.MapUnit

   def setIsMapUnit( self, isMapUnits ):
      if isMapUnits:
          self.setUnits(QgsSymbolV2.MapUnit)
      else:
          self.setUnits(QgsSymbolV2.MM)

   def clicked(self):
      self.setIsMapUnit( not self.isMapUnit())

# Vector field renderer widget

class VectorFieldRendererWidget(QgsRendererV2Widget,Ui_VectorFieldRendererWidget):

    def __init__(self,layer,style,renderer):
        QgsRendererV2Widget.__init__(self, layer, style)

        if renderer is None or renderer.type() != VectorFieldRenderer.rendererName:
            self.r = VectorFieldRenderer()
        else:
            self.r = renderer

        self.validLayer = True
        if layer.geometryType() != QGis.Point:
           self.setupBlankUi(layer)
           self.validLayer = False
           return

        self._mode = VectorFieldRenderer.Cartesian
        self.buildWidget()
        self.setupLayer(layer)
        self.loadFromRenderer()

    def setupBlankUi(self,layer):
        name = layer.name()
        self.uLayout = QVBoxLayout()
        self.uLabel = QLabel(
              "The vector field renderer only applies to point type layers.\n\n"
              +name+" is not a point layer, and cannot be displayed by the vector field renderer.\n\n"
              )
        self.uLayout.addWidget(self.uLabel)
        self.setLayout(self.uLayout)

    def buildWidget(self):
        self.setupUi(self)
        self.arrowColor = ColorButton(self.uArrowColor)
        self.baseColor = ColorButton(self.uBaseColor)
        self.baseBorderColor = ColorButton(self.uBaseBorderColor)

        self.outputUnits = UnitButton(self.uOutputUnits)
        self.scaleUnits = UnitButton(self.uScaleUnits,"Arrow unit")

        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uArrowScale.setValidator(QRegExpValidator(re,self))

        resg = QRegExp("(\\w+(\\*\\d+(\\.\\d*)?)?)?")
        self.uScaleGroup.setValidator(QRegExpValidator(resg,self))

        QObject.connect(self.uFieldTypeCartesian, SIGNAL("toggled(bool)"), self.setFieldTypeCartesian )
        QObject.connect(self.uFieldTypePolar, SIGNAL("toggled(bool)"), self.setFieldTypePolar )
        QObject.connect(self.uFieldTypeHeight, SIGNAL("toggled(bool)"), self.setFieldTypeHeight )
        QObject.connect(self.uHelpButton, SIGNAL("clicked()"), self.showHelp )

    # event handlers

    def showHelp(self):
        VectorFieldRenderer.showHelp()

    def setFieldTypeCartesian( self, isset):
        if isset:
           self.setMode( VectorFieldRenderer.Cartesian )

    def setFieldTypePolar( self, isset):
        if isset:
           self.setMode( VectorFieldRenderer.Polar )

    def setFieldTypeHeight( self, isset):
        if isset:
           self.setMode( VectorFieldRenderer.Height )

    def mode(self):
        return self._mode

    def setMode(self,mode):
        if mode == VectorFieldRenderer.Height:
            self.uFieldTypeHeight.setChecked(True)
            self.uXFieldLabel.setText("Height attribute")
            self.uYFieldLabel.setText("")
            self.uYField.setCurrentIndex(-1)
        elif mode == VectorFieldRenderer.Polar:
            self.uFieldTypePolar.setChecked(True)
            self.uXFieldLabel.setText("Length attribute")
            self.uYFieldLabel.setText("Angle attribute")
        else:
            self.uFieldTypeCartesian.setChecked(True)
            mode == VectorFieldRenderer.Cartesian
            self.uXFieldLabel.setText("X attribute")
            self.uYFieldLabel.setText("Y attribute")
        self._mode = mode
        self.uYField.setEnabled(mode != VectorFieldRenderer.Height)
        isPolar = (mode == VectorFieldRenderer.Polar)
        self.uAngleUnitsGroupBox.setEnabled( isPolar )
        self.uOrientationGroupBox.setEnabled( isPolar )
 
    def setupLayer( self, layer ):
        self.layer = layer
        self.uXField.clear()
        self.uYField.clear()
        if layer:
           for f in self.getLayerFields(layer):
             self.uXField.addItem(f)
             self.uYField.addItem(f)
 
    def getLayerFields( self, layer ):
         provider = layer.dataProvider()
         feat = QgsFeature()
         attrs = provider.attributeIndexes()
         provider.select(attrs)
         fields = provider.fields()
         fieldlist = []
         for i in fields:
             # type = str(fields[i].typeName()).lower()
             # if (type=="integer") or (type=="double") or (type=="real"):
                 fieldlist.append(fields[i].name())
         return fieldlist 
 
    def renderer(self):
        if self.validLayer:
            self.saveToRenderer()
        return self.r
  
    def loadFromRenderer( self ):
        vfr = self.r
        self.setMode( vfr.mode())
        self.uXField.setCurrentIndex( self.uXField.findText(vfr.xFieldName()))
        self.uYField.setCurrentIndex( self.uYField.findText(vfr.yFieldName()))
        self.uAngleUnitsDegrees.setChecked( vfr.degrees())
        self.uAngleUnitsRadians.setChecked( not vfr.degrees())
        self.uAngleOrientationNorth.setChecked( vfr.angleFromNorth())
        self.uAngleOrientationEast.setChecked( not vfr.angleFromNorth())
        self.scaleUnits.setIsMapUnit(vfr.useMapUnit())
        self.uArrowScale.setText( str(vfr.scale()))
        group = vfr.scaleGroup()
        factor = vfr.scaleGroupFactor()
        if group and factor != 1.0:
           group = group + "*" + str(factor)
        self.uScaleGroup.setText(group)
        self.outputUnits.setUnits(vfr.outputUnit())
        arrow = vfr.arrow()
        self.uArrowHeadSize.setValue( arrow.headSize())
        self.uArrowHeadMaxSize.setValue( arrow.maxHeadSize())
        self.uArrowWidth.setValue( arrow.width())
        self.uArrowBaseSize.setValue( arrow.baseSize())
        self.arrowColor.setColor( arrow.color())
        self.baseColor.setColor( arrow.baseColor())
        self.baseBorderColor.setColor( arrow.baseBorderColor())
        self.uLegendText.setText( vfr.legendText())
        self.uScaleBoxText.setText( vfr.scaleBoxText())
        self.uShowInScaleBox.setChecked( vfr.showInScaleBox())

    def saveToRenderer( self ):
        vfr = self.r
        # Avoid accidentally resetting scale group scale until we've
        # set the new scale group
        vfr.setScaleGroup("")
        vfr.setMode( self.mode())
        vfr.setXFieldName( self.uXField.currentText())
        vfr.setYFieldName( self.uYField.currentText())
        vfr.setDegrees( self.uAngleUnitsDegrees.isChecked())
        vfr.setAngleFromNorth(self.uAngleOrientationNorth.isChecked())
        try:
           vfr.setScale( float(self.uArrowScale.text()))
        except:
           pass
        vfr.setUseMapUnit( self.scaleUnits.isMapUnit())
        group = self.uScaleGroup.text()
        factor = 1.0
        if "*" in group:
            group,f = group.split("*")
            try:
               factor = float(f)
            except:
               pass
        vfr.setScaleGroupFactor(factor)
        vfr.setScaleGroup(group)
        vfr.setOutputUnit(self.outputUnits.units())
        arrow = vfr.arrow()
        arrow.setHeadSize( self.uArrowHeadSize.value())
        arrow.setMaxHeadSize( self.uArrowHeadMaxSize.value())
        arrow.setWidth( self.uArrowWidth.value())
        arrow.setBaseSize( self.uArrowBaseSize.value())
        arrow.setColor( self.arrowColor.color())
        arrow.setBaseColor( self.baseColor.color())
        arrow.setBaseBorderColor( self.baseBorderColor.color())
        vfr.setLegendText( self.uLegendText.text())
        vfr.setScaleBoxText( self.uScaleBoxText.text())
        vfr.setShowInScaleBox( self.uShowInScaleBox.isChecked())
    # TODO: Sort out error handling for scale field.. 
