import numpy as np

directions = [[-1, 0, 0],
             [ 0,-1, 0],
             [ 1, 0, 0],
             [ 0, 1, 0],
             [ 0, 0,-1],
             [ 0, 0, 1]]
cost = 1

def move_direction(x, y, z, direction, multiplier = 1):
    x = x + directions[direction][0] * multiplier
    y = y + directions[direction][1] * multiplier
    z = z + directions[direction][2] * multiplier
    return x, y, z

def search(init, goal, grid):
    heuristic = calcHeuristic(grid, goal)

    xdim=grid.shape[0]
    ydim=grid.shape[1]
    zdim=grid.shape[2]

    x = init[0]
    y = init[1]
    z = init[2]

    closed = np.empty((xdim,ydim,zdim), dtype=np.int8)
    closed[:] = 0
    closed[x,y,z] = 1

    expand = np.empty((xdim,ydim,zdim), dtype=np.int8)
    expand[:] = -1
    action = np.empty((xdim,ydim,zdim), dtype=np.int8)
    action[:] = -1

    g = 0
    h = heuristic[x,y,z]
    f = g+h

    openl = [[f, g, x, y, z]]

    found = False  # flag that is set when search is complete
    resign = False # flag set if we can't find expand
    count = 0

    while not found and not resign and count < 1e6:
        if len(openl) == 0:
            resign = True
            return "Fail: Open List is empty"
        else:
            openl.sort()
            openl.reverse()
            nextl = openl.pop()

            x = nextl[2]
            y = nextl[3]
            z = nextl[4]
            g = nextl[1]
            f = nextl[0]
            expand[x,y,z] = count
            count += 1

            if x == goal[0] and y == goal[1] and z == goal[2]:
                found = True
            else:
                for i in range(len(directions)):
                    x2, y2, z2 = move_direction(x, y, z, i)

                    if z2 >= 0 and z2 < zdim and y2 >=0 and y2 < ydim and x2 >=0 and x2 < xdim:
                        if closed[x2,y2,z2] == 0 and not grid[x2,y2,z2]:

                            continuation = False
                            for j in range(len(directions)):
                                x3, y3, z3 = move_direction(x2, y2, z2, j)
                                if (x3 >= 0 and x3 < xdim and y3 >= 0 and y3 < ydim and z3 >= 0 and z3 < zdim):
                                    x4, y4, z4 = move_direction(x2, y2, z2, action[x3, y3, z3])
                                    if x2 == x4 and y2 == y4 and z2 == z4:
                                        continuation = True

                            g2 = g + cost
                            f2 = g2 + heuristic[x2,y2,z2] + (0 if continuation else 10)
                            openl.append([f2, g2, x2, y2, z2])
                            closed[x2,y2,z2] = 1
                            action[x2,y2,z2] = i
                    else:
                        pass

    path=[]
    path.append((goal[0], goal[1], goal[2]))

    while x != init[0] or y != init[1] or z != init[2]:
        x, y, z = move_direction(x, y, z, action[x, y, z], -1)
        path.append((x, y, z))

    path.reverse()
    return path

def calcHeuristic(grid, goal):
    xdim=grid.shape[0]
    ydim=grid.shape[1]
    zdim=grid.shape[2]

    heuristic = np.empty((xdim,ydim,zdim), dtype=np.float32)
    heuristic[:] = 0.0

    for z in range(zdim):
        for y in range(ydim):
            for x in range(xdim):
                heuristic[x, y, z] = (x - goal[0]) + (y - goal[1]) + (z - goal[2])
    return heuristic

# start = [1, 50, 10]
# goal = [95, 50, 10]
# path=search(start, goal, grid)

