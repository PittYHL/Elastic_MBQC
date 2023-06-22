import copy
import networkx as nx
from matplotlib import pyplot as plt
from placement import  *

la_win = 1
keep = 4
long = 4
def DP(ori_map, qubits, rows, force_right):
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
    table, shapes, index = place_core(graph, nodes, W_len, rows, qubits, A_loc, B_loc, C_loc, force_right)
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
            if map[i][indexes[index]] != 0:
                if map[i][indexes[index] + 1] != 0 and next_0 % 2 == 0:
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
def place_core(graph, nodes, W_len, rows, qubits, A_loc, B_loc, C_loc, force_right):
    qubits = len(nodes)
    order = list(nx.topological_sort(graph))
    placed = []
    #place the first one
    table = []
    shape = []
    valid = [] #for chosen patterns
    c_layer = [] #record the current layer
    two_wire = [] #record the node with two wire predecessors
    qubit_record = []
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
    qubit_record = get_qubit_record(current, nodes, qubit_record)
    if gate == 'A':
        dep = 1
        temp_shape.append([1])
        temp_shape.append([1])
        temp_shape.append([1])
        table[0].append({'New': current, 'P': 'NA', 'row': 3, 'S': 0, 'D': dep, 'Q': 2, 'front': [[0, 0], [2, 0]], 'successor':[succ[0], succ[1]], 'targets':[], 'preds':[]})
    else:
        dep = 2
        temp_shape.append([1,1])
        temp_shape.append([1,1])
        temp_shape.append([1,1])
        table[0].append({'New': current, 'P': 'NA', 'row': 3, 'S': 0, 'D': dep, 'Q': 2, 'front': [[0, 1], [2, 1]], 'successor':[succ[0], succ[1]], 'targets':[], 'preds':[]})
    c_layer.append(current)
    f_layer = copy.deepcopy(succ) #future layer
    shape[0].append(temp_shape)
    valid[0].append(0)
    previous = current
    i = 0
    only_right = [] #record the C that only can go right (if previous two-qubit gate and later are on the same qubits)
    while nodes_left != []:
        #current version, the wires are added at the end
        next = choose_next(nodes_left, placed, graph, nodes, A_loc, B_loc, C_loc, two_wire) #chose the next
        c_qubit = find_qubits(nodes, placed, next)
        new_sucessors = list(graph.successors(next))
        loc = check_loc(nodes, placed, next, graph, two_wire)
        #c_layer = update_layer(c_layer, f_layer, next, graph)
        if next == 'B.3':
            print('g')
        next_list = place_next(next, table, shape, valid, i, rows, new_sucessors, qubits, c_qubit, loc, graph, nodes, W_len, placed, two_wire, only_right, force_right, qubit_record) #place the next node
        qubit_record = get_qubit_record(next, nodes, qubit_record)
        i = i + 1
        for j in next_list:
            nodes_left.remove(j)
            placed.append(j)
        current = next_list[-1]
    return table, shape, i
def check_loc(nodes, placed, next, graph, two_wire):
    newnext = 0
    preds = list(graph.predecessors(next))
    previous = 0
    no_pred = 0
    if next in two_wire:    #put back
        previous = next
        succs = list(graph.successors(next))
        for succ in succs:
            if succ in placed:
                newnext = succ
                break
    else:
        newnext = next
        for pred in preds:
            if pred in placed:
                previous = pred
                break
    if previous == 0: #no preds have been placed
        no_pred = 1 #no previous indication
        previous = next
        succs = list(graph.successors(next))
        for succ in succs:
            if succ in placed:
                newnext = succ
                break
    p_gate, _ = previous.split('.')
    c_gate, _ = newnext.split('.')
    if p_gate == 'A' or p_gate == 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if previous in nodes[i]:
                qubit1 = i
                break
        if newnext in nodes[qubit1]:
            loc = 'u'
        else:
            loc = 'd'
    elif c_gate == 'A' or p_gate == 'B':
        qubit1 = 0
        for i in range(len(nodes)):
            if newnext in nodes[i]:
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
        if qubit1 == len(nodes) - 1 or newnext in nodes[qubit1 - 1]:
            loc = 'u'
        else:
            loc = 'd'
    else:
        loc = 'r'
    if (next in two_wire or no_pred) and loc == 'd':
        loc = 'u'
    elif (next in two_wire or no_pred) and loc == 'u':
        loc = 'd'
    return loc

