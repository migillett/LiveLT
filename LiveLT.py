#!/usr/bin/python3

# built-in
import sys
from os import path
from tkinter import EventType
from turtle import back

# install using pip
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# https://www.geeksforgeeks.org/creating-a-camera-application-using-pyqt5/
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

global captured_data
captured_data = ['LiveLT']


class LiveLTMainGui(QMainWindow):
    def __init__(self):
        super(LiveLTMainGui, self).__init__()

        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.chromaKeyWindow = ChromaKeyWindow()

        self.setWindowTitle('LiveLT Version 0.1')
        self.vfWidth, self.vfHeight = 480, 360

        self.name_index = 0

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            exit()
        
        self.init_gui()

    def init_gui(self):
        # setup central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # create the vertical box layout
        self.veritcalLayout = QVBoxLayout(self.centralWidget)

        # camera selection label
        self.cameraLabel = QLabel('Select a Camera:')
        self.veritcalLayout.addWidget(self.cameraLabel)

        # camera selection
        self.camera_selector = QComboBox()
        self.camera_selector.addItems([camera.description() for camera in self.available_cameras])
        self.camera_selector.currentIndexChanged.connect(self.select_camera)
        self.veritcalLayout.addWidget(self.camera_selector)

        # Video Feed
        self.FeedLabel = QLabel('Select a camera from the dropdown menu above')
        self.FeedLabel.setAlignment(Qt.AlignCenter)
        self.FeedLabel.setFixedSize(self.vfWidth, self.vfHeight)
        self.FeedLabel.setStyleSheet('Border: 1px solid black;')
        self.veritcalLayout.addWidget(self.FeedLabel)

        # Currently displayed name
        self.name_label = QLabel(f'Currently Displaying: {captured_data[0]}')
        self.veritcalLayout.addWidget(self.name_label)

        # Create nested layout for next and previous buttons
        self.nameButtonsWidget = QWidget()
        self.nameButtonsLayout = QHBoxLayout(self.nameButtonsWidget)
        # Previous Name
        self.previousButton = QPushButton('Previous Name')
        self.previousButton.clicked.connect(self.previous_name)
        self.nameButtonsLayout.addWidget(self.previousButton)
        # Next Name
        self.nextButton = QPushButton('Next Name')
        self.nextButton.clicked.connect(self.next_name)
        self.nameButtonsLayout.addWidget(self.nextButton)

        self.veritcalLayout.addWidget(self.nameButtonsWidget)

        # Display Default
        self.showDefault = QPushButton('Display Default')
        self.showDefault.clicked.connect(self.previous_name)
        self.veritcalLayout.addWidget(self.showDefault)

        # Start second chromakey window
        self.startChromaKeyButton = QPushButton('Begin Secondary Display')
        self.startChromaKeyButton.clicked.connect(self.initializeChromaKey)
        self.veritcalLayout.addWidget(self.startChromaKeyButton)

    def viewFrame(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def stopCamera(self):
        try:
            self.worker.stop()
        except AttributeError: # if the camera isn't open, ignore the error it throws
            pass

    def select_camera(self, index):
        self.stopCamera()
        self.worker = ImageWorker(camera_index=index, width=self.vfWidth, height=self.vfHeight)
        self.worker.start()
        self.worker.ImageUpdate.connect(self.viewFrame)

    def previous_name(self):
        if self.name_index != 0:
            self.name_index -= 1
            self.update_name_label(captured_data[self.name_index])
            self.chromaKeyWindow.updateTitle(captured_data[self.name_index])

    def next_name(self):
        if self.name_index + 2 <= len(captured_data):
            self.name_index += 1
            self.update_name_label(captured_data[self.name_index])
            self.chromaKeyWindow.updateTitle(captured_data[self.name_index])

    def show_default_name(self):
        self.update_name_label(captured_data[0])
        self.chromaKeyWindow.updateTitle(captured_data[0])

    def update_name_label(self, name):
        self.name_label.setText(f'Currently Displaying: {name}')

    def initializeChromaKey(self):
        self.chromaKeyWindow.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_name()
        elif event.key() == Qt.Key_Left:
            self.previous_name()
        elif event.key() == Qt.Key_Space:
            self.show_default_name()

    def exit(self):
        self.capture.release()
        cv2.destroyAllWindows()


class ChromaKeyWindow(QMainWindow):
    def __init__(self, bkgnd_color='#009933', lt_color='#003366'):
        super(ChromaKeyWindow, self).__init__()

        self.bkgnd_color = bkgnd_color
        self.lt_color = lt_color

        self.w, self.h = 1280, 720
        self.resize(self.w, self.h)
        self.setWindowTitle('LiveLT Chromakey')
        self.setStyleSheet(f'background-color: {self.bkgnd_color};') #chroma-key green

    def InitGui(self):
        self.name_label = QLabel(self)
        self.name_label.setText('LiveLT')

        font = QFont()
        font.setFamily('Arial')
        self.name_label.setFont(font)

    def updateTitle(self, text):
        self.name_label.setText(text)

    def paintEvent(self, event):
        self.width, self.height = self.window
        painter = QPainter(self)
        painter.setBrush(QColor(self.lt_color))
        painter.drawRect(0, int(self.h*0.8), self.w, int(self.h*.15))

        # current_dir = path.dirname(path.realpath(__file__))
        # self.PixmapPath = path.join(current_dir, 'assets', 'ltbkgd.png')
        # self.ltLabel = QLabel(self)
        # self.pixmap = QPixmap(self.PixmapPath).scaled(self.width, self.height)
        # self.ltLabel.setPixmap(self.pixmap)
        # self.ltLabel.resize(self.pixmap.width(), self.pixmap.height())

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if (EventType() == QEvent.Resize):
            self.paintEvent()
        return super().eventFilter(a0, a1)

    # def eventFilter(self, obj, event):
    #     if (event.type() == QEvent.Resize):
    #         self.paintEvent()
    #         # if not self.pix.isNull():
    #         #     pixmap = self.pix.scaled(self.width(), self.height(),Qt.KeepAspectRatio)
    #         #     if pixmap.width()!=self.width() or pixmap.height()!=self.height():
    #         self.ResizeSignal.emit(1)
    #     return super().eventFilter(obj, event)


class ImageWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def __init__(self, camera_index, width=640, height=480):
        super().__init__()
        self.width, self.height = width, height
        self.camera_index = camera_index
        self.capture = cv2.VideoCapture(camera_index)
        self.ThreadActive = True

        self.player = QMediaPlayer()

        self.qrscan = cv2.QRCodeDetector()

    def confirm_audio(self):
        current_dir = path.dirname(path.realpath(__file__))
        url = QUrl.fromLocalFile(path.join(current_dir, 'assets', 'cork.mp3'))
        content = QMediaContent(url)

        self.player.setMedia(content)
        self.player.setVolume(100)
        self.player.play()

    def run(self):
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(self.width, self.height, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)

                data, points, _ = self.qrscan.detectAndDecode(frame)
                if len(data) > 0:
                    if data != captured_data[-1]:
                        captured_data.append(data)
                        print(captured_data)
                        self.confirm_audio()

    def stop(self):
        self.ThreadActive = False
        self.quit()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveLTMainGui()
    window.show()
    sys.exit(app.exec())