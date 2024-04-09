# pot placement strategy
# hardcode the plant placement positions 
# approx 6 plants 

import numpy as np

def is_occupied(grid, x, y):
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        return grid[x][y]
    else:
        return True

def find_corner(grid):
    rows, cols = len(grid), len(grid[0])
    return rows - 1, cols - 1

def find_nearest_unoccupied_space(grid, x, y):
    search_radius = 1
    while True:
        for i in range(-search_radius, search_radius + 1):
            for j in range(-search_radius, search_radius + 1):
                new_x, new_y = x + i, y + j
                if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]) and not grid[new_x][new_y]:
                    return new_x, new_y
        search_radius += 1

# test result printed
#def place_pot(x, y):
   #print(f"Placing pot at position ({x}, {y})")

placement_grid = [[False] * 5 for _ in range(5)]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # match the detected markers with hardcoded zone positions

    furthest_corner = find_furthest_corner(placement_grid)

    pot_position = find_nearest_unoccupied_space(placement_grid, furthest_corner[0], furthest_corner[1])

    if pot_position:
        if not is_position_occupied(placement_grid, pot_position[0], pot_position[1]):
            place_pot(pot_position[0], pot_position[1])
            placement_grid[pot_position[0]][pot_position[1]] = True

    # display the frame with detected markers

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
