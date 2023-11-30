from PIL import Image
import os
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageExporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        logging.info(f"Image exporter initialized with output directory: {output_dir}")

    def save_image(self, image: Image.Image) -> str:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"Created directory: {self.output_dir}")
            
        output_path = os.path.join(self.output_dir, f"output/out-{timestamp}.png")
        image.save(output_path)
        logging.info(f"Image saved at: {output_path}")
        return output_path
