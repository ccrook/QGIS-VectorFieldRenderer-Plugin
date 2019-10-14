#!/usr/bin/python3
import json
import re
from re import T

from PyQt5.QtGui import QColor
from qgis.core import (
    QgsArrowSymbolLayer,
    QgsFillSymbol,
    QgsMapLayerType,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsSimpleFillSymbolLayer,
    QgsUnitTypes,
    QgsVectorFieldSymbolLayer,
    QgsWkbTypes,
)

VECTOR_SETTINGS_PROP = "vfr_settings"


class VectorFieldLayerSettings:

    NoEllipse = 0
    CovarianceEllipse = 1
    AxesEllipse = 2
    CircularEllipse = 3
    HeightEllipse = 4

    def __init__(self):
        self._degrees = True
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
        self._symbolUnitType = QgsUnitTypes.RenderMillimeters
        self._arrowShaftSize = 1.5
        self._arrowRelativeHeadSize = 0.3
        self._arrowMaxHeadSize = 3.0
        self._arrowBorderWidth = 0.0
        self._arrowFillColor = QColor(0, 0, 0)
        self._fillArrow = True
        self._arrowBorderColor = QColor(0, 0, 0)
        self._arrowHeadShapeFront=0.0
        self._arrowHeadShapeBackOuter=-1.0
        self._arrowHeadShapeBackInner=-0.7
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

    def degrees(self):
        return self._degrees

    def setDegrees(self,value):
        self._degrees = value

    def mode(self):
        return self._mode

    def setMode(self,value):
        self._mode = value

    def angleOrientation(self):
        return self._angleOrientation

    def setAngleOrientation(self,value):
        self._angleOrientation = value

    def angleUnits(self):
        return self._angleUnits

    def setAngleUnits(self,value):
        self._angleUnits = value

    def scale(self):
        return self._scale

    def setScale(self,value):
        self._scale = value

    def dxField(self):
        return self._dxField

    def setDxField(self,value):
        self._dxField = value

    def dyField(self):
        return self._dyField

    def setDyField(self,value):
        self._dyField = value

    def scaleUnitType(self):
        return self._scaleUnitType

    def setScaleUnitType(self,value):
        self._scaleUnitType = value

    def symbolUnitType(self):
        return self._symbolUnitType

    def setSymbolUnitType(self,value):
        self._symbolUnitType = value

    def scaleGroup(self):
        return self._scaleGroup

    def setScaleGroup(self,value):
        self._scaleGroup = value

    def scaleGroupFactor(self):
        return self._scaleGroupFactor

    def setScaleGroupFactor(self,value):
        self._scaleGroupFactor = value

    def ellipseMode(self):
        return self._ellipseMode

    def setEllipseMode(self,value):
        self._ellipseMode = value

    def ellipseAngleFromNorth(self):
        return self._ellipseAngleFromNorth

    def setEllipseAngleFromNorth(self,value):
        self._ellipseAngleFromNorth = value

    def ellipseDegrees(self):
        return self._ellipseDegrees

    def setEllipseDegrees(self,value):
        self._ellipseDegrees = value

    def ellipseScale(self):
        return self._ellipseScale

    def setEllipseScale(self,value):
        self._ellipseScale = value

    def arrowShaftSize(self):
        return self._arrowShaftSize

    def setArrowShaftSize(self,value):
        self._arrowShaftSize = value

    def arrowRelativeHeadSize(self):
        return self._arrowRelativeHeadSize

    def setArrowRelativeHeadSize(self,value):
        self._arrowRelativeHeadSize = value

    def arrowMaxHeadSize(self):
        return self._arrowMaxHeadSize

    def setArrowMaxHeadSize(self,value):
        self._arrowMaxHeadSize = value

    def arrowBorderWidth(self):
        return self._arrowBorderWidth

    def setArrowBorderWidth(self,value):
        self._arrowBorderWidth = value

    def arrowFillColor(self):
        return self._arrowFillColor

    def setArrowFillColor(self,value):
        self._arrowFillColor = value

    def fillArrow(self):
        return self._fillArrow

    def setFillArrow(self,value):
        self._fillArrow = value

    def arrowBorderColor(self):
        return self._arrowBorderColor

    def setArrowBorderColor(self,value):
        self._arrowBorderColor = value

    def arrowHeadShapeFront(self):
        return self._arrowHeadShapeFront

    def setArrowHeadShapeFront(self,value):
        self._arrowHeadShapeFront = value

    def arrowHeadShapeBackOuter(self):
        return self._arrowHeadShapeBackOuter

    def setArrowHeadShapeBackOuter(self,value):
        self._arrowHeadShapeBackOuter = value
 
    def arrowHeadShapeBackInner(self):
        return self._arrowHeadShapeBackInner

    def setArrowHeadShapeBackInner(self,value):
        self._arrowHeadShapeBackInner = value

    def baseSize(self):
        return self._baseSize

    def arrowHeadShape(self):
        return self._arrowHeadShape

    def setArrowHeadShape(self,value):
        self._arrowHeadShape = value

    def setBaseSize(self,value):
        self._baseSize = value

    def fillBase(self):
        return self._fillBase

    def setFillBase(self,value):
        self._fillBase = value

    def baseFillColor(self):
        return self._baseFillColor

    def setBaseFillColor(self,value):
        self._baseFillColor = value

    def baseBorderWidth(self):
        return self._baseBorderWidth

    def setBaseBorderWidth(self,value):
        self._baseBorderWidth = value

    def baseBorderColor(self):
        return self._baseBorderColor

    def setBaseBorderColor(self,value):
        self._baseBorderColor = value

    def ellipseBorderWidth(self):
        return self._ellipseBorderWidth

    def setEllipseBorderWidth(self,value):
        self._ellipseBorderWidth = value

    def emaxField(self):
        return self._emaxField

    def setEmaxField(self,value):
        self._emaxField = value

    def eminField(self):
        return self._eminField

    def setEminField(self,value):
        self._eminField = value

    def emaxAzimuthField(self):
        return self._emaxAzimuthField

    def setEmaxAzimuthField(self,value):
        self._emaxAzimuthField = value

    def ellipseBorderColor(self):
        return self._ellipseBorderColor

    def setEllipseBorderColor(self,value):
        self._ellipseBorderColor = value

    def ellipseFillColor(self):
        return self._ellipseFillColor

    def setEllipseFillColor(self,value):
        self._ellipseFillColor = value

    def fillEllipse(self):
        return self._fillEllipse

    def setFillEllipse(self,value):
        self._fillEllipse = value

    def drawEllipse(self):
        return self._drawEllipse

    def setDrawEllipse(self,value):
        self._drawEllipse = value

    def drawEllipseAxes(self):
        return self._drawEllipseAxes

    def setDrawEllipseAxes(self,value):
        self._drawEllipseAxes = value

    def ellipseTickSize(self):
        return self._ellipseTickSize

    def setEllipseTickSize(self,value):
        self._ellipseTickSize = value

    # Functions to construct symbology

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
                "arrow_head_length": str(self._arrowMaxHeadSize * (_arrowHeadShapeFront - self._arrowHeadShapeBackOuter)),
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
        return ellipseLine

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
                value = self.__dict__[setting]
                key = setting[1:]
                if callable(value):
                    continue
                if type(value) == QColor:
                    value = value.name(QColor.HexArgb)
                settings[key] = value
        settingstr = json.dumps(settings, sort_keys=True)
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
        result=False
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
            result=True
        except:
            pass
        return result

    def readFromLayer(self, layer):
        """
        Write the layer settings to a QgsMapLayer custom property 
        """

        result=False
        settingstr = layer.customProperty(VECTOR_SETTINGS_PROP, "")
        if settingstr != "":
            result=self.readFromString(settingstr)
        return result
            