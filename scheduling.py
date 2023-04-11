import numpy as np
import math
from gate_blocks import *
from new_swap import *
from dense import *
import copy
from dense import *
physical_gate = []
tracker= []
map = []
def scheduling(n,DAG, rows):
    extra_row = rows - 2 * n + 1
    print("widest width is:" + str((n-1) * 3 + 2))
    depth = 0
    for i in range(len(DAG)):
        length = 4  # record length iof the DAG layer
        for gate in DAG[i]:
            if gate['gate'] == 'CNOT':
                length = 6
        depth = depth + length
    print("shortest depth is:" + str(depth - len(DAG) + 1))
    if (extra_row < 0):
        print("illegal row number")
    qubit_range = []
    for i in range(n):
        interval = [i*2, rows - (n - i - 1)*2 - 1]
        current = []
        for j in range(interval[0], interval[1] + 1):
            current.append(j)
        qubit_range.append(current)

    front_DAG = []
    middle_DAG = []
    back_DAG = []
    #create three DAG
    for i in range(len(DAG)):
        front_DAG.append([])
        middle_DAG.append([])
        back_DAG.append([])
        for gate in DAG[i]:
            if gate['gate'] == 'I1' or gate['gate'] == 'I2' or gate['gate'] == 'I3':
                middle_DAG[i].append(gate)
            elif gate['type'] == 'S' and i < gate['front'][gate['t1']]:
                front_DAG[i].append(gate)
            elif gate['type'] == 'S' and i > gate['front'][gate['t1']] and i < gate['back'][gate['t1']]:
                middle_DAG[i].append(gate)
            elif gate['type'] == 'S' and i > gate['back'][gate['t1']]:
                back_DAG[i].append(gate)
            elif gate['type'] == 'D':
                middle_DAG[i].append(gate)
    #if rows >= 3 * (n - 1) + 2:
    #    map = placement2(rows, n, DAG, front_DAG, middle_DAG, qubit_range)
    #else:
    if rows >= 3 * (n - 1) + 2:
        full = True
    else:
        full = False
    map, front_loc, front_length, _ =search_mid(rows, n, DAG, back_DAG, middle_DAG, qubit_range, True, full)
    fill_front(map, front_loc, front_DAG, front_length, qubit_range)
    return map

