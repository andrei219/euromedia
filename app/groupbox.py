



from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal


class GroupBox(QGroupBox):

    focus_in = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent) 
        
    
    def focusInEvent(self, event):
        self.focus_in.emit()
        super().focusInEvent(event) 