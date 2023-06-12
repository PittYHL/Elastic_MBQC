from DP import *
import copy

def place_C(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits): #place single node
    new = 0 #how many new node
    new_shape1 = copy.deepcopy(p_shape)
    new_shape2 = copy.deepcopy(p_shape)
    new_shape3 = copy.deepcopy(p_shape)
    new_front1 = copy.deepcopy(front)
    new_front2 = copy.deepcopy(front)
    new_front3 = copy.deepcopy(front)
    # for front
    if base[1] == len(p_shape[0]) - 1:
        new_shape1[base[0]].append(1)
    else:
        x = base[0]
        y = base[1] + 1
        new_shape1[x][y] = 1
    new = new + 1
    new_shape1, space = fill_shape(new_shape1)
    spaces.append(space)
    shapes.append(new_shape1)
    new_front1.insert(c_index, [base[0], base[1] + 1])
    fronts.append(new_front1)

    if loc == 'u' or loc == 'r': #up
        placed = 0
        if base[0] == 0 and p_row + 1 + extra_qubits * 2<= rows:
            new = new + 1
            placed = 1
            new_row = [0]*len(p_shape[0])
            new_shape2.insert(0, new_row)
            new_shape2[base[0]][base[1]] = 1
            for element in new_front2:  # change exsisting element
                element[0] = element[0] + 1
            new_front2.insert(c_index, [base[0], base[1]])
        elif feasible_placement(base, [base[0] - 1, base[1]], p_shape, 'C'):
            new = new + 1
            placed = 1
            new_shape2[base[0] - 1][base[1]] = 1
            new_front2.insert(c_index, [base[0] - 1, base[1]])
        if placed:
            new_shape2, space = fill_shape(new_shape2)
            spaces.append(space)
            shapes.append(new_shape2)
            fronts.append(new_front2)
    if loc == 'd' or loc == 'r': #down
        placed = 0
        if base[0] == len(p_shape) - 1 and p_row + 1 + extra_qubits * 2 <= rows:
            new = new + 1
            placed = 1
            new_row = [0]*len(p_shape[0])
            new_shape3.append(new_row)
            new_shape3[base[0] + 1][base[1]] = 1
            new_front3.insert(c_index, [base[0] + 1, base[1]])
        elif base[0] != len(p_shape) - 1 and feasible_placement(base, [base[0] + 1, base[1]], p_shape, 'C'):
            new = new + 1
            placed = 1
            new_shape3[base[0] + 1][base[1]] = 1
            new_front3.insert(c_index, [base[0] + 1, base[1]])
        if placed:
            new_shape3, space = fill_shape(new_shape3)
            spaces.append(space)
            shapes.append(new_shape3)
            fronts.append(new_front3)
    return shapes, fronts, spaces, new

