from PySide2 import QtWidgets, QtCore
from PIL import Image
import hou
import os
import logging
from ai_render.config.config import Config
from ai_render.render_manager.render_thread import RenderThread
from ai_render.core import render_from_text
from ai_render.core.utils.exporter import ImageExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AiRenderPanel(QtWidgets.QWidget):
    image_update_signal = QtCore.Signal(str) 
    def __init__(self, parent=None):
        super(AiRenderPanel, self).__init__(parent)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setStyleSheet(hou.qt.styleSheet())
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Create the text edit with Houdini style
        self.text_edit = AutoResizingTextEdit(self)
        self.text_edit.setPlaceholderText("Enter a prompt here...")
        self.layout.addWidget(self.text_edit)
        
        # Parameters layout
        self.parameters_layout = QtWidgets.QFormLayout()
        
        # Sliders
        self.width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.height_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.steps_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.seed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        
        # Value labels
        self.width_value_label = QtWidgets.QLabel("512")
        self.height_value_label = QtWidgets.QLabel("512")
        self.steps_value_label = QtWidgets.QLabel("8")
        self.seed_value_label = QtWidgets.QLabel("0")  # Assuming seed_slider is a slider
        
        # Connect sliders to labels
        self.width_slider.valueChanged.connect(lambda value: self.width_value_label.setText(str(value)))
        self.height_slider.valueChanged.connect(lambda value: self.height_value_label.setText(str(value)))
        self.steps_slider.valueChanged.connect(lambda value: self.steps_value_label.setText(str(value)))
        self.seed_slider.valueChanged.connect(lambda value: self.seed_value_label.setText(str(value)))
        
        # Add widgets to layout
        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.width_value_label)
        width_layout.addWidget(self.width_slider)
        self.parameters_layout.addRow("Width:", width_layout)

        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(self.height_value_label)
        height_layout.addWidget(self.height_slider)
        self.parameters_layout.addRow("Height:", height_layout)

        steps_layout = QtWidgets.QHBoxLayout()
        steps_layout.addWidget(self.steps_value_label)
        steps_layout.addWidget(self.steps_slider)
        self.parameters_layout.addRow("Steps:", steps_layout)

        seed_layout = QtWidgets.QHBoxLayout()
        seed_layout.addWidget(self.seed_value_label)
        seed_layout.addWidget(self.seed_slider)
        self.parameters_layout.addRow("Seed:", seed_layout)
        
        self.layout.addLayout(self.parameters_layout)
        
        # Create the render button with Houdini style
        self.render_button = QtWidgets.QPushButton("🎨 Render 🚀")
        self.render_button.clicked.connect(self.on_render_clicked)
        self.layout.addWidget(self.render_button)
        
        # Create QLabel for the image
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        # Setup parameters
        self.setup_parameters()
        
        self.setWindowTitle("AI Render Panel")  # Set window title
        self.setGeometry(500, 300, 300, 150)  # Set window size and position

        self.connect_signals()
    
    def connect_signals(self):
        self.image_update_signal.connect(self.update_comp_image)

    def setup_parameters(self):
        self.width_slider.setRange(256, 1024)
        self.height_slider.setRange(256, 1024)
        self.steps_slider.setRange(1, 50)
        self.seed_slider.setRange(0, 9999)

        self.width_slider.setValue(512)
        self.height_slider.setValue(512)
        self.steps_slider.setValue(4)
        self.seed_slider.setValue(0)

    def on_render_clicked(self):
        prompt = self.text_edit.toPlainText()
        
        if not prompt:
            logging.error("Prompt is empty.")
            return

        width = self.width_slider.value()
        height = self.height_slider.value()
        steps = self.steps_slider.value()
        seed = self.seed_slider.value()
        hip_dir = "/Users/siva/devel/houdini"
        output_dir = os.path.join(hip_dir, "output")

        self.config = Config(
            output_dir=output_dir,
            prompt=prompt,
            width=width,
            height=height,
            steps=steps,
            seed=seed,
        )
        engine = render_from_text.RenderFromText(self.config)
        
        self.render_thread = RenderThread(engine=engine, on_complete_callback=self.save_image)
        self.render_thread.start()

    def save_image(self, image: Image.Image):
        logging.info("Saving image...")
        image_exporter = ImageExporter(self.config.output_dir)  # Use a different variable name
        image_path = image_exporter.export(image)
        logging.info(f"Image saved at: {image_path}")
        self.image_update_signal.emit(image_path)

    def update_comp_image(self, image_path):
        # Define the path to the composite network and the node name
        comp_network_path = '/img/ai_render_comp'  # Updated as per your request
        node_name = 'default_pic'
        
        # Get the composite network node
        comp_net = hou.node(comp_network_path)
        
        # If the composite network doesn't exist, create it
        if not comp_net:
            img_network = hou.node('/img')
            comp_net = img_network.createNode('img', 'ai_render_comp')
        
        # Check if the node exists
        comp_node = comp_net.node(node_name)
        
        # If the node doesn't exist, create it
        if not comp_node:
            comp_node = comp_net.createNode('file', node_name)
        
        # Set the filename parameter to the image path
        comp_node.parm('filename1').set(image_path)
        comp_net.layoutChildren()

    def _paneActivated(self, pane_tab):
        pass

    def _paneDeactivated(self):
        pass

    def _paneClosed(self):
        pass

class AutoResizingTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setFixedHeight(self.fontMetrics().lineSpacing() + 20)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
            if self.parent_widget:
                self.parent_widget.submit_input()
            return

        new_height = min(self.document().size().height() + 10, self.fontMetrics().lineSpacing() * 15 + 10)
        self.setFixedHeight(new_height)
