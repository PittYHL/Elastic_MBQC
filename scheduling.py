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
    two_qubits = [] #track physical qubits that with two_qubit_gate
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
    map = place_middle(rows, n, DAG, front_DAG, middle_DAG, qubit_range)
    return map

def placement(rows, qubits, DAG, front_DAG, mid_DAG, qubit_range):
    map = []
    for i in range(rows):
        map.append(['Z']*(len(DAG)*4))
    gate_list = []
    #place the first gate
    for layer in DAG:
        for current in layer:
            gate_list.append(current)
    current = gate_list.pop(0)
    qubit_loc = []
    for i in range(qubits):
        qubit_loc.append([-1, -1])
    if current['type'] == 'S':
        pattern, _, _, _, _ = de_gate(current['gate'] + ' 0 0 ')
        target = current['t1']
        start = qubit_range[target][-1]
        map[start][0:0] = pattern
        qubit_loc[target] = [start, len(pattern) - 1]
        active_qubit = current['active']
    else:
        pattern, _, _, _, _ = de_gate(current['gate'] + ' 0 0 ')
        if current['t1'] < current['t2']:
            target = current['t1']
            start = qubit_range[target][-1]
            map[start][0:0] = pattern[0]
            map[start + 1][0:0] = pattern[1]
            map[start + 2][0:0] = pattern[2]
            qubit_loc[current['t1']] = [start, len(pattern) - 1]
            qubit_loc[current['t1'] + 1] = [start + 2, len(pattern) - 1]
            active_qubit = current['active']
        else:
            target = current['t2']
            start = qubit_range[target][-1]
            map[start][0:0] = pattern[2]
            map[start + 1][0:0] = pattern[1]
            map[start + 2][0:0] = pattern[0]
            qubit_loc[current['t2']] = [start, len(pattern) - 1]
            qubit_loc[current['t2'] + 1] = [start + 2, len(pattern) - 1]
            active_qubit = current['active']
    while gate_list != []:
        current = gate_list.pop(0)
        if current['type'] == 'S':
            start = check_locate(current, qubit_loc, map, qubit_range, rows, active_qubit)
            pattern, _, _, _, _ = de_gate(current['gate'] + ' 0 0 ')
            map[start[0]][start[1]:start[1]] = pattern
        else:
            start = check_locate(current, qubit_loc, map, qubit_range, rows, active_qubit)
            pattern, _, _, _, _ = de_gate(current['gate'] + ' 0 0 ')
            map[start[0]][start[1]:start[1]] = pattern[0]
            map[start[0]+1][start[1]:start[1]] = pattern[1]
            map[start[0]+2][start[1]:start[1]] = pattern[2]
    #delete redundancy
    min = 100000
    for row in map:
        if len(row) < min:
            min = len(row)
    for i in range(min):
        found = 1
        for row in map:
            if row[i] != 'Z':
                found = 0
        if found == 1:
            end = i
            break
    for row in map:
        delete_length = len(row) - end
        for i in range(delete_length):
            row.pop(-1)
    return map

def place_middle(rows, qubits, DAG, front_DAG, mid_DAG, qubit_range):
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
        qubit_loc = init_qubit2(rows, qubits, current, widest_mid, mid_length, front_length, back_length)
        index = 0  # for qubit loc
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
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + ['Z','Z'] + pattern
                        elif gate['length'] == 6 and (i == len(DAG) - 1 or gate['t1'] not in DAG[i + 1][0]['active']):
                            map[qubit_loc[index][gate['t1']]] = map[qubit_loc[index][gate['t1']]] + pattern + ['Z']
                        else:
                            map[qubit_loc[index][gate['t1']]].extend(pattern)
                            fill_length = len(map[qubit_loc[index][gate['t1']]])
                schedule_fill(map, fill_length)
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

def init_qubit2(rows, qubits, gate, widest_mid, mid_length, front_length, back_length):
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
        for i in range(mid_length):
            if i % 2 == 1:
                qubit_loc.append(layout1)
            else:
                qubit_loc.append(layout2)
    else:
        for i in range(mid_length):
            if i % 2 == 0:
                qubit_loc.append(layout1)
            else:
                qubit_loc.append(layout2)
    for i in range(front_length):
        qubit_loc.insert(0, qubit_loc[1])
    for i in range(back_length):
        qubit_loc.append(qubit_loc[len(qubit_loc) - 2])
    return qubit_loc
def schedule_fill(map, fill):
    max = 0
    for i in range(len(map)):
        if len(map[i]) < fill:
            map[i].extend(['Z'] * (fill - len(map[i]) - 1))

def check_locate(gate, qubit_loc, map, qubit_range, rows, active_qubit):
    if gate['type'] == 'S':
        target = gate['t1']
        locate = qubit_loc[target]
        if target == 0 and locate[0] != 0:
            start = [locate[0]-1, locate[1]]
            qubit_loc[target] = [locate[0]-1, locate[1] + 3]
            return start
        if target == 0 and locate[0] == 0:
            qubit_loc[target] = [locate[0], locate[1] + 4]
            return [locate[0], locate[1] + 1]
        elif target == len(qubit_range) - 1 and locate[0] != rows - 1:
            start = [locate[0] + 1, locate[1]]
            qubit_loc[target] = [locate[0] + 1, locate[1] + 3]
            return start
        elif target == len(qubit_range) - 1 and locate[0] == rows - 1:
            qubit_loc[target] = [locate[0], locate[1] + 4]
            return [locate[0], locate[1] + 1]
        elif map[locate[0] - 1][locate[1] - 1] == 'Z' and map[locate[0] - 2][ locate[1]] == 'Z':
            start = [locate[0] - 1, locate[1]]
            qubit_loc[target] = [locate[0] - 1, locate[1] + 3]
            return start
        elif map[locate[0] + 1][locate[1] - 1] == 'Z' and map[locate[0] + 2][ locate[1]] == 'Z':
            start = [locate[0] + 1, locate[1]]
            qubit_loc[target] = [locate[0] + 1, locate[1] + 3]
            return start
        else:
            qubit_loc[target] = [locate[0], locate[1] + 4]
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
                    qubit_loc[target] = [qubit_loc[target + 1][0] -3, qubit_loc[target + 1][1] + 5]
                    qubit_loc[target + 1] = [start[0]+2, start[1] + 5]
                else:
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 3, qubit_loc[target + 1][1] + 3]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                return start
            else:
                start = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 1]
                if gate['gate'] == 'CNOT':
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 6]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 5]
                else:
                    qubit_loc[target] = [qubit_loc[target + 1][0] - 2, qubit_loc[target + 1][1] + 4]
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                return start
        elif qubit_loc[target + 1] == [-1,-1]:
            if qubit_loc[target][0] + 3 in qubit_range[target + 1]:
                start = [qubit_loc[target][0] + 1, qubit_loc[target][1]]
                if gate['gate'] == 'CNOT':
                    qubit_loc[target + 1] = [start[0]+2, start[1] + 5]
                    qubit_loc[target] = [start[0], start[1] + 5]
                else:
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                    qubit_loc[target] = [start[0], start[1] + 3]
                return start
            else:
                start = [qubit_loc[target][0], qubit_loc[target][1] + 1]
                if gate['gate'] == 'CNOT':
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 5]
                    qubit_loc[target] = [start[0], start[1] + 5]
                else:
                    qubit_loc[target + 1] = [start[0] + 2, start[1] + 3]
                    qubit_loc[target] = [start[0], start[1] + 3]
                return start
        else:
            if qubit_loc[target][0]+3 <= rows-1:
                if map[qubit_loc[target][0] + 3][qubit_loc[target][1]] == 'Z':
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