#!/usr/bin/python3

# TODO: Fix QGIS error on exit
# TODO: copy/paste/save vector settings
# TODO: Handling of height error ellipse (ticks on line, build from 3 line symbols?)
# TODO: look at vector scale options (map metres)
# TODO: Check alternative map units (map metres?)
# TODO: Handle map units for size of vector/ellipse
# TODO: scale down arrow when vector small
# TODO: restore feature - no alignment to true north
# TODO: Live update
# TODO: fix handling of scale groups
# FIX: reinstall autoscale feature

from qgis.core import (
    QgsMapLayerType,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsWkbTypes,
    QgsExpressionContextUtils,
)

from .VectorFieldLayerSettings import VectorFieldLayerSettings

VECTOR_SETTINGS_PROP = "vfr_settings"
VECTOR_SCALE_VARIABLE_NAME = "vfr_scale"
VECTOR_SCALE_GROUP_PROP = "vfr_scale_group"
VECTOR_SCALE_GROUP_FACTOR_PROP = "vfr_scale_group_factor"


class VectorFieldLayerManager:

    VectorFieldLayerTypeName = "VectorField"

    @staticmethod
    def isValidLayerType(layer):
        if layer is None:
            return False
        if layer.type() != QgsMapLayerType.VectorLayer:
            return False
        if layer.geometryType() != QgsWkbTypes.PointGeometry:
            return False
        return True

    def __init__(self, iface=None):
        self._iface = iface

    def applySettingsToLayer(self, layer, settings):
        if not self.isValidLayerType(layer):
            return False
        settingstr = settings.saveToString()
        layer.setCustomProperty(VECTOR_SETTINGS_PROP, settingstr)
        layer.setCustomProperty(VECTOR_SCALE_GROUP_PROP, settings.scaleGroup())
        layer.setCustomProperty(VECTOR_SCALE_GROUP_FACTOR_PROP, settings.scaleGroupFactor())
        settings.setScaleVariableName(VECTOR_SCALE_VARIABLE_NAME)
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
        # FIX scale = VectorFieldU
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
        if layer.type() != QgsMapLayerType.VectorLayer:
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
        return VECTOR_SETTINGS_PROP in layer.customPropertyKeys()

    def vectorFieldLayerScale(self, layer):
        """
        Return the scale of the vector field layer.  Uses the current value
        of a vector field layer if defined, else the scale layer variable.
        If neither is defined return None.
        """
        # TODO: Fix this - ellipse without arrow doesn't include this :-(
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
            vectorlayer.setScale(scale)
            setsymbol(symbol)
        # Set a variable that can be used by symbology expressions
        QgsExpressionContextUtils.setLayerVariable(layer, VECTOR_SCALE_VARIABLE_NAME, str(scale))
        layer.triggerRepaint()
        if propogate:
            self.propogateVectorFieldScale(layer)

    def vectorFieldScaleGroup(self, layer):
        group = layer.customProperty(VECTOR_SCALE_GROUP_PROP, None)
        if group == "":
            group = None
        factor = 1.0
        if group is not None:
            factor = layer.customProperty(VECTOR_SCALE_GROUP_FACTOR_PROP, 1.0)
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
