

from PyQt4.QtGui import *
from qgis.core import QgsRendererV2Registry, QgsSymbolLayerV2Registry

from VectorFieldRendererMetadata import VectorFieldRendererMetadata
from VectorFieldRenderer import VectorFieldRenderer
from VectorFieldRendererController import VectorFieldRendererController

class Plugin:

    Name = "VectorFieldRenderer"
    LongName=""
    Version=""
    Author=""
    PluginUrl="http://pygqgis.org/repo/contributed"

    def __init__( self, iface, longname, version, author ):
        self._iface = iface
        Plugin.LongName = longname
        Plugin.Version = version
        Plugin.Author = author
        VectorFieldRenderer.iface = iface
        VectorFieldRenderer.plugin = self

    def initGui(self):
        # QgsSymbolLayerV2Registry.instance().addSymbolLayerType( VectorArrowMarkerMetadata() )
        QgsRendererV2Registry.instance().addRenderer( VectorFieldRendererMetadata() )
        self._controller = VectorFieldRendererController(self._iface)

    def unload(self):      
        self._controller.unload()
        pass

    def canBeUninstalled(self):
        return self._controller.canBeUninstalled()

    def save(self,doc):
        pe = doc.createElement("plugin")
        pe.setAttribute("name",Plugin.Name)
        pe.setAttribute("version",Plugin.Version)
        pe.setAttribute("url",Plugin.PluginUrl)
        return pe


