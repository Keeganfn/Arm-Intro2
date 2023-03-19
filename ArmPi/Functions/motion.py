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


class MotionArm():

    def __init__(self) -> None:
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        self.AK = ArmIK()
        self.servo1 = 500
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def open_gripper(self):
        Board.setBusServoPulse(1, self.servo1 - 280, 500)
        time.sleep(.5)

    def close_gripper(self):
        Board.setBusServoPulse(1, self.servo1, 500)
        time.sleep(.5)
    
    def change_gripper_angle(self, theta):
        Board.setBusServoPulse(2, theta, 500)
        time.sleep(.5)

    def reset(self):       
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1)

    def move_arm(position, rotation, runtime=None):
        pos = position
        rot_x = rotation[0]
        rot_y = rotation[1]
        rot_z = rotation[2]
        if runtime:
            AK.setPitchRangeMoving(pos, rot_x, rot_y, rot_z, runtime) 
        else:
            AK.setPitchRangeMoving(pos, rot_x, rot_y, rot_z)
        time.sleep(1) 



if __name__ == '__main__':
    controller = MotionArm()
    controller.open_gripper()