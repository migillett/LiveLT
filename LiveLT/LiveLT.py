#!/usr/bin/python3

# Written by Michael Gillett, 2022

# built-in
import sys
from os import path, mkdir
import json
from csv import DictReader
    
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
from functions.QRCodeGenerator import CSVtoQR


class LiveLTMainGui(QMainWindow):
    def __init__(self):
        super(LiveLTMainGui, self).__init__()

        self.player = QMediaPlayer()

        self.current_dir = path.dirname(path.realpath(__file__))
        self.config_json = path.join(self.current_dir, 'config.json')

        self.config = {
            'webcam_index': 0,
            'vf_dimensions': (480, 360),
            'default_slide': 'LiveLT',
            'tricaster_ipaddr': ''
        }

        self.load_config()

        # set keyboard focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        self.name_index = 0

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            exit()

        self.init_gui()

    def init_gui(self):
        # GUI title
        self.setWindowTitle('LiveLT')

        # create menubar for settings and such
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        # helpMenu = mainMenu.addMenu('Help')

        # file > create QR Codes
        createQRButton = QAction(' &Create QR Codes...', self)
        createQRButton.setStatusTip('Import a CSV file to create QR Codes')
        createQRButton.triggered.connect(self.QR_code_gui)
        fileMenu.addAction(createQRButton)

        # file > load names...
        loadNames = QAction(' &Load Names...', self)
        loadNames.setStatusTip('Load names from a CSV file')
        loadNames.triggered.connect(self.load_names)
        fileMenu.addAction(loadNames)

        # file > exit
        exitButton = QAction(' &Exit', self)
        exitButton.setStatusTip('Exit LiveLT')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

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

        # change default slide button
        self.change_default_name_button = QPushButton('Change Default Name')
        self.change_default_name_button.clicked.connect(self.set_default_name)
        self.veritcalLayout.addWidget(self.change_default_name_button)

        # Add custom name button
        self.add_custom_button = QPushButton('Add Custom Name')
        self.add_custom_button.clicked.connect(self.custom_name)
        self.veritcalLayout.addWidget(self.add_custom_button)

        # Label for scanned names
        self.scanned_names_label = QLabel('Scanned Names:')
        self.veritcalLayout.addWidget(self.scanned_names_label)
        # list of scanned names
        self.scanned_names_list = QListWidget()
        self.scanned_names_list.insertItem(0, self.config['default_slide'])
        self.scanned_names_list.itemClicked.connect(self.select_name)
        self.veritcalLayout.addWidget(self.scanned_names_list)

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
        self.showDefault.clicked.connect(self.display_name)
        self.veritcalLayout.addWidget(self.showDefault)

        # Status Bar for program updates (placeholder until used later)
        self.statusBar().showMessage('')

    # loads the config.json file on load. keeps settings the same between instances
    def load_config(self):
        if path.exists(self.config_json):
            with open(self.config_json, 'r') as j:
                for key, value in json.load(j).items():
                    self.config[key] = value

    # exporting running config to config.json
    def export_config(self):
        with open(self.config_json, 'w') as j:
            json.dump(self.config, j)

    # change the tricaster target IP address
    def change_ip(self):
        ip, okPressed = QInputDialog.getText(
            self, 'Target IP Address', 'IP Address: ',
            QLineEdit.Normal, self.config['tricaster_ipaddr'])
        if okPressed:
            # and save it to running config
            self.config['tricaster_ipaddr'] = ip
            self.tricaster_ip.setText(f'Tricaster IP: {self.config["tricaster_ipaddr"]}')

    # add a custom name to the scanned_names_list
    def custom_name(self):
        name, okPressed = QInputDialog.getText(
            self, 'Add Name', 'Name: ', QLineEdit.Normal, '')
        if okPressed:
            self.update_name_list(name)

    # change the default slide name (default is LiveLT, but can be organization name)
    def set_default_name(self):
        name, okPressed = QInputDialog.getText(
            self, 'Change Default Name', 'Default Name: ',
            QLineEdit.Normal, self.config['default_slide'])
        if okPressed:
            self.config['default_slide'] = name
            self.scanned_names_list.item(0).setText(self.config['default_slide'])

    # allows you to load a list of names from a CSV file
    def load_names(self):
        csv_path, filetype = QFileDialog.getOpenFileName(
            self, 'Open CSV File', self.current_dir, "CSV Files (*.csv *.CSV)")

        if csv_path.endswith('.csv'):
            with open(csv_path, mode='r', newline='', encoding='utf-8-sig') as f:
                name_data = list(DictReader(f))
        
            for name in name_data:
                new_name = f"{name['FirstName']} {name['LastName']}"
                self.update_name_list(new_name)

        else:
            self.error_window(title='Invalid Filetype', message='Invalid filetype. Please load a CSV file.')

    # launches GUI interface to convert a CSV file to QR codes
    def QR_code_gui(self):
        self.qr_gui = CSVtoQR()
        self.qr_gui.show()

    # show frame captured from webcam
    def view_frame(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    # close camera
    def stop_camera(self):
        try:
            self.worker.stop()
        except AttributeError: # if the camera isn't open, ignore the error it throws
            pass

    # start webcam capture after the user selects one from the dropdown
    def select_camera(self, index):
        self.stop_camera()
        self.config['webcam_index'] = index
        self.worker = ImageWorker(**self.config)
        self.worker.start()
        # connect the worker emited signals to GUI functions
        self.worker.ImageUpdate.connect(self.view_frame) # displays webcam frame on viewfinder
        self.worker.ListUpdate.connect(self.update_name_list) # adds scanned name to the scanned names list

    # when user clicks on an item in scanned_names_list
    def select_name(self, clicked_item):
        self.name_index = self.scanned_names_list.currentRow()
        self.display_name(self.name_index)

    # what runs when the webcam successfully scans a QR code
    def update_name_list(self, item):
        # get max last in list
        last_item = self.scanned_names_list.count() - 1 
        # check to make sure that the new item isn't the same as the last scanned (prevent duplicates)
        if item != self.scanned_names_list.item(last_item).text():
            # Add item to scanned_names_list
            self.scanned_names_list.insertItem(self.scanned_names_list.count(), item)
            # send auditory feedback of success
            self.confirm_audio()

    # go back one name in scanned_names_list
    def previous_name(self):
        # just make sure you already aren't at the first item in the list.
        if self.name_index != 0:
            self.name_index -= 1
            self.display_name(self.name_index)

    # display next name
    def next_name(self):
        # prevents indexerror if you're already at list maximum
        if self.name_index + 1 < self.scanned_names_list.count():
            self.name_index += 1
            self.display_name(self.name_index)

    # sends the default slide to the specified tricaster IP to make sure all is good
    def test_connection(self):
        self.display_name()
        self.statusBar().showMessage(f'Connection established with Tricaster')

    # The meat n'potatoes function. Sends the currently selected name to the tricaster.
    def display_name(self, index=0): # index 0 will return the default slide specified in config.json
        try:
            name = self.scanned_names_list.item(index).text()
            tricaster_response, displayed_data = tricaster_data_link(ip=self.config['tricaster_ipaddr'], gfx_text=name)
            if tricaster_response == 200:
                self.statusBar().showMessage(f'Tricaster Confirmed: {displayed_data}')
            else:
                self.error_window(title='Connection Error', message=f'ERROR: {tricaster_response}\n\nUnable to connect to Tricaster')

        except Exception as e:
            self.error_window(
                title='Connection Error',
                message=f'ERROR: {e}\n\nPlease check your Tricaster IP address in settings.')

    # for errors. duh.
    def error_window(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    # keyboard shortcuts.
    def keyPressEvent(self, event):
        # right arrow = next name
        if event.key() == Qt.Key_Right:
            self.next_name()
        # left arrow = previous name
        elif event.key() == Qt.Key_Left:
            self.previous_name()
        # space bar = display default name
        elif event.key() == Qt.Key_Space:
            self.display_name()

    # plays a little sound to confirm name added
    def confirm_audio(self):
        url = QUrl.fromLocalFile(path.join(path.dirname(path.realpath(__file__)), 'assets', 'cork.mp3'))
        content = QMediaContent(url)

        self.player.setMedia(content)
        self.player.setVolume(100)
        self.player.play()

    # quit the program
    def closeEvent(self, event):
        # exports json config before closing everything
        self.export_config()
        exit()


# treaded image ingest using OpenCV2
class ImageWorker(QThread):

    # Uses selected webcam to scan for QR codes, then emits them back to main GUI
    ImageUpdate = pyqtSignal(QImage)
    ListUpdate = pyqtSignal(object)

    def __init__(self, **kwargs):
        super().__init__()
        self.width, self.height = kwargs['vf_dimensions'][0], kwargs['vf_dimensions'][1]
        self.capture = cv2.VideoCapture(kwargs['webcam_index'])
        self.ThreadActive = True

        self.qrscan = cv2.QRCodeDetector()

    def run(self):
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(self.width, self.height, Qt.KeepAspectRatio)
                # send image back to main GUI for display on viewfinder
                self.ImageUpdate.emit(Pic)

                data, points, _ = self.qrscan.detectAndDecode(frame)
                # if QR code detected, emit name to main GUI
                if len(data) > 0:
                    self.ListUpdate.emit(data)

    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LiveLTMainGui()
    window.show()
    sys.exit(app.exec_())