def place_next(next, table, shape, valid, p_index, rows, new_sucessors, qubits, c_qubit, loc, graph, nodes, W_len, placed, two_wire, only_right, force_right, qubit_record):
    next_list = [next]
    c_gate, gate_index = next.split('.')
    parents = [] #record parents
    fronts = []#record the new fronts
    spaces = []#record the new spaces
    shapes = [] #record the new shapes
    wire_targets = [] #for the target of wires
    new_preds = [] #for the new preds
    old_wire_targets = [] #for the old target
    old_preds = [] #for the old predecessors
    not_placed_preds = [] #for current unplaced predecessors
    end = 0
    b_end = 0
    not_placed = False #check if there is wire for the previous
    n_preds = list(graph.predecessors(next))
    for pred in n_preds:
        if pred not in placed:
            not_placed = True
            not_placed_preds.append(pred)
    if (c_gate == 'A' or c_gate == 'B') and len(new_sucessors) == 1:
        end = detec_end(next, new_sucessors[0], nodes)
        if force_right:#detect end point for forward
            p_gate1, _ = new_sucessors[0].split('.')
            if p_gate1 == 'C':
                only_right = detect_only_right(next, graph, only_right, force_right)
    if (c_gate == 'A' or c_gate == 'B') and len(new_sucessors) == 2: #detect only right(all second C will be forward)
        p_gate1, _ = new_sucessors[0].split('.')
        p_gate2, _ = new_sucessors[1].split('.')
        if p_gate1 == 'C' or p_gate2 == 'C':
            only_right = detect_only_right(next, graph, only_right, force_right)
    if (c_gate == 'A' or c_gate == 'B') and len(n_preds) == 1: #detect end point for forward
        b_end = detec_end_b(next, new_sucessors[0], nodes)
    parent = copy.deepcopy(table[p_index][0])
    successors = parent['successor']
    preds = parent['preds']
    if not_placed_preds != n_preds:
        c_index = successors.index(next)  # remove the next node from the table
        successors.pop(c_index)
    nextnext = 0
    prepre = 0
    if c_gate != 'W':
        for succ in new_sucessors:
            if succ in successors:
                nextnext = succ
            if succ not in placed:
                # successors.insert(c_index, succ)
                successors.append(succ)
        for pred in n_preds:
            if pred in preds:
                prepre = pred
    if c_gate != 'W' and nextnext == 0 and prepre == 0:
        parent_node = valid[p_index]
    elif c_gate == 'W' or nextnext != 0 or prepre != 0: #three cases: fill wire and fill the nextnext
        parent_node = list(range(len(shape[p_index])))
    if c_gate == 'C' and next in only_right:  # check if only right
        right = 1
        only_right.remove(next)
    else:
        right = 0
    for j in parent_node: #iterate all the feasible node of the parents and create new table
        parent = copy.deepcopy(table[p_index][j])
        front = parent['front']
        p_shape = shape[p_index][j]  # parent shape
        p_table = table[p_index][j]
        p_row = p_table['row']
        wire_target = parent['targets']  # for recording the current wire target
        preds = parent['preds']  # recording the current preds
        if next not in two_wire and not_placed_preds != n_preds: #forward
            base = front.pop(c_index) #start base
            next_qubit = get_next_qubit(nodes, next)
            if c_gate == 'C': #check if only right
                shapes, fronts, spaces, new, wire_targets = place_C(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces, qubits - c_qubit, wire_target, wire_targets, right, next_qubit, qubit_record)
            elif c_gate == 'A':
                shapes, fronts, spaces, new, wire_targets = place_A(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces,
                qubits - c_qubit, new_sucessors, end, not_placed, wire_targets, wire_target, next_qubit, qubit_record)
            elif c_gate == 'B':
                shapes, fronts, spaces, new, wire_targets = place_B(p_shape, base, loc, rows, p_row, front, shapes, fronts, spaces,
                qubits - c_qubit, new_sucessors, end, not_placed, wire_targets, wire_target, next_qubit, qubit_record)
            elif c_gate == 'W':
                wire_len = W_len[int(gate_index)] + 1 #for the special combination gate
                t_index = preds.index(next)
                preds.remove(next)
                target = wire_target.pop(t_index)
                shapes, fronts, spaces, new, wire_targets = place_W(p_shape, base, rows, p_row, front, shapes, fronts, spaces, target, wire_len, wire_target, wire_targets)
        else: #fbackward
            wire_target = parent['targets']
            preds = parent['preds']
            t_index = preds.index(next)
            preds.remove(next)
            base = wire_target.pop(t_index)
            if c_gate == 'A':
                shapes, fronts, spaces, new, wire_targets = reversed_place_A(p_shape, base, loc, rows, p_row, front,
                                                                    shapes, fronts, spaces, qubits - c_qubit,
                                                                    new_sucessors, wire_targets, wire_target, b_end)
            elif c_gate == 'B':
                shapes, fronts, spaces, new, wire_targets = reversed_place_B(p_shape, base, loc, rows, p_row, front,
                                                                    shapes, fronts, spaces, qubits - c_qubit,
                                                                    new_sucessors, wire_targets, wire_target, b_end)
            elif c_gate == 'C':
                shapes, fronts, spaces, new, wire_targets = reversed_place_C(p_shape, base, loc, rows,
                                                                                               p_row, front,
                                                                                               shapes, fronts, spaces,
                                                                                               qubits - c_qubit,
                                                                                               wire_targets,
                                                                                               wire_target)
        for i in range(new):
            parents.append([p_index, j])

    same_qubit = 0
    new_preds = preds + not_placed_preds
    while nextnext != 0:
        next = nextnext
        newnew_sucessors = list(graph.successors(nextnext))
        shapes, fronts, spaces, successors, nextnext, parents, same_qubit, wire_targets = fill_nextnext(shapes, fronts, spaces, successors, nextnext, newnew_sucessors, parents,
            nodes, same_qubit, wire_targets)
        if len(newnew_sucessors) == 1 and force_right:  # detect end point for forward
            p_gate1, _ = newnew_sucessors[0].split('.')
            if p_gate1 == 'C':
                only_right = detect_only_right(next, graph, only_right, force_right)
        if len(newnew_sucessors) == 2:  # detect only right(all second C will be forward)
            p_gate1, _ = newnew_sucessors[0].split('.')
            p_gate2, _ = newnew_sucessors[1].split('.')
            if p_gate1 == 'C' or p_gate2 == 'C':
                only_right = detect_only_right(next, graph, only_right, force_right)
        next_list.append(next)
    while prepre != 0:
        next = prepre
        newnew_preds = list(graph.predecessors(prepre))
        shapes, fronts, spaces, new_preds, prepre, parents, same_qubit, wire_targets = fill_prepre(
            shapes, fronts, spaces, new_preds, not_placed_preds, prepre, newnew_preds, parents,
            nodes, same_qubit, wire_targets)
        next_list.append(next)
    update(next, c_qubit, shapes, fronts, spaces, parents, table, shape, valid, successors, p_index, rows, wire_targets, new_preds, qubits)
    return next_list

