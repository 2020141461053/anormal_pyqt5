# 结构示意，可以把网上已有的模块封装一下
import os
import queue
import random
import threading
import time

import cv2


# yolo框架的
class yolo:
    def __init__(self):
        # 额外设置一个队列，放推理的结果,
        self.reslut = []
        self.lock = threading.Lock()  # 锁

    def predict(self, image):
        # 需要异常检测的结果存入队列
        with self.lock:
            self.reslut.append(image)

    def getResult(self):
        with self.lock:
            if self.reslut:
                return self.reslut.pop(0)
            else:
                return None


# 异常检测
class detect:
    def __init__(self):
        # 额外设置一个队列，放推理的结果,
        self.result = []
        self.lock = threading.Lock()  # 锁

    def predict(self, image):
        # 结果存入队列
        with self.lock:
            self.result.append(random.choice([True, False]))

    def getResult(self):
        with self.lock:
            if self.result:
                return self.result.pop(0)
            else:
                return None


# 数据获取类
# 参考LoadStreams
class DataSet:
    def __init__(self):
        # 完成初始化相机等等，将畸变数据存为类的属性
        # 设置一个队列，数据放进去
        self.is_running = threading.Event()
        self.is_running.set()
        self.queue = queue.Queue()
        self.getDataThread = threading.Thread(target=self.update)
        self.getDataThread.setDaemon(True)


    # 获取当前的畸变数据（类的属性）
    def getCalibrator(self, image):
        pass

    # 队列中获取数据
    def getData(self):
        if not self.queue.empty():
            return self.queue.get()
        else:
            return None

    # Start reading data
    def startGetData(self):
        self.is_running.set()
        self.getDataThread.start()

    # Pause reading data
    def pause(self):
        self.is_running.clear()

    def recover(self):
        self.is_running.set()

    # 关闭读入
    # Stop reading data
    def stop(self):
        self.is_running.clear()
        self.getDataThread.join()
        with self.queue.mutex:
            self.queue.queue.clear()

    # 读取图片的线程函数
    # Thread function to read images
    def update(self):
        while True:
            self.is_running.wait()
            # Read data or perform any other necessary operations
            image_data = self.read_image()  # Replace this with your logic to read images

            # Add the data to the queue
            self.queue.put(image_data)

            time.sleep(0.05)  # Wait for 0.1 second

    def read_image(self):
        folder_path = 'test_img'  # Specify the folder path here

        # Get a list of image files in the folder
        image_files = [file_name for file_name in os.listdir(folder_path) if
                       file_name.endswith('.jpg') or file_name.endswith('.png')]

        if image_files:
            # Randomly select an image file
            random_image_file = random.choice(image_files)

            # Read the image data or perform any necessary operations
            image_data = self.read_image_data(os.path.join(folder_path, random_image_file))

            return image_data

        return None

    def read_image_data(self, file_path):
        # Replace this with your logic to read image data
        # Return the image data
        image_data = cv2.imread(file_path)
        return image_data

    # 重新获取畸变数据
    def setCalibrator(self):
        pass


'''
# 初始化数据获取
DataSet = DataSet()
# 初始化yolo
yolo = yolo()
# 初始化异常检测    
detector = detect()

'''

'''
# 定义线程函数
def yolo_thread_func():
    while True:
        frame = DataSet.getData()
        if frame is None:
            continue
        yolo.predict(frame)


def detector_thread_func():
    while True:
        frame = yolo.getResult()
        if frame is None:
            continue
        detector.predict(frame)
'''
'''
# 创建线程对象
yolo_thread = threading.Thread(target=yolo_thread_func)
detector_thread = threading.Thread(target=detector_thread_func)
# 摄像头工作
DataSet.start()
# 启动线程
yolo_thread.start()
detector_thread.start()

# 主线程处理业务

while True:
    detector_result = detector.getResult()
    if detector_result is not None:
        # 处理异常检测结果
        # 重命名+存入数据库等等
        pass


# 命名规则
def reName(img, normal):
    pass
'''
