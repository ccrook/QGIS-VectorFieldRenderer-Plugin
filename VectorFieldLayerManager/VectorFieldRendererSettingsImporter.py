#!/usr/bin/python3

import xml.etree.ElementTree as et
from .VectorFieldLayerManager import VectorFieldLayerManager
from .VectorFieldLayerSettings import VectorFieldLayerSettings


class VectorFieldRendererSettingsImporter:
    def __init__(self, controller, project):
        self._controller = controller
        self._project = project

    def readVectorFieldSettings(self, projectFile):
        prj = et.parse(projectFile)
        version = prj.find(".").attrib["version"]
        if not version.startswith("2."):
            return
        for layer in prj.findall("./projectlayers/maplayer/renderer-v2[@type='VectorFieldRenderer']/.."):
            id = layer.find("id").text
            vfrsettings = layer.find("renderer-v2").attrib
            yield id, vfrsettings

    @staticmethod
    def calcArrowHeadRelativeLength(vfrsettings):
        try:
            front, back, centre = vfrsettings["arrowHeadRelativeLength"]
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
        "arrowHeadWidth": "arrowHeadSize",
        "arrowMaxRelativeHeadSize": "arrowMaxHeadSize",
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
        return settings

    @staticmethod
    def importSettings(self):
        projectFile = self._project.absoluteFileName()
        for layerid, vfrsettings in self.readVectorFieldSettings(projectFile):
            vfmsettings = self.getVectorFieldManagerSettings(vfrsettings)
            layer = self._project.mapLayer(layerid)
            self._controller.renderLayerAsVectorField(layer, propogate=False, **vfmsettings)
