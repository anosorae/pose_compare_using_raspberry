from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np


def draw_chinese(txt, image, positon=(0, 0)):
    font = ImageFont.truetype("C:\\WINDOWS\\Fonts\\SIMYOU.TTF", 30)
    cv2_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # cv2和PIL中颜色的hex码的储存顺序不同
    pil_img = Image.fromarray(cv2_img)
    draw = ImageDraw.Draw(pil_img)
    # draw.ink = 0 + 255*256 + 0*255*256
    draw.text(positon, txt, font=font)
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv2_img


txt = """
大腿前侧拉伸 L的动作要领
1、挺胸收腹，保持平衡
2、左脚后跟尽量贴近臀部，膝盖垂直向下
3、感受股四头肌（大腿前侧）有一定的拉伸感
"""

img = cv2.imread("../templates/1.png")
cv2.imshow("test", draw_chinese(txt, img))
cv2.waitKey(0)