def search_mid(rows, n, DAG, back_DAG, middle_DAG, qubit_range, sche, full):
    front_loc = [] #record front layer location
    map = []
    qubit_loc = []
    for i in range(rows):
        map.append(['Z']*(4))
    active_qubit = []
    gate_list = []  # for all the mid gates
    mid_length = 0  # count how long is mid
    qubits = len(qubit_range)
    front_length = 0
    back_length = 0
    found_mid = 0
    current_qubit = [] #record current active qubit
    current_two = [] #record current two qubit groups
    for i in range(qubits):
        qubit_loc.append([-1,-1])
        front_loc.append([-1,-1])
    for i in range(len(middle_DAG)):
        if middle_DAG[i] != []:
            found_mid = 1
            mid_length = mid_length + 1
            for gate in middle_DAG[i]:
                gate_list.append(gate)
        elif found_mid == 1 and middle_DAG[i] == []:
            back_length = back_length + 1
    for i in range(len(middle_DAG)):
        if middle_DAG[i] == []:
            front_length = front_length + 1
        elif middle_DAG[i] != []:
            break
    mid_DAG = copy.deepcopy(middle_DAG)
    if sche:
        for i in range(len(back_DAG)):
            if back_DAG[i] != []:
                mid_DAG[i].extend(back_DAG[i])
    initial_layer(mid_DAG, front_length, rows, qubits, full, active_qubit, front_loc, qubit_loc, current_two, current_qubit, map)
    for i in range(len(mid_DAG)):
        if mid_DAG[i] == []:
            continue
        active_qubit = copy.deepcopy(current_qubit)
        current_qubit = []
        constant, current_two = check_two_qubit(current_two, mid_DAG[i])
        if constant == True:
            for gate in mid_DAG[i]:
                if gate['type'] == 'S':
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    start = [qubit_loc[gate['t1']][0], qubit_loc[gate['t1']][1] + 1]
                    map[start[0]][start[1]:start[1]] = pattern
                    qubit_loc[gate['t1']] = [start[0], start[1] + len(pattern) - 1]
                    current_qubit.append(gate['t1'])
                    current_qubit.sort()
                else:
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    add_qubit(gate, active_qubit, qubit_loc)
                    current_qubit.append(gate['t1'])
                    current_qubit.append(gate['t2'])
                    current_qubit.sort()
                    if gate['t1'] < gate['t2']:
                        start = [qubit_loc[gate['t1']][0], qubit_loc[gate['t1']][1] + 1]
                        map[start[0]][start[1]:start[1]] = pattern[0]
                        map[start[0] + 1][start[1]:start[1]] = pattern[1]
                        map[start[0] + 2][start[1]:start[1]] = pattern[2]
                        qubit_loc[gate['t1']] = [start[0], start[1] + len(pattern[0]) - 1]
                        qubit_loc[gate['t2']] = [start[0] + 2, start[1] + len(pattern[0]) - 1]
                    elif gate['t1'] > gate['t2']:
                        start = [qubit_loc[gate['t2']][0], qubit_loc[gate['t2']][1] + 1]
                        map[start[0]][start[1]:start[1]] = pattern[2]
                        map[start[0] + 1][start[1]:start[1]] = pattern[1]
                        map[start[0] + 2][start[1]:start[1]] = pattern[0]
                        qubit_loc[gate['t2']] = [start[0], start[1] + len(pattern[0]) - 1]
                        qubit_loc[gate['t1']] = [start[0] + 2, start[1] + len(pattern[0]) - 1]
        else:
            for gate in mid_DAG[i]:
                if gate['type'] == 'S':
                    start = check_locate(gate, qubit_loc, map, qubit_range, rows, active_qubit, front_loc)
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    map[start[0]][start[1]:start[1]] = pattern
                    current_qubit.append(gate['t1'])
                    current_qubit.sort()
                else:
                    current_qubit.append(gate['t1'])
                    current_qubit.append(gate['t2'])
                    current_qubit.sort()
                    start = check_locate(gate, qubit_loc, map, qubit_range, rows, active_qubit, front_loc)
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    if gate['t1'] < gate['t2']:
                        map[start[0]][start[1]:start[1]] = pattern[0]
                        map[start[0] + 1][start[1]:start[1]] = pattern[1]
                        map[start[0] + 2][start[1]:start[1]] = pattern[2]
                    else:
                        map[start[0]][start[1]:start[1]] = pattern[2]
                        map[start[0] + 1][start[1]:start[1]] = pattern[1]
                        map[start[0] + 2][start[1]:start[1]] = pattern[0]
        align(map, qubit_loc, current_qubit)
        map = fill_z(map)
    max = 0
    for i in range(len(map)):
        last_point = -1
        for j in reversed(range(len(map[i]))):
            if map[i][j] != 'Z':
                last_point = j
                z_length = len(map[i]) - last_point - 1
                break
        for j in range(z_length):
            map[i].pop(-1)
        if len(map[i]) > max:
            max = len(map[i])
    for row in map:
        if len(row) < max:
            for i in range(max - len(row)):
                row.append('Z')
    return map, front_loc, front_length, back_length

