import asyncio
import base64
import json
import time
import functools
from io import BytesIO
import multiprocessing
from multiprocessing import set_start_method
from torch.multiprocessing import Pool, Queue, Process

import cv2
import numpy as np
import utils.controller
import websockets
from PIL import Image

from simple_pid import PID

import utils
import configs.config as config
from utils import trafficsign_detector
import torch


# Global queue to save current image
# We need to run the sign classification model in a separate process
# Use this queue as an intermediate place to exchange images

# Car controller 
car_controller = utils.controller.carController()
car_controller.controller = PID(config.KP, config.KI, config.KD, setpoint=0.)
car_controller.throttle = config.THROTTLE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Function to run sign classification model continuously
# We will start a new process for this
def process_traffic_sign_loop(g_image_queue, model, signs):
    prev_time = time.time()
    lastSigns = {
        'left': [0, 0],
        'right': [0, 0],
        'straight': [0, 0],
        'no_right': [0, 0],
        'no_left': [0, 0],
        'stop': [0, 0],
    }

    while True:
        if g_image_queue.empty():
            time.sleep(0.1)
            continue
        image = g_image_queue.get()

        # Prepare visualization image
        draw = image.copy()
        # Detect traffic signs
        detected_signs = trafficsign_detector.detect_traffic_signs(image, model, draw=draw, device=device)

        tmp_signs = []

        for sign in lastSigns.keys():
            # Count the number presence of the signs 
            if (sign in detected_signs):
                lastSigns[sign][0] = lastSigns[sign][0] + 1
                lastSigns[sign][1] = time.time()
            # Remove the signs which disappear more than 0.01 sec 
            elif time.time() - lastSigns[sign][1] > 0.001:
                lastSigns[sign][0] = 0

            # If the sign appear more than 5 time, add it to signs
            if lastSigns[sign][0] > 5:
                tmp_signs.append(sign)

        if len(tmp_signs)>0:
            signs[:] = tmp_signs
        else:
            signs[:] = []

        # print("Detected signs:", signs)
        


        # Calculate and display FPS
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(draw, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
        # Show the result to a window
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)


async def process_image(websocket, path, signs):
    async for message in websocket:
        # Get image from simulation
        data = json.loads(message)
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cur_throttle = data['throttle']
        cur_steer_angle = data['steering_angle']
        
        # print(f"Current throttle: {cur_throttle}")
        # print(f"Current steering angle: {cur_steer_angle}")

        # Prepare visualization image
        draw = image.copy()

        # Send back throttle and steering angle
        car_controller.decision_control(image, signs=signs[:], draw=draw)
        throttle, steering_angle = car_controller.throttle, car_controller.steering_angle

        # Update image to g_image_queue - used to run sign detection
        if not g_image_queue.full():
            g_image_queue.put(image)

        # Show the result to a window
        cv2.imshow("Result", draw)
        cv2.waitKey(1)


        # Send back throttle and steering angle
        message = json.dumps(
            {"throttle": throttle, "steering": steering_angle})

        await websocket.send(message)


async def main():
    process_image_partial = functools.partial(process_image, signs=signs)
    async with websockets.serve(process_image_partial, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    set_start_method('spawn', force=True)
    manager = multiprocessing.Manager()
    g_image_queue = Queue(maxsize=5)
    signs = manager.list()

    # Load traffic sign model
    # traffic_sign_model = torch.load("/home/ngin/autonomous_car/models/traffic_sign_classifier.pth", weights_only=False)
    # traffic_sign_model.to(device)
    # traffic_sign_model.eval()
    
    # p = Process(target=process_traffic_sign_loop, args=(g_image_queue, traffic_sign_model, signs))
    # p.start()
    asyncio.run(main())