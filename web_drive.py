import asyncio
import base64
import json
import time
from io import BytesIO
from multiprocessing import Process, Queue

import cv2
import numpy as np
import utils.controller
import websockets
from PIL import Image

from simple_pid import PID

import utils
import config
import utils.trafficsign_detector

traffic_sign_model = cv2.dnn.readNetFromONNX(config.TRAFFICSIGN_MODEL)

# Global queue to save current image
# We need to run the sign classification model in a separate process
# Use this queue as an intermediate place to exchange images
g_image_queue = Queue(maxsize=5)

# Car controller 
car_controller = utils.controller.carController()
car_controller.controller = PID(config.KP, config.KI, config.KD, setpoint=0.)
car_controller.throttle = config.THROTTLE

# Function to run sign classification model continuously
# We will start a new process for this
def process_traffic_sign_loop(g_image_queue):
    while True:
        if g_image_queue.empty():
            time.sleep(0.1)
            continue
        image = g_image_queue.get()

        # Prepare visualization image
        draw = image.copy()
        # Detect traffic signs
        utils.trafficsign_detector.detect_traffic_signs(image, traffic_sign_model, draw=draw)
        # Show the result to a window
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)


async def process_image(websocket, path):
    async for message in websocket:
        # Get image from simulation
        data = json.loads(message)
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cur_throttle = data['throttle']
        cur_steer_angle = data['steering_angle']
        
        print(f"Current throttle: {cur_throttle}")
        print(f"Current steering angle: {cur_steer_angle}")

        # Prepare visualization image
        draw = image.copy()

        # Send back throttle and steering angle
        car_controller.control(image, draw)
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
        print(message)

        await websocket.send(message)


async def main():
    async with websockets.serve(process_image, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    p = Process(target=process_traffic_sign_loop, args=(g_image_queue,))
    p.start()
    asyncio.run(main())