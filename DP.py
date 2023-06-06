import copy
import networkx as nx
from matplotlib import pyplot as plt

la_win = 1
keep = 3
long = 3
def DP(ori_map, qubits, rows):
    new_map = []
    for row in ori_map:
        new_map.append([])
        for item in row:
            if item != 'Z' and item != 'X':
                new_map[-1].append(1)
            elif item == 'X':
                new_map[-1].append(2)
            else:
                new_map[-1].append(0)
    graph, nodes, W_len, first, last, A_loc, B_loc, C_loc = gen_index(new_map)
    table, shapes, index = place_core(graph, nodes, W_len, rows, qubits, A_loc, B_loc, C_loc)
    print('g')

def gen_index(map):
    cut = []
    s_row = []
    for i in range(1, len(map)-1, 2):
        rowcut = []
        j = 0
        while j < len(map[0]):
            if map[i][j] != 0:
                rowcut.append(j)
                # if j + 1 < len(map[0]):
                #     if map[i][j+1] == 1:
                #         j = j + 1
            j = j + 1
        cut.append(rowcut)

    for i in range(0, len(cut) - 1):
        temp_row = cut[i] + cut[i + 1]
        temp_row.sort()
        s_row.append(copy.deepcopy(temp_row))
    s_row.insert(0, cut[0])
    s_row.append(cut[-1]) #the two qubit gate location for each row
    first = []
    last = []
    qubit = 0
    for i in range(0, len(map), 2):
        for j in range(len(map[i])):
            if map[i][j] != 0:
                front = s_row[qubit][0] - j
                break
        for j in reversed(range(len(map[i]))):
            if map[i][j] != 0:
                back = j - s_row[qubit][-1]
                break
        qubit = qubit + 1
        first.append(front) #length for the patterns in the front
        last.append(back) #length for the patterns in the back
    nodes, W_len, A_loc, B_loc, C_loc = gen_DAG(map,s_row)
    graph = nx.DiGraph()
    for node in nodes:
        for i in range(len(node) - 1):
            graph.add_edge(node[i], node[i+1])
    nx.draw_networkx(graph)
    #order = list(nx.topological_sort(graph))
    #next = list(graph.successors('A.0'))
    return graph, nodes, W_len, first, last, A_loc, B_loc, C_loc

def gen_DAG(map, s_row):
    indexes = []
    for index in s_row:
        indexes = indexes + index
    indexes = [*set(indexes)]
    indexes.sort()
    nodes = [] #graph nodes
    node_loc = []
    for i in range(len(s_row)):
        nodes.append([])
        node_loc.append([])
    A = 0
    B = 0
    C = 0
    W = 0
    A_loc = []
    B_loc = []
    C_loc = [] #none wire single row length
    W_loc = []
    W_len = [] #wire single row length
    index = 0
    while index < len(indexes):
        for i in range(1, len(map)-1, 2):
            next_0 = check_next_0(map, i, indexes[index])
            if map[i][indexes[index]] != 0 and next_0 % 2 == 0:
                if map[i][indexes[index] + 1] != 0:
                    node = 'B.' + str(B)
                    loc = int((i-1)/2)
                    nodes[loc].append(node)
                    nodes[loc + 1].append(node)
                    node_loc[loc].append(indexes[index] + 1)
                    node_loc[loc + 1].append(indexes[index] + 1)
                    B_loc.append(indexes[index])
                    B = B + 1
                elif map[i][indexes[index] - 1] == 0:
                    node = 'A.' + str(A)
                    loc = int((i - 1) / 2)
                    nodes[loc].append(node)
                    nodes[loc + 1].append(node)
                    node_loc[loc].append(indexes[index])
                    node_loc[loc + 1].append(indexes[index])
                    A_loc.append(indexes[index])
                    A =  A + 1
        index = index + 1
    for i in range(len(s_row)):
        add = 1
        for j in range(len(s_row[i]) - 1):
            if s_row[i][j + 1] - s_row[i][j] > 1:
                if map[i * 2][s_row[i][j] + 1] == 2 and s_row[i][j + 1] - s_row[i][j] > 3:
                    node = 'W.' + str(W)
                    W = W + 1
                    loc = node_loc[i].index(s_row[i][j])
                    nodes[i].insert(loc + add, node)
                    add = add + 1
                    W_len.append(s_row[i][j + 1] - s_row[i][j] - 1)
                #elif map[i * 2][s_row[i][j] + 1] != 2:
                else:
                    for k in range(s_row[i][j + 1] - s_row[i][j] - 1):
                        C_loc.append(k + s_row[i][j] + 1)
                        node = 'C.' + str(C)
                        C = C + 1
                        loc = node_loc[i].index(s_row[i][j])
                        nodes[i].insert(loc + add, node)
                        add = add + 1
                    #C_len.append(s_row[i][j + 1] -  s_row[i][j] - 1)
    return nodes, W_len, A_loc, B_loc, C_loc

