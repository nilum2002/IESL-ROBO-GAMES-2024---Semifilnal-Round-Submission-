import heapq

# Define movement directions (North, South, East, West)
DIRECTIONS = [(0, -1), (0, 1), (1, 0), (-1, 0)]

class AStarSolver:
    def __init__(self, cell_map, start, survivors, exit_point):
        self.cell_map = cell_map  # 2D list representing the grid
        self.start = start  # (x, y)
        self.survivors = survivors  # List of survivor positions [(x1, y1), (x2, y2), (x3, y3)]
        self.exit_point = exit_point  # (x, y)
        self.rows = len(cell_map)
        self.cols = len(cell_map[0])

    def heuristic(self, a, b):
        """Compute Manhattan distance as heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal):
        """A* search algorithm to find the shortest path avoiding fire pits."""
        pq = []  # Priority queue (min-heap)
        heapq.heappush(pq, (0, start))  # (cost, (x, y))
        came_from = {start: None}  # Tracks the path
        cost_so_far = {start: 0}  # Tracks the cost to each node

        while pq:
            current_cost, current = heapq.heappop(pq)

            if current == goal:
                break  # Stop when reaching the goal

            x, y = current
            ccell = self.cell_map[y][x]

            for i in range(4):
                if ccell.wall_data[i] == 1: continue  # Skip if there is a wall

                dx, dy = DIRECTIONS[i]
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    ncell = self.cell_map[ny][nx]
                    new_cost = cost_so_far[current] + ncell.get_cost()

                    if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                        cost_so_far[(nx, ny)] = new_cost
                        priority = new_cost + self.heuristic((nx, ny), goal)
                        heapq.heappush(pq, (priority, (nx, ny)))
                        came_from[(nx, ny)] = current

        return self.reconstruct_path(came_from, start, goal)

    def reconstruct_path(self, came_from, start, goal):
        """Reconstructs the path from A* search results."""
        path = []
        current = goal
        while current and current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path
    
    def find_rescue_route(self):
        """Finds the best rescue route visiting all survivors and returning to exit."""
        path = []
        current_position = self.start

        survivors_set = set(self.survivors)

        minimum = float('inf')
        nearest_path = None
        nearest_survivor = None

        while survivors_set:
            for survivor in survivors_set:
                temp_path = self.a_star(current_position, survivor)[1:]
                temp_cost = len(temp_path)
                if temp_cost < minimum:
                    minimum = temp_cost
                    nearest_survivor = survivor
                    nearest_path = temp_path

            current_position = nearest_survivor
            path.extend(nearest_path)

            survivors_set.remove(nearest_survivor)

            minimum = float('inf')

        path.extend(self.a_star(current_position, self.exit_point)[1:])  # Return to exit

        return path
