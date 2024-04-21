#!/usr/bin/python3
import json
import re
import math

from PyQt5.QtGui import QColor
from qgis.core import (
    QgsArrowSymbolLayer,
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsUnitTypes,
    QgsVectorFieldSymbolLayer,
    QgsEllipseSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleFillSymbolLayer,
    QgsSymbolLayer,
    QgsProperty,
)


class VectorFieldLayerSettings:

    AxesEllipse = 1
    CircularEllipse = 2
    HeightEllipse = 3
    # TODO: Currently don't handle ellipse defined by covariance

    _defaults = dict(
        symbolRenderUnit=QgsUnitTypes.RenderMillimeters,
        baseSize=2.0,
        baseBorderWidth=0.0,
        baseBorderColor=QColor(0, 0, 0),
        fillBase=True,
        baseFillColor=QColor(255, 0, 0),
        drawArrow=True,
        arrowMode=QgsVectorFieldSymbolLayer.Cartesian,
        dxField="",
        dyField="",
        arrowAngleDegrees=True,
        arrowAngleFromNorth=True,
        arrowShaftWidth=0.75,
        arrowHeadWidth=3.0,
        arrowHeadRelativeLength=1.5,
        arrowMaxRelativeHeadSize=0.3,
        arrowBorderWidth=0.0,
        arrowBorderColor=QColor(0, 0, 0),
        fillArrow=True,
        arrowFillColor=QColor(0, 0, 0),
        drawEllipse=True,
        emaxField="",
        eminField="",
        emaxAzimuthField="",
        ellipseMode=AxesEllipse,
        ellipseAngleFromNorth=True,
        ellipseDegrees=True,
        ellipseScale=1.0,
        ellipseBorderWidth=0.7,
        ellipseBorderColor=QColor(0, 0, 0),
        fillEllipse=False,
        ellipseFillColor=QColor(0, 0, 0),
        drawEllipseAxes=False,
        ellipseTickSize=2.0,
        scale=1.0,
        scaleIsMetres=False,
        scaleGroup="",
        scaleGroupFactor=1.0,
    )

    _types = {k: type(v) for k, v in _defaults.items()}
    _normalize = {k.lower(): k for k in _defaults}
    _alias = {
        "lengthfield": {"dxField": None, "arrowMode": "polar"},
        "directionfield": {"dxField": None, "arrowMode": "polar"},
        "heightfield": {"dxField": None, "arrowMode": "height"},
        "radiusfield": {"emaxField": None, "ellipseMode": "circular"},
        "heighterrorfield": {"emaxField": None, "ellipseMode": "height"},
    }
    _arrowModeCodes = {
        "xy": QgsVectorFieldSymbolLayer.Cartesian,
        "polar": QgsVectorFieldSymbolLayer.Polar,
        "height": QgsVectorFieldSymbolLayer.Height,
    }
    _ellipseModeCodes = {
        "axes": AxesEllipse,
        "circular": CircularEllipse,
        "height": HeightEllipse,
    }

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
        self._scaleVariable = ""
        self._metresConversionVariable = ""
        self.set(**settings)

    def set(self, ignore_errors=False, **settings):
        settings = {k.lower(): v for k, v in settings.items()}
        # Handle colour first to allow override of specific colours
        if "color" in settings:
            v = settings["color"]
            for k, t in self._types.items():
                if t == QColor:
                    self.set(**{k: v})
        for k, v in settings.items():
            k = k.lower()
            if k == "color":
                continue
            if k in self._alias:
                alias = {
                    ak: av if av is not None else v for ak, av in self._alias[k].items()
                }
                self.set(**alias)
                continue
            k = self._normalize.get(k, k)
            if k not in self._types:
                if not ignore_errors:
                    raise KeyError(k)
                continue
            if k == "symbolRenderUnit":
                v, ok = QgsUnitTypes.decodeRenderUnit(v)
            elif k == "arrowMode":
                v = self._arrowModeCodes.get(
                    v.lower(), QgsVectorFieldSymbolLayer.Cartesian
                )
            elif k == "ellipseMode":
                v = self._ellipseModeCodes.get(v.lower(), self.AxesEllipse)
            self._settings[k] = self._types[k](v)

    def setScaleVariableName(self, name):
        self._scaleVariable = name

    def setMetresToUnitsVariableName(self, name):
        self._metresConversionVariable = name

    def clone(self):
        clone = VectorFieldLayerSettings()
        clone._settings.update(self._settings)
        return clone

    def sameAs(self, other):
        return self.toString() == other.toString()

    # Functions to construct symbology

    # TODO: Is there an API call for quotedFieldExpression.

    def quotedFieldExpression(self, field):
        return '"' + field + '"'

    def encodedSymbolRenderUnit(self):
        return QgsUnitTypes.encodeUnit(self.symbolRenderUnit())

    def encodedScaleUnit(self):
        if self.scaleIsMetres():
            return QgsUnitTypes.encodeUnit(QgsUnitTypes.RenderMetersInMapUnits)
        return self.encodedSymbolRenderUnit()

    def vectorScaleUnit(self):
        if self.scaleIsMetres():
            return QgsUnitTypes.RenderMetersInMapUnits
        return self.symbolRenderUnit()

    def haveArrow(self):
        if not self.drawArrow() or self.dxField() == "":
            return False
        mode = self.arrowMode()
        if mode in (
            QgsVectorFieldSymbolLayer.Cartesian,
            QgsVectorFieldSymbolLayer.Polar,
        ):
            if self.dyField() == "":
                return False
        return True

    def haveEllipse(self):
        if not self.drawEllipse() or self.emaxField() == "":
            return False
        mode = self.ellipseMode()
        if mode == self.AxesEllipse:
            if self.eminField() == "" or self.emaxAzimuthField() == "":
                return False
        return True

    def basepointSymbol(self):
        """
        Creates a marker symbol for the base point
        """
        symbolRenderUnit = self.encodedSymbolRenderUnit()
        basecolor = QColor(self.baseFillColor())
        if not self.fillBase():
            basecolor.setAlpha(0)
        basepointSymbol = QgsMarkerSymbol.createSimple(
            {
                "name": "circle",
                "size": str(self.baseSize()),
                "color": basecolor.name(QColor.HexArgb),
                "outline_width": str(self.baseBorderWidth()),
                "outline_color": self.baseBorderColor().name(QColor.HexArgb),
                "size_unit": symbolRenderUnit,
                "outline_width_unit": symbolRenderUnit,
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

        if not self.haveArrow():
            return None
        symbolRenderUnit = self.encodedSymbolRenderUnit()
        width = str(self.arrowShaftWidth())
        headWidth = str(self.arrowHeadWidth() / 2.0)
        headLength = str(self.arrowHeadWidth() * self.arrowHeadRelativeLength())
        arrow = QgsArrowSymbolLayer.create(
            {
                "head_type": "0",
                "arrow_type": "0",
                "arrow_width": width,
                "arrow_start_width": width,
                "head_thickness": headWidth,
                "head_length": headLength,
                "arrow_start_width_unit": symbolRenderUnit,
                "arrow_width_unit": symbolRenderUnit,
                "head_thickness_unit": symbolRenderUnit,
                "head_length_unit": symbolRenderUnit,
            }
        )
        arrowFillSymbolLayer = QgsSimpleFillSymbolLayer.create(
            {
                "color": self.arrowFillColor().name(QColor.HexArgb),
                "style": "solid" if self.fillArrow() else "no",
                "outline_style": "solid",
                "outline_width": str(self.arrowBorderWidth()),
                "outline_width_unit": symbolRenderUnit,
                "outline_color": self.arrowBorderColor().name(QColor.HexArgb),
                "joinstyle": "miter",
            }
        )

        shrinkArrow = self.arrowMaxRelativeHeadSize() > 0
        needConversion = (
            self.scaleIsMetres()
            and self.symbolRenderUnit() != QgsUnitTypes.RenderMetersInMapUnits
        )
        # If need a conversion to from vector scale unit to symbol units  then need a metres to units conversion to apply scale
        if needConversion and (
            self._metresConversionVariable == "" or self._scaleVariable == ""
        ):
            shrinkArrow = False

        if self.arrowHeadWidth() * self.arrowHeadRelativeLength() <= 0:
            shrinkArrow = False
        if shrinkArrow:
            if self.arrowMode() == QgsVectorFieldSymbolLayer.Cartesian:
                lengthVar = 'sqrt("{0}"*"{0}"+"{1}"*"{1}")'.format(
                    self.dxField(), self.dyField()
                )
            else:
                lengthVar = 'abs("{0}")'.format(self.dxField())
            if needConversion:
                lengthVar = "(@{0}*{1})".format(
                    self._metresConversionVariable, lengthVar
                )
            lengthVar = "(@{0}*{1})".format(self._scaleVariable, lengthVar)
            scaleVar = "min({0}*{1}/{2},1.0)".format(
                lengthVar, self.arrowMaxRelativeHeadSize(), headLength
            )
            widthVar = "{0}*{1}".format(scaleVar, width)
            headWidthVar = "{0}*{1}".format(scaleVar, headWidth)
            headLengthVar = "{0}*{1}".format(scaleVar, headLength)
            outlineWidthVar = "{0}*{1}".format(scaleVar, self.arrowBorderWidth())
            arrow.setDataDefinedProperty(
                QgsSymbolLayer.PropertyArrowWidth, QgsProperty.fromExpression(widthVar)
            )
            arrow.setDataDefinedProperty(
                QgsSymbolLayer.PropertyArrowStartWidth,
                QgsProperty.fromExpression(widthVar),
            )
            arrow.setDataDefinedProperty(
                QgsSymbolLayer.PropertyArrowHeadThickness,
                QgsProperty.fromExpression(headWidthVar),
            )
            arrow.setDataDefinedProperty(
                QgsSymbolLayer.PropertyArrowHeadLength,
                QgsProperty.fromExpression(headLengthVar),
            )
            arrowFillSymbolLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyStrokeWidth,
                QgsProperty.fromExpression(outlineWidthVar),
            )

        arrowFill = QgsFillSymbol()
        arrowFill.changeSymbolLayer(0, arrowFillSymbolLayer)
        arrow.setSubSymbol(arrowFill)
        return arrow

    def heightErrorSymbolLayers(self):
        if not self.haveEllipse():
            return None
        symbolRenderUnit = self.encodedSymbolRenderUnit()
        scaleUnit = self.encodedScaleUnit()
        tick1 = QgsSimpleMarkerSymbolLayer.create(
            {
                "name": "line",
                "size": "0.0",
                "angle": "0.0",
                "color": self.ellipseBorderColor().name(QColor.HexArgb),
                "line_width": str(self.ellipseBorderWidth()),
                "line_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "size_unit": scaleUnit,
                "joinstyle": "miter",
            }
        )
        tick2 = QgsSimpleMarkerSymbolLayer.create(
            {
                "name": "line",
                "size": str(self.ellipseTickSize()),
                "angle": "90.0",
                "color": self.ellipseBorderColor().name(QColor.HexArgb),
                "line_width": str(self.ellipseBorderWidth()),
                "line_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "size_unit": symbolRenderUnit,
                "offset_unit": scaleUnit,
                "joinstyle": "miter",
            }
        )

        scale = self.ellipseScale() * 2.0
        useproperty = self._scaleVariable != ""
        if useproperty:
            ellipseScale = "(@" + self._scaleVariable + " * " + str(scale) + ")"
        else:
            ellipseScale = str(scale * self.scale())
        sizeExpression = (
            self.quotedFieldExpression(self.emaxField()) + "*" + ellipseScale
        )
        tick3 = tick2.clone()
        tick1.setDataDefinedProperty(
            QgsSymbolLayer.PropertySize, QgsProperty.fromExpression(sizeExpression)
        )
        offset2 = "to_string(0.5*" + sizeExpression + ") || ',0.0'"
        offset3 = "to_string(-0.5*" + sizeExpression + ") || ',0.0'"
        tick2.setDataDefinedProperty(
            QgsSymbolLayer.PropertyOffset, QgsProperty.fromExpression(offset2)
        )
        tick3.setDataDefinedProperty(
            QgsSymbolLayer.PropertyOffset, QgsProperty.fromExpression(offset3)
        )
        return [tick1, tick2, tick3]

    def ellipseSymbolLayer(self):

        if not self.haveEllipse():
            return None
        symbolRenderUnit = self.encodedSymbolRenderUnit()
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
                "symbol_name": ("cross" if self.drawEllipseAxes() else "circle"),
                "angle": "0",
                "outline_width": str(self.ellipseBorderWidth()),
                "outline_width_unit": symbolRenderUnit,
                "outline_color": self.ellipseBorderColor().name(QColor.HexArgb),
                "fill_color": fillColor,
            }
        )
        scale = self.ellipseScale() * 2.0  # As symbol measured on diameter
        useproperty = self._scaleVariable != ""
        if useproperty:
            ellipseScale = "(@" + self._scaleVariable + " * " + str(scale) + ")"
        else:
            ellipseScale = str(scale * self.scale())
        widthExpression = (
            self.quotedFieldExpression(self.emaxField()) + "*" + ellipseScale
        )

        if self.ellipseMode() == self.AxesEllipse:
            heightExpression = (
                self.quotedFieldExpression(self.eminField()) + "*" + ellipseScale
            )
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyWidth,
                QgsProperty.fromExpression(widthExpression),
            )
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyHeight,
                QgsProperty.fromExpression(heightExpression),
            )
            angleExpression = self.quotedFieldExpression(self.emaxAzimuthField())
            if not self.ellipseDegrees():
                angleExpression = "radians(" + angleExpression + ")"
            if self.ellipseAngleFromNorth():
                angleExpression = "(90.0-" + angleExpression + ")"
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyAngle,
                QgsProperty.fromExpression(angleExpression),
            )
        elif self.ellipseMode() == self.CircularEllipse:
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyWidth,
                QgsProperty.fromExpression(widthExpression),
            )
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyHeight,
                QgsProperty.fromExpression(widthExpression),
            )
        elif self.ellipseMode() == self.HeightEllipse:
            ellipseLayer.setDataDefinedProperty(
                QgsSymbolLayer.PropertyHeight,
                QgsProperty.fromExpression(widthExpression),
            )
        else:
            return None
        return ellipseLayer

    def errorSymbolLayers(self):
        if not self.haveEllipse():
            return None
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
        vfl = QgsVectorFieldSymbolLayer()
        vfl.setXAttribute(self.dxField())
        if self.arrowMode() == QgsVectorFieldSymbolLayer.Height:
            vfl.setYAttribute(self.dxField())
        else:
            vfl.setYAttribute(self.dyField())
        vfl.setScale(self.scale())
        vfl.setVectorFieldType(self.arrowMode())
        angleOrientation = (
            QgsVectorFieldSymbolLayer.ClockwiseFromNorth
            if self.arrowAngleFromNorth()
            else QgsVectorFieldSymbolLayer.AntiClockwiseFromEast
        )
        angleUnit = (
            QgsVectorFieldSymbolLayer.Degrees
            if self.arrowAngleDegrees()
            else QgsVectorFieldSymbolLayer.Radians
        )
        vfl.setAngleOrientation(angleOrientation)
        vfl.setAngleUnits(angleUnit)
        if self.scaleIsMetres():
            vfl.setDistanceUnit(QgsUnitTypes.RenderMetersInMapUnits)
        else:
            vfl.setDistanceUnit(self.symbolRenderUnit())

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
        if self.haveArrow():
            try:
                ds = abs(float(feature.attribute(self.dxField())))
                if self.arrowMode() == QgsVectorFieldSymbolLayer.Cartesian:
                    dy = float(feature.attribute(self.dyField()))
                    ds = math.sqrt(ds * ds + dy * dy)
                size = ds
            except:
                pass
        if self.haveEllipse():
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
        if self.haveArrow():
            attributes.add(self.dxField())
            if self.arrowMode() == QgsVectorFieldSymbolLayer.Cartesian:
                attributes.add(self.dyField())
        if self.haveEllipse():
            attributes.add(self.emaxField())
            if self.ellipseMode() == self.AxesEllipse:
                attributes.add(self.eminField())
                # _emaxAzimuth not added as this is currently only used for estimating size
        return attributes

    def encode(self, codes, value, default):
        result = default
        for k, v in codes.items():
            if v == value:
                result = k
        return result

    def toString(self, indent=None):
        """
        Write the layer settings to a string
        """
        settings = {
            k: (
                v.name(QColor.HexArgb)
                if self._types[k] == QColor
                else (
                    QgsUnitTypes.encodeUnit(QgsUnitTypes.RenderUnit(v)).lower()
                    if k == "symbolRenderUnit"
                    else (
                        self.encode(self._arrowModeCodes, v, "xy")
                        if k == "arrowMode"
                        else (
                            self.encode(self._ellipseModeCodes, v, "axes")
                            if k == "ellipseMode"
                            else v
                        )
                    )
                )
            )
            for k, v in self._settings.items()
        }
        settingstr = json.dumps(settings, sort_keys=True, indent=indent)
        return settingstr

    def readFromString(self, settingstr, ignore_errors=True):
        """
        Read the layer settings from a JSON formatted string
        """
        result = False
        try:
            settings = json.loads(settingstr)
            self.set(ignore_errors=ignore_errors, **settings)
            result = True
        except:
            if not ignore_errors:
                raise
        return result


def _createAccessors(key, ktype):
    setattr(VectorFieldLayerSettings, key, lambda self: self._settings[key])
    setfunc = "set" + key[0].upper() + key[1:]

    def func(self, value):
        self._settings[key] = ktype(value)

    setattr(VectorFieldLayerSettings, setfunc, func)


for key, ktype in VectorFieldLayerSettings._types.items():
    _createAccessors(key, ktype)
