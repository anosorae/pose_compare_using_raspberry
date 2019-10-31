import socket
import pickle
import struct
import cv2
import basicMovement as bmt


class Recoder:
    body_percents = {0: 0}
    body_percents_mark = 0
    body_percents_limit = 4

    def set_body_percent_limit(self, n):
        self.body_percents_limit = n

    def record(self, n):
        self.body_percents[self.body_percents_mark] = n
        self.body_percents_mark = (self.body_percents_mark + 1) % self.body_percents_limit

    def get_avg(self):
        return sum(self.body_percents.values()) / len(self.body_percents)


def cacu_distance(recorder, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.04,
        minNeighbors=5,
        minSize=(2, 2)
    )
    # 对于本次识别到的第一张脸
    body_percent = 0
    for (x, y, w, h) in faces:
        # 如果没在这个里边，就不能算作在里边
        if x < 160 or x > 480 or y > 240:
            break
        body_percent = (480 - y) / 8 / h
        if body_percent > 1.2:
            body_percent = 1.2
        print("识别到的身体占比为 ", body_percent)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]

        break
    if body_percent == 0:
        # 表示没有识别到一张人脸，此时有可能是距离太近，需要让小车后退
        return -1
    else:
        recorder.record(body_percent)

        if recorder.get_avg() > 0.9:
            # 经过多次计算，发现已经基本识别到了人的全身
            return 1
        elif body_percent > 0.9:
            # 如果本次识别的时候发现已经基本覆盖了全部的内容，此时先不要移动。
            return 0
        else:
            # 距离近，只识别到了人的部分身体
            return -1

# HOST = "172.16.159.18" # 测试用的本机IP
# HOST = "192.168.137.1"
HOST = "192.168.137.64"
PORT = 8001

encode_param = [cv2.IMWRITE_JPEG_QUALITY, 20]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST, PORT))
print("start to send frames...")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)


faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
a_recorder = Recoder()
a_recorder.set_body_percent_limit(3)
pi_car = bmt.Car()

psd = 0
# 程序状态字，如果是0 表示还在距离控制中，如果是1 ，表示准备开始姿势识别了

while True:
    ret, frame = cap.read()
    pi_car.t_stop(0.01)
    while not ret:
        ret, frame = cap.read()

    if psd == 0:
        res_of_cacu_dist = cacu_distance(a_recorder, frame)

        if res_of_cacu_dist == 0:
            print("None")
            pi_car.t_stop(0.01)
        elif res_of_cacu_dist == 1:
            print("OK")
            pi_car.t_stop(0.01)
        else:
            print("Part")
            pi_car.t_down(10, 0.3)
            pi_car.t_stop(0.01)
    else:
        # 发送数据给客户端
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)  # 编码
        data = pickle.dumps(imgencode)
        message_size = struct.pack("L", len(data))
        s.sendall(message_size)
        s.sendall(data)
        print("send one frame")


s.close()
bmt.GPIO.cleanup()


