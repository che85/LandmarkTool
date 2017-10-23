import ast

from slicer.ScriptedLoadableModule import *

from SlicerDevelopmentToolboxUtils.mixins import *
from SlicerDevelopmentToolboxUtils.widgets import TargetCreationWidget
from SlicerDevelopmentToolboxUtils.buttons import *


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
    """


class LandmarkToolWidget(ModuleWidgetMixin, ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    ScriptedLoadableModuleWidget.__init__(self, parent)

  def cleanup(self):
    pass

  def enter(self):
    pass

  def exit(self):
    self.cleanup()

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.setupViewSettingGroupBox()

    self.createSliceWidgetClassMembers("Red")
    self.createSliceWidgetClassMembers("Yellow")

    self.preopTargetTable = TargetCreationWidget()
    self.preopTargetTable.targetListSelectorVisible = True

    self.intraopTargetTable = TargetCreationWidget()
    self.intraopTargetTable.targetListSelectorVisible = True

    self.layout.addWidget(self.preopTargetTable)
    self.layout.addWidget(self.intraopTargetTable)

    self.layout.addStretch(1)
    self.setupConnections()

  def setupViewSettingGroupBox(self):
    self.sideBySideLayoutButton = SideBySideLayoutButton()
    self.layoutButtons = [self.sideBySideLayoutButton]
    self.crosshairButton = CrosshairButton()
    self.wlEffectsToolButton = WindowLevelEffectsButton()

    viewSettingButtons = [self.sideBySideLayoutButton, self.crosshairButton, self.wlEffectsToolButton]

    self.layout.addWidget(self.createHLayout(viewSettingButtons))

  def setupConnections(self):
    # TODO: release connection when reloading module
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)

    self.preopTargetTable.addEventObserver(self.preopTargetTable.TargetSelectedEvent, self.onTargetSelected)
    self.intraopTargetTable.addEventObserver(self.intraopTargetTable.TargetSelectedEvent, self.onTargetSelected)

  @vtk.calldata_type(vtk.VTK_STRING)
  def onTargetSelected(self, caller, event, callData):
    info = ast.literal_eval(callData)
    node = slicer.mrmlScene.GetNodeByID(info["nodeID"])
    index = info["index"]

    if node is self.preopTargetTable.currentNode:
      sliceNode = self.redSliceNode
    else:
      sliceNode = self.yellowSliceNode

    self.jumpSliceNodeToTarget(sliceNode, node, index)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self, caller, event, calldata):
    node = calldata
    if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      self.applyDefaultTargetDisplayNode(node)

  def applyDefaultTargetDisplayNode(self, targetNode, new=False):
    displayNode = None if new else targetNode.GetDisplayNode()
    modifiedDisplayNode = self.setupDisplayNode(displayNode, True)
    targetNode.SetAndObserveDisplayNodeID(modifiedDisplayNode.GetID())

  def setupDisplayNode(self, displayNode=None, starBurst=False):
    if not displayNode:
      displayNode = slicer.vtkMRMLMarkupsDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
    displayNode.SetTextScale(2.5)
    displayNode.SetGlyphScale(2)
    if starBurst:
      displayNode.SetGlyphType(slicer.vtkMRMLAnnotationPointDisplayNode.StarBurst2D)
    return displayNode