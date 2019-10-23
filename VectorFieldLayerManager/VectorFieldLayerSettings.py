#!/usr/bin/python3
import json
import re
import math

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
    QgsSimpleMarkerSymbolLayer,
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

    _defaults = dict(
        mode=QgsVectorFieldSymbolLayer.Cartesian,
        angleOrientation=QgsVectorFieldSymbolLayer.ClockwiseFromNorth,
        angleUnits=QgsVectorFieldSymbolLayer.Degrees,
        scale=1.0,
        dxField="",
        dyField="",
        scaleIsMetres=False,
        scaleGroup="",
        scaleGroupFactor=1.0,
        symbolUnitType=QgsUnitTypes.RenderMillimeters,
        ellipseMode=AxesEllipse,
        ellipseAngleFromNorth=True,
        ellipseDegrees=True,
        ellipseScale=1.0,
        drawArrow=True,
        arrowShaftWidth=1.5,
        arrowHeadWidth=3.0,
        arrowHeadRelativeLength=2.0,
        arrowBorderWidth=0.0,
        arrowMaxRelativeHeadSize=0.3,
        arrowFillColor=QColor(0, 0, 0),
        fillArrow=True,
        arrowBorderColor=QColor(0, 0, 0),
        baseSize=2.0,
        fillBase=True,
        baseFillColor=QColor(255, 0, 0),
        baseBorderWidth=0.0,
        baseBorderColor=QColor(0, 0, 0),
        ellipseBorderWidth=0.7,
        emaxField="",
        eminField="",
        emaxAzimuthField="",
        ellipseBorderColor=QColor(0, 0, 0),
        ellipseFillColor=QColor(0, 0, 0),
        fillEllipse=False,
        drawEllipse=True,
        drawEllipseAxes=False,
        ellipseTickSize=2.0,
    )

    _types = {k: type(v) for k, v in _defaults.items()}

    # Not used in current version of renderer
    # self._vectorIsTrueNorth = True
    # self._useMapNorth = True
    # self._layerId = None
    # self._legendText = ""
    # self._showInScaleBox = True
    # self._scaleBoxText = ""

    def __init__(self, **settings):
        # Layer variable used to automatically change the scale...
        self._settings = dict(self._defaults)
        self._scaleVariableName = ""
        self.set(**settings)

    def set(self, ignore_errors=False, **settings):
        for k, v in settings.items():
            if k not in self._types:
                if not ignore_errors:
                    raise KeyError(k)
                continue
            self._settings[k] = self._types[k](v)

    def setScaleVariableName(self, name):
        self._scaleVariableName = name

    def clone(self):
        clone = VectorFieldLayerSettings(**self._settings)
        return clone

    def sameAs(self, other):
        return self.saveToString() == other.saveToString()

    # Functions to construct symbology

    # TODO: Is there an API call for quotedFieldExpression.

    def quotedFieldExpression(self, field):
        return '"' + field + '"'

    def encodedSymbolUnit(self):
        return QgsUnitTypes.encodeUnit(self.symbolUnitType())

    def encodedScaleUnit(self):
        if self.scaleIsMetres():
            return QgsUnitTypes.encodeUnit(QgsUnitTypes.RenderMetersInMapUnits)
        return self.encodedSymbolUnit()

    def vectorScaleUnit(self):
        if self.scaleIsMetres():
            return QgsUnitTypes.RenderMetersInMapUnits
        return self.symbolUnitType()

    def basepointSymbol(self):
        """
        Creates a marker symbol for the base point
        """
        symbolUnit = self.encodedSymbolUnit()
        basepointSymbol = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "size": str(self.baseSize()),
                "color": self.baseFillColor().name(QColor.HexArgb),
                "outline_width": str(self.baseBorderWidth()),
                "outline_color": self.baseBorderColor().name(QColor.HexArgb),
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
        basepointLine = QgsMarkerLineSymbolLayer(rotateMarker=False)
        basepointLine.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
        basepointLine.setSubSymbol(basepointSymbol)
        return basepointLine

    def arrowSymbolLayer(self):
        """
        Creates a line symbol layer for the arrow.  
        """

        if not self.drawArrow():
            return None
        symbolUnit = self.encodedSymbolUnit()
        arrow = QgsArrowSymbolLayer.create(
            {
                "head_type": "0",
                "arrow_type": "0",
                "arrow_width": str(self.arrowShaftWidth()),
                "arrow_start_width": str(self.arrowShaftWidth()),
                "head_thickness": str(self.arrowHeadWidth()),
                "head_length": str(self.arrowHeadWidth() * self.arrowHeadRelativeLength()),
                "arrow_start_width_unit": symbolUnit,
                "arrow_width_unit": symbolUnit,
                "arrow_head_thickness_unit": symbolUnit,
                "arrow_head_length_unit": symbolUnit,
            }
        )
        arrowFillSymbol = QgsFillSymbol.createSimple(
            {
                "color": self.arrowFillColor().name(QColor.HexArgb),
                "style": "solid" if self.fillArrow() else "no",
                "outline_style": "solid",
                "outline_width": str(self.arrowBorderWidth()),
                "outline_width_unit": symbolUnit,
                "outline_color": self.arrowBorderColor().name(QColor.HexArgb),
                "joinstyle": "miter",
            }
        )
        arrow.setSubSymbol(arrowFillSymbol)
        return arrow

    def heightErrorSymbolLayers(self):
        symbolUnit = self.encodedSymbolUnit()
        scaleUnit = self.encodedScaleUnit()
        tick1 = QgsSimpleMarkerSymbolLayer.create(
            {
                "name": "line",
                "size": "0.0",
                "angle": "0.0",
                "color": self.ellipseBorderColor().name(QColor.HexArgb),
                "line_width": str(self.baseBorderWidth()),
                "line_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "size_unit": scaleUnit,
            }
        )
        tick2 = QgsSimpleMarkerSymbolLayer.create(
            {
                "name": "line",
                "size": str(self.ellipseTickSize()),
                "angle": "90.0",
                "color": self.ellipseBorderColor().name(QColor.HexArgb),
                "line_width": str(self.baseBorderWidth()),
                "line_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "size_unit": symbolUnit,
                "offset_unit": scaleUnit,
            }
        )

        scale = self.ellipseScale() * 2.0
        useproperty = self._scaleVariableName != ""
        if useproperty:
            ellipseScale = "(@" + self._scaleVariableName + " * " + str(scale) + ")"
        else:
            ellipseScale = str(scale * self.scale())
        sizeExpression = self.quotedFieldExpression(self.emaxField()) + "*" + ellipseScale
        tick3 = tick2.clone()
        tick1.setDataDefinedProperty(QgsSymbolLayer.PropertySize, QgsProperty.fromExpression(sizeExpression))
        offset2 = "to_string(0.5*" + sizeExpression + ") || ',0.0'"
        offset3 = "to_string(-0.5*" + sizeExpression + ") || ',0.0'"
        tick2.setDataDefinedProperty(QgsSymbolLayer.PropertyOffset, QgsProperty.fromExpression(offset2))
        tick3.setDataDefinedProperty(QgsSymbolLayer.PropertyOffset, QgsProperty.fromExpression(offset3))
        return [tick1, tick2, tick3]

    def ellipseSymbolLayer(self):

        if self.ellipseMode() == self.NoEllipse:
            return None
        # TODO: Currently don't handle ellipse defined by covariance
        if self.ellipseMode() == self.CovarianceEllipse:
            return None
        symbolUnit = self.encodedSymbolUnit()
        scaleUnit = self.encodedScaleUnit()
        fillColor = self.ellipseFillColor().name(QColor.HexArgb)
        if not self.fillEllipse():
            fillColor = "#00000000"
        ellipseLayer = QgsEllipseSymbolLayer.create(
            {
                "symbol_width": "0",
                "symbol_width_unit": scaleUnit,
                "symbol_height": "0",
                "symbol_height_unit": scaleUnit,
                "symbol_name": ("circle" if self.drawEllipse() else "cross"),
                "angle": "0",
                "outline_width": str(self.ellipseBorderWidth()),
                "outline_width_unit": symbolUnit,
                "outline_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "fill_color": fillColor,
            }
        )
        scale = self.ellipseScale() * 2.0  # As symbol measured on diameter
        useproperty = self._scaleVariableName != ""
        if useproperty:
            ellipseScale = "(@" + self._scaleVariableName + " * " + str(scale) + ")"
        else:
            ellipseScale = str(scale * self.scale())
        widthExpression = self.quotedFieldExpression(self.emaxField()) + "*" + ellipseScale

        if self.ellipseMode() == self.AxesEllipse:
            heightExpression = self.quotedFieldExpression(self.eminField()) + "*" + ellipseScale
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyWidth, QgsProperty.fromExpression(widthExpression))
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(heightExpression))
            angleExpression = self.quotedFieldExpression(self.emaxAzimuthField())
            if not self.ellipseDegrees():
                angleExpression = "radians(" + angleExpression + ")"
            if self.ellipseAngleFromNorth():
                angleExpression = "(90.0-" + angleExpression + ")"
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyAngle, QgsProperty.fromExpression(angleExpression))
        elif self.ellipseMode() == self.CircularEllipse:
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyWidth, QgsProperty.fromExpression(widthExpression))
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(widthExpression))
        elif self.ellipseMode() == self.HeightEllipse:
            ellipseLayer.setDataDefinedProperty(QgsSymbolLayer.PropertyHeight, QgsProperty.fromExpression(widthExpression))
        else:
            return None
        return ellipseLayer

    def errorSymbolLayers(self):
        if self.ellipseMode() == self.HeightEllipse:
            return self.heightErrorSymbolLayers()
        ellipseLayer = self.ellipseSymbolLayer()
        if ellipseLayer is not None:
            return [ellipseLayer]
        return None

    def ellipseLineSymbolLayer(self):
        errorLayers = self.errorSymbolLayers()
        if errorLayers is None:
            return None
        ellipseSymbol = QgsMarkerSymbol()
        ellipseSymbol.deleteSymbolLayer(0)
        for errorLayer in errorLayers:
            ellipseSymbol.appendSymbolLayer(errorLayer)
        ellipseLine = QgsMarkerLineSymbolLayer(rotateMarker=False)
        ellipseLine.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
        ellipseLine.setSubSymbol(ellipseSymbol)
        return ellipseLine

    def vectorFieldSymbol(self):
        scaleUnit = QgsUnitTypes.toAbbreviatedString(self.scaleIsMetres())
        vfl = QgsVectorFieldSymbolLayer()
        vfl.setXAttribute(self.dxField())
        vfl.setYAttribute(self.dyField())
        vfl.setScale(self.scale())
        vfl.setVectorFieldType(self.mode())
        vfl.setAngleOrientation(self.angleOrientation())
        vfl.setAngleUnits(self.angleUnits())
        if self.scaleIsMetres():
            vfl.setDistanceUnit(QgsUnitTypes.RenderMetersInMapUnits)
        else:
            vfl.setDistanceUnit(self.symbolUnitType())

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
        if self.drawArrow():
            symbol = self.vectorFieldSymbol()
        else:
            symbol = self.basepointSymbol()
            errorLayers = self.errorSymbolLayers()
            if errorLayers is not None:
                for errorLayer in errorLayers:
                    symbol.insertSymbolLayer(0, errorLayer)
        return symbol

    def estimatedVectorSize(self, feature):
        size = 0.0
        if self.drawArrow():
            try:
                ds = abs(float(feature.attribute(self.dxField())))
                if self.mode() == QgsVectorFieldSymbolLayer.Cartesian:
                    dy = float(feature.attribute(self.dyField()))
                    ds = math.sqrt(ds * ds + dy * dy)
                size = ds
            except:
                pass
        if self.ellipseMode() != self.NoEllipse:
            try:
                ds = abs(float(feature.attribute(self.emaxField())))
                if self.ellipseMode() == self.AxesEllipse:
                    dmin = abs(float(feature.attribute(self.eminField())))
                    ds = max(ds, dmin)
                size += ds * self.ellipseScale()
            except:
                pass
        return size

    def usedAttributes(self):
        attributes = set()
        if self.drawArrow():
            attributes.add(self.dxField())
            if self.mode() == QgsVectorFieldSymbolLayer.Cartesian:
                attributes.add(self.dyField())
        if self.ellipseMode() != self.NoEllipse:
            attributes.add(self.emaxField())
            if self.ellipseMode() == self.AxesEllipse:
                attributes.add(self.eminField())
                # _emaxAzimuth not added as this is currently only used for estimating size
        return attributes

    def saveToString(self):
        """
        Write the layer settings to a string 
        """
        settings = {k: v.name(QColor.HexArgb) if self._types[k] == QColor else v for k, v in self._settings.items()}
        settingstr = json.dumps(settings, sort_keys=True)
        return settingstr

    def readFromString(self, settingstr):
        """
        Read the layer settings from a JSON formatted string
        """
        result = False
        try:
            settings = json.loads(settingstr)
            self.set(ignore_errors=True, **settings)
            result = True
        except:
            pass
        return result


def _createAccessors(key):
    setattr(VectorFieldLayerSettings, key, lambda self: self._settings[key])
    setfunc = "set" + key[0].upper() + key[1:]
    setattr(VectorFieldLayerSettings, setfunc, lambda self, value: self.set(**{key: value}))


for key in VectorFieldLayerSettings._types:
    _createAccessors(key)

