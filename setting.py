from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtWidgets
import sys


class setting:
    def __init__(self):
        # 从文件中加载UI定义
        ui_path = "setting.ui"
        self.ui = uic.loadUi(ui_path)
        # 设置窗口标题
        self.ui.setWindowTitle("设置")
        # 初始化窗口里UI控件信号
        self.ui.selectDir.clicked.connect(self.selectDir)
        self.url = ""

    def selectDir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "C:/")  # 起始路径
        if directory:
            self.url = directory
            self.ui.dir.setText(directory)
