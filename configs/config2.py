###############################
###### Car Controller #########
###############################
KP = 0.2
KI = 0.01
KD = 0.005

MAX_THROTTLE = 0.8
MIN_THROTTLE = 0.4
THROTTLE = 0.6
STEERING_ANGLE = 0.0

MAX_STEERING_ANGLE = 25.0
MIN_STEERING_ANGLE = -25.0

MAX_TURNING_TIME = 5
MIN_TURNING_TIME = 0.8
STOP_TIME = 2
GO_STRAIGHT_THROTTLE = .8
TURNING_THROTTLE = 1.
TURN_LEFT_ANGLE = -0.9
TURN_RIGHT_ANGLE = 0.9

###############################
###### TRAFFIC DETECTOR #######
###############################

TRAFFICSIGN_MODEL = "/home/ngin/autonomous_car/models/traffic_sign_classifier_lenet_v2.onnx"


###############################
###### TRAFFIC DETECTOR #######
###############################
LINEOFINTEREST = [
    0.99,
    0.8
]


###############################
############ MAP ##############
###############################
LANE_WIDTH = 105
MAX_LANE_WIDTH = int(1.5 * LANE_WIDTH)

###############################
######## SENSOR DATA ##########
###############################
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

###############################
########### DEBUG #############
###############################
SHOW_IMAGE = True
SHOW_TRAFFIC_SIGN = True