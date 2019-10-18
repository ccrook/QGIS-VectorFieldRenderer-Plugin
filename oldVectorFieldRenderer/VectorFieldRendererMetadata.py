# Set up the metadata required to implement a vector field renderer

from qgis.core import QgsRendererAbstractMetadata
from PyQt5.QtGui import *

from .VectorFieldRenderer import VectorFieldRenderer
from .VectorFieldRendererWidget import VectorFieldRendererWidget
from . import VectorFieldRendererResources

class VectorFieldRendererMetadata(QgsRendererAbstractMetadata):

    def __init__(self,controller):
        self._controller=controller
        QgsRendererAbstractMetadata.__init__(
           self, 
           VectorFieldRenderer.rendererName, 
           "Vector field",
           QIcon(QPixmap(":plugins/VectorFieldRenderer/VectorFieldRendererIcon.png","png")))

    def createRenderer(self, element):
        vfr = VectorFieldRenderer()
        if element: vfr.reload(element)
        return vfr

    def createRendererWidget(self, layer, style, renderer):
        return VectorFieldRendererWidget(layer,style,renderer,self._controller)
 
