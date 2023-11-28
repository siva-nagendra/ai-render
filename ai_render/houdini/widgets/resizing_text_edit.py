from PySide2 import QtCore, QtWidgets

class ResizingTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setFixedHeight(self.fontMetrics().lineSpacing() + 40)

    def keyPressEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.key() == QtCore.Qt.Key_C:
                self.copy()
            elif event.key() == QtCore.Qt.Key_V:
                self.paste()
            return

        if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
            if self.parent_widget:
                self.parent_widget.submit_input()
            return

        new_height = min(self.document().size().height() + 10, self.fontMetrics().lineSpacing() * 40 + 10)
        self.setFixedHeight(new_height)
        super().keyPressEvent(event)