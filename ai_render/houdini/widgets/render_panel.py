from PySide2 import QtWidgets, QtCore
from PIL import Image
import hou
import logging
from ai_render.config import Config
from ai_render.core import render_engine, render_thread
from ai_render.houdini.widgets.resizing_text_edit import ResizingTextEdit
from ai_render.houdini.managers.image_manager import update_comp_image, export_image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AiRenderPanel(QtWidgets.QWidget):
    image_update_signal = QtCore.Signal(str) 
    def __init__(self, parent=None):
        super(AiRenderPanel, self).__init__(parent)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setWindowTitle("AI Render Panel")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet(hou.qt.styleSheet())
        self.config = Config()
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.text_edit = ResizingTextEdit(self)
        self.text_edit.setPlaceholderText("Enter a prompt here...")
        self.layout.addWidget(self.text_edit)
        
        self.parameters_layout = QtWidgets.QFormLayout()
        
        self.steps_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.seed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.steps_value_edit = QtWidgets.QLineEdit("4")
        self.seed_value_edit = QtWidgets.QLineEdit("0")

        steps_layout = QtWidgets.QHBoxLayout()
        steps_layout.addWidget(self.steps_value_edit)
        steps_layout.addWidget(self.steps_slider)
        self.parameters_layout.addRow("Steps:", steps_layout)

        seed_layout = QtWidgets.QHBoxLayout()
        seed_layout.addWidget(self.seed_value_edit)
        seed_layout.addWidget(self.seed_slider)
        self.parameters_layout.addRow("Seed:", seed_layout)
        
        self.layout.addLayout(self.parameters_layout)
        
        self.connect_viewport_button = QtWidgets.QPushButton("Connect to Viewport")
        self.connect_viewport_button.setCheckable(True)
        self.connect_viewport_button.clicked.connect(self.toggle_viewport_connection)
        self.layout.addWidget(self.connect_viewport_button)
        
        self.render_button = QtWidgets.QPushButton("🎨 Render 🚀")
        self.render_button.clicked.connect(self.on_render_clicked)
        self.layout.addWidget(self.render_button)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.is_rendering = False

        self.setup_parameters()

        self.connect_signals()

    def connect_signals(self):
        self.steps_slider.valueChanged.connect(lambda value: self.steps_value_edit.setText(str(value)))
        self.seed_slider.valueChanged.connect(lambda value: self.seed_value_edit.setText(str(value)))
        self.steps_value_edit.textChanged.connect(lambda value: self.steps_slider.setValue(int(value)))
        self.seed_value_edit.textChanged.connect(lambda value: self.seed_slider.setValue(int(value)))
    
    def toggle_viewport_connection(self):
        if self.connect_viewport_button.isChecked():
            self.connect_viewport_button.setText("Disconnect from Viewport")
            self.config.render_mode = "img2img"
        else:
            self.connect_viewport_button.setText("Connect to Viewport")
            self.config.render_mode = "text2img"

    def setup_parameters(self):
        self.steps_slider.setValue(4)
        self.steps_value_edit.setText("4")

        self.seed_slider.setValue(0)
        self.seed_value_edit.setText("0")

    def on_render_clicked(self):
        if not self.is_rendering:
            self.start_rendering()
        else:
            self.stop_rendering()

    def start_rendering(self):
        prompt = self.text_edit.toPlainText()
        
        if not prompt:
            logging.error("Prompt is empty.")
            hou.ui.displayMessage("Please enter a prompt to continue.", severity=hou.severityType.WarningMessage)
            return

        self.config.prompt = prompt
        self.config.steps = self.steps_slider.value()
        self.config.seed = self.seed_slider.value()

        self.config.output_dir = "/Users/siva/devel/houdini"

        if self.config.render_mode == "img2img":
            img_path = "/Users/siva/devel/ai-render/data/input1.png"
            self.config.image = Image.open(img_path)

        engine = render_engine.RenderEngine(self.config)
        
        self.render_thread = render_thread.RenderThread(engine=engine, on_complete_callback=self.post_render_tasks)

        self.render_button.setText("✋ Stop Rendering")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.is_rendering = True
        self.render_thread.start()

    def stop_rendering(self):
        if self.render_thread.is_alive():
            self.render_thread.stop_rendering()
        
        self.render_button.setText("🎨 Render")
        self.progress_bar.setVisible(False)
        self.is_rendering = False

    def post_render_tasks(self, image: Image.Image):
        image_path = export_image(image[0], self.config.output_dir)
        update_comp_image(self, image_path)