def update(current, c_qubit, shapes, fronts, spaces, parents, table, shape, valid, successors, p_index, row_limit, wire_targets, new_preds, qubits):
    rows = []
    depths = []
    for i in range(len(shapes)):
        rows.append(len(shapes[i]))
        depths.append(len(shapes[i][0]))
        table[p_index + 1].append({'New': current, 'P': parents[i], 'row': len(shapes[i]), 'S': spaces[i], 'D': depths[i], 'Q': c_qubit,
        'front': fronts[i], 'successor': successors, 'targets':wire_targets[i], 'preds': new_preds})
        shape[p_index + 1].append(shapes[i])
    new_valid = check_valid(rows, depths, spaces, row_limit, c_qubit, qubits)
    valid[p_index + 1] = new_valid

def choose_next(nodes_left, placed, graph, nodes, A_loc, B_loc, C_loc, two_wire):
    next = []
    parent_index = [] #the parent of the chosen
    found_wire = 0 #choose the wire
    found_C = 0 #choose the C
    only_one = [] #the node that only one preds have been placed
    succ_placed = [] #the node that succs have been placed
    for node in nodes_left: #found all the nodes that predecessors have been resolved
        succs = list(graph.successors(node))
        before = list(graph.predecessors(node))
        p_index = 100000
        wires = 0
        gate, _ = node.split('.')
        if before != []:
            solved = 1
            pred_placed = []
            for pred in before:
                gate1, _ = pred.split('.')
                if pred in placed:
                    index = placed.index(pred)
                    pred_placed.append(pred)
                elif pred not in placed and gate1 != 'W': #if one of the predecessor is wire
                    solved = 0
                elif gate1 == 'W':
                    wires = wires + 1
                if pred in placed and p_index > index:
                    p_index = index
            if len(before) == 2 and pred_placed != [] and (before[0] in two_wire or before[1] in two_wire): #for two wire
                solved = 1
            if len(pred_placed) == 1 and len(before) == 2:
                only_one.append(node)
            elif len(pred_placed) == 0 and gate != 'W':#if none of the predecessors have been placed, look for succesor
                for succ in succs:
                    if succ in placed:
                        succ_placed.append(node)
        else:
            solved = 0
        if wires == len(before) and before != []: #both predecessors are wires and one of the sucessors is placed
            solved = 0
            if node not in two_wire:
                two_wire.append(node)
            elif len(succs) == 1:
                if wires == len(before) and succs[0] in placed:
                    found_wire = 1
                    next_node = node
                    break
            elif len(succs) == 2:
                if wires == len(before) and (succs[0] in placed or succs[0] in placed):
                    found_wire = 1
                    next_node = node
                    break
        elif solved:
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
        if parent_index != []:
            next_node = next[parent_index.index(min(parent_index))]
        elif only_one != []: # cannot find node with both predecessors resolved or wires or
            next_node = only_one[-1]
        elif succ_placed != []:
            next_node = succ_placed[0]
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

