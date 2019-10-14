import sys
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qgis.core import *
from qgis.gui import *

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
      self.setIsMapUnit( not self.isMapUnit())

# Vector field settings widget

class VectorFieldRendererWidget(Ui_VectorFieldRendererWidget):

    def __init__(self,layer,settings):
        self._controller=controller

        self._settings = VectorFieldLayerSettings() if settings is None else settings

        self._layer=layer
        self.validLayer = True
        if layer is None or layer.type() != QgsMapLayer.VectorLayer or layer.geometryType() != QgsWkbTypes.PointGeometry:
           self.setupBlankUi(layer)
           self.validLayer = False
           return

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
        self.uCxxField.setFilters(QgsFieldProxyModel.Numeric)
        self.uCxyField.setFilters(QgsFieldProxyModel.Numeric)
        self.uCyyField.setFilters(QgsFieldProxyModel.Numeric)
        self.uArrowColor.setColorDialogTitle('Arrow colour')
        self.uArrowHeadColor.setColorDialogTitle('Arrow head fill colour')
        self.uBaseColor.setColorDialogTitle('Base symbol line colour')
        self.uBaseBorderColor.setColorDialogTitle('Base symbol fill colour')
        # self.uEllipseBorderColor.setColorDialogTitle('Ellipse line colour')
        # self.uEllipseFillColor.setColorDialogTitle('Ellipse fill colour')

        self.scaleUnits = UnitButton(self.uScaleUnits,"Symbol unit")
        self.outputUnits = UnitButton(self.uOutputUnits)

        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uArrowScale.setValidator(QRegExpValidator(re,self))

        resg = QRegExp("(\\w+(\\*\\d+(\\.\\d*)?)?)?")
        self.uScaleGroup.setValidator(QRegExpValidator(resg,self))

        ft = QButtonGroup()
        ft.addButton(self.uFieldTypeCartesian,VectorFieldLayerSettings.Cartesian)
        ft.addButton(self.uFieldTypePolar,VectorFieldLayerSettings.Polar)
        ft.addButton(self.uFieldTypeHeight,VectorFieldLayerSettings.Height)
        ft.addButton(self.uFieldTypeNone,VectorFieldLayerSettings.NoArrow)
        ft.buttonClicked[int].connect(self.setMode)
        self.fieldTypeGroup = ft

        # et = QButtonGroup()
        # et.addButton(self.uEllipseTypeCovariance,VectorFieldLayerSettings.CovarianceEllipse)
        # et.addButton(self.uEllipseTypeAxes,VectorFieldLayerSettings.AxesEllipse)
        # et.addButton(self.uEllipseTypeCircular,VectorFieldLayerSettings.CircularEllipse)
        # et.addButton(self.uEllipseTypeHeight,VectorFieldLayerSettings.HeightEllipse)
        # et.addButton(self.uEllipseTypeNone,VectorFieldLayerSettings.NoEllipse)
        # et.buttonClicked[int].connect(self.setEllipseMode)
        # self.ellipseTypeGroup = et
        
        self.uHelpButton.clicked.connect( self.showHelp )

    # event handlers

    def showHelp(self):
        pass
        # VectorFieldLayerSettings.showHelp()

    def mode( self ):
        return self._mode

    def setMode(self,mode):
        if mode == VectorFieldLayerSettings.Height:
            self.uFieldTypeHeight.setChecked(True)
            fields=["Height attribute"]
        elif mode == VectorFieldLayerSettings.Polar:
            self.uFieldTypePolar.setChecked(True)
            fields=["Length attribute","Angle attribute"]
        elif mode == VectorFieldLayerSettings.NoArrow:
            self.uFieldTypeNone.setChecked(True)
            fields=[]
        else:
            self.uFieldTypeCartesian.setChecked(True)
            mode == VectorFieldLayerSettings.Cartesian
            fields=["X attribute","Y attribute"]
        self._mode = mode
        nfields=len(fields)
        self.uXField.setEnabled( nfields > 0 )
        self.uYField.setEnabled( nfields > 1 )
        self.uXFieldLabel.setText( fields[0] if nfields > 0 else '' )
        self.uYFieldLabel.setText( fields[1] if nfields > 1 else '' )
        self.uXField.setExpressionDialogTitle( fields[0] if nfields > 0 else '' )
        self.uYField.setExpressionDialogTitle( fields[1] if nfields > 1 else '' )
        if nfields < 1:
            self.uXField.setField("")
        if nfields < 2:
            self.uYField.setField("")
        isPolar = mode == VectorFieldLayerSettings.Polar
        self.uAngleUnitsGroupBox.setEnabled( isPolar )
        self.uOrientationGroupBox.setEnabled( isPolar )
        self.uArrowFormatGroup.setEnabled( mode != VectorFieldLayerSettings.NoArrow )

    # def ellipseMode(self):
    #     return self._ellipseMode

    # def setEllipseMode(self,mode):
    #     if mode == VectorFieldLayerSettings.HeightEllipse:
    #         self.uEllipseTypeHeight.setChecked(True)
    #         fields = ["Height error"]
    #     elif mode == VectorFieldLayerSettings.CircularEllipse:
    #         self.uEllipseTypeCircular.setChecked(True)
    #         fields = ["X/Y error"]
    #     elif mode == VectorFieldLayerSettings.AxesEllipse:
    #         self.uEllipseTypeAxes.setChecked(True)
    #         fields=["Semi-major axis","Semi-minor axis","Major axis orientation"]
    #     elif mode == VectorFieldLayerSettings.CovarianceEllipse:
    #         self.uEllipseTypeCovariance.setChecked(True)
    #         fields=["Cxx covariance","Cxy covariance","Cyy covariance"]
    #     else:
    #         self.uEllipseTypeNone.setChecked(True)
    #         mode == VectorFieldLayerSettings.NoEllipse
    #         fields = []

    #     self._ellipseMode = mode
    #     nfields = len(fields)
    #     self.uCxxField.setEnabled(nfields>0)
    #     self.uCxyField.setEnabled(nfields>1)
    #     self.uCyyField.setEnabled(nfields>2)
    #     self.uCxxFieldLabel.setText(fields[0] if nfields > 0 else '')
    #     self.uCxyFieldLabel.setText(fields[1] if nfields > 1 else '')
    #     self.uCyyFieldLabel.setText(fields[2] if nfields > 2 else '')
    #     self.uCxxField.setExpressionDialogTitle(fields[0] if nfields > 0 else '')
    #     self.uCxyField.setExpressionDialogTitle(fields[1] if nfields > 1 else '')
    #     self.uCyyField.setExpressionDialogTitle(fields[2] if nfields > 2 else '')
    #     if nfields < 1:
    #         self.uCxxField.setField("")
    #     if nfields < 2:
    #         self.uCxyField.setField("")
    #     if nfields < 3:
    #         self.uCyyField.setField("")

    #     isPolar = mode == VectorFieldLayerSettings.AxesEllipse
    #     self.uAxisAngleUnitsGroupBox.setEnabled( isPolar )
    #     self.uAxisOrientationGroupBox.setEnabled( isPolar )
    #     self.uEllipseFormatGroup.setEnabled( mode != VectorFieldLayerSettings.NoEllipse )
 
    def setupLayer( self, layer ):
        self.layer = layer
        self.uXField.setLayer(layer)
        self.uYField.setLayer(layer)
        # self.uCxxField.setLayer(layer)
        # self.uCxyField.setLayer(layer)
        # self.uCyyField.setLayer(layer)
 
    def settings(self):
        if self.validLayer:
            self.saveToSettings()
            self._controller.saveLayerRenderer( self._layer, self._settings )
            # self._controller.repaintScaleBox()
        return self._settings

    def applyRenderer( self ):
        if self.validLayer:
            settings=self.settings()
            settings.applyToLayer(self._layer)
  
    def loadFromSettings( self ):
        vfr = self._settings
        self.setMode( vfr.mode())
        self.setEllipseMode( vfr.ellipseMode())
        self.uXField.setField( vfr.xFieldName())
        self.uYField.setField( vfr.yFieldName())
        self.uCxxField.setField( vfr.cxxFieldName())
        self.uCxyField.setField( vfr.cxyFieldName())
        self.uCyyField.setField( vfr.cyyFieldName())
        self.uAngleUnitsDegrees.setChecked( vfr.degrees())
        self.uAngleUnitsRadians.setChecked( not vfr.degrees())
        self.uAngleOrientationNorth.setChecked( vfr.angleFromNorth())
        self.uAngleOrientationEast.setChecked( not vfr.angleFromNorth())
        self.uEllipseAngleUnitsDegrees.setChecked( vfr.ellipseDegrees())
        self.uEllipseAngleUnitsRadians.setChecked( not vfr.ellipseDegrees())
        self.uEllipseOrientationNorth.setChecked( vfr.ellipseAngleFromNorth())
        self.uEllipseOrientationEast.setChecked( not vfr.ellipseAngleFromNorth())
        self.scaleUnits.setIsMapUnit(vfr.useMapUnit())
        self.uVectorIsTrueNorth.setChecked(vfr.vectorIsTrueNorth())
        self.uAlignToMapNorth.setChecked(vfr.useMapNorth())
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
        self.uArrowColor.setColor( arrow.color())
        self.uArrowHeadColor.setColor(arrow.headFillColor())
        self.uBaseColor.setColor( arrow.baseFillColor())
        shape = arrow.headShape()
        self.uArrowHeadShapeFront.setValue( shape[0] )
        self.uArrowHeadShapeBack.setValue( shape[1] )
        self.uArrowHeadShapeCentre.setValue( shape[2] )
        self.uFillBase.setChecked( arrow.fillBase())
        # self.uDrawEllipse.setChecked( arrow.drawEllipse())
        # self.uDrawEllipseAxes.setChecked( arrow.drawEllipseAxes())
        # self.uBaseBorderColor.setColor( arrow.baseBorderColor())
        # self.uEllipseBorderWidth.setValue( arrow.ellipseBorderWidth())
        # self.uEllipseTickSize.setValue( arrow.ellipseTickSize())
        # self.uEllipseBorderColor.setColor( arrow.ellipseBorderColor())
        # self.uFillEllipse.setChecked( arrow.fillEllipse())
        # self.uEllipseFillColor.setColor( arrow.ellipseFillColor())
        # self.uLegendText.setText( vfr.legendText())
        # self.uScaleBoxText.setText( vfr.scaleBoxText())
        # self.uShowInScaleBox.setChecked( vfr.showInScaleBox())

    def saveToSettings( self ):
        vfr = self._settings
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
        vfr.setVectorIsTrueNorth(self.uVectorIsTrueNorth.isChecked())
        vfr.setUseMapNorth(self.uAlignToMapNorth.isChecked())
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
        arrow.setColor( self.uArrowColor.color())
        arrow.setHeadFillColor( self.uArrowHeadColor.color())
        arrow.setFillBase( self.uFillBase.isChecked())
        arrow.setFillHead( self.uFillHead.isChecked())
        arrow.setDrawEllipse( self.uDrawEllipse.isChecked())
        arrow.setDrawEllipseAxes( self.uDrawEllipseAxes.isChecked())
        arrow.setBaseFillColor( self.uBaseColor.color())
        arrow.setBaseBorderColor( self.uBaseBorderColor.color())
        arrow.setEllipseBorderWidth( self.uEllipseBorderWidth.value())
        arrow.setEllipseTickSize( self.uEllipseTickSize.value())
        arrow.setEllipseBorderColor( self.uEllipseBorderColor.color())
        arrow.setFillEllipse( self.uFillEllipse.isChecked())
        arrow.setEllipseFillColor( self.uEllipseFillColor.color())
        vfr.setLegendText( self.uLegendText.text())
        vfr.setScaleBoxText( self.uScaleBoxText.text())
        vfr.setShowInScaleBox( self.uShowInScaleBox.isChecked())
    # TODO: Sort out error handling for scale field.. 
