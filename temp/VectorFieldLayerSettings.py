#!/usr/bin/python3
from qgis.core import (
    QgsUnitTypes,
    QgsVectorFieldSymbolLayer,
    QgsMarkerSymbol,
    QgsMarkerLineSymbolLayer,
    QgsArrowSymbolLayer,
    QgsSimpleFillSymbolLayer,
    QgsFillSymbol,
    QgsMapLayerType,
    QgsWkbTypes,
)

from PyQt5.QtGui import QColor

import json
import re

from re import T

VECTOR_SETTINGS_PROP = "vfr_settings"


class VectorFieldLayerSettings:
    def __init__(self):
        self._degrees = True
        self._mode = QgsVectorFieldSymbolLayer.Cartesian
        self._angleOrientation = QgsVectorFieldSymbolLayer.ClockwiseFromNorth
        self._angleUnits = QgsVectorFieldSymbolLayer.Degrees
        self._scale = 1.0
        self._dxField = ""
        self._dyField = ""
        self._unitType = QgsUnitTypes.RenderMillimeters
        self._scaleGroup = ""
        self._scaleGroupFactor = 1.0
        # self._ellipseMode = VectorFieldRenderer.AxesEllipse
        self._ellipseAngleFromNorth = True
        self._ellipseDegrees = True
        self._ellipseScale = 1.0
        self._arrowShaftSize = 1.5
        self._arrowRelativeHeadSize = 0.3
        self._arrowMaxHeadSize = 3.0
        self._arrowBorderWidth = 0.0
        self._arrowFillColor = QColor(0, 0, 0)
        self._fillArrow = True
        self._arrowBorderColor = QColor(0, 0, 0)
        self._arrowHeadShape = (0, -1.0, -0.7)
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

        # Not used in current version of renderer
        # self._vectorIsTrueNorth = True
        # self._useMapNorth = True
        # self._layerId = None
        # self._legendText = ""
        # self._showInScaleBox = True
        # self._scaleBoxText = ""

    def basepointSymbolLayer(self):
        """
        Creates a line symbol layer for the base point of the arrow.  This is a marker line
        with a marker at the first vertex.
        """
        symbolUnit = QgsUnitTypes.toAbbreviatedString()
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
        basepointLine = QgsMarkerLineSymbolLayer()
        basepointLine.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
        basepointLine.setSubSymbol(basepointSymbol)
        return basepointLine

    def arrowSymbolLayer(self):
        symbolUnit = QgsUnitTypes.toAbbreviatedString()
        arrow = QgsArrowSymbolLayer.create(
            {
                "head_type": "0",
                "arrow_type": "0",
                "arrow_width": str(self._arrowShaftSize),
                "arrow_start_width": str(self._arrowShaftSize),
                "arrow_head_length": str(self._arrowMaxHeadSize * (_arrowHeadShape[0] - self._arrowHeadShape[1])),
                "arrow_head_width": str(self._arrowMaxHeadSize),
                "arrow_start_width_unit": symbolUnit,
                "arrow_width_unit": symbolUnit,
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
            }
        )
        arrow.setSubSymbol(arrowFillSymbol)
        return arrow

    def ellipseSymbolLayer(self):

        ellipseLine = None
        # symbolUnit = QgsUnitTypes.toAbbreviatedString()
        # ellipseLine=QgsMarkerLineSymbolLayer()
        # ellipseLine.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
        # ellipse=QgsEllipseSymbolLayer()
        return ellipseLine()

    def createVectorFieldSymbol(self):
        vfl = QgsVectorFieldSymbolLayer()
        vfl.setXAttribute(self._dxField)
        vfl.setYAttribute(self._dyField)
        vfl.setScale(self._scale)
        vfl.setVectorFieldType(self._mode)
        vfl.setAngleOrientation(self._angleOrientation)
        vfl.setAngleUnits(self._angleUnits)
        vfl.setDistanceUnit(self._unitType)

        # Create the symbology for the vector layer
        symbol = QgsLineSymbol()
        symbol.removeSymbolLayer(0)
        basepoint = self.basepointSymbolLayer()
        if basepoint is not None:
            symbol.appendSymbolLayer(basepoint)
        arrow = self.arrowSymbolLayer()
        if arrow is not None:
            symbol.appendSymbolLayer(arrow)
        ellipse = self.ellipseSymbolLayer()
        if ellipse is not None:
            symbol.appendSymbolLayer(ellipse)
        vfl.setSubSymbol(symbol)

        # Now create the marker symbol using the symbol layer
        vflsymbol = QgsMarkerSymbol()
        vflsymbol.changeSymbolLayer(0, vfl)

        return vflsymbol

    def applyToLayer(self, layer):
        if layer.type() != QgsMapLayerType.VectorLayer:
            return None
        if layer.geometryType() != QgsWkbTypes.PointGeometry:
            return None
        vflsymbol = self.createVectorFieldSymbol()
        renderer = QgsSingleSymbolRenderer(vflsymbol)
        layer.setRenderer(renderer)
        VectorFieldUtils.setVectorFieldLayerScale(self._scale, self._scaleGroup, self._scaleGroupFactor)
        layer.triggerRepaint()

    def saveToString(self):
        """
        Write the layer settings to a string 
        """
        settings = {}
        for setting in self.__dict__:
            if re.match(r"_[a-z]", setting):
                value = self.__dict__(setting)
                key = setting[1:]
                if callable(value):
                    continue
                if type(value) == QColor:
                    value = value.name(QColor.HexArgb)
                settings[key] = value
        settingstr = json.dumps(settings,sort_keys=True)
        return settingstr

    def saveToLayer(self, layer):
        """
        Write the layer settings to a QgsMapLayer custom property 
        """
        settingstr = self.saveToString()
        layer.setCustomProperty(VECTOR_SETTINGS_PROP, settingstr)

    def readFromString(self, settingstr):
        """
        Read the layer settings from a JSON formatted string
        """
        try:
            settingstr = layer.customPropert(VECTOR_SETTINGS_PROP)
            settings = json.loads(settingstr)
            newvalues = {}
            for setting in self.__dict__:
                if re.match(r"_[a-z]", setting):
                    value = self.__dict__(setting)
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
        except:
            pass

    def readFromLayer(self, layer):
        """
        Write the layer settings to a QgsMapLayer custom property 
        """

        settingstr = layer.customProperty(VECTOR_SETTINGS_PROP, "")
        if settingstr != "":
            self.readFromString(settingstr)
