import sys
import os.path
from PyQt5.QtGui import QColor

modpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, modpath)
print(modpath)

import fileunittest
from VectorFieldLayerManager.VectorFieldLayerSettings import VectorFieldLayerSettings


class VectorFieldLayerSettingsTestCase(fileunittest.TestCase):
    def test001_Params(self):
        """
        Test vector field layer settings
        """
        vs = VectorFieldLayerSettings()
        settings = vs.saveToString()
        self.check("001: Dump default settings", settings)
        self.checkRun("001: Reload settings", lambda: vs.readFromString(settings))

    def test002_Setters(self):
        """
        Test vector field layer settings
        """
        vs = VectorFieldLayerSettings()
        vs.setMode(2)
        vs.setAngleOrientation(1)
        vs.setAngleUnits(1)
        vs.setScale(0.2)
        vs.setDxField("de")
        vs.setDyField("dn")
        vs.setScaleIsMetres(True)
        vs.setScaleGroup("def")
        vs.setScaleGroupFactor(0.3)
        vs.setEllipseMode(4)
        vs.setEllipseAngleFromNorth(False)
        vs.setEllipseDegrees(False)
        vs.setEllipseScale(0.7)
        vs.setSymbolUnitType(1)
        vs.setArrowBorderColor(QColor("#ffbbffcc"))
        vs.setArrowHeadWidth(2.5)
        vs.setArrowHeadRelativeLength(2.3)
        vs.setArrowShaftWidth(0.5)
        vs.setArrowBorderWidth(0.15)
        vs.setArrowFillColor(QColor("#ffffbbcc"))
        vs.setFillArrow(False)
        vs.setArrowMaxRelativeHeadSize(0.2)
        vs.setBaseSize(0.27)
        vs.setFillBase(False)
        vs.setBaseFillColor(QColor("#aabbccdd"))
        vs.setBaseBorderWidth(0.07)
        vs.setBaseBorderColor(QColor("#ffccbbff"))
        vs.setEllipseBorderWidth(0.08)
        vs.setEmaxField("emaxf")
        vs.setEminField("eminf")
        vs.setEmaxAzimuthField("eazf")
        vs.setEllipseBorderColor(QColor("#ffffeedd"))
        vs.setEllipseFillColor(QColor("#ddeeff00"))
        vs.setFillEllipse(False)
        vs.setDrawEllipse(False)
        vs.setDrawEllipseAxes(True)
        vs.setEllipseTickSize(0.003)
        settings = vs.saveToString()
        self.check("002: Setter functions", settings)
        vs2 = VectorFieldLayerSettings()
        self.checkRun("002: Reload modified settings", lambda: vs2.readFromString(settings))
        settings2 = vs2.saveToString()
        self.check("002: Modified settings reloaded correctly", settings == settings2)


if __name__ == "__main__":
    fileunittest.main()
