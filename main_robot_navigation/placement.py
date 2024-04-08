# pot placement strategy
# predefined points to place pots
# pick up pots and see whether standing or knocked over 
# check whether place is occupied 
# if empty place pot
# else go to next free space 

# find the furthest corner of the placement area
def find_corner(grid):
    rows, cols = len(grid), len(grid[0])
    return rows - 1, cols - 1
# leave sufficient space between plants 
