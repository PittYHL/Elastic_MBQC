#method that make physical gates more dense
from gate_blocks import *
import copy

def dense(qubits, physical_gate):
    gates = copy.deepcopy(physical_gate)
    DAG = []
    layer = []
    layer_q = []
    # generate normal DAG
    while(len(gates)!=0):
        gate = gates.pop(0)
        type = gate['type']
        if type == 'S':
            if gate['t1'] not in layer:
                layer_q.append(gate)
                layer.append(gate['t1'])
            elif gate['t1'] in layer:
                DAG.append(layer_q)
                layer = []
                layer_q = []
                layer_q.append(gate)
                layer.append(gate['t1'])
        if type == 'D':
            if gate['t1'] not in layer and gate['t2'] not in layer:
                layer_q.append(gate)
                layer.append(gate['t1'])
                layer.append(gate['t2'])
            elif gate['t1'] in layer or gate['t2'] in layer:
                DAG.append(layer_q)
                layer = []
                layer_q = []
                layer_q.append(gate)
                layer.append(gate['t1'])
                layer.append(gate['t2'])
    DAG.append(layer_q)
    # generate dense DAG
    front_barrier = [-1]*qubits #push the front single gate
    back_barrier = [-1] * qubits #push the back single gate
    newDAG = copy.deepcopy(DAG)
    for i in range(len(newDAG)):
        for j in range(len(newDAG[i])):
            if newDAG[i][j]['type'] == 'D':
                if front_barrier[newDAG[i][j]['t1']] == -1:
                    front_barrier[newDAG[i][j]['t1']] = i
                if front_barrier[newDAG[i][j]['t2']] == -1:
                    front_barrier[newDAG[i][j]['t2']] = i
    for i in reversed(range(len(newDAG))):
        for j in range(len(newDAG[i])):
            if newDAG[i][j]['type'] == 'D':
                if back_barrier[newDAG[i][j]['t1']] == -1:
                    back_barrier[newDAG[i][j]['t1']] = i
                if back_barrier[newDAG[i][j]['t2']] == -1:
                    back_barrier[newDAG[i][j]['t2']] = i
    for i in range(qubits):
        temp_gates = []
        for j in reversed(range(front_barrier[i])):
            for gate in newDAG[j]:
                if gate['type'] == 'S' and gate['t1'] == i:
                    temp_gates.append(gate)
                    newDAG[j].remove(gate)
        index = front_barrier[i] - 1
        while len(temp_gates) != 0:
            newDAG[index].append(temp_gates.pop(0))
            index = index - 1
        temp_gates = []
        for j in range(back_barrier[i] + 1, len(newDAG)):
            for gate in newDAG[j]:
                if gate['type'] == 'S' and gate['t1'] == i:
                    temp_gates.append(gate)
                    newDAG[j].remove(gate)
        index = back_barrier[i] + 1
        while len(temp_gates) != 0:
            newDAG[index].append(temp_gates.pop(0))
            index = index + 1
    count1 = 0
    count2 = 0
    for i in range(len(DAG)):
        count1 = count1 + len(DAG[i])
        count2 = count2 + len(newDAG[i])
    for i in reversed(range(len(newDAG))):
        if newDAG[i] == []:
            newDAG.pop(i)
    if count2 != count1:
        raise Exception('check why the two DAG do not have the same gate number')
    track = []
    for layer in newDAG:
        for gate in layer:
            if gate['type'] == 'S':
                if gate['t1'] not in track:
                    track.append(gate['t1'])
            elif gate['type'] == 'D':
                if gate['t1'] not in track:
                    track.append(gate['t1'])
                if gate['t2'] not in track:
                    track.append(gate['t2'])
        for gate in layer:
            track.sort()
            gate['active'] = copy.deepcopy(track)
    for i in range(len(back_barrier)):
        for j in range(back_barrier[i]+1, len(newDAG)):
            current_active = []
            for gate in newDAG[j]:
                current_active.append(gate['t1'])
            for gate in newDAG[j]:
                if i not in current_active:
                    gate['active'].remove(i)
    #assign barrier for 2-qubit gate
    for i in range(len(newDAG)):
        for gate in newDAG[i]:
            gate['front'] = front_barrier
            gate['back'] = back_barrier
    return newDAG

