#!/usr/bin/python3

# TODO: restore feature: optional alignment to true north
# TODO: restore feature: scale box
# TODO: restore feature: expressions for vector components and covariance (could do with geometry generator layer)
# TODO: enhancement: configure vector layer rendering using processor function
# TODO: enhancement: Live update

import math

from PyQt5.QtCore import QObject, pyqtSignal

from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsWkbTypes,
    QgsExpressionContextUtils,
    QgsFeatureRequest,
    QgsUnitTypes,
    QgsRenderContext,
)

from .VectorFieldLayerSettings import VectorFieldLayerSettings
from .VectorFieldRendererSettingsImporter import VectorFieldRendererSettingsImporter

VECTOR_SETTINGS_PROP = "vfr_settings"
VECTOR_SCALE_GROUP_PROP = "vfr_scale_group"
VECTOR_SCALE_GROUP_FACTOR_PROP = "vfr_scale_group_factor"
VECTOR_SCALE_VARIABLE_NAME = "vfr_scale"
METRES_TO_UNITS_VARIABLE_NAME = "vfr_metres_to_unit"


class VectorFieldLayerManager(QObject):

    VectorFieldLayerTypeName = "VectorField"

    vectorFieldLayerScaleChanged = pyqtSignal(QgsMapLayer, name="layerScaleChanged")

    @staticmethod
    def isValidLayerType(layer):
        if layer is None:
            return False
        if layer.type() != QgsMapLayer.VectorLayer:
            return False
        if layer.geometryType() != QgsWkbTypes.PointGeometry:
            return False
        return True

    def __init__(self, iface=None):
        QObject.__init__(self)
        self._iface = iface
        self._project = QgsProject.instance()
        if iface is not None:
            iface.mapCanvas().scaleChanged.connect(self.mapScaleChanged)
        self._project.homePathChanged.connect(self.importSettings)

    def unload(self):
        self._iface.mapCanvas().scaleChanged.disconnect(self.mapScaleChanged)
        self._project.homePathChanged.disconnect(self.importSettings)

    def importSettings(self):
        " Import settings from Vector Field Renderer "
        importer = VectorFieldRendererSettingsImporter(self._iface, self, self._project)
        importer.importSettings()

    def renderLayerAsVectorField(self, layer, autoscale=False, propogate=True, **settings):
        settings = VectorFieldLayerSettings(**settings)
        self.applySettingsToLayer(layer, settings)
        if autoscale:
            scale = self.estimateOptimalScale(layer)
            if scale is not None:
                self.setVectorFieldLayerScale(layer, scale, propogate=propogate)

    def applySettingsToLayer(self, layer, settings):
        if not self.isValidLayerType(layer):
            return False
        settingstr = settings.toString()
        layer.setCustomProperty(VECTOR_SETTINGS_PROP, settingstr)
        layer.setCustomProperty(VECTOR_SCALE_GROUP_PROP, settings.scaleGroup())
        layer.setCustomProperty(VECTOR_SCALE_GROUP_FACTOR_PROP, settings.scaleGroupFactor())
        settings.setScaleVariableName(VECTOR_SCALE_VARIABLE_NAME)
        settings.setMetresToUnitsVariableName(METRES_TO_UNITS_VARIABLE_NAME)
        symbol = settings.symbol()
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        self.setVectorFieldLayerScale(layer, settings.scale(), force=True)
        layer.triggerRepaint()
        return True

    def removeSettingsFromLayer(self, layer):
        layer.removeCustomProperty(VECTOR_SETTINGS_PROP)
        layer.removeCustomProperty(VECTOR_SCALE_GROUP_PROP)
        layer.removeCustomProperty(VECTOR_SCALE_GROUP_FACTOR_PROP)
        # Don't remove scale layer variable as may still be used by symbology

    def readSettingsFromLayer(self, layer):
        """
        Read the vector layer settings from a QgsMapLayer custom property.
        Return settings or None if not found or not valid 
        """
        result = None
        settingstr = layer.customProperty(VECTOR_SETTINGS_PROP, "")
        if settingstr != "":
            settings = VectorFieldLayerSettings()
            if settings.readFromString(settingstr):
                scale = self.vectorFieldLayerScale(layer)
                if scale is not None:
                    settings.setScale(scale)
                result = settings
        return result

    def layerScaleGroupScale(self, layer):
        """
        Returns the scale group and scale group scale for a layer
        """
        group = layer.customProperty(VECTOR_SCALE_GROUP_PROP, "")
        if group == "":
            return None, None
        factor = 1.0
        try:
            factor = layer.customProperty(VECTOR_SCALE_GROUP_FACTOR_PROP)
            factor = float(factor)
            if factor <= 0.0:
                factor = 1.0

        except:
            pass
        return

    def findVectorFieldMarkerLayer(self, symbol):
        """
        Identifies a vector field symbol layer in a symbol.  Looks in the 
        symbol or any embedded subsymbols.  Returns the first vector field 
        symbol layer, or None if not found at all.
        """
        for layer in symbol.symbolLayers():
            if layer.layerType() == self.VectorFieldLayerTypeName:
                return layer
        for layer in symbol.symbolLayers():
            subsymbol = layer.subSymbol()
            if subsymbol is not None:
                vectorlayer = self.findVectorFieldMarkerLayer(subsymbol)
                if vectorlayer is not None:
                    return vectorlayer
        return None

    def findLayerVectorField(self, layer):
        """
        Finds a vector field symbol layer in the renderer for a map layer.
        Returns None if the renderer does not include a vector field symbol 
        layer.  

        If a symbol layer is return, this returns a tuple of:
        * a clone of the symbol used by the layer renderer
        * the vector field layer in the cloned symbol
        * a callable to update the symbol in the renderer

        """
        if layer is None:
            return None
        if layer.type() != QgsMapLayer.VectorLayer:
            return None
        renderer = layer.renderer()
        if isinstance(renderer, QgsSingleSymbolRenderer):
            symbol = renderer.symbol()
            setsymbol = renderer.setSymbol
        elif isinstance(renderer, QgsCategorizedSymbolRenderer):
            symbol = renderer.sourceSymbol()
            setsymbol = renderer.updateSymbols
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            symbol = renderer.sourceSymbol()
            setsymbol = renderer.updateSymbols
        else:
            return None

        symbol = symbol.clone()
        vectorlayer = self.findVectorFieldMarkerLayer(symbol)
        if vectorlayer is None:
            return None

        return vectorlayer, symbol, setsymbol

    def isVectorFieldLayer(self, layer):
        """
        Test if layer includes a vector field symbol layer
        """
        if layer is None:
            return False
        return VECTOR_SETTINGS_PROP in layer.customPropertyKeys()

    def vectorFieldLayerScale(self, layer):
        """
        Return the scale of the vector field layer.  Uses the current value
        of a vector field layer if defined, else the scale layer variable.
        If neither is defined return None.
        """
        vector = self.findLayerVectorField(layer)
        if vector is not None:
            vectorlayer = vector[0]
            return vectorlayer.scale()
        layervars = QgsExpressionContextUtils.layerScope(layer)
        if layervars.hasVariable(VECTOR_SCALE_VARIABLE_NAME):
            try:
                scale = float(layervars.variable(VECTOR_SCALE_VARIABLE_NAME))
                return scale
            except:
                pass
        return None

    def setLayerMetresToUnits(self, layer, canvas=None):
        if canvas is None:
            canvas = self._iface.mapCanvas()
        if canvas is None:
            return None
        settings = self.readSettingsFromLayer(layer)
        scope = QgsExpressionContextUtils.layerScope(layer)
        if settings is None:
            scope.removeVariable(METRES_TO_UNITS_VARIABLE_NAME)
            return
        mapsettings = canvas.mapSettings()
        ctx = QgsRenderContext.fromMapSettings(mapsettings)
        units = settings.symbolRenderUnit()
        conversion = ctx.convertMetersToMapUnits(1.0)
        conversion = ctx.convertFromMapUnits(conversion, units)
        QgsExpressionContextUtils.setLayerVariable(layer, METRES_TO_UNITS_VARIABLE_NAME, str(conversion))

    def mapScaleChanged(self):
        for layer in QgsProject.instance().mapLayers().values():
            self.setLayerMetresToUnits(layer)

    def setVectorFieldLayerScale(self, layer, scale, force=False, propogate=True):
        """
        Reset the scale of the vector field layer. Updates the scale value in vector field
        symbol layers and the scale layer variable value.
        If propogate is True then the layers of other layers in the same scale group is updated.
        """
        if not force and not self.isVectorFieldLayer(layer):
            return
        vector = self.findLayerVectorField(layer)
        if vector is not None:
            vectorlayer, symbol, setsymbol = vector
            if not force and scale == vectorlayer.scale():
                return
            vectorlayer.setScale(scale)
            setsymbol(symbol)
        # Set the variables used by symbology expressions
        self.setLayerMetresToUnits(layer)
        QgsExpressionContextUtils.setLayerVariable(layer, VECTOR_SCALE_VARIABLE_NAME, str(scale))
        layer.triggerRepaint()
        self.vectorFieldLayerScaleChanged.emit(layer)
        if propogate:
            self.propogateVectorFieldScale(layer)

    def vectorFieldScaleGroup(self, layer):
        group = layer.customProperty(VECTOR_SCALE_GROUP_PROP, None)
        if group == "":
            group = None
        factor = 1.0
        if group is not None:
            factor = float(layer.customProperty(VECTOR_SCALE_GROUP_FACTOR_PROP, 1.0))
            if factor <= 0:
                factor = 1.0
        return group, factor

    def propogateVectorFieldScale(self, layer):
        """
        Copies the scale of the specified vector layer to other layers in the same scale group.
        """
        scale = self.vectorFieldLayerScale(layer)
        if scale is None:
            return
        if self._iface is None:
            return
        group, factor = self.vectorFieldScaleGroup(layer)
        if group is None or group == "":
            return
        scale /= factor
        for target in self._iface.mapCanvas().layers():
            if target.id() == layer.id():
                continue
            tgroup, tfactor = self.vectorFieldScaleGroup(target)
            if tgroup != group:
                continue
            self.setVectorFieldLayerScale(target, scale * tfactor, propogate=False)

    def rescaleVectorFieldLayer(self, layer, factor):
        scale = self.vectorFieldLayerScale(layer)
        if scale is not None:
            scale *= factor
            self.setVectorFieldLayerScale(layer, scale, propogate=True)

    def estimateOptimalScale(self, layer, canvas=None):
        if canvas is None:
            canvas = self._iface.mapCanvas()
        if canvas is None:
            return None
        settings = self.readSettingsFromLayer(layer)
        if settings is None:
            return None
        mapextent = canvas.extent()
        mapsettings = canvas.mapSettings()
        layerExtent = mapsettings.outputExtentToLayerExtent(layer, mapextent)
        request = QgsFeatureRequest()
        request.setFilterRect(layerExtent)

        attributes = settings.usedAttributes()
        if len(attributes) == 0:
            return None

        # Would be more efficient to select attributes ...
        # Attributes needs to be integer ids...
        # fields = layer.fields()
        # ...
        # request.setSubsetOfAttributes(attributes)

        nFeatures = 0
        nErrors = 0
        maxLength = 0.0
        sumLength = 0.0
        sumLength2 = 0.0

        for feature in layer.getFeatures(request):
            try:
                size = settings.estimatedVectorSize(feature)
                if size is not None:
                    nFeatures += 1
                    maxLength = max(maxLength, size)
                    sumLength += size
                    sumLength2 += size * size
                else:
                    nErrors += 1
            except:
                nErrors += 1
        if nFeatures == 0:
            return None

        # Compute a representative vector size trying to ignore
        # outliers

        size = math.sqrt(sumLength2 / nFeatures)
        size = min(size * 2, maxLength)
        if size <= 0.0:
            return None

        # Compute the desired length on the map - based on the number
        # of features, ie shorter arrows if more points on the map

        mapsize = math.sqrt(mapextent.width() * mapextent.height())
        maplen = mapsize / math.sqrt(16.0 + nFeatures)
        maplen = max(min(maplen, mapsize / 10), mapsize / 100) / 2

        # Set the scale - the scale conversion is required if not
        # using map units for rendering the arrow, as we have
        # calculated the scale in map units

        units = settings.vectorScaleUnit()
        if units != QgsUnitTypes.RenderMapUnits:
            ctx = QgsRenderContext.fromMapSettings(mapsettings)
            size = ctx.convertToMapUnits(size, units)

        scale = maplen / size
        return scale
