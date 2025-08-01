import cv2
import numpy as np 
import threading 
import math 
from queue import Queue 

class CameraThread(threading.Thread):
    def __init__(self, camera_index):
        threading.Thread.__init__(self, daemon=True)
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.queue = Queue()
        self.running = True
        self.detection_history = [] 
        self.history_length = 5     
        self.stability_threshold = 3

    def is_stable(self, current_coord, history):
        if not history:
            return False
            
        matches = 0
        for frame_detections in history:
            for coord, _ in frame_detections:
                distance = math.sqrt((current_coord[0]-coord[0])**2 + (current_coord[1]-coord[1])**2)
                if distance < 30:  
                    matches += 1
                    break
                    
        return matches >= self.stability_threshold

    def isolate_red(self, hsv_image):
        hsv = hsv_image
        lower_red_r1, upper_red_r1 = np.array([0, 100, 50]), np.array([15, 255, 255])
        lower_red_r2, upper_red_r2 = np.array([165, 100, 50]), np.array([180, 255, 255])
        red_mask = cv2.inRange(hsv, lower_red_r1, upper_red_r1) + cv2.inRange(hsv, lower_red_r2, upper_red_r2)
        red_highlighted = cv2.bitwise_and(hsv_image, hsv_image, mask=red_mask)
        return red_highlighted, red_mask
    
    def normalize_brightness(self, bgr_image):
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v) 
        hsv_normalized = cv2.merge([h, s, v])
        return hsv_normalized
    
    def draw_bbox(self, red_highlight, red_mask):
        contours,_ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        coord_list = []
        area_list = []
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            if w>=50 and h>=50:
                cx_fruit = int(x +0.5*w)
                cy_fruit = int(y+ 0.5*h)

                coord_list.append((cx_fruit,cy_fruit)) 
                area_list.append((w*h))

                cv2.rectangle(red_highlight, (x,y),(x+w,y+h),(0,255,0),2)
                cv2.circle(red_highlight, (cx_fruit, cy_fruit), 1, (255,0,0), -1)

        return coord_list, area_list

    def run(self):
        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                break
            
            frame = np.array(frame)
            frame = cv2.flip(frame,1)

            #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            #if self.camera_index == 1:
                #frame = cv2.flip(frame,0)

            hsv_norm = self.normalize_brightness(frame)
            red_highlight, red_mask = self.isolate_red(hsv_norm)
            coord_list, area_list = self.draw_bbox(red_highlight, red_mask)

            stable_coords = []
            stable_areas = []
            
            for coord, area in zip(coord_list, area_list):
                if self.is_stable(coord, self.detection_history[-self.history_length:]):
                    stable_coords.append(coord)
                    stable_areas.append(area)
            
            self.detection_history.append(list(zip(coord_list, area_list)))
            if len(self.detection_history) > self.history_length:
                self.detection_history.pop(0)
            
            coord_list = stable_coords
            area_list = stable_areas
            
            h,w,_ = frame.shape
            center_x = int(w//2)
            center_y = int(h//2)

            self.queue.put((coord_list, area_list, (center_x,center_y)))

            cv2.circle(frame, (center_x, center_y), 1, (255,0,0),-1)

            frame = cv2.resize(frame, (960, 540))
            red_highlight = cv2.resize(red_highlight, (960, 540))

            cv2.imshow(f'{self.camera_index}', frame)
            cv2.imshow(f'{self.camera_index} Red', red_highlight)

            if cv2.waitKey(1) == ord('q'):
                self.running = False

        self.cap.release()
        cv2.destroyAllWindows()



