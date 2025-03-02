import pygame
from colors import *
from threading import Thread

# Constants
CELL_SIZE = 20
GRID_SIZE = 20
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE + 50, GRID_SIZE * CELL_SIZE + 50

# Grid Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (173, 216, 230)
PINK = (255, 192, 203)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Real-Time Maze Drawer")
clock = pygame.time.Clock()

class MazeVisualizer:
    def __init__(self, maze):
        self.maze = maze

    def draw(self, best_route=None):
        screen.fill(WHITE)
        # draw maze boundaries in red lines
        pygame.draw.rect(screen, RED, (0, 0, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE), 2)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = self.maze.cell_map[y][x]
                px, py = x * CELL_SIZE, y * CELL_SIZE
                
                if cell.damage == 0:
                    pygame.draw.rect(screen, YELLOW, (px, py, CELL_SIZE, CELL_SIZE))
                elif cell.damage == 10:
                    pygame.draw.rect(screen, ORANGE, (px, py, CELL_SIZE, CELL_SIZE))
                elif cell.damage == 40:
                    pygame.draw.rect(screen, RED, (px, py, CELL_SIZE, CELL_SIZE))
                elif cell.explored:
                    pygame.draw.rect(screen, BLUE, (px, py, CELL_SIZE, CELL_SIZE))

                if cell.has_survivor:
                    pygame.draw.circle(screen, (0, 255, 0), (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 5)

                if best_route and (x, y) in best_route:
                    pygame.draw.circle(screen,  BLACK, (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 2.5)

                if cell.wall_data[0]:  # North
                    pygame.draw.line(screen, BLACK, (px, py), (px + CELL_SIZE, py), 2)
                if cell.wall_data[1]:  # South
                    pygame.draw.line(screen, BLACK, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE), 2)
                if cell.wall_data[2]:  # East
                    pygame.draw.line(screen, BLACK, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE), 2)
                if cell.wall_data[3]:  # West
                    pygame.draw.line(screen, BLACK, (px, py), (px, py + CELL_SIZE), 2)
        pygame.display.flip()
        pygame.event.get()