def placement2(rows, qubits, DAG, front_DAG, mid_DAG, qubit_range):
    widest_mid = 3 * (qubits - 1) #without single gate in the middle
    map = []
    for i in range(rows):
        map.append(['Z'])
    gate_list = [] #for all the mid gates
    mid_length = 0 #count how long is mid
    front_length = 0
    back_length = 0
    found_mid = 0
    for i in range(len(mid_DAG)):
        if mid_DAG[i] != []:
            found_mid = 1
            mid_length =mid_length + 1
            for gate in mid_DAG[i]:
                gate_list.append(gate)
        elif found_mid == 1 and mid_DAG[i] == []:
            back_length = back_length + 1
    for i in range(len(mid_DAG)):
        if mid_DAG[i] == []:
            front_length = front_length + 1
        elif mid_DAG[i] != []:
            break
    if widest_mid + 2 > rows >= widest_mid: #only for maximal case and without single gate
        current = gate_list.pop(0)
        qubit_loc = init_qubit1(rows, qubits, current, widest_mid, mid_length, front_length, back_length)
        #initial the first gate
        index = 0 #for qubit loc
        fill_length = 0
        for i in range(len(DAG)):
            if DAG[i] != []:
                for gate in DAG[i]:
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    if gate['type'] == 'D':
                        if gate['t1'] < gate['t2']:
                            map[qubit_loc[index][gate['t1']]].extend(pattern[0])
                            map[qubit_loc[index][gate['t1']] + 1].extend(pattern[1])
                            map[qubit_loc[index][gate['t2']]].extend(pattern[2])
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                        else:
                            map[qubit_loc[index][gate['t2']]].extend(pattern[0])
                            map[qubit_loc[index][gate['t2']] + 1].extend(pattern[1])
                            map[qubit_loc[index][gate['t1']]].extend(pattern[2])
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                    else:
                        if gate['length'] == 6 and (i == 0 or gate['t1'] not in DAG[i - 1][0]['active']):
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + ['Z'] + pattern
                        elif gate['length'] == 6 and (i == len(DAG) - 1 or gate['t1'] not in DAG[i + 1][0]['active']):
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + pattern + ['Z']
                        elif (gate['t1'] == 0 or gate['t1'] == qubits - 1) and gate['t1'] not in DAG[i - 1][0]['active']:
                            map[qubit_loc[index][gate['t1']]].pop(-1)
                            map[qubit_loc[index][gate['t1']]].extend(pattern)
                        elif (gate['t1'] == 0 or gate['t1'] == qubits - 1) and gate['gate'] == 'I2':
                            map[qubit_loc[index][gate['t1']]].extend(['X', 'X'])
                        elif (gate['t1'] == 0 or gate['t1'] == qubits - 1) and gate['gate'] == 'I3':
                            map[qubit_loc[index][gate['t1']]].extend(['X', 'X','X', 'X'])
                        elif gate['t1'] == 0 or gate['t1'] == qubits - 1:
                            map[qubit_loc[index][gate['t1']]].extend(pattern)
                        else:
                            map[qubit_loc[index][gate['t1']]].extend(pattern)
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                schedule_fill(map, fill_length)
                index = index + 1
    elif rows >= widest_mid + 2:
        current = gate_list.pop(0)
        qubit_loc = init_qubit2(rows, qubits, current, mid_DAG, mid_length, front_length, back_length)
        index = 0  # for qubit loc
        for i in range(len(DAG)):
            if DAG[i] != []:
                for gate in DAG[i]:
                    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                    if gate['type'] == 'D':
                        if gate['gate'] == 'SW' and gate['length'] == 6:
                            map[qubit_loc[index][gate['t1']]].extend(['X']*2)
                            map[qubit_loc[index][gate['t1']] + 1].extend(['Z']*2)
                            map[qubit_loc[index][gate['t2']]].extend(['X']*2)
                        if gate['t1'] < gate['t2']:
                            map[qubit_loc[index][gate['t1']]].extend(pattern[0])
                            map[qubit_loc[index][gate['t1']] + 1].extend(pattern[1])
                            map[qubit_loc[index][gate['t2']]].extend(pattern[2])
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                        else:
                            map[qubit_loc[index][gate['t1']]].extend(pattern[0])
                            map[qubit_loc[index][gate['t2']] + 1].extend(pattern[1])
                            map[qubit_loc[index][gate['t2']]].extend(pattern[2])
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                    else:
                        if gate['length'] == 6 and (i == 0 or gate['t1'] not in DAG[i - 1][0]['active']):
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + ['Z','Z'] + pattern
                        elif gate['length'] == 6 and (i == len(DAG) - 1 or gate['t1'] not in DAG[i + 1][0]['active']):
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + pattern + ['Z']
                        else:
                            map[qubit_loc[index][gate['t1']]].extend(pattern)
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                schedule_fill(map, fill_length, qubit_loc, index)
                index = index + 1

    only_z = 1
    max = 0
    for i in range(len(map)):
        if map[i][0] != 'Z':
            only_z = 0
        if len(map[i]) > max:
            max = len(map[i])
    if only_z:
        max = max - 1
        for i in range(len(map)):
            map[i].pop(0)
    for i in range(len(map)):
        if len(map[i]) < max:
            map[i].extend(['Z'] * (max - len(map[i])))
    return map