def cons_new_map(n,DAG):
    map = []
    for i in range(n * 2 - 1):
        map.append([])
    for i in range(len(DAG)):
        length = 4 #record length iof the DAG layer
        for gate in DAG[i]:
            if gate['gate'] == 'CNOT':
                length = 6
        qubit = []  # record non-wire gate location
        for gate in DAG[i]:
            gate['length'] = length
            pattern, t1, t2, t3, name = de_gate(gate['gate'] + ' 0 0 ')
            if gate['type'] == 'S':
                t1 = gate['t1']
                qubit.append(t1)
                if length == 6 and (i == 0 or t1 not in DAG[i-1][0]['active']):
                    map[gate['t1'] * 2] = map[gate['t1'] * 2] + ['Z','Z'] + pattern
                elif length == 6 and (i == len(DAG) - 1 or t1 not in DAG[i+1][0]['active']):
                    map[gate['t1'] * 2] = map[gate['t1'] * 2] + pattern + ['Z', 'Z']
                else:
                    map[gate['t1']*2] = map[gate['t1']*2] + pattern
            elif gate['type'] == 'D':
                qubit.append(gate['t1'])
                qubit.append(gate['t2'])
                map[gate['t1'] * 2].extend(pattern[0])
                map[gate['t2'] * 2].extend(pattern[2])
                if gate['t1'] - gate['t2'] > 0:
                    map[gate['t1'] * 2 - 1].extend(pattern[1])
                else:
                    map[gate['t2'] * 2 - 1].extend(pattern[1])
        # add wire
        active = gate['active']
        s = set(qubit)
        temp3 = [x for x in active if x not in s]
        if temp3 != []:
            for target in temp3:
                num_wire = 0
                for j in range(int(length/2)):
                    num_wire = num_wire + 1
                    map[target*2] = map[target*2] + ['X','X']
                wire = 'I' + str(num_wire)
                DAG[i].append({'gate': wire, 'type': 'S', 't1': target, 'active': active, 'length': num_wire * 2})
        new_fill_map(n,map, gate['active'])
    return map

def new_fill_map(n,map, active):
    max = 0
    for i in range(n):
        if len(map[i*2]) > max:
            max = len(map[i*2])
    for i in active:
        if len(map[i * 2]) < max:
            map[i * 2].extend(['X'] * (max - len(map[i * 2])))
        if (i < n - 1 and len(map[i * 2 + 1]) < max):
            map[i * 2 + 1].extend(['Z'] * (max - len(map[i * 2 + 1])))
    for i in range(len(map)):
        if len(map[i]) < max:
            map[i].extend(['Z']* (max - len(map[i])))

