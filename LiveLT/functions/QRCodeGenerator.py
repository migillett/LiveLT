#!/usr/bin/python3

# Written by Michael Gillett, 2022

from csv import DictReader
import sys
import qrcode
from os import path, mkdir

from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 


class CSVtoQR(QMainWindow):
    def __init__(self) -> None:
        super(CSVtoQR, self).__init__()

        self.current_dir = path.dirname(path.realpath(__file__))
        self.csv_path = None

        self.total_rows = 1
        self.index = 1

        self.name_data = []

        self.export_dir = path.join(path.dirname(path.realpath(__file__)), 'qr_exports')

        self.initGUI()

    def initGUI(self):
        self.setWindowTitle('LiveLT QR Generator')

        # setup central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # create the vertical box layout
        self.veritcalLayout = QVBoxLayout(self.centralWidget)
        self.veritcalLayout.addStretch()

        # load csv label
        self.csv_label = QLabel(f'Please load CSV file')
        # load csv button
        self.csv_load_button = QPushButton('Load CSV File')
        self.csv_load_button.clicked.connect(self.csv_dialog_box)
        # add to layout
        self.veritcalLayout.addWidget(self.csv_label)
        self.veritcalLayout.addWidget(self.csv_load_button)

        # select export dir
        self.export_label = QLabel(f'Export Directory:\n{self.export_dir}')
        self.export_dir_button = QPushButton('Change Export Directory')
        self.export_dir_button.clicked.connect(self.export_dir_dialog)
        self.veritcalLayout.addWidget(self.export_label)
        self.veritcalLayout.addWidget(self.export_dir_button)

        # progress bar
        self.pbar = QProgressBar(self)
        self.pbar.setMaximum(self.total_rows)
        self.veritcalLayout.addWidget(self.pbar)
        self.pbar.setVisible(False)

        # start button
        self.startButton = QPushButton('Start QR Creation')
        self.startButton.clicked.connect(self.start_qr_creation)
        # add sub-layout to root window
        self.veritcalLayout.addWidget(self.startButton)

    def csv_dialog_box(self):
        self.csv_path, filetype = QFileDialog.getOpenFileName(self, 'Open CSV File', self.current_dir, "CSV Files (*.csv *.CSV)")
        self.load_csv()
        self.csv_label.setText(f'Loaded CSV File:\n{self.csv_path}')

    def export_dir_dialog(self):
        self.export_dir = QFileDialog.getExistingDirectory(self, 'Choose Export Directory', self.current_dir)
        self.export_label.setText(f'Export Directory:\n{self.export_dir}')

    def message_box(self, title, message):
        msg = QMessageBox()
        # msg.setIcon(QMessageBox.information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def load_csv(self):
        if path.exists(self.csv_path) and self.csv_path.endswith('.csv'):
            with open(self.csv_path, mode='r', newline='', encoding='utf-8-sig') as f:
                self.name_data = list(DictReader(f))
                self.total_rows = sum(1 for row in self.name_data)
            self.pbar.setMaximum(self.total_rows)

    def start_qr_creation(self):
        self.pbar.setVisible(True)

        self.thread = QThread()
        config = {
            'name_data': self.name_data,
            'export_dir': self.export_dir
        }
        self.worker = QRExport(**config)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.PbarProcess.connect(self.pbar.setValue)
        
        self.thread.start()

        self.thread.finished.connect(lambda: self.done_exporting())
    
    def done_exporting(self):
        self.message_box(title='Export Complete', message=f'Successfully exported QR Codes. You may now close the window.')
        self.pbar.setVisible(False)
        self.index=1


class QRExport(QThread):
    PbarProcess = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, **args):
        super().__init__()
        self.name_data = args['name_data']
        self.export_dir = args['export_dir']
        self.index = 1

    def run(self):
        for row in self.name_data:
            formatted_name = row['Diploma Name']
            filename = "{:04d}_{}.png".format(self.index, formatted_name)

            img = qrcode.make(formatted_name)
            img.save(path.join(self.export_dir, filename))

            self.PbarProcess.emit(self.index)
            self.index += 1

        self.finished.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSVtoQR()
    window.show()
    sys.exit(app.exec_())