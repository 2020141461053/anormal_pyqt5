import threading

import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import sys
import yaml
from PyQt5.uic.properties import QtGui

from setting import setting
from module import DataSet, yolo, detect


_translate = QtCore.QCoreApplication.translate
'''
全部ui:
button:
    reset
    start
    stop
    setting

label:
    label_output
    label_input
frame:
    inputImg
    outputImg

'''


class MainWindow:
    def __init__(self):
        self.detector = None
        self.DataSet = None
        self.yolo = None
        self.store_url = None
        self.yolo_thread = None
        self.detector_thread = None

        # 从文件中加载UI定义
        ui_path = "MainWindow.ui"
        self.ui = uic.loadUi(ui_path)
        # 设置窗口标题
        self.ui.setWindowTitle("异常检测")

        # 初始化窗口里UI控件信号
        self.ui.reset.clicked.connect(self.reset)
        self.ui.start.clicked.connect(self.start)
        self.ui.stop.clicked.connect(self.stop)
        self.ui.setting.clicked.connect(self.setting)

        # 窗口设置
        self.setting = setting()

        

        # 初始化
        self.reset()



    # 重置按初始化
    def reset(self):
        # 创建线程对象
        self.get_config()
        #设置线程
        self.yolo_thread = threading.Thread(target=self.yolo_thread_func)
        self.detector_thread = threading.Thread(target=self.detector_thread_func)
        # 业务逻辑
        self.DataSet = DataSet()
        # 初始化yolo
        self.yolo = yolo()
        # 初始化异常检测
        self.detector = detect()
        print("MainWindow--> reset()")

    # 开始检测按钮
    def start(self):
        self.DataSet.start()
        # 启动线程
        #self.yolo_thread.start()
        #self.detector_thread.start()
        print("MainWindow--> start()")

    # 暂停
    def stop(self):
        # 摄像头工作
        self.DataSet.stop()
        print("MainWindow--> stop()")

    # 更改储存路径
    def setting(self):
        self.setting.ui.show()
        print("MainWindow--> setting()")

    """
    这个需要改，改成响应式的好一些，摄像头获取数据驱动事件更新图片
    """
    def yolo_thread_func(self):
        while True:
            frame = self.DataSet.getData()
            self.update_frame_input(frame)
            if frame is None:
                continue
            self.yolo.predict(frame)

    def detector_thread_func(self):
        while True:
            frame = self.yolo.getResult()
            if frame is None:
                #self.ui.output.setText(_translate("MainWindow", "未检测到"))
                continue
            self.update_frame_output(frame)
            self.ui.result.setText(_translate("MainWindow", self.detector.predict(frame)))


    # 获取储存目录（用yaml储存）
    def get_config(self):
        with open("./config.yaml", 'r') as stream:
            config = yaml.safe_load(stream)
            self.store_url = config["url"]

    def update_frame_input(self,img):
        # 加载当前帧的图片
        pixmap = QPixmap(img)

        # 设置QLabel的图像
        self.ui.input.setPixmap(pixmap)

        # 调整QLabel的大小，使其适应图片大小
        self.ui.input.resize(pixmap.width(), pixmap.height())

    def update_frame_output(self,img):
        # 加载当前帧的图片
        pixmap = QPixmap(img)

        # 设置QLabel的图像
        self.ui.output.setPixmap(pixmap)

        # 调整QLabel的大小，使其适应图片大小
        self.ui.output.resize(pixmap.width(), pixmap.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cusMainWin = MainWindow()
    cusMainWin.ui.show()
    app.exec_()
