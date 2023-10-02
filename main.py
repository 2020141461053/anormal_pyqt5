import datetime
import os
from threading import Thread, Event
from time import sleep

import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage
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
label（图片）:
    input
    output

'''


def generate_file_name():
    # 生成文件名，这里使用当前时间戳作为文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # 去掉毫秒部分
    file_name = timestamp + ".jpg"

    return file_name


class MainWindow:
    def __init__(self):
        self.get_data = None
        self.detector = None
        self.DataSet = None
        self.yolo = None
        self.store_url = None
        self.yolo_thread = None
        self.detector_thread = None

        self.event_addImg = Event()

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
        self.ui.input.setScaledContents(True)
        self.ui.output.setScaledContents(True)
        # 窗口设置
        self.setting = setting()
        self.setting.ui.confirm.clicked.connect(self.confirmDir)
        # 是否暂停
        self.is_stop = False
        # 初始化
        self.reset()

    def confirmDir(self):
        with open("./config.yaml", 'w') as stream:
            data = {
                "url": self.setting.url
            }
            yaml.safe_dump(data, stream)
        self.setting.ui.close()



    # 重置按初始化
    def reset(self):
        # 创建线程对象
        self.get_config()
        # 业务逻辑
        self.DataSet = DataSet()
        # 初始化yolo
        self.yolo = yolo()
        # 初始化异常检测
        self.detector = detect()
        # 设置线程
        self.detector_thread = Thread(target=self.YoloAndDector_thread_func)
        self.detector_thread.setDaemon(True)
        # 开始按钮回复点击
        self.ui.start.setEnabled(True)

    # 开始检测按钮
    def start(self):
        self.event_addImg.set()
        # 摄像机模块默认自己开线程
        self.DataSet.startGetData()
        # 启动线程
        self.detector_thread.start()

        # 改灰
        self.ui.start.setEnabled(False)

    # 暂停
    def stop(self):
        if not self.is_stop:
            self.event_addImg.clear()
            # 摄像头暂停
            self.DataSet.pause()
            self.ui.stop.setText(_translate("MainWindow", "继续"))
        else:
            self.event_addImg.set()
            # 摄像头开始
            self.DataSet.recover()
            self.ui.stop.setText("暂停")

        self.is_stop = not self.is_stop

    # 更改储存路径
    def setting(self):
        self.setting.url = self.store_url
        self.setting.ui.dir.setText(self.store_url)
        self.setting.ui.show()


    def YoloAndDector_thread_func(self):
        same_one = False

        while True:
            self.event_addImg.wait()
            frame = self.DataSet.getData()
            if frame is None:
                sleep(0.5)
                same_one = False
                continue
            self.update_frame_input(frame)

            self.yolo.predict(frame)
            output_frame = self.yolo.getResult()
            self.detector.predict(output_frame)
            self.update_frame_output(output_frame)
            result=self.detector.getResult()
            self.saveResult(output_frame, same_one, result)
            self.ui.result.setText("正常" if result else "异常")
            same_one = True

    # 获取储存目录（用yaml储存）
    def get_config(self):
        with open("./config.yaml", 'r') as stream:
            config = yaml.safe_load(stream)
            self.store_url = config["url"]

    # 更新图片 （应该更新图片用主线程比较好？）
    def update_frame_input(self, img):
        # 加载当前帧的图片
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, channel = image_rgb.shape
        bytes_per_line = 3 * width
        pixmap = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 设置QLabel的图像
        self.ui.input.setPixmap(QPixmap.fromImage(pixmap))

        # 调整QLabel的大小，使其适应图片大小
        self.ui.input.resize(pixmap.width(), pixmap.height())

    def update_frame_output(self, img):
        # 加载当前帧的图片
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, channel = image_rgb.shape
        bytes_per_line = 3 * width
        pixmap = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # 设置QLabel的图像
        self.ui.output.setPixmap(QPixmap.fromImage(pixmap))

        # 调整QLabel的大小，使其适应图片大小
        self.ui.input.resize(pixmap.width(), pixmap.height())

    # 储存相关
    #TODO://可以考虑添加一个mysql储存路径？
    def saveResult(self, img, same_one, label):
        # 获取当前日期
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        # 构建日期文件夹路径
        date_folder = os.path.join(self.store_url, current_date)
        # 如果日期文件夹不存在，则创建
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        # 根据label确定存储子文件夹的名称
        if label:
            sub_folder = "normal"
        else:
            sub_folder = "anormal"

        # 如果same_one为True，获取最新的子文件夹路径，否则创建一个新的编号子文件夹路径
        if same_one:
            sub_folder_path = self.get_latest_subfolder(date_folder, sub_folder)
        else:
            sub_folder_path = self.create_new_subfolder(date_folder, sub_folder)

        # 生成文件名
        file_name = generate_file_name()
        # 构建完整的保存路径
        if sub_folder_path is None:
            print(f"datatime:{date_folder},sbu:{sub_folder},same:{same_one},")
            return

        save_path = os.path.join(sub_folder_path, file_name)

        # 保存图像
        cv2.imwrite(save_path, img)

    def get_latest_subfolder(self, parent_folder, sub_folder):
        # 获取指定父文件夹下指定子文件夹的最新路径
        sub_folder_list = [
            int(folder[len(sub_folder):]) for folder in os.listdir(parent_folder)
            if os.path.isdir(os.path.join(parent_folder, folder)) and folder.startswith(sub_folder)
        ]

        if sub_folder_list:
            sub_folder_list.sort(reverse=True)
            sub_folder_path = os.path.join(parent_folder, sub_folder + str(sub_folder_list[0]))
        else:
            sub_folder_path = os.path.join(parent_folder, sub_folder + str(0))
        return sub_folder_path

    def create_new_subfolder(self, parent_folder, sub_folder):
        # 创建一个新的编号子文件夹路径
        sub_folder_path = None
        sub_folder_list = [
            int(folder[len(sub_folder):]) for folder in os.listdir(parent_folder)
            if os.path.isdir(os.path.join(parent_folder, folder)) and folder.startswith(sub_folder)
        ]
        if sub_folder_list:
            sub_folder_list.sort(reverse=True)
            latest_sub_folder_number = sub_folder_list[0]
            sub_folder_number = latest_sub_folder_number + 1
            sub_folder_name = sub_folder + str(sub_folder_number)
        else:
            sub_folder_name = sub_folder + "0"

        sub_folder_path = os.path.join(parent_folder, sub_folder_name)
        if not os.path.exists(sub_folder_path):
            os.makedirs(sub_folder_path)

        return sub_folder_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cusMainWin = MainWindow()
    cusMainWin.ui.show()
    app.exec_()
