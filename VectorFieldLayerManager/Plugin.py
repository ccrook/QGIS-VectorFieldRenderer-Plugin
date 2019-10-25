from .VectorFieldLayerToolbar import VectorFieldLayerToolbar


class Plugin:

    Name = "VectorFieldLayerManager"
    Version = "1.0.1"

    def __init__(self, iface):
        self._iface = iface
        self._toolbar = None

    def initGui(self):
        if self._toolbar is None:
            self._toolbar = VectorFieldLayerToolbar(self._iface)

    def unload(self):
        if self._toolbar is not None:
            self._toolbar.unload()
            self._toolbar = None