def Average(lst):
    return int(sum(lst) / len(lst))

def init_qubit1(rows, qubits, gate, widest_mid, mid_length, front_length, back_length): #only for no single gate in middle!
    qubit_loc = []
    qubits_layer = [0] * qubits
    if gate['type'] == 'D':
        start = min(gate['t1'], gate['t2'])
    else:
        start = gate['t1']
    first = 0 + int((rows - widest_mid) / 2)
    qubits_layer[0] = first
    qubits_layer[-1] = rows - int((rows-widest_mid)/2) - 1
    if start % 2 == 0:
        for i in range(1, qubits - 1):
            if i % 2 == 1:
                qubits_layer[i] = qubits_layer[i-1] + 2
            else:
                qubits_layer[i] = qubits_layer[i - 1] + 4
    else:
        qubits_layer[1] = qubits_layer[0] + 3
        for i in range(2, qubits - 1):
            if i % 2 == 1:
                qubits_layer[i] = qubits_layer[i-1] + 4
            else:
                qubits_layer[i] = qubits_layer[i - 1] + 2
    qubit_loc.append(qubits_layer)
    for i in range(1, mid_length):
        qubits_layer = [0] * qubits
        qubits_layer[0] = first
        qubits_layer[-1] = rows - int((rows - widest_mid) / 2) - 1
        for j in range(1, qubits - 1):
            if (qubit_loc[i-1][j] - qubit_loc[i-1][j - 1]) == 2:
                qubits_layer[j] = qubit_loc[i-1][j] + 1
            else:
                qubits_layer[j] = qubit_loc[i - 1][j] - 1
        qubit_loc.append(qubits_layer)
    for i in range(front_length):
        qubit_loc.insert(0, qubit_loc[1])
    for i in range(back_length):
        qubit_loc.append(qubit_loc[len(qubit_loc) - 2])
    return qubit_loc

def init_qubit2(rows, qubits, gate, mid_DAG, mid_length, front_length, back_length):
    qubit_loc = []
    qubits_layer = [0] * qubits
    if gate['type'] == 'D':
        start = min(gate['t1'], gate['t2'])
    else:
        start = gate['t1']
    layout1 = [0]
    layout2 = [1]
    for i in range(1, qubits):
        if i % 2 == 1:
            layout1.append(layout1[i - 1] + 4)
        else:
            layout1.append(layout1[i - 1] + 2)
    for i in range(1, qubits):
        if i % 2 == 1:
            layout2.append(layout2[i - 1] + 2)
        else:
            layout2.append(layout2[i - 1] + 4)
    if start % 2 == 0:
        current_layout = layout2
    else:
        current_layout = layout1
    qubit_loc.append(current_layout)
    index = copy.deepcopy(front_length)
    current_2 = []
    for gate in mid_DAG[index]:
        if gate['type'] == 'D':
            target = [gate['t1'], gate['t2']]
            target.sort()
            current_2.append(copy.deepcopy(target))
    index = index + 1
    for i in range(1, mid_length):
        next_2 = []
        for gate in mid_DAG[index]:
            if gate['type'] == 'D':
                target = [gate['t1'], gate['t2']]
                target.sort()
                next_2.append(copy.deepcopy(target))
        same = 0 #found same target 2 qubit gates
        for gate1 in current_2:
            for gate2 in next_2:
                if gate1 == gate2:
                    same = 1
                    break
        if same == 0:
            if current_layout == layout2:
                current_layout = layout1
            elif current_layout == layout1:
                current_layout = layout2
        qubit_loc.append(current_layout)
        index = index + 1
        current_2 = copy.deepcopy(next_2)
    for i in range(front_length):
        if qubit_loc[0] == layout1:
            qubit_loc.insert(0, layout2)
        else:
            qubit_loc.insert(0, layout1)
    for i in range(back_length):
        if qubit_loc[-1] == layout1:
            qubit_loc.append(layout2)
        else:
            qubit_loc.append(layout1)
    return qubit_loc
