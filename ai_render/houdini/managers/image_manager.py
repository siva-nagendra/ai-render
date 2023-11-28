import hou
import logging
from ai_render.core.exporter import ImageExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_comp_image(self, image_path):
    comp_network_path = '/img/comp1'
    node_name = 'default_pic'
    
    comp_net = hou.node(comp_network_path)

    if not comp_net:
        img_network = hou.node('/img')
        comp_net = img_network.createNode('img', 'comp1')
    
    comp_node = comp_net.node(node_name)
    
    if not comp_node:
        comp_node = comp_net.createNode('file', node_name)
    
    comp_node.parm('filename1').set(image_path)
    comp_net.layoutChildren()
    self.stop_rendering()

def export_image(image, output_dir):
    logging.info("Saving image...")
    exporter = ImageExporter(output_dir)
    image_path = exporter.export(image)
    logging.info(f"Image saved at: {image_path}")
    return image_path