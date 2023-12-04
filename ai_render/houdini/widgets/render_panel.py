import os
import sys
import hou
import logging
from PIL import Image
from PySide2 import QtWidgets, QtCore, QtGui
from diffusers.utils import load_image, make_image_grid
from ai_render.config import Config
from ai_render.core import render_engine, render_thread
from ai_render.houdini.managers import image_manager

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

        self.render_thread = None

        self.grid_mode = False

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.header_label = QtWidgets.QLabel("AI Render")
        font = self.header_label.font()
        font.setPointSize(25)
        font.setBold(True)
        self.header_label.setFont(font)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setFixedHeight(50)
        self.text_edit.setPlaceholderText("Enter a prompt here...")
        self.layout.addWidget(self.text_edit)

        self.parameters_layout = QtWidgets.QFormLayout()
        self.parameters_layout.setSpacing(8)

        self.steps_value_edit = QtWidgets.QLineEdit()
        self.seed_value_edit = QtWidgets.QLineEdit()
        self.guidance_scale_value_edit = QtWidgets.QLineEdit()
        self.strength_value_edit = QtWidgets.QLineEdit()

        self.parameters_layout.addRow("Steps:", self.steps_value_edit)
        self.parameters_layout.addRow("Seed:", self.seed_value_edit)
        self.parameters_layout.addRow("Guidance Scale:", self.guidance_scale_value_edit)
        self.parameters_layout.addRow("Strength:", self.strength_value_edit)
        
        self.layout.addLayout(self.parameters_layout)

        self.grid_mode_checkbox = QtWidgets.QCheckBox("Grid Mode")
        self.grid_mode_checkbox.setChecked(False)
        self.layout.addWidget(self.grid_mode_checkbox)
        
        self.button_layout = QtWidgets.QHBoxLayout()
        self.render_button = QtWidgets.QPushButton("🎨 Render 🚀")

        self.button_layout.addWidget(self.render_button)

        self.layout.addLayout(self.button_layout)
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setFixedHeight(7)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.redirector = StreamRedirector()
        self.redirector.textWritten.connect(self.on_text_written)
        sys.stdout = self.redirector
        sys.stderr = self.redirector

        self.log_widget = QtWidgets.QTextEdit(self)
        self.log_widget.setVisible(False)

        self.log_widget.setReadOnly(True)
        self.log_widget.setFixedHeight(40)
        self.layout.addWidget(self.log_widget)

        self.layout.addStretch(1)

        self.is_rendering = False

        self.setup_parameters()
        self.load_engine()

        self.connect_signals()

    def connect_signals(self):
        self.grid_mode_checkbox.stateChanged.connect(self.toggle_grid_mode)
        self.render_button.clicked.connect(self.on_render_clicked)
    
    def toggle_grid_mode(self, state):
        if state == QtCore.Qt.Checked:
            self.grid_mode = True
        else:
            self.grid_mode = False

    def setup_parameters(self):
        self.steps_value_edit.setText(str(self.config.steps))
        self.seed_value_edit.setText(str(self.config.seed))
        self.guidance_scale_value_edit.setText(str(self.config.guidance_scale))
        self.strength_value_edit.setText(str(self.config.strength))

    def on_render_clicked(self):
        if not self.is_rendering:
            self.is_rendering = True
            self.render_button.setText("✋ Stop Rendering")
            self.progress_bar.setVisible(True)
            self.log_widget.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.start_rendering()
        else:
            self.is_rendering = False
            self.render_button.setText("🎨 Render")
            self.progress_bar.setVisible(False)
            self.log_widget.setVisible(False)
            self.stop_rendering()

    def load_engine(self):
        self.engine = render_engine.RenderEngine(self.config)

    def start_rendering(self):
        prompt = self.text_edit.toPlainText()
        
        if not prompt:
            logging.error("Prompt is empty.")
            hou.ui.displayMessage("Please enter a prompt to continue.", severity=hou.severityType.ImportantMessage)
            return

        self.config.prompt = prompt
        self.config.steps = int(self.steps_value_edit.text())
        self.config.seed = int(self.seed_value_edit.text())
        self.config.guidance_scale = float(self.guidance_scale_value_edit.text())
        self.config.strength = float(self.strength_value_edit.text())

        self.grid_mode = self.grid_mode_checkbox.isChecked()

        self.config.output_dir = "/tmp/ai-render"

        self.clean_image = image_manager.capture_viewport(self.config.output_dir, width=self.config.width, height=self.config.height, mask_path=self.config.mask_path)
        self.config.image = load_image(self.clean_image)

        if self.render_thread is not None and self.render_thread.is_alive():
            self.render_thread.stop_rendering()
        self.render_thread = render_thread.RenderThread(engine=self.engine, config=self.config, on_complete_callback=self.post_render_tasks)
        self.render_thread.start()

    def stop_rendering(self):
        if self.render_thread and self.render_thread.is_alive():
            self.render_thread.stop_rendering()
            self.render_thread.join()

    def post_render_tasks(self, image: Image.Image):
        print("Post render tasks")
        rendered_image = image[0]

        if self.grid_mode:
            rendered_image = make_image_grid([load_image(self.clean_image), image[0]], rows=1, cols=2)
    
        image_path = image_manager.export_image(rendered_image, self.config.output_dir)
        print(f"Image path: {image_path}")
        # image_manager.update_comp_image(self, image_path)
        # print("Updated comp image")

    def on_text_written(self, text):
        self.log_widget.moveCursor(QtGui.QTextCursor.End)
        self.log_widget.insertPlainText(text)

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class StreamRedirector(QtCore.QObject):
    textWritten = QtCore.Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass