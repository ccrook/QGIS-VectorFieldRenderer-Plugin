#!/usr/bin/python3
from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def tryit():
    _degrees = True
    _mode = QgsVectorFieldSymbolLayer.Cartesian
    _angleOrientation = QgsVectorFieldSymbolLayer.ClockwiseFromNorth
    _angleUnits = QgsVectorFieldSymbolLayer.Degrees
    _scale = 1.0
    _fieldname = [None] * 5
    _unitType = QgsUnitTypes.RenderMillimeters
    _legendText = ""
    _showInScaleBox = True
    _scaleBoxText = ""
    _scaleGroup = ""
    _scaleGroupFactor = 1.0
    #_ellipseMode = VectorFieldRenderer.AxesEllipse
    _ellipseAngleFromNorth = True
    _ellipseDegrees = True
    _ellipseScale = 1.0
    _vectorIsTrueNorth = True
    _useMapNorth = True
    _layerId = None
    _arrowShaftSize = 1.5
    _arrowRelativeHeadSize = 0.3
    _arrowMaxHeadSize = 3.0
    _arrowBorderWidth = 0.0
    _arrowFillColor = QColor(0, 0, 0)
    _fillArrow = True
    _arrowBorderColor = QColor(0, 0, 0)
    _arrowHeadShape = (0, -1.0, -0.7)
    _baseSize = 2.0
    _ellipseTickSize = 2.0
    _fillBase = True
    _baseFillColor = QColor(255, 0, 0)
    _baseBorderWidth = 0.0
    _baseBorderColor = QColor(0, 0, 0)
    _ellipseBorderWidth = 0.7
    _ellipseBorderColor = QColor(0, 0, 0)
    _ellipseFillColor = QColor(0, 0, 0)
    _fillEllipse = False
    _drawEllipse = True
    _drawEllipseAxes = False

    # 
    # What are these - do I need to do anything with them?
    # vfl.setMapUnitScale()
    # vfl.setOutputUnit()
    # vfl.setDistanceMapUnitScale()
    symbolUnit = "MM"
    basePointSymbol = QgsMarkerSymbol.createSimple(
    {
        "name": "circle",
        "size": str(_baseSize),
        "color": _baseFillColor.name(QColor.HexArgb),
        "outline_width": str(_baseBorderWidth),
        "outline_color": _baseBorderColor.name(QColor.HexArgb),
        "size_unit": symbolUnit,
        "outline_width_unit": symbolUnit,
    }
    )
    basePointLine = QgsMarkerLineSymbolLayer()
    basePointLine.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
    basePointLine.setSubSymbol(basePointSymbol)

    arrow = QgsArrowSymbolLayer.create(
        {
            "head_type": "0",
            "arrow_type": "0",
            "arrow_width": str(_arrowShaftSize),
            "arrow_start_width": str(_arrowShaftSize),
            "arrow_head_length": str(
                _arrowMaxHeadSize
                * (_arrowHeadShape[0] - _arrowHeadShape[1])
            ),
            "arrow_head_width": str(_arrowMaxHeadSize),
            "arrow_start_width_unit": symbolUnit,
            "arrow_width_unit": symbolUnit,
            "arrow_head_length_unit": symbolUnit,
        }
    )
    arrowFill = QgsSimpleFillSymbolLayer.create(
        {
            "color": _arrowFillColor.name(QColor.HexArgb),
            "style": "solid" if _fillArrow else "no",
            "outline_style": "solid",
            "outline_width": str(_arrowBorderWidth),
            "outline_width_unit": symbolUnit,
            "outline_color": _arrowBorderColor.name(QColor.HexArgb),
        }
    )
    arrowFillSymbol=QgsFillSymbol()
    arrowFillSymbol.changeSymbolLayer(0,arrowFill)
    arrow.setSubSymbol(arrowFillSymbol)

    # ellipseLine=QgsMarkerLineSymbolLayer()
    # ellipseLine.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
    # ellipse=QgsEllipseSymbolLayer()

    vfl = QgsVectorFieldSymbolLayer()
    vfl.setXAttribute(_fieldname[0])
    vfl.setYAttribute(_fieldname[0])
    vfl.setScale(_scale)
    vfl.setVectorFieldType(_mode)
    vfl.setAngleOrientation(_angleOrientation)
    vfl.setAngleUnits(_angleUnits)
    vfl.setDistanceUnit(_unitType)
    symbol=QgsLineSymbol()
    symbol.changeSymbolLayer(0,basePointLine)
    symbol.appendSymbolLayer(arrow)

    vfl.setSubSymbol(symbol)
    vflSymbol = QgsMarkerSymbol()
    vflSymbol.changeSymbolLayer(0,vfl)

    renderer = QgsSingleSymbolRenderer(vflSymbol)
    layer=iface.activeLayer()
    layer.setRenderer(renderer)
    layer.triggerRepaint()

tryit()    