def remove_wire(map, qubits, remove_single, remove_y):
    new_map = copy.deepcopy(map)
    fronts = []
    backs = []
    front_loc = []
    back_loc = []
    front_leaves = []#recording the leaves
    back_leaves = []
    for i in range(qubits - 1):
        for j in range(len(new_map[i])):
            if new_map[i * 2 + 1][j] != 'Z':
                fronts.append(j - 1)
                break
        for j in reversed(range(len(new_map[i]))):
            if new_map[i * 2 + 1][j] != 'Z':
                backs.append(j + 1)
                break
    front_loc.append(fronts[0])
    back_loc.append(backs[0])
    for i in range(qubits - 2):
        front_loc.append(min(fronts[i], fronts[i + 1]))
        back_loc.append(max(backs[i], backs[i + 1]))
    front_loc.append(fronts[-1])
    back_loc.append(backs[-1])
    for i in range(qubits):
        fl = []
        bl = []
        for j in range(front_loc[i] + 1):
            if new_map[i * 2][j] != 'Z':
                fl.append(new_map[i * 2].pop(j))
                new_map[i * 2].insert(j, 'Z')
        for j in range(back_loc[i], len(new_map[i * 2])):
            if new_map[i * 2][j] != 'Z':
                bl.append(new_map[i * 2].pop(j))
                new_map[i * 2].insert(j, 'Z')
        front_leaves.append(fl)
        back_leaves.append(bl)
    new_map = prune_Z(new_map)
    two_qubit_gate = []
    wires = [[] for _ in range(qubits)]
    for i in range(qubits - 1):
        temp = []
        indx = 0
        while indx <= len(new_map[i]) - 1:
            if new_map[i * 2 + 1][indx] != 'Z':
                if indx != len(new_map[i]) - 1 and new_map[i * 2 + 1][indx + 1] != 'Z':
                    temp.append(indx)
                    indx += 1
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
                else:
                    temp.append(indx)
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
            indx += 1
        two_qubit_gate.append(temp)
    double_wire = 0
    new_map = move_R(new_map)
    for i in range(qubits - 1):
        for j in two_qubit_gate[i]:
            if j != 0 and remove_single and new_map[i*2][j] != 'Y' and new_map[i*2 + 2][j] != 'Y' and \
                (new_map[i*2][j] == new_map[i*2][j - 1] == new_map[i*2 + 2][j] == new_map[i*2 + 2][j - 1] == 'X'\
                or (new_map[i*2][j] == new_map[i*2][j - 1] == 'X' and new_map[i*2 + 2][j - 1] == 'Z') or
                    (new_map[i*2 + 2][j] == new_map[i*2 + 2][j - 1] == 'X' and new_map[i*2][j - 1] == 'Z')):
                double_wire = 1
                break
            elif j != 0 and remove_single == 0 and \
                ((new_map[i*2][j - 1] == new_map[i*2][j - 2] == new_map[i*2 + 2][j - 1] == new_map[i*2 + 2][j - 2] == 'X') or (new_map[i*2][j] == 'Y'\
                and new_map[i*2 + 1][j] == 'Y'and new_map[i*2 + 2][j] == 'Y' and new_map[i*2][j - 1] == 'Y'and new_map[i*2][j - 2] == 'Y' and
                new_map[i*2][j - 3] == new_map[i*2][j - 4] == new_map[i*2 + 2][j - 1] == new_map[i*2 + 2][j - 2] == 'X') or (new_map[i*2][j] == 'Y'\
                and new_map[i*2 + 1][j] == 'Y'and new_map[i*2 + 2][j] == 'Y' and new_map[i*2 + 2][j - 1] == 'Y'and new_map[i*2 + 2][j - 2] == 'Y' and
                new_map[i*2 + 2][j - 3] == new_map[i*2 + 2][j - 4] == new_map[i*2][j - 1] == new_map[i*2][j - 2] == 'X')):
                double_wire = 1
                break
    while double_wire:
        for i in range(qubits - 1):
            for j in two_qubit_gate[i]:
                found_wire = 0
                CX = 0
                if remove_y:
                    if j != 0 and new_map[i*2][j] != 'Y' and new_map[i*2 + 2][j] != 'Y' and\
                            new_map[i * 2][j] == new_map[i * 2][j - 1] == new_map[i * 2 + 2][j] == new_map[i * 2 + 2][j - 1] == 'X':
                        up_len = check_wire_len(new_map, i * 2, j)
                        low_len = check_wire_len(new_map, i * 2 + 2, j)
                        length = min(up_len, low_len)
                        found_wire = 1
                    elif j != 0 and new_map[i*2][j] != 'Y' and new_map[i*2 + 2][j] != 'Y' and\
                        remove_single and (new_map[i * 2][j] == new_map[i * 2][j - 1] == 'X'
                        and new_map[i * 2 + 2][j - 1] == 'Z'):  # upper wire
                        length = check_wire_len(new_map, i * 2, j - 1)
                        found_wire = 1
                    elif j != 0 and new_map[i*2][j] != 'Y' and new_map[i*2 + 2][j] != 'Y' and\
                        remove_single and (new_map[i * 2 + 2][j] == new_map[i * 2 + 2][j - 1] == 'X'
                        and new_map[i * 2][j - 1] == 'Z'):  # upper wire
                        length = check_wire_len(new_map, i * 2 + 2, j - 1)
                        found_wire = 1
                    elif j != 0 and new_map[i*2][j] == 'Y'and new_map[i*2 + 1][j] == 'Y'and new_map[i*2 + 2][j] == 'Y' and\
                    new_map[i*2][j - 1] == 'Y'and new_map[i*2][j - 2] == 'Y' and\
                    new_map[i*2][j - 3] == new_map[i*2][j - 4] == new_map[i*2 + 2][j - 1] == new_map[i*2 + 2][j - 2] == 'X':
                        up_len = check_wire_len(new_map, i * 2, j - 3)
                        low_len = check_wire_len(new_map, i * 2 + 2, j - 1)
                        length = min(up_len, low_len)
                        found_wire = 1
                        CX = 1
                        for k in range(length):
                            new_map[i * 2].pop(j - length - 2)
                            new_map[i * 2 + 1].pop(j - length)
                            new_map[i * 2 + 2].pop(j - length)
                        for k in range(length):
                            new_map[i * 2].insert(j - length + 3, 'X')
                            new_map[i * 2 + 1].insert(j - length + 1, 'Z')
                            new_map[i * 2 + 2].insert(j - length + 1, 'X')
                        new_map = move_R(new_map)
                    elif j != 0 and new_map[i*2][j] == 'Y'and new_map[i*2 + 1][j] == 'Y'and new_map[i*2 + 2][j] == 'Y' and\
                    new_map[i*2 + 2][j - 1] == 'Y'and new_map[i*2 + 2][j - 2] == 'Y' and\
                    new_map[i*2 + 2][j - 3] == new_map[i*2 + 2][j - 4] == new_map[i*2][j - 1] == new_map[i*2][j - 2] == 'X':
                        up_len = check_wire_len(new_map, i * 2, j - 1)
                        low_len = check_wire_len(new_map, i * 2 + 2, j - 3)
                        length = min(up_len, low_len)
                        found_wire = 1
                        CX = 1
                        for k in range(length):
                            new_map[i * 2].pop(j - length)
                            new_map[i * 2 + 1].pop(j - length)
                            new_map[i * 2 + 2].pop(j - length - 2)
                        for k in range(length):
                            new_map[i * 2].insert(j - length + 1, 'X')
                            new_map[i * 2 + 1].insert(j - length + 1, 'Z')
                            new_map[i * 2 + 2].insert(j - length + 3, 'X')
                        new_map = move_R(new_map)
                    if found_wire and CX == 0:
                        for k in range(length):
                            new_map[i * 2].pop(j - length + 1)
                            new_map[i * 2 + 1].pop(j - length)
                            new_map[i * 2 + 2].pop(j - length + 1)
                        for k in range(length):
                            new_map[i * 2].insert(j - length + 2, 'X')
                            new_map[i * 2 + 1].insert(j - length + 2, 'Z')
                            new_map[i * 2 + 2].insert(j - length + 2, 'X')
                        new_map = move_R(new_map)
                else:
                    if j != 0 and new_map[i * 2][j - 1] == new_map[i * 2][j - 2] == new_map[i * 2 + 2][j - 1] == new_map[i * 2 + 2][j - 2] == 'X':
                        up_len = check_wire_len(new_map, i * 2, j - 1)
                        low_len = check_wire_len(new_map, i * 2 + 2, j - 1)
                        length = min(up_len, low_len)
                        found_wire = 1
                    elif j != 0 and remove_single and (new_map[i * 2][j - 1] == new_map[i * 2][j - 2] == 'X'
                        and new_map[i * 2 + 2][j - 1] == 'Z'):  # upper wire
                        length = check_wire_len(new_map, i * 2, j - 1)
                        found_wire = 1
                    elif j != 0 and remove_single and (new_map[i * 2 + 2][j - 1] == new_map[i * 2 + 2][j - 2] == 'X'
                        and new_map[i * 2][j - 1] == 'Z'):  # upper wire
                        length = check_wire_len(new_map, i * 2 + 2, j - 1)
                        found_wire = 1
                    if found_wire and CX == 0:
                        for k in range(length):
                            new_map[i * 2].pop(j - length)
                            new_map[i * 2 + 1].pop(j - length)
                            new_map[i * 2 + 2].pop(j - length)
                        for k in range(length):
                            new_map[i * 2].insert(j - length + 2, 'X')
                            new_map[i * 2 + 1].insert(j - length + 2, 'Z')
                            new_map[i * 2 + 2].insert(j - length + 2, 'X')
                        new_map = move_R(new_map)
        new_map, two_qubit_gate, double_wire = update_two_qubit(new_map, qubits, remove_single, remove_y)
    new_map = move_R2(new_map)
    new_map = put_back_leaves(new_map, front_leaves, back_leaves, qubits)
    new_map = prune_Z(new_map)
    return new_map