def schedule_fill(map, fill, qubit_loc, index):
    max = 0
    if (len(qubit_loc) - 1 > index and qubit_loc[index] == qubit_loc[index + 1]):
        for i in range(len(map)):
            if len(map[i]) < fill + 1:
                map[i].extend(['Z'] * (fill - len(map[i])))
    else:
        for i in range(len(map)):
            if len(map[i]) < fill:
                map[i].extend(['Z'] * (fill - len(map[i]) - 1))

def check_locate(gate, qubit_loc, map, qubit_range, rows, active_qubit, front_loc):
    pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
    if gate['type'] == 'S':
        target = gate['t1']
        locate = qubit_loc[target]
        if target == 0 and locate[0] != 0:
            start = [locate[0]-1, locate[1]]
            qubit_loc[target] = [locate[0]-1, locate[1] + len(pattern) - 1]
            return start
        if target == 0 and locate[0] == 0:
            if map[locate[0] + 1][locate[1]] == 'Z' and map[locate[0] + 2][locate[1]] == 'Z':
                qubit_loc[target] = [locate[0] + 1, locate[1] + len(pattern) - 1]
                start = [locate[0] + 1, locate[1]]
                return start
            else:
                qubit_loc[target] = [locate[0], locate[1] + len(pattern)]
                return [locate[0], locate[1] + 1]
        elif target == len(qubit_range) - 1 and locate[0] != rows - 1:
            start = [locate[0] + 1, locate[1]]
            qubit_loc[target] = [locate[0] + 1, locate[1] + len(pattern) - 1]
            return start
        elif target == len(qubit_range) - 1 and locate[0] == rows - 1:
            qubit_loc[target] = [locate[0], locate[1] + len(pattern)]
            return [locate[0], locate[1] + 1]
        elif locate[0] - 1 in qubit_range[gate['t1']] and map[locate[0] - 1][locate[1] - 1] == 'Z' and map[locate[0] - 2][ locate[1]] == 'Z':
            start = [locate[0] - 1, locate[1]]
            qubit_loc[target] = [locate[0] - 1, locate[1] + len(pattern) - 1]
            return start
        elif locate[0] + 1 in qubit_range[gate['t1']] and map[locate[0] + 1][locate[1] - 1] == 'Z' and map[locate[0] + 2][ locate[1]] == 'Z':
            start = [locate[0] + 1, locate[1]]
            qubit_loc[target] = [locate[0] + 1, locate[1] + len(pattern) - 1]
            return start
        else:
            qubit_loc[target] = [locate[0], locate[1] + len(pattern)]
            return [locate[0], locate[1] + 1]
    if gate['type'] == 'D':
        if gate['t1'] < gate['t2']:
            target = gate['t1']
        else:
            target = gate['t2']
        if qubit_loc[target] == [-1,-1]:
            if qubit_loc[target + 1][0] -3 in qubit_range[target]:
                start = [qubit_loc[target + 1][0] -3, qubit_loc[target + 1][1]]
                if gate['gate'] == 'CNOT':
                    front_loc[target] = [qubit_loc[target + 1][0] -3, qubit_loc[target + 1][1]]
                    qubit_loc[target] = [qubit_loc[target + 1][0] -3, qubit_loc[target + 1][1] + 5]
                    qubit_loc[target + 1] = [start[0]+2, start[1] + 5]
                else:
                    front_loc[target] = [qubit_loc[target + 1][0] - 3, qubit_loc[target + 1][1]]
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 3, qubit_loc[target + 1][1] + 3]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                return start
            else:
                start = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 1]
                if gate['gate'] == 'CNOT':
                    front_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 1]
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 6]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 5]
                else:
                    front_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 1]
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 4]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                return start
        elif qubit_loc[target + 1] == [-1,-1]:
            if qubit_loc[target][0] + 3 in qubit_range[target + 1]:
                start = [qubit_loc[target][0] + 1, qubit_loc[target][1]]
                if gate['gate'] == 'CNOT':
                    front_loc[target + 1] = [start[0]+2, start[1]]
                    qubit_loc[target + 1] = [start[0]+2, start[1] + 5]
                    qubit_loc[target] = [start[0], start[1] + 5]
                else:
                    front_loc[target + 1] = [start[0] + 2, start[1]]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                    qubit_loc[target] = [start[0], start[1] + 3]
                return start
            else:
                start = [qubit_loc[target][0], qubit_loc[target][1] + 1]
                if gate['gate'] == 'CNOT':
                    front_loc[target + 1] = [start[0] + 2, start[1]]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 5]
                    qubit_loc[target] = [start[0], start[1] + 5]
                else:
                    front_loc[target + 1] = [start[0] + 2, start[1]]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                    qubit_loc[target] = [start[0], start[1] + 3]
                return start
        else:
            if qubit_loc[target][0]+3 in qubit_range[target + 1] and map[qubit_loc[target][0] + 3][qubit_loc[target][1]] == 'Z' \
                    and map[qubit_loc[target][0] + 2][qubit_loc[target][1]] == 'Z':
                start = [qubit_loc[target][0]+1, qubit_loc[target][1]]
            else:
                start = [qubit_loc[target][0], qubit_loc[target][1] + 1]
            if gate['gate'] == 'CNOT':
                qubit_loc[target + 1] = [start[0] + 2, start[1] + 5]
                qubit_loc[target] = [start[0], start[1] + 5]
            else:
                qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                qubit_loc[target] = [start[0], start[1] + 3]
            return start

