import numpy as np
import math
from gate_blocks import *
from new_swap import *
from dense import *
import copy
from dense import *
from scheduling import *

def elastic(n,DAG, rows):
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
    map, qubit_loc = place_mid(rows, n, DAG, front_DAG, middle_DAG, qubit_range)
    front_loc, back_loc = find_qubit_row(middle_DAG, qubit_loc, map)
    return map

def place_mid(rows, qubits, DAG, front_DAG, mid_DAG, qubit_range):
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
    if rows >= widest_mid + 2:
        current = gate_list.pop(0)
        qubit_loc = init_qubit2(rows, qubits, current, mid_DAG, mid_length, front_length, back_length)
        DAG = copy.deepcopy(mid_DAG)
        for i in range(front_length):
            qubit_loc.pop(0)
            DAG.pop(0)
        for i in range(back_length):
            qubit_loc.pop(-1)
            DAG.pop(-1)
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
    return map, qubit_loc

def find_qubit_row(middle_DAG, qubit_loc, map):
    empty = 0
    for layer in middle_DAG:
        if layer == []:
            empty += 1
        else:
            break
    front_layer = [x - empty for x in middle_DAG[empty][0]['front']]
    back_layer = [x - empty for x in middle_DAG[empty][0]['back']]
    front_row = []
    back_row = []
    for i in range(len(front_layer)):
        front_row.append(qubit_loc[front_layer[i]][i])
        back_row.append(qubit_loc[back_layer[i]][i])
    front_loc = []
    back_loc = []
    for row in front_row:
        index = 0
        if row != 0 and row != len(map) - 1:
            while map[row][index] == 'Z' or (map[row-1][index] == 'Z' and map[row+1][index] == 'Z'):
                index += 1
        elif row != 0:
            while map[row][index] == 'Z' or map[row-1][index] == 'Z':
                index += 1
        else:
            while map[row][index] == 'Z' or map[row+1][index] == 'Z':
                index += 1
        loc = [row, index]
        front_loc.append(loc)

    for row in back_row:
        index = len(map[0]) - 1
        if row != 0 and row != len(map) - 1:
            while map[row][index] == 'Z' or (map[row-1][index] == 'Z' and map[row+1][index] == 'Z'):
                index -= 1
        elif row != 0:
            while map[row][index] == 'Z' or map[row-1][index] == 'Z':
                index -= 1
        else:
            while map[row][index] == 'Z' or map[row+1][index] == 'Z':
                index -= 1
        loc = [row, index]
        back_loc.append(loc)