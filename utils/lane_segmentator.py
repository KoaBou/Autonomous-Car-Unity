import cv2
import numpy as np
from configs import config


polygon = np.array([[
    (int(config.IMAGE_WIDTH * 0), config.IMAGE_HEIGHT),            # Bottom left
    (int(config.IMAGE_WIDTH * 0.2), int(config.IMAGE_HEIGHT * 0.4)), # Top left (approx where lane lines meet)
    (int(config.IMAGE_WIDTH * 0.8), int(config.IMAGE_HEIGHT * 0.4)), # Top right (approx where lane lines meet)
    (int(config.IMAGE_WIDTH * 1), config.IMAGE_HEIGHT)             # Bottom right
]])


def get_roi(image, polygon):
    """Define the region of interest (ROI) as a polygon."""
    roi = np.zeros_like(image)

    cv2.fillPoly(roi, [polygon], 255)  # Fill the polygon

    masked_image = cv2.bitwise_and(roi, image)

    return masked_image

def lane_segmentation(image):
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define a range for gray colors
    # Gray colors usually have low saturation and varying values for brightness
    lower_gray = np.array([0, 0, 50])  # Low saturation and low brightness for gray
    upper_gray = np.array([180, 50, 200])  # Low saturation and high brightness for gray

    # Create a mask to isolate gray colors
    gray_mask = cv2.inRange(hsv_image, lower_gray, upper_gray)
    gray_mask = get_roi(gray_mask, polygon)

    return gray_mask


if __name__ == "__main__":
    image_path = 'data/save_images/image_1728534420.jpg'
    img = cv2.imread(image_path)
    # Apply Gaussian blur to the image to remove noise
    img = cv2.GaussianBlur(img, (5, 5), 0)

    config.IMAGE_HEIGHT, config.IMAGE_WIDTH = img.shape[:2]
    polygon = np.array([[
        (int(config.IMAGE_WIDTH * 0), config.IMAGE_HEIGHT),            # Bottom left
        (int(config.IMAGE_WIDTH * 0.2), int(config.IMAGE_HEIGHT * 0.4)), # Top left (approx where lane lines meet)
        (int(config.IMAGE_WIDTH * 0.8), int(config.IMAGE_HEIGHT * 0.4)), # Top right (approx where lane lines meet)
        (int(config.IMAGE_WIDTH * 1), config.IMAGE_HEIGHT)             # Bottom right
    ]])

    segment_lane = lane_segmentation(img)
    roi = get_roi(segment_lane, polygon)

    cv2.imshow("Original", img)
    cv2.imshow("Segmented Lane", segment_lane)
    cv2.imshow("ROI", roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()