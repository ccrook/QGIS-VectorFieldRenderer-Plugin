from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from .VectorFieldLayerWidget import VectorFieldLayerWidget

# Vector field renderer layer dialog - for use when the python bindings layer properties
# fail to load the renderer interface

class VectorFieldLayerDialog(QDialog):

    def __init__(self,controller,layer,parent=None):
        QDialog.__init__(self,parent)
        self.setWindowTitle("Vector Field Layer")

        self.layer=layer
        self.widget=VectorFieldLayerWidget(controller,layer)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply )
        layout=QVBoxLayout()
        layout.addWidget(self.widget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        applyButton=buttonBox.button(QDialogButtonBox.Apply)
        applyButton.clicked.connect(self.apply)

    def accept( self ):
        self.widget.applyToLayer()
        QDialog.accept( self )

    def apply( self ):
        self.widget.applyToLayer()



    
