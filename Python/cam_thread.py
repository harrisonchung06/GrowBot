import cv2
import numpy as np 
import threading 

class CameraThread(threading.Thread):
    def __init__(self, camera_index):
        threading.Thread.__init__(self)
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.coord_list = []
        self.running = True

    def isolate_red(hsv_image):
        hsv = hsv_image
        lower_red_r1, upper_red_r1 = np.array([0, 120, 70]), np.array([10, 255, 255])
        lower_red_r2, upper_red_r2 = np.array([170, 120, 70]), np.array([180, 255, 255])
        red_mask = cv2.inRange(hsv, lower_red_r1, upper_red_r1) + cv2.inRange(hsv, lower_red_r2, upper_red_r2)
        red_highlighted = cv2.bitwise_and(hsv_image, hsv_image, mask=red_mask)
        return red_highlighted
    
    def normalize_brightness(bgr_image):
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v) 
        hsv_normalized = cv2.merge([h, s, v])
        return hsv_normalized

    def run(self):
        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                break
            
            frame = np.array(frame)
            frame = cv2.flip(frame,1)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            hsv_norm = self.normalize_brightness(frame)
            red_highlight = self.isolate_red(hsv_norm)

            h,w,_ = frame.shape
            center_x = w//2
            center_y = h//2

            cv2.circle(frame, (center_x, center_y), 1, (255,0,0),-1)

            cv2.imshow(f'{self.camera_index}',  cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            cv2.imshow(f'{self.camera_index}',  cv2.cvtColor(red_highlight, cv2.COLOR_BGR2RGB))

            if cv2.waitKey(1) == ord('q'):
                self.running = False
        self.cap.release()
    



