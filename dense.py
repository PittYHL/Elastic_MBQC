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
    for i in range(len(newDAG)):
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
    new_map = prune_Z(new_map)
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
            if row[-1] != qubits - 1:
                if len(x_loc) == 2 and x_loc[1][0] > wires[row[-1] + 1][-1]:
                    shift = 0
                elif len(x_loc) == 1 and x_loc[0][0] > wires[row[-1] + 1][-1]:
                    shift = 0
                else:
                    shift = 1
            else:
                shift = 1
            for j in range(len(row)):
                to_be_remove = []
                loc = x_loc[j].pop(0)
                for k in range(min_x):
                    del new_map[row[j] * 2][loc]
                    del new_map[row[j] * 2][loc]
                    if shift:
                        new_map[row[j] * 2].insert(0, 'Z')
                        new_map[row[j] * 2].insert(0, 'Z')
                    # if len(x_loc[j]) != 0:
                    #     for element in x_loc[j]:
                    #         element = element - 2
                    # for l in range(len(wires[row[j]])):
                    #     if wires[row[j]][l] > start + 1:
                    #         wires[row[j]][l] = wires[row[j]][l] - 2
                    # for l in range(len(wire_group)):
                    #     if wire_group[l][row[j]] != []:
                    #         if wire_group[l][row[j]][0] > start + 1:
                    #             wire_group[l][row[j]][0] = wire_group[l][row[j]][0] - 2
                    #         if wire_group[l][row[j]][1] > start + 1:
                    #             wire_group[l][row[j]][1] = wire_group[l][row[j]][1] - 2
                    if j > 0:
                        if new_map[row[j] * 2 - 1][loc - 1] == new_map[row[j] * 2 - 1][loc] == 'Z':
                            del new_map[row[j] * 2 - 1][loc - 1]
                            del new_map[row[j] * 2 - 1][loc - 1]
                        elif new_map[row[j] * 2 - 1][loc] == new_map[row[j] * 2 - 1][loc + 1] == 'Z':
                            del new_map[row[j] * 2 - 1][loc]
                            del new_map[row[j] * 2 - 1][loc]
                        if shift:
                            new_map[row[j] * 2 - 1].insert(0, 'Z')
                            new_map[row[j] * 2 - 1].insert(0, 'Z')
            if row[0] > 0 and shift:
                for j in range(0, row[0]):
                    extra = ['Z'] * (2 * min_x)
                    new_map[j * 2] = extra + new_map[j * 2]
                    new_map[j * 2 + 1] = extra + new_map[j * 2 + 1]
            #remove the upper part
            # if row[0] != 0:
            #     for j in range(0, row[0]):
            #         if start + 1 < wires[j][0]:
            #             for k in range(min_x):
            #                 new_map[j*2].pop(0)
            #                 new_map[j * 2].pop(0)
            #                 new_map[j * 2 + 1].pop(0)
            #                 new_map[j * 2 + 1].pop(0)
            #                 for l in range(len(wires[j])):
            #                     wires[j][l] = wires[j][l] - 2
            #                 for l in range(len(wire_group)):
            #                     if wire_group[l][j]!=[]:
            #                         if wire_group[l][j][0] > start + 1:
            #                             wire_group[l][j][0] = wire_group[l][j][0] - 2
            #                         if wire_group[l][j][1] > start + 1:
            #                             wire_group[l][j][1] = wire_group[l][j][1] - 2
            #         elif start + 1 > wires[j][0]:
            #             for k in range(min_x):
            #                 new_map[j*2].pop(-1)
            #                 new_map[j * 2].pop(-1)
            #                 new_map[j * 2 + 1].pop(-1)
            #                 new_map[j * 2 + 1].pop(-1)
            # # remove the lower part
            # if row[-1] != qubits - 1:
            #     for j in range(row[-1] + 1, qubits):
            #         if start + 1 <= wires[j][0]:
            #             for k in range(min_x):
            #                 new_map[j*2].pop(0)
            #                 new_map[j * 2].pop(0)
            #                 new_map[j * 2 - 1].pop(0)
            #                 new_map[j * 2 - 1].pop(0)
            #                 for l in range(len(wires[j])):
            #                     wires[j][l] = wires[j][l] - 2
            #                 for l in range(len(wire_group)):
            #                     if wire_group[l][j]!=[]:
            #                         if wire_group[l][j][0] > start + 1:
            #                             wire_group[l][j][0] = wire_group[l][j][0] - 2
            #                         if wire_group[l][j][1] > start + 1:
            #                             wire_group[l][j][1] = wire_group[l][j][1] - 2
            #         elif start + 1 > wires[j][0]:
            #             for k in range(min_x):
            #                 new_map[j*2].pop(-1)
            #                 new_map[j * 2].pop(-1)
            #                 new_map[j * 2 - 1].pop(-1)
            #                 new_map[j * 2 - 1].pop(-1)
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