def check_valid(rows, depths, spaces, row_limit, c_qubit, qubits):
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
        # if row_collect[i] == row_limit:
        #     keep_more = 2 * keep
        if c_qubit == qubits:
            keep_more = 2 * keep
        else:
            keep_more = keep
        if len(row_collect_num[i]) > keep_more:
            c_depths = []
            c_spaces = []
            for j in row_collect_num[i]:
                c_depths.append(depths[j])
                c_spaces.append(spaces[j])
            valid = valid + rank_result(row_collect_num[i], c_depths, c_spaces, keep_more)
        else:
            valid = valid + row_collect_num[i]
    valid.sort()
    long_index = []
    for index in valid: #remove too long
        if depths[index] - min_dep >= long:
            long_index.append(index)
    for index in reversed(long_index):
        valid.remove(index)
    return valid

def rank_result(row_collect_num, c_depths, c_spaces, keep_more):
    temp_depth = copy.deepcopy(c_depths) #rank the depth
    temp_depth = list(set(temp_depth))
    temp_depth.sort()
    selected = []
    dep_group = [] #store the index of each depth
    for dep in temp_depth:
        temp_dep_group = []
        c_dep_group = []
        c_spaces_group = []
        offset = 0.01
        for i in range(len(c_depths)):
            if c_depths[i] == dep:
                c_dep_group.append(i)
                if c_spaces[i] in c_spaces_group:
                    c_spaces_group.append(c_spaces[i] + offset)
                    offset = offset + 0.01
                else:
                    c_spaces_group.append(c_spaces[i])
        temp_spaces_group = copy.deepcopy(c_spaces_group)
        temp_spaces_group.sort(reverse=True)
        for i in range(len(temp_spaces_group)):
            temp_dep_group.append(c_dep_group[c_spaces_group.index(temp_spaces_group[i])])
        dep_group = dep_group + temp_dep_group
    while(len(selected)!=keep_more):
        selected.append(row_collect_num[dep_group.pop(0)])
    selected.sort()
    return selected