def check_next_0(map, i, start):
    index = copy.deepcopy(start)
    while(map[i][index] != 0):
        index = index + 1
    return index - start
def place_core(graph, nodes, W_len, rows, qubits, A_loc, B_loc, C_loc):
    qubits = len(nodes)
    order = list(nx.topological_sort(graph))
    placed = []
    #place the first one
    table = []
    shape = []
    valid = [] #for chosen patterns
    c_layer = [] #record the current layer
    current_row = 3
    current_d = 0
    for i in range(len(order)):
        table.append([])
        shape.append([])
        valid.append([])
    nodes_left = copy.deepcopy(order)
    current = nodes_left.pop(0)
    placed.append(current)
    gate, _ = current.split('.')
    temp_shape = []
    succ = list(graph.successors(current))
    if gate == 'A':
        dep = 1
        temp_shape.append([1])
        temp_shape.append([1])
        temp_shape.append([1])
        table[0].append({'New': current, 'P': 'NA', 'row': 3, 'S': 0, 'D': dep, 'Q': 2, 'front': [[0, 0], [2, 0]], 'successor':[succ[0], succ[1]]})
    else:
        dep = 2
        temp_shape.append([1,1])
        temp_shape.append([1,1])
        temp_shape.append([1,1])
        table[0].append({'New': current, 'P': 'NA', 'row': 3, 'S': 0, 'D': dep, 'Q': 2, 'front': [[0, 1], [2, 1]], 'successor':[succ[0], succ[1]]})
    c_layer.append(current)
    f_layer = copy.deepcopy(succ) #future layer
    shape[0].append(temp_shape)
    valid[0].append(0)
    previous = current
    i = 0
    while nodes_left != []:
        #current version, the wires are added at the end
        next = choose_next(nodes_left, placed, graph, nodes, A_loc, B_loc, C_loc) #chose the next
        c_qubit = find_qubits(nodes, placed, next)
        new_sucessors = list(graph.successors(next))
        loc = check_loc(nodes, placed, next, graph)
        #c_layer = update_layer(c_layer, f_layer, next, graph)
        next_list = place_next(current, next, table, shape, valid, i, rows, new_sucessors, qubits, c_qubit, loc, graph, nodes) #place the next node
        i = i + 1
        # if len(next) == 2: #first priorize two-qubit gate, than c
        #     gate1, _ = next[0].split('.')
        #     gate2, _ = next[1].split('.')
        #     if gate1 == 'A' or gate1 == 'B':
        #         current = next[0]
        #         loc = 'u'
        #     elif gate2 == 'A' or gate2 == 'B':
        #         current = next[1]
        #         loc = 'd'
        #     elif gate1 == 'C':
        #         current = next[0]
        #         loc = 'u'
        #     elif gate2 == 'C':
        #         current = next[1]
        #         loc = 'd'
        #     else:  # only has wire
        #         current = next[0]
        #         loc = check_loc(nodes, previous, current)
        #     place_next(parent_node, loc, previous, current, table, shape, chose, nodes, p_index, rows, order)
        #     next.remove(current)
        #     gate1, _ = next[0].split('.')
        #     if gate1 == 'W':
        #         previous = current
        #         next = list(graph.successors(current))
        # else: # only has wire
        #     current = next[0]
        #     loc = check_loc(nodes, previous, current)
        #     place_next(parent_node, loc, previous, current, table, shape, chose, nodes, p_index, rows, order)
        for j in next_list:
            nodes_left.remove(j)
            placed.append(j)
        current = next_list[-1]
    return table, shape, i