def place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed, wire_targets): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 3 - len(new_shape1[0]) + base[1]
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            # for i in range(3):
            #     for j in range(base[1] + 1, base[1] + 3):
            #         new_shape1[i][j] = 1
            if base[0] < 2:  #place the B
                for i in range(3):
                    for j in range(base[1] + 1, base[1] + 3):
                        new_shape1[i][j] = 1
            else:
                for i in range(3):
                    for j in range(base[1] + 1, base[1] + 3):
                        new_shape1[base[0] - i][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 2:
                new_front.append([base[0] + extra_row, base[1] + 2])  # add two base
                new_front.append([0, base[1] + 2])
            else:
                new_front.append([base[0], base[1] + 2])  # add two base
                new_front.append([base[0] - 2, base[1] + 2])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed and base[0] < 2:
                wire_targets.append([[0, base[1] + 1]])
            elif wire_not_placed and base[0] >= 2:
                wire_targets.append([[base[0] - 2, base[1] + 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] == 0 or (p_shape[base[0] - 1][base[1] - 1] == 0 and ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or base[0] >= 3)): #first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] < 3:
                extra_row = 3 - base[0]
            else:
                extra_row = 0
            if base[1] == len(new_shape1[0]) - 1: #if need extra 1 column
                for row in new_shape1:
                    row.append(0)
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            # for i in range(3):
            #     for j in range(base[1], base[1] + 2):
            #         new_shape1[i][j] = 1
            if base[0] < 3:  #place the B
                for i in range(3):
                    for j in range(base[1], base[1] + 2):
                        new_shape1[i][j] = 1
            else:
                for i in range(3):
                    for j in range(base[1], base[1] + 2):
                        new_shape1[base[0] - i - 1][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 3:
                new_front.append([base[0] + extra_row - 1, base[1] + 1])  # add two base
                new_front.append([0, base[1] + 1])
            else:
                new_front.append([base[0] - 1, base[1] + 1])  # add two base
                new_front.append([base[0] - 3, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed and base[0] < 3:
                wire_targets.append([[0, base[1]]])
            elif wire_not_placed and base[0] >= 3:
                wire_targets.append([[base[0] - 3, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 3 < len(p_shape): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 3 - len(new_shape1[0]) + base[1]
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(copy.deepcopy(new_row)))
            for i in range(base[0], base[0] + 3):
                for j in range(base[1] + 1, base[1] + 3):
                    new_shape1[i][j] = 1
            new_front.append([base[0] + 2, base[1] + 2])  # add two base
            new_front.append([base[0], base[1] + 2])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed:
                wire_targets.append([[base[0] + 2, base[1] + 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] == len(p_shape) - 1 or (p_shape[base[0] + 1][base[1] - 1] == 0 and ((base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 4 < len(p_shape))): #first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] + 4 >= len(p_shape):
                extra_row = base[0] + 4 - len(p_shape)
            else:
                extra_row = 0
            #base[0] = base[0] + extra_row
            if base[1] == len(new_shape1[0]) - 1: #if need extra 1 column
                for row in new_shape1:
                    row.append(0)
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0]+1, base[0] + 4):
                for j in range(base[1], base[1] + 2):
                    new_shape1[i][j] = 1
            new_front.append([base[0] + 3, base[1] + 1])  # add two base
            new_front.append([base[0] + 1, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed:
                wire_targets.append([[base[0] + 3, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    return shapes, fronts, spaces, new, wire_targets

def place_A(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed, wire_targets): #place A node
    new = 0  # how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2):  # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 2 - len(new_shape1[0]) + base[1]
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 2:  #place the A
                for i in range(3):
                    new_shape1[i][base[1] + 1] = 1
            else:
                for i in range(3):
                    new_shape1[base[0] - i][base[1] + 1] = 1
            for element in new_front1:  # change exsisting element
                element[0] = element[0] + extra_row
            if extra_row != 0:
                new_front.append([base[0] + extra_row, base[1] + 1])  # add two base
                new_front.append([0, base[1] + 1])
            else:
                new_front.append([base[0], base[1] + 1])  # add two base
                new_front.append([base[0] - 2, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed and base[0] < 2:
                wire_targets.append([[0, base[1] + 1]])
            elif wire_not_placed and base[0] >= 2:
                wire_targets.append([[base[0] - 2, base[1] + 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] == 0 or (p_shape[base[0] - 1][base[1] - 1] == 0 and ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or base[0] >= 3)):  # first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] < 3:
                extra_row = 3 - base[0]
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 3:  #place the A
                for i in range(3):
                    new_shape1[i][base[1]] = 1
            else:
                for i in range(3):
                    new_shape1[base[0] - i - 1][base[1]] = 1
            for element in new_front1:  # change exsisting element
                element[0] = element[0] + extra_row
            if extra_row != 0:
                new_front.append([base[0] + extra_row - 1, base[1]])  # add two base
                new_front.append([0, base[1]])
            else:
                new_front.append([base[0] - 1, base[1]])  # add two base
                new_front.append([base[0] - 3, base[1]])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed and base[0] < 3:
                wire_targets.append([[0, base[1]]])
            elif wire_not_placed and base[0] >= 3:
                wire_targets.append([[base[0] - 3, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 3 < len(p_shape):  # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 2 - len(new_shape1[0]) + base[1]
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0], base[0] + 3):
                new_shape1[i][base[1] + 1] = 1
            new_front.append([base[0] + 2, base[1] + 1])  # add two base
            new_front.append([base[0], base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed:
                wire_targets.append([[base[0] + 2, base[1] + 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] == len(p_shape) - 1 or (p_shape[base[0] + 1][base[1] - 1] == 0 and ((base[0] + 4 >= len(p_shape) and p_row +base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 4 < len(p_shape))):  # first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] + 4 >= len(p_shape):
                extra_row = base[0] + 4 - len(p_shape)
            else:
                extra_row = 0
            # base[0] = base[0] + extra_row
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0] + 1, base[0] + 4):
                new_shape1[i][base[1]] = 1
            new_front.append([base[0] + 3, base[1]])  # add two base
            new_front.append([base[0] + 1, base[1]])
            if num_succ == 1 and end == 'u':
                new_front1.insert(c_index, new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.insert(c_index, new_front[1])
            elif num_succ == 2:
                new_front1.insert(c_index, new_front[0])
                new_front1.insert(c_index, new_front[1])
            if wire_not_placed:
                wire_targets.append([[base[0] + 3, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    return shapes, fronts, spaces, new, wire_targets

def place_W(p_shape, base, c_index, rows, p_row, front, shapes, fronts, spaces, target, w_len, wire_target):
    shape = copy.deepcopy(p_shape)
    count = 0
    tar_loc = []
    found = 0
    if target[0] - base[0] >0:
        direc = 'd'
    elif target[0] - base[0] < 0:
        direc = 'u'
    else:
        direc = 'f'
    if direc == 'f' and target[1] - base[1] <= w_len + 1:
        found = 1
        for j in range(base[1] + 1, target[1]):
            shape[base[0]][j] = 2
            count = count + 1
    else:
        if shape[target[0]][target[1] - 2] == 0:
            tar_loc = [target[0], target[1] - 1]
        if len(shape) == target[0] + 1 or shape[target[0] + 1][target[1]] == 0: #the case bottom are empty
            if direc == 'u':
                if tar_loc == []:
                    tar_loc = [target[0] + 1, target[1]]
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                if found == 0 and (p_row < rows or len(shape) > base[0] + 1): #check bot start loc
                    if len(shape) == base[0] + 1:
                        row = [0] * len(shape[0])
                        shape.append(row)
                    start_loc = [base[0] + 1, base[1]]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
            elif direc == 'd':
                if (p_row < rows or len(shape) > target[0] + 1) and tar_loc == []:
                    tar_loc = [target[0] + 1, target[1]]
                    if len(shape) == target[0] + 1:
                        row = [0] * len(shape[0])
                        shape.append(row)
                if tar_loc == []:  # cannot find target loc
                    return shapes, fronts, spaces, 0
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                if found == 0: #check bot start loc
                    start_loc = [base[0] + 1, base[1]]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
        else: #the case top are empty
            if wire_target != []:
                more_wire = 1 #leave space for the other wire
            else:
                more_wire = 0
            if direc == 'u':
                if (p_row < rows or target[0] != 0) and tar_loc == []:
                    tar_loc = [target[0] - 1, target[1]]
                    if target[0] == 0:
                        row = [0] * len(shape[0])
                        shape.insert(0, row)
                        for element in front:
                            element[0] = element[0] + 1
                if tar_loc == []: #cannot find target loc
                    return shapes, fronts, spaces, 0
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                if found == 0: #check up start loc
                    start_loc = [base[0] - 1, base[1]]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
            elif direc == 'd':
                if tar_loc == []:
                    tar_loc = [target[0] - 1, target[1]]
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                if found == 0 and (p_row < rows or base[0] != 0): #check up start loc
                    if base[0] == 0:
                        row = [0] * len(shape[0])
                        shape.insert(0, row)
                        for element in front:
                            element[0] = element[0] + 1
                    start_loc = [base[0] - 1, base[1]]
                    shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
    if found:
        all_zero1 = 1
        all_zero2 = 1
        for j in range(len(shape[0])):
            if shape[0][j] == 1:
                all_zero1 = 0
                break
        for j in range(len(shape[-1])):
            if shape[-1][j] == 1:
                all_zero2 = 0
                break
        if all_zero1:
            shape.pop(0)
            for element in front:
                element[0] = element[0] - 1
        if all_zero2:
            shape.pop(-1)
        shape, space = fill_shape(shape)
        shapes.append(shape)
        fronts.append(front)
        spaces.append(space)
    return shapes, fronts, spaces, found

def greedy_W(shape, base, start_loc, tar_loc, direc, secton, w_len, more_wire):
    current = copy.deepcopy(base)
    next = copy.deepcopy(start_loc)
    shape1 = copy.deepcopy(shape)
    shape1[start_loc[0]][start_loc[1]] = 2
    found = 0
    # if next[0] - current[0] == 1:
    #     loc = 'u'
    # elif next[0] - current[0] == -1:
    #     loc = 'd'
    # else:
    #     loc = 'r'
    if (secton == 'b' and direc == 'u') or (secton == 't' and direc == 'u' and more_wire == 1):
        wire_num = 1
        while next != tar_loc:
            dead_end = 1
            if next[0] > tar_loc[0] and ((shape[next[0] - 1][next[1] - 1] == 0 and shape[next[0] - 2][next[1]] == 0 and shape[next[0] - 1][next[1] + 1] == 0) or \
                [next[0] - 1, next[1]] == tar_loc):  # prorize up
                    current = copy.deepcopy(next)
                    next[0] = next[0] - 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'u'
                    dead_end = 0
            elif (next[0] < len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
            (next[0] == len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc:
                current = copy.deepcopy(next)
                next[1] = next[1] + 1
                shape1[next[0]][next[1]] = 2
                wire_num = wire_num + 1
                loc = 'r'
                dead_end = 0
            if dead_end:
                break
            if next == tar_loc and wire_num <= w_len:
                found = 1

    elif secton == 't' and direc == 'u' and more_wire == 0:
        wire_num = 1
        while next != tar_loc:
            dead_end = 1
            if (next[0] > 0 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
            (next[0] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or [next[0], next[1] + 1] == tar_loc: #prorize right
                current = copy.deepcopy(next)
                next[1] = next[1] + 1
                shape1[next[0]][next[1]] = 2
                wire_num = wire_num + 1
                loc = 'r'
                dead_end = 0
            elif next[0] > tar_loc[0] and next[0] > 1:
                if (shape[next[0] - 1][next[1] - 1] == 0 and shape[next[0] - 2][next[1]] == 0 and shape[next[0] - 1][next[1] + 1] == 0) or \
                [next[0] - 1, next[1]] == tar_loc:
                    current = copy.deepcopy(next)
                    next[0] = next[0] - 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'u'
                    dead_end = 0
            elif next[0] > tar_loc[0] and next[0] == 1:
                if (next[1] > 0 and shape[next[0] - 1][next[1] - 1] == 0 and shape[next[0] - 1][next[1] + 1] == 0) or \
                (next[1] == 0 and shape[next[0] - 1][next[1] + 1] == 0) or [next[0] - 1, next[1]] == tar_loc:
                    current = copy.deepcopy(next)
                    next[0] = next[0] - 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'u'
                    dead_end = 0
            if dead_end:
                break
            if next == tar_loc and wire_num <= w_len:
                found = 1
    elif secton == 't' and direc == 'd' and more_wire == 0:
        wire_num = 1
        while next != tar_loc:
            dead_end = 1
            if next[0] < tar_loc[0] and ((shape[next[0] + 1][next[1] - 1] == 0 and shape[next[0] + 2][next[1]] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or\
                [next[0] + 1,next[1]] == tar_loc): #prorize down
                    current = copy.deepcopy(next)
                    next[0] = next[0] + 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'd'
                    dead_end = 0
            elif (next[0] > 0 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
            (next[0] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or [next[0], next[1] + 1] == tar_loc:
                current = copy.deepcopy(next)
                next[1] = next[1] + 1
                shape1[next[0]][next[1]] = 2
                wire_num = wire_num + 1
                loc = 'r'
                dead_end = 0
            if dead_end:
                break
            if next == tar_loc and wire_num <= w_len:
                found = 1
    elif (secton == 'b' and direc == 'd') or (more_wire == 1 and secton == 't' and direc == 'd'):
        wire_num = 1
        while next != tar_loc:
            dead_end = 1
            if (next[0] < len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
            (next[0] == len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc: #priorize right
                current = copy.deepcopy(next)
                next[1] = next[1] + 1
                shape1[next[0]][next[1]] = 2
                wire_num = wire_num + 1
                loc = 'r'
                dead_end = 0
            elif next[0] < tar_loc[0] and next[0] + 2 < len(shape1):
                if (shape[next[0] + 1][next[1] - 1] == 0 and shape[next[0] + 2][next[1]] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
                [next[0] + 1,next[1]] == tar_loc:
                    current = copy.deepcopy(next)
                    next[0] = next[0] + 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'd'
                    dead_end = 0
            elif next[0] < tar_loc[0] and next[0] + 2 == len(shape1): #when reeach the end of the shape
                if (next[1] > 0 and shape[next[0] + 1][next[1] - 1] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
                (next[1] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or [next[0] + 1, next[1]] == tar_loc:
                    current = copy.deepcopy(next)
                    next[0] = next[0] + 1
                    shape1[next[0]][next[1]] = 2
                    wire_num = wire_num + 1
                    loc = 'd'
                    dead_end = 0
            if dead_end:
                break
            if next == tar_loc and wire_num <= w_len:
                found = 1
    return shape1, found

def fill_shape(shape):
    total = 0
    longest = 0
    for row in shape:
        if longest < len(row):
            longest = len(row)
    for row in shape:
        if len(row) < longest:
            distance = longest - len(row)
            for i in range(distance):
                row.append(0)
    for row in shape:
        for i in reversed(range(longest)):
            if row[i] != 0:
                total = total + longest - i - 1
                break
    p = total/len(shape)
    return shape, p

def feasible_placement(ori_loc, new_loc, p_shape, gate):
    legal = 1
    locs = []
    if gate == 'C':
        if new_loc[0] - 1 != -1:
            locs.append([new_loc[0] - 1, new_loc[1]])
        if new_loc[0] + 1 != len(p_shape):
            locs.append([new_loc[0] + 1, new_loc[1]])
        locs.append([new_loc[0], new_loc[1] - 1])
        locs.append([new_loc[0], new_loc[1] + 1])
        for loc in locs:
            if loc != ori_loc and loc[0] < len(p_shape) and loc[1] < len(p_shape[0]):
                if p_shape[loc[0]][loc[1]] != 0:
                    legal = 0
                    break
    return legal

def reversed_place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed, wire_targets, preds): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 2:  #place the B
                for i in range(3):
                    for j in range(base[1] - 2, base[1]):
                        new_shape1[i][j] = 1
            else:
                for i in range(3):
                    for j in range(base[1] - 2, base[1]):
                        new_shape1[base[0] - i][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 2:
                new_front.append([0, base[1] - 1]) # add two base
            else: # add two base
                new_front.append([base[0] - 2, base[1] - 1])
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            if base[0] >= 2:
                wire_targets.append([[base[0] - 2, base[1] - 2], [base[0], base[1] - 2]]) #has two wire targets
            else:
                wire_targets.append([[0, base[1] - 2], [2, base[1] - 2]])  # has two wire targets
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or base[0] >= 3): #first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] < 3:
                extra_row = 3 - base[0]
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 3:  #place the B
                for i in range(3):
                    for j in range(base[1] - 1, base[1] + 1):
                        new_shape1[i][j] = 1
            else:
                for i in range(3):
                    for j in range(base[1] - 1, base[1] + 1):
                        new_shape1[base[0] - i - 1][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 3:# add two base
                new_front.append([0, base[1]])
            else:# add two base
                new_front.append([base[0] - 3, base[1]])
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            if base[0] < 3:
                wire_targets.append([[0, base[1] - 1], [2, base[1] - 1]])
            elif base[0] >= 3:
                wire_targets.append([[base[0] - 3, base[1] - 1], [base[0] - 1, base[1] - 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 3 < len(p_shape): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(copy.deepcopy(new_row)))
            for i in range(base[0], base[0] + 3):
                for j in range(base[1] - 2, base[1]):
                    new_shape1[i][j] = 1
            new_front.append([base[0] + 2, base[1] - 1])  # add two base
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            wire_targets.append([[base[0], base[1] - 2], [base[0] + 2, base[1] - 2]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if (base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 4 < len(p_shape): #first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] + 4 >= len(p_shape):
                extra_row = base[0] + 4 - len(p_shape)
            else:
                extra_row = 0
            #base[0] = base[0] + extra_row
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0]+1, base[0] + 4):
                for j in range(base[1] - 1, base[1] + 1):
                    new_shape1[i][j] = 1
            new_front.append([base[0] + 3, base[1]])  # add two base
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            wire_targets.append([[base[0] + 1, base[1] - 1], [base[0] + 3, base[1] - 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    return shapes, fronts, spaces, new, wire_targets

def reversed_place_A(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed, wire_targets, preds): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 2:  #place the B
                for i in range(3):
                    new_shape1[i][base[1] - 1] = 1
            else:
                for i in range(3):
                    new_shape1[base[0] - i][base[1] - 1] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 2:
                new_front.append([0, base[1] - 1]) # add two base
            else: # add two base
                new_front.append([base[0] - 2, base[1] - 1])
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            if base[0] >= 2:
                wire_targets.append([[base[0] - 2, base[1] - 1], [base[0], base[1] - 1]]) #has two wire targets
            else:
                wire_targets.append([[0, base[1] - 1], [2, base[1] - 1]])  # has two wire targets
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or base[0] >= 3): #first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] < 3:
                extra_row = 3 - base[0]
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            if base[0] < 3:  #place the B
                for i in range(3):
                    new_shape1[i][base[1]] = 1
            else:
                for i in range(3):
                    new_shape1[base[0] - i - 1][base[1]] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 3:# add one base
                new_front.append([0, base[1]])
            else:# add two base
                new_front.append([base[0] - 3, base[1]])
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            if base[0] < 3:
                wire_targets.append([[0, base[1]], [2, base[1]]])
            elif base[0] >= 3:
                wire_targets.append([[base[0] - 3, base[1]], [base[0] - 1, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 3 < len(p_shape): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(copy.deepcopy(new_row)))
            for i in range(base[0], base[0] + 3):
                new_shape1[i][base[1] - 1] = 1
            new_front.append([base[0] + 2, base[1] - 1])  # add two base
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            wire_targets.append([[base[0], base[1] - 1], [base[0] + 2, base[1] - 1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if (base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or base[0] + 4 < len(p_shape): #first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            if base[0] + 4 >= len(p_shape):
                extra_row = base[0] + 4 - len(p_shape)
            else:
                extra_row = 0
            #base[0] = base[0] + extra_row
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0]+1, base[0] + 4):
                new_shape1[i][base[1]] = 1
            new_front.append([base[0] + 3, base[1]])  # add two base
            if num_succ == 2:
                new_front1.insert(c_index, new_front[0])
            wire_targets.append([[base[0] + 1, base[1]], [base[0] + 3, base[1]]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    return shapes, fronts, spaces, new, wire_targets