def fill_nextnext(shapes, fronts, spaces, successors, nextnext, newnew_sucessors, parents, nodes, same_qubit, wire_targets):
    locs = []
    new_parents = []
    new_wire_target = []
    new_old_wire_target = []
    gate, _ = nextnext.split('.')
    #same_qubit = 0 #found node on the same qbits
    for i in range(len(successors)):
        if successors[i] == nextnext:
            locs.append(i)
    if gate == 'A':
        shapes, fronts, spaces, valid = fill_A(shapes, fronts, spaces, locs, same_qubit)
    elif gate == 'B':
        shapes, fronts, spaces, valid = fill_B(shapes, fronts, spaces, locs, same_qubit)
    same_qubit = 0 #if the next two-qubit gate has the same qubits
    if len(newnew_sucessors) == 1: #remove one front
        first_qubit = 0
        second_qubit = 0
        gate, _ = newnew_sucessors[0].split('.')
        for i in range(len(nodes)):
            if nextnext in nodes[i]:
                first_qubit = first_qubit + i
            if newnew_sucessors[0] in nodes[i]:
                second_qubit = second_qubit + i
        if gate == 'A' or gate == 'B':
            if second_qubit - first_qubit > 0:
                for front in fronts:
                    front.pop(-2)
            elif second_qubit - first_qubit < 0:
                for front in fronts:
                    front.pop(-1)
            else:
                same_qubit = 1
        else:
            if first_qubit == second_qubit * 2 + 1:
                for front in fronts:
                    front.pop(-1)
            else:
                for front in fronts:
                    front.pop(-2)

    elif len(newnew_sucessors) == 0:
        for front in fronts:
            front.pop(-1)
            front.pop(-1)
    successors.remove(nextnext)
    successors.remove(nextnext)
    nextnext = 0
    for succ in newnew_sucessors:
        if succ in successors:
            nextnext = succ
        elif same_qubit:
            nextnext = succ
            successors.append(succ)
        successors.append(succ)
    for index in valid:
        new_parents.append(parents[index])
        if wire_targets != []:
            new_wire_target.append(wire_targets[index])
    return shapes, fronts, spaces, successors, nextnext, new_parents, same_qubit, new_wire_target

