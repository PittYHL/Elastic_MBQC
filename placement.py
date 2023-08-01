from DP import *
import copy
import math
restrict_max = 3
def place_C(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces, extra_qubits,
            wire_target, wire_targets, right, next_qubit, qubit_record, start_p, end_p, starts, ends, avoild_points, avoid_dir): #place single node
    new = 0 #how many new node
    new_shape1 = copy.deepcopy(p_shape)
    new_shape2 = copy.deepcopy(p_shape)
    new_shape3 = copy.deepcopy(p_shape)
    new_front1 = copy.deepcopy(front)
    new_front2 = copy.deepcopy(front)
    new_front3 = copy.deepcopy(front)
    new_wire_target1 = copy.deepcopy(wire_target)
    new_wire_target2 = copy.deepcopy(wire_target)
    new_start_p1 = copy.deepcopy(start_p)
    new_end_p1 = copy.deepcopy(end_p)
    up_qubits, down_qubit, old_qubit = get_old_qubit(qubit_record, next_qubit, extra_qubits, loc)
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
    new_front1.append([base[0], base[1] + 1])
    fronts.append(new_front1)
    wire_targets.append(new_wire_target1)
    starts.append(start_p)
    ends.append(end_p)
    if (loc == 'u' or loc == 'r') and right == 0 and avoid_dir != 'u': #up
        placed = 0
        if base[0] == 0 and p_row + 1 + extra_qubits * 2<= rows:
            new = new + 1
            placed = 1
            new_row = [0]*len(p_shape[0])
            new_shape2.insert(0, new_row)
            new_shape2[base[0]][base[1]] = 1
            for element in new_front2:  # change exsisting element
                element[0] = element[0] + 1
            for element in new_wire_target2:  # change exsisting element
                element[0] = element[0] + 1
            for element in new_end_p1:
                element[0] = element[0] + 1
            for element in new_start_p1:
                element[0] = element[0] + 1
            for element in avoild_points:
                element[0] = element[0] + 1
            new_front2.append([base[0], base[1]])
        elif feasible_placement(base, [base[0] - 1, base[1]], p_shape, 'C') \
            and base[0] - 1 >= up_qubits * 2 and [base[0] - 1, base[1]] not in avoild_points:
            new = new + 1
            placed = 1
            new_shape2[base[0] - 1][base[1]] = 1
            new_front2.append([base[0] - 1, base[1]])
        if placed:
            new_shape2, space = fill_shape(new_shape2)
            spaces.append(space)
            shapes.append(new_shape2)
            fronts.append(new_front2)
            wire_targets.append(new_wire_target2)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if (loc == 'd' or loc == 'r') and right == 0 and avoid_dir != 'd': #down
        placed = 0
        if base[0] == len(p_shape) - 1 and p_row + 1 + extra_qubits * 2 <= rows:
            new = new + 1
            placed = 1
            new_row = [0]*len(p_shape[0])
            new_shape3.append(new_row)
            new_shape3[base[0] + 1][base[1]] = 1
            new_front3.append([base[0] + 1, base[1]])
        elif base[0] != len(p_shape) - 1 and feasible_placement(base, [base[0] + 1, base[1]], p_shape, 'C') \
            and len(p_shape) - base[0] - 2 >= down_qubit * 2 and [base[0] + 1, base[1]] not in avoild_points:
            new = new + 1
            placed = 1
            new_shape3[base[0] + 1][base[1]] = 1
            new_front3.append([base[0] + 1, base[1]])
        if placed:
            new_shape3, space = fill_shape(new_shape3)
            spaces.append(space)
            shapes.append(new_shape3)
            fronts.append(new_front3)
            wire_targets.append(new_wire_target2)
            starts.append(start_p)
            ends.append(end_p)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def place_B(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed,
            wire_targets, wire_target, next_qubit, qubit_record, start_p, end_p, starts, ends, new_qubit, restricted): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    up_qubits, down_qubit, old_qubit = get_old_qubit(qubit_record, next_qubit, extra_qubits, loc)
    if loc == 'u':
        if restricted and new_qubit == 0:
            qubit_row = start_p[next_qubit[0] - 1][0]
            qubit_row2 = start_p[next_qubit[1] - 1][0]
        if ((restricted and new_qubit == 0 and abs(base[0] - 2 -qubit_row) <= restrict_max) or restricted == 0 or new_qubit == 1) and \
            ((base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2 and base[0] - 2 >= up_qubits * 2)): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            new_wire_target1 = copy.deepcopy(wire_target)
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
            for element in new_wire_target1:
                element[0] = element[0] + extra_row
            for element in new_start_p1:
                element[0] = element[0] + extra_row
            for element in new_end_p1:
                element[0] = element[0] + extra_row
            if base[0] < 2:
                new_front.append([0, base[1] + 2])
                new_front.append([base[0] + extra_row, base[1] + 2])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([0, base[1] + 1])
            else:
                new_front.append([base[0] - 2, base[1] + 2])
                new_front.append([base[0], base[1] + 2])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([base[0] - 2, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.append(new_front[1])
                new_end_p1.append(new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed and base[0] < 2:
                new_wire_target1.append([0, base[1] + 1])
            elif wire_not_placed and base[0] >= 2:
                new_wire_target1.append([base[0] - 2, base[1] + 1])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] == 0) or \
            (p_shape[base[0] - 1][base[1] - 1] == 0 and p_shape[base[0] - 1][base[1]] == 0 and ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows)
            or (base[0] >= 3  and base[0] - 3 >= up_qubits * 2))): #first case: on top
            if (base[0] == 0 and len(p_shape) + 3 + extra_qubits * 2 > rows) or (restricted and new_qubit == 0 and abs(base[0] - 3 -qubit_row) > restrict_max)\
                    or (restricted and new_qubit == 0 and abs(base[0] - 1 - qubit_row2) > restrict_max):
                return shapes, fronts, spaces, new, wire_targets, starts, ends
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            for element in new_wire_target1: #change exsisting element
                element[0] = element[0] + extra_row
            for element in new_start_p1:
                element[0] = element[0] + extra_row
            for element in new_end_p1:
                element[0] = element[0] + extra_row
            if base[0] < 3:
                new_front.append([0, base[1] + 1])
                new_front.append([base[0] + extra_row - 1, base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([0, base[1]])
            else:
                new_front.append([base[0] - 3, base[1] + 1])
                new_front.append([base[0] - 1, base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([base[0] - 3, base[1]])
            if num_succ == 1 and end == 'u':
                new_front1.append(new_front[1])
                new_end_p1.append(new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed and base[0] < 3:
                new_wire_target1.append([0, base[1]])
            elif wire_not_placed and base[0] >= 3:
                new_wire_target1.append([base[0] - 3, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if loc == 'd':
        if restricted and new_qubit == 0:
            qubit_row = start_p[next_qubit[1] - 1][0]
            qubit_row2 = start_p[next_qubit[0] - 1][0]
        if ((restricted and new_qubit == 0 and abs(base[0] + 2 -qubit_row) <= restrict_max) or restricted == 0 or new_qubit == 1) \
                and ((base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or \
                (base[0] + 3 < len(p_shape) and len(p_shape) - base[0] - 3 >= down_qubit * 2)): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            new_front.append([base[0], base[1] + 2])
            new_front.append([base[0] + 2, base[1] + 2])  # add two base
            if new_qubit and wire_not_placed==False:
                new_start_p1.append([base[0] + 2, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_front1.append(new_front[1])
                new_end_p1.append(new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed:
                new_wire_target1.append([base[0] + 2, base[1] + 1])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] == len(p_shape) - 1) or (p_shape[base[0] + 1][base[1] - 1] == 0 and p_shape[base[0] + 1][base[1]] == 0\
            and ((base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) \
                 or (base[0] + 4 < len(p_shape) and len(p_shape) - base[0] - 4 >= down_qubit * 2))): #first case: on bot
            if (base[0] == len(p_shape) - 1 and len(p_shape) + 3 + extra_qubits * 2 > rows) or (restricted and new_qubit == 0 and abs(base[0] + 3 -qubit_row) > restrict_max)\
                    or (restricted and new_qubit == 0 and abs(base[0] + 1 - qubit_row2) > restrict_max):
                return shapes, fronts, spaces, new, wire_targets, starts, ends
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_front1 = copy.deepcopy(front)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            new_front.append([base[0] + 1, base[1] + 1])
            new_front.append([base[0] + 3, base[1] + 1])  # add two base
            if new_qubit and wire_not_placed==False:
                new_start_p1.append([base[0] + 3, base[1]])
            if num_succ == 1 and end == 'u':
                new_end_p1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed:
                new_wire_target1.append([base[0] + 3, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def place_B1(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed,
            wire_targets, wire_target, next_qubit, qubit_record, start_p, end_p, starts, ends, new_qubit): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    up_qubits, down_qubit, old_qubit = get_old_qubit(qubit_record, next_qubit, extra_qubits, loc)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or (base[0] >= 2 and base[0] - 2 >= up_qubits * 2): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            new_wire_target1 = copy.deepcopy(wire_target)
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
            if base[0] < 2:  #place the B
                for i in range(2):
                    for j in range(base[1], base[1] + 2):
                        new_shape1[i][j] = 1
                    new_shape1[3][base[1] + 1] = 1
            else:
                for i in range(3):
                    for j in range(base[1], base[1] + 2):
                        new_shape1[base[0] - i][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            for element in new_wire_target1:
                element[0] = element[0] + extra_row
            for element in new_start_p1:
                element[0] = element[0] + extra_row
            for element in new_end_p1:
                element[0] = element[0] + extra_row
            if base[0] < 2:
                new_front.append([0, base[1] + 1])
                new_front.append([base[0] + extra_row, base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([0, base[1]])
            else:
                new_front.append([base[0] - 2, base[1] + 1])
                new_front.append([base[0], base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([base[0] - 2, base[1]])
            if num_succ == 1 and end == 'u':
                new_front1.append(new_front[1])
                new_end_p1.append(new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed and base[0] < 2:
                new_wire_target1.append([0, base[1]])
            elif wire_not_placed and base[0] >= 2:
                new_wire_target1.append([base[0] - 2, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or \
                (base[0] + 3 < len(p_shape) and len(p_shape) - base[0] - 3 >= down_qubit * 2): # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            extra_column = 2 - len(new_shape1[0]) + base[1]
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
                for j in range(base[1], base[1] + 2):
                    new_shape1[i][j] = 1
            new_front.append([base[0], base[1] + 1])
            new_front.append([base[0] + 2, base[1] + 1])  # add two base
            if new_qubit and wire_not_placed==False:
                new_start_p1.append([base[0] + 2, base[1]])
            if num_succ == 1 and end == 'u':
                new_front1.append(new_front[1])
                new_end_p1.append(new_front[0])
            elif num_succ == 1 and end == 'd':
                new_front1.append(new_front[0])
                new_end_p1.append(new_front[1])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed:
                new_wire_target1.append([base[0] + 2, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def place_A(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors, end, wire_not_placed,
            wire_targets, wire_target, next_qubit, qubit_record, start_p, end_p, starts, ends, new_qubit, restricted): #place A node
    new = 0  # how many new node
    num_succ = len(new_sucessors)
    up_qubits, down_qubit, old_qubit = get_old_qubit(qubit_record, next_qubit, extra_qubits, loc)
    if loc == 'u':
        if restricted and new_qubit == 0:
            qubit_row = start_p[next_qubit[0] - 1][0]
            qubit_row2 = start_p[next_qubit[1] - 1][0]
            temp = abs(base[0] - 2 -qubit_row)
            temp2 = temp <= restrict_max
        if ((restricted and new_qubit == 0 and temp2) or restricted == 0 or new_qubit == 1) and ((base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or\
            (base[0] >= 2 and p_shape[base[0] - 1][base[1]] == 0 and base[0] - 2 >= up_qubits * 2 and p_shape[base[0] - 2][base[1]] == 0)):  # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            extra_column = 2 - len(new_shape1[0]) + base[1]
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            for element in new_wire_target1:  # change exsisting element
                element[0] = element[0] + extra_row
            for element in new_start_p1:
                element[0] = element[0] + extra_row
            for element in new_end_p1:
                element[0] = element[0] + extra_row
            if extra_row != 0:
                new_front.append([0, base[1] + 1])
                new_front.append([base[0] + extra_row, base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([0, base[1] + 1])
            else:
                new_front.append([base[0] - 2, base[1] + 1])
                new_front.append([base[0], base[1] + 1])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([base[0] - 2, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_end_p1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 1 and end == 'd':
                new_end_p1.append(new_front[1])
                new_front1.append(new_front[0])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed and base[0] < 2:
                new_wire_target1.append([0, base[1] + 1])
            elif wire_not_placed and base[0] >= 2:
                new_wire_target1.append([base[0] - 2, base[1] + 1])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] == 0) or (p_shape[base[0] - 1][base[1] - 1] == 0 and p_shape[base[0] - 1][base[1]] == 0\
            and ((base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or \
                 (base[0] >= 3 and base[0] - 3 >= up_qubits * 2 and p_shape[base[0] - 3][base[1]] == 0))):  # first case: on top
            if (len(p_shape) + 3 + extra_qubits * 2 > rows and base[0] == 0) or (restricted and new_qubit == 0 and abs(base[0] - 3 -qubit_row) > restrict_max)\
                    or (restricted and new_qubit == 0 and abs(base[0] - 1 - qubit_row2) > restrict_max):
                return shapes, fronts, spaces, new, wire_targets, starts, ends
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            for element in new_wire_target1:  # change exsisting element
                element[0] = element[0] + extra_row
            for element in new_start_p1:
                element[0] = element[0] + extra_row
            for element in new_end_p1:
                element[0] = element[0] + extra_row
            if extra_row != 0:
                new_front.append([0, base[1]])
                new_front.append([base[0] + extra_row - 1, base[1]])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([0, base[1]])
            else:
                new_front.append([base[0] - 3, base[1]])
                new_front.append([base[0] - 1, base[1]])  # add two base
                if new_qubit and wire_not_placed==False:
                    new_start_p1.append([base[0] - 3, base[1]])
            if num_succ == 1 and end == 'u':
                new_end_p1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 1 and end == 'd':
                new_end_p1.append(new_front[1])
                new_front1.append(new_front[0])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed and base[0] < 3:
                new_wire_target1.append([0, base[1]])
            elif wire_not_placed and base[0] >= 3:
                new_wire_target1.append([base[0] - 3, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if loc == 'd':
        if restricted and new_qubit == 0:
            qubit_row = start_p[next_qubit[1] - 1][0]
            qubit_row2 = start_p[next_qubit[1] - 1][0]
            temp = abs(base[0] + 2 -qubit_row)
            temp2 = temp <= restrict_max
        if ((restricted and new_qubit == 0 and temp2) or restricted == 0 or new_qubit == 1) \
                and ((base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or\
                (base[0] + 3 < len(p_shape) and p_shape[base[0] + 1][base[1]] == 0 and len(p_shape) - base[0] - 3 >= down_qubit * 2 and p_shape[base[0] + 2][base[1]] == 0)):  # place the one to the right
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            new_front.append([base[0], base[1] + 1])
            new_front.append([base[0] + 2, base[1] + 1])  # add two base
            if new_qubit and wire_not_placed==False:
                new_start_p1.append([base[0] + 2, base[1] + 1])
            if num_succ == 1 and end == 'u':
                new_end_p1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 1 and end == 'd':
                new_end_p1.append(new_front[1])
                new_front1.append(new_front[0])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed:
                new_wire_target1.append([base[0] + 2, base[1] + 1])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] == len(p_shape) - 1) or (p_shape[base[0] + 1][base[1] - 1] == 0 and p_shape[base[0] + 1][base[1]] == 0 and \
            ((base[0] + 4 >= len(p_shape) and p_row +base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or \
             (base[0] + 4 < len(p_shape) and len(p_shape) - base[0] - 4 >= down_qubit * 2 and p_shape[base[0] + 3][base[1]] == 0))):  # first case: on bot
            if (len(p_shape) + 3 + extra_qubits * 2 > rows and base[0] == len(p_shape) - 1) or (restricted and new_qubit == 0 and abs(base[0] + 3 - qubit_row) > restrict_max)\
                    or (restricted and new_qubit == 0 and abs(base[0] + 1 - qubit_row2) > restrict_max):
                return shapes, fronts, spaces, new, wire_targets, starts, ends
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target1 = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            new_front.append([base[0] + 1, base[1]])
            new_front.append([base[0] + 3, base[1]])  # add two base
            if new_qubit and wire_not_placed==False:
                new_start_p1.append([base[0] + 3, base[1]])
            if num_succ == 1 and end == 'u':
                new_end_p1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 1 and end == 'd':
                new_end_p1.append(new_front[1])
                new_front1.append(new_front[0])
            elif num_succ == 2 or (num_succ == 1 and end == 0):
                new_front1.append(new_front[0])
                new_front1.append(new_front[1])
            elif num_succ == 0:
                new_end_p1.append(new_front[0])
                new_end_p1.append(new_front[1])
            if wire_not_placed:
                new_wire_target1.append([base[0] + 3, base[1]])
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target1)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def place_W(p_shape, base, rows, p_row, front, shapes, fronts, spaces, target, w_len, wire_target, wire_targets, special_greedy):
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
        f_possible = check_f_possible(base, target, shape)
    if direc == 'f' and target[1] - base[1] <= w_len + 1 and f_possible:
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
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                if found == 0 and (p_row < rows or len(shape) > base[0] + 1): #check bot start loc
                    if len(shape) == base[0] + 1:
                        row = [0] * len(shape[0])
                        shape.append(row)
                    start_loc = [base[0] + 1, base[1]]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
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
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                if found == 0: #check bot start loc
                    start_loc = [base[0] + 1, base[1]]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 'b', w_len, 0)
        else: #the case top are empty
            if wire_target != []:
                more_wire = 0
                for tar in wire_target:
                    if math.fabs(tar[0] - target[0]) == 2 and tar[1] == target[1]:
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
                        for element in wire_target:
                            element[0] = element[0] + 1
                if tar_loc == []: #cannot find target loc
                    return shapes, fronts, spaces, 0
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                if found == 0: #check up start loc
                    start_loc = [base[0] - 1, base[1]]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
            elif direc == 'd':
                if tar_loc == []:
                    tar_loc = [target[0] - 1, target[1]]
                if shape[base[0]][base[1] + 2] == 0: #check right start loc
                    start_loc = [base[0], base[1] + 1]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                if found == 0 and (p_row < rows or base[0] != 0): #check up start loc
                    if base[0] == 0:
                        row = [0] * len(shape[0])
                        shape.insert(0, row)
                        for element in front:
                            element[0] = element[0] + 1
                        for element in wire_target:
                            element[0] = element[0] + 1
                    start_loc = [base[0] - 1, base[1]]
                    if special_greedy == 0:
                        shape, found = greedy_W(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
                    else:
                        shape, found = greedy_W2(shape, base, start_loc, tar_loc, direc, 't', w_len, more_wire)
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
            for element in wire_target:
                element[0] = element[0] - 1
        if all_zero2:
            shape.pop(-1)
        shape, space = fill_shape(shape)
        shapes.append(shape)
        fronts.append(front)
        spaces.append(space)
        wire_targets.append(wire_target)
    return shapes, fronts, spaces, found, wire_targets

def greedy_W(shape, base, start_loc, tar_loc, direc, secton, w_len, more_wire):
    current = copy.deepcopy(base)
    next = copy.deepcopy(start_loc)
    shape1 = copy.deepcopy(shape)
    shape1[start_loc[0]][start_loc[1]] = 2
    found = 0
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
            elif [next[0], next[1] + 1] == tar_loc or (next[0] < len(shape) - 1 and next[1] < len(shape[0]) - 2 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0
            and shape[next[0] + 1][next[1] + 1] == 0) or (next[0] == len(shape) - 1 and next[1] < len(shape[0]) - 2 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0):
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
            if next[1] < tar_loc[1] and ((next[0] > 0 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0] + 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0) or \
            (next[0] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or [next[0], next[1] + 1] == tar_loc): #prorize right
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
            elif (next[0] > 0 and shape[next[0] - 1][next[1] + 1] == 0 and next[1] < len(shape[0]) - 2 and shape[next[0]][next[1] + 2] == 0) or \
            (next[0] == 0 and next[1] < len(shape[0]) - 2 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc:
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
            if next[1] < tar_loc[1] and ((next[0] < len(shape) - 1 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or \
            (next[0] == len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc): #priorize right
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

def greedy_W2(shape, base, start_loc, tar_loc, direc, secton, w_len, more_wire):
    current = copy.deepcopy(base)
    next = copy.deepcopy(start_loc)
    shape1 = copy.deepcopy(shape)
    shape1[start_loc[0]][start_loc[1]] = 2
    found = 0
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
            elif [next[0], next[1] + 1] == tar_loc or (next[0] < len(shape) - 1 and next[1] < len(shape[0]) - 2 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0
            and shape[next[0] + 1][next[1] + 1] == 0) or (next[0] == len(shape) - 1 and next[1] < len(shape[0]) - 2 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0):
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
            if next[1] < tar_loc[1] and ((next[0] > 0 and shape[next[0]][next[1] + 2] == 0) or \
            (next[0] == 0 and shape[next[0]][next[1] + 2] == 0 and shape[next[0] + 1][next[1] + 1] == 0) or [next[0], next[1] + 1] == tar_loc): #prorize right
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
            elif (next[0] > 0 and shape[next[0] - 1][next[1] + 1] == 0 and next[1] < len(shape[0]) - 2 and shape[next[0]][next[1] + 2] == 0) or \
            (next[0] == 0 and next[1] < len(shape[0]) - 2 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc:
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
            if next[1] < tar_loc[1] and ((next[0] < len(shape) - 1 and shape[next[0]][next[1] + 2] == 0) or \
            (next[0] == len(shape) - 1 and shape[next[0] - 1][next[1] + 1] == 0 and shape[next[0]][next[1] + 2] == 0) or [next[0], next[1] + 1] == tar_loc): #priorize right
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

def reversed_place_B(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces,
    extra_qubits, new_sucessors, wire_targets, wire_target, b_end, start_p, end_p, starts, ends, n_preds): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or \
                (base[0] >= 2 and p_shape[base[0] - 1][base[1] - 3] == 0): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            extra_col = 0
            if base[1] == 0:
                base[1] = 2
                extra_col = 2
            elif base[1] == 1:
                base[1] = 2
                extra_col = 1
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            for i in range(len(new_shape1)): #insert extra colums
                new_shape1[i] = [0] * extra_col + new_shape1[i]
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
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            if base[0] < 2:
                new_front.append([0, base[1] - 1]) # add two base
            else: # add two base
                new_front.append([base[0] - 2, base[1] - 1])
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            if base[0] >= 2:
                new_wire_target.append([base[0] - 2, base[1] - 2]) #has two wire targets
                new_wire_target.append([base[0], base[1] - 2])
            else:
                new_wire_target.append([0, base[1] - 2])  # has two wire targets
                new_wire_target.append([2, base[1] - 2])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or \
                (base[0] >= 3  and p_shape[base[0] - 2][base[1] - 2] == 0): #first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            # place the one to the top
            if base[0] < 3:
                extra_row = 3 - base[0]
            else:
                extra_row = 0
            extra_col = 0
            if base[1] == 0:
                base[1] = 1
                extra_col = 1
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            for i in range(len(new_shape1)): #insert extra colums
                new_shape1[i] = [0] * extra_col + new_shape1[i]
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
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            if base[0] < 3:# add two base
                new_front.append([0, base[1]])
            else:# add two base
                new_front.append([base[0] - 3, base[1]])
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            if base[0] < 3:
                new_wire_target.append([0, base[1] - 1])
                new_wire_target.append([2, base[1] - 1])
            elif base[0] >= 3:
                new_wire_target.append([base[0] - 3, base[1] - 1])
                new_wire_target.append([base[0] - 1, base[1] - 1])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or \
                (base[0] + 3 < len(p_shape) and p_shape[base[0] + 1][base[1] - 3] == 0): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            extra_col = 0
            if base[1] == 0:
                base[1] = 2
                extra_col = 2
            elif base[1] == 1:
                base[1] = 2
                extra_col = 1
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(copy.deepcopy(new_row)))
            for i in range(len(new_shape1)): #insert extra colums
                new_shape1[i] = [0] * extra_col + new_shape1[i]
            for i in range(base[0], base[0] + 3):
                for j in range(base[1] - 2, base[1]):
                    new_shape1[i][j] = 1
            for element in new_front1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[1] = element[1] + extra_col
            new_front.append([base[0] + 2, base[1] - 1])  # add two base
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            new_wire_target.append([base[0], base[1] - 2])
            new_wire_target.append([base[0] + 2, base[1] - 2])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or \
                (base[0] + 4 < len(p_shape) and p_shape[base[0] + 2][base[1] - 2] == 0): #first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            # place the one to the top
            if base[0] + 4 >= len(p_shape):
                extra_row = base[0] + 4 - len(p_shape)
            else:
                extra_row = 0
            extra_col = 0
            if base[1] == 0:
                base[1] = 1
                extra_col = 1
            #base[0] = base[0] + extra_row
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0]+1, base[0] + 4):
                for j in range(base[1] - 1, base[1] + 1):
                    new_shape1[i][j] = 1
            for element in new_front1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[1] = element[1] + extra_col
            new_front.append([base[0] + 3, base[1]])  # add two base
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            new_wire_target.append([base[0] + 1, base[1] - 1])
            new_wire_target.append([base[0] + 3, base[1] - 1])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def reversed_place_A(p_shape, base, loc, rows, p_row, front, shapes, fronts,
                     spaces, extra_qubits, new_sucessors, wire_targets, wire_target, b_end, start_p, end_p, starts, ends, n_preds): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if (base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows) or \
                (base[0] >= 2 and p_shape[base[0] - 1][base[1] - 2] == 0): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            if base[0] < 2:
                extra_row = 2 - base[0]
            else:
                extra_row = 0
            extra_col = 0
            if base[1] == 0:
                base[1] = 1
                extra_col = 1
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, copy.deepcopy(new_row))
            for i in range(len(new_shape1)): #insert extra colums
                new_shape1[i] = [0] * extra_col + new_shape1[i]
            if base[0] < 2:  #place the B
                for i in range(3):
                    new_shape1[i][base[1] - 1] = 1
            else:
                for i in range(3):
                    new_shape1[base[0] - i][base[1] - 1] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[0] = element[0] + extra_row
                element[1] = element[1] + extra_col
            if base[0] < 2:
                new_front.append([0, base[1] - 1]) # add two base
            else: # add two base
                new_front.append([base[0] - 2, base[1] - 1])
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            if base[0] >= 2:
                new_wire_target.append([base[0] - 2, base[1] - 1]) #has two wire targets
                new_wire_target.append([base[0], base[1] - 1])
            else:
                new_wire_target.append([0, base[1] - 1])  # has two wire targets
                new_wire_target.append([2, base[1] - 1])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows) or\
                (base[0] >= 3 and p_shape[base[0] - 2][base[1] - 1] == 0): #first case: on top
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
            for element in new_wire_target: #change exsisting element
                element[0] = element[0] + extra_row
            for element in new_start_p1: #change exsisting element
                element[0] = element[0] + extra_row
            for element in new_end_p1: #change exsisting element
                element[0] = element[0] + extra_row
            if base[0] < 3:# add one base
                new_front.append([0, base[1]])
            else:# add two base
                new_front.append([base[0] - 3, base[1]])
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            if base[0] < 3:
                new_wire_target.append([0, base[1]])
                new_wire_target.append([2, base[1]])
            elif base[0] >= 3:
                new_wire_target.append([base[0] - 3, base[1]])
                new_wire_target.append([base[0] - 1, base[1]])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
    if loc == 'd':
        if (base[0] + 3 >= len(p_shape) and p_row + base[0] + 3 - len(p_shape) + extra_qubits * 2 <= rows) or\
                (base[0] + 3 < len(p_shape) and p_shape[base[0] + 1][base[1] - 2] == 0): # place the one to the left
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
            if base[0] + 3 >= len(p_shape):
                extra_row = base[0] + 3 - len(p_shape)
            else:
                extra_row = 0
            if base[1] == 0:
                base[1] = 1
                extra_col = 1
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(copy.deepcopy(new_row)))
            for i in range(len(new_shape1)): #insert extra colums
                new_shape1[i] = [0] * extra_col + new_shape1[i]
            for i in range(base[0], base[0] + 3):
                new_shape1[i][base[1] - 1] = 1
            for element in new_front1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_wire_target: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_start_p1: #change exsisting element
                element[1] = element[1] + extra_col
            for element in new_end_p1: #change exsisting element
                element[1] = element[1] + extra_col
            new_front.append([base[0] + 2, base[1] - 1])  # add two base
            if num_succ == 2:
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            new_wire_target.append([base[0], base[1] - 1])
            new_wire_target.append([base[0] + 2, base[1] - 1])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
            starts.append(new_start_p1)
            ends.append(new_end_p1)
        if (base[0] + 4 >= len(p_shape) and p_row + base[0] + 4 - len(p_shape) + extra_qubits * 2 <= rows) or \
                (base[0] + 4 < len(p_shape) and p_shape[base[0] + 2][base[1] - 1] == 0): #first case: on bot
            new_front = []
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            new_wire_target = copy.deepcopy(wire_target)
            new_start_p1 = copy.deepcopy(start_p)
            new_end_p1 = copy.deepcopy(end_p)
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
                new_front1.append(new_front[0])
            elif num_succ == 1:
                new_end_p1.append(new_front[0])
            new_wire_target.append([base[0] + 1, base[1]])
            new_wire_target.append([base[0] + 3, base[1]])
            if b_end == 'd':
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
            elif b_end == 'u':
                new_start_p1.append(new_wire_target[-2])
                new_wire_target.pop(-2)
            elif n_preds == []:
                new_start_p1.append(new_wire_target[-2])
                new_start_p1.append(new_wire_target[-1])
                new_wire_target.pop(-1)
                new_wire_target.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            wire_targets.append(new_wire_target)
            spaces.append(space)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def reversed_place_C(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces,
                     extra_qubits, wire_targets, wire_target, start_p, end_p, starts, ends):
    new = 0  # how many new node
    new_shape1 = copy.deepcopy(p_shape)
    new_shape2 = copy.deepcopy(p_shape)
    new_shape3 = copy.deepcopy(p_shape)
    new_front1 = copy.deepcopy(front)
    new_front2 = copy.deepcopy(front)
    new_front3 = copy.deepcopy(front)
    new_wire_target1 = copy.deepcopy(wire_target)
    new_wire_target2 = copy.deepcopy(wire_target)
    new_wire_target3 = copy.deepcopy(wire_target)
    new_start_p1 = copy.deepcopy(start_p)
    new_start_p2 = copy.deepcopy(start_p)
    new_end_p1 = copy.deepcopy(end_p)
    new_end_p2 = copy.deepcopy(end_p)
    # for front
    if base[1] == 0:
        for i in range(new_shape1):
            new_shape1[i].insert(0,0)
        for element in new_front1:  # change exsisting element
            element[1] = element[1] + 1
        for element in new_wire_target1:  # change exsisting element
            element[1] = element[1] + 1
        for element in new_start_p1:  # change exsisting element
            element[1] = element[1] + 1
        for element in new_end_p1:  # change exsisting element
            element[1] = element[1] + 1
        new_shape1[base[0]][base[1]] = 1
        new = new + 1
        new_shape1, space = fill_shape(new_shape1)
        spaces.append(space)
        shapes.append(new_shape1)
        new_wire_target1.append([base[0], base[1] - 1])
        wire_targets.append(new_wire_target1)
        fronts.append(new_front1)
        starts.append(new_start_p1)
        ends.append(new_end_p1)
    elif p_shape[base[0]][base[1] - 2] == 0:
        x = base[0]
        y = base[1] - 1
        new_shape1[x][y] = 1
        new_shape1[base[0]][base[1]] = 1
        new = new + 1
        new_shape1, space = fill_shape(new_shape1)
        spaces.append(space)
        shapes.append(new_shape1)
        new_wire_target1.append([base[0], base[1] - 1])
        wire_targets.append(new_wire_target1)
        fronts.append(new_front1)
        starts.append(start_p)
        ends.append(end_p)
    if loc == 'u' or loc == 'r':  # up
        placed = 0
        if base[0] == 0 and p_row + 1 + extra_qubits * 2 <= rows:
            new = new + 1
            placed = 1
            new_row = [0] * len(p_shape[0])
            new_shape2.insert(0, new_row)
            new_shape2[base[0]][base[1]] = 1
            for element in new_front2:  # change exsisting element
                element[0] = element[0] + 1
            for element in new_wire_target2:  # change exsisting element
                element[0] = element[0] + 1
            for element in new_start_p2:  # change exsisting element
                element[0] = element[0] + 1
            for element in new_end_p2:  # change exsisting element
                element[0] = element[0] + 1
            new_wire_target2.append([base[0], base[1]])
        elif feasible_placement(base, [base[0] - 1, base[1]], p_shape, 'C'):
            new = new + 1
            placed = 1
            new_shape2[base[0] - 1][base[1]] = 1
            new_wire_target2.append([base[0] - 1, base[1]])
        if placed:
            new_shape2, space = fill_shape(new_shape2)
            spaces.append(space)
            shapes.append(new_shape2)
            fronts.append(new_front2)
            wire_targets.append(new_wire_target2)
            starts.append(new_start_p2)
            ends.append(new_end_p2)
    if loc == 'd' or loc == 'r':  # down
        placed = 0
        if base[0] == len(p_shape) - 1 and p_row + 1 + extra_qubits * 2 <= rows:
            new = new + 1
            placed = 1
            new_row = [0] * len(p_shape[0])
            new_shape3.append(new_row)
            new_shape3[base[0] + 1][base[1]] = 1
            new_wire_target3.append([base[0] + 1, base[1]])
        elif base[0] != len(p_shape) - 1 and feasible_placement(base, [base[0] + 1, base[1]], p_shape, 'C'):
            new = new + 1
            placed = 1
            new_shape3[base[0] + 1][base[1]] = 1
            new_wire_target3.append([base[0] + 1, base[1]])
        if placed:
            new_shape3, space = fill_shape(new_shape3)
            spaces.append(space)
            shapes.append(new_shape3)
            fronts.append(new_front3)
            wire_targets.append(new_wire_target3)
            starts.append(start_p)
            ends.append(end_p)
    return shapes, fronts, spaces, new, wire_targets, starts, ends

def get_old_qubit(qubit_record, next_qubit, extra_qubits, loc):
    inside = 0
    for qubit in next_qubit:
        if min(qubit_record) <= qubit and max(qubit_record) >= qubit:
            inside = inside + 1
    if inside < len(next_qubit):
        return 0, 0, 0
    elif inside == len(next_qubit):
        return min(next_qubit) - min(qubit_record),  max(qubit_record) - max(next_qubit), 1

def check_f_possible(base, target, shape):
    possible = 1
    for j in range(base[1] + 1, target[1]):
        if shape[base[0]][j] != 0:
            possible = 0
            break
    return possible
