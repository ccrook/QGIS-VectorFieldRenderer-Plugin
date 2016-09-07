import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from .VectorFieldRendererWidget import VectorFieldRendererWidget

# Vector field renderer layer dialog - for use when the python bindings layer properties
# fail to load the renderer interface

class VectorFieldRendererLayerDialog(QDialog):

    def __init__(self,layer,renderer,controller,parent=None):
        QDialog.__init__(self,parent)
        self.setWindowTitle("Vector Field Renderer")

        self.stylev2=QgsStyleV2()
        self.layer=layer
        self.widget=VectorFieldRendererWidget(layer,self.stylev2,renderer,controller)
        self.widget.uCrashWarning.hide()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout=QVBoxLayout()
        layout.addWidget(self.widget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def accept( self ):
        self.widget.applyRenderer()
        QDialog.accept( self )



    
