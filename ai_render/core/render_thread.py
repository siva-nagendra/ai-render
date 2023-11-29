import threading
import logging
import warnings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

class RenderThread(threading.Thread):
    def __init__(self, engine, on_complete_callback):
        super().__init__()
        self.engine = engine
        self.on_complete = on_complete_callback
        self.rendered_image = None
        self._stop_event = threading.Event()

    def run(self):
        try:
            logging.info("Rendering...")
            if not self._stop_event.is_set():
                self.model = self.engine.load_model()
                self.rendered_image = self.engine.render(model=self.model)
            if not self.rendered_image:
                raise Exception("Rendering failed.")
            logging.info("Rendering completed successfully.")
            print("Rendering completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during rendering: {e}")
        finally:
            self.on_complete(self.rendered_image)
    
    def stop_rendering(self):
        self._stop_event.set()
        logging.info("Stopping rendering...")