def new_eliminate_redundant(map, qubits):
    new_map = copy.deepcopy(map)
    two_qubit_gate = []
    for i in range(qubits - 1):
        temp = []
        indx = 0
        while indx < len(new_map[i]):
            if new_map[i*2 + 1][indx] != 'Z':
                if new_map[i*2 + 1][indx + 1] != 'Z':
                    temp.append(indx + 1)
                    indx += 1
                else:
                    temp.append(indx)
            indx += 1
        two_qubit_gate.append(temp)
    #prune outside the DAG
    front = [-1] * qubits
    back = [-1] * qubits
    front[0] = two_qubit_gate[0][0]
    back[0] = two_qubit_gate[0][-1]
    front[-1] = two_qubit_gate[-1][0]
    back[-1] = two_qubit_gate[-1][-1]
    for i in range(1, qubits - 1):
        front[i] = min(two_qubit_gate[i -1][0], two_qubit_gate[i][0])
        back[i] = max(two_qubit_gate[i - 1][-1], two_qubit_gate[i][-1])
    for i in range(qubits):
        indx = 0
        end = 1
        while end != front[i]: #remove the front X
            if (new_map[i * 2][end - 1] == new_map[i * 2][end] == 'X'):
                new_map[i * 2].pop(end - 1)
                new_map[i * 2].pop(end - 1)
                new_map[i * 2].insert(0, 'Z')
                new_map[i * 2].insert(0, 'Z')
            end = end + 1
        end = back[i] + 2
        while end != len(new_map[i]) - 2:  # remove the back X
            if (new_map[i * 2][end - 1] == new_map[i * 2][end] == 'X'):
                new_map[i * 2].pop(end - 1)
                new_map[i * 2].pop(end - 1)
                new_map[i * 2].append('Z')
                new_map[i * 2].append('Z')
            else:
                end = end + 1
    # prune the Z
    # new_map = prune_Z(new_map)

    row_len = int(len(map[0]))
    # row_len = 0
    for i in range(len(new_map)):
        new_map[i] = ['Z'] * row_len + new_map[i] + ['Z'] * row_len
    #update two qubit gate
    two_qubit_gate = []
    wires = [[] for _ in range(qubits)]
    for i in range(qubits - 1):
        temp = []
        indx = 0
        while indx < len(new_map[i]):
            if new_map[i * 2 + 1][indx] != 'Z':
                if new_map[i * 2 + 1][indx + 1] != 'Z':
                    temp.append(indx + 1)
                    indx += 1
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
                else:
                    temp.append(indx)
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
            indx += 1
        two_qubit_gate.append(temp)
    #for i in range(qubits):
    partition = []
    for wire in wires:
        wire.sort()
        partition.extend(wire)
    partition = [*set(partition)]
    partition.sort()
    wire_group = []
    for i in range(len(partition) - 1):
        start = partition[i]
        end = partition[i + 1]
        row = [] #which row to be removed
        portion = [] #the portion in each row
        for j in range(qubits):
            if len(wires[j]) == 1:
                portion.append([])
                continue
            elif start >= wires[j][-1] or end <= wires[j][0]:
                portion.append([])
                continue
            row.append(j)
            for k in range(len(wires[j]) - 1):
                if start >= wires[j][k] and end <= wires[j][k + 1]:
                    portion.append([wires[j][k], wires[j][k + 1]])
        wire_group.append(portion)
    wire_group = update_wire_group(wire_group)
    starts, ends = check_start_end(two_qubit_gate)
    for i in range(len(wire_group)):
        start = -1
        end = 10000000000
        row = [] #which row to remove
        num = 0
        for wire in wire_group[i]:
            if wire == []:
                num = num + 1
                continue
            row.append(num)
            num = num + 1
            if wire[0] > start:
                start = wire[0]
            if wire[1] < end:
                end = wire[1]
        for row_num in row:
            if wire_group[i][row_num][0] == start and wire_group[i][row_num][1] == end:
                main_row = row_num
                break
        indication = [0]*len(row) #indicate found wire
        x_loc = [[] for _ in range(len(row))] #wire location
        num_x = [0]*len(row) #number of wires found
        min_x = 10000000 #minimun wires number
        min_row = -1 #minimum x measurements row
        ind = 0
        for r in row:
            indx = wire_group[i][r][0] + 1
            while (indx < wire_group[i][r][1]):
                if new_map[r*2][indx] == new_map[r*2][indx + 1] == 'X':
                    indication[ind] = 1
                    x_loc[ind].append(indx)
                    indx = indx + 1
                indx = indx + 1
            x_loc[ind] = [*set(x_loc[ind])]
            x_loc[ind].sort(reverse=True)
            num_x[ind] = len(x_loc[ind])
            if num_x[ind]< min_x:
                min_x = num_x[ind]
                min_row = ind
            ind = ind + 1
        if (all(ele == 1 for ele in indication)): #found wire in all rows
            for j in range(len(row)):
                for k in range(min_x):
                    loc = x_loc[j].pop(0)
                    del new_map[row[j] * 2][loc]
                    del new_map[row[j] * 2][loc]
                    if len(x_loc[j]) != 0:
                        for element in x_loc[j]:
                            element = element - 2
                    for l in range(len(wires[row[j]])):
                        if wires[row[j]][l] > start + 1:
                            wires[row[j]][l] = wires[row[j]][l] - 2
                    for l in range(len(wire_group)):
                        if wire_group[l][row[j]] != []:
                            if wire_group[l][row[j]][0] > start + 1:
                                wire_group[l][row[j]][0] = wire_group[l][row[j]][0] - 2
                            if wire_group[l][row[j]][1] > start + 1:
                                wire_group[l][row[j]][1] = wire_group[l][row[j]][1] - 2
                    if j > 0:
                        if new_map[row[j] * 2 - 1][loc - 1] == new_map[row[j] * 2 - 1][loc] == 'Z':
                            del new_map[row[j] * 2 - 1][loc - 1]
                            del new_map[row[j] * 2 - 1][loc - 1]
                        elif new_map[row[j] * 2 - 1][loc] == new_map[row[j] * 2 - 1][loc + 1] == 'Z':
                            del new_map[row[j] * 2 - 1][loc]
                            del new_map[row[j] * 2 - 1][loc]
            #update starts and ends
            for j in range(len(row) - 1):
                if starts[row[j]] > start:
                    starts[row[j]] = starts[row[j]] - 2 * min_x
                if ends[row[j]] > start:
                    ends[row[j]] = ends[row[j]] - 2 * min_x
            if row[0] != 0 and start < starts[row[0] - 1]:
                for j in range(row[0]):
                    starts[j] = starts[j] - 2 * min_x
                    ends[j] = ends[j] - 2 * min_x
            if row[-1] != qubits - 1 and start < starts[row[-1]]:
                for j in range(row[-1], len(starts)):
                    starts[j] = starts[j] - 2 * min_x
                    ends[j] = ends[j] - 2 * min_x
            # remove the upper part
            if row[0] != 0:
                for j in range(0, row[0]):
                    if start < starts[row[0] - 1]:
                        for k in range(min_x):
                            new_map[j*2].pop(0)
                            new_map[j * 2].pop(0)
                            new_map[j * 2 + 1].pop(0)
                            new_map[j * 2 + 1].pop(0)
                            for l in range(len(wires[j])):
                                wires[j][l] = wires[j][l] - 2
                            for l in range(i + 1, len(wire_group)):
                                if wire_group[l][j]!=[]:
                                    # if wire_group[l][j][0] > start + 1:
                                    wire_group[l][j][0] = wire_group[l][j][0] - 2
                                    # if wire_group[l][j][1] > start + 1:
                                    wire_group[l][j][1] = wire_group[l][j][1] - 2
                    elif start >= ends[row[0] - 1]:
                        for k in range(min_x):
                            new_map[j*2].pop(-1)
                            new_map[j * 2].pop(-1)
                            new_map[j * 2 + 1].pop(-1)
                            new_map[j * 2 + 1].pop(-1)
            # remove the lower part
            if row[-1] != qubits - 1:
                for j in range(row[-1] + 1, qubits):
                    if start < starts[row[-1]]:
                        for k in range(min_x):
                            new_map[j*2].pop(0)
                            new_map[j * 2].pop(0)
                            new_map[j * 2 - 1].pop(0)
                            new_map[j * 2 - 1].pop(0)
                            for l in range(len(wires[j])):
                                wires[j][l] = wires[j][l] - 2
                            for l in range(i + 1, len(wire_group)):
                                if wire_group[l][j]!=[]:
                                    # if wire_group[l][j][0] > start + 1:
                                    wire_group[l][j][0] = wire_group[l][j][0] - 2
                                    # if wire_group[l][j][1] > start + 1:
                                    wire_group[l][j][1] = wire_group[l][j][1] - 2
                    elif start >= ends[row[-1]]:
                        for k in range(min_x):
                            new_map[j*2].pop(-1)
                            new_map[j * 2].pop(-1)
                            new_map[j * 2 - 1].pop(-1)
                            new_map[j * 2 - 1].pop(-1)
    new_map = prune_Z(new_map)
    return new_map

