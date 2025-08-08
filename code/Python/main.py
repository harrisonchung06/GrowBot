from cam_thread import CameraThread
from motor_controller import MotorController
from pyusbcameraindex import enumerate_usb_video_devices_windows
import random
import time
import numpy as np
import math 

def get_latest_frame(queue):
    latest = None
    while not queue.empty():
        latest = queue.get()
    return latest

def get_score(threads, camera_indices):
    infos = []
    squared_dists = [0] * len(camera_indices)
    side_squared_dists = [0] * len(camera_indices)
    #Get info 
    for thread in threads:
        latest_info = get_latest_frame(thread.queue)
        if latest_info is not None:
            #print(f'Index: {thread.camera_index} Queue: {thread.queue.get()}')
            infos.append(latest_info)
            time.sleep(0.02)
    #Find the largest object 
    if infos:
        largest_areas = []
        largest_indices = []
        #Find the largest areas inside the info list and place the area inside the largest areas list and the indices to find the largest areas 
        for i in range(len(infos)):
            largest_area = 0
            largest_index = -1
            if infos[i][1]:
                for j in range(len(infos[i][1])):
                    if infos[i][1][j] > largest_area:
                        largest_area = infos[i][1][j]
                        largest_index = j
                largest_areas.append(largest_area)
                largest_indices.append(largest_index)
            else:
                largest_areas.append(largest_area)
                largest_indices.append(largest_index)

        for i in range(len(largest_indices)):
            #print(f'largest areas: {largest_areas}, largest indices: {largest_indices}, all info: {infos}')
            camera_center = infos[i][2]
            cam_y = camera_center[0]
            cam_z = camera_center[1]
            
            if i == 0: #Left cam min right 
                camera_side_y = 0
            elif i ==1: #Rigth cam min left 
                camera_side_y = 2*cam_y
            
            try:
                largest_center = infos[i][0][largest_indices[i]]
                
                if largest_indices[i] == -1:
                    largest_center = (float('inf'), float('inf'))
            except IndexError:
                largest_center = (float('inf'), float('inf'))

            large_y = largest_center[0]
            large_z = largest_center[1]

            #print(f'Cam_y {cam_y}, large_y {large_y}, cam_z {cam_z}, large_z {large_z}')
            #print(f' SIDE Cam_y {camera_side_y}, large_y {large_y}, cam_z {cam_z}, large_z {large_z}')
            squared_dist = (cam_y - large_y)**2 + (cam_z - large_z)**2
            squared_dists[i] = squared_dist

            side_squared_dist = (camera_side_y - large_y)**2 + (cam_z - large_z)**2
            side_squared_dists[i] = side_squared_dist
        

        valid_dists = []
        for i in range(len(squared_dists)):
            if not math.isinf(squared_dists[i]) and not squared_dists[i] == 0:
                valid_dists.append(squared_dists[i])
        valid_side_dists = []
        for i in range(len(side_squared_dists)):
            if not math.isinf(side_squared_dists[i]) and not side_squared_dists[i] == 0:
                valid_side_dists.append(side_squared_dists[i])
        
        print(f'valid distances {valid_dists}')
        print(f'valid side dists {valid_side_dists}')

        if len(valid_dists) == 2:
            print(f'both cams ')
            return sum(valid_dists)/len(valid_dists)
        elif len(valid_dists) == 1:
            print(f'one cam {valid_side_dists[0] * 1e3}')
            return valid_side_dists[0] * 1e3
        else:
            print(f'no cam')
            return float('inf')
    else:
        return float('inf')

def main():
    # Camera setup
    camera_indices = [0,1]  
    threads = []
    for index in camera_indices:
        thread = CameraThread(index)
        thread.start()
        threads.append(thread)

    # Motor setup
    arduino_port = 'COM4' 
    baud_rate = 9600
    controller = MotorController(arduino_port, baud_rate)
    controller.home()
    
    # Start at center position
    center_pos = [int(controller.max[0]//2), 
                 int(controller.max[1]//2), 
                 int(controller.max[2]//2)]
    controller.move_to_position(*center_pos, 5000, 5000, 5000)
    current_pos = center_pos.copy()

    # Monte Carlo parameters
    stop_score = 15000 #~50 mm away from the fruit stem 
    step_per_mm = 50.93
    max_iterations = 40
    temp = 1000  # Initial temperature
    cooling_rate = 0.97
    step_size = 5000  # Initial step size
    min_step = 100
    best_score = float('inf')
    best_pos = current_pos.copy()

    while True:
        temp=1000
        step_size = step_size + 1000
        for iteration in range(max_iterations):
            
            current_score = get_score(threads, camera_indices)
            print(f"curr score {current_score}")
            # Generate random neighbor (within bounds)
            while True:
                neighbor_pos = [
                    current_pos[0] + random.randint(-step_size, step_size),
                    current_pos[1] + random.randint(-step_size, step_size),
                    current_pos[2] + random.randint(-int(step_size*0.5), int(step_size*0.5))
                ]
                
                # Ensure within bounds
                if all(0 <= p <= m for p, m in zip(neighbor_pos, controller.max)):
                    break

            # Move to neighbor position
            controller.move_to_position(*neighbor_pos, 5000, 5000, 5000)
            print(f"neighbor {neighbor_pos}")

            new_score = get_score(threads, camera_indices)

            print(f"new score{new_score}")

            # Acceptance probability (simulated annealing)
            delta = new_score - current_score
            accept_prob = np.exp(-delta / temp) if temp > 0 else 0

            # Update best solution
            if new_score < best_score:
                best_score = new_score
                best_pos = neighbor_pos.copy()
                print(f"New best score: {best_score} at position {best_pos}")
                
                # If we're very close, grab the fruit
                if best_score < stop_score:  # Adjust threshold as needed
                    print("GRABBING THE FRUIT")
                    time.sleep(5)
                    controller.move_claw(0)
                    controller.move_step(0,0,-int(15*step_per_mm))
                    controller.move_step(-int(50*step_per_mm), 0,0)
                    controller.move_claw(79)
                    controller.move_step(0,0,100)
                    #Go to collection point  
                    print("Fruit grabbed!")
                    break
            
            # Accept or reject move
            if new_score < current_score or random.random() < accept_prob:
                current_pos = neighbor_pos
            else:
                # Rejected - move back
                controller.move_to_position(*current_pos, 5000, 5000, 5000)
                print("Rejected!!!")

            # Cooling schedule
            temp *= cooling_rate
            step_size = int(max(min_step, step_size * 0.95))
            
            print(f"Iteration {iteration}: Temp={temp:.1f}, Step={step_size:.0f}, Current Score={current_score:.1f}, Best Score = {best_score:.1f}")
        controller.move_to_position(*best_pos, 5000, 5000, 5000)
        


if __name__ == '__main__':
    main()