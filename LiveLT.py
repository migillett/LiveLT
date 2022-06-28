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
- bug test this business
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

        self.load_config()
        captured_data.append(self.config['default_slide'])

        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('LiveLT')

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
        self.veritcalLayout.addStretch()

        # Camera selection sub-layout
        self.camera_selection_widget = QWidget()
        self.camera_selection_layout = QHBoxLayout(self.camera_selection_widget)
        # camera selection label
        self.cameraLabel = QLabel('Select a Camera:')
        self.camera_selection_layout.addWidget(self.cameraLabel)
        # camera selection dropdown
        self.camera_selector_dd = QComboBox()
        self.camera_selector_dd.addItems([camera.description() for camera in self.available_cameras])
        self.camera_selector_dd.setCurrentIndex(self.config['webcam_index'])
        self.select_camera(index=self.config['webcam_index'])
        self.camera_selector_dd.currentIndexChanged.connect(self.select_camera)
        self.camera_selector_dd.setFixedWidth(400)
        self.camera_selection_layout.addWidget(self.camera_selector_dd)
        # Add sub-layout to root window
        self.veritcalLayout.addWidget(self.camera_selection_widget)

        # Tricaster Settings sub-layout
        self.tricaster_settings_widget = QWidget()
        self.tricaster_settings_layout = QHBoxLayout(self.tricaster_settings_widget)
        # Tricaster IP
        self.tricaster_ip = QLabel(f'Tricaster IP: {self.config["tricaster_ipaddr"]}')
        self.tricaster_settings_layout.addWidget(self.tricaster_ip)
        # Configure Tricaster IP
        self.configure_tc_ip = QPushButton('Change IP')
        self.configure_tc_ip.clicked.connect(self.change_ip)
        self.tricaster_settings_layout.addWidget(self.configure_tc_ip)
        # Test connection
        self.test_connection_button = QPushButton('Test Connection')
        self.test_connection_button.clicked.connect(self.test_connection)
        self.tricaster_settings_layout.addWidget(self.test_connection_button)
        # add sub-layout to root window
        self.veritcalLayout.addWidget(self.tricaster_settings_widget)

        # Video Feed
        self.FeedLabel = QLabel('Select a camera from the dropdown menu above')
        self.FeedLabel.setAlignment(Qt.AlignCenter)
        self.FeedLabel.setStyleSheet('Border: 1px solid black;')
        self.veritcalLayout.addWidget(self.FeedLabel)

        # Add custom name button
        self.add_custom_button = QPushButton('Add Custom Name')
        self.add_custom_button.clicked.connect(self.custom_name)
        self.veritcalLayout.addWidget(self.add_custom_button)

        # Label for scanned names
        self.scannedNamesLabel = QLabel('Scanned Names:')
        self.veritcalLayout.addWidget(self.scannedNamesLabel)
        # list of scanned names
        self.scannedNamesList = QListWidget()
        self.scannedNamesList.insertItem(0, captured_data[0])
        self.scannedNamesList.itemClicked.connect(self.select_name)
        self.veritcalLayout.addWidget(self.scannedNamesList)

        # Create sub-layout for next and previous buttons
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
        # add sub-layout to root window
        self.veritcalLayout.addWidget(self.nameButtonsWidget)

        # Display Default in emergencies
        self.showDefault = QPushButton('Display Default')
        self.showDefault.clicked.connect(self.set_to_default)
        self.veritcalLayout.addWidget(self.showDefault)

        # Status Bar for program updates (placeholder until used later)
        self.statusBar().showMessage('')

    def load_config(self):
        if path.exists(self.config_json):
            with open(self.config_json, 'r') as j:
                for key, value in json.load(j).items():
                    self.config[key] = value

    def export_config(self):
        with open(self.config_json, 'w') as j:
            json.dump(self.config, j)

    def change_ip(self):
        ip, okPressed = QInputDialog.getText(
            self, 'Target IP Address', 'IP Address: ',
            QLineEdit.Normal, self.config['tricaster_ipaddr'])
        if okPressed:
            self.config['tricaster_ipaddr'] = ip
            self.tricaster_ip.setText(f'Tricaster IP: {self.config["tricaster_ipaddr"]}')

    def custom_name(self):
        name, okPressed = QInputDialog.getText(
            self, 'Add Name', 'Name: ', QLineEdit.Normal, '')
        if okPressed:
            captured_data.append(name)
            self.update_name_list(name)

    def view_frame(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def stop_camera(self):
        try:
            self.worker.stop()
        except AttributeError: # if the camera isn't open, ignore the error it throws
            pass

    def select_camera(self, index):
        self.stop_camera()
        self.config['webcam_index'] = index
        self.worker = ImageWorker(**self.config)
        self.worker.start()
        self.worker.ImageUpdate.connect(self.view_frame)
        self.worker.ListUpdate.connect(self.update_name_list)

    def select_name(self, clicked_item):
        self.name_index = self.scannedNamesList.currentRow()
        self.display_name(clicked_item.text())

    def update_name_list(self, item):
        new_index = len(captured_data) + 1
        self.scannedNamesList.insertItem(new_index, item)

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

    def test_connection(self):
        self.display_name(captured_data[0])
        self.statusBar().showMessage(f'Connection established with Tricaster')

    def display_name(self, name):
        try:
            tricaster_response = tricaster_data_link(ip=self.config['tricaster_ipaddr'], data=name)
            if tricaster_response == 200:
                self.statusBar().showMessage(f'Tricaster Confirmed: {name}')
            else:
                self.error_window(message=f'ERROR: {tricaster_response}\n\nUnable to connect to Tricaster')

        except Exception as e:
            self.error_window(
                message=f'''ERROR: {e}
                
Please check your Tricaster IP address in settings.
Current IP is {self.config["tricaster_ipaddr"]}''',
                title='Connection Error')

    def error_window(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_name()
        elif event.key() == Qt.Key_Left:
            self.previous_name()
        elif event.key() == Qt.Key_Space:
            self.set_to_default()

    def closeEvent(self, event):
        self.export_config()


class ImageWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    ListUpdate = pyqtSignal(object)

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
                        self.ListUpdate.emit(data)
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