def fill_A(shapes, fronts, spaces, locs, same_qubit):
    valid = []  # valid shpae after fill A
    new_shapes = []
    new_Spaces = []
    new_fronts = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        first_base = front[locs[0]]
        second_base = front[locs[1]]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]:  # rr
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit:  # constraints for rr
                valid.append(i)
                extra_column = 0
                if first_base[1] == len(shape[0]) - 1:
                    extra_column = 1
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0]][first_base[1] + 1] = 1
                shape[first_base[0] + 1][first_base[1] + 1] = 1
                shape[first_base[0] + 2][first_base[1] + 1] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 1])
                front.append([second_base[0], second_base[1] + 1])
                new_fronts.append(front)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]:  # ru
            if shapes[i][first_base[0] + 1][first_base[1]] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0]][first_base[1] + 1] = 1
                shape[first_base[0] + 1][first_base[1] + 1] = 1
                shape[first_base[0] + 2][first_base[1] + 1] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 1])
                front.append([second_base[0] - 1, second_base[1]])
                new_fronts.append(front)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]:  # dr
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                #front[locs[0]][1] = front[locs[0]][1] + 1
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1]])
                front.append([second_base[0], second_base[1] + 1])
                new_fronts.append(front)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]:  # du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]:] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1] + 1])
                front.append([second_base[0] - 1, second_base[1] + 1])
                new_fronts.append(front)
    return new_shapes, new_fronts, new_Spaces, valid

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
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
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
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 2])
                front.append([second_base[0], second_base[1] + 2])
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
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 2])
                front.append([second_base[0] - 1, second_base[1] + 1])
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
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1] + 1])
                front.append([second_base[0], second_base[1] + 2])
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
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1] + 1])
                front.append([second_base[0] - 1, second_base[1] + 1])
                new_fronts.append(front)
    return new_shapes, new_fronts, new_Spaces, valid

def fill_prepre(shapes, fronts, spaces, new_preds, not_placed_preds, prepre, newnew_preds, parents,
            nodes, same_qubit, wire_targets):
    locs = []
    new_parents = []
    new_wire_target = []
    new_fronts = []
    gate, _ = prepre.split('.')
    # same_qubit = 0 #found node on the same qbits
    for i in range(len(new_preds)):
        if new_preds[i] == prepre:
            locs.append(i)
    if gate == 'A':
        shapes, fronts, spaces, valid, wire_targets = fill_A_P(shapes, fronts, wire_targets, locs, same_qubit)
    # elif gate == 'B':
    #     shapes, fronts, spaces, valid = fill_B(shapes, fronts, spaces, locs, same_qubit)
    same_qubit = 0
    if len(newnew_preds) == 1:  # remove one front
        first_qubit = 0
        second_qubit = 0
        for i in range(len(nodes)):
            if prepre in nodes[i]:
                first_qubit = first_qubit + i
            if newnew_preds[0] in nodes[i]:
                second_qubit = second_qubit + i
        if second_qubit - first_qubit > 0:
            for front in wire_targets:
                front.pop(locs[0])
        elif second_qubit - first_qubit < 0:
            for front in wire_targets:
                front.pop(locs[1])
        else:
            same_qubit = 1
    elif len(newnew_preds) == 0:
        for front in wire_targets:
            front.pop(locs[0])
            front.pop(locs[0])
    new_preds.remove(prepre)
    new_preds.remove(prepre)
    prepre = 0
    for succ in reversed(newnew_preds):
        if succ in new_preds:
            prepre = succ
        elif same_qubit:
            prepre = succ
            new_preds.append(succ)
        new_preds.append(succ)
    for index in valid:
        new_parents.append(parents[index])
    return shapes, fronts, spaces, new_preds, prepre, new_parents, same_qubit, wire_targets