def first_loc(rows, target, qubits, full):
    if len(target) == 1:
        if full == False:
            if target[0] == 0:
                row = 0
            elif target[0] == qubits - 1:
                row = rows - 2
            else:
                interval = (rows - 1)/(qubits - 1)
                row = math.ceil(interval * target[0])
        else:
            layout1 = [0]
            layout2 = [1]
            for i in range(1, qubits):
                if i % 2 == 1:
                    layout1.append(layout1[i - 1] + 4)
                else:
                    layout1.append(layout1[i - 1] + 2)
            for i in range(1, qubits):
                if i % 2 == 1:
                    layout2.append(layout2[i - 1] + 2)
                else:
                    layout2.append(layout2[i - 1] + 4)
            if target[0] % 2 == 0:
                row = layout2[target[0]]
            else:
                row = layout1[target[0]]
        return row
    else:
        row = []
        if full == False:
            for tar in target:
                if tar == 0:
                    row.append(0)
                elif tar == qubits - 1:
                    row.append(rows - 2)
                else:
                    interval = (rows - 1)/(qubits - 1)
                    row.append(math.ceil(interval * tar))
        else:
            first_tar = target[0]
            layout1 = [0]
            layout2 = [1]
            for i in range(1, qubits):
                if i % 2 == 1:
                    layout1.append(layout1[i - 1] + 4)
                else:
                    layout1.append(layout1[i - 1] + 2)
            for i in range(1, qubits):
                if i % 2 == 1:
                    layout2.append(layout2[i - 1] + 2)
                else:
                    layout2.append(layout2[i - 1] + 4)
            if first_tar % 2 == 0:
                layout = layout2
            else:
                layout = layout1
            for tar in target:
                row.append(layout[tar])
        return row
def check_two_qubit(current_two, layer):
    future_two = []
    constant =False
    for gate in layer:
        if gate['type'] == 'D':
            if gate['t1'] < gate['t2']:
                future_two.append([gate['t1'], gate['t2']])
            else:
                future_two.append([gate['t2'], gate['t1']])
    for targets in future_two:
        if targets in current_two:
            constant = True
            break
    return constant, future_two