def check_loc(nodes, placed, next, graph):
    preds = list(graph.predecessors(next))
    for pred in preds:
        if pred in placed:
            previous = pred
            break
    p_gate, _ = previous.split('.')
    c_gate, _ = next.split('.')
    if p_gate == 'A' or p_gate == 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if previous in nodes[i]:
                qubit1 = i
                break
        if next in nodes[qubit1]:
            loc = 'u'
        else:
            loc = 'd'
    elif c_gate == 'A' or p_gate == 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if next in nodes[i]:
                qubit1 = i
                break
        if previous in nodes[qubit1]:
            loc = 'd'
        else:
            loc = 'u'
    elif p_gate == 'C' and (c_gate == 'B' or c_gate == 'A'):
        qubit1 = 0
        for i in range(len(nodes)):
            if previous in nodes[i]:
                qubit1 = i
                break
        if qubit1 == len(nodes) - 1 or next in nodes[qubit1 - 1]:
            loc = 'u'
        else:
            loc = 'd'
    else:
        loc = 'r'
    return loc

def place_next(current, next, table, shape, valid, p_index, rows, new_sucessors, qubits, c_qubit, loc, graph, nodes):
    next_list = [next]
    c_gate, _ = next.split('.')
    parent_node = valid[p_index]
    parents = [] #record parents
    fronts = []#record the new fronts
    spaces = []#record the new spaces
    shapes = [] #record the new shapes
    for j in parent_node: #iterate all the feasible node of the parents and create new table
        parent = copy.deepcopy(table[p_index][j])
        successors = parent['successor']
        front = parent['front']
        c_index = successors.index(next) #remove the next node from the table
        base = front.pop(c_index) #start base
        successors.pop(c_index)
        p_shape = shape[p_index][j] #parent shape
        p_table = table[p_index][j]
        p_row = p_table['row']
        if c_gate == 'C':
            shapes, fronts, spaces, new = place_C(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, qubits - c_qubit)
            for i in range(new):
                parents.append([p_index, j])
        elif c_gate == 'A':
            new_shapes, position, fronts, spaces = place_A(p_shape, base, loc, rows, c_row)
        elif c_gate == 'B':
            shapes, fronts, spaces, new = place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, qubits - c_qubit, new_sucessors)
            for i in range(new):
                parents.append([p_index, j])
    nextnext = 0
    for succ in reversed(new_sucessors):
        if succ in successors:
            nextnext = succ
        successors.insert(c_index, succ)
    same_qubit = 0
    while nextnext != 0:
        next = nextnext
        newnew_sucessors = list(graph.successors(nextnext))
        shapes, fronts, spaces, successors, nextnext, parents, same_qubit = fill_nextnext(shapes, fronts, spaces, successors, nextnext, newnew_sucessors, parents, nodes, same_qubit)
        next_list.append(next)
    update(next, c_qubit, shapes, fronts, spaces, parents, table, shape, valid, successors, p_index)
    return next_list

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
        if base[0] == 0 and p_row + 1 + extra_qubits * 2 <= rows:
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

