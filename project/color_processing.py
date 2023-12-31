from utils.brick import EV3ColorSensor, wait_ready_sensors
import math
import time

#### GLOBAL VARIABLES ####

CS = EV3ColorSensor(1)
color_centers = {}
distance_cap = 0.2

def train_model():
    """ Train KNN model based on data from csvs in the color_data folder

    Params
    -------
    None

    Returns
    -------
        color_centers : dict<String, list<int>>
            The centers of each color cluster
    """
    for color in ["blue", "red", "green"]:
        with open(f"color_data/{color}.csv", "r") as f:
            red_sum = 0
            green_sum = 0
            blue_sum = 0
            n_points = 0
            for line in f.readlines():
                point = line.strip("[]").split(",")[:3]
                for j in range(len(point)):
                    point[j] = int(point[j])
                total = sum(point)
                for j in range(len(point)):
                    point[j] = point[j] / total
                red_sum += point[0]
                green_sum += point[1]
                blue_sum += point[2]
                n_points += 1
            color_centers[color] = [red_sum / n_points, green_sum / n_points, blue_sum / n_points]
    return color_centers
            
            
                

def classify(point, color_centers):
    """ Classifies an rgb point as blue, red, or green. Classifies as other if confidence on that
    point is beyond the threshold given by distance_cap.

    Params
    ------
        point: list<int>
            red, green, and blue values
        color_centers : dict<String, list<int>>
            The centers of each color cluster

    Returns
    -------
        color: int
            0 for blue, 1 for red, 2 for green, or 3 for other.
    """
    point = point[:3]
    total = sum(point)
    if total == 0:
        return 3
    
    for i in range(len(point)):
        point[i] = point[i] / total
    
    red_distance = math.sqrt(sum(math.pow(point[i] - color_centers["red"][i], 2) for i in range(3)))
    green_distance = math.sqrt(sum(math.pow(point[i] - color_centers["green"][i], 2) for i in range(3)))
    blue_distance = math.sqrt(sum(math.pow(point[i] - color_centers["blue"][i], 2) for i in range(3)))

    if red_distance < green_distance and red_distance < blue_distance:
        if red_distance > distance_cap:
            return 3
        return 1
    elif blue_distance < green_distance and blue_distance < red_distance:
        if blue_distance > distance_cap:
            return 3
        return 0
    elif green_distance > distance_cap:
        return 3
    return 2

if __name__ == '__main__':
    clusters = train_model()
    wait_ready_sensors(True)
    for i in range(1000):
        time.sleep(0.1)
        print(classify(CS.get_value(), clusters))