import sys
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

# ******COMMAND LIST*******************
ENABLE_MOTOR = b'\x00'
MOVE_UP = b'\x01'
MOVE_DOWN = b'\x02'
DISABLE_MOTOR = b'\x03'

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.motor_controller = serial.Serial('/dev/ttyUSB0', 115200)
        self.title = 'Structo IPA test GUI'
        self.left = 10
        self.top = 10
        self.width = 200
        self.height = 200
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Motor controller ready.')
        button = QPushButton('Start', self)
        button.setToolTip('Press to move up')
        button.move(50,70) 
        button2 = QPushButton('Stop', self)
        button2.setToolTip('Press to move down')
        button2.move(50,100) 
        
        # button.clicked.connect(self.on_click)
        # button.pressed.connect(self.on_pressed_up)
        # button.released.connect(self.on_released)

        # button2.clicked.connect(self.on_click)
        # button2.pressed.connect(self.on_pressed_down)
        # button2.released.connect(self.on_released)

        self.show()

    @pyqtSlot()
    def on_pressed_up(self):
        # print('Button pressed')
        self.motor_controller.write(MOVE_UP)

    @pyqtSlot()
    def on_pressed_down(self):
        # print('Button pressed')
        self.motor_controller.write(MOVE_DOWN)

    @pyqtSlot()
    def on_released(self):
        # print('Button released')
        self.motor_controller.write(DISABLE_MOTOR)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())