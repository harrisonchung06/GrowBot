import random
import time

TARGET = 10

def obj_function(pos):
    return 

def monte_carlo_minimize(init_pos,search_range,num_iterations=10):
    best_position = init_pos
    best_value = obj_function(best_position)

    if not(best_value == 0):
        for i in range(num_iterations):
            new_position = (int)(random.uniform(search_range[0], search_range[1]))
            new_value = obj_function(new_position)
            if new_value < best_value:
                best_position = new_position
                best_value = new_value

    return best_position, best_value

#init variables  

start_time = time.perf_counter()

init_x, init_y = 0,0
best_x_pos, min_dist = monte_carlo_minimize()
best_y_pos, min_dist = monte_carlo_minimize()

end_time = time.perf_counter()

elapsed_time = end_time - start_time
