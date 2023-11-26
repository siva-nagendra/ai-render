
from PySide2 import QtWidgets, QtCore, QtGui
from PIL import Image
import hou
import io

class AiRenderPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AiRenderPanel, self).__init__(parent)
        
        self.layout = QtWidgets.QVBoxLayout()

        # Create a button
        self.button = QtWidgets.QPushButton("Hello World")
        self.button.clicked.connect(self.on_button_clicked)
        self.layout.addWidget(self.button)

        # Create an image label
        self.image_label = QtWidgets.QLabel()
        self.image_label.setMinimumSize(512, 512)  # Set minimum size for the image viewer
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

    def on_button_clicked(self):
        hou.ui.displayMessage("Hello World!")

    def display_pil_image(self, pil_img):
        # Convert PIL image to QPixmap and display it
        byte_array = io.BytesIO()
        pil_img.save(byte_array, format='PNG')
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(byte_array.getvalue())
        scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
    

    def _paneActivated(self, pane_tab):
        """ Called when the python panel pane is activated. """

        pass
    

    def _paneDeactivated(self):
        """ Called when the python panel pane is deactivated. """

        pass


    def _paneClosed(self):
        """ Called when the python panel pane is closed. """

        pass

