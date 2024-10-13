import asyncio
import base64
import json
import time
from io import BytesIO

import cv2
import numpy as np
import websockets
from PIL import Image


async def save_image(websocket, path):
    last_saved_time = time.time()
    async for message in websocket:
        current_time = time.time()
        if current_time - last_saved_time >= 0.1:
            # Get image from simulation
            data = json.loads(message)
            image = Image.open(BytesIO(base64.b64decode(data["image"])))
            image = np.asarray(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Save image to folder
            timestamp = int(current_time)
            filename = f"/home/ngin/autonomous_car/data/save_images/image_{timestamp}.jpg"
            cv2.imwrite(filename, image)
            print(f"Saved image to {filename}")

            cv2.imshow("Image", image)
            cv2.waitKey(1)

            last_saved_time = current_time



async def main():
    async with websockets.serve(save_image, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())