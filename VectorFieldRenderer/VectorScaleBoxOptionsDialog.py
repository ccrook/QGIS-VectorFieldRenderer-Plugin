import sys
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qgis.core import *
from qgis.gui import *

from .Ui_VectorScaleBoxOptionsDialog import Ui_VectorScaleBoxOptionsDialog
from .VectorFieldRenderer import VectorFieldRenderer

# Color button class - connects up QgsColorButton with a color dialog

class ColorButton:
   def __init__(self,button):
      self._button = button
      button.clicked.connect(self.clicked)

   def color(self):
      return self._button.color()

   def setColor(self,color):
      if color.isValid():
         self._button.setColor(color)

   def clicked(self):
      self.setColor(QColorDialog.getColor(self.color()))

class FontButton:
   def __init__(self,button):
      self._button = button
      self._font = QFont("Arial",12)
      button.clicked.connect(self.clicked)

   def font(self):
      return self._font

   def setFont(self,font):
      self._font =  font

   def clicked(self):
      font,ok = QFontDialog.getFont(self.font())
      if ok:
         self.setFont(font)


# Vector field renderer widget

class VectorScaleBoxOptionsDialog(QDialog,Ui_VectorScaleBoxOptionsDialog):

    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.penColor = ColorButton(self.uPenColor)
        self.brushColor = ColorButton(self.uBrushColor)
        self.alignButtons = [self.uRadioTL, self.uRadioTR, self.uRadioBL, self.uRadioBR ]
        self.titleFont = FontButton(self.uTitleFont)
        self.scaleFont = FontButton(self.uScaleFont)
        self.uButtonBox.helpRequested.connect( self.showHelp )

    
    def loadOptions( self, sb ):
        self.alignButtons[sb.align()].setChecked(True)
        self.uOffsetX.setValue(sb.offsetX())
        self.uOffsetY.setValue(sb.offsetY())
        self.uArrowSizePercent.setValue(sb.arrowSizePercent())
        self.uShowBox.setChecked(sb.showBox())
        self.uFillBox.setChecked(sb.fillBox())
        self.penColor.setColor(sb.penColor())
        self.brushColor.setColor(sb.brushColor())
        self.uTitle.setText(sb.title())
        self.titleFont.setFont(sb.titleFont())
        self.scaleFont.setFont(sb.scaleFont())

    def saveOptions( self, sb ):
        for i in range(len(self.alignButtons)):
            if self.alignButtons[i].isChecked():
                sb.setAlign(i)
        sb.setOffsetX(self.uOffsetX.value())
        sb.setOffsetY(self.uOffsetY.value())
        sb.setArrowSizePercent(self.uArrowSizePercent.value())
        sb.setShowBox(self.uShowBox.isChecked())
        sb.setFillBox(self.uFillBox.isChecked())
        sb.setPenColor(self.penColor.color())
        sb.setBrushColor(self.brushColor.color())
        sb.setTitle(self.uTitle.text())
        sb.setTitleFont(self.titleFont.font())
        sb.setScaleFont(self.scaleFont.font())

    def showHelp(self):
        VectorFieldRenderer.showHelp()

    @staticmethod
    def getOptions(sb,parent=None):
        dialog = VectorScaleBoxOptionsDialog(parent)
        dialog.loadOptions(sb)
        result = dialog.exec_() == QDialog.Accepted
        if result:
           dialog.saveOptions(sb)
        return result
        

        
        
