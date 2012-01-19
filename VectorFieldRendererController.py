

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from VectorFieldRenderer import VectorFieldRenderer
from VectorFieldRendererScaleBox import VectorFieldRendererScaleBox
from VectorScaleBoxOptionsDialog import VectorScaleBoxOptionsDialog

class VectorFieldRendererController:

    toolBarName = "Vector field controller"

    def __init__( self, iface ):
        self._iface = iface
        self._factor = 2.0
        self._helpWindow = None
        self._scaleBox = VectorFieldRendererScaleBox(iface)

        toolbar = iface.addToolBar(self.toolBarName)
        self._toolbar = toolbar

        action1 = QAction(QIcon(":/plugins/VectorFieldRenderer/RescaleRendererIcon.png"),
                  "Autosize arrows", iface.mainWindow())
        action1.setWhatsThis("Resize the arrows to a suggested scale for the current view")
        action1.setStatusTip("Resize the arrows to a suggested scale for the current view")
        QObject.connect(action1,SIGNAL("triggered()"), self.autoRescale )

        action2 = QAction(QIcon(":/plugins/VectorFieldRenderer/EnlargeRendererIcon.png"),
                  "Enlarge arrows", iface.mainWindow())
        action2.setWhatsThis("Increase the arrow size")
        action2.setStatusTip("Increase the arrow size")
        QObject.connect(action2,SIGNAL("triggered()"), self.enlarge )

        action3 = QAction(QIcon(":/plugins/VectorFieldRenderer/ShrinkRendererIcon.png"),
                  "Shrink arrows", iface.mainWindow())
        action3.setWhatsThis("Decrease the arrow size")
        action3.setStatusTip("Decrease the arrow size")
        QObject.connect(action3,SIGNAL("triggered()"), self.shrink )

        action4 = QAction(QIcon(":/plugins/VectorFieldRenderer/VectorScaleBoxOptionsIcon.png"),
                  "Configure arrow scale box", iface.mainWindow())
        action4.setWhatsThis("Configure the arrow scale box")
        action4.setStatusTip("Configure the arrow scale box")
        QObject.connect(action4,SIGNAL("triggered()"), self.setScaleBoxOptions )

        action5 = QAction(QIcon(":plugins/VectorFieldRenderer/RendererHelpIcon.png"),
                  "Vector field renderer help", iface.mainWindow())
        action5.setWhatsThis("Show vector field renderer help")
        action5.setStatusTip("Show vector field renderer help")
        QObject.connect(action5,SIGNAL("triggered()"), self.showHelp )

        toolbar.addAction(action1)
        toolbar.addAction(action2)
        toolbar.addAction(action3)
        toolbar.addAction(action4)
        toolbar.addAction(action5)

        self._rescaleAction = action1
        self._enlargeAction = action2
        self._shrinkAction = action3
        self._scaleOptionsAction = action4
        self._helpAction = action5

        # Only enable when active layer has a Vector Field renderer, so
        # disable and check whenever the canvas has redrawn (eg after
        # changing symobology), or the active layer has changed

        self.enableActions(False)
        QObject.connect(iface,SIGNAL("currentLayerChanged(QgsMapLayer*)"),
            self.activeLayerChanged)
        QObject.connect( iface.mainWindow(), SIGNAL( "projectRead()" ), self.loadProject)
        QObject.connect(iface.mapCanvas(),SIGNAL("renderComplete(QPainter*)"),
            self.renderComplete)
        QObject.connect( iface.mapCanvas(),SIGNAL("renderStarting()"),self.renderStarting )

    def unload( self ):
        QObject.disconnect(self._iface,SIGNAL("currentLayerChanged(QgsMapLayer*)"),
            self.activeLayerChanged)
        QObject.disconnect( self._iface.mainWindow(), SIGNAL( "projectRead()" ), self.loadProject)
        QObject.disconnect(self._iface.mapCanvas(),SIGNAL("renderComplete(QPainter*)"),
            self.renderComplete)
        QObject.disconnect( self._iface.mapCanvas(),SIGNAL("renderStarting()"),self.renderStarting )
        self._iface.mainWindow().removeToolBar(self._toolbar)

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
                QgsMapLayerRegistry.instance().removeMapLayer(lid)

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
        for l,r in self.vectorRendererLayers():
            r.setMapRenderingFinished()
        self._scaleBox.render( painter )
        self.resetEnabled()

    def findRenderer(self):
        layer = self._iface.activeLayer()
        return layer,self.findLayerRenderer(layer)

    def findLayerRenderer(self,layer):
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            return None
        renderer = layer.rendererV2()
        if not renderer or renderer.type() != VectorFieldRenderer.rendererName:
            return None
        return renderer

    def vectorRendererLayers( self ):
        for l in self._iface.mapCanvas().layers():
            r = self.findLayerRenderer(l)
            if r:
                yield l,r

    def renderStarting( self ):
        for l,r in self.vectorRendererLayers():
            r.setMapRenderingStarting()
            if r.getGroupScale():
                l.setCacheImage(None)


    def refreshLayer(self,layer):
        layer.setCacheImage(None)
        self._iface.mapCanvas().refresh()

    def autoRescale(self):
        layer, renderer = self.findRenderer()
        mapsize = self._iface.mapCanvas().extent();
        if renderer and renderer.autoRescale(mapsize):
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
           self._iface.mapCanvas().refresh()
           
    def showHelp(self):
        VectorFieldRenderer.showHelp()
