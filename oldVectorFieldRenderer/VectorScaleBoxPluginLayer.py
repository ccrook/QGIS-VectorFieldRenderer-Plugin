
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qgis.core import *

from .VectorFieldRenderer import VectorFieldRenderer
 
class VectorScaleBoxPluginLayer(QgsPluginLayer):

    LayerType="vectorfieldrendererscalebox"
      
    class Type(QgsPluginLayerType):

        def __init__(self):
            QgsPluginLayerType.__init__(self, VectorScaleBoxPluginLayer.LayerType)
        
        def createLayer(self):
            return VectorScaleBoxPluginLayer()
        
        def showLayerProperties(self, layer):
            layer.showDialog()
            return True
  
    def __init__(self):
        QgsPluginLayer.__init__(self, VectorScaleBoxPluginLayer.LayerType, "Vector scale box")
        self.setValid(True)
        self._scalebox = None
    
    # QGIS3 - need to implement clone()
    # QGIS3 - need to implement createMapRenderer() instead of draw
    #def draw(self, rendererContext):
    #    if self._scalebox != None:
    #        self._scalebox.render( rendererContext )
    #    return True
    
    def readXml(self, node):
        # custom properties
        return True
    
    def writeXml(self, node, doc):
        element = node.toElement();
        # write plugin layer type to project  (essential to be read from project)
        element.setAttribute("type", "plugin")
        element.setAttribute("name", VectorScaleBoxPluginLayer.LayerType);
        # custom properties
        return True
    
    def setScaleBox(self, scalebox):
        self._scalebox = scalebox

    def repaintScaleBox( self ):
        self.repaintRequested.emit()
  
    def showDialog(self):
        if self._scalebox:
            from .VectorScaleBoxOptionsDialog import VectorScaleBoxOptionsDialog
            if VectorScaleBoxOptionsDialog.getOptions( self._scalebox ):
                self.repaintScaleBox()
    