def prune_Z(map):
    longest = 0
    for row in map:
        if len(row) > longest:
            longest = len(row)
    for i in range(len(map)):
        if len(map[i]) < longest:
            map[i] = map[i] + ['Z'] * (longest - len(map[i]))

    end = 0
    while end < len(map[0]):
        record = [0] * len(map)
        for i in range(len(map)):
            if map[i][end] == 'Z':
                record[i] = 1
        if 0 not in record:
            for i in range(len(map)):
                map[i].pop(end)
        else:
            end = end + 1
    return map

def update_wire_group(wire_group):
    temp_wire_group = copy.deepcopy(wire_group)
    for i in range(len(temp_wire_group)):
        for j in range(i + 1, len(temp_wire_group)):
            exist = 1
            loc = []
            for k in range(len(temp_wire_group[i])):
                if temp_wire_group[i][k] != [] and temp_wire_group[i][k] != temp_wire_group[j][k]:
                    exist = 0
                elif temp_wire_group[i][k] == temp_wire_group[j][k]:
                    loc.append(k)
            if exist:
                for index in loc:
                    temp_wire_group[j][index] = []
    return temp_wire_group

def check_start_end(two_qubit_gate):
    starts = []
    ends = []
    index = 0
    for gate in two_qubit_gate:
        starts.append(gate[0])
        ends.append(gate[-1])
    return starts, ends

