# 结构示意，可以把网上已有的模块封装一下
import threading


# yolo框架的
class yolo:
    def __init__(self):
        # 额外设置一个队列，放推理的结果,
        self.reslut = []
        self.lock = threading.Lock()  # 锁

    def predict(self, image):
        # 需要异常检测的结果存入队列
        with self.lock:
            self.reslut.append("reslut")


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
        self.reslut = []
        self.lock = threading.Lock()  # 锁

    def predict(self, image):
        # 结果存入队列
        with self.lock:
            self.reslut.append("reslut")


    def getResult(self):
        with self.lock:
            if self.reslut:
                return self.reslut.pop(0)
            else:
                return None



# 数据获取类
# 参考LoadStreams
class DataSet:
    def __init__(self):
        # 完成初始化相机等等，将畸变数据存为类的属性
        # 设置一个队列，数据放进去
        pass

    # 获取当前的畸变数据（类的属性）
    def getCalibrator(self, image):
        pass

    # 队列中获取数据
    def getData(self):
        pass

    # 开始摄像头读入
    def start(self):
        pass

    # 关闭/暂停摄像头读入 
    def stop(self):
        pass

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