def add_qubit(gate, active_qubit, qubit_loc):
    if gate['t1'] < gate['t2']:
        if gate['t1'] not in active_qubit:
            active_qubit.append(gate['t1'])
            active_qubit.sort()
            qubit_loc[gate['t1']] = [qubit_loc[gate['t2']][0] - 2, qubit_loc[gate['t2']][1]]
        elif gate['t2'] not in active_qubit:
            active_qubit.append(gate['t2'])
            active_qubit.sort()
            qubit_loc[gate['t2']] = [qubit_loc[gate['t1']][0] + 2, qubit_loc[gate['t2']][1]]
    elif gate['t1'] > gate['t2']:
        if gate['t1'] not in active_qubit:
            active_qubit.append(gate['t1'])
            active_qubit.sort()
            qubit_loc[gate['t1']] = [qubit_loc[gate['t2']][0] + 2, qubit_loc[gate['t2']][1]]
        elif gate['t2'] not in active_qubit:
            active_qubit.append(gate['t2'])
            active_qubit.sort()
            qubit_loc[gate['t2']] = [qubit_loc[gate['t1']][0] - 2, qubit_loc[gate['t2']][1]]

def fill_front(map, front_loc, front_DAG, front_length, qubit_range):
    active_qubit = []
    for i in range(len(map)):
        map[i] = ['Z'] * front_length * 4 + map[i]
    for i in range(len(front_loc)):
        front_loc[i][1] = front_loc[i][1] + 4 * front_length
    for layer in reversed(front_DAG):
        if layer != []:
            for gate in layer:
                if gate['t1'] not in active_qubit:
                    active_qubit.append(gate['t1'])
                start = front_loc[gate['t1']]
                pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                if start[0] == len(map) - 1:
                    if map[start[0] - 2][start[1]] == 'Z':
                        map[start[0] - 1][start[1] - 3:start[1] + 1] = pattern
                        front_loc[gate['t1']][1] = front_loc[gate['t1']][1] - 3
                        front_loc[gate['t1']][0] = front_loc[gate['t1']][0] - 1
                    else:
                        map[start[0]][start[1]-4:start[1]] = pattern
                        front_loc[gate['t1']][1] = front_loc[gate['t1']][1] - 4
                elif start[0] == 0:
                    if map[start[0] + 2][start[1]] == 'Z':
                        map[start[0] + 1][start[1] - 3:start[1] + 1] = pattern
                        front_loc[gate['t1']][1] = front_loc[gate['t1']][1] - 3
                        front_loc[gate['t1']][0] = front_loc[gate['t1']][0] + 1
                    else:
                        map[start[0]][start[1]-4:start[1]] = pattern
                        front_loc[gate['t1']][1] = front_loc[gate['t1']][1] - 4
                elif start[0] == len(map) - 2 and map[start[0] + 1][start[1]] == 'Z':
                    map[start[0] + 1][start[1] - 3:start[1] + 1] = pattern #need to consider up and down and also qubit range!
                    front_loc[gate['t1']] = [front_loc[gate['t1']][0] + 1, front_loc[gate['t1']][1] - 3]
                elif start[0] == 1 and map[start[0] - 1][start[1]] == 'Z':
                    map[start[0] - 1][start[1] - 3:start[1] + 1] = pattern
                    front_loc[gate['t1']] = [front_loc[gate['t1']][0] - 1, front_loc[gate['t1']][1] - 3]
                elif map[start[0] - 1][start[1]] == map[start[0] - 2][start[1]] and map[start[0] - 2][start[1]] == 'Z' and start[0] - 1 in qubit_range[gate['t1']]:
                    map[start[0] - 1][start[1] - 3:start[1] + 1] = pattern
                    front_loc[gate['t1']] = [front_loc[gate['t1']][0] - 1, front_loc[gate['t1']][1] - 3]
                elif map[start[0] + 1][start[1]] == map[start[0] + 2][start[1]] and map[start[0] + 2][start[1]] == 'Z' and start[0] + 1 in qubit_range[gate['t1']]:
                    map[start[0] + 1][start[1] - 3:start[1] + 1] = pattern
                    front_loc[gate['t1']] = [front_loc[gate['t1']][0] + 1, front_loc[gate['t1']][1] - 3]
                else:
                    map[start[0]][start[1] - 4:start[1]] = pattern
                    front_loc[gate['t1']][1] = front_loc[gate['t1']][1] - 4
    for i in range(len(map[0])):
        all_z = True
        for j in range(len(map)):
            if map[j][0] != 'Z':
                all_z = False
                break
        if all_z == True:
            for row in map:
                row.pop(0)
        else:
            break

