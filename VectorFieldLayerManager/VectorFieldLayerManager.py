#!/usr/bin/python3

# TODO: get ellipse rendering working
# TODO: look at vector scale options (map metres)
# TODO: restore feature - no alignment to true north
# TODO: scale down arrow when vector small
# TODO: Move all property names into a common module
# TODO: Handling of drawing no arrow
# TODO: Handle map units for size of vector/ellipse
# TODO: Check alternative map units (map metres?)
# TODO: Save/reuse symbology
# TODO: Live update
# FIXME: fix handling of scale groups
# FIXME: reinstall autoscale feature

from qgis.core import (
    QgsMapLayerType,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsWkbTypes,
)

SCALE_PROP = "vfr_scale"
SCALE_GROUP_PROP = "vfr_scale_group"
SCALE_GROUP_FACTOR_PROP = "vfr_scale_group_factor"


class VectorFieldLayerManager:

    VectorFieldLayerTypeName = "VectorField"

    def __init__(self, iface=None):
        self._iface = iface

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
        vector = self.findLayerVectorField(layer)
        return vector is not None

    def vectorFieldLayerScale(self, layer):
        """
        Return the scale of the vector field layer.  Can either 
        scale by a factor, or set a specific scale.   If a scale 
        is defined then it overrides a factor setting.
        """
        vector = self.findLayerVectorField(layer)
        if vector is None:
            return None
        vectorlayer = vector[0]
        return vectorlayer.scale()

    def setVectorFieldLayerScale(self, layer, scale, scaleGroup=None, scaleGroupFactor=None, propogate=True):
        """
        Reset the scale of the vector field layer.  Optionally can also define
        the scaleGroup and scaleGroupFactor custom properties, which are used to keep
        the vector scale of layers the same.  
        If propogate is True then the layers of other layers in the same scale group is updated.
        """
        vector = self.findLayerVectorField(layer)
        if vector is None:
            return None
        vectorlayer, symbol, setsymbol = vector
        vectorlayer.setScale(scale)
        setsymbol(symbol)
        layer.setCustomProperty(SCALE_PROP, scale)
        self.setVectorFieldScaleGroup(layer, scaleGroup, scaleGroupFactor)
        layer.triggerRepaint()
        if propogate:
            self.propogateVectorFieldScale(layer)

    def setVectorFieldScaleGroup(self, layer, group, factor):
        if group is not None:
            layer.setCustomProperty(SCALE_GROUP_PROP, group)
        if factor is not None:
            layer.setCustomProperty(SCALE_GROUP_FACTOR_PROP, factor)

    def vectorFieldScaleGroup(self, layer):
        group = layer.customProperty(SCALE_GROUP_PROP, None)
        if group == "":
            group = None
        factor = 1.0
        if group is not None:
            factor = layer.customProperty(SCALE_GROUP_FACTOR_PROP, 1.0)
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
