#!/usr/bin/python3

import os.path
import xml.etree.ElementTree as et
from .VectorFieldLayerSettings import VectorFieldLayerSettings
from qgis.gui import QgsMessageBar


class VectorFieldRendererSettingsImporter:
    def __init__(self, iface, controller, project):
        self._iface = iface
        self._controller = controller
        self._project = project

    def readVectorFieldSettings(self, projectFile):
        if not os.path.isfile(projectFile):
            return
        try:
            prj = et.parse(projectFile)
            version = prj.find(".").attrib["version"]
            if not version.startswith("2."):
                return
            for layer in prj.findall("./projectlayers/maplayer/renderer-v2[@type='VectorFieldRenderer']/.."):
                id = layer.find("id").text
                vfrsettings = layer.find("renderer-v2").attrib
                yield id, vfrsettings
            if prj.find("./projectlayers/maplayer[@type='plugin'][@name='vectorfieldrendererscalebox']"):
                yield None, "scalebox"
        except:
            pass

    @staticmethod
    def calcArrowHeadRelativeLength(vfrsettings):
        try:
            front, back, centre = [float(x) for x in vfrsettings["arrowHeadRelativeLength"].split()]
            return front - min(back, centre)
        except:
            return 2.0

    arrowMapping = {0: "xy", 1: "polar", 2: "height"}
    ellipseMapping = {2: "axes", 3: "circular", 4: "height"}

    mapping = {
        "arrowAngleDegrees": "degrees",
        "arrowAngleFromNorth": "angleFromNorth",
        "arrowBorderColor": "arrowColor",
        "arrowBorderWidth": "arrowHeadWidth",
        "arrowFillColor": "arrowHeadColor",
        "arrowHeadRelativeLength": lambda vfr: VectorFieldRendererSettingsImporter.calcArrowHeadRelativeLength(vfr),
        "arrowHeadWidth": "arrowMaxHeadSize",
        "arrowMaxRelativeHeadSize": "arrowHeadSize",
        "arrowMode": lambda vfr: VectorFieldRendererSettingsImporter.arrowMapping.get(int(vfr.get("mode")), "xy"),
        "arrowShaftWidth": "arrowWidth",
        "baseBorderColor": "baseBorderColor",
        "baseBorderWidth": "baseBorderWidth",
        "baseFillColor": "baseColor",
        "baseSize": "baseSize",
        "drawArrow": lambda vfr: int(vfr.get("mode")) in VectorFieldRendererSettingsImporter.arrowMapping,
        "drawEllipse": lambda vfr: int(vfr.get("ellipseMode")) in VectorFieldRendererSettingsImporter.ellipseMapping,
        "drawEllipseAxes": "drawEllipseAxes",
        "dxField": "xfieldname",
        "dyField": "yfieldname",
        "ellipseAngleFromNorth": "ellipseAngleFromNorth",
        "ellipseBorderColor": "ellipseBorderColor",
        "ellipseBorderWidth": "ellipseBorderWidth",
        "ellipseDegrees": "ellipseDegrees",
        "ellipseFillColor": "ellipseFillColor",
        "ellipseMode": lambda vfr: VectorFieldRendererSettingsImporter.ellipseMapping.get(int(vfr.get("ellipseMode")), "axes"),
        "ellipseScale": "ellipseScale",
        "ellipseTickSize": "ellipseTickSize",
        "emaxAzimuthField": "cyyfieldname",
        "emaxField": "cxxfieldname",
        "eminField": "cxyfieldname",
        "fillArrow": "arrowFillHead",
        "fillBase": "fillBase",
        "fillEllipse": "fillEllipse",
        "scale": "scale",
        "scaleGroup": "scalegroup",
        "scaleGroupFactor": "scalegroupfactor",
        "scaleIsMetres": "usemapunit",
        "symbolRenderUnit": "outputunit",
    }

    def getVectorFieldManagerSettings(self, vfrsettings):
        settings = {}
        warnings = []
        if str(settings.get("EllipseMode")) == "1":
            warnings.append("Covariance based error ellipses are not supported by vector field manager plugin")
        #!!! Check this shouldn't be false?
        if str(settings.get("vectoristruenorth")).lower() == "true":
            warnings.append("Aligning vectors with true north is not supported by the vector field manager plugin")
        for k, v in self.mapping.items():
            s = None
            if type(v) is str:
                s = vfrsettings.get(v)
            elif callable(v):
                print("Calling", k)
                try:
                    s = v(vfrsettings)
                except Exception as ex:
                    print(ex)
                    continue
            else:
                print("Cannot use", v)
            if s is not None:
                settings[k] = s
            else:
                print(k, s)
        return settings, warnings

    def importSettings(self):
        projectFile = self._project.absoluteFilePath()
        nlayers = 0
        warnings = []
        for layerid, vfrsettings in self.readVectorFieldSettings(projectFile):
            if layerid is None:
                warnings.append("Vector field scale box not supported by Vector Field Manager plugin")
                continue

            vfmsettings, lwarnings = self.getVectorFieldManagerSettings(vfrsettings)
            layer = self._project.mapLayer(layerid)
            nlayers += 1
            self._controller.renderLayerAsVectorField(layer, propogate=False, **vfmsettings)
            if len(warnings) > 0:
                message = "Layer {0}: {1}".format(layer.name(), ", ".join(lwarnings))
                warnings.append(message)

        if nlayers > 0:
            messagebar = self._iface.messageBar()
            title = "Vector field renderer plugin settings imported"
            message = "{0} vector field layers imported".format(nlayers)
            if len(warnings) > 0:
                message = message + ".\n  " + ".\n  ".join(warnings)
                messagebar.pushWarning(title, message)
            else:
                messagebar.pushInfo(title, message)
