import cv2
import numpy as np

red = {
    "hue" : [np.array([0, 10]), np.array([170, 180])],
    "saturation" : np.array([100, 255]),
    "value" : np.array([140, 255])
}

red_ranges = {
    "lower1" : np.array([red["hue"][0][0], red["saturation"][0], red["value"][0]]),
    "upper1" : np.array([red["hue"][0][1], red["saturation"][1], red["value"][1]]),
    "lower2" : np.array([red["hue"][1][0], red["saturation"][0], red["value"][0]]),
    "upper2" : np.array([red["hue"][1][1], red["saturation"][1], red["value"][1]])
}

def detect_red_pixels(image):
    # switch to HSV colorspace (better for detecting colors) from BGR
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # create red color mask
    red_mask = cv2.inRange(hsv, red_ranges["lower1"], red_ranges["upper1"]) + cv2.inRange(hsv, red_ranges["lower2"], red_ranges["upper2"])

    # apply color mask to highlight red pixels
    red_highlighted = cv2.bitwise_and(image, image, mask=red_mask)

    return red_highlighted


def normalize_brightness(image):
    # convert to HSV to normalize V (value) channel
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.equalizeHist(v) # normalize brightness using histogram eqtn

    # merge HSV channels again and convert back to BGR colorspace
    hsv_normalized = cv2.merge([h, s, v])
    bgr_normalized = cv2.cvtColor(hsv_normalized, cv2.COLOR_HSV2BGR)

    return bgr_normalized

def draw_contour_centers(image, contours):
    for contour in contours:
        M = cv2.moments(contour)
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])

        cv2.circle(image, (center_x, center_y), 3, (255, 0, 0), -1)

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cam.isOpened():
    print("Error, camera not opened succesfully.")
    exit()
else:
    print("Camera opened succesfully.")

run = True
while run:
    # get image from camera & normalize the brightness
    success, image = cam.read()

    if not success:
        print("Error, no frame captured")
        break

    normalized_image = normalize_brightness(image)
    red_pixels = detect_red_pixels(normalized_image)

    # blob detection
    greyscale = cv2.cvtColor(red_pixels, cv2.COLOR_BGR2GRAY)
    cv2.imshow("grey", greyscale)
    _, threshold = cv2.threshold(greyscale, 10, 255, cv2.THRESH_BINARY)
    cv2.imshow("threshold", threshold)

    # dilate threshold image to remove small holes and combine regions for more accurate contours
    kernel = np.ones((7,7), np.uint8)
    threshold = cv2.dilate(threshold, kernel)

    # get contours
    contours,_ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        cv2.drawContours(image, contours, -1, (0, 255, 0), 5)
        draw_contour_centers(image, contours)

    # show webcam feed and red pixel mask
    cv2.imshow('Webcam Feed', image)
    cv2.imshow('Red Highlight', red_pixels)

    # break loop when q is pressed
    if cv2.waitKey(1) == ord('q'):
        break