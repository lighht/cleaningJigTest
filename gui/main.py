import sys
from time import time, sleep
from serial import Serial
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QApplication, QLabel, QLineEdit)
from PyQt5.QtCore import (QObject, QThread, QRegExp, pyqtSlot, pyqtSignal)
from PyQt5.QtGui import (QRegExpValidator)



#### DEFAULT VALUES ######
DEFAULT_ACCELERATION = 5
DEFAULT_WASH_DISTANCE = 20
DEFAULT_DURATION = 5
DEFAULT_SUBMERGE = 40


#### COMMUNICATION SETUP ############
interrupt_flag = False

ENABLE_MOTOR = b'\x00'
DISABLE_MOTOR = b'\x01'
SUBMERGE = b'\x02'
RAISE = b'\x03'
AGITATE = b'\x04'
DATA_WRITE = b'\x05'

class Agitator(QObject):
    finished_signal = pyqtSignal()
    motor_controller = Serial('/dev/ttyUSB0', 115200)

    def setup_values(self, submerge, distance, acceleration, duration):
        # Values entered in GUI are in mm, while the firmware understands in 10s of microns
        self.submerge = submerge * 100
        self.distance = distance * 100
        self.acceleration = acceleration * 100 
        self.duration = duration * 60 #Values in GUI are in minutes. Convert to seconds
        self.distance_byte_data = self.distance.to_bytes(2, byteorder='little')
        self.acceleration_byte_data = self.acceleration.to_bytes(2, byteorder='little')
        self.submerge_byte_data = self.submerge.to_bytes(2, byteorder='little')
        print([self.distance_byte_data,self.acceleration_byte_data])

    @pyqtSlot()
    def run(self):
        global interrupt_flag
        self.motor_controller.write(DATA_WRITE)
        self.motor_controller.write(self.distance_byte_data)
        self.motor_controller.write(self.acceleration_byte_data)
        self.motor_controller.write(self.submerge_byte_data)
        self.motor_controller.read(size=1)

        self.motor_controller.write(SUBMERGE)
        self.motor_controller.read(size = 1)

        starting_time = time()
        diff = 0
        while (not interrupt_flag) and diff < self.duration:
            diff = (time()-starting_time)
            self.motor_controller.write(AGITATE)
            self.motor_controller.read(size=1)
        
        self.motor_controller.write(RAISE)
        self.motor_controller.read(size = 1)

        self.finished_signal.emit()


class MainAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.agitator = Agitator()
        self.agitatorThread = QThread(self)
        self.agitator.finished_signal.connect(self.motionFinishedHandle)
        self.agitator.moveToThread(self.agitatorThread)
        self.agitatorThread.started.connect(self.agitator.run)

        self.initUI()

    def initUI(self):
        acc_data_hbox = QHBoxLayout()
        acc_data_hbox.addStretch(1)
        accelerationLabel = QLabel("acc")
        accelerationUnitLabel = QLabel("mm/s2")
        reg_ex = QRegExp("[0-9]{1,2}")
        self.accelerationTextBox = QLineEdit()
        self.accelerationTextBox.setObjectName("acc")
        # Gets input in mm/s/s. Converted to DU per second
        self.accelerationTextBox.setText(str(DEFAULT_ACCELERATION))
        input_validator_acc = QRegExpValidator(
            reg_ex, self.accelerationTextBox)
        self.accelerationTextBox.setValidator(input_validator_acc)
        acc_data_hbox.addWidget(accelerationLabel)
        acc_data_hbox.addWidget(self.accelerationTextBox)
        acc_data_hbox.addWidget(accelerationUnitLabel)
        acc_data_hbox.addStretch(1)

        distDataHBox = QHBoxLayout()
        distDataHBox.addStretch(1)
        distanceLabel = QLabel("dist")
        distance_unit_label = QLabel("mm     ")
        reg_ex = QRegExp("[0-9]{1,3}")
        self.distanceTextBox = QLineEdit()
        self.distanceTextBox.setObjectName("dist")
        self.distanceTextBox.setText(str(DEFAULT_WASH_DISTANCE))  # Gets input in mm. Converted to DU
        input_validator_acc = QRegExpValidator(reg_ex, self.distanceTextBox)
        self.distanceTextBox.setValidator(input_validator_acc)
        distDataHBox.addWidget(distanceLabel)
        distDataHBox.addWidget(self.distanceTextBox)
        distDataHBox.addWidget(distance_unit_label)
        distDataHBox.addStretch(1)

        timeDataHBox = QHBoxLayout()
        timeDataHBox.addStretch(1)
        timeLabel = QLabel("time")
        time_unit_label = QLabel("min   ")
        reg_ex = QRegExp("[0-9]{1,3}")
        self.timeTextBox = QLineEdit()
        self.timeTextBox.setObjectName("time")
        # Gets input in minutes. Converted to seconds
        self.timeTextBox.setText(str(DEFAULT_DURATION))
        input_validator_acc = QRegExpValidator(reg_ex, self.timeTextBox)
        self.timeTextBox.setValidator(input_validator_acc)
        timeDataHBox.addWidget(timeLabel)
        timeDataHBox.addWidget(self.timeTextBox)
        timeDataHBox.addWidget(time_unit_label)
        timeDataHBox.addStretch(1)

        submerge_data_hbox = QHBoxLayout()
        submerge_data_hbox.addStretch(1)
        submerge_label = QLabel("sub")
        submerge_unit_label = QLabel("mm     ")
        reg_ex = QRegExp("[0-9]{1,3}")
        self.submerge_text_box = QLineEdit()
        self.submerge_text_box.setObjectName("submerge")
        # Gets input in minutes. Converted to seconds
        self.submerge_text_box.setText(str(DEFAULT_SUBMERGE))
        input_validator_acc = QRegExpValidator(reg_ex, self.submerge_text_box)
        self.submerge_text_box.setValidator(input_validator_acc)
        submerge_data_hbox.addWidget(submerge_label)
        submerge_data_hbox.addWidget(self.submerge_text_box)
        submerge_data_hbox.addWidget(submerge_unit_label)
        submerge_data_hbox.addStretch(1)

        buttonHBox = QHBoxLayout()
        buttonHBox.addStretch(1)
        self.startButton = QPushButton("Start", self)
        self.cancelButton = QPushButton("Stop", self)
        self.cancelButton.setEnabled(False)
        buttonHBox.addWidget(self.startButton)
        buttonHBox.addWidget(self.cancelButton)

        vbox = QVBoxLayout(self)
        vbox.addStretch(1)
        vbox.addLayout(acc_data_hbox)
        vbox.addLayout(distDataHBox)
        vbox.addLayout(timeDataHBox)
        vbox.addLayout(submerge_data_hbox)
        vbox.addStretch(1)
        vbox.addLayout(buttonHBox)

        self.setLayout(vbox)
        self.startButton.clicked.connect(self.onStartClicked)
        self.cancelButton.clicked.connect(self.onCancelClicked)
        self.setGeometry(500, 600, 300, 150)
        self.setWindowTitle('IPA Cleaning test')
        self.show()

    def motionFinishedHandle(self):
        global interrupt_flag
        self.agitatorThread.quit()
        interrupt_flag = False
        self.startButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

    @pyqtSlot()
    def onStartClicked(self):
        global interrupt_flag
        self.agitator.setup_values(int(self.submerge_text_box.text()), int(self.distanceTextBox.text()),
                                   int(self.accelerationTextBox.text()),
                                   int(self.timeTextBox.text()))
        self.startButton.setEnabled(False)
        # print(int(self.accelerationTextBox.text()))
        # print(self.distanceTextBox.text())
        print("interrupt-flag")
        print(interrupt_flag)
        self.agitatorThread.start()
        self.cancelButton.setEnabled(True)

    @pyqtSlot()
    def onCancelClicked(self):
        global interrupt_flag
        interrupt_flag = True
        self.cancelButton.setEnabled(False)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainAppWindow()
    sys.exit(app.exec_())
