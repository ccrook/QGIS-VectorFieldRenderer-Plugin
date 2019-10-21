import sys
import os.path
import importlib

modpath = "/home/ccrook/projects/qgis/plugins/qgis3/VectorFieldRenderer"
if sys.path[0] != modpath:
    sys.path.insert(0, modpath)

import VectorFieldLayerManager.VectorFieldLayerSettings
import VectorFieldLayerManager.VectorFieldLayerManager
importlib.reload(VectorFieldLayerManager.VectorFieldLayerSettings)
importlib.reload(VectorFieldLayerManager.VectorFieldLayerManager)

def evaluateFeatures():
    canvas = iface.mapCanvas()
    mgr=VectorFieldLayerManager.VectorFieldLayerManager.VectorFieldLayerManager(iface)
    ms=canvas.mapSettings()
    ctx = QgsRenderContext.fromMapSettings(ms)
    layer = canvas.currentLayer()
    #layerscope = layer.expressionContextScope()
    #ctx.appendScope(layerscope)
    #symcontext = QgsSymbolRenderContext(ctx,QgsUnitTypes.RenderMillimeters)  # what is context!
    settings=mgr.readSettingsFromLayer(layer)
    symbol=settings.symbol()
    request = QgsFeatureRequest()
    for f in iface.mapCanvas().currentLayer().getFeatures(request):
        ctx.expressionContext().setFeature(f)
        size = symbol.size(symcontext)
        print("Feature", f.id(), size.width(), size.height())


evaluateFeatures()

# tests/src/python/test_qgssymbollayer.py
#         # Test usedAttributes
#         ctx = QgsRenderContext.fromMapSettings(ms)
#         ctx.expressionContext().appendScope(points_layer.createExpressionContextScope())
#         # for symbol layer
#         self.assertCountEqual(layer.usedAttributes(ctx), {'Class'})
#         # for symbol
#         self.assertCountEqual(symbol.usedAttributes(ctx), {'Class'})
#         # for symbol renderer
#         self.assertCountEqual(points_layer.renderer().usedAttributes(ctx), {'Class'})

# tests/src/python/test_qgssymbol.py
