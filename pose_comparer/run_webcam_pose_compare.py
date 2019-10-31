import argparse
import logging
import time

import cv2
# import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh


# 配置日志
logger = logging.getLogger('TfPoseEstimator-PoseCompare')  # 设置日志名
logger.setLevel(logging.DEBUG)                        # 设置输出级别为DEBUG
ch = logging.StreamHandler()                          # 设置处理器
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')  # 设置输出格式（年月日时分秒毫秒，日志名，日志级别，消息
ch.setFormatter(formatter)
logger.addHandler(ch)

# 为计算fps的辅助全局变量
fps_time = 0


if __name__ == '__main__':
    # 配置命令行参数
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    # 调整图片尺寸 宽和高为16的倍数
    w, h = model_wh(args.resize)
    # w，h == 0 时，设置默认尺寸为432x368
    if w > 0 and h > 0:
        # 获取姿势估计器对象
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    logger.debug('cam read+')
    # 打开摄像头获取视频对象
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    # 打开模板图片
    template = cv2.imread('./images/template.jpg')
    humans_template = e.inference(template, resize_to_default=False, upsample_size=args.resize_out_ratio)
    # template = TfPoseEstimator.draw_humans(template, humans_template, imgcopy=False)

    while True:
        ret_val, image = cam.read()

        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

        logger.debug('postprocess+')
        image = TfPoseEstimator.draw_compared_human(image, humans, humans_template)

        logger.debug('show+')
        # 给图像添加FPS数据
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('template', template)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()
