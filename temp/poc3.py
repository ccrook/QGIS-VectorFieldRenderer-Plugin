#!/usr/bin/python3
from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

VectorFieldLayerTypeName='VectorField'

def findVectorFieldMarkerLayer( symbol ):
    for layer in symbol.symbolLayers():
        if layer.layerType() == VectorFieldLayerTypeName:
            return layer
    for ilayer,layer in enum(symbol.symbolLayers()):
        subsymbol=layer.subSymbol()
        if subsymbol is not None:
            vectorlayer=findVectorFieldMarkerLayer(subsymbol)
            if vectorlayer is not None:
                return vectorlayer
    return None

def findLayerVectorField( layer ):
    if layer.type() != QgsMapLayerType.VectorLayer:
        return None
    renderer=layer.renderer()
    if isinstance(renderer,QgsSingleSymbolRenderer):
        symbol=renderer.symbol()
        setsymbol=renderer.setSymbol
    elif isinstance(renderer,QgsCategorizedSymbolRenderer):
        symbol=renderer.sourceSymbol()
        setsymbol=renderer.updateSymbols
    elif isinstance(renderer,QgsGraduatedSymbolRenderer):
        symbol=renderer.sourceSymbol()
        setsymbol=renderer.updateSymbols
    else:
        return None        

    symbol=symbol.clone()
    vectorlayer=findVectorFieldMarkerLayer(symbol)

    return vectorlayer, symbol,setsymbol

def scaleVectorLayer( layer, factor ):
    vector=findLayerVectorField(layer)
    if vector is None:
        return
    vectorlayer,symbol,setsymbol=vector
    vectorlayer.setScale(vectorlayer.scale()*factor)
    print("Scale {0}".format(vectorlayer.scale()))
    setsymbol(symbol)
    layer.triggerRepaint()


scaleVectorLayer(iface.activeLayer(),2)   