###############################
###### Car Controller #########
###############################
KP = 1.
KI = 0.00
KD = 1.5

MAX_THROTTLE = 1.0
MIN_THROTTLE = 0.1
THROTTLE = 0.3
STEERING_ANGLE = 0.0

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
LINEOFINTEREST_Y1 = 0.83
LINEOFINTEREST_Y2 = 0.9


###############################
############ MAP ##############
###############################
LANE_WIDTH = 110

