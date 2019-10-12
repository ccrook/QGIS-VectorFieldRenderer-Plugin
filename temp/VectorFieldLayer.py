#!/usr/bin/python3
from qgis.core import (
    QgsUnitTypes, 
    QgsVectorFieldSymbolLayer,
    QgsMarkerSymbol, 
    QgsMarkerLineSymbolLayer,
    QgsArrowSymbolLayer,
    QgsSimpleFillSymbolLayer,
    QgsFillSymbol,
)

from PyQt5.QtCore import QColor
from PyQt5.QtGui import *

class VectorFieldLayer:

    def __init__( self ):
        self._degrees = True
        self._mode = QgsVectorFieldSymbolLayer.Cartesian
        self._angleOrientation = QgsVectorFieldSymbolLayer.ClockwiseFromNorth
        self._angleUnits = QgsVectorFieldSymbolLayer.Degrees
        self._scale = 1.0
        self._fieldname = [None] * 5
        self._unitType = QgsUnitTypes.RenderMillimeters
        self._scaleGroup = ""
        self._scaleGroupFactor = 1.0
        #self._ellipseMode = VectorFieldRenderer.AxesEllipse
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

    def basepointSymbolLayer( self ):
        '''
        Creates a line symbol layer for the base point of the arrow.  This is a marker line
        with a marker at the first vertex.
        '''        
        symbolUnit=QgsUnitTypes.toAbbreviatedString()
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

    def arrowSymbolLayer( self ):
        symbolUnit=QgsUnitTypes.toAbbreviatedString()
        arrow = QgsArrowSymbolLayer.create(
            {
                "head_type": "0",
                "arrow_type": "0",
                "arrow_width": str(self._arrowShaftSize),
                "arrow_start_width": str(self._arrowShaftSize),
                "arrow_head_length": str(
                    self._arrowMaxHeadSize
                    * (_arrowHeadShape[0] - self._arrowHeadShape[1])
                ),
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

    def ellipseSymbolLayer( self ):

        symbolUnit=QgsUnitTypes.toAbbreviatedString()
        ellipseLine=None
        #ellipseLine=QgsMarkerLineSymbolLayer()
        #ellipseLine.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
        #ellipse=QgsEllipseSymbolLayer()
        return ellipseLine()

        vfl = QgsVectorFieldSymbolLayer()
        vfl.setXAttribute(_fieldname[0])
        vfl.setYAttribute(_fieldname[0])
        vfl.setScale(_scale)
        vfl.setVectorFieldType(_mode)
        vfl.setAngleOrientation(_angleOrientation)
        vfl.setAngleUnits(_angleUnits)
        vfl.setDistanceUnit(_unitType)
        symbol=QgsLineSymbol()
        symbol.changeSymbolLayer(0,basepointLine)
        symbol.appendSymbolLayer(arrow)

        vfl.setSubSymbol(symbol)
        vflSymbol = QgsMarkerSymbol()
        vflSymbol.changeSymbolLayer(0,vfl)

        renderer = QgsSingleSymbolRenderer(vflSymbol)
        layer=iface.activeLayer()
        layer.setRenderer(renderer)
        layer.triggerRepaint()
