import sys
import cv2
import pyvirtualcam
import multiprocessing as mp
import socket
import Facial_Expression as fe


class Live(object):
    # 初始化模板与视频（摄像头）参数
    def __init__(self, file, target):
        # 定义opencv所需的模板
        #self.template = template
        # 读取模板并获取模板的高度和宽度
        #self.template = cv2.imread(self.template, 1)
        # 视频路径，0时调用摄像头
        self.file = file

        # 视频对象，0时调用摄像头
        cap = cv2.VideoCapture(self.file)

        cap.set(3, 1920)
        cap.set(4, 1080)

        # 视频高度
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 视频宽度
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # 视频尺寸
        self.size = f'{self.width}x{self.height}'
        # 视频帧率
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        del cap

        self.target = target  # 截图尺寸
        self.targetSize = f'{self.target[2]}x{self.target[3]}'

        #self.model = model
        #self.client = client

    
    # 此线程用于视频捕获处理
    def image_put(self, queue, filepath):
        while 1:
            cap = cv2.VideoCapture(filepath)
            if filepath == 0:  # 摄像头时设置分辨率
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            print(f'Source Video Parameters: size: {self.size} fps: {self.fps}.')

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    if filepath == 0:
                        print("Opening camera is failed!!!")
                    else:
                        print("Video is over.")

                    # queue.put('stop')
                    break
                queue.put(frame[self.target[1]:self.target[1] + self.target[3],
                          self.target[0]:self.target[0] + self.target[2]])

    # 此线程用于推流
    def image_get(self, queue):
        cam = pyvirtualcam.Camera(width=self.target[2], height=self.target[3], fps=self.fps)
        #cam = pyvirtualcam.Camera(width=1920, height=1080, fps=self.fps)
        print(f'Virtual Camera: {cam.device}.')
        print(f'Virtual Camera Parameters: size: {self.targetSize} fps: {self.fps}.')
        while True:
            frame = queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR TO RGB
            frame = cv2.flip(frame, 1)  # 水平翻转
            cam.send(frame)

            cam.sleep_until_next_frame()
    
    # 此线程用于实时分析表情
    def inference(self,queue, queue_message):
        model = fe.Model()
        while True:
            frame = queue.get()
            # if type(frame) == type('stop'):
            #     queue_message.put('stop')
            #     break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR TO RGB
            #image = cv2.flip(frame, 1)  # 水平翻转
            #label = self.model.fe.fer(image)
            label, face = model.fer(image)

            if label != -1:
                queue_message.put(label)  # 放一张模板
                #queue_message.put('stop')
                #print(f'emotion label: {label}')

        
    #此线程用于传送消息
    def send_message(self,queue_message):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 55555
        sock.bind((host,port))
        sock.listen(1)
        client, addr = sock.accept()  # 接受客户端连接请求
        print(client, "------", addr)  # 输出客户端信息
        data = client.recv(1024)  # 接收客户端发送的数据
        print(data.decode())  # 输出接收到的数据

        while True:
            if not queue_message.empty():
                sys.stdout.flush()

                message = queue_message.get()
                # if type(message) == type('stop'):
                #     break

                print(f'emotion label: {message}')
                client.sendall(str(message).encode("utf-8"))
            

    # 多线程执行一个摄像头
    def run_single_camera(self):
        queue = mp.Queue(maxsize=2)  # 队列
        queue4inf = mp.Queue(maxsize=2)  # 队列
        queue_message = mp.Queue(maxsize=2)  #消息队列
        processes = [mp.Process(target=self.image_put, args=(queue, self.file,)),
                     mp.Process(target=self.image_get, args=(queue,)),
                     mp.Process(target=self.inference, args=(queue, queue_message)),
                     mp.Process(target=self.send_message, args=(queue_message,)),]
        [process.start() for process in processes]
        [process.join() for process in processes]



if __name__ == '__main__':

    mp.freeze_support()
    file_path = 0  # 摄像头
    real_camera_size = (1920, 1080)  #(640, 480)
    target_size = (1920, 1080)
    #real_camera_size = (640, 480)
    #target_size = (380, 300)
    
    target = ((real_camera_size[0] - target_size[0]) // 2, (real_camera_size[1] - target_size[1]) // 2, target_size[0],
                target_size[1])

    live = Live(file=file_path, target=target)
    live.run_single_camera()

