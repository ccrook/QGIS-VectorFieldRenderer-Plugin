
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from VectorFieldRenderer import VectorFieldRenderer
 
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
    
    def draw(self, rendererContext):
        if self._scalebox != None:
            self._scalebox.render( rendererContext )
        return True
    
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
        self.repaintScaleBox()

    def repaintScaleBox( self ):
        self.setCacheImage(None)
        self.emit(SIGNAL("repaintRequested()"))
  
    def showDialog(self):
        if self._scalebox:
            from VectorScaleBoxOptionsDialog import VectorScaleBoxOptionsDialog
            if VectorScaleBoxOptionsDialog.getOptions( self._scalebox ):
                self.repaintScaleBox()
    
