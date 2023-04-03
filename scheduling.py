import numpy as np
import math
from gate_blocks import *
from new_swap import *
from dense import *
import copy
from dense import *
qubits = 4
physical_gate = []
tracker= []
map = []
rows = 11
def scheduling(n,DAG):
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
        qubit_range.append([i*2, rows - (n - i - 1)*2 - 1])
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
    map = place_middle(rows, qubits, DAG, front_DAG, middle_DAG, qubit_range)

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