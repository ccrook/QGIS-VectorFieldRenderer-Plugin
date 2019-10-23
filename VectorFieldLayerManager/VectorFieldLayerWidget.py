import sys

from PyQt5.QtCore import QObject, QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QButtonGroup, QLabel, QVBoxLayout, QWidget

from qgis.core import QgsFieldProxyModel, QgsUnitTypes, QgsVectorFieldSymbolLayer

from .VectorFieldLayerSettings import VectorFieldLayerSettings
from .Ui_VectorFieldLayerWidget import Ui_VectorFieldLayerWidget

SymbolRenderUnitList = [
    QgsUnitTypes.RenderMillimeters,
    QgsUnitTypes.RenderMapUnits,
    QgsUnitTypes.RenderPixels,
    QgsUnitTypes.RenderPercentage,
    QgsUnitTypes.RenderPoints,
    QgsUnitTypes.RenderInches,
    QgsUnitTypes.RenderUnknownUnit,
    QgsUnitTypes.RenderMetersInMapUnits,
]

# Vector field settings widget


class VectorFieldLayerWidget(QWidget, Ui_VectorFieldLayerWidget):

    ArrowTypeNone = 999

    def __init__(self, controller, layer):
        QWidget.__init__(self)
        self._controller = controller
        self._settings = VectorFieldLayerSettings()
        self._originalSettings = VectorFieldLayerSettings()

        self._mode = QgsVectorFieldSymbolLayer.Cartesian
        self._ellipseMode = VectorFieldLayerSettings.NoEllipse
        self._layer = None
        self._layerId = ""
        self._validLayer = False
        self.buildWidget()

        # Hide fields not used in current implementation
        self.uVectorLegendFieldsFrame.hide()
        self.uEllipseTypeCovariance.hide()
        self.uVectorFieldAlignmentFrame.hide()

        # Install information from layer

        self.setLayer(layer)
        self.setLayerScale(layer)
        self._controller.vectorFieldLayerScaleChanged.connect(self.setLayerScale)

    def buildWidget(self):
        self.setupUi(self)
        self.uXField.setFilters(QgsFieldProxyModel.Numeric)
        self.uYField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEmaxField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEminField.setFilters(QgsFieldProxyModel.Numeric)
        self.uEmaxAzimuthField.setFilters(QgsFieldProxyModel.Numeric)
        self.uArrowBorderColor.setColorDialogTitle("Arrow border colour")
        self.uArrowFillColor.setColorDialogTitle("Arrow fill colour")
        self.uBaseColor.setColorDialogTitle("Base symbol line colour")
        self.uBaseBorderColor.setColorDialogTitle("Base symbol fill colour")
        self.uEllipseBorderColor.setColorDialogTitle("Ellipse line colour")
        self.uEllipseFillColor.setColorDialogTitle("Ellipse fill colour")
        for unit in SymbolRenderUnitList:
            unitName = QgsUnitTypes.toString(unit)
            self.uSymbolUnits.addItem(unitName, unit)
        self.uScaleUnits.addItem("Symbol unit")
        self.uScaleUnits.addItem("Map meters")

        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uArrowScale.setValidator(QRegExpValidator(re, self))

        resg = QRegExp("(\\w+(\\*\\d+(\\.\\d*)?)?)?")
        self.uScaleGroup.setValidator(QRegExpValidator(resg, self))

        ft = QButtonGroup()
        ft.addButton(self.uFieldTypeCartesian, QgsVectorFieldSymbolLayer.Cartesian)
        ft.addButton(self.uFieldTypePolar, QgsVectorFieldSymbolLayer.Polar)
        ft.addButton(self.uFieldTypeHeight, QgsVectorFieldSymbolLayer.Height)
        ft.addButton(self.uFieldTypeNone, self.ArrowTypeNone)
        ft.buttonClicked[int].connect(self.setMode)
        self.fieldTypeGroup = ft

        et = QButtonGroup()
        et.addButton(self.uEllipseTypeCovariance, VectorFieldLayerSettings.CovarianceEllipse)
        et.addButton(self.uEllipseTypeAxes, VectorFieldLayerSettings.AxesEllipse)
        et.addButton(self.uEllipseTypeCircular, VectorFieldLayerSettings.CircularEllipse)
        et.addButton(self.uEllipseTypeHeight, VectorFieldLayerSettings.HeightEllipse)
        et.addButton(self.uEllipseTypeNone, VectorFieldLayerSettings.NoEllipse)
        et.buttonClicked[int].connect(self.setEllipseMode)
        self.ellipseTypeGroup = et

        # self.uHelpButton.clicked.connect( self.showHelp )

    # event handlers

    def showHelp(self):
        pass
        # VectorFieldLayerSettings.showHelp()

    def mode(self):
        return self._mode

    def setMode(self, mode):
        if mode == QgsVectorFieldSymbolLayer.Height:
            self.uFieldTypeHeight.setChecked(True)
            fields = ["Height attribute"]
        elif mode == QgsVectorFieldSymbolLayer.Polar:
            self.uFieldTypePolar.setChecked(True)
            fields = ["Length attribute", "Angle attribute"]
        elif mode == self.ArrowTypeNone:
            self.uFieldTypeNone.setChecked(True)
            fields = []
        else:
            self.uFieldTypeCartesian.setChecked(True)
            mode == QgsVectorFieldSymbolLayer.Cartesian
            fields = ["X attribute", "Y attribute"]
        self._mode = mode
        nfields = len(fields)
        self.uXField.setEnabled(nfields > 0)
        self.uYField.setEnabled(nfields > 1)
        self.uXFieldLabel.setText(fields[0] if nfields > 0 else "")
        self.uYFieldLabel.setText(fields[1] if nfields > 1 else "")
        # self.uXField.setExpressionDialogTitle( fields[0] if nfields > 0 else '' )
        # self.uYField.setExpressionDialogTitle( fields[1] if nfields > 1 else '' )
        if nfields < 1:
            self.uXField.setField("")
        if nfields < 2:
            self.uYField.setField("")
        isPolar = mode == QgsVectorFieldSymbolLayer.Polar
        self.uAngleUnitsGroupBox.setEnabled(isPolar)
        self.uOrientationGroupBox.setEnabled(isPolar)
        # self.uArrowFormatGroup.setEnabled(mode != QgsVectorFieldSymbolLayer.NoArrow)

    def ellipseMode(self):
        return self._ellipseMode

    def setEllipseMode(self, mode):
        if mode == VectorFieldLayerSettings.HeightEllipse:
            self.uEllipseTypeHeight.setChecked(True)
            fields = ["Height error"]
        elif mode == VectorFieldLayerSettings.CircularEllipse:
            self.uEllipseTypeCircular.setChecked(True)
            fields = ["X/Y error"]
        elif mode == VectorFieldLayerSettings.AxesEllipse:
            self.uEllipseTypeAxes.setChecked(True)
            fields = ["Semi-major axis", "Semi-minor axis", "Major axis orientation"]
        elif mode == VectorFieldLayerSettings.CovarianceEllipse:
            self.uEllipseTypeCovariance.setChecked(True)
            fields = ["Emax covariance", "Emin covariance", "EmaxAzimuth covariance"]
        else:
            self.uEllipseTypeNone.setChecked(True)
            mode == VectorFieldLayerSettings.NoEllipse
            fields = []

        self._ellipseMode = mode
        nfields = len(fields)
        self.uEmaxField.setEnabled(nfields > 0)
        self.uEminField.setEnabled(nfields > 1)
        self.uEmaxAzimuthField.setEnabled(nfields > 2)
        self.uEmaxFieldLabel.setText(fields[0] if nfields > 0 else "")
        self.uEminFieldLabel.setText(fields[1] if nfields > 1 else "")
        self.uEmaxAzimuthFieldLabel.setText(fields[2] if nfields > 2 else "")
        # self.uEmaxField.setExpressionDialogTitle(fields[0] if nfields > 0 else "")
        # self.uEminField.setExpressionDialogTitle(fields[1] if nfields > 1 else "")
        # self.uEmaxAzimuthField.setExpressionDialogTitle(fields[2] if nfields > 2 else "")
        if nfields < 1:
            self.uEmaxField.setField("")
        if nfields < 2:
            self.uEminField.setField("")
        if nfields < 3:
            self.uEmaxAzimuthField.setField("")

        isPolar = mode == VectorFieldLayerSettings.AxesEllipse
        self.uAxisAngleUnitsGroupBox.setEnabled(isPolar)
        self.uAxisOrientationGroupBox.setEnabled(isPolar)
        self.uEllipseFormatGroup.setEnabled(mode != VectorFieldLayerSettings.NoEllipse)
        self.uEllipseTickSize.setEnabled(mode == VectorFieldLayerSettings.HeightEllipse)

    def layer(self):
        return self._layer

    def layerRemoved(self, layerid):
        if layerid == self._layerId:
            self.setLayer(None)

    def setLayerScale(self, layer):
        if self._layer is not None and layer is not None and layer.id() == self._layerId:
            scale = self._controller.vectorFieldLayerScale(self._layer)
            if scale is not None:
                self.uArrowScale.setText(str(scale))
            self._originalSettings.setScale(scale)

    def setLayer(self, layer):
        if not self._controller.isValidLayerType(layer):
            if layer is None:
                self.uLayerName.setText("No layer selected")
            else:
                self.uLayerName.setText(layer.name() + " is not a point layer")
            self.setEnabled(False)
            self._layer = None
            self._layerId = ""
            self._validLayer = False
            return
        self.setEnabled(True)
        self.uLayerName.setText("Layer: " + layer.name())
        self._validLayer = True
        self._layer = layer
        self._layerId = layer.id()
        self.uXField.setLayer(layer)
        self.uYField.setLayer(layer)
        self.uEmaxField.setLayer(layer)
        self.uEminField.setLayer(layer)
        self.uEmaxAzimuthField.setLayer(layer)
        self.readFromLayer()

    def settings(self):
        if self._validLayer:
            self.saveToSettings()
        return self._settings

    def isModified(self):
        return self._validLayer and not self._originalSettings.sameAs(self.settings())

    def readFromLayer(self):
        layersettings = self._controller.readSettingsFromLayer(self._layer)
        if layersettings is not None:
            self._settings = layersettings
        self.loadFromSettings()
        self._originalSettings = self.settings().clone()

    def applyToLayer(self):
        if self._validLayer:
            settings = self.settings()
            self._controller.applySettingsToLayer(self._layer, settings)
            self._originalSettings = settings.clone()

    def loadFromSettings(self):
        settings = self._settings
        if settings.drawArrow():
            self.setMode(settings.mode())
        else:
            self.setMode(self.ArrowTypeNone)
        self.setEllipseMode(settings.ellipseMode())
        self.uXField.setField(settings.dxField())
        self.uYField.setField(settings.dyField())
        self.uEmaxField.setField(settings.emaxField())
        self.uEminField.setField(settings.eminField())
        self.uEmaxAzimuthField.setField(settings.emaxAzimuthField())
        self.uAngleUnitsDegrees.setChecked(settings.angleUnits() == QgsVectorFieldSymbolLayer.Degrees)
        self.uAngleUnitsRadians.setChecked(self.uAngleUnitsDegrees.isChecked())
        self.uAngleOrientationNorth.setChecked(settings.angleOrientation() == QgsVectorFieldSymbolLayer.ClockwiseFromNorth)
        self.uAngleOrientationEast.setChecked(settings.angleOrientation() != QgsVectorFieldSymbolLayer.ClockwiseFromNorth)
        self.uEllipseAngleUnitsDegrees.setChecked(settings.ellipseDegrees())
        self.uEllipseAngleUnitsRadians.setChecked(not settings.ellipseDegrees())
        self.uEllipseOrientationNorth.setChecked(settings.ellipseAngleFromNorth())
        self.uEllipseOrientationEast.setChecked(not settings.ellipseAngleFromNorth())
        self.uArrowScale.setText(str(settings.scale()))
        self.uScaleUnits.setCurrentIndex(1 if settings.scaleIsMetres() else 0)
        # self.uVectorIsTrueNorth.setChecked(settings.vectorIsTrueNorth())
        # self.uAlignToMapNorth.setChecked(settings.useMapNorth())
        self.uEllipseScale.setText(str(settings.ellipseScale()))
        group = settings.scaleGroup()
        factor = settings.scaleGroupFactor()
        if group and factor != 1.0:
            group = group + "*" + str(factor)
        self.uScaleGroup.setText(group)
        symbolIndex = 0
        if settings.symbolUnitType in SymbolRenderUnitList:
            symbolIndex = SymbolRenderUnitList.index(settings.symbolUnitType())
        self.uSymbolUnits.setCurrentIndex(symbolIndex)
        self.uArrowHeadWidth.setValue(settings.arrowHeadWidth())
        self.uArrowShaftWidth.setValue(settings.arrowShaftWidth())
        self.uArrowHeadRelativeLength.setValue(settings.arrowHeadRelativeLength())
        self.uArrowMaxRelativeHeadSize.setValue(settings.arrowMaxRelativeHeadSize())
        self.uArrowBorderWidth.setValue(settings.arrowBorderWidth())
        self.uFillArrow.setChecked(settings.fillArrow())
        self.uArrowBaseSize.setValue(settings.baseSize())
        self.uArrowFillColor.setColor(settings.arrowFillColor())
        self.uArrowBorderColor.setColor(settings.arrowBorderColor())
        self.uBaseColor.setColor(settings.baseFillColor())
        self.uFillBase.setChecked(settings.fillBase())
        self.uDrawEllipse.setChecked(settings.drawEllipse())
        self.uDrawEllipseAxes.setChecked(settings.drawEllipseAxes())
        self.uBaseBorderColor.setColor(settings.baseBorderColor())
        self.uEllipseBorderWidth.setValue(settings.ellipseBorderWidth())
        self.uEllipseTickSize.setValue(settings.ellipseTickSize())
        self.uEllipseBorderColor.setColor(settings.ellipseBorderColor())
        self.uFillEllipse.setChecked(settings.fillEllipse())
        self.uEllipseFillColor.setColor(settings.ellipseFillColor())
        # self.uLegendText.setText( settings.legendText())
        # self.uScaleBoxText.setText( settings.scaleBoxText())
        # self.uShowInScaleBox.setChecked( settings.showInScaleBox())

    def saveToSettings(self):
        settings = self._settings
        # Avoid accidentally resetting scale group scale until we've
        # set the new scale group
        settings.setScaleGroup("")
        if self.mode() == self.ArrowTypeNone:
            settings.setDrawArrow(False)
            settings.setMode(QgsVectorFieldSymbolLayer.Cartesian)
        else:
            settings.setDrawArrow(True)
            settings.setMode(self.mode())
        settings.setEllipseMode(self.ellipseMode())
        settings.setDxField(self.uXField.currentText())
        settings.setDyField(self.uYField.currentText())
        settings.setEmaxField(self.uEmaxField.currentText())
        settings.setEminField(self.uEminField.currentText())
        settings.setEmaxAzimuthField(self.uEmaxAzimuthField.currentText())
        angleUnits = (
            QgsVectorFieldSymbolLayer.Degrees if self.uAngleUnitsDegrees.isChecked() else QgsVectorFieldSymbolLayer.Radians
        )
        settings.setAngleUnits(angleUnits)
        settings.setAngleOrientation(
            QgsVectorFieldSymbolLayer.ClockwiseFromNorth
            if self.uAngleOrientationNorth.isChecked()
            else QgsVectorFieldSymbolLayer.CounterclockwiseFromEast
        )
        settings.setEllipseDegrees(self.uEllipseAngleUnitsDegrees.isChecked())
        settings.setEllipseAngleFromNorth(self.uEllipseOrientationNorth.isChecked())
        try:
            settings.setScale(float(self.uArrowScale.text()))
        except:
            pass
        try:
            settings.setEllipseScale(float(self.uEllipseScale.text()))
        except:
            pass
        # settings.setUseMapUnit( self.scaleUnits.isMapUnit())
        # settings.setVectorIsTrueNorth(self.uVectorIsTrueNorth.isChecked())
        # settings.setUseMapNorth(self.uAlignToMapNorth.isChecked())
        group = self.uScaleGroup.text()
        factor = 1.0
        if "*" in group:
            group, f = group.split("*")
            try:
                factor = float(f)
            except:
                pass
        settings.setScaleGroupFactor(factor)
        settings.setScaleGroup(group)
        settings.setScaleIsMetres(self.uScaleUnits.currentIndex() != 0)
        settings.setSymbolUnitType(SymbolRenderUnitList[self.uSymbolUnits.currentIndex()])
        settings.setArrowHeadWidth(float(self.uArrowHeadWidth.value()))
        settings.setArrowShaftWidth(float(self.uArrowShaftWidth.value()))
        settings.setArrowHeadRelativeLength(float(self.uArrowHeadRelativeLength.value()))
        settings.setArrowMaxRelativeHeadSize(float(self.uArrowMaxRelativeHeadSize.value()))
        settings.setArrowBorderWidth(float(self.uArrowBorderWidth.value()))
        settings.setBaseSize(self.uArrowBaseSize.value())
        settings.setArrowBorderColor(self.uArrowBorderColor.color())
        settings.setArrowFillColor(self.uArrowFillColor.color())
        settings.setFillBase(self.uFillBase.isChecked())
        settings.setFillArrow(self.uFillArrow.isChecked())
        settings.setDrawEllipse(self.uDrawEllipse.isChecked())
        settings.setDrawEllipseAxes(self.uDrawEllipseAxes.isChecked())
        settings.setBaseFillColor(self.uBaseColor.color())
        settings.setBaseBorderColor(self.uBaseBorderColor.color())
        settings.setEllipseBorderWidth(self.uEllipseBorderWidth.value())
        settings.setEllipseTickSize(self.uEllipseTickSize.value())
        settings.setEllipseBorderColor(self.uEllipseBorderColor.color())
        settings.setFillEllipse(self.uFillEllipse.isChecked())
        settings.setEllipseFillColor(self.uEllipseFillColor.color())
        # settings.setLegendText( self.uLegendText.text())
        # settings.setScaleBoxText( self.uScaleBoxText.text())
        # settings.setShowInScaleBox( self.uShowInScaleBox.isChecked())
