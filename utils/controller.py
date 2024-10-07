from simple_pid import PID
from utils.lane_detector import *


class carController():
    def __init__(self) -> None:
        self.controller = PID(0.02, 0.001, 0.1, setpoint=0)
        self.steering_angle = 0
        self.throttle = 1.

    def control(self, img, draw=None):
        # Find left/right points
        img_lines = find_lane_lines(img)
        img_birdview = birdview_transform(img_lines)
        draw[:, :] = birdview_transform(draw)
        left_point, right_point = find_left_right_points(img_birdview, draw=draw)

        im_center = img.shape[1] // 2

        if left_point != -1 and right_point != -1:

            # Calculate the deviation
            center_point = (right_point + left_point) // 2
            center_diff =  im_center - center_point

        # self.steering_angle = self.controller(center_diff)
        self.steering_angle = self.controller(center_diff)



if __name__=='__main__':
    import numpy as np

    car_controller = carController()
    print(car_controller.controller)
