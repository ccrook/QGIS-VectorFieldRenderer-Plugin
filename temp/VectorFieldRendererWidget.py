import sys
#from PyQt5.QtWidgets import *

from PyQt5.QtCore import (
    QButtonGroup,
    QLabel,
    QObject,
    QRegExp,
    QRegExpValidator,
    QVBoxLayout,
    QWidget
    )
from PyQt5.QtGui import *

from qgis.core import (
    QgsFieldProxyModel,
    QgsMapLayer,
    QgsUnitTypes,
    QgsVectorFieldSymbolLayer,
    QgsWkbTypes
    )
#from qgis.gui import ()

from .VectorFieldLayerSettings import VectorFieldLayerSettings
from .Ui_VectorFieldRendererWidget import Ui_VectorFieldRendererWidget


class UnitButton( QObject ):

   valueChanged = pyqtSignal(name='valueChanged')

   def __init__(self,button,mmtext="Millimetres"):
      QObject.__init__(self)
      self._button = button
      self._mmLabel = mmtext
      self.setUnits(QgsUnitTypes.RenderMillimeters)
      button.clicked.connect(self.clicked)

   def units(self):
      return self._units

   def setUnits(self,units):
      if units == QgsUnitTypes.RenderMillimeters:
         self._units = QgsUnitTypes.RenderMillimeters
         self._button.setText(self._mmLabel)
      else:
         self._units = QgsUnitTypes.RenderMapUnits
         self._button.setText("Map units")

   def isMapUnit( self ):
       return self._units == QgsUnitTypes.RenderMapUnits

   def setIsMapUnit( self, isMapUnits ):
      if isMapUnits:
          self.setUnits(QgsUnitTypes.RenderMapUnits)
      else:
          self.setUnits(QgsUnitTypes.RenderMillimeters)
      self.valueChanged.emit()

   def clicked(self):
      self.setIsMapUnit( not self.isMapUnit())-

# Vector field settings widget

