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

        self.lines = None
        self.lastSignDetection = None
        self.last_sign = None
        self.lastSignTime = 0

        self.turningTime = 0
        self.state = 'PID'

    def calculate_control_signal(self):
        # Find left/right points
        draw = np.copy(self.image)

        img_lines = find_lane_lines(self.image)
        img_birdview = birdview_transform(img_lines)
        draw[:, :] = birdview_transform(draw)
        self.lines = find_left_right_points(img_birdview, draw=draw)

        cv2.imshow("Lines", img_lines)
        cv2.imshow("Result", draw)
        cv2.waitKey(1)


        im_center = config.IMAGE_WIDTH // 2

        angle_diff = np.arctan((self.lines[0]['center'] - config.IMAGE_WIDTH//2)/ 
                               ((1-config.LINEOFINTEREST_Y1)*config.IMAGE_HEIGHT))
        angle_diff = -np.rad2deg(angle_diff)

        # self.steering_angle = self.controller(center_diff)
        self.steering_angle = self.controller(angle_diff) / config.MAX_STEERING_ANGLE
        self.throttle = (abs(self.steering_angle)*(config.MAX_THROTTLE-config.THROTTLE)) + config.THROTTLE
        # self.throttle = config.THROTTLE



    def decision_control(self, image, signs):
        self.image = image
        self.im_height, self.im_width = image.shape[:2]
        self.calculate_control_signal()

        # Set detected signs
        if self.state=='PID' and len(signs) >= 1:
            if 'left' in signs:
                self.lastSignDetection = 'left'
            elif 'right' in signs:
                self.lastSignDetection = 'right'
            elif 'straight' in signs:
                self.lastSignDetection = 'straight'
            elif 'no_left' in signs:
                self.lastSignDetection = 'no_left'
            elif 'no_right' in signs:
                self.lastSignDetection = 'no_right'

            print("\nDetected sign: ", self.lastSignDetection)

            self.turningTime = config.MAX_TURNING_TIME
            self.lastSignTime = time.time()

        # Slow down when detected sign
        if self.lastSignDetection and self.lastSignDetection in signs:
            self.waitTurn()
            self.lastSignTime = time.time()


        # Turn left/right when the sign disappear
        if self.lastSignDetection and self.lines[0]['lane_line']!=2:
            if self.lastSignDetection == 'left':
                self.turnLeft()
            elif self.lastSignDetection == 'right':
                self.turnRight()  
            elif self.lastSignDetection == 'straight':  
                self.goStraight()

        # Reset the sign detection
        if self.turningTime!=0: 
            ## Reset after the turning time
            if (time.time() - self.lastSignTime) > self.turningTime:
                print("\nReset sign detection")
                self.resetState()
            ## Early reset when detected two lane lines
            if self.lines[0]['lane_line'] == 2 and (time.time() - self.lastSignTime) > config.MIN_TURNING_TIME:
                print("\nEarly reset sign detection")
                self.resetState()

        print("\nState: ", self.state, 
              "\nTuring time remains: ", self.turningTime - (time.time() - self.lastSignTime), 
              "\nLane lines: ", self.lines[0]['lane_line'], 
              "Steering angle: ", self.steering_angle,
              "Throttle: ", self.throttle)
        # print(f"Steering angle: {self.steering_angle}, Throttle: {self.throttle}")


    def waitTurn(self):
        self.state = 'WAITING'
        self.throttle = config.MIN_THROTTLE

    def turnRight(self):
        self.state = 'RIGHT'
        self.steering_angle = config.TURN_RIGHT_ANGLE
        self.throttle = config.TURNING_THROTTLE

    def turnLeft(self):
        self.state = 'LEFT'
        self.steering_angle = config.TURN_LEFT_ANGLE
        self.throttle = config.TURNING_THROTTLE
    
    def goStraight(self):
        self.state = 'STRAIGHT'
        self.steering_angle = 0
        self.throttle = config.GO_STRAIGHT_THROTTLE

    def resetState(self):
        self.state = 'PID'
        self.lastSignDetection = None
        self.turningTime = 0
        self.lastSignTime = 0       





if __name__=='__main__':
    import numpy as np

    car_controller = carController()
    print(car_controller.controller)