def place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits, new_sucessors): #place B node
    #current
    new = 0 #how many new node
    num_succ = len(new_sucessors)
    if loc == 'u':
        if base[0] < 2 and p_row + 2 - base[0] + extra_qubits * 2 <= rows: # place the one to the right
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 3 - len(new_shape1[0]) + base[1]
            extra_row = 2 - base[0]
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.insert(0, new_row)
            for i in range(3):
                for j in range(base[1] + 1, base[1] + 3):
                    new_shape1[i][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            new_front1.insert(c_index, [base[0] + extra_row, base[1] + 2])  # add two base
            new_front1.insert(c_index, [0, base[1] + 2])
            for i in range(2 - num_succ):
                new_front1.pop(0)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] < 3 and p_row + 3 - base[0] + extra_qubits * 2 <= rows: #first case: on top
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            extra_row = 3 - base[0]
            #base[0] = base[0] + extra_row
            if base[1] == len(new_shape1[0]) - 1: #if need extra 1 column
                for row in new_shape1:
                    row.append(0)
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row): #insert extra rows
                new_shape1.insert(0, new_row)
            for i in range(3):
                for j in range(base[1], base[1] + 2):
                    new_shape1[i][j] = 1
            for element in new_front1: #change exsisting element
                element[0] = element[0] + extra_row
            new_front1.insert(c_index, [base[0] + extra_row - 1, base[1] + 1])  # add two base
            new_front1.insert(c_index, [0, base[1] + 1])
            for i in range(2 - num_succ):
                new_front1.pop(0)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    if loc == 'd':
        if base[0] + 3 >= len(p_shape) and p_row + 2 - base[0] + extra_qubits * 2 <= rows: # place the one to the right
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            extra_column = 3 - len(new_shape1[0]) + base[1]
            extra_row = base[0] + 3 - len(p_shape)
            for i in range(len(new_shape1)):  # place extra columns
                new_shape1[i] = new_shape1[i] + [0] * extra_column
            new_row = [0] * len(new_shape1[0])
            for i in range(extra_row):  # insert extra rows
                new_shape1.append(copy.deepcopy(new_row))
            for i in range(base[0], base[0] + 3):
                for j in range(base[1] + 1, base[1] + 3):
                    new_shape1[i][j] = 1
            new_front1.insert(c_index, [base[0] + 2, base[1] + 2])  # add two base
            new_front1.insert(c_index, [base[0], base[1] + 2])
            for i in range(2 - num_succ):
                new_front1.pop(-1)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
        if base[0] + 4 >= len(p_shape) and p_row + 3 - base[0] + extra_qubits * 2 <= rows: #first case: on bot
            new = new + 1
            new_shape1 = copy.deepcopy(p_shape)
            new_front1 = copy.deepcopy(front)
            # place the one to the top
            extra_row = base[0] + 4 - len(p_shape)
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
            new_front1.insert(c_index, [base[0] + 3, base[1] + 1])  # add two base
            new_front1.insert(c_index, [base[0] + 1, base[1] + 1])
            for i in range(2 - num_succ):
                new_front1.pop(0)
            new_shape1, space = fill_shape(new_shape1)
            shapes.append(new_shape1)
            fronts.append(new_front1)
            spaces.append(space)
    return shapes, fronts, spaces, new


def place_A(c_shape, base, loc, rows, c_row): #place A node
    print('g')

def update(current, c_qubit, shapes, fronts, spaces, parents, table, shape, valid, successors, p_index):
    rows = []
    depths = []
    for i in range(len(shapes)):
        rows.append(len(shapes[i]))
        depths.append(len(shapes[i][0]))
        table[p_index + 1].append({'New': current, 'P': parents[i], 'row': len(shapes[i]), 'S': spaces[i], 'D': depths[i], 'Q': c_qubit, 'front': fronts[i], 'successor':successors})
        shape[p_index + 1].append(shapes[i])
    new_valid = check_valid(rows, depths, spaces)
    valid[p_index + 1] = new_valid
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