class VectorFieldRendererWidget(QWidget, Ui_VectorFieldRendererWidget):

    def __init__(self,layer):
        QWidget.__init__( self )
        self._controller=controller

        self._layer=layer
        self.validLayer = True
        if layer is None or layer.type() != QgsMapLayer.VectorLayer or layer.geometryType() != QgsWkbTypes.PointGeometry:
           self.setupBlankUi(layer)
           self.validLayer = False
           return

        self._settings = VectorFieldLayerSettings()
        self._settings.readFromLayer(layer)
        
        # Hide fields not used in current implementation
        self.uArrowFormatLayout.hide()
        self.uVectorLegendFieldsLayout.hide()
        self.uEllipseTypeCovariance.hide()
        self.uTickSizeLabel.hide()
        self.uDrawEllipse.hide()
        self.uDrawEllipseAxes.hide()
        self.uVectorAlignmentLayout.hide()

        self._mode = VectorFieldLayerSettings.Cartesian
        self._ellipsemode = VectorFieldLayerSettings.NoEllipse
        self.buildWidget()
        self.setupLayer(layer)
        self.loadFromSettings()
        # Try creating a new settings to save to ...
        self._settings=VectorFieldLayerSettings()

    def setupBlankUi(self,layer):
        name = layer.name() if layer else "Selected layer"
        self.uLayout = QVBoxLayout()
        self.uLabel = QLabel(
              "The vector field settings only applies to point type layers.\n\n"
              +name+" is not a point layer, and cannot be displayed by the vector field settings.\n\n"
              )
        self.uLayout.addWidget(self.uLabel)
        self.setLayout(self.uLayout)

    def buildWidget(self):
        self.setupUi(self)
        self.uXField.setFilters(QgsFieldProxyModel.Numeric)
        self.uYField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEmaxField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEminField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEmaxAzimuthField.setFilters(QgsFieldProxyModel.Numeric)
        self.uArrowColor.setColorDialogTitle('Arrow colour')
        self.uArrowHeadColor.setColorDialogTitle('Arrow head fill colour')
        self.uBaseColor.setColorDialogTitle('Base symbol line colour')
        self.uBaseBorderColor.setColorDialogTitle('Base symbol fill colour')
        self.uEllipseBorderColor.setColorDialogTitle('Ellipse line colour')
        self.uEllipseFillColor.setColorDialogTitle('Ellipse fill colour')

        self.scaleUnits = UnitButton(self.uScaleUnits,"Symbol unit")
        self.symbolUnits = UnitButton(self.uSymbolUnits)

        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uArrowScale.setValidator(QRegExpValidator(re,self))

        resg = QRegExp("(\\w+(\\*\\d+(\\.\\d*)?)?)?")
        self.uScaleGroup.setValidator(QRegExpValidator(resg,self))

        ft = QButtonGroup()
        ft.addButton(self.uFieldTypeCartesian,QgsVectorFieldSymbolLayer.Cartesian)
        ft.addButton(self.uFieldTypePolar,QgsVectorFieldSymbolLayer.Polar)
        ft.addButton(self.uFieldTypeHeight,QgsVectorFieldSymbolLayer.Height)
        ft.addButton(self.uFieldTypeNone,QgsVectorFieldSymbolLayer.NoArrow)
        ft.buttonClicked[int].connect(self.setMode)
        self.fieldTypeGroup = ft

        et = QButtonGroup()
        et.addButton(self.uEllipseTypeCovariance,VectorFieldLayerSettings.CovarianceEllipse)
        et.addButton(self.uEllipseTypeAxes,VectorFieldLayerSettings.AxesEllipse)
        et.addButton(self.uEllipseTypeCircular,VectorFieldLayerSettings.CircularEllipse)
        et.addButton(self.uEllipseTypeHeight,VectorFieldLayerSettings.HeightEllipse)
        et.addButton(self.uEllipseTypeNone,VectorFieldLayerSettings.NoEllipse)
        et.buttonClicked[int].connect(self.setEllipseMode)
        self.ellipseTypeGroup = et
        
        #self.uHelpButton.clicked.connect( self.showHelp )

    # event handlers

    def showHelp(self):
        pass
        # VectorFieldLayerSettings.showHelp()

    def mode( self ):
        return self._mode

    def setMode(self,mode):
        if mode == QgsVectorFieldSymbolLayer.Height:
            self.uFieldTypeHeight.setChecked(True)
            fields=["Height attribute"]
        elif mode == QgsVectorFieldSymbolLayer.Polar:
            self.uFieldTypePolar.setChecked(True)
            fields=["Length attribute","Angle attribute"]
        elif mode == QgsVectorFieldSymbolLayer.NoArrow:
            self.uFieldTypeNone.setChecked(True)
            fields=[]
        else:
            self.uFieldTypeCartesian.setChecked(True)
            mode == QgsVectorFieldSymbolLayer.Cartesian
            fields=["X attribute","Y attribute"]
        self._mode = mode
        nfields=len(fields)
        self.uXField.setEnabled( nfields > 0 )
        self.uYField.setEnabled( nfields > 1 )
        self.uXFieldLabel.setText( fields[0] if nfields > 0 else '' )
        self.uYFieldLabel.setText( fields[1] if nfields > 1 else '' )
        # self.uXField.setExpressionDialogTitle( fields[0] if nfields > 0 else '' )
        # self.uYField.setExpressionDialogTitle( fields[1] if nfields > 1 else '' )
        if nfields < 1:
            self.uXField.setField("")
        if nfields < 2:
            self.uYField.setField("")
        isPolar = mode == QgsVectorFieldSymbolLayer.Polar
        self.uAngleUnitsGroupBox.setEnabled( isPolar )
        self.uOrientationGroupBox.setEnabled( isPolar )
        self.uArrowFormatGroup.setEnabled( mode != QgsVectorFieldSymbolLayer.NoArrow )

    def ellipseMode(self):
        return self._ellipseMode

    def setEllipseMode(self,mode):
        if mode == VectorFieldLayerSettings.HeightEllipse:
            self.uEllipseTypeHeight.setChecked(True)
            fields = ["Height error"]
        elif mode == VectorFieldLayerSettings.CircularEllipse:
            self.uEllipseTypeCircular.setChecked(True)
            fields = ["X/Y error"]
        elif mode == VectorFieldLayerSettings.AxesEllipse:
            self.uEllipseTypeAxes.setChecked(True)
            fields=["Semi-major axis","Semi-minor axis","Major axis orientation"]
        elif mode == VectorFieldLayerSettings.CovarianceEllipse:
            self.uEllipseTypeCovariance.setChecked(True)
            fields=["Emax covariance","Emin covariance","EmaxAzimuth covariance"]
        else:
            self.uEllipseTypeNone.setChecked(True)
            mode == VectorFieldLayerSettings.NoEllipse
            fields = []

        self._ellipseMode = mode
        nfields = len(fields)
        self.uEmaxField.setEnabled(nfields>0)
        self.uEminField.setEnabled(nfields>1)
        self.uEmaxAzimuthField.setEnabled(nfields>2)
        self.uEmaxFieldLabel.setText(fields[0] if nfields > 0 else '')
        self.uEminFieldLabel.setText(fields[1] if nfields > 1 else '')
        self.uEmaxAzimuthFieldLabel.setText(fields[2] if nfields > 2 else '')
        self.uEmaxField.setExpressionDialogTitle(fields[0] if nfields > 0 else '')
        self.uEminField.setExpressionDialogTitle(fields[1] if nfields > 1 else '')
        self.uEmaxAzimuthField.setExpressionDialogTitle(fields[2] if nfields > 2 else '')
        if nfields < 1:
            self.uEmaxField.setField("")
        if nfields < 2:
            self.uEminField.setField("")
        if nfields < 3:
            self.uEmaxAzimuthField.setField("")

        isPolar = mode == VectorFieldLayerSettings.AxesEllipse
        self.uAxisAngleUnitsGroupBox.setEnabled( isPolar )
        self.uAxisOrientationGroupBox.setEnabled( isPolar )
        self.uEllipseFormatGroup.setEnabled( mode != VectorFieldLayerSettings.NoEllipse )
 
    def setupLayer( self, layer ):
        self.layer = layer
        self.uXField.setLayer(layer)
        self.uYField.setLayer(layer)
        self.uEmaxField.setLayer(layer)
        self.uEminField.setLayer(layer)
        self.uEmaxAzimuthField.setLayer(layer)
 
    def settings(self):
        if self.validLayer:
            self.saveToSettings()
        return self._settings

    def applyToLayer( self ):
        if self.validLayer:
            settings=self.settings()
            settings.applyToLayer(self._layer)
  
    def loadFromSettings( self ):
        settings = self._settings
        self.setMode( settings.mode())
        self.setEllipseMode( settings.ellipseMode())
        self.uXField.setField( settings.dxField())
        self.uYField.setField( settings.dyField())
        self.uEmaxField.setField( settings.emaxField())
        self.uEminField.setField( settings.eminField())
        self.uEmaxAzimuthField.setField( settings.emaxAzimuthField())
        self.uAngleUnitsDegrees.setChecked( settings.degrees())
        self.uAngleUnitsRadians.setChecked( not settings.degrees())
        self.uAngleOrientationNorth.setChecked( settings.angleOrientation() == QgsVectorFieldSymbolLayer.ClockwiseFromNorth)
        self.uAngleOrientationEast.setChecked( settings.angleOrientation() != QgsVectorFieldSymbolLayer.ClockwiseFromNorth)
        self.uEllipseAngleUnitsDegrees.setChecked( settings.ellipseDegrees())
        self.uEllipseAngleUnitsRadians.setChecked( not settings.ellipseDegrees())
        self.uEllipseOrientationNorth.setChecked( settings.ellipseAngleFromNorth())
        self.uEllipseOrientationEast.setChecked( not settings.ellipseAngleFromNorth())
        self.scaleUnits.setUnits(settings.scaleUnitType())
        # self.uVectorIsTrueNorth.setChecked(settings.vectorIsTrueNorth())
        # self.uAlignToMapNorth.setChecked(settings.useMapNorth())
        # self.uArrowScale.setText( str(settings.scale()))
        self.uEllipseScale.setText( str(settings.ellipseScale()))
        group = settings.scaleGroup()
        factor = settings.scaleGroupFactor()
        if group and factor != 1.0:
           group = group + "*" + str(factor)
        self.uScaleGroup.setText(group)
        self.symbolUnits.setUnits(settings.symbolUnitType())
        self.uArrowHeadSize.setValue( settings.arrowRelativeHeadSize())
        self.uArrowHeadMaxSize.setValue( settings.arrowMaxHeadSize())
        self.uArrowShaftWidth.setValue( settings.arrowShaftSize())
        self.uArrowBorderWidth.setValue( settings.arrowBorderWidth())
        self.uFillArrow.setChecked( settings.fillArrow())
        self.uArrowBaseSize.setValue( settings.baseSize())
        self.uArrowFillColor.setColor( settings.arrowFillColor())
        self.uArrowBorderColor.setColor(settings.arrowBorderColor())
        self.uBaseColor.setColor( settings.baseFillColor())
        self.uArrowHeadShapeFront.setValue( settings.arrowHeadShapeFront )
        self.uArrowHeadShapeBack.setValue( settings.arrowHeadShapeBackOuter )
        self.uArrowHeadShapeCentre.setValue( settings.arrowHeadShapeBackInner )
        self.uFillBase.setChecked( settings.fillBase())
        self.uDrawEllipse.setChecked( settings.drawEllipse())
        self.uDrawEllipseAxes.setChecked( settings.drawEllipseAxes())
        self.uBaseBorderColor.setColor( settings.baseBorderColor())
        self.uEllipseBorderWidth.setValue( settings.ellipseBorderWidth())
        self.uEllipseTickSize.setValue( settings.ellipseTickSize())
        self.uEllipseBorderColor.setColor( settings.ellipseBorderColor())
        self.uFillEllipse.setChecked( settings.fillEllipse())
        self.uEllipseFillColor.setColor( settings.ellipseFillColor())
        # self.uLegendText.setText( settings.legendText())
        # self.uScaleBoxText.setText( settings.scaleBoxText())
        # self.uShowInScaleBox.setChecked( settings.showInScaleBox())

    def saveToSettings( self ):
        settings = self._settings
        # Avoid accidentally resetting scale group scale until we've
        # set the new scale group
        settings.setScaleGroup("")
        settings.setMode( self.mode())
        settings.setEllipseMode( self.ellipseMode())
        settings.setDxField( self.uXField.currentText())
        settings.setDyField( self.uYField.currentText())
        settings.setEmaxField( self.uEmaxField.currentText())
        settings.setEminField( self.uEminField.currentText())
        settings.setEmaxAzimuthField( self.uEmaxAzimuthField.currentText())
        settings.setDegrees( self.uAngleUnitsDegrees.isChecked())
        settings.setAngleOrientation(QgsVectorFieldSymbolLayer.ClockwiseFromNorth if self.uAngleOrientationNorth.isChecked() else QgsVectorFieldSymbolLayer.ClockwiseFromEast)
        settings.setEllipseDegrees( self.uEllipseAngleUnitsDegrees.isChecked())
        settings.setEllipseAngleFromNorth(self.uEllipseOrientationNorth.isChecked())
        try:
           settings.setScale( float(self.uArrowScale.text()))
        except:
           pass
        try:
           settings.setEllipseScale( float(self.uEllipseScale.text()))
        except:
           pass
        # settings.setUseMapUnit( self.scaleUnits.isMapUnit())
        # settings.setVectorIsTrueNorth(self.uVectorIsTrueNorth.isChecked())
        # settings.setUseMapNorth(self.uAlignToMapNorth.isChecked())
        group = self.uScaleGroup.text()
        factor = 1.0
        if "*" in group:
            group,f = group.split("*")
            try:
               factor = float(f)
            except:
               pass
        settings.setScaleGroupFactor(factor)
        settings.setScaleGroup(group)
        settings.setScaleUnitType(self.scaleUnits.units())
        settings.setSymbolUnitType(self.symbolUnits.units())
        settings.setArrowRelativeHeadSize( self.uArrowHeadSize.value())
        settings.setArrowMaxHeadSize( self.uArrowHeadMaxSize.value())
        settings.setArrowShaftSize( self.uArrowShaftWidth.value())
        settings.setArrowBorderWidth( self.uArrowBorderWidth.value())
        settings.setArrowHeadShapeFront( float(self.uArrowHeadShapeFront.value()))
        settings.setArrowHeadShapeBackOuter( float(self.uArrowHeadShapeBack.value()))
        settings.setArrowHeadShapeBackInner( float(self.uArrowHeadShapeCentre.value()))
        settings.setBaseSize( self.uArrowBaseSize.value())
        settings.setArrowBorderColor( self.uArrowBorderColor.color())
        settings.setArrowFillColor( self.uArrowFillColor.color())
        settings.setFillBase( self.uFillBase.isChecked())
        settings.setFillArrow( self.uFillArrow.isChecked())
        settings.setDrawEllipse( self.uDrawEllipse.isChecked())
        settings.setDrawEllipseAxes( self.uDrawEllipseAxes.isChecked())
        settings.setBaseFillColor( self.uBaseColor.color())
        settings.setBaseBorderColor( self.uBaseBorderColor.color())
        settings.setEllipseBorderWidth( self.uEllipseBorderWidth.value())
        settings.setEllipseTickSize( self.uEllipseTickSize.value())
        settings.setEllipseBorderColor( self.uEllipseBorderColor.color())
        settings.setFillEllipse( self.uFillEllipse.isChecked())
        settings.setEllipseFillColor( self.uEllipseFillColor.color())
        # settings.setLegendText( self.uLegendText.text())
        # settings.setScaleBoxText( self.uScaleBoxText.text())
        # settings.setShowInScaleBox( self.uShowInScaleBox.isChecked())
    # TODO: Sort out error handling for scale field.. 
