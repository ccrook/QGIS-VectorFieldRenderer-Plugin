from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QDialog, QMessageBox, QAction

from qgis.core import QgsApplication, QgsMapLayer, QgsProject
from qgis import utils

from .VectorFieldLayerDialog import VectorFieldLayerDialog
from .VectorFieldLayerManager import VectorFieldLayerManager
from .VectorFieldLayerSettings import VectorFieldLayerSettings
from . import VectorFieldManagerResources


class VectorFieldLayerToolbar:

    toolBarName = "Vector field manager"

    def __init__(self, iface):
        self._iface = iface
        self._controller = VectorFieldLayerManager(iface)
        self._dialog = VectorFieldLayerDialog(self._controller, self.currentLayer(), iface.mainWindow())
        self._factor = 2.0

        toolbar = iface.addToolBar(self.toolBarName)
        self._toolbar = toolbar

        actionEdit = QAction(
            QIcon(":plugins/VectorFieldLayerManager/icon/VectorFieldLayerManagerIcon.png"),
            "Edit vector field settings for current layer",
            iface.mainWindow(),
        )
        actionEdit.setWhatsThis("Edit vector field settings for current layer")
        actionEdit.setStatusTip("Edit vector field settings for current layer")
        actionEdit.triggered.connect(self.showLayerDialog)

        actionAutosize = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/icon/AutoscaleVectorFieldIcon.png"), "Autosize arrows", iface.mainWindow()
        )
        actionAutosize.setWhatsThis("Resize the arrows to a suggested scale for the current view")
        actionAutosize.setStatusTip("Resize the arrows to a suggested scale for the current view")
        actionAutosize.triggered.connect(self.autoRescale)

        actionEnlarge = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/icon/MagnifyVectorFieldIcon.png"), "Enlarge arrows", iface.mainWindow()
        )
        actionEnlarge.setWhatsThis("Increase the arrow size")
        actionEnlarge.setStatusTip("Increase the arrow size")
        actionEnlarge.triggered.connect(self.enlarge)

        actionShrink = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/icon/ShrinkVectorFieldIcon.png"), "Shrink arrows", iface.mainWindow()
        )
        actionShrink.setWhatsThis("Decrease the arrow size")
        actionShrink.setStatusTip("Decrease the arrow size")
        actionShrink.triggered.connect(self.shrink)

        actionCopy = QAction(
            QIcon(":plugins/VectorFieldLayerManager/icon/CopyVectorSettingsIcon.png"),
            "Copy current layer vector settings to clipboard",
            iface.mainWindow(),
        )
        actionCopy.setWhatsThis("Copy current layer vector settings to clipboard")
        actionCopy.setStatusTip("Copy current layer vector settings to clipboard")
        actionCopy.triggered.connect(self.copySettings)

        actionPaste = QAction(
            QIcon(":plugins/VectorFieldLayerManager/icon/PasteVectorSettingsIcon.png"),
            "Paste vector settings from clipboard to selected layer(s)",
            iface.mainWindow(),
        )
        actionPaste.setWhatsThis("Paste vector settings from clipboard to selected layer(s)")
        actionPaste.setStatusTip("Paste vector settings from clipboard to selected layer(s)")
        actionPaste.triggered.connect(self.pasteSettings)

        actionHelp = QAction(
            QIcon(":plugins/VectorFieldLayerManager/icon/VectorFieldLayerManagerHelpIcon.png"),
            "Vector field settings help",
            iface.mainWindow(),
        )
        actionHelp.setWhatsThis("Show vector field settings help")
        actionHelp.setStatusTip("Show vector field settings help")
        actionHelp.triggered.connect(self.showHelp)

        toolbar.addAction(actionEdit)
        toolbar.addAction(actionAutosize)
        toolbar.addAction(actionEnlarge)
        toolbar.addAction(actionShrink)
        toolbar.addAction(actionCopy)
        toolbar.addAction(actionPaste)
        toolbar.addAction(actionHelp)

        self._rescaleAction = actionAutosize
        self._enlargeAction = actionEnlarge
        self._shrinkAction = actionShrink
        self._copyAction = actionCopy
        self._pasteAction = actionPaste
        self._editAction = actionEdit
        self._helpAction = actionHelp

        # Only enable when active layer has a Vector Field settings, also
        # disable and check whenever the canvas has redrawn (eg after
        # changing symobology), or the active layer has changed

        self.enableActions()
        iface.currentLayerChanged[QgsMapLayer].connect(self.currentLayerChanged)
        QgsProject.instance().layerRemoved.connect(self.layerRemoved)

    def unload(self):
        self._controller.unload()
        self._iface.currentLayerChanged[QgsMapLayer].disconnect(self.currentLayerChanged)
        self._iface.mainWindow().removeToolBar(self._toolbar)

    def enableActions(self):
        layer = self.currentLayer()
        isvectorlayer = self._controller.isVectorFieldLayer(layer)
        isvalidlayer = self._controller.isValidLayerType(layer)
        self._rescaleAction.setEnabled(isvectorlayer)
        self._enlargeAction.setEnabled(isvectorlayer)
        self._shrinkAction.setEnabled(isvectorlayer)
        self._editAction.setEnabled(isvalidlayer)
        self._copyAction.setEnabled(isvectorlayer)
        self._pasteAction.setEnabled(isvalidlayer)

    def currentLayerChanged(self, layer):
        self._dialog.setLayer(layer)
        self.enableActions()

    def layerRemoved(self, layerid):
        self._dialog.layerRemoved(layerid)

    def currentLayer(self):
        return self._iface.activeLayer()

    def autoRescale(self):
        layer = self.currentLayer()
        scale = self._controller.autoscaleVectorLayer(layer)

    def enlarge(self):
        layer = self.currentLayer()
        self._controller.rescaleVectorFieldLayer(layer, self._factor)

    def shrink(self):
        layer = self.currentLayer()
        self._controller.rescaleVectorFieldLayer(layer, 1.0 / self._factor)

    def resetLayerScale(self, layer):
        self._dialog.resetLayerScale(self, layer)

    def showLayerDialog(self):
        self._dialog.show()
        self._dialog.raise_()

    def copySettings(self):
        layer = self.currentLayer()
        settings = self._controller.readSettingsFromLayer(layer)
        if settings is not None:
            QgsApplication.clipboard().setText(settings.toString())
            self._iface.messageBar().pushInfo(
                "Vector settings copied", "The current layer vector settings have been copied to the clipboard."
            )
        else:
            self._iface.messageBar().pushWarning(
                "Vector settings copy error", "The current layer does not have vector settings - not copied."
            )

    def pasteSettings(self):
        clipboard = QgsApplication.clipboard()
        text = clipboard.text()
        settings = VectorFieldLayerSettings()
        try:
            nbad = 0
            if settings.readFromString(text, ignore_errors=False):
                for layer in self._iface.layerTreeView().selectedLayers():
                    if self._controller.applySettingsToLayer(layer, settings):
                        self._dialog.layerUpdated(layer)
                    else:
                        nbad += 1
            if nbad > 0:
                self._iface.messageBar().pushWarning(
                    "Vector settings paste error", "Could not apply vector field settings to {0} layers".format(nbad)
                )
        except:
            self._iface.messageBar().pushWarning(
                "Vector settings paste error", "Could not read vector field settings from the clipboard"
            )

    def showHelp(self):
        utils.showPluginHelp()
