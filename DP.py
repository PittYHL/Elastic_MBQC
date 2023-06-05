import copy
import networkx as nx
from matplotlib import pyplot as plt

la_win = 1
keep = 2
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
    graph, nodes, W_len, first, last = gen_index(new_map)
    place_core(graph, nodes, W_len, rows, qubits)

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
    nodes, W_len = gen_DAG(map,s_row)
    graph = nx.DiGraph()
    for node in nodes:
        for i in range(len(node) - 1):
            graph.add_edge(node[i], node[i+1])
    nx.draw_networkx(graph)
    #order = list(nx.topological_sort(graph))
    #next = list(graph.successors('A.0'))
    return graph, nodes, W_len, first, last

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
    #C_len = [] #none wire single row length
    W_len = [] #wire single row length
    index = 0
    while index < len(indexes):
        for i in range(1, len(map)-1, 2):
            if map[i][indexes[index]] != 0:
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
                if map[i * 2][s_row[i][j] + 1] == 2:
                    node = 'W.' + str(W)
                    W = W + 1
                    loc = node_loc[i].index(s_row[i][j])
                    nodes[i].insert(loc + add, node)
                    add = add + 1
                    W_len.append(s_row[i][j + 1] - s_row[i][j] - 1)
                elif map[i * 2][s_row[i][j] + 1] != 2:
                    for k in range(s_row[i][j + 1] - s_row[i][j] - 1):
                        node = 'C.' + str(C)
                        C = C + 1
                        loc = node_loc[i].index(s_row[i][j])
                        nodes[i].insert(loc + add, node)
                        add = add + 1
                    #C_len.append(s_row[i][j + 1] -  s_row[i][j] - 1)
    return nodes, W_len

def place_core(graph, nodes, W_len, rows, qubits):
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
        next = choose_next(nodes_left, placed, graph, order) #chose the next
        c_qubit = find_qubits(nodes, placed, next)
        new_sucessors = list(graph.successors(next))
        loc = check_loc(nodes, previous, next)
        #c_layer = update_layer(c_layer, f_layer, next, graph)
        place_next(current, next, table, shape, valid, i, rows, new_sucessors, qubits, c_qubit, loc) #place the next node
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
        nodes_left.remove(next)
        placed.append(next)
        current = next
        print('g')

def check_loc(nodes, previous, current):
    p_gate, _ = previous.split('.')
    c_gate, _ = current.split('.')
    if p_gate == 'A' or 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if previous in nodes[i]:
                qubit1 = i
                break
        if current in nodes[qubit1]:
            loc = 'u'
        else:
            loc = 'd'
    elif c_gate == 'A' or 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if current in nodes[i]:
                qubit1 = i
                break
        if previous in nodes[qubit1]:
            loc = 'd'
        else:
            loc = 'u'
    else:
        loc = 'r'
    return loc

def place_next(current, next, table, shape, valid, p_index, rows, new_sucessors, qubits, c_qubit, loc):
    c_gate, _ = current.split('.')
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
        base = front.pop(c_index)
        successors.pop(c_index)
        p_shape = shape[p_index][j]
        p_table = table[p_index][j]
        p_row = p_table['row']

        if c_gate == 'C':
            new_shapes, position, fronts, spaces = place_C(p_shape, base, loc, rows, c_row)
            # c_index = order.index(current)
            # qubit = c_table['Q']
            update(new_shapes, table, shape, c_index, position, fronts, parent, qubit, spaces)
        elif c_gate == 'A':
            new_shapes, position, fronts, spaces = place_A(p_shape, base, loc, rows, c_row)
        elif c_gate == 'B':
            shapes, fronts, spaces, new = place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, qubits - c_qubit)
            for i in range(new):
                parents.append([p_index, j])
    for succ in reversed(new_sucessors):
        if succ not in successors:
            successors.insert(c_index, succ)
    update(next, c_qubit, shapes, fronts, spaces, parents, table, shape, valid, successors, p_index)

def place_C(c_shape, base, loc, rows, c_row): #place single node
    new_shape1 = copy.deepcopy(c_shape)
    new_shape2 = copy.deepcopy(c_shape)
    new_shape3 = copy.deepcopy(c_shape)
    spaces = []
    new_shapes = []
    fronts = []
    position = []
    if base[1] == len(c_shape[0]) - 1:#for front
        new_shape1[base[0]].append(1)
    else:
        new_shape1[base[0]][base[1] + 1] = 1
    new_shape1, space = fill_shape(new_shape1)
    spaces.append(space)
    new_shapes.append(new_shape1)
    position.append(0)
    fronts.append([[base[0], base[1] + 1]])
    if loc == 'u' or loc == 'r': #up
        if base[0] == 0 and c_row < rows:
            new_row = [0]*len(c_shape[0])
            new_shape2.insert(0, new_row)
            new_shape2[base[0]][base[1]] = 1
            fronts.append([[base[0], base[1]]])
        elif base[0] < len(c_shape) - 1:
            new_shape2[base[0] - 1][base[1]] = 1
            fronts.append([[base[0] - 1, base[1]]])
        new_shape2, space = fill_shape(new_shape2)
        spaces.append(space)
        new_shapes.append(new_shape2)
        position.append(1)
    elif loc == 'd' or loc == 'r': #down
        if base[0] == len(c_shape) - 1 and c_row < rows:
            new_row = [0]*len(c_shape[0])
            new_shape3.append(new_row)
            new_shape3[base[0] + 1][base[1]] = 1
            fronts.append([[base[0] + 1, base[1]]])
        elif base[0] < len(c_shape) - 1:
            new_shape3[base[0] + 1][base[1]] = 1
            fronts.append([[base[0] + 1, base[1]]])
        new_shape3, space = fill_shape(new_shape3)
        spaces.append(space)
        new_shapes.append(new_shape3)
        position.append(2)
    return new_shapes, position, fronts, spaces

def place_B(p_shape, base, loc, c_index, rows, p_row, front, shapes, fronts, spaces, extra_qubits): #place B node
    #current
    new = 0
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
    print('g')
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

def choose_next(nodes_left, placed, graph, order):
    next = []
    parent_index = [] #the parent of the chosen
    found_wire = 0 #choose the wire
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
            gate1, _ = node.split('.')
            if gate1 == 'W':
                succ = list(graph.successors(node)) #choose the wire whose succesor has been placed
                if succ[0] in placed:
                    found_wire = 1
                    next_node = node
                    break
            else:
                next.append(node)
                parent_index.append(p_index)
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
    row_collect_num = [[] for _ in range(len(row_collect))]
    for row in rows:
        index = row_collect.index(row)
        row_index.append(index)
        row_collect_num[index].append(index)
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
    return valid

def rank_result(row_collect_num, c_depths, c_spaces):
    print('g')