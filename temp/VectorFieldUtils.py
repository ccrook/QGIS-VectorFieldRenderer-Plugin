#!/usr/bin/python3
from qgis.core import QgsMapLayerType, QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer

# from PyQt5.QtCore import *
# from PyQt5.QtGui import *

SCALE_PROP = "vfr_scale"
SCALE_GROUP_PROP = "vfr_scale_group"
SCALE_GROUP_FACTOR_PROP = "vfr_scale_group_factor"


class VectorFieldUtils:

    VectorFieldLayerTypeName = "VectorField"

    @staticmethod
    def findVectorFieldMarkerLayer(symbol):
        """
        Identifies a vector field symbol layer in a symbol.  Looks in the 
        symbol or any embedded subsymbols.  Returns the first vector field 
        symbol layer, or None if not found at all.
        """
        for layer in symbol.symbolLayers():
            if layer.layerType() == VectorFieldUtils.VectorFieldLayerTypeName:
                return layer
        for layer in symbol.symbolLayers():
            subsymbol = layer.subSymbol()
            if subsymbol is not None:
                vectorlayer = VectorFieldUtils.findVectorFieldMarkerLayer(subsymbol)
                if vectorlayer is not None:
                    return vectorlayer
        return None

    @staticmethod
    def findLayerVectorField(layer):
        """
        Finds a vector field symbol layer in the renderer for a map layer.
        Returns None if the renderer does not include a vector field symbol 
        layer.  

        If a symbol layer is return, this returns a tuple of:
        * a clone of the symbol used by the layer renderer
        * the vector field layer in the cloned symbol
        * a callable to update the symbol in the renderer

        """
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
        vectorlayer = VectorFieldUtils.findVectorFieldMarkerLayer(symbol)
        if vectorlayer is None:
            return None

        return vectorlayer, symbol, setsymbol

    @staticmethod
    def isVectorFieldLayer(layer):
        """
        Test if layer includes a vector field symbol layer
        """
        vector = VectorFieldUtils.findLayerVectorField(layer)
        return vector is not None

    @staticmethod
    def vectorFieldLayerScale(layer):
        """
        Return the scale of the vector field layer.  Can either 
        scale by a factor, or set a specific scale.   If a scale 
        is defined then it overrides a factor setting.
        """
        vector = VectorFieldUtils.findLayerVectorField(layer)
        if vector is None:
            return None
        vectorlayer = vector[0]
        return vectorlayer.scale()

    @staticmethod
    def setVectorFieldLayerScale(layer, scale, scaleGroup=None, scaleGroupFactor=None, propogate=True):
        """
        Reset the scale of the vector field layer.  Optionally can also define
        the scaleGroup and scaleGroupFactor custom properties, which are used to keep
        the vector scale of layers the same.  
        If propogate is True then the layers of other layers in the same scale group is updated.
        """
        vector = VectorFieldUtils.findLayerVectorField(layer)
        if vector is None:
            return None
        vectorlayer, symbol, setsymbol = vector
        vectorlayer.setScale(scale)
        setsymbol(symbol)
        layer.setCustomProperty(SCALE_PROP, scale)
        VectorFieldUtils.setVectorFieldScaleGroup(layer, scaleGroup, scaleGroupFactor)
        layer.triggerRepaint()
        if propogate:
            VectorFieldUtils.propogateVectorFieldScale(layer)

    @staticmethod
    def setVectorFieldScaleGroup(layer, group, factor):
        if group is not None:
            layer.setCustomProperty(SCALE_GROUP_PROP, group)
        if factor is not None:
            layer.setCustomProperty(SCALE_GROUP_FACTOR_PROP, factor)

    @staticmethod
    def vectorFieldScaleGroup(layer):
        group = layer.customProperty(SCALE_GROUP_PROP, None)
        if group == "":
            group = None
        factor = layer.customProperty(SCALE_GROUP_FACTOR_PROP, 1.0)
        if factor <= 0:
            factor = 1.0
        return group, factor

    @staticmethod
    def propogateVectorFieldScale(layer):
        """
        Copies the scale of the specified vector layer to other layers in the same scale group.
        """
        scale = VectorFieldUtils.vectorFieldLayerScale(layer)
        if scale is None:
            return
        group, factor = VectorFieldUtils.vectorFieldScaleGroup(layer)
        if group is None or group == "":
            return
        scale /= factor
        for target in findMapLayers():
            if target.id() == layer.id():
                continue
            tgroup, tfactor = VectorFieldUtils.vectorFieldScaleGroup(target)
            if tgroup != group:
                continue
            VectorFieldUtils.setVectorFieldLayerScale(target, scale * tfactor, propogate=False)

    @staticmethod
    def rescaleVectorField(layer, factor):
        scale = VectorFieldUtils.vectorFieldLayerScale(layer)
        if scale is not None:
            scale *= factor
            VectorFieldUtils.setVectorFieldLayerScale(layer, scale, propogate=True)
