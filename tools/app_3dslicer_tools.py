from tools.tools import function_tool
from utils.app_3dslicer_client import SlicerClient
import subprocess
import os
import signal

SLICER_EXE_PATH = r"C:/Users/Riddle/AppData/Local/slicer.org/Slicer 5.8.1/Slicer.exe"  # Update this path as needed
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(PROJECT_DIR, "slicer_server", "slicer_file_server.py")

slicer_process = None

def safe_result(result):
    return str(result) if result else '[No result returned]'

@function_tool
def open_slicer() -> str:
    """
    Open 3D Slicer and run the file server script.
    Returns:
        str: Status message
    """
    global slicer_process
    if slicer_process is not None and slicer_process.poll() is None:
        return "Slicer is already running."
    try:
        slicer_process = subprocess.Popen([
            SLICER_EXE_PATH,
            "--python-script",
            SLICER_SERVER_SCRIPT
        ])
        return "Slicer started successfully."
    except Exception as e:
        return f"Failed to start Slicer: {e}"

@function_tool
def close_slicer(save: bool = True) -> str:
    """
    Close 3D Slicer application.
    Args:
        save (bool): Whether to save before closing (default: True)
    Returns:
        str: Status message
    """
    client = SlicerClient()
    if save:
        slicer_code = '''
scenePath = slicer.mrmlScene.GetURL()
slicer.util.saveScene(scenePath)
slicer.app.exit()
print("Slicer project saved and application closed.")
'''
    else:
        slicer_code = '''
slicer.app.exit()
print("Slicer application closed without saving.")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def set_view_coronal() -> str:
    """
    Set the 3D Slicer view to coronal.
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = '''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
    redWidget = layoutManager.sliceWidget('Red')
    if redWidget is not None:
        redWidget.sliceLogic().GetSliceNode().SetOrientationToCoronal()
print("View set to coronal.")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def set_view_axial() -> str:
    """
    Set the 3D Slicer view to axial.
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = '''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
    redWidget = layoutManager.sliceWidget('Red')
    if redWidget is not None:
        redWidget.sliceLogic().GetSliceNode().SetOrientationToAxial()
print("View set to axial.")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def set_view_sagittal() -> str:
    """
    Set the 3D Slicer view to sagittal.
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = '''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
    redWidget = layoutManager.sliceWidget('Red')
    if redWidget is not None:
        redWidget.sliceLogic().GetSliceNode().SetOrientationToSagittal()
print("View set to sagittal.")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def scroll_slice_up(steps: int = 1) -> str:
    """
    Scroll up (forward) by a number of slices in the current view.
    Args:
        steps (int): Number of slices to scroll up
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = f'''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    redWidget = layoutManager.sliceWidget('Red')
    if redWidget is not None:
        for i in range({steps}):
            redWidget.sliceLogic().StartSliceOffsetInteraction()
            redWidget.sliceLogic().GetSliceNode().SetSliceOffset(redWidget.sliceLogic().GetSliceOffset() + 1)
            redWidget.sliceLogic().EndSliceOffsetInteraction()
            slicer.app.processEvents()
print("Scrolled up {steps} slice(s).")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def scroll_slice_down(steps: int = 1) -> str:
    """
    Scroll down (backward) by a number of slices in the current view.
    Args:
        steps (int): Number of slices to scroll down
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = f'''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    redWidget = layoutManager.sliceWidget('Red')
    if redWidget is not None:
        for i in range({steps}):
            redWidget.sliceLogic().StartSliceOffsetInteraction()
            redWidget.sliceLogic().GetSliceNode().SetSliceOffset(redWidget.sliceLogic().GetSliceOffset() - 1)
            redWidget.sliceLogic().EndSliceOffsetInteraction()
            slicer.app.processEvents()
print("Scrolled down {steps} slice(s).")
'''
    return safe_result(client.send_code(slicer_code))

@function_tool
def set_view_overview_4up() -> str:
    """
    Set the 3D Slicer layout to 4-up (overview) view.
    Returns:
        str: Result of the operation from Slicer
    """
    client = SlicerClient()
    slicer_code = '''
layoutManager = slicer.app.layoutManager()
if layoutManager is not None:
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
print("View set to 4-up (overview) mode.")
'''
    return safe_result(client.send_code(slicer_code))


