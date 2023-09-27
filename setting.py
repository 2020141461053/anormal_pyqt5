from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import sys


class setting:
    def __init__(self):
        print("CusMainWindow--> __init__()")
        # 从文件中加载UI定义
        ui_path = "setting.ui"
        self.ui = uic.loadUi(ui_path)
        # 设置窗口标题
        self.ui.setWindowTitle("设置")
        # 初始化窗口里UI控件信号





