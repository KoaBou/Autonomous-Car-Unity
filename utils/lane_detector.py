import cv2
import numpy as np
from configs import config


def find_lane_lines(img):
    """
    Detecting road markings
    This function will take a color image, in BGR color system,
    Returns a filtered image of road markings
    """

    # Convert to gray scale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    # Apply a Gaussian filter to remove noise
    # You can experiment with other filters here.
    # img_gauss = cv2.GaussianBlur(gray, (11, 11), 0)

    # # Apply Canny edge detection
    # thresh_low = 150
    # thresh_high = 200
    # img_canny = cv2.Canny(img_gauss, thresh_low, thresh_high)

    ret, lanes = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Return image
    return lanes


def birdview_transform(img):
    """Apply bird-view transform to the image
    """
    IMAGE_H = 480
    IMAGE_W = 640
    src = np.float32([[0, IMAGE_H], [640, IMAGE_H], [0, IMAGE_H * 0.4], [IMAGE_W, IMAGE_H * 0.4]])
    dst = np.float32([[240, IMAGE_H], [640 - 240, IMAGE_H], [-160, 0], [IMAGE_W+160, 0]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H)) # Image warping
    return warped_img


def find_left_right_points(image, draw=None):
    """Find left and right points of lane
    """

    points = {
        "left": -1,
        "right": -1,
        "center": config.IMAGE_WIDTH // 2,
        "have_left": False,
        "have_right": False,
        "lane_line": 0
    }

    res = [points.copy() for _ in range(2)]

    center = config.IMAGE_WIDTH // 2

    # Consider the position 70% from the top of the image
    interested_lines_y = [int(config.IMAGE_HEIGHT * line_y) for line_y in config.LINEOFINTEREST]
    
    if draw is not None:
        for interested_line_y in interested_lines_y:
            cv2.line(draw, (0, interested_line_y),
                    (config.IMAGE_WIDTH, interested_line_y), (0, 0, 255), 2)
            
    for i, interested_line_y in enumerate(interested_lines_y):
        interested_line = image[interested_line_y, :]

        # Traverse the two sides, find the first non-zero value pixels, and
        # consider them as the position of the left and right lines
        for x in range(center, 0, -1):
            if interested_line[x] > 0:
                res[i]['left'] = x
                break

        for x in range(center + 1, config.IMAGE_WIDTH):
            if interested_line[x] > 0:
                res[i]['right'] = x
                break

        # Predict right point when only see the left point
        if res[i]['left'] != -1 and res[i]['right'] == -1:
            res[i]['right'] = center + config.LANE_WIDTH
            res[i]['have_left'] = True    
        # Predict left point when only see the right point
        elif res[i]['right'] != -1 and res[i]['left'] == -1:
            res[i]['left'] = center - config.LANE_WIDTH
            res[i]['have_right'] = True
        elif res[i]['right'] == -1 and res[i]['left'] == -1:
            res[i]['right'] = center + config.LANE_WIDTH//2
            res[i]['left'] = center - config.LANE_WIDTH//2
        elif res[i]['right'] != -1 and res[i]['left'] != -1:
            res[i]['have_right'] = True
            res[i]['have_left'] = True

        res[i]['lane_line'] = res[i]['have_left'] + res[i]['have_right']
        res[i]['center'] = (res[i]['left'] + res[i]['right']) // 2

        # Draw two points on the image
        if draw is not None:
            draw = cv2.circle(draw, (res[i]['left'], interested_line_y), 7, (0, 0, 0), -1)
            draw = cv2.circle(draw, (res[i]['right'], interested_line_y), 7, (0, 0, 0), -1)
            draw = cv2.circle(draw, (res[i]['center'], interested_line_y), 7, (0, 0, 0), -1)

    return res


def find_left_right_points_seg(image, draw=None):
    """Find left and right points of lane
    """

    points = {
        "left": -1,
        "right": -1,
        "center": config.IMAGE_WIDTH // 2,
        "have_left": False,
        "have_right": False,
        "lane_line": 0
    }

    res = [points.copy() for _ in range(2)]

    center = config.IMAGE_WIDTH // 2

    # Consider the position 70% from the top of the image
    interested_lines_y = [int(config.IMAGE_HEIGHT * line_y) for line_y in config.LINEOFINTEREST]
    

    if draw is not None:
        for interested_line_y in interested_lines_y:
            cv2.line(draw, (0, interested_line_y),
                    (config.IMAGE_WIDTH, interested_line_y), (0, 0, 255), 2)
            
    for i, interested_line_y in enumerate(interested_lines_y):
        interested_line = image[interested_line_y, :]

        # Traverse the two sides, find the first non-zero value pixels, and
        # consider them as the position of the left and right lines
        for x in range(center, 0, -1):
            if interested_line[x] == 0:
                res[i]['left'] = x
                break

        for x in range(center + 1, config.IMAGE_WIDTH):
            if interested_line[x] == 0:
                res[i]['right'] = x
                break

        if res[i]['center'] - res[i]['left'] <= config.MAX_LANE_WIDTH//2:
            res[i]['have_left'] = True

        if res[i]['right'] - res[i]['center'] <= config.MAX_LANE_WIDTH//2:
            res[i]['have_right'] = True
            
        res[i]['lane_line'] = res[i]['have_left'] + res[i]['have_right']
        res[i]['center'] = (res[i]['left'] + res[i]['right']) // 2


        # Draw two points on the image
        if draw is not None:
            draw = cv2.circle(draw, (res[i]['left'], interested_line_y), 7, (255, 255, 255), -1)
            draw = cv2.circle(draw, (res[i]['right'], interested_line_y), 7, (255, 255, 255), -1)
            draw = cv2.circle(draw, (res[i]['center'], interested_line_y), 7, (255, 255, 255), -1)

    return res


if __name__ == '__main__':
    img = cv2.imread("/home/ngin/autonomous_car/data/lane_line_images/2.png")
    img_lines = find_lane_lines(img)
    img_birdview = birdview_transform(img_lines)
    draw = np.copy(img)
    draw = birdview_transform(draw)
    points = find_left_right_points(img_birdview, draw=draw)
    cv2.imshow("Lines", img_lines)
    cv2.imshow("Birdview", img_birdview)
    cv2.imshow("Draw", draw)
    cv2.waitKey(0)
    cv2.destroyAllWindows()