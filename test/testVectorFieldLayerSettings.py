import sys
import os.path
modpath=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
sys.path.insert(0, modpath)
print(modpath)

import fileunittest
from VectorFieldLayerSettings import VectorFieldLayerSettings


class VectorFieldLayerSettingsTestCase(fileunittest.TestCase):
    def test001_Params(self):
        """
        Test vector field layer settings
        """
        vs = VectorFieldLayerSettings()
        settings=vs.saveToString()
        self.check("001: Dump default settings", settings)
        self.checkRun("001: Reload settings", lambda : vs.readFromString(settings))


if __name__ == "__main__":
    fileunittest.main()

