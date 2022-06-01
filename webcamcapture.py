#!/usr/bin/python3

import sys

# pip install python-opencv
import cv2 

# pip install pyqt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

title = 'LiveLT | Version 0.1'

captured_data = [] # list of all names captured by QRCodeCapture

class LiveLtGUI(QMainWindow):
    def __init__(self, width=1280, height=720):
        QMainWindow.__init__(self)

        self.setWindowTitle = title
        self.setGeometry(10, 10, width, height)

        self.menubar_gui()

        self.name_label = QLabel(self)
        self.name_label.setText('Georgia College & State University')

    def menubar_gui(self):
        # optionsAction = QAction(' &Options', self)
        # optionsAction.setStatusTip('Webcam Options')

        exitAction = QAction(' &Exit', self)
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()

        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAction)
    
    def update_name(self):
        self.name_label.setText(captured_data[-1])


class QRCodeCapture():
    def __init__(self, webcam_select=0, width=1280, height=720, brightness=150, webcam_view=False) -> None:
        self.webcam_select = webcam_select
        self.webcam_view = webcam_view
        self.width, self.height = width, height
        self.brightness = brightness

        self.init_camera()

        self.qrscan = cv2.QRCodeDetector()
        
        self.captured_data = []

        self.capture_QRCode() # while loop

        self.capture.release()
        cv2.destroyAllWindows()
        exit(0)

    def init_camera(self):
        self.capture = cv2.VideoCapture(self.webcam_select)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        self.capture.open(self.webcam_select)
        print('Webcam active')

    def capture_QRCode(self):
        while self.capture.isOpened():
            ret, frame = self.capture.read()

            if frame is not None:
                if self.webcam_view:
                    cv2.imshow(title, frame)
        
                data, points, _ = self.qrscan.detectAndDecode(frame)

                if len(data) > 0: # if a QR is detected
                    if data not in self.captured_data: # and is not a duplicate of past scan
                        captured_data.append(data)
                        LiveLtGUI.update_name()

                if cv2.waitKey(1) & 0xFF==27: # escape key cancel
                    print('Webcam closed')
                    break

            else:
                print('Error loading webcam. Executing re-initialization')
                self.capture.release()
                self.init_camera()

# try:
#     QRCodeCapture(webcam_select=2)
# except KeyboardInterrupt:
#     exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveLtGUI()
    window.show()
    sys.exit(app.exec_())