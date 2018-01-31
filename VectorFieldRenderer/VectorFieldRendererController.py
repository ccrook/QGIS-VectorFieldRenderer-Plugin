
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from qgis.core import *
from qgis.gui import *

from .VectorFieldRenderer import VectorFieldRenderer
from .VectorScaleBox import VectorScaleBox
from .VectorScaleBoxPluginLayer import VectorScaleBoxPluginLayer
from .VectorScaleBoxOptionsDialog import VectorScaleBoxOptionsDialog
from .VectorFieldRendererLayerDialog import VectorFieldRendererLayerDialog

class VectorFieldRendererController:

    toolBarName = "Vector field controller"

    def __init__( self, iface ):
        self._iface = iface
        # jferencik workaround for 'QgsFeatureRenderer' object has no attribute error
        # _vlayers...
        self._vlayers={}
        VectorFieldRenderer.controller=self
        VectorScaleBox.controller=self
        self._factor = 2.0
        self._helpWindow = None
        self._scaleBoxLayer=None
        self._pluginLayerType=VectorScaleBoxPluginLayer.Type()

        QgsApplication.instance().pluginLayerRegistry().addPluginLayerType(self._pluginLayerType)
        self._scaleBox = VectorScaleBox(iface)

        toolbar = iface.addToolBar(self.toolBarName)
        self._toolbar = toolbar

        action1 = QAction(QIcon(":/plugins/VectorFieldRenderer/RescaleRendererIcon.png"),
                  "Autosize arrows", iface.mainWindow())
        action1.setWhatsThis("Resize the arrows to a suggested scale for the current view")
        action1.setStatusTip("Resize the arrows to a suggested scale for the current view")
        action1.triggered.connect(self.autoRescale)

        action2 = QAction(QIcon(":/plugins/VectorFieldRenderer/EnlargeRendererIcon.png"),
                  "Enlarge arrows", iface.mainWindow())
        action2.setWhatsThis("Increase the arrow size")
        action2.setStatusTip("Increase the arrow size")
        action2.triggered.connect(self.enlarge)

        action3 = QAction(QIcon(":/plugins/VectorFieldRenderer/ShrinkRendererIcon.png"),
                  "Shrink arrows", iface.mainWindow())
        action3.setWhatsThis("Decrease the arrow size")
        action3.setStatusTip("Decrease the arrow size")
        action3.triggered.connect(self.shrink)

        action4 = QAction(QIcon(":/plugins/VectorFieldRenderer/VectorScaleBoxOptionsIcon.png"),
                  "Display the vector scale box", iface.mainWindow())
        action4.setWhatsThis("Display the vector scale box")
        action4.setStatusTip("Display the vector scale box")
        action4.triggered.connect(self.setScaleBoxOptions)

        action5 = QAction(QIcon(":plugins/VectorFieldRenderer/VectorFieldRendererIcon.png"),
                  "Apply vector renderer to current layer", iface.mainWindow())
        action5.setWhatsThis("Apply vector renderer to current layer")
        action5.setStatusTip("Apply vector renderer to current layer")
        action5.triggered.connect(self.showLayerDialog)

        action6 = QAction(QIcon(":plugins/VectorFieldRenderer/RendererHelpIcon.png"),
                  "Vector field renderer help", iface.mainWindow())
        action6.setWhatsThis("Show vector field renderer help")
        action6.setStatusTip("Show vector field renderer help")
        action6.triggered.connect(self.showHelp)

        toolbar.addAction(action1)
        toolbar.addAction(action2)
        toolbar.addAction(action3)
        toolbar.addAction(action4)
        toolbar.addAction(action5)
        toolbar.addAction(action6)

        self._rescaleAction = action1
        self._enlargeAction = action2
        self._shrinkAction = action3
        self._scaleOptionsAction = action4
        self._layerDialog=action5
        self._helpAction = action6

        # Only enable when active layer has a Vector Field renderer, so
        # disable and check whenever the canvas has redrawn (eg after
        # changing symobology), or the active layer has changed

        self.enableActions(False)
        iface.currentLayerChanged[QgsMapLayer].connect(self.activeLayerChanged)
        iface.mainWindow().projectRead.connect(self.loadProject)
        iface.mapCanvas().renderComplete[QPainter].connect(self.renderComplete)
        iface.mapCanvas().renderStarting.connect(self.renderStarting)

    def unload( self ):
        self._iface.currentLayerChanged[QgsMapLayer].disconnect(self.activeLayerChanged)
        self._iface.mainWindow().projectRead.disconnect(self.loadProject)
        self._iface.mapCanvas().renderComplete[QPainter].disconnect(self.renderComplete)
        self._iface.mapCanvas().renderStarting.disconnect(self.renderStarting)
        self._iface.mainWindow().removeToolBar(self._toolbar)
        QgsApplication.instance().pluginLayerRegistry().removePluginLayerType(VectorScaleBoxPluginLayer.LayerType)

    def canBeUninstalled(self):
        vrlayers = []
        vrlayerids = []
        for l, r in self.vectorRendererLayers():
            vrlayers.append(str(l.name()))
            vrlayerids.append(l.getLayerID())
                

        if len(vrlayers) > 0:
            message = ("The following layers are using the vector field renderer plugin\n    "+
                    "\n    ".join(vrlayers)+"\n" +
                    "If it is uninstalled these will be removed from the project\n\n" +
                    "Do you want to remove the plugin?")
            result = QMessageBox.question(self._iface.mainWindow(),"Remove plugin?",message,QMessageBox.Ok,QMessageBox.Cancel)
            if result != QMessageBox.Ok:
                return False

            for lid in vrlayerids:
                QgsProject.instance().removeMapLayer(lid)

        return True

    def loadProject(self):
        self._scaleBox.reset()

    def resetEnabled(self):
        self.enableActions(bool(self.findRenderer()[1]))

    def enableActions(self,enabled):
        self._rescaleAction.setEnabled(enabled)
        self._enlargeAction.setEnabled(enabled)
        self._shrinkAction.setEnabled(enabled)

    def activeLayerChanged( self, layer ):
        self.resetEnabled()

    def renderComplete( self, painter ):
        # window=painter.window()
        # extents=QgsRectangle(window.left(),window.bottom(),window.right(),window.top())
        # self._scaleBox.render( painter, extents )
        self.resetEnabled()
        # self.setupScaleBox()

    def findRenderer(self):
        layer = self._iface.activeLayer()
        return layer,self.findLayerRenderer(layer)

    def findLayerRenderer(self,layer):
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            return None
        renderer = layer.renderer()
        if not renderer or renderer.type() != VectorFieldRenderer.rendererName:
            return None
        if not isinstance(renderer,VectorFieldRenderer):
            renderer=self._vlayers.get(layer.id())
            # Is it worth resetting the layer renderer here?
        return renderer

    # saveLayerRenderer is a workaround for the bug/issue that the passing a renderer
    # through C++ pointers and SIP sometimes seems to lose its python instance
    #
    # This may not be sufficient as when renderer is cloned the cloned python object 
    # is not saved.  A WIP resolution

    def saveLayerRenderer(self,layer,renderer):
        layerrenderer=layer.renderer()
        if isinstance(layerrenderer,VectorFieldRenderer):
            renderer=layerrenderer
        self._vlayers[layer.id()]=renderer

    def vectorRendererLayers( self ):
        for l in self._iface.mapCanvas().layers():
            r = self.findLayerRenderer(l)
            if r:
                yield l,r

    def vectorScaleBoxLayers( self ):
        for l in list(QgsProject.instance().mapLayers().values()):
            if l.type() == QgsMapLayer.PluginLayer:
                if type(l) == VectorScaleBoxPluginLayer:
                    yield l

    def setupScaleBox( self ):
        haveVectors = False
        for l,r in self.vectorRendererLayers():
            haveVectors = True
            break
        
        haveScaleBox = False
        for l in self.vectorScaleBoxLayers():
            haveScaleBox = True
            break

        if haveVectors and not haveScaleBox:
            l = VectorScaleBoxPluginLayer()
            l.setScaleBox( self._scaleBox )
            self._scaleBoxLayer=l
            QgsProject.instance().addMapLayer(l)

    def renderStarting( self ):
        for l,r in self.vectorRendererLayers():
            if r.getGroupScale():
                l.triggerRepaint()
        
        for l in self.vectorScaleBoxLayers():
            l.setScaleBox( self._scaleBox )

    def repaintScaleBox( self ):
        for l in self.vectorScaleBoxLayers():
            l.repaintScaleBox()

    def refreshLayer(self,layer):
        layer.repaintRequested.emit()
        self.repaintScaleBox()

    def autoRescale(self):
        layer, renderer = self.findRenderer()
        if renderer and renderer.autoRescale(layer,self._iface.mapCanvas()):
            self.refreshLayer(layer)
   
    def enlarge(self):
        layer,renderer = self.findRenderer()
        if renderer:
            renderer.setScale(renderer.scale()*self._factor)
            self.refreshLayer(layer)
   
    def shrink(self):
        layer,renderer = self.findRenderer()
        if renderer:
            renderer.setScale(renderer.scale()/self._factor)
            self.refreshLayer(layer)
        
    def setScaleBoxOptions(self):
        if VectorScaleBoxOptionsDialog.getOptions(self._scaleBox,self._iface.mainWindow()):
            self.setupScaleBox()
            self.repaintScaleBox()

    def showLayerDialog( self ):
        layer, renderer = self.findRenderer()
        if layer is None or layer.type() != QgsMapLayer.VectorLayer or layer.geometryType() != QgsWkbTypes.PointGeometry:
            self._iface.messageBar().pushMessage("Invalid layer",
                "The vector field renderer only renders point layers",
                level=QgsMessageBar.WARNING, duration=5)
            return
        dialog=VectorFieldRendererLayerDialog( layer, renderer, self )
        if dialog.exec_() == QDialog.Accepted:
            self.refreshLayer(layer)
           
    def showHelp(self):
        VectorFieldRenderer.showHelp()
