from simple_pid import PID
import time
from configs import config

from utils.lane_detector import *


# TODO: Add Traffic Logic Control
class carController():
    def __init__(self) -> None:
        self.controller = PID(config.KP, config.KI, config.KD, setpoint=0)
        self.steering_angle = 0
        self.throttle = config.THROTTLE

        self.image = None

        self.haveRight = False
        self.haveLeft = False
        self.laneLine = 0

        self.lastSignDetection = None
        self.last_sign = None
        self.lastSignTime = 0

        self.turningTime = 0

    def calculate_control_signal(self, draw=None):
        # Find left/right points
        img_lines = find_lane_lines(self.image)
        img_birdview = birdview_transform(img_lines)
        draw[:, :] = birdview_transform(draw)
        left_point, right_point, have_left, have_right = find_left_right_points(img_birdview, draw=draw)

        self.haveLeft = have_left
        self.haveRight = have_right
        self.laneLine = have_left + have_right

        im_center = self.image.shape[1] // 2

        if left_point != -1 and right_point != -1:

            # Calculate the deviation
            center_point = (right_point + left_point) // 2
            center_diff =  im_center - center_point

        # self.steering_angle = self.controller(center_diff)
        self.throttle = config.THROTTLE
        self.steering_angle = self.controller(center_diff)



    def decision_control(self, image, signs, draw=None):
        self.image = image
        self.im_height, self.im_width = image.shape[:2]
        self.calculate_control_signal(draw=draw)

        if len(signs)>0 and not self.lastSignDetection:
            for sign in signs:
                self.lastSignDetection = sign
                self.lastSignTime = time.time()

        # print("Detected signs:", signs)
        # print("Last detected sign is:", self.lastSignDetection)

        # Reduce the throttle if detected the sign
        # if self.lastSignDetection and self.turningTime==0:
        #     self.throttle = config.MIN_THROTTLE
        #     print("Slow down!")

        # Set time for turn right
        if self.turningTime == 0 and self.lastSignDetection=='right' and len(signs)==0 and self.haveRight==0:
            self.turningTime = config.MAX_TURNING_TIME
            self.lastSignTime = time.time()
            print("Turn right!")

        # Set time for turn left
        if self.turningTime == 0 and self.lastSignDetection=='left' and len(signs)==0 and self.haveLeft==0:
            self.turningTime = config.MAX_TURNING_TIME
            self.lastSignTime = time.time()
            print("Turn left!")

        if self.turningTime == 0 and self.lastSignDetection=='straight' and len(signs)==0:
            self.turningTime = config.MAX_TURNING_TIME
            self.lastSignTime = time.time()
            print("Go straight!")

        if self.turningTime == 0 and (self.lastSignDetection=='no_left' or self.lastSignDetection=='no_right') and len(signs)==0 and self.haveLeft==0:
            self.turningTime = config.MAX_TURNING_TIME
            self.lastSignTime = time.time()
            print("See no left/right!")

        # Set time for stop
        if self.turningTime == 0 and self.lastSignDetection=='left' and len(signs) == 0 and self.haveLeft == 0:
            self.turningTime = config.STOP_TIME
            self.lastSignTime = time.time()
            print("Stop!")
        

        if (time.time() - self.lastSignTime) <= self.turningTime and not self.lastSignDetection:
            if self.lastSignDetection:
                if self.lastSignDetection == 'left':
                    self.throttle = config.TURNING_THROTTLE
                    self.steering_angle = config.TURN_LEFT_ANGLE
                    print("Turning left!")
                if self.lastSignDetection == 'right':
                    self.throttle = config.TURNING_THROTTLE
                    self.steering_angle = config.TURN_RIGHT_ANGLE
                    print("Turning right!")
                if self.lastSignDetection == 'right':
                    self.throttle = config.TURNING_THROTTLE
                    self.steering_angle = 0
                    print("Go ahead!")
                if self.lastSignDetection == 'stop':
                    self.throttle = 0
                    self.steering_angle = 0
                    print("Stopping!")

            if self.laneLine == 2 and (time.time() - self.lastSignTime) >= config.MIN_TURNING_TIME:
                self.turningTime = 0
                self.last_sign = self.lastSignDetection
                self.lastSignDetection = None
                print("Early finish turning!")
        elif (time.time() - self.lastSignTime) >= self.turningTime and self.laneLine == 2 and self.turningTime != 0:
            self.turningTime = 0 
            self.last_sign = self.lastSignDetection
            self.lastSignDetection = None
            print("Finish turning!")

        if not self.haveLeft and not self.haveRight:
            self.throttle = config.MIN_THROTTLE
            print("No lane line, slow down!")

        
        print(f"Turning time: {self.turningTime}, Last sign: {self.lastSignDetection}, number of lane line: {self.laneLine}")
        # print(f"Have left: {self.haveLeft}, Have right: {self.haveRight}")





if __name__=='__main__':
    import numpy as np

    car_controller = carController()
    print(car_controller.controller)
