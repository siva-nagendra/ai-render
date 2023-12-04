import hou
import time
import os
import logging
from ai_render.core.cleanup import process_image

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

def update_comp_image(image_path: str) -> None:
    print(f"Updating comp image at: {image_path}")
    comp_network_path: str = '/img/comp1'
    node_name: str = 'default_pic'
    
    comp_net: hou.NetworkNode = hou.node(comp_network_path)

    if not comp_net:
        img_network: hou.NetworkNode = hou.node('/img')
        comp_net = img_network.createNode('img', 'comp1')
    
    comp_node: hou.Node = comp_net.node(node_name)
    
    if not comp_node:
        comp_node = comp_net.createNode('file', node_name)
    print(f"Updating comp image at: {image_path}")
    comp_node.parm('filename1').set(image_path)
    comp_net.layoutChildren()

def export_image(image, output_dir: str) -> str:
    image_path = os.path.join(output_dir, f"output/out-{get_time_stamp()}.jpg")
    os.makedirs(os.path.join(output_dir, "output"), exist_ok=True)
    image.save(image_path)
    print(f"Image saved at: {image_path}")
    update_comp_image(image_path)
    print("Updated comp image")
    return image_path

def get_time_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def get_image_path(output_dir: str) -> str:
    image_path = os.path.join(output_dir, f"input/in-{get_time_stamp()}.jpg")
    os.makedirs(os.path.join(output_dir, "input"), exist_ok=True)
    return image_path

def get_cleaned_image_path(output_dir: str) -> str:
    image_path = os.path.join(output_dir, f"cleaned/cleaned-{get_time_stamp()}.jpg")
    os.makedirs(os.path.join(output_dir, "cleaned"), exist_ok=True)
    return image_path

def get_output_image_path(output_dir: str) -> str:
    image_path = os.path.join(output_dir, f"output/out-{get_time_stamp()}.jpg")
    os.makedirs(os.path.join(output_dir, "output"), exist_ok=True)
    return image_path

def capture_viewport(output_dir: str, width, height, mask_path) -> str:
    sceneview: hou.SceneViewer = getSceneViewer()
    viewport: hou.Viewport = sceneview.curViewport()
    image_path: str = get_image_path(output_dir)

    flipbook_settings: hou.FlipbookSettings = sceneview.flipbookSettings().stash()
    flipbook_settings.frameRange((1, 1))
    flipbook_settings.outputToMPlay(False)

    flipbook_settings.useResolution(True)
    flipbook_settings.resolution((width, height))
    flipbook_settings.output(image_path)
    cleaned_image_path = get_cleaned_image_path(output_dir)

    viewport: hou.Viewport = sceneview.curViewport()

    sceneview.flipbook(viewport, flipbook_settings)
    
    process_image(file_path=image_path,
                cleaned_path=cleaned_image_path,
                mask_path=mask_path)

    logging.info(f"Viewport snapshot saved at: {cleaned_image_path}")
    return cleaned_image_path