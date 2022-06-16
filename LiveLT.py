#!/usr/bin/python3

# built-in
import sys
from tkinter import Image

# install using pip
import cv2
import qrcode
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# https://www.geeksforgeeks.org/creating-a-camera-application-using-pyqt5/
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

# def create_qr(data, filename):
#     img = qrcode.make(data)
#     img.save(filename)

global captured_data
captured_data = ['Georgia College & State University']

class LiveLT(QWidget):
    def __init__(self):
        super(LiveLT, self).__init__()
        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('LiveLT Version 0.1')
        self.width, self.height = 440, 440
        self.setGeometry(10, 10, self.width, self.height)

        # self.captured_data = []
        self.name_index = 0
        
        self.VBL = QVBoxLayout()

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            exit()

        # toolbar = QToolBar('Camera Tool Bar')
        # self.addToolBar(toolbar)

        # # camera selection
        # camera_selector = QComboBox()
        # camera_selector.addItems([camera.description() for camera in self.available_cameras])
        # camera_selector.currentIndexChanged.connect(self.initCamera)

        # toolbar.addWidget(camera_selector)

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.cancelButton = QPushButton('Exit')
        self.cancelButton.clicked.connect(self.stopCamera)
        self.VBL.addWidget(self.cancelButton)

        self.name_label = QLabel()
        self.VBL.addWidget(self.name_label)

        self.worker = ImageWorker(camera_index=2)
        self.worker.start()
        self.worker.ImageUpdate.connect(self.viewFrame)

        self.setLayout(self.VBL)

    def viewFrame(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def stopCamera(self):
        self.worker.stop()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.name_index += 1
            try:
                print(captured_data[self.name_index])
                self.name_label.setText(captured_data[self.name_index])
            except IndexError:
                self.name_label.setText(captured_data[-1])
                print(captured_data[-1])

        elif event.key() == Qt.Key_Left:
            if self.name_index > 0:
                self.name_index -= 1
                print(captured_data[self.name_index])
                self.name_label.setText(captured_data[self.name_index])

    def exit(self):
        self.capture.release()
        cv2.destroyAllWindows()


class ImageWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.capture = cv2.VideoCapture(camera_index)
        self.ThreadActive = True

        self.captured_data = []

        self.qrscan = cv2.QRCodeDetector()

    def run(self):
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)

                data, points, _ = self.qrscan.detectAndDecode(frame)
                if len(data) > 0:
                    # LiveLT.update_names(data)
                    if data not in captured_data:
                        captured_data.append(data)
                        print(captured_data)

    def stop(self):
        self.ThreadActive = False
        self.quit()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveLT()
    window.show()
    sys.exit(app.exec())