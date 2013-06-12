import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from VectorFieldRenderer import VectorFieldRenderer
from Ui_VectorFieldRendererWidget import Ui_VectorFieldRendererWidget

# Color button class - connects up QgsColorButton with a color dialog

class ColorButton( QObject ):

   def __init__(self,button):
      QObject.__init__(self)
      self._button = button
      button.clicked.connect( self.clicked )

   def color(self):
      return self._button.color()

   def setColor(self,color):
      if color.isValid():
         self._button.setColor(color)

   def clicked(self):
      self.setColor(QColorDialog.getColor(self.color()))

class UnitButton( QObject ):

   valueChanged = pyqtSignal(name='valueChanged')

   def __init__(self,button,mmtext="Millimetres"):
      QObject.__init__(self)
      self._button = button
      self._mmLabel = mmtext
      self.setUnits(QgsSymbolV2.MM)
      button.clicked.connect(self.clicked)

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
      self.valueChanged.emit()

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
        self._ellipsemode = VectorFieldRenderer.NoEllipse
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
        self.arrowHeadColor = ColorButton(self.uArrowHeadColor)
        self.baseColor = ColorButton(self.uBaseColor)
        self.baseBorderColor = ColorButton(self.uBaseBorderColor)
        self.ellipseBorderColor = ColorButton(self.uEllipseBorderColor)
        self.ellipseFillColor = ColorButton(self.uEllipseFillColor)

        self.scaleUnits = UnitButton(self.uScaleUnits,"Symbol unit")
        self.outputUnits = UnitButton(self.uOutputUnits)

        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uArrowScale.setValidator(QRegExpValidator(re,self))

        resg = QRegExp("(\\w+(\\*\\d+(\\.\\d*)?)?)?")
        self.uScaleGroup.setValidator(QRegExpValidator(resg,self))

        ft = QButtonGroup()
        ft.addButton(self.uFieldTypeCartesian,VectorFieldRenderer.Cartesian)
        ft.addButton(self.uFieldTypePolar,VectorFieldRenderer.Polar)
        ft.addButton(self.uFieldTypeHeight,VectorFieldRenderer.Height)
        ft.addButton(self.uFieldTypeNone,VectorFieldRenderer.NoArrow)
        ft.buttonClicked[int].connect(self.setMode)
        self.fieldTypeGroup = ft

        et = QButtonGroup()
        et.addButton(self.uEllipseTypeCovariance,VectorFieldRenderer.CovarianceEllipse)
        et.addButton(self.uEllipseTypeAxes,VectorFieldRenderer.AxesEllipse)
        et.addButton(self.uEllipseTypeCircular,VectorFieldRenderer.CircularEllipse)
        et.addButton(self.uEllipseTypeHeight,VectorFieldRenderer.HeightEllipse)
        et.addButton(self.uEllipseTypeNone,VectorFieldRenderer.NoEllipse)
        et.buttonClicked[int].connect(self.setEllipseMode)
        self.ellipseTypeGroup = et
        
        self.uHelpButton.clicked.connect( self.showHelp )

    # event handlers

    def showHelp(self):
        VectorFieldRenderer.showHelp()

    def mode( self ):
        return self._mode

    def setMode(self,mode):
        if mode == VectorFieldRenderer.Height:
            self.uFieldTypeHeight.setChecked(True)
            fields=["Height attribute"]
        elif mode == VectorFieldRenderer.Polar:
            self.uFieldTypePolar.setChecked(True)
            fields=["Length attribute","Angle attribute"]
        elif mode == VectorFieldRenderer.NoArrow:
            self.uFieldTypeNone.setChecked(True)
            fields=[]
        else:
            self.uFieldTypeCartesian.setChecked(True)
            mode == VectorFieldRenderer.Cartesian
            fields=["X attribute","Y attribute"]
        self._mode = mode
        nfields=len(fields)
        self.uXField.setEnabled( nfields > 0 )
        self.uYField.setEnabled( nfields > 1 )
        self.uXFieldLabel.setText( fields[0] if nfields > 0 else '' )
        self.uYFieldLabel.setText( fields[1] if nfields > 1 else '' )
        if nfields < 1:
            self.uXField.setCurrentIndex(-1)
        if nfields < 2:
            self.uYField.setCurrentIndex(-1)
        isPolar = mode == VectorFieldRenderer.Polar
        self.uAngleUnitsGroupBox.setEnabled( isPolar )
        self.uOrientationGroupBox.setEnabled( isPolar )
        self.uArrowFormatGroup.setEnabled( mode != VectorFieldRenderer.NoArrow )

    def ellipseMode(self):
        return self._ellipseMode

    def setEllipseMode(self,mode):
        if mode == VectorFieldRenderer.HeightEllipse:
            self.uEllipseTypeHeight.setChecked(True)
            fields = ["Height error"]
        elif mode == VectorFieldRenderer.CircularEllipse:
            self.uEllipseTypeCircular.setChecked(True)
            fields = ["X/Y error"]
        elif mode == VectorFieldRenderer.AxesEllipse:
            self.uEllipseTypeAxes.setChecked(True)
            fields=["Semi-major axis","Semi-minor axis","Major axis orientation"]
        elif mode == VectorFieldRenderer.CovarianceEllipse:
            self.uEllipseTypeCovariance.setChecked(True)
            fields=["Cxx covariance","Cxy covariance","Cyy covariance"]
        else:
            self.uEllipseTypeNone.setChecked(True)
            mode == VectorFieldRenderer.NoEllipse
            fields = []

        self._ellipseMode = mode
        nfields = len(fields)
        self.uCxxField.setEnabled(nfields>0)
        self.uCxyField.setEnabled(nfields>1)
        self.uCyyField.setEnabled(nfields>2)
        self.uCxxFieldLabel.setText(fields[0] if nfields > 0 else '')
        self.uCxyFieldLabel.setText(fields[1] if nfields > 1 else '')
        self.uCyyFieldLabel.setText(fields[2] if nfields > 2 else '')
        if nfields < 1:
            self.uCxxField.setCurrentIndex(-1)
        if nfields < 2:
            self.uCxyField.setCurrentIndex(-1)
        if nfields < 3:
            self.uCyyField.setCurrentIndex(-1)

        isPolar = mode == VectorFieldRenderer.AxesEllipse
        self.uAxisAngleUnitsGroupBox.setEnabled( isPolar )
        self.uAxisOrientationGroupBox.setEnabled( isPolar )
        self.uEllipseFormatGroup.setEnabled( mode != VectorFieldRenderer.NoEllipse )
 
    def setupLayer( self, layer ):
        self.layer = layer
        self.uXField.clear()
        self.uYField.clear()
        self.uCxxField.clear()
        self.uCxyField.clear()
        self.uCyyField.clear()
        if layer:
           for f in self.getLayerFields(layer):
             self.uXField.addItem(f)
             self.uYField.addItem(f)
             self.uCxxField.addItem(f)
             self.uCxyField.addItem(f)
             self.uCyyField.addItem(f)
 
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
        self.setEllipseMode( vfr.ellipseMode())
        self.uXField.setCurrentIndex( self.uXField.findText(vfr.xFieldName()))
        self.uYField.setCurrentIndex( self.uYField.findText(vfr.yFieldName()))
        self.uCxxField.setCurrentIndex( self.uCxxField.findText(vfr.cxxFieldName()))
        self.uCxyField.setCurrentIndex( self.uCxyField.findText(vfr.cxyFieldName()))
        self.uCyyField.setCurrentIndex( self.uCyyField.findText(vfr.cyyFieldName()))
        self.uAngleUnitsDegrees.setChecked( vfr.degrees())
        self.uAngleUnitsRadians.setChecked( not vfr.degrees())
        self.uAngleOrientationNorth.setChecked( vfr.angleFromNorth())
        self.uAngleOrientationEast.setChecked( not vfr.angleFromNorth())
        self.uEllipseAngleUnitsDegrees.setChecked( vfr.ellipseDegrees())
        self.uEllipseAngleUnitsRadians.setChecked( not vfr.ellipseDegrees())
        self.uEllipseOrientationNorth.setChecked( vfr.ellipseAngleFromNorth())
        self.uEllipseOrientationEast.setChecked( not vfr.ellipseAngleFromNorth())
        self.scaleUnits.setIsMapUnit(vfr.useMapUnit())
        self.uArrowScale.setText( str(vfr.scale()))
        self.uEllipseScale.setText( str(vfr.ellipseScale()))
        group = vfr.scaleGroup()
        factor = vfr.scaleGroupFactor()
        if group and factor != 1.0:
           group = group + "*" + str(factor)
        self.uScaleGroup.setText(group)
        self.outputUnits.setUnits(vfr.outputUnit())
        arrow = vfr.arrow()
        self.uArrowHeadSize.setValue( arrow.relativeHeadSize())
        self.uArrowHeadMaxSize.setValue( arrow.maxHeadSize())
        self.uHeadWidth.setValue( arrow.headWidth())
        self.uFillHead.setChecked( arrow.fillHead())
        self.uArrowWidth.setValue( arrow.shaftWidth())
        self.uArrowBaseSize.setValue( arrow.baseSize())
        self.arrowColor.setColor( arrow.color())
        self.arrowHeadColor.setColor(arrow.headFillColor())
        self.baseColor.setColor( arrow.baseFillColor())
        shape = arrow.headShape()
        self.uArrowHeadShapeFront.setValue( shape[0] )
        self.uArrowHeadShapeBack.setValue( shape[1] )
        self.uArrowHeadShapeCentre.setValue( shape[2] )
        self.uFillBase.setChecked( arrow.fillBase())
        self.uDrawEllipse.setChecked( arrow.drawEllipse())
        self.uDrawEllipseAxes.setChecked( arrow.drawEllipseAxes())
        self.baseBorderColor.setColor( arrow.baseBorderColor())
        self.uEllipseBorderWidth.setValue( arrow.ellipseBorderWidth())
        self.uEllipseTickSize.setValue( arrow.ellipseTickSize())
        self.ellipseBorderColor.setColor( arrow.ellipseBorderColor())
        self.uFillEllipse.setChecked( arrow.fillEllipse())
        self.ellipseFillColor.setColor( arrow.ellipseFillColor())
        self.uLegendText.setText( vfr.legendText())
        self.uScaleBoxText.setText( vfr.scaleBoxText())
        self.uShowInScaleBox.setChecked( vfr.showInScaleBox())

    def saveToRenderer( self ):
        vfr = self.r
        # Avoid accidentally resetting scale group scale until we've
        # set the new scale group
        vfr.setScaleGroup("")
        vfr.setMode( self.mode())
        vfr.setEllipseMode( self.ellipseMode())
        vfr.setXFieldName( self.uXField.currentText())
        vfr.setYFieldName( self.uYField.currentText())
        vfr.setCxxFieldName( self.uCxxField.currentText())
        vfr.setCxyFieldName( self.uCxyField.currentText())
        vfr.setCyyFieldName( self.uCyyField.currentText())
        vfr.setDegrees( self.uAngleUnitsDegrees.isChecked())
        vfr.setAngleFromNorth(self.uAngleOrientationNorth.isChecked())
        vfr.setEllipseDegrees( self.uEllipseAngleUnitsDegrees.isChecked())
        vfr.setEllipseAngleFromNorth(self.uEllipseOrientationNorth.isChecked())
        try:
           vfr.setScale( float(self.uArrowScale.text()))
        except:
           pass
        try:
           vfr.setEllipseScale( float(self.uEllipseScale.text()))
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
        arrow.setRelativeHeadSize( self.uArrowHeadSize.value())
        arrow.setMaxHeadSize( self.uArrowHeadMaxSize.value())
        arrow.setShaftWidth( self.uArrowWidth.value())
        arrow.setHeadWidth( self.uHeadWidth.value())
        front = float(self.uArrowHeadShapeFront.value())
        back = float(self.uArrowHeadShapeBack.value())
        centre = float(self.uArrowHeadShapeCentre.value())
        arrow.setHeadShape( front, back, centre )
        arrow.setBaseSize( self.uArrowBaseSize.value())
        arrow.setColor( self.arrowColor.color())
        arrow.setHeadFillColor( self.arrowHeadColor.color())
        arrow.setFillBase( self.uFillBase.isChecked())
        arrow.setFillHead( self.uFillHead.isChecked())
        arrow.setDrawEllipse( self.uDrawEllipse.isChecked())
        arrow.setDrawEllipseAxes( self.uDrawEllipseAxes.isChecked())
        arrow.setBaseFillColor( self.baseColor.color())
        arrow.setBaseBorderColor( self.baseBorderColor.color())
        arrow.setEllipseBorderWidth( self.uEllipseBorderWidth.value())
        arrow.setEllipseTickSize( self.uEllipseTickSize.value())
        arrow.setEllipseBorderColor( self.ellipseBorderColor.color())
        arrow.setFillEllipse( self.uFillEllipse.isChecked())
        arrow.setEllipseFillColor( self.ellipseFillColor.color())
        vfr.setLegendText( self.uLegendText.text())
        vfr.setScaleBoxText( self.uScaleBoxText.text())
        vfr.setShowInScaleBox( self.uShowInScaleBox.isChecked())
    # TODO: Sort out error handling for scale field.. 
