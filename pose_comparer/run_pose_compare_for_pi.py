import pickle
import socket
import struct
import logging
import time
import cv2
import os
import threading
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path


# 配置日志
logger = logging.getLogger('TfPoseEstimator-PoseCompareForPi')                         # 设置日志名
logger.setLevel(logging.DEBUG)                                                         # 设置输出级别为DEBUG
ch = logging.StreamHandler()                                                           # 设置处理器
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')  # 设置输出格式（年月日时分秒毫秒，日志名，日志级别，消息
ch.setFormatter(formatter)
logger.addHandler(ch)

# 为计算fps的辅助全局变量
fps_time = 0

CHANGE_TIME = 10.0

HOST = ''
PORT = 8001

payload_size = struct.calcsize("L")
bufSize = 65535

# 采用udp协议传输
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
logger.debug("server bind complete")

# 打开模板图片
path = './templates'
file_names = os.listdir(path)
template_imgs = []

descriptions = []
for filename in file_names:
    template_imgs.append(cv2.imread(path + '/' + filename))

# 获取姿势文本描述
txt_names = os.listdir('./txts')
for txt_name in txt_names:
    descriptions.append(open('./txts/' + txt_name, 'r', encoding='utf-8').read())

index = 0

e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(432, 368))
logger.debug('initialization %s from: %s' % ('mobilenet_thin', get_graph_path('mobilenet_thin')))


humans_template = e.inference(template_imgs[index], resize_to_default=False, upsample_size=4.0)


def add_chinese_to_cv2_img(txt, image, positon=(0, 0)):
    font = ImageFont.truetype("C:\\WINDOWS\\Fonts\\SIMYOU.TTF", 30)
    cv2_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # cv2和PIL中颜色的hex码的储存顺序不同
    pil_img = Image.fromarray(cv2_img)
    draw = ImageDraw.Draw(pil_img)
    draw.ink = 0 + 255*256 + 0*255*256
    draw.text(positon, txt, font=font)
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv2_img


def change_template_img():
    global template_imgs
    global humans_template
    global index
    global descriptions
    if index == len(template_imgs):
        index = 0
    humans_template = e.inference(template_imgs[index], resize_to_default=False, upsample_size=4.0)
    cv2.imshow('template_img', add_chinese_to_cv2_img(descriptions[index], template_imgs[index]))
    if cv2.waitKey(1) == 27:
        pass
    index += 1
    logger.debug("template changed+")
    t = threading.Timer(CHANGE_TIME, change_template_img)
    t.start()


# 指定时间内切换一次template照片
change_template_img()

if __name__ == '__main__':
    while True:
        # 先接收长度信息
        data, addr = s.recvfrom(bufSize)
        # 如果接收到的消息不是携带长度信息的包，就继续判断下一个包
        if len(data) != payload_size:
            continue
        # 图像编码的长度值
        length = struct.unpack("L", data)[0]
        # 接收图像编码包
        data, addr = s.recvfrom(bufSize)
        if length != len(data):
            continue

        frame_codes = pickle.loads(data)
        image = cv2.imdecode(frame_codes, 1)

        logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))
        # Display
        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=False, upsample_size=4.0)
        logger.debug('postprocess+')
        # 画线
        image = TfPoseEstimator.draw_compared_human(image, humans, humans_template)
        # image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        logger.debug('show+')
        # 给图像添加FPS数据
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        fps_time = time.time()
        cv2.imshow('tf-pose-estimation result', image)
        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()
    s.close()