def choose_next(nodes_left, placed, graph, nodes, A_loc, B_loc, C_loc):
    next = []
    parent_index = [] #the parent of the chosen
    found_wire = 0 #choose the wire
    found_C = 0 #choose the C
    for node in nodes_left: #found all the nodes that don't have predecessors
        before = list(graph.predecessors(node))
        solved = 1
        p_index = 100000
        for pred in before:
            gate1, _ = pred.split('.')
            if pred in placed:
                index = placed.index(pred)
            elif pred not in placed and gate1 != 'W': #if one of the predecessor is wire
                solved = 0
            if pred in placed and p_index > index:
                p_index = index
        if solved:
            gate1, num = node.split('.')
            pred = list(graph.predecessors(node))
            gate2, _ = pred[0].split('.')
            if gate1 == 'B':
                loc = B_loc[int(num)]
            elif gate1 == 'A':
                loc = A_loc[int(num)]
            elif gate1 == 'C':
                loc = C_loc[int(num)]
            if gate1 == 'W':
                succ = list(graph.successors(node)) #choose the wire whose succesor has been placed
                if succ[0] in placed:
                    found_wire = 1
                    next_node = node
                    break
            elif gate1 == 'C' and pred[0] in placed and gate2 == 'C': #choose C if the previous is also C
                found_C = 1
                next_node = node
                break
            else:
                next.append(node)
                parent_index.append(loc)
    if found_wire != 1 and found_C != 1:
        next_node = next[parent_index.index(min(parent_index))]
    return next_node

def find_qubits(nodes, placed, next):
    qubit = []
    new_placed = placed + [next]
    for i in range(len(nodes)):
        for node in new_placed:
            if node in nodes[i]:
                qubit.append(i)
                break
    return len(qubit)

def update_layer(c_layer, f_layer, next, graph):
    c_layer.append(next)
    f_layer.remove(next)
    nextnext = list(graph.successors(next))
    for element in nextnext:
        if element not in f_layer:
            f_layer.append(element)

def check_valid(rows, depths, spaces):
    row_collect = copy.deepcopy(rows)
    row_collect = list(set(row_collect))
    row_collect.sort() #row collection
    row_index = [] #indexes of rows
    valid = []
    min_dep = min(depths)
    row_collect_num = [[] for _ in range(len(row_collect))]
    for i in range(len(rows)):
        index = row_collect.index(rows[i])
        row_index.append(index)
        row_collect_num[index].append(i)
    for i in range(len(row_collect_num)):
        if len(row_collect_num[i]) > keep:
            c_depths = []
            c_spaces = []
            for j in row_collect_num[i]:
                c_depths.append(depths[j])
                c_spaces.append(spaces[j])
            valid = valid + rank_result(row_collect_num[i], c_depths, c_spaces)
        else:
            valid = valid + row_collect_num[i]
    valid.sort()
    for index in valid: #remove too long
        if depths[index] - min_dep >= long:
            valid.remove(index)
    return valid

def rank_result(row_collect_num, c_depths, c_spaces):
    temp_depth = copy.deepcopy(c_depths) #rank the depth
    temp_depth = list(set(temp_depth))
    temp_depth.sort()
    selected = []
    dep_group = [] #store the index of each depth
    for dep in temp_depth:
        temp_dep_group = []
        c_dep_group = []
        c_spaces_group = []
        for i in range(len(c_depths)):
            if c_depths[i] == dep:
                c_dep_group.append(i)
                if c_spaces[i] in c_spaces_group:
                    c_spaces_group.append(c_spaces[i] + 0.01)
                else:
                    c_spaces_group.append(c_spaces[i])
        temp_spaces_group = copy.deepcopy(c_spaces_group)
        temp_spaces_group.sort(reverse=True)
        for i in range(len(temp_spaces_group)):
            temp_dep_group.append(c_dep_group[c_spaces_group.index(temp_spaces_group[i])])
        dep_group = dep_group + temp_dep_group
    while(len(selected)!=keep):
        selected.append(row_collect_num[dep_group.pop(0)])
    selected.sort()
    return selected

def feasible_placement(ori_loc, new_loc, p_shape, gate):
    legal = 1
    locs = []
    if gate == 'C':
        locs.append([new_loc[0] - 1, new_loc[1]])
        locs.append([new_loc[0] + 1, new_loc[1]])
        locs.append([new_loc[0], new_loc[1] - 1])
        locs.append([new_loc[0], new_loc[1] + 1])
        for loc in locs:
            if loc != ori_loc and loc[0] < len(p_shape) and loc[1] < len(p_shape[0]):
                if p_shape[loc[0]][loc[1]] != 0:
                    legal = 0
                    break
    return legal

