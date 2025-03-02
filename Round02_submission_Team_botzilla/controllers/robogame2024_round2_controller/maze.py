# from maze_visualizer import MazeVisualizer
import json

MAZE_CELL_SIZE = 20
ENTRANCE_CELL = (10, 19)

class Maze:
    def __init__(self):
        self.cell_map = [[Cell() for _ in range(MAZE_CELL_SIZE)] for _ in range(MAZE_CELL_SIZE)]
        self.explore_cell_stack = []
        # self.visualizer = MazeVisualizer(self)

    def current_cell(self):
        return self.explore_cell_stack[-1]

    def set_entrance(self, x_coord, y_coord):
        cell = self.cell_map[ENTRANCE_CELL[1]][ENTRANCE_CELL[0]]
        cell.x = x_coord
        cell.y = y_coord
        self.explore_cell_stack.append((ENTRANCE_CELL[0], ENTRANCE_CELL[1]))

    def set_cell(self, x, y, x_coord, y_coord):
        cell = self.cell_map[y][x]
        cell.x = x_coord
        cell.y = y_coord
        self.explore_cell_stack.append((x, y))
        # self.visualizer.draw()

    def update_current_cell(self, wall_data=[0,0,0,0], damage=0, survivor=0):
        cell = self.cell_map[self.explore_cell_stack[-1][1]][self.explore_cell_stack[-1][0]]
        if cell.explored: return
        cell.wall_data = wall_data
        cell.damage = damage
        cell.has_survivor = survivor
        cell.explored = True
        # self.visualizer.draw()

    def back_track(self):
        self.explore_cell_stack.pop()

    def to_array(self):
        return [[cell.to_array() for cell in row] for row in self.cell_map]

    def to_json(self):
        return json.dumps(self.to_array())
    
    def from_file(self, file):
        with open(file, 'r') as f:
            json_data = f.read()
            json_data = json.loads(json_data)

            for y in range(MAZE_CELL_SIZE):
                for x in range(MAZE_CELL_SIZE):
                    cell = self.cell_map[y][x]
                    cell.wall_data = json_data[y][x][0]
                    cell.damage = json_data[y][x][1]
                    cell.has_survivor = json_data[y][x][2]
                    cell.x = json_data[y][x][3][0]
                    cell.y = json_data[y][x][3][1]

    def save(self, file):
        with open(file, 'w') as f:
            f.write(self.to_json())
        

class Cell:
    def __init__(self):
        self.explored = False
        self.x = None # gps x coordinate
        self.y = None # gps y coordinate
        self.wall_data = [0, 0, 0, 0] # [has_wall_north, has_wall_south, has_wall_east, has_wall_west]
        self.damage = None
        self.has_survivor = None

    def get_cost(self):
        if self.damage == None or self.damage == -1: return 1
        return self.damage

    def to_array(self):
        return [self.wall_data, self.damage, self.has_survivor, [self.x, self.y]]