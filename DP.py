import copy
import networkx as nx
from matplotlib import pyplot as plt

la_win = 1
keep = 3
long = 3
def DP(ori_map, qubits, rows):
    new_map = []
    for rows in ori_map:
        new_map.append([])
        for item in rows:
            if item != 'Z' and item != 'X':
                new_map[-1].append(1)
            elif item == 'X':
                new_map[-1].append(2)
            else:
                new_map[-1].append(0)
    graph, nodes, W_len, first, last = gen_index(new_map)
    place_core(graph, nodes, W_len, rows)

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

def place_core(graph, nodes, W_len, rows):
    qubits = len(nodes)
    order = list(nx.topological_sort(graph))
    placed = []
    #place the first one
    table = []
    shape = []
    chose = [] #for chosen patterns
    current_row = 3
    current_d = 0
    for i in range(len(order)):
        table.append([])
        shape.append([])
        chose.append([])
    nodes_left = copy.deepcopy(order)
    current = nodes_left.pop(0)
    placed.append(current)
    next = list(graph.successors(current))
    gate, _ = current.split('.')
    temp_shape = []
    if gate == 'A':
        dep = 1
        temp_shape.append([1])
        temp_shape.append([1])
        temp_shape.append([1])
    else:
        dep = 2
        temp_shape.append([1,1])
        temp_shape.append([1,1])
        temp_shape.append([1,1])
    # for pat in next:
    #     gate, _ = pat.split('.')
    #     if gate == 'B':
    #         LD = dep + 1
    #     else:
    #         LD = dep
    table[0].append({'Parent':'NA', 'P':'NA', 'row':3, 'S':0, 'D':dep, 'Q':2, 'front':[[2,0], [0,0]]})
    shape[0].append(temp_shape)
    chose[0].append(0)
    previous = current
    while nodes_left != []:
        #current version, the wires are added at the end
        p_index = order.index(previous) # the index of the previous pattern
        parent_node = chose[p_index]
        if len(next) == 2: #first priorize two-qubit gate, than c
            gate1, _ = next[0].split('.')
            gate2, _ = next[0].split('.')
            if gate1 == 'A' or gate1 == 'B':
                current = next[0]
                loc = 'u'
            elif gate2 == 'A' or gate2 == 'B':
                current = next[1]
                loc = 'd'
            elif gate1 == 'C':
                current = next[0]
                loc = 'u'
            elif gate2 == 'C':
                current = next[1]
                loc = 'd'
        else: # only has wire
            current = next[0]
            loc = check_loc(nodes, previous, current)
        place_next(parent_node, loc, previous, current, table, shape, chose, nodes, p_index)
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

def place_next(parent_node, loc, previous, current, table, shape, chose, nodes, p_index):
    c_gate, _ = current.split('.')
    for index in parent_node:
        c_shape = shape[p_index][index]
        c_table = table[p_index][index]
        if loc == 'd':
            base = c_table['front'][1]
        else:
            base = c_table['front'][0]
        if c_gate == 'C':
            new_shape = place_C(c_shape, c_gate, base)
        elif c_gate == 'A':
            new_shape = place_A(c_shape, c_gate, base)
        elif c_gate == 'B':
            new_shape = place_B(c_shape, c_gate, base)

def place_C(c_shape, c_gate, base): #place single node

    print('g')

def place_B(c_shape, c_gate, base): #place B node
    print('g')

def place_A(c_shape, c_gate, base): #place A node
    print('g')
