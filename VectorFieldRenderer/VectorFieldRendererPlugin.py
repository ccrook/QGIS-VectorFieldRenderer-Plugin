

from PyQt4.QtGui import *
from qgis.core import QgsRendererV2Registry, QgsSymbolLayerV2Registry

from .VectorFieldRendererMetadata import VectorFieldRendererMetadata
from .VectorFieldRenderer import VectorFieldRenderer
from .VectorFieldRendererController import VectorFieldRendererController

class Plugin:

    Name = "VectorFieldRenderer"
    Version="3.1"

    def __init__( self, iface ):
        self._iface = iface
        VectorFieldRenderer.iface = iface
        VectorFieldRenderer.plugin = self

    def initGui(self):
        # QgsSymbolLayerV2Registry.instance().addSymbolLayerType( VectorArrowMarkerMetadata() )
        self._controller = VectorFieldRendererController(self._iface)
        self._metadata=VectorFieldRendererMetadata(self._controller)
        QgsRendererV2Registry.instance().addRenderer( self._metadata ) 

    def unload(self):      
        self._controller.unload()
        pass

    def canBeUninstalled(self):
        return self._controller.canBeUninstalled()

    def save(self,doc):
        pe = doc.createElement("plugin")
        pe.setAttribute("name",Plugin.Name)
        pe.setAttribute("version",Plugin.Version)
        return pe


