from robot_utils import RobotUtils
from navigation_utils import NavigationUtils
from maze import Maze
# from maze_visualizer import MazeVisualizer
from astar_solver import AStarSolver
import time

ENTRANCE_CELL = (10, 19)

class Mission:
    def __init__(self, maze, initial_position, initial_bearing, entarnce_position, robot):
        self.initial_position = initial_position
        self.initial_bearing = initial_bearing
        self.entrance_position = entarnce_position

        self.robot_utils = RobotUtils(robot)
        self.nav_utils = NavigationUtils(self.robot_utils)
        self.maze = maze

        self.survivor_cells = self.find_survivor_cells()

        self.p_millis = 0

        # self.maze_visualizer = MazeVisualizer(self.maze)

    def get_normalized_shortest_path(self, points):
        if len(points) <= 2:
            return points
        
        normalized_points = [] 

        previous_direction = None

        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            if x1 == x2:
                if y2 > y1:
                    current_direction = "D"
                else:
                    current_direction = "U"
            else:
                if x2 > x1:
                    current_direction = "R"
                else:
                    current_direction = "L"

            if i == 1:
                pass
            elif current_direction != previous_direction:
                normalized_points.append(points[i - 1])
                if i == len(points) - 1:
                    normalized_points.append(points[i])
            elif i == len(points) - 1:
                normalized_points.append(points[i])

            previous_direction = current_direction

        return normalized_points
    
    def find_survivor_cells(self):
        survivor_cells = []
        for y in range(0, len(self.maze.cell_map)):
            for x in range(0, len(self.maze.cell_map[0])):
                cell = self.maze.cell_map[y][x]
                if cell.has_survivor:
                    survivor_cells.append((x, y))
        return survivor_cells

    def run(self):
        # Move to the entrance position
        self.nav_utils.move_to_point(self.entrance_position[0], self.entrance_position[1])

        # Start solving the maze
        solver = AStarSolver(self.maze.cell_map, ENTRANCE_CELL, self.survivor_cells, ENTRANCE_CELL)

        best_route = solver.find_rescue_route()
        normalized_route = self.get_normalized_shortest_path(best_route)

        survivor_detected = False
        reverse = False

        for point in normalized_route:
            cell = self.maze.cell_map[point[1]][point[0]]

            if reverse:
                self.nav_utils.move_to_point_reverse(cell.x, cell.y)
            else:
                self.nav_utils.move_to_point(cell.x, cell.y)

            if (cell.has_survivor):
                reverse = True
            elif (cell.damage <= 0):
                reverse = False

            if cell.has_survivor:
                print("Extracting Survivor... Wait for 3 seconds")
                # wait for 3 seconds (3000000000 nanoseconds)
                self.p_millis = time.time_ns()
                while (time.time_ns() - self.p_millis < 3000000000):
                    self.robot_utils.step()
                print("Survivor Extracted!")

        print("Returning to Initial Position...")

        self.nav_utils.move_to_point(self.initial_position[0], self.initial_position[1])
        self.nav_utils.rotate_to_angle(self.initial_bearing)
