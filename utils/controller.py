from simple_pid import PID
import time
from configs import config

from utils.lane_detector import *
from utils.lane_segmentator import lane_segmentation


# TODO: Add Traffic Logic Control
class carController():
    def __init__(self) -> None:
        self.controller = PID(config.KP, config.KI, config.KD, setpoint=0)
        self.steering_angle = 0
        self.throttle = config.THROTTLE

        self.image = None

        self.lane = {
            "type": 2,
            "lines": [{
                'left': -1,
                'right': -1,
                'center': -1,
                'lane_width': -1,
                'have_left': False,
                'have_right': False,
                'lane_line': 0
            } for _ in range(len(config.LINEOFINTEREST))]
        }

        self.lastSignDetection = None
        self.last_sign = None
        self.lastSignTime = 0

        self.turningTime = 0
        self.state = 'PID'
        self.discontinuous = True


    def drive(self, image, signs, cur_angle):
        self.image = image
        self.signs = signs
        self.cur_angle = float(cur_angle)
        self.image_process()
        self.decision_state()
        self.calculate_control_signal()

        print("\nState: ", self.state, 
              "\nTuring time remains: ", self.turningTime - (time.time() - self.lastSignTime), 
              "\nLane type: ", self.lane['type'], 
              "Steering angle: ", self.steering_angle,
              "Throttle: ", self.throttle)

    
    def image_process(self):
        # Find left/right points
        draw = np.copy(self.image)
        draw[:, :] = birdview_transform(draw)

        # img_lines = find_lane_lines(self.image)
        # img_birdview = birdview_transform(img_lines)
        line_img = find_lane_lines(self.image)
        line_birdview = birdview_transform(line_img)
        lines = find_left_right_points(line_birdview)
        self.lane['lines'] = lines

        img_lines_seg = lane_segmentation(self.image)
        img_birdview_seg = birdview_transform(img_lines_seg)
        lines_seg = find_left_right_points_seg(img_birdview_seg, draw=draw)

        for i, line_seg in enumerate(lines_seg):
            self.lane['lines'][i]['lane_width'] = line_seg['right'] - line_seg['left']
            self.lane['lines'][i]['left_seg'] = line_seg['left']
            self.lane['lines'][i]['right_seg'] = line_seg['right']

        if lines[1]['lane_width'] > config.MAX_LANE_WIDTH:
            self.lane['type'] = 3
        else:
            self.lane['type'] = 2


        if config.SHOW_IMAGE:
            # cv2.imshow("Lines", img_lines)
            cv2.imshow("Lines", line_birdview)
            cv2.imshow("Segments", img_lines_seg)
            cv2.imshow("Result", draw)
            cv2.waitKey(1)

    def decision_state(self):
        # Set detected signs
        if self.state=='PID' and len(self.signs) >= 1 and abs(self.steering_angle)<0.2:
        # if self.state=='PID' and len(self.signs) >= 1:
            if 'left' in self.signs:
                self.lastSignDetection = 'left'
            elif 'right' in self.signs:
                self.lastSignDetection = 'right'
            elif 'straight' in self.signs:
                self.lastSignDetection = 'straight'
            elif 'no_left' in self.signs:
                self.lastSignDetection = 'no_left'
            elif 'no_right' in self.signs:
                self.lastSignDetection = 'no_right'

            print("\nDetected sign: ", self.lastSignDetection)

            self.turningTime = config.MAX_TURNING_TIME*(1.5 if self.lastSignDetection in ['no_left', 'no_right'] else 1)
            self.lastSignTime = time.time()
            self.waitTurn()

        # Slow down when detected sign
        if self.lastSignDetection and self.lastSignDetection in self.signs:
            self.lastSignTime = time.time()


        # Turn left/right when the sign disappear
        if self.state=='WAITING':
            if self.lastSignDetection == 'straight' and self.lane['lines'][1]['lane_line']!=2:
                if abs(self.angle_diff) < 1:
                    self.state = 'STRAIGHT'
                    return
            elif self.lastSignDetection == 'no_left':
                    self.state = 'NO_LEFT'
            elif self.lastSignDetection == 'no_right':
                    self.state = 'NO_RIGHT'
            elif self.lastSignDetection == 'left':
                self.turnLeft()
            elif self.lastSignDetection == 'right':
                self.turnRight()  
   

        # Reset the sign detection
        if self.turningTime!=0: 
            ## Reset after the turning time
            if (time.time() - self.lastSignTime) > self.turningTime:
                print("\nReset sign detection")
                self.resetState()
            ## Early reset when detected two lane lines
            if self.lane['lines'][0]['lane_line'] == 2 and (time.time() - self.lastSignTime) > config.MIN_TURNING_TIME:
                print("\nEarly reset sign detection")
                self.resetState()


    def calculate_control_signal(self):
        if self.discontinuous and self.lane['lines'][0]['lane_line'] == 0:
            self.lane['lines'][0]['center'] = (self.lane['lines'][0]['left_seg'] + self.lane['lines'][0]['right_seg'])//2              
        angle_diff = np.arctan((self.lane['lines'][0]['center'] - config.IMAGE_WIDTH//2)/ 
                            ((1-config.LINEOFINTEREST[0])*config.IMAGE_HEIGHT))
        angle_diff = -np.rad2deg(angle_diff)
        self.angle_diff = angle_diff
        print("\nAngle diff: ", angle_diff)

        # self.steering_angle = self.controller(center_diff)
        self.steering_angle = self.controller(angle_diff) / config.MAX_STEERING_ANGLE
        self.throttle = (abs(self.steering_angle)*(config.MAX_THROTTLE-config.THROTTLE)) + config.THROTTLE
        # self.throttle = config.THROTTLE
        if self.state == 'WAITING':
            self.throttle = config.MIN_THROTTLE
        elif self.state == 'NO_LEFT':
            if not self.lane['lines'][1]['have_right']:
                self.turnRight()
            elif not self.lane['lines'][1]['have_left']:
                self.state = 'STRAIGHT'
        elif self.state == 'NO_RIGHT':
            if not self.lane['lines'][1]['have_right']:
                self.turnLeft()
            elif not self.lane['lines'][1]['have_left']:
                self.state = 'STRAIGHT'
        elif self.state == 'STRAIGHT':
            self.steering_angle = 0
            self.throttle = config.GO_STRAIGHT_THROTTLE
        elif self.state == 'LEFT' and self.lane['lines'][0]['lane_line'] != 2:
            self.steering_angle = config.TURN_LEFT_ANGLE
            self.throttle = config.TURNING_THROTTLE
        elif self.state == 'RIGHT' and self.lane['lines'][0]['lane_line'] != 2:
            self.steering_angle = config.TURN_RIGHT_ANGLE
            self.throttle = config.TURNING_THROTTLE




    def waitTurn(self):
        self.state = 'WAITING'
        # self.throttle = config.MIN_THROTTLE

    def turnRight(self):
        self.state = 'RIGHT'
        # self.steering_angle = config.TURN_RIGHT_ANGLE
        # self.throttle = config.TURNING_THROTTLE

    def turnLeft(self):
        self.state = 'LEFT'
        # self.steering_angle = config.TURN_LEFT_ANGLE
        # self.throttle = config.TURNING_THROTTLE
    
    def goStraight(self):
        self.state = 'STRAIGHT'
        # self.steering_angle = 0
        # self.throttle = config.GO_STRAIGHT_THROTTLE

    def resetState(self):
        self.state = 'PID'
        self.lastSignDetection = None
        self.turningTime = 0
        self.lastSignTime = 0       





if __name__=='__main__':
    import numpy as np

    car_controller = carController()
    print(car_controller.controller)
