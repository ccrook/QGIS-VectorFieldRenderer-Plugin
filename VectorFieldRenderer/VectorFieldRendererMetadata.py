# Set up the metadata required to implement a vector field renderer

from qgis.core import QgsRendererV2AbstractMetadata
from PyQt4.QtGui import *

from .VectorFieldRenderer import VectorFieldRenderer
from .VectorFieldRendererWidget import VectorFieldRendererWidget
from . import VectorFieldRendererResources

class VectorFieldRendererMetadata(QgsRendererV2AbstractMetadata):
    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(
           self, 
           VectorFieldRenderer.rendererName, 
           "Vector field",
           QIcon(QPixmap(":plugins/VectorFieldRenderer/VectorFieldRendererIcon.png","png")))

    def createRenderer(self, element):
        vfr = VectorFieldRenderer()
        if element: vfr.reload(element)
        return vfr

    def createRendererWidget(self, layer, style, renderer):
        return VectorFieldRendererWidget(layer,style,renderer)
 