def fill_z(map):
    max = 0
    for row in map:
        if len(row) > max:
            max = len(row)
    for i in range(len(map)):
        map[i].extend(['Z'] * (max - len(map[i])))
    return map

def align(map, qubit_loc, current_qubit):
    max = 0
    min = 1000000
    for i in current_qubit:
        if qubit_loc[i][1] > max:
            max = qubit_loc[i][1]
        elif qubit_loc[i][1] < min:
            min = qubit_loc[i][1]
    if max - min == 2:
        for i in current_qubit:
            if qubit_loc[i][1] == min:
                map[qubit_loc[i][0]][qubit_loc[i][1] + 1:qubit_loc[i][1] + 1] = ['X','X']
                qubit_loc[i][1] = qubit_loc[i][1] + 2

def initial_layer(mid_DAG, front_length, rows, qubits, full, active_qubit, front_loc, qubit_loc, current_two, current_qubit, map):
    if len(mid_DAG[front_length]) == 1:
        init_gate = mid_DAG[front_length].pop(0)
        pattern, _, _, _, _ = de_gate(init_gate['gate'] + ' 0 0 ')
        if init_gate['t1'] < init_gate['t2']:
            target = [init_gate['t1']]
            first_row = first_loc(rows, target, qubits, full)
            map[first_row][0:0] = pattern[0]
            map[first_row + 1][0:0] = pattern[1]
            map[first_row + 2][0:0] = pattern[2]
            active_qubit.append(init_gate['t1'])
            active_qubit.append(init_gate['t2'])
            active_qubit.sort()
        else:
            target = [init_gate['t2']]
            first_row = first_loc(rows, target, qubits, full)
            map[first_row][0:0] = pattern[2]
            map[first_row + 1][0:0] = pattern[1]
            map[first_row + 2][0:0] = pattern[0]
            active_qubit.append(init_gate['t1'])
            active_qubit.append(init_gate['t2'])
            active_qubit.sort()
        front_loc[target[0]] = [first_row, 0]
        front_loc[target[0] + 1] = [first_row + 2, 0]
        qubit_loc[target[0]] = [first_row, len(pattern[0]) - 1]
        qubit_loc[target[0] + 1] = [first_row + 2, len(pattern[0]) - 1]
        current_two.append([target[0], target[0] + 1])
        current_qubit.append(target[0])
        current_qubit.append(target[0] + 1)
    else:
        target = []
        for gate in mid_DAG[front_length]:
            if gate['t1'] < gate['t2']:
                target.append(gate['t1'])
            else:
                target.append(gate['t2'])
        #target.sort()
        first_row = first_loc(rows, target, qubits, full)
        gate_num = len(mid_DAG[front_length])
        for i in range(gate_num):
            gate = mid_DAG[front_length].pop(0)
            pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
            length = 0
            #index = 0
            if (gate['gate'] == 'SW' or gate['gate'] == 'CP') and gate['length'] == 6:
                row = first_row[i]
                map[row][0:0] = ['X','X']
                map[row + 1][0:0] = ['Z','Z']
                map[row + 2][0:0] = ['X','X']
                length = length + 2
            if gate['t1'] < gate['t2']:
                row = first_row[i]
                map[row][length:length] = pattern[0]
                map[row + 1][length:length] = pattern[1]
                map[row + 2][length:length] = pattern[2]
                active_qubit.append(gate['t1'])
                active_qubit.append(gate['t2'])
                active_qubit.sort()
            else:
                row = first_row[i]
                map[row][0:0] = pattern[2]
                map[row + 1][0:0] = pattern[1]
                map[row + 2][0:0] = pattern[0]
                active_qubit.append(gate['t1'])
                active_qubit.append(gate['t2'])
                active_qubit.sort()
            length = length + len(pattern[0]) - 1
            front_loc[target[i]] = [row, 0]
            front_loc[target[i] + 1] = [row + 2, 0]
            qubit_loc[target[i]] = [row, length]
            qubit_loc[target[i] + 1] = [row + 2, length]
            current_two.append([target[i], target[i] + 1])
            current_qubit.append(target[i])
            current_qubit.append(target[i] + 1)