def fill_nextnext(shapes, fronts, spaces, successors, nextnext, newnew_sucessors, parents, nodes, same_qubit):
    locs = []
    new_parents = []
    gate, _ = nextnext.split('.')
    #same_qubit = 0 #found node on the same qbits
    for i in range(len(successors)):
        if successors[i] == nextnext:
            locs.append(i)
    if gate == 'A':
        shapes, fronts, spaces, valid = fill_A(shapes, fronts, spaces, locs, same_qubit)
    elif gate == 'B':
        shapes, fronts, spaces, valid = fill_B(shapes, fronts, spaces, locs, same_qubit)
    same_qubit = 0
    if len(newnew_sucessors) == 1: #remove one front
        first_qubit = 0
        second_qubit = 0
        for i in range(len(nodes)):
            if nextnext in nodes[i]:
                first_qubit = first_qubit + i
            if newnew_sucessors[0] in nodes[i]:
                second_qubit = second_qubit + i
        if second_qubit - first_qubit > 0:
            for front in fronts:
                front.pop(locs[0])
        elif second_qubit - first_qubit < 0:
            for front in fronts:
                front.pop(locs[1])
        else:
            same_qubit = 1
    elif len(newnew_sucessors) == 0:
        for front in fronts:
            front.pop(locs[0])
            front.pop(locs[0])
    successors.remove(nextnext)
    successors.remove(nextnext)
    nextnext = 0
    for succ in reversed(newnew_sucessors):
        if succ in successors:
            nextnext = succ
        elif same_qubit:
            nextnext = succ
            successors.insert(locs[0], succ)
        successors.insert(locs[0], succ)
    for index in valid:
        new_parents.append(parents[index])
    return shapes, fronts, spaces, successors, nextnext, new_parents, same_qubit

def fill_A(shapes, fronts, spaces, locs):
    print('g')

def fill_B(shapes, fronts, spaces, locs, same_qubit): #may need to add more cases
    valid = [] #valid shpae after fill B
    new_shapes = []
    new_Spaces = []
    new_fronts = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        first_base = front[locs[0]]
        second_base = front[locs[1]]
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]: #rr
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit: #constraints for rr
                valid.append(i)
                extra_column = first_base[1] + 3 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0]*extra_column
                shape[first_base[0]][first_base[1] + 1: first_base[1] + 3] = [1,1]
                shape[first_base[0] + 1][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 2][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front[locs[0]][1] = front[locs[0]][1] + 2
                front[locs[1]][1] = front[locs[1]][1] + 2
                new_fronts.append(front)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]: #ru
            if shapes[i][first_base[0] + 1][first_base[1]] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 3 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0]][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 1][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 2][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front[locs[0]][1] = front[locs[0]][1] + 2
                front[locs[1]][0] = front[locs[1]][0] - 1
                front[locs[1]][1] = front[locs[1]][1] + 1
                new_fronts.append(front)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]: #dr
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 2 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0] + 1][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 2][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 3][first_base[1]: first_base[1] + 2] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front[locs[0]][1] = front[locs[0]][1] + 1
                front[locs[0]][0] = front[locs[0]][0] + 1
                front[locs[1]][1] = front[locs[1]][1] + 2
                new_fronts.append(front)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]: #du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 2 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0] + 1][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 2][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 3][first_base[1]: first_base[1] + 2] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front[locs[0]][1] = front[locs[0]][1] + 1
                front[locs[0]][0] = front[locs[0]][0] + 1
                front[locs[1]][1] = front[locs[1]][1] + 1
                front[locs[1]][0] = front[locs[1]][0] - 1
                new_fronts.append(front)
    return new_shapes, new_fronts, new_Spaces, valid

# rows = [2,3,4,5]
# c_depths = [5,4,4,3]
# c_spaces = [2,4/3,3/2,2]
# rank_result(rows, c_depths, c_spaces)
