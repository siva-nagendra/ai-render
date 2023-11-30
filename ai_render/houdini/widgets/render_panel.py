from PySide2 import QtWidgets, QtCore, QtGui
from PIL import Image
from diffusers.utils import load_image

import sys
import hou
import logging
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

        self.steps_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.seed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.steps_value_edit = QtWidgets.QLineEdit()
        self.seed_value_edit = QtWidgets.QLineEdit()

        steps_layout = QtWidgets.QHBoxLayout()
        steps_layout.addWidget(self.steps_value_edit)
        steps_layout.addWidget(self.steps_slider)
        self.parameters_layout.addRow("Steps:", steps_layout)

        seed_layout = QtWidgets.QHBoxLayout()
        seed_layout.addWidget(self.seed_value_edit)
        seed_layout.addWidget(self.seed_slider)
        self.parameters_layout.addRow("Seed:", seed_layout)
        
        self.layout.addLayout(self.parameters_layout)

        self.connect_viewport_button = QtWidgets.QPushButton("Disconnect Viewport")
        self.connect_viewport_button.setCheckable(True)
        self.connect_viewport_button.setChecked(True)
        self.connect_viewport_button.setFixedWidth(150)
        self.config.render_mode = "img2img"
    
        self.button_layout = QtWidgets.QHBoxLayout()
        self.render_button = QtWidgets.QPushButton("🎨 Render 🚀")

        self.button_layout.addWidget(self.connect_viewport_button)
        self.button_layout.addWidget(self.render_button)

        self.layout.addLayout(self.button_layout)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setFixedHeight(7)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

         # Setup for stream redirector
        self.redirector = StreamRedirector()
        self.redirector.textWritten.connect(self.on_text_written)
        sys.stdout = self.redirector
        sys.stderr = self.redirector

        # Add a QTextEdit for logging
        self.log_widget = QtWidgets.QTextEdit(self)
        self.log_widget.setVisible(False)

        self.log_widget.setReadOnly(True)
        self.log_widget.setFixedHeight(50)
        self.layout.addWidget(self.log_widget)

        self.layout.addStretch(1)

        self.is_rendering = False

        self.setup_parameters()

        self.connect_signals()

    def connect_signals(self):
        self.connect_viewport_button.clicked.connect(self.toggle_viewport_connection)
        self.render_button.clicked.connect(self.on_render_clicked)
        self.steps_slider.valueChanged.connect(lambda value: self.steps_value_edit.setText(str(value)))
        self.seed_slider.valueChanged.connect(lambda value: self.seed_value_edit.setText(str(value)))
        self.steps_value_edit.textChanged.connect(lambda value: self.steps_slider.setValue(int(value)))
        self.seed_value_edit.textChanged.connect(lambda value: self.seed_slider.setValue(int(value)))

    def setup_parameters(self):
        self.steps_slider.setValue(4)
        self.steps_value_edit.setText("4")

        self.seed_slider.setValue(0)
        self.seed_value_edit.setText("0")

    def toggle_viewport_connection(self):
        if self.connect_viewport_button.isChecked():
            self.connect_viewport_button.setText("Disconnect Viewport")
            self.config.render_mode = "img2img"
        else:
            self.connect_viewport_button.setText("Connect Viewport")
            self.config.render_mode = "text2img"

    def on_render_clicked(self):
        if not self.is_rendering:
            self.start_rendering()
        else:
            self.stop_rendering()

    def start_rendering(self):
        prompt = self.text_edit.toPlainText()
        
        if not prompt:
            logging.error("Prompt is empty.")
            hou.ui.displayMessage("Please enter a prompt to continue.", severity=hou.severityType.ImportantMessage)
            return

        self.config.prompt = prompt
        self.config.steps = self.steps_slider.value()
        self.config.seed = self.seed_slider.value()

        self.config.output_dir = "/Users/siva/devel/houdini"

        if self.config.render_mode == "img2img":
            img_path = image_manager.capture_viewport(self.config.output_dir, width=self.config.width, height=self.config.height, mask_path=self.config.mask_path)
            self.config.image = load_image(img_path)

        engine = render_engine.RenderEngine(self.config)
        
        self.render_thread = render_thread.RenderThread(engine=engine, on_complete_callback=self.post_render_tasks)

        self.render_button.setText("✋ Stop Rendering")
        self.progress_bar.setVisible(True)
        self.log_widget.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.is_rendering = True
        self.render_thread.start()

    def stop_rendering(self):
        if self.render_thread.is_alive():
            self.render_thread.stop_rendering()
        
        self.render_button.setText("🎨 Render")
        self.progress_bar.setVisible(False)
        self.log_widget.setVisible(False)
        self.is_rendering = False

    def post_render_tasks(self, image: Image.Image):
        image_path = image_manager.export_image(image[0], self.config.output_dir)
        image_manager.update_comp_image(self, image_path)
        self.stop_rendering()

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