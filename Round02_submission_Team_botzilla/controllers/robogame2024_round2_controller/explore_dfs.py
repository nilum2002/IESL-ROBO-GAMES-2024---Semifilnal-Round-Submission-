from controller import Robot
from robot_utils import RobotUtils
from navigation_utils import NavigationUtils
from maze import Maze
from colors import *
from color_detect import is_color_exists, get_color_deltas

robot = Robot()
robot_utils = RobotUtils(robot)
nav_utils = NavigationUtils(robot_utils)
maze = Maze()

# Cardinal bearings (ENU)
CARDINAL_BEARING = {
    0:   'N',
    90:  'W',
    180: 'S',
    270: 'E',
}

# Cardinal step factors for move forward from current bearing (dx, dy)
CARDINAL_STEPPING = {
    'N': lambda step: (0, +step),
    'W': lambda step: (-step, 0),
    'S': lambda step: (0, -step),
    'E': lambda step: (+step, 0),
}

# Cell step factors for move forward from current cell of maze (dx, dy)
CELL_STEPPING = {
    'N': lambda step: (0, -step),
    'W': lambda step: (-step, 0),
    'S': lambda step: (0, +step),
    'E': lambda step: (+step, 0),
}

INITIAL_DIRECTION_BEARING = 0
INITIAL_POSITION = None

def get_direction():
    bearing = robot_utils.direction_bearing()
    return CARDINAL_BEARING[bearing]

def get_direction_relative_to_initial(abosolute_direction_bearing):
    return CARDINAL_BEARING[(abosolute_direction_bearing - INITIAL_DIRECTION_BEARING) % 360]

def get_direction_bearing_relative_to_initial(abosolute_direction_bearing):
    return (abosolute_direction_bearing - INITIAL_DIRECTION_BEARING) % 360

def stepped_position(current_position, step, direction=None, stepper=CARDINAL_STEPPING):
    if direction is None:
        direction = get_direction()
    stepping = stepper[direction](step)
    return [current_position[0] + stepping[0], current_position[1] + stepping[1]]

def scan_available_directions():
    bearing = robot_utils.direction_bearing()
    available_directions = []
    if not robot_utils.ds_front_detected():
        available_directions.append(bearing)
    if not robot_utils.ds_right_detected():
        available_directions.append((bearing - 90) % 360)
    if not robot_utils.ds_left_detected():
        available_directions.append((bearing + 90) % 360)
    return available_directions

def maze_set_new_cell(selected_direction_bearing, next_position):
    relative_direction = get_direction_relative_to_initial(selected_direction_bearing)
    next_cell = stepped_position(maze.current_cell(), 1, relative_direction, CELL_STEPPING)
    maze.set_cell(next_cell[0], next_cell[1], next_position[0], next_position[1])

def maze_update_current_cell():
    bearing = get_direction_bearing_relative_to_initial(robot_utils.direction_bearing())
    
    # Wall data [North, South, East, West]
    walls = []

    if robot_utils.ds_front_detected():
        walls.append(CARDINAL_BEARING[bearing])
    if robot_utils.ds_right_detected():
        walls.append(CARDINAL_BEARING[(bearing - 90) % 360])
    if robot_utils.ds_left_detected():
        walls.append(CARDINAL_BEARING[(bearing + 90) % 360])
    
    wall_data = [0, 0, 0, 0]

    if 'N' in walls:
        wall_data[0] = 1
    if 'S' in walls:
        wall_data[1] = 1
    if 'E' in walls:
        wall_data[2] = 1
    if 'W' in walls:
        wall_data[3] = 1

    # Color detection (bottom camera)
    damage = -1

    image_array = robot_utils.camera_bottom.getImageArray()
    color_deltas_array = [get_color_deltas(image_array, RED), get_color_deltas(image_array, ORANGE), get_color_deltas(image_array, YELLOW)]
    min_delta = float('inf')
    min_delta_index = -1

    for i in range(3):
        if color_deltas_array[i] is not None and color_deltas_array[i] < min_delta:
            min_delta = color_deltas_array[i]
            min_delta_index = i

    if min_delta_index == 0:
        damage = 40
    elif min_delta_index == 1:
        damage = 10
    elif min_delta_index == 2:
        damage = 0

    # Color detection (front camera)
    survivor = 0

    image_array = robot_utils.camera_front.getImageArray()

    if robot_utils.ds_front_detected() and is_color_exists(image_array, GREEN, threshold=20):
        survivor = 1

    # Update the current cell of maze
    maze.update_current_cell(wall_data, damage, survivor)

while robot_utils.step(): break

# Use initial cardinal bearing as initial direction
INITIAL_DIRECTION_BEARING = robot_utils.direction_bearing()
# Initialize initial position
INITIAL_POSITION = robot_utils.gps.getValues()

# Move to the entrance cell (it is located after 0.455m (radius + tile + tile / 2 = 0.08 + 0.25 + 0.125) north from the initial position)
entarnce_position = stepped_position(INITIAL_POSITION, 0.455)

# Normalize the entrance position (to nearest factor of 0.125)
entarnce_position[0] = round(entarnce_position[0] / 0.125) * 0.125
entarnce_position[1] = round(entarnce_position[1] / 0.125) * 0.125

# Move to the entrance position
nav_utils.move_to_point(entarnce_position[0], entarnce_position[1])
maze.set_entrance(entarnce_position[0], entarnce_position[1])

location_stack = []
branch_stack = []
visited = set()

location_stack.append(entarnce_position)
visited.add(tuple(entarnce_position))

print('Exploration started...')

while robot_utils.step():
    # update the current cell of maze
    maze_update_current_cell()

    # scan available directions
    available_directions = scan_available_directions()

    # check those visited
    for direction in available_directions[:]:
        next_position = stepped_position(location_stack[-1], 0.25, CARDINAL_BEARING[direction])
        if tuple(next_position) in visited:
            available_directions.remove(direction)

    # return to initial position if all directions are visited
    if len(visited) == 400:
        print('Backtracking to entrance...')
        while True:
            previous = location_stack[-1]
            nav_utils.move_to_point(previous[0], previous[1])

            if (previous == location_stack[0]):
                break
            else: 
                location_stack.pop()
                maze.back_track()
        print('Returning to initial position...')
        nav_utils.move_to_point(INITIAL_POSITION[0], INITIAL_POSITION[1])
        nav_utils.rotate_to_angle(INITIAL_DIRECTION_BEARING)
        # maze.save('maze.json') For testing purposes
        print('Exploration completed!')
        break

    # if there are no available directions, backtrack
    if len(available_directions) == 0:
        print('Backtracking...')
        while True:
            previous = location_stack[-1]
            nav_utils.move_to_point(previous[0], previous[1])

            if (previous == branch_stack[-1]):
                branch_stack.pop()
                break
            else: 
                location_stack.pop()
                maze.back_track()
        continue

    # select the next direction
    selected_direction_bearing = available_directions.pop()

    # append the current position to the branches if there are more than one available directions after popping the selected direction
    if len(available_directions) > 0:
        branch_stack.append(location_stack[-1])

    # move to the next position
    next_position = stepped_position(location_stack[-1], 0.25, CARDINAL_BEARING[selected_direction_bearing])
    nav_utils.move_to_point(next_position[0], next_position[1])

    location_stack.append(next_position)
    visited.add(tuple(next_position))

    # set the new cell of maze
    maze_set_new_cell(selected_direction_bearing, next_position)

    print(f'Explored: {len(visited)}/400 --> {len(visited) / 400 * 100:.2f}%')
