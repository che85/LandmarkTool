from slicer.ScriptedLoadableModule import *
from SlicerDevelopmentToolboxUtils.mixins import *
from SlicerDevelopmentToolboxUtils.widgets import TargetCreationWidget


class LandmarkTool(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "LandmarkTool"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = ["SlicerDevelopmentToolbox"]
    self.parent.contributors = ["Christian Herz (SPL)"]
    self.parent.helpText = """
    This extensions provides functionality for setting landmarks.
    """
    self.parent.acknowledgementText = """
    This work was supported in part by the National Cancer Institute funding to the
    Quantitative Image Informatics for Cancer Research (QIICR) (U24 CA180918).
    """ # replace with organization, grant and thanks.


class LandmarkToolWidget(ModuleWidgetMixin, ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    # self.setup()

  def cleanup(self):
    pass

  def enter(self):
    pass

  def exit(self):
    self.cleanup()

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.preopTargetTable = TargetCreationWidget()
    self.preopTargetTable.targetListSelectorVisible = True

    self.intraopTargetTable = TargetCreationWidget()
    self.intraopTargetTable.targetListSelectorVisible = True

    self.layout.addWidget(self.preopTargetTable)
    self.layout.addWidget(self.intraopTargetTable)

    self.layout.addStretch(1)
    self.setupConnections()

  def setupConnections(self):
    # self.preopTargetTable.addEventObserver(t.TargetSelectedEvent, onTargetSelected)
    pass