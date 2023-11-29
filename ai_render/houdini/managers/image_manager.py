import hou
import time
import os
import logging
from ai_render.core.exporter import ImageExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def getSceneViewer() -> hou.SceneViewer:
    """
    return an instance of a visible viewport. 
    There may be many, some could be closed, any visible are current
    """
    panetabs = hou.ui.paneTabs()
    panetabs = [x for x in panetabs if x.type() == hou.paneTabType.SceneViewer]
    panetabs = sorted(panetabs, key=lambda x: x.isCurrentTab())
    if panetabs:
        return panetabs[-1]
    else:
        print("No SceneViewers detected.")
        return None

def update_comp_image(self, image_path: str) -> None:
    comp_network_path: str = '/img/comp1'
    node_name: str = 'default_pic'
    
    comp_net: hou.NetworkNode = hou.node(comp_network_path)

    if not comp_net:
        img_network: hou.NetworkNode = hou.node('/img')
        comp_net = img_network.createNode('img', 'comp1')
    
    comp_node: hou.Node = comp_net.node(node_name)
    
    if not comp_node:
        comp_node = comp_net.createNode('file', node_name)
    
    comp_node.parm('filename1').set(image_path)
    comp_net.layoutChildren()
    self.stop_rendering()

def export_image(image, output_dir: str) -> str:
    logging.info("Saving image...")
    exporter: ImageExporter = ImageExporter(output_dir)
    image_path: str = exporter.export(image)
    logging.info(f"Image saved at: {image_path}")
    return image_path

def get_time_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def get_image_path(output_dir: str) -> str:
    return os.path.join(output_dir, f"input/in-{get_time_stamp()}.jpg") 

def capture_viewport(output_dir: str, frame_start: int = 1, frame_end: int = 1, width: int = 1024, height: int = 1024) -> str:
    sceneview: hou.SceneViewer = getSceneViewer()
    viewport: hou.Viewport = sceneview.curViewport()
    image_path: str = get_image_path(output_dir)

    flipbook_settings: hou.FlipbookSettings = sceneview.flipbookSettings().stash()
    flipbook_settings.frameRange((frame_start, frame_end))
    flipbook_settings.outputToMPlay(False)

    flipbook_settings.useResolution(True)
    flipbook_settings.resolution((768, 768))
    flipbook_settings.output(image_path)

    viewport: hou.Viewport = sceneview.curViewport()

    sceneview.flipbook(viewport, flipbook_settings)
    logging.info(f"Viewport snapshot saved at: {image_path}")
    return image_path