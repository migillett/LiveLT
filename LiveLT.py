#!/usr/bin/python3

# built-in
import sys
from os import path
import json

# install using pip
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# sudo apt-get build-dep qtmultimedia5-dev
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

# Local
from functions.TricasterDataLink import tricaster_data_link

'''
### TO DO LIST ###
- add in a way to have text auto-scale on lower thirds (long names)
- options menu to change running config
'''

global captured_data
captured_data = []


class LiveLTMainGui(QMainWindow):
    def __init__(self):
        super(LiveLTMainGui, self).__init__()

        self.current_dir = path.dirname(path.realpath(__file__))
        self.config_json = path.join(self.current_dir, 'config.json')

        self.config = {
            'webcam_index': 0,
            'vf_dimensions': (480, 360),
            'default_slide': 'LiveLT',
            'tricaster_ipaddr': ''
        }

        self.loadConfig()
        captured_data.append(self.config['default_slide'])

        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('LiveLT Version 0.1')

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

        # Tricaster IP Address Label
        # self.tc_ip_label = QLabel('Tricaster IP Address:')
        # self.veritcalLayout.addWidget(self.tc_ip_label)

        # Tricaster IP textbox
        # self.tc_ip_textbox = QLineEdit(self).setText(self.config['tricaster_ipaddr'])
        # self.veritcalLayout.addWidget(self.tc_ip_textbox)

        # camera selection label
        self.cameraLabel = QLabel('Select a Camera:')
        self.veritcalLayout.addWidget(self.cameraLabel)

        # camera selection
        self.camera_selector = QComboBox()
        self.camera_selector.addItems([camera.description() for camera in self.available_cameras])
        self.camera_selector.setCurrentIndex(self.config['webcam_index'])
        self.select_camera(index=self.config['webcam_index'])
        self.camera_selector.currentIndexChanged.connect(self.select_camera)
        self.veritcalLayout.addWidget(self.camera_selector)

        # Video Feed
        self.FeedLabel = QLabel('Select a camera from the dropdown menu above')
        self.FeedLabel.setAlignment(Qt.AlignCenter)
        self.FeedLabel.setFixedSize(self.config['vf_dimensions'][0], self.config['vf_dimensions'][1])
        self.FeedLabel.setStyleSheet('Border: 1px solid black;')
        self.veritcalLayout.addWidget(self.FeedLabel)

        # Selectable list of names scanned
        self.scannedNamesLabel = QLabel('Scanned Names:')
        self.veritcalLayout.addWidget(self.scannedNamesLabel)
        self.scannedNamesList = QListWidget()
        self.scannedNamesList.insertItem(0, captured_data[0])
        self.scannedNamesList.clicked.connect(self.select_name)
        self.veritcalLayout.addWidget(self.scannedNamesList)

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
        self.showDefault.clicked.connect(self.set_to_default)
        self.veritcalLayout.addWidget(self.showDefault)

    def add_name(self, name):
        if captured_data[-1] != name:
            captured_data.append(name)
            self.updateNameList()

    def loadConfig(self):
        if path.exists(self.config_json):
            with open(self.config_json, 'r') as j:
                for key, value in json.load(j).items():
                    self.config[key] = value

    def exportConfig(self):
        with open(self.config_json, 'w') as j:
            json.dump(self.config, j)

    def viewFrame(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def stopCamera(self):
        try:
            self.worker.stop()
        except AttributeError: # if the camera isn't open, ignore the error it throws
            pass

    def select_camera(self, index):
        self.stopCamera()
        self.config['webcam_index'] = index
        self.worker = self.ImageWorker(**self.config)
        self.worker.start()
        self.worker.ImageUpdate.connect(self.viewFrame)

    def select_name(self):
        item = self.name_list.currentIndex()
        self.display_name(item.text())

    def updateNameList(self, item):
        new_index = len(captured_data) + 1
        self.name_list.insertItem(new_index, item)

    def previous_name(self):
        if self.name_index != 0:
            self.name_index -= 1
            self.display_name(captured_data[self.name_index])

    def next_name(self):
        if self.name_index + 2 <= len(captured_data):
            self.name_index += 1
            self.display_name(captured_data[self.name_index])

    def set_to_default(self):
        self.display_name(captured_data[0])

    def display_name(self, name):
        try:
            tricaster_data_link(ip=self.config['tricaster_ipaddr'], data=name)
        except Exception as e:
            self.error_window(message=f'ERROR: {e}', title='Connection Error')

    def error_window(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_name()
        elif event.key() == Qt.Key_Left:
            self.previous_name()
        elif event.key() == Qt.Key_Space:
            self.set_to_default()

    def closeEvent(self, event):
        self.exportConfig()

    class ImageWorker(QThread):
        ImageUpdate = pyqtSignal(QImage)
        def __init__(self, **kwargs):
            super().__init__()
            self.width, self.height = kwargs['vf_dimensions'][0], kwargs['vf_dimensions'][1]
            self.capture = cv2.VideoCapture(kwargs['webcam_index'])
            self.ThreadActive = True

            self.player = QMediaPlayer()

            self.qrscan = cv2.QRCodeDetector()

        def confirm_audio(self):
            url = QUrl.fromLocalFile(path.join(path.dirname(path.realpath(__file__)), 'assets', 'cork.mp3'))
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
                        if captured_data[-1] != data:
                            captured_data.append(data)
                            self.confirm_audio()

        def stop(self):
            self.ThreadActive = False
            self.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveLTMainGui()
    window.show()
    sys.exit(app.exec_())