def remove_SW(qubits, physical_gate):
    qubits_gate = []
    for i in range(qubits):
        qubits_gate.append([])
    for gate in physical_gate:
        if gate['type'] == 'S':
            qubits_gate[gate['t1']].append(gate)
        else:
            qubits_gate[gate['t1']].append(gate)
            qubits_gate[gate['t2']].append(gate)
    front_SW = 1
    remove = []
    while front_SW: #find the removable swap
        front_SW = 0
        for i in range(qubits - 1):
            for gate1 in qubits_gate[i]:
                if gate1['type'] == 'D':
                    break
            for gate2 in qubits_gate[i + 1]:
                if gate2['type'] == 'D':
                    break
            if gate1 == gate2 and gate1['gate'] == 'SW':
                qubits_gate[i].remove(gate1)
                qubits_gate[i + 1].remove(gate1)
                remove.append(gate1)
                front_SW = 1
    new_physical_gate = copy.deepcopy(physical_gate)
    while remove != []:
        gate = remove.pop(0)
        index = new_physical_gate.index(gate)
        t1 = gate['t1']
        t2 = gate['t2']
        for i in range(index):
            if new_physical_gate[i]['type'] == 'S' and new_physical_gate[i]['t1'] == t1:
                new_physical_gate[i]['t1'] = t2
            elif new_physical_gate[i]['type'] == 'S' and new_physical_gate[i]['t1'] == t2:
                new_physical_gate[i]['t1'] = t1
        new_physical_gate.remove(gate)
    return new_physical_gate

