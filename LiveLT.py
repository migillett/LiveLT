# https://www.zebra.com/us/en/support-downloads/scanners/general-purpose-scanners/ds4308.html#pageandfilelist_e56b
# https://pythonspot.com/pyqt5-textbox-example/

import sys
from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt

import qrcode

def create_qr(data, filename):
    img = qrcode.make(data)
    img.save(filename)

class App(QWidget):
    def __init__(self):
        super().__init__()
        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.title = 'LiveLT Version 0.1'
        self.left = 10
        self.top = 10
        self.width = 440
        self.height = 400
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(400,25)

        # Create name list
        self.name_list = QListWidget(self)
        self.name_list.setGeometry(20,60,400,250)
        
        # # Create a button in the window
        # self.button = QPushButton('Show text', self)
        # self.button.move(20,80)
        # self.button.clicked.connect(self.save_name)

        self.show()
    
    def select_name(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.name_list.addItem(self.textbox.text())
            self.textbox.setText("")
    
    # @pyqtSlot()
    # def save_name(self):
    #     self.names.append(self.textbox.text())
    #     self.textbox.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())