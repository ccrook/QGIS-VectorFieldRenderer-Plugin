from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox

from .VectorFieldLayerWidget import VectorFieldLayerWidget

# Vector field renderer layer dialog - for use when the python bindings layer properties
# fail to load the renderer interface


class VectorFieldLayerDialog(QDialog):
    def __init__(self, controller, layer, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Vector Field Layer Settings")

        self.layer = layer
        self._widget = VectorFieldLayerWidget(controller, layer)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        layout = QVBoxLayout()
        layout.addWidget(self._widget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        applyButton = buttonBox.button(QDialogButtonBox.Apply)
        applyButton.clicked.connect(self.apply)

    def accept(self):
        self._widget.applyToLayer()
        QDialog.accept(self)

    def apply(self):
        self._widget.applyToLayer()

    def layerRemoved(self, layerid):
        self._widget.layerRemoved(layerid)

    def layerUpdated(self, layer):
        self._widget.layerUpdated(layer.id())

    def setLayer(self, layer, force=False):
        if self._widget.isModified() and not force:
            message = (
                "The vector field settings for layer {0} have been modified.\n"
                + "Do you want to apply these changes before changing the layer?"
            ).format(self._widget.layer().name())

            result = QMessageBox.question(
                self, "Save changes?", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if result == QMessageBox.Cancel:
                return False
            if result == QMessageBox.Yes:
                self._widget.applyToLayer()
        self._widget.setLayer(layer)