def convert_new_map(new_map):
    newnew_map = copy.deepcopy(new_map)
    for i in range(len(newnew_map)):
        for j in range(len(newnew_map[i])):
            if newnew_map[i][j] == 'Z':
                newnew_map[i][j] = ''
    return newnew_map

def convert_new_map2(new_map):
    newnew_map = copy.deepcopy(new_map)
    for i in range(len(newnew_map)):
        for j in range(len(newnew_map[i])):
            if newnew_map[i][j] == 0:
                newnew_map[i][j] = ''
    return newnew_map

def remove_middle_part(wire_loc):
    new_wire_loc = []
    for i in range(len(wire_loc)):
        wire = []
        for j in range(len(wire_loc[i]) - 1):
            if wire_loc[i][j + 1] - wire_loc[i][j] > 1:
                wire.append([wire_loc[i][j], wire_loc[i][j + 1]])
        new_wire_loc.append(wire)
    return new_wire_loc

def check_wire_len(map, row, start):
    length = 0
    for j in range(start, -1, -2):
        if map[row][j] == map[row][j-1] == 'X':
            length = length + 2
        else:
            break
    return length

def update_two_qubit(map, qubits, remove_single, remove_y):
    for i in range(qubits):
        indx = len(map[i * 2]) - 1
        while indx != 1:
            if map[i * 2][indx] == 'Z':
                indx = indx - 1
            elif map[i * 2][indx] == map[i * 2][indx - 1] == 'X':
                map[i * 2].pop(indx - 1)
                map[i * 2].pop(indx - 1)
                map[i * 2].append('Z')
                map[i * 2].append('Z')
                indx = indx - 1
            else:
                break
    two_qubit_gate = []
    wires = [[] for _ in range(qubits)]
    for i in range(qubits - 1):
        temp = []
        indx = 0
        while indx <= len(map[i]) - 1:
            if map[i * 2 + 1][indx] != 'Z':
                if indx != len(map[i]) - 1 and map[i * 2 + 1][indx + 1] != 'Z':
                    temp.append(indx)
                    indx += 1
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
                else:
                    temp.append(indx)
                    wires[i].append(indx)
                    wires[i + 1].append(indx)
            indx += 1
        two_qubit_gate.append(temp)
    double_wire = 0
    for i in range(qubits - 1):
        for j in two_qubit_gate[i]:
            if remove_y:
                if j != 0 and remove_single and map[i*2][j] != 'Y' and map[i*2 + 2][j] != 'Y' and (
                        map[i * 2][j - 1] == map[i * 2][j - 2] == map[i * 2 + 2][j - 1] == map[i * 2 + 2][
                    j - 2] == 'X' \
                        or (map[i * 2][j - 1] == map[i * 2][j - 2] == 'X' and map[i * 2 + 2][j - 1] == 'Z') or
                        (map[i * 2 + 2][j - 1] == map[i * 2 + 2][j - 2] == 'X' and map[i * 2][j - 1] == 'Z')):
                    double_wire = 1
                    break
                elif j != 0 and remove_single == 0 and map[i*2][j] != 'Y' and map[i*2 + 2][j] != 'Y' and \
                        (map[i * 2][j - 1] == map[i * 2][j - 2] == map[i * 2 + 2][j - 1] == map[i * 2 + 2][
                            j - 2] == 'X'):
                    double_wire = 1
                    break
                elif j != 0 and \
                    ((map[i*2][j] == 'Y' and map[i*2 + 1][j] == 'Y'and map[i*2 + 2][j] == 'Y' and map[i*2][j - 1] == 'Y'and map[i*2][j - 2] == 'Y' and
                    map[i*2][j - 3] == map[i*2][j - 4] == map[i*2 + 2][j - 1] == map[i*2 + 2][j - 2] == 'X') or (map[i*2][j] == 'Y'\
                    and map[i*2 + 1][j] == 'Y'and map[i*2 + 2][j] == 'Y' and map[i*2 + 2][j - 1] == 'Y' and map[i*2 + 2][j - 2] == 'Y' and
                    map[i*2 + 2][j - 3] == map[i*2 + 2][j - 4] == map[i*2][j - 1] == map[i*2][j - 2] == 'X')):
                    double_wire = 1
                    break
            else:
                if j != 0 and remove_single and (map[i * 2][j - 1] == map[i * 2][j - 2] == map[i * 2 + 2][j - 1] == map[i * 2 + 2][j - 2] == 'X' \
                        or (map[i * 2][j - 1] == map[i * 2][j - 2] == 'X' and map[i * 2 + 2][j - 1] == 'Z') or
                        (map[i * 2 + 2][j - 1] == map[i * 2 + 2][j - 2] == 'X' and map[i * 2][j - 1] == 'Z')):
                    double_wire = 1
                    break
                elif j != 0 and remove_single == 0 and \
                    (map[i * 2][j - 1] == map[i * 2][j - 2] == map[i * 2 + 2][j - 1] == map[i * 2 + 2][j - 2] == 'X'):
                    double_wire = 1
                    break
    return map, two_qubit_gate, double_wire

