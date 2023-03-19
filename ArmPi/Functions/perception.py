#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


class PerceptionArm():
    def __init__(self) -> None:
        self.size = (640, 480)
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }

        pass


    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # 历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max  # 返回最大的轮廓


    def identify_box(self, color, img):
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #如果检测到某个区域有识别到的物体，则一直检测该区域直到没有为止
        frame_gb = getMaskROI(frame_gb, roi, self.size)         
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间  
        area_max = 0
        areaMaxContour = 0

        for i in color_range:
            if i in color:
                detect_color = i
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # 对原图像和掩模进行位运算
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # 开运算
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # 闭运算
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # 找出最大轮廓
        if area_max > 2500:  # 有找到最大面积
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))

            roi = getROI(box) #获取roi区域
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # 获取木块中心坐标
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) #转换为现实世界坐标
            
            
            cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) #绘制中心点
            distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2)) #对比上次坐标来判断是否移动
            last_x, last_y = world_x, world_y



if __name__ == '__main__':
    my_camera = Camera.Camera()
    my_camera.camera_open()
    per = PerceptionArm()
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = per.identify_box(img)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()