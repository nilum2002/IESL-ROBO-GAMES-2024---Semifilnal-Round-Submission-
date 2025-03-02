from explore_dfs import *
from mission import Mission

######################################################
# Mission Started.
######################################################

print('==============================')
print('Mission Started.')
print('==============================')

mission = Mission(maze, INITIAL_POSITION, INITIAL_DIRECTION_BEARING, entarnce_position, robot)
mission.run()

print('==============================')
print('Mission Completed.')
print('==============================')

######################################################
# Mission End.
######################################################

# # Testing only
# maze = Maze()
# maze.from_file('maze.json')

# from maze_visualizer import MazeVisualizer
# maze_visualizer = MazeVisualizer(maze)
# maze_visualizer.draw() 

# while robot_utils.step():
#     pass