def put_back_leaves(new_map, front_leaves, back_leaves, qubits):
    new_map = prune_Z(new_map)
    max_f = 0
    max_b = 0
    for i in range(len(front_leaves)):
        if len(front_leaves[i]) > max_f:
            max_f = len(front_leaves[i])
        if len(back_leaves[i]) > max_b:
            max_b = len(back_leaves[i])
    for i in range(len(new_map)):
        new_map[i] = ['Z']*max_f + new_map[i] + ['Z']*max_b
    for i in range(qubits):
        front_loc = 0
        back_loc = 0
        for j in range(len(new_map[i * 2])):
            if new_map[i * 2][j] !='Z':
                front_loc = j
                break
        for j in reversed(range(len(new_map[i * 2]))):
            if new_map[i * 2][j] !='Z':
                back_loc = j + 1
                break
        new_map[i * 2][front_loc - len(front_leaves[i]):front_loc] = front_leaves[i]
        new_map[i * 2][back_loc:back_loc + len(back_leaves[i])] = back_leaves[i]
    return new_map

def move_R(new_map):
    for i in range(len(new_map)):
        for j in range(len(new_map[i])):
            if new_map[i][j] == 'R' and new_map[i][j - 1] == new_map[i][j - 2] == 'X':
                length = check_wire_len(new_map, i, j - 1)
                new_map[i][j - length] = 'R'
                new_map[i][j] = 'X'
    return new_map

def move_R2(new_map):
    for i in range(len(new_map)):
        for j in range(len(new_map[i])):
            if new_map[i][j] == 'R' and new_map[i][j + 1] == new_map[i][j + 2] == 'X':
                length = 0
                for k in range(j + 1, len(new_map[i])):
                    if new_map[i][k] == 'X':
                        length = length + 1
                    else:
                        break
                new_map[i][j + length] = 'R'
                new_map[i][j] = 'X'
            elif j < len(new_map[i]) - 3 and new_map[i][j] == new_map[i][j + 1] == 'Y' and new_map[i][j + 2] == new_map[i][j + 3] == 'X':
                length = 0
                for k in range(j + 2, len(new_map[i])):
                    if new_map[i][k] == 'X':
                        length = length + 1
                    else:
                        break
                new_map[i][j + length:j + length+2] = ['Y','Y']
                new_map[i][j: j + 2] = ['X', 'X']
    return new_map