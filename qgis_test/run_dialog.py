import sys
import os.path
import importlib
modpath='/home/ccrook/projects/qgis/plugins/qgis3/VectorFieldRenderer'
if sys.path[0] != modpath:
    sys.path.insert(0,modpath)

import VectorFieldLayerManager.VectorFieldLayerSettings
import VectorFieldLayerManager.Ui_VectorFieldLayerWidget
import VectorFieldLayerManager.VectorFieldLayerWidget
import VectorFieldLayerManager.VectorFieldLayerDialog
import VectorFieldLayerManager.VectorFieldLayerManager
import VectorFieldLayerManager.VectorFieldLayerToolbar
importlib.reload(VectorFieldLayerManager.VectorFieldLayerSettings)
importlib.reload(VectorFieldLayerManager.Ui_VectorFieldLayerWidget)
importlib.reload(VectorFieldLayerManager.VectorFieldLayerWidget)
importlib.reload(VectorFieldLayerManager.VectorFieldLayerDialog)
importlib.reload(VectorFieldLayerManager.VectorFieldLayerManager)
importlib.reload(VectorFieldLayerManager.VectorFieldLayerToolbar)

def runDialog():
    def run():
       global testdialog
       controller=VectorFieldLayerManager.VectorFieldLayerManager.VectorFieldLayerManager(iface)
       testdialog=VectorFieldLayerManager.VectorFieldLayerDialog.VectorFieldLayerDialog( controller, iface.mapCanvas().currentLayer() )
       testdialog.show()
    return run


def toolbar():
    return VectorFieldLayerManager.VectorFieldLayerToolbar.VectorFieldLayerToolbar(iface)

showdialog=runDialog()
showdialog()