def fill_A_P(shapes, fronts, wire_targets, locs, same_qubit):
    valid = []  # valid shpae after fill A
    new_shapes = []
    new_Spaces = []
    new_preds = []
    new_fronts = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        pred = wire_targets[i]
        first_base = pred[locs[0]]
        second_base = pred[locs[1]]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]:  # ll
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit:  # constraints for rr
                valid.append(i)
                if first_base[1] == 0:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0]][first_base[1] - 1] = 1
                    shape[first_base[0] + 1][first_base[1] - 1] = 1
                    shape[first_base[0] + 2][first_base[1] - 1] = 1
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    pred[locs[0]][1] = pred[locs[0]][1] - 1 #change the locs of pre
                    pred[locs[1]][1] = pred[locs[1]][1] - 1
                    shape[first_base[0]][first_base[1]] = 1
                    shape[first_base[0] + 1][first_base[1]] = 1
                    shape[first_base[0] + 2][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_fronts.append(front)
                new_preds.append(pred)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]:  # lu
            if shapes[i][first_base[0] + 1][first_base[1]] == 0:  # constraints for ru
                valid.append(i)
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                shape[first_base[0]][first_base[1] - 1] = 1
                shape[first_base[0] + 1][first_base[1] - 1] = 1
                shape[first_base[0] + 2][first_base[1] - 1] = 1
                pred[locs[0]][1] = pred[locs[0]][1] - 1  # change the locs of pre
                pred[locs[1]][0] = pred[locs[1]][0] - 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_preds.append(pred)
                new_fronts.append(front)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]:  # dl
            if shapes[i][first_base[0] + 2][first_base[1] + 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred[locs[0]][0] = pred[locs[0]][0] + 1
                pred[locs[1]][1] = pred[locs[1]][1] - 1
                new_fronts.append(front)
                new_preds.append(pred)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]:  # du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]:] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred[locs[0]][0] = pred[locs[0]][0] + 1
                pred[locs[1]][0] = pred[locs[1]][0] - 1
                new_fronts.append(front)
                new_preds.append(pred)
    return new_shapes, new_fronts, new_Spaces, valid, new_preds

def detec_end(next, succ, nodes):
    first_qubit = 0
    second_qubit = 0
    gate, _ = succ.split('.')
    for i in range(len(nodes)):
        if next in nodes[i]:
            first_qubit = first_qubit + i
        if succ in nodes[i]:
            second_qubit = second_qubit + i
    if gate == 'A' or gate == 'B':
        if second_qubit - first_qubit < 0:
            end = 'd'
        elif second_qubit - first_qubit > 0:
            end = 'u'
    else:
        if first_qubit == second_qubit * 2 + 1:
            end = 'd'
        else:
            end = 'u'
    return end

def detec_end_b(next, pred, nodes):
    first_qubit = 0
    second_qubit = 0
    gate, _ = pred.split('.')
    for i in range(len(nodes)):
        if next in nodes[i]:
            first_qubit = first_qubit + i
        if pred in nodes[i]:
            second_qubit = second_qubit + i
    if gate == 'A' or gate == 'B':
        if second_qubit - first_qubit < 0:
            end = 'd'
        elif second_qubit - first_qubit > 0:
            end = 'u'
    else:
        if first_qubit == second_qubit * 2 + 1:
            end = 'd'
        else:
            end = 'u'
    return end
def detect_only_right(next, graph, only_right, force_right):
    sucessors = list(graph.successors(next))
    if len(sucessors) == 2:
        s1 = list(graph.successors(sucessors[0]))[0]
        s2 = list(graph.successors(sucessors[1]))[0]
        gs1, _ = s1.split('.')
        if s1 == s2 and (gs1 == 'B' or gs1 == 'C'):
            only_right.append(sucessors[0])
            only_right.append(sucessors[1])
    s1 = sucessors[0]
    gs1, _ = s1.split('.')
    while gs1 == 'C':
        s1 = list(graph.successors(s1))[0]
        gs1, _ = s1.split('.')
        if gs1 == 'C' and force_right:
            only_right.append(s1)
    if len(sucessors) == 2:
        s2 = sucessors[1]
        gs2, _ = s2.split('.')
        while gs2 == 'C':
            s2 = list(graph.successors(s2))[0]
            gs2, _ = s2.split('.')
            if gs2 == 'C' and force_right:
                only_right.append(s2)
    return only_right

def get_qubit_record(current, nodes, qubit_record):
    for i in range(len(nodes)):
        if current in nodes[i]:
            if i + 1 not in qubit_record:
                qubit_record.append(i + 1)
    return qubit_record

def get_next_qubit(nodes, next):
    c_qubit = []
    for i in range(len(nodes)):
        if next in nodes[i]:
            c_qubit.append(i + 1)
    return c_qubit

# rows = [2,3,4,5]
# c_depths = [5,4,4,3]
# c_spaces = [2,4/3,3/2,2]
# rank_result(rows, c_depths, c_spaces)
