###############################
###### Car Controller #########
###############################
KP = 0.385
KI = 0.00
KD = 0.05

MAX_THROTTLE = 1.
MIN_THROTTLE = 0.6
THROTTLE = 0.5
STEERING_ANGLE = 0.0

MAX_STEERING_ANGLE = 25.0
MIN_STEERING_ANGLE = -25.0
MAX_TURNING_TIME = 2
MIN_TURNING_TIME = 0.5
STOP_TIME = 2
TURNING_THROTTLE = 0.1

TURN_LEFT_ANGLE = -1
TURN_RIGHT_ANGLE = 1

###############################
###### TRAFFIC DETECTOR #######
###############################

TRAFFICSIGN_MODEL = "/home/ngin/autonomous_car/models/traffic_sign_classifier_lenet_v2.onnx"


###############################
###### TRAFFIC DETECTOR #######
###############################
LINEOFINTEREST_X1 = 0.25
LINEOFINTEREST_X2 = 0.75
LINEOFINTEREST_Y1 = 0.95
LINEOFINTEREST_Y2 = 0.8


###############################
############ MAP ##############
###############################
LANE_WIDTH = 105

###############################
######## SENSOR DATA ##########
###############################
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480