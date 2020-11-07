from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QLineEdit
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np


import numpy as np
from PIL import ImageGrab
import win32gui
import cv2
import time

def nearest_ind(items, pivot):
    time_diff = np.abs([date - pivot for date in items])
    return time_diff.argmin(0)


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

        windows_list = []
        toplist = []
        def enum_win(hwnd, result):
            win_text = win32gui.GetWindowText(hwnd)
            windows_list.append((hwnd, win_text))
        win32gui.EnumWindows(enum_win, toplist)


        # Game handle
        game_hwnd = 0
        for (hwnd, win_text) in windows_list:
            if "Camera" in win_text:
                game_hwnd = hwnd

        self.position = win32gui.GetWindowRect(game_hwnd)

        self.DELAY_SECONDS = 2

        self.frames = []
        self.times = []


    def run(self):
        # capture from web cam
        # cap = cv2.VideoCapture(0)
        while self._run_flag:

            screenshot = ImageGrab.grab(self.position)
            screenshot = np.array(screenshot)
            # print(screenshot.shape)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

            screenshot_time = time.time()

            self.frames.append(screenshot)
            self.times.append(screenshot_time)

            target_time = screenshot_time - self.DELAY_SECONDS

            target_time_idx = nearest_ind(self.times, target_time )

            # print(target_time_idx)

            display_screnshot = self.frames[target_time_idx]

            self.frames = self.frames[target_time_idx:]
            self.times = self.times[target_time_idx:]


            self.change_pixmap_signal.emit(display_screnshot)

            # ret, cv_img = cap.read()
            # if ret:
            #     self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cv2.destroyAllWindows()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        
        self.wait()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()


        self.time_display = QLineEdit()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(5000)
        self.slider.setValue(1000)
        self.delaychanged()
        self.slider.sliderReleased.connect(self.delaychanged)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.slider)
        hbox.addWidget(self.time_display)

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        vbox.addLayout(hbox)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)



    def delaychanged(self):
        self.time_display.setText(str(self.slider.value()))
        self.thread.DELAY_SECONDS = self.slider.value()/1000


    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())