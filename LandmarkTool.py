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

    self.preopVolumeSelector = self.createVolumeSelector()
    # preopSelector = self.createHLayout([qt.QLabel("Preop Volume:"), self.preopVolumeSelector])

    self.preopTargetTable = TargetCreationWidget()
    self.preopTargetTable.targetListSelectorVisible = True

    self.intraopVolumeSelector = self.createVolumeSelector()
    # intraopSelector = self.createHLayout([qt.QLabel("Intraop Volume:"), self.intraopVolumeSelector])
    self.intraopTargetTable = TargetCreationWidget()
    self.intraopTargetTable.targetListSelectorVisible = True


    self.layout.addWidget(self.createHLayout([self.createVLayout([self.preopVolumeSelector ,self.preopTargetTable]),
                                              self.createVLayout([self.intraopVolumeSelector , self.intraopTargetTable])]))

    self.layout.addStretch(1)
    self.setupConnections()

  def createVolumeSelector(self):
      return self.createComboBox(nodeTypes=["vtkMRMLScalarVolumeNode", ""], addEnabled=False,
                                 removeEnabled=True, noneEnabled=True, showChildNodeTypes=False,
                                 renameEnabled=True, selectNodeUponCreation=True,
                                 toolTip="Select volume node")

  def setupViewSettingGroupBox(self):
    self.sideBySideLayoutButton = SideBySideLayoutButton()
    self.layoutButtons = [self.sideBySideLayoutButton]

    self.layout.addWidget(self.createHLayout(self.layoutButtons))

  def setupConnections(self):
    # TODO: release connection when reloading module
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)

    self.preopVolumeSelector.currentNodeChanged.connect(self.onPreopVolumeChanged)
    self.preopTargetTable.addEventObserver(self.preopTargetTable.TargetSelectedEvent, self.onTargetSelected)

    self.intraopVolumeSelector.currentNodeChanged.connect(self.onIntraopVolumeChanged)
    self.intraopTargetTable.addEventObserver(self.intraopTargetTable.TargetSelectedEvent, self.onTargetSelected)

  def onPreopVolumeChanged(self, node):
    self.setBackgroundVolume(self.redWidget, node)

  def onIntraopVolumeChanged(self, node):
    self.setBackgroundVolume(self.yellowWidget, node)

  def setBackgroundVolume(self, widget, node):
    compositeNode = widget.mrmlSliceCompositeNode()
    compositeNode.SetBackgroundVolumeID(node.GetID() if node else None)
    sliceNode = widget.sliceLogic().GetSliceNode()
    sliceNode.SetOrientationToAxial()
    sliceNode.RotateToVolumePlane(node)
    sliceLogic = widget.sliceLogic()
    sliceLogic.FitSliceToAll()
    FOV = sliceLogic.GetSliceNode().GetFieldOfView()
    self.setFOV(sliceLogic, [FOV[0] * .5, FOV[1] * .5, FOV[2]])

  @vtk.calldata_type(vtk.VTK_STRING)
  def onTargetSelected(self, caller, event, callData):
    info = ast.literal_eval(callData)
    node = slicer.mrmlScene.GetNodeByID(info["nodeID"])
    index = info["index"]

    if node is self.preopTargetTable.currentNode:
      sliceNode = self.redSliceNode
      otherTable = self.intraopTargetTable
    else:
      sliceNode = self.yellowSliceNode
      otherTable = self.preopTargetTable

    self.jumpSliceNodeToTarget(sliceNode, node, index)

    self.selectTargetIndexInOtherTable(otherTable, index)

  def selectTargetIndexInOtherTable(self, table, index):
    if not table.currentNode or index > table.currentNode.GetNumberOfFiducials():
      return

    table.table.selectRow(index)

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