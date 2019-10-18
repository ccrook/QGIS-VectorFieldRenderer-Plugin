#!/usr/bin/python3
import json
import re

from PyQt5.QtGui import QColor
from qgis.core import (
    QgsArrowSymbolLayer,
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMapLayerType,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
    QgsVectorFieldSymbolLayer,
    QgsEllipseSymbolLayer,
    QgsSymbolLayer,
    QgsProperty,
    QgsWkbTypes,
)


class VectorFieldLayerSettings:

    NoEllipse = 0
    CovarianceEllipse = 1
    AxesEllipse = 2
    CircularEllipse = 3
    HeightEllipse = 4

    def __init__(self):
        self._mode = QgsVectorFieldSymbolLayer.Cartesian
        self._angleOrientation = QgsVectorFieldSymbolLayer.ClockwiseFromNorth
        self._angleUnits = QgsVectorFieldSymbolLayer.Degrees
        self._scale = 1.0
        self._dxField = ""
        self._dyField = ""
        self._scaleUnitType = QgsUnitTypes.RenderMillimeters
        self._scaleGroup = ""
        self._scaleGroupFactor = 1.0
        self._symbolUnitType = QgsUnitTypes.RenderMillimeters
        self._ellipseMode = VectorFieldLayerSettings.AxesEllipse
        self._ellipseAngleFromNorth = True
        self._ellipseDegrees = True
        self._ellipseScale = 1.0
        self._drawArrow = True
        self._arrowShaftWidth = 1.5
        self._arrowHeadWidth = 3.0
        self._arrowHeadRelativeLength = 2.0
        self._arrowBorderWidth = 0.0
        self._arrowMaxRelativeHeadSize = 0.3
        self._arrowFillColor = QColor(0, 0, 0)
        self._fillArrow = True
        self._arrowBorderColor = QColor(0, 0, 0)
        self._baseSize = 2.0
        self._fillBase = True
        self._baseFillColor = QColor(255, 0, 0)
        self._baseBorderWidth = 0.0
        self._baseBorderColor = QColor(0, 0, 0)
        self._ellipseBorderWidth = 0.7
        self._emaxField = ""
        self._eminField = ""
        self._emaxAzimuthField = ""
        self._ellipseBorderColor = QColor(0, 0, 0)
        self._ellipseFillColor = QColor(0, 0, 0)
        self._fillEllipse = False
        self._drawEllipse = True
        self._drawEllipseAxes = False
        self._ellipseTickSize = 2.0
        self._scaleVariableName = ""

        # Not used in current version of renderer
        # self._vectorIsTrueNorth = True
        # self._useMapNorth = True
        # self._layerId = None
        # self._legendText = ""
        # self._showInScaleBox = True
        # self._scaleBoxText = ""

    def mode(self):
        return self._mode

    def setMode(self, value):
        self._mode = value

    def angleOrientation(self):
        return self._angleOrientation

    def setAngleOrientation(self, value):
        self._angleOrientation = value

    def angleUnits(self):
        return self._angleUnits

    def setAngleUnits(self, value):
        self._angleUnits = value

    def scale(self):
        return self._scale

    def setScale(self, value):
        self._scale = value

    def dxField(self):
        return self._dxField

    def setDxField(self, value):
        self._dxField = value

    def dyField(self):
        return self._dyField

    def setDyField(self, value):
        self._dyField = value

    def scaleUnitType(self):
        return self._scaleUnitType

    def setScaleUnitType(self, value):
        self._scaleUnitType = value

    def symbolUnitType(self):
        return self._symbolUnitType

    def setSymbolUnitType(self, value):
        self._symbolUnitType = value

    def scaleGroup(self):
        return self._scaleGroup

    def setScaleGroup(self, value):
        self._scaleGroup = value

    def scaleGroupFactor(self):
        return self._scaleGroupFactor

    def setScaleGroupFactor(self, value):
        self._scaleGroupFactor = value

    def ellipseMode(self):
        return self._ellipseMode

    def setEllipseMode(self, value):
        self._ellipseMode = value

    def ellipseAngleFromNorth(self):
        return self._ellipseAngleFromNorth

    def setEllipseAngleFromNorth(self, value):
        self._ellipseAngleFromNorth = value

    def ellipseDegrees(self):
        return self._ellipseDegrees

    def setEllipseDegrees(self, value):
        self._ellipseDegrees = value

    def ellipseScale(self):
        return self._ellipseScale

    def setEllipseScale(self, value):
        self._ellipseScale = value

    def drawArrow(self):
        return self._drawArrow

    def setDrawArrow(self, value):
        self._drawArrow = value

    def arrowShaftWidth(self):
        return self._arrowShaftWidth

    def setArrowShaftWidth(self, value):
        self._arrowShaftWidth = value

    def arrowMaxRelativeHeadSize(self):
        return self._arrowMaxRelativeHeadSize

    def setArrowMaxRelativeHeadSize(self, value):
        self._arrowMaxRelativeHeadSize = value

    def arrowHeadWidth(self):
        return self._arrowHeadWidth

    def setArrowHeadWidth(self, value):
        self._arrowHeadWidth = value

    def arrowHeadRelativeLength(self):
        return self._arrowHeadRelativeLength

    def setArrowHeadRelativeLength(self, value):
        self._arrowHeadRelativeLength = value

    def arrowBorderWidth(self):
        return self._arrowBorderWidth

    def setArrowBorderWidth(self, value):
        self._arrowBorderWidth = value

    def arrowFillColor(self):
        return self._arrowFillColor

    def setArrowFillColor(self, value):
        self._arrowFillColor = value

    def fillArrow(self):
        return self._fillArrow

    def setFillArrow(self, value):
        self._fillArrow = value

    def arrowBorderColor(self):
        return self._arrowBorderColor

    def setArrowBorderColor(self, value):
        self._arrowBorderColor = value

    def baseSize(self):
        return self._baseSize

    def setBaseSize(self, value):
        self._baseSize = value

    def fillBase(self):
        return self._fillBase

    def setFillBase(self, value):
        self._fillBase = value

    def baseFillColor(self):
        return self._baseFillColor

    def setBaseFillColor(self, value):
        self._baseFillColor = value

    def baseBorderWidth(self):
        return self._baseBorderWidth

    def setBaseBorderWidth(self, value):
        self._baseBorderWidth = value

    def baseBorderColor(self):
        return self._baseBorderColor

    def setBaseBorderColor(self, value):
        self._baseBorderColor = value

    def ellipseBorderWidth(self):
        return self._ellipseBorderWidth

    def setEllipseBorderWidth(self, value):
        self._ellipseBorderWidth = value

    def emaxField(self):
        return self._emaxField

    def setEmaxField(self, value):
        self._emaxField = value

    def eminField(self):
        return self._eminField

    def setEminField(self, value):
        self._eminField = value

    def emaxAzimuthField(self):
        return self._emaxAzimuthField

    def setEmaxAzimuthField(self, value):
        self._emaxAzimuthField = value

    def ellipseBorderColor(self):
        return self._ellipseBorderColor

    def setEllipseBorderColor(self, value):
        self._ellipseBorderColor = value

    def ellipseFillColor(self):
        return self._ellipseFillColor

    def setEllipseFillColor(self, value):
        self._ellipseFillColor = value

    def fillEllipse(self):
        return self._fillEllipse

    def setFillEllipse(self, value):
        self._fillEllipse = value

    def drawEllipse(self):
        return self._drawEllipse

    def setDrawEllipse(self, value):
        self._drawEllipse = value

    def drawEllipseAxes(self):
        return self._drawEllipseAxes

    def setDrawEllipseAxes(self, value):
        self._drawEllipseAxes = value

    def ellipseTickSize(self):
        return self._ellipseTickSize

    def setEllipseTickSize(self, value):
        self._ellipseTickSize = value

    def setScaleVariableName(self, name):
        self._scaleVariableName = name

    # Functions to construct symbology

    def basepointSymbol(self):
        """
        Creates a markser symbol for the base point
        """
        symbolUnit = QgsUnitTypes.toAbbreviatedString(self._symbolUnitType)
        basepointSymbol = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "size": str(self._baseSize),
                "color": self._baseFillColor.name(QColor.HexArgb),
                "outline_width": str(self._baseBorderWidth),
                "outline_color": self._baseBorderColor.name(QColor.HexArgb),
                "size_unit": symbolUnit,
                "outline_width_unit": symbolUnit,
            }
        )
        return basepointSymbol

    def basepointLineSymbolLayer(self):
        """
        Creates a line symbol layer for the base point of the arrow.  This is a marker line
        with a marker at the first vertex.
        """
        basepointSymbol = self.basepointSymbol()
        basepointLine = QgsMarkerLineSymbolLayer()
        basepointLine.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
        basepointLine.setSubSymbol(basepointSymbol)
        return basepointLine

    def arrowSymbolLayer(self):
        """
        Creates a line symbol layer for the arrow.  
        """

        if not self._drawArrow:
            return None
        symbolUnit = QgsUnitTypes.toAbbreviatedString(self._symbolUnitType)
        arrow = QgsArrowSymbolLayer.create(
            {
                "head_type": "0",
                "arrow_type": "0",
                "arrow_width": str(self._arrowShaftWidth),
                "arrow_start_width": str(self._arrowShaftWidth),
                "head_thickness": str(self._arrowHeadWidth),
                "head_length": str(self._arrowHeadWidth * self._arrowHeadRelativeLength),
                "arrow_start_width_unit": symbolUnit,
                "arrow_width_unit": symbolUnit,
                "arrow_head_thickness_unit": symbolUnit,
                "arrow_head_length_unit": symbolUnit,
            }
        )
        arrowFillSymbol = QgsFillSymbol.createSimple(
            {
                "color": self._arrowFillColor.name(QColor.HexArgb),
                "style": "solid" if self._fillArrow else "no",
                "outline_style": "solid",
                "outline_width": str(self._arrowBorderWidth),
                "outline_width_unit": symbolUnit,
                "outline_color": self._arrowBorderColor.name(QColor.HexArgb),
                "joinstyle": "miter",
            }
        )
        arrow.setSubSymbol(arrowFillSymbol)
        return arrow

    # TODO: Must be an API call for this - not sure if there is a way to
    # escape " in field

    def _fieldExpression(self, field):
        return '"' + field + '"'

    def ellipseSymbolLayer(self):

        if self._ellipseMode == self.NoEllipse:
            return None
        # TODO: Currently don't handle ellipse defined by covariance
        if self._ellipseMode == self.CovarianceEllipse:
            return None
        symbolUnit = QgsUnitTypes.toAbbreviatedString(self._symbolUnitType)
        scaleUnit = QgsUnitTypes.toAbbreviatedString(self._scaleUnitType)
        fillColor = self._ellipseFillColor.name(QColor.HexArgb)
        if not self._fillEllipse:
            fillColor = "#00000000"
        ellipseLayer = QgsEllipseSymbolLayer.create(
            {
                "symbol_width": "0",
                "symbol_width_unit": scaleUnit,
                "symbol_height": "0",
                "symbol_height_unit": scaleUnit,
                "symbol_name": ("circle" if self._drawEllipse else "cross"),
                "angle": "0",
                "outline_width": str(self._ellipseBorderWidth),
                "outline_width_unit": symbolUnit,
                "outline_color": self._ellipseBorderColor.name(QColor.HexArgb),
                "fill_color": fillColor,
            }
        )
        scale = self._ellipseScale
        useproperty = self._scaleVariableName != ""
        if useproperty:
            ellipseScale = "(@" + self._scaleVariableName + " * " + str(scale) + ")"
        else:
            ellipseScale = str(scale * self._scale)
        widthExpression = self._fieldExpression(self._emaxField) + "*" + ellipseScale

        if self._ellipseMode == self.AxesEllipse:
            heightExpression = self._fieldExpression(self._eminField) + "*" + ellipseScale
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyWidth, QgsProperty.fromExpression(widthExpression))
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(heightExpression))
            angleExpression = self._fieldExpression(self._emaxAzimuthField)
            if not self._ellipseDegrees:
                angleExpression = "radians(" + angleExpression + ")"
            if self._ellipseAngleFromNorth:
                angleExpression = "(90.0-" + angleExpression + ")"
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyAngle, QgsProperty.fromExpression(angleExpression))
        elif self._ellipseMode == self.CircularEllipse:
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyWidth, QgsProperty.fromExpression(widthExpression))
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(widthExpression))
        elif self._ellipseMode == self.HeightEllipse:
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(widthExpression))
        else:
            return None
        return ellipseLayer

    def ellipseLineSymbolLayer(self):
        ellipseLayer = self.ellipseSymbolLayer()
        if ellipseLayer is None:
            return None
        ellipseSymbol = QgsMarkerSymbol()
        ellipseSymbol.deleteSymbolLayer(0)
        ellipseSymbol.appendSymbolLayer(ellipseLayer)
        ellipseLine = QgsMarkerLineSymbolLayer()
        ellipseLine.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
        ellipseLine.setSubSymbol(ellipseSymbol)
        return ellipseLine

    def vectorFieldSymbol(self):
        scaleUnit = QgsUnitTypes.toAbbreviatedString(self._scaleUnitType)
        vfl = QgsVectorFieldSymbolLayer()
        vfl.setXAttribute(self._dxField)
        vfl.setYAttribute(self._dyField)
        vfl.setScale(self._scale)
        vfl.setVectorFieldType(self._mode)
        vfl.setAngleOrientation(self._angleOrientation)
        vfl.setAngleUnits(self._angleUnits)
        vfl.setDistanceUnit(self._scaleUnitType)

        # Create the symbology for the vector layer
        symbol = QgsLineSymbol()
        symbol.deleteSymbolLayer(0)
        basepoint = self.basepointLineSymbolLayer()
        if basepoint is not None:
            symbol.appendSymbolLayer(basepoint)
        arrow = self.arrowSymbolLayer()
        if arrow is not None:
            symbol.appendSymbolLayer(arrow)
        ellipse = self.ellipseLineSymbolLayer()
        if ellipse is not None:
            symbol.insertSymbolLayer(0, ellipse)
        vfl.setSubSymbol(symbol)

        # Now create the marker symbol using the symbol layer
        vflsymbol = QgsMarkerSymbol()
        vflsymbol.changeSymbolLayer(0, vfl)

        return vflsymbol

    def symbol(self):
        if self._drawArrow:
            symbol = self.vectorFieldSymbol()
        else:
            symbol = self.basepointSymbol()
            ellipse = self.ellipseSymbolLayer()
            if ellipse is not None:
                symbol.insertSymbolLayer(0, ellipse)
        return symbol

    def saveToString(self):
        """
        Write the layer settings to a string 
        """
        settings = {}
        for setting in self.__dict__:
            if re.match(r"_[a-z]", setting):
                value = self.__dict__[setting]
                key = setting[1:]
                if callable(value):
                    continue
                if setting == "_scaleVariableName":
                    continue
                if type(value) == QColor:
                    value = value.name(QColor.HexArgb)
                settings[key] = value
        settingstr = json.dumps(settings, sort_keys=True)
        return settingstr

    def readFromString(self, settingstr):
        """
        Read the layer settings from a JSON formatted string
        """
        result = False
        try:
            settings = json.loads(settingstr)
            newvalues = {}
            for setting in self.__dict__:
                if re.match(r"_[a-z]", setting):
                    value = self.__dict__[setting]
                    valueType = type(value)
                    if callable(value):
                        continue
                    key = setting[1:]
                    if key not in settings:
                        continue
                    value = settings.get(key)
                    if value is None:
                        continue
                    try:
                        value = valueType(value)
                        newvalues[setting] = value
                    except:
                        pass
            self.__dict__.update(newvalues)
            result = True
        except:
            pass
        return result
