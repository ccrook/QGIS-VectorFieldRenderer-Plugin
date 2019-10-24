from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QDialog, QMessageBox, QAction

from qgis.core import QgsApplication, QgsMapLayer, QgsProject
from qgis.gui import QgsMessageBar
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

        # self._helpWindow = None
        # self._scaleBoxLayer=None
        # self._pluginLayerType=VectorScaleBoxPluginLayer.Type()
        # QgsApplication.instance().pluginLayerRegistry().addPluginLayerType(self._pluginLayerType)
        # self._scaleBox = VectorScaleBox(iface)

        toolbar = iface.addToolBar(self.toolBarName)
        self._toolbar = toolbar

        actionAutosize = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/AutoscaleVectorFieldIcon.png"), "Autosize arrows", iface.mainWindow()
        )
        actionAutosize.setWhatsThis("Resize the arrows to a suggested scale for the current view")
        actionAutosize.setStatusTip("Resize the arrows to a suggested scale for the current view")
        actionAutosize.triggered.connect(self.autoRescale)

        actionEnlarge = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/MagnifyVectorFieldIcon.png"), "Enlarge arrows", iface.mainWindow()
        )
        actionEnlarge.setWhatsThis("Increase the arrow size")
        actionEnlarge.setStatusTip("Increase the arrow size")
        actionEnlarge.triggered.connect(self.enlarge)

        actionShrink = QAction(
            QIcon(":/plugins/VectorFieldLayerManager/ShrinkVectorFieldIcon.png"), "Shrink arrows", iface.mainWindow()
        )
        actionShrink.setWhatsThis("Decrease the arrow size")
        actionShrink.setStatusTip("Decrease the arrow size")
        actionShrink.triggered.connect(self.shrink)

        # action4 = QAction(QIcon(":/plugins/VectorFieldLayerManager/VectorScaleBoxOptionsIcon.png"),
        #           "Display the vector scale box", iface.mainWindow())
        # action4.setWhatsThis("Display the vector scale box")
        # action4.setStatusTip("Display the vector scale box")
        # action4.triggered.connect(self.setScaleBoxOptions)

        actionEdit = QAction(
            QIcon(":plugins/VectorFieldLayerManager/VectorFieldLayerManagerIcon.png"),
            "Edit vector field settings for current layer",
            iface.mainWindow(),
        )
        actionEdit.setWhatsThis("Edit vector field settings for current layer")
        actionEdit.setStatusTip("Edit vector field settings for current layer")
        actionEdit.triggered.connect(self.showLayerDialog)

        actionCopy = QAction(
            QIcon(":plugins/VectorFieldLayerManager/CopyVectorSettingsIcon.png"),
            "Copy current layer vector settings to clipboard",
            iface.mainWindow(),
        )
        actionCopy.setWhatsThis("Copy current layer vector settings to clipboard")
        actionCopy.setStatusTip("Copy current layer vector settings to clipboard")
        actionCopy.triggered.connect(self.copySettings)

        actionPaste = QAction(
            QIcon(":plugins/VectorFieldLayerManager/PasteVectorSettingsIcon.png"),
            "Paste vector settings from clipboard to selected layer(s)",
            iface.mainWindow(),
        )
        actionPaste.setWhatsThis("Paste vector settings from clipboard to selected layer(s)")
        actionPaste.setStatusTip("Paste vector settings from clipboard to selected layer(s)")
        actionPaste.triggered.connect(self.pasteSettings)

        actionHelp = QAction(
            QIcon(":plugins/VectorFieldLayerManager/VectorFieldLayerManagerHelpIcon.png"),
            "Vector field settings help",
            iface.mainWindow(),
        )
        actionHelp.setWhatsThis("Show vector field settings help")
        actionHelp.setStatusTip("Show vector field settings help")
        actionHelp.triggered.connect(self.showHelp)

        toolbar.addAction(actionAutosize)
        toolbar.addAction(actionEnlarge)
        toolbar.addAction(actionShrink)
        # toolbar.addAction(action4)
        toolbar.addAction(actionEdit)
        toolbar.addAction(actionCopy)
        toolbar.addAction(actionPaste)
        toolbar.addAction(actionHelp)

        self._rescaleAction = actionAutosize
        self._enlargeAction = actionEnlarge
        self._shrinkAction = actionShrink
        # self._scaleOptionsAction = action4
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
        # iface.mainWindow().projectRead.connect(self.loadProject)
        # iface.mapCanvas().renderComplete[QPainter].connect(self.renderComplete)
        # iface.mapCanvas().renderStarting.connect(self.renderStarting)

    def unload(self):
        self._iface.currentLayerChanged[QgsMapLayer].disconnect(self.currentLayerChanged)
        # self._iface.mainWindow().projectRead.disconnect(self.loadProject)
        # self._iface.mapCanvas().renderComplete[QPainter].disconnect(self.renderComplete)
        # self._iface.mapCanvas().renderStarting.disconnect(self.renderStarting)
        self._iface.mainWindow().removeToolBar(self._toolbar)
        # QgsApplication.instance().pluginLayerRegistry().removePluginLayerType(VectorScaleBoxPluginLayer.LayerType)

    # def canBeUninstalled(self):
    #     vrlayers = []
    #     vrlayerids = []
    #     for l, r in self.vectorSettingsLayers():
    #         vrlayers.append(str(l.name()))
    #         vrlayerids.append(l.getLayerID())

    #     if len(vrlayers) > 0:
    #         message = ("The following layers are using the vector field settings plugin\n    "+
    #                 "\n    ".join(vrlayers)+"\n" +
    #                 "If it is uninstalled these will be removed from the project\n\n" +
    #                 "Do you want to remove the plugin?")
    #         result = QMessageBox.question(self._iface.mainWindow(),"Remove plugin?",message,QMessageBox.Ok,QMessageBox.Cancel)
    #         if result != QMessageBox.Ok:
    #             return False

    #         for lid in vrlayerids:
    #             QgsProject.instance().removeMapLayer(lid)

    #     return True

    # def loadProject(self):
    #     self._scaleBox.reset()

    # def resetEnabled(self):
    #     self.enableActions(bool(self.findSettings()[1]))

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

    # def renderComplete( self, painter ):
    #     # window=painter.window()
    #     # extents=QgsRectangle(window.left(),window.bottom(),window.right(),window.top())
    #     # self._scaleBox.render( painter, extents )
    #     self.resetEnabled()
    #     # self.setupScaleBox()

    def currentLayer(self):
        return self._iface.activeLayer()

    # def findSettings(self):
    #     layer = self.currentLayer()
    #     return layer,VectorFieldLayerSettings.layerSettings(layer)

    # def vectorSettingsLayers( self ):
    #     for l in self._iface.mapCanvas().layers():
    #         s = VectorFieldLayerSettings.layerSettings(layer)
    #         if s:
    #             yield l,s

    # def vectorScaleBoxLayers( self ):
    #     for l in list(QgsProject.instance().mapLayers().values()):
    #         if l.type() == QgsMapLayer.PluginLayer:
    #             if type(l) == VectorScaleBoxPluginLayer:
    #                 yield l

    # def setupScaleBox( self ):
    #     haveVectors = False
    #     for l,r in self.vectorSettingsLayers():
    #         haveVectors = True
    #         break

    #     haveScaleBox = False
    #     for l in self.vectorScaleBoxLayers():
    #         haveScaleBox = True
    #         break

    #     if haveVectors and not haveScaleBox:
    #         l = VectorScaleBoxPluginLayer()
    #         l.setScaleBox( self._scaleBox )
    #         self._scaleBoxLayer=l
    #         QgsProject.instance().addMapLayer(l)

    # def renderStarting( self ):
    #     for l,r in self.vectorSettingsLayers():
    #         if r.getGroupScale():
    #             l.triggerRepaint()

    #     for l in self.vectorScaleBoxLayers():
    #         l.setScaleBox( self._scaleBox )

    # def repaintScaleBox( self ):
    #     for l in self.vectorScaleBoxLayers():
    #         l.repaintScaleBox()

    # def refreshLayer(self,layer):
    #     layer.triggerRepaint()
    #     self.repaintScaleBox()

    def autoRescale(self):
        layer = self.currentLayer()
        scale = self._controller.estimateOptimalScale(layer)
        if scale is not None:
            self._controller.setVectorFieldLayerScale(layer, scale)

    def enlarge(self):
        layer = self.currentLayer()
        self._controller.rescaleVectorFieldLayer(layer, self._factor)

    def shrink(self):
        layer = self.currentLayer()
        self._controller.rescaleVectorFieldLayer(layer, 1.0 / self._factor)

    def resetLayerScale(self, layer):
        self._dialog.resetLayerScale(self, layer)

    # def setScaleBoxOptions(self):
    #     if VectorScaleBoxOptionsDialog.getOptions(self._scaleBox,self._iface.mainWindow()):
    #         self.setupScaleBox()
    #         self.repaintScaleBox()

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
