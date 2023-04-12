import numpy as np
import math
from gate_blocks import *
from new_swap import *
from dense import *
import copy
from dense import *
from scheduling import *

def sche_ela(n,DAG, rows):
    extra_row = rows - 2 * n + 1
    print("widest width is:" + str((n-1) * 3 + 2))
    depth = 0
    for i in range(len(DAG)):
        length = 4  # record length iof the DAG layer
        for gate in DAG[i]:
            if gate['gate'] == 'CNOT':
                length = 6
        depth = depth + length
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
    if rows >= 3 * (n - 1) + 2:
        full = True
    else:
        full = False
    map, front_loc, front_length, back_length = search_mid(rows, n, DAG, back_DAG, middle_DAG, qubit_range, False, full)
    #map, qubit_loc = place_mid(rows, n, DAG, front_DAG, middle_DAG, qubit_range)
    #front_loc, back_loc = find_qubit_row(middle_DAG, qubit_loc, map)
    front_loc, back_loc = find_qubit_row2(map, front_length, back_length)
    front_pattern, back_pattern, mid_map = combine(front_DAG, front_loc, back_DAG, back_loc, map)
    elastic_map = greedy_elastic(front_pattern, back_pattern, mid_map, front_loc, back_loc, DAG)
    return elastic_map

def only_elastic(qubits,DAG, rows):
    front_DAG = []
    middle_DAG = []
    back_DAG = []
    # create three DAG
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
    map, qubit_loc = place_mid_normal(rows, qubits, DAG, front_DAG, middle_DAG)
    front_loc, back_loc = find_qubit_row(middle_DAG, qubit_loc, map)
    front_pattern, back_pattern, mid_map = combine(front_DAG, front_loc, back_DAG, back_loc, map)
    elastic_map = greedy_elastic(front_pattern, back_pattern, mid_map, front_loc, back_loc, DAG)
    return elastic_map

def place_mid_normal(rows, qubits, DAG, front_DAG, mid_DAG):
    qubit_loc = []
    up_rows = math.floor((rows - 2*qubits + 1)/2)
    bot_rows = math.ceil((rows - 2 * qubits + 1) / 2)
    layout = [up_rows]
    for i in range(1, qubits):
        layout.append(layout[i - 1] + 2)
    map = []
    for i in range(2*qubits-1):
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
    for i in range(len(mid_DAG)):
        if mid_DAG[i] == []:
            continue
        qubit_loc.append(layout)
        for gate in mid_DAG[i]:
            length = gate['length']
            pattern, t1, t2, t3, name = de_gate(gate['gate'] + ' 0 0 ')
            if gate['type'] == 'S':
                t1 = gate['t1']
                map[gate['t1']*2] = map[gate['t1']*2] + pattern
            elif gate['type'] == 'D':
                if gate['gate'] == 'SW' and gate['length'] == 6:
                    map[gate['t1'] * 2].extend(['X', 'X'])
                    map[gate['t2'] * 2].extend(['X', 'X'])
                    if gate['t1'] - gate['t2'] > 0:
                        map[gate['t1'] * 2 - 1].extend(['Z', 'Z'])
                    else:
                        map[gate['t2'] * 2 - 1].extend(['Z', 'Z'])
                map[gate['t1'] * 2].extend(pattern[0])
                map[gate['t2'] * 2].extend(pattern[2])
                if gate['t1'] - gate['t2'] > 0:
                    map[gate['t1'] * 2 - 1].extend(pattern[1])
                else:
                    map[gate['t2'] * 2 - 1].extend(pattern[1])
        normal_fill(map)
    row_length = len(map[0])
    for i in range(up_rows):
        map.insert(0, ['Z'] * row_length)
    for i in range(bot_rows):
        map.append(['Z'] * row_length)
    for i in range(len(map)):
        map[i] = ['Z'] * front_length * 3 + map[i] + ['Z'] * back_length * 3
    return map, qubit_loc

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
    for i in range(len(map)):
        map[i] = ['Z'] * front_length * 3 + map[i] + ['Z'] * back_length * 3
    return map, qubit_loc

def find_qubit_row2(map, front_length, back_length):
    front_loc = []
    back_loc = []
    for i in range(len(map)):
        found = 0
        for j in range(len(map[i])):
            if i == 0 and map[i][j] != 'Z' and map[i+1][j] != 'Z':
                break
            elif i == len(map) - 1 and map[i-1][j] != 'Z':
                break
            elif map[i][j] != 'Z' and (map[i-1][j] != 'Z' or map[i+1][j] != 'Z'):
                break
            elif i == 0 and j != len(map[i]) - 1 and map[i][j] != 'Z' and map[i][j+1] != 'Z' and map[i+1][j] == 'Z' \
                    and map[i+1][j-1] != 'Z':
                found = 1
                index = j
                break
            elif i == len(map) - 1 and j != len(map[i]) - 1 and map[i][j] != 'Z' and map[i][j+1] != 'Z' and map[i-1][j] == 'Z'\
                    and map[i+1][j-1] != 'Z':
                found = 1
                index = j
                break
            elif j != len(map[i]) - 1 and map[i][j] != 'Z' and map[i][j+1] != 'Z' and map[i-1][j] == 'Z' and map[i+1][j] == 'Z':
                found = 1
                index = j
                break
        if found == 1:
            if i == 0:
                while map[i][index] == 'Z' or map[i + 1][index] == 'Z':
                    index += 1
            elif i == len(map) - 1:
                while map[i][index] == 'Z' or map[i - 1][index] == 'Z':
                    index += 1
            else:
                while map[i][index] == 'Z' or (map[i - 1][index] == 'Z' and map[i + 1][index] == 'Z'):
                    index += 1
            loc = [i, index]
            front_loc.append(loc)
    for i in range(len(map)):
        found = 0
        for j in reversed(range(len(map[i]))):
            if i == 0 and map[i][j] != 'Z' and map[i+1][j] != 'Z':
                break
            elif i == len(map) - 1 and map[i-1][j] != 'Z':
                break
            elif map[i][j] != 'Z' and (map[i-1][j] != 'Z' or map[i+1][j] != 'Z'):
                break
            if i == 0 and j != 0 and map[i][j] != 'Z' and map[i][j-1] != 'Z' and map[i+1][j] == 'Z' and map[i+1][j+1] != 'Z':
                found = 1
                index = j
                break
            elif i == len(map) - 1 and j != 0 and map[i][j] != 'Z' and map[i][j-1] != 'Z' and map[i-1][j] == 'Z' and map[i+1][j+1] != 'Z':
                found = 1
                index = j
                break
            elif j != 0 and map[i][j] != 'Z' and map[i][j-1] != 'Z' and map[i-1][j] == 'Z' and map[i+1][j] == 'Z':
                found = 1
                index = j
                break
        if found == 1:
            if i == 0:
                while map[i][index] == 'Z' or map[i + 1][index] == 'Z':
                    index -= 1
            elif i == len(map) - 1:
                while map[i][index] == 'Z' or map[i - 1][index] == 'Z':
                    index -= 1
            else:
                while map[i][index] == 'Z' or (map[i - 1][index] == 'Z' and map[i + 1][index] == 'Z'):
                    index -= 1
            loc = [i, index]
            back_loc.append(loc)
    for i in range(len(map)):
        map[i] = ['Z'] * front_length * 3 + map[i] + ['Z'] * back_length * 3
    for i in range(len(front_loc)):
        front_loc[i][1] += front_length * 3
        back_loc[i][1] += front_length * 3
    return front_loc, back_loc


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
    return front_loc, back_loc

def combine(front_DAG, front_loc, back_DAG, back_loc, map):
    front_pattern = []
    back_pattern = []
    mid_map = copy.deepcopy(map)
    for loc in front_loc:
        row = loc[0]
        column = loc[1]
        temp = []
        for i in range(column):
            if mid_map[row][i] != 'Z':
                temp.append(mid_map[row][i])
                mid_map[row][i] = 'Z'
        front_pattern.append(temp)
    for loc in back_loc:
        row = loc[0]
        column = loc[1]
        temp = []
        for i in range(column + 1, len(mid_map[0])):
            if mid_map[row][i] != 'Z':
                temp.append(mid_map[row][i])
                mid_map[row][i] = 'Z'
        back_pattern.append(temp)
    for layer in reversed(front_DAG):
        if layer != []:
            for gate in layer:
                pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                front_pattern[gate['t1']] = pattern + front_pattern[gate['t1']]
    for layer in back_DAG:
        if layer != []:
            for gate in layer:
                pattern, _, _, _, _ = de_gate(gate['gate'] + ' 0 0 ')
                back_pattern[gate['t1']] = back_pattern[gate['t1']] + pattern
    return front_pattern, back_pattern, mid_map

def greedy_elastic(front_pattern, back_pattern, mid_map, front_loc, back_loc, DAG):
    front_barrier = DAG[0][0]['front']
    back_barrier = DAG[0][0]['back']
    front_barrier_sort = copy.deepcopy(front_barrier)
    back_barrier_sort = copy.deepcopy(back_barrier)
    front_barrier_sort.sort(reverse=True)
    back_barrier_sort.sort()
    front_order = []
    back_order = []
    rows = len(mid_map)
    front_loc_copy = copy.deepcopy(front_loc)
    back_loc_copy = copy.deepcopy(back_loc)
    front_order = find_front_order(front_loc, rows)
    back_order = find_back_order(back_loc, rows)
    """
    for i in range(len(front_barrier_sort)):
        front_ind = front_barrier.index(front_barrier_sort[i])
        back_ind = back_barrier.index(back_barrier_sort[i])
        front_order.append(front_ind)
        back_order.append(back_ind)
        front_barrier[front_ind] = -1
        back_barrier[back_ind] = -1
    resolve_order(front_order)
    resolve_order(back_order)
    """
    elastic_map = copy.deepcopy(mid_map)
    #place the front
    for i in range(len(front_order)):
        elastic_map = greedy_place_front(elastic_map, i, front_order, front_pattern,front_loc)
    #greedy_place_front2(elastic_map, front_order, front_loc, front_pattern)
    #place the back
    for i in range(len(back_order)):
        elastic_map = greedy_place_back(elastic_map, i, back_order, back_pattern,back_loc)
    #greedy_place_back2(elastic_map, back_order, back_loc, back_pattern)
    elastic_map = clean_map(elastic_map)
    return elastic_map

def greedy_place_front2(elastic_map, front_order, front_loc, front_pattern):
    patterns = copy.deepcopy(front_pattern)
    lists = [[] for _ in range(len(patterns))]
    start_loc = copy.deepcopy(front_loc)
    while patterns != lists:
        for i in front_order:
            if patterns[i] != []:
                pattern = patterns[i]
                next = pattern.pop(-1)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, left, down = found_possible_loc_front(elastic_map, front_loc[i], last)
                if i != 0 and front_loc[i][0] > start_loc[i-1][0] and front_loc[i][1] > start_loc[i-1][1]:
                    if left == 1:
                        front_loc[i] = [front_loc[i][0], front_loc[i][1] - 1]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    elif down == 1:
                        front_loc[i] = [front_loc[i][0] + 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    else:
                        front_loc[i] = [front_loc[i][0] - 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                elif front_loc[i][0] < len(elastic_map) / 2:
                    if down == 1:
                        front_loc[i] = [front_loc[i][0] + 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    elif up == 1:
                        front_loc[i] = [front_loc[i][0] - 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    else:
                        front_loc[i] = [front_loc[i][0], front_loc[i][1] - 1]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                else:
                    if up == 1:
                        front_loc[i] = [front_loc[i][0] - 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    elif down == 1:
                        front_loc[i] = [front_loc[i][0] + 1, front_loc[i][1]]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next
                    else:
                        front_loc[i] = [front_loc[i][0], front_loc[i][1] - 1]
                        k = front_loc[i][0]
                        j = front_loc[i][1]
                        elastic_map[k][j] = next

def greedy_place_back2(elastic_map, back_order, back_loc, back_pattern):
    patterns = copy.deepcopy(back_pattern)
    lists = [[] for _ in range(len(patterns))]
    while patterns != lists:
        for i in back_order:
            if patterns[i] != []:
                pattern = patterns[i]
                next = pattern.pop(0)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, right, down = found_possible_loc_back(elastic_map, back_loc[i], last)
                if back_loc[i][0] < len(elastic_map) / 2:
                    if down == 1:
                        back_loc[i] = [back_loc[i][0] + 1, back_loc[i][1]]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next
                    elif up == 1:
                        back_loc[i] = [back_loc[i][0] - 1, back_loc[i][1]]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next
                    else:
                        back_loc[i] = [back_loc[i][0], back_loc[i][1] + 1]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next
                else:
                    if up == 1:
                        back_loc[i] = [back_loc[i][0] - 1, back_loc[i][1]]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next
                    elif down == 1:
                        back_loc[i] = [back_loc[i][0] + 1, back_loc[i][1]]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next
                    else:
                        back_loc[i] = [back_loc[i][0], back_loc[i][1] + 1]
                        k = back_loc[i][0]
                        j = back_loc[i][1]
                        elastic_map[k][j] = next

def greedy_place_front(elastic_map, index, front_order, patterns, locations):
    front_pattern = patterns[front_order[index]]
    front_loc = locations[front_order[index]]
    pattern = copy.deepcopy(front_pattern)
    current_loc = copy.deepcopy(front_loc)
    if index == len(front_order) - 1:
        last = True
    else:
        last = False
    if last:
        while pattern != []:
            next = pattern.pop(-1)
            if pattern != []:
                last = 0
            else:
                last = 1
            up, left, down = found_possible_loc_front(elastic_map, current_loc, last)
            if current_loc[0] < len(elastic_map) / 2:
                if down == 1 :
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                else:
                    current_loc = [current_loc[0], current_loc[1] - 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
            else:
                if up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif down == 1 :
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                else:
                    current_loc = [current_loc[0], current_loc[1] - 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
    else:
        next_loc = find_close(index, front_order, locations)
        if next_loc[0] < front_loc[0]: #should go down
            while pattern != []:
                next = pattern.pop(-1)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, left, down = found_possible_loc_front(elastic_map, current_loc, last)
                if current_loc[0] - next_loc[0] <= 2:
                    up = 0
                if down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif left == 1:
                    current_loc = [current_loc[0], current_loc[1] - 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
        elif next_loc[0] > front_loc[0]: #should go up
            while pattern != []:
                next = pattern.pop(-1)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, left, down = found_possible_loc_front(elastic_map, current_loc, last)
                if next_loc[0] - current_loc[0] <= 2:
                    down = 0
                if up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif left == 1:
                    current_loc = [current_loc[0], current_loc[1] - 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
    return elastic_map

def greedy_place_back(elastic_map, index, back_order, patterns, locations):
    back_pattern = patterns[back_order[index]]
    back_loc = locations[back_order[index]]
    pattern = copy.deepcopy(back_pattern)
    current_loc = copy.deepcopy(back_loc)
    if index == len(back_order) - 1:
        last = True
    else:
        last = False
    if last:
        while pattern != []:
            next = pattern.pop(0)
            if pattern != []:
                last = 0
            else:
                last = 1
            up, right, down = found_possible_loc_back(elastic_map, current_loc, last)
            if current_loc[0] < len(elastic_map)/2:
                if down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                else:
                    current_loc = [current_loc[0], current_loc[1] + 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
            else:
                if up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                else:
                    current_loc = [current_loc[0], current_loc[1] + 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
    else:
        next_loc = find_close(index, back_order, locations)
        if next_loc[0] < back_loc[0]: #should go down
            while pattern != []:
                next = pattern.pop(0)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, right, down = found_possible_loc_back(elastic_map, current_loc, last)
                if current_loc[0] - next_loc[0] <= 2:
                    up = 0
                if down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif right == 1:
                    current_loc = [current_loc[0], current_loc[1] + 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
        elif next_loc[0] > back_loc[0]: #should go up
            while pattern != []:
                next = pattern.pop(0)
                if pattern != []:
                    last = 0
                else:
                    last = 1
                up, right, down = found_possible_loc_back(elastic_map, current_loc, last)
                if next_loc[0] - current_loc[0] <= 2:
                    down = 0
                if up == 1:
                    current_loc = [current_loc[0] - 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif down == 1:
                    current_loc = [current_loc[0] + 1, current_loc[1]]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next
                elif right == 1:
                    current_loc = [current_loc[0], current_loc[1] + 1]
                    i = current_loc[0]
                    j = current_loc[1]
                    elastic_map[i][j] = next

    return elastic_map
def found_possible_loc_front(elastic_map, current_loc, last):
    up = 0
    left = 0
    down = 0
    if current_loc[0] == len(elastic_map) - 1: #last row
        left = check_left(elastic_map, current_loc, last)
        up = check_up(elastic_map, current_loc, last, 'l')
    elif current_loc[0] == 0: #first row
        left = check_left(elastic_map, current_loc, last)
        down = check_down(elastic_map, current_loc, last, 'l')
    else:
        left = check_left(elastic_map, current_loc, last)
        down = check_down(elastic_map, current_loc, last, 'l')
        up = check_up(elastic_map, current_loc, last, 'l')
    return up, left, down

def found_possible_loc_back(elastic_map, current_loc, last):
    up = 0
    right = 0
    down = 0
    if current_loc[0] == len(elastic_map) - 1:  # last row
        right = check_right(elastic_map, current_loc, last)
        up = check_up(elastic_map, current_loc, last, 'r')
    elif current_loc[0] == 0:  # first row
        right = check_right(elastic_map, current_loc, last)
        down = check_down(elastic_map, current_loc, last, 'r')
    else:
        right = check_right(elastic_map, current_loc, last)
        down = check_down(elastic_map, current_loc, last, 'r')
        up = check_up(elastic_map, current_loc, last, 'r')
    return up, right, down


def check_up(elastic_map, current_loc, last, direc):
    ok = 0
    row = current_loc[0]
    col = current_loc[1]
    if row != 1:
        if last == 1:
            if (elastic_map[row - 2][col] == 'Z' and elastic_map[row-1][col - 1] == 'Z' and elastic_map[row-1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'l':
            if (elastic_map[row - 2][col] == 'Z' and elastic_map[row - 1][col - 1] == 'Z' and elastic_map[row - 1][col + 1] == 'Z'
                    and elastic_map[row - 2][col - 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'r':
            if (elastic_map[row - 2][col] == 'Z' and elastic_map[row - 1][col - 1] == 'Z' and elastic_map[row - 1][col + 1] == 'Z'
                    and elastic_map[row - 2][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    else:
        if last == 1:
            if (elastic_map[row-1][col - 1] == 'Z' and elastic_map[row-1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'l':
            if (elastic_map[row-1][col - 1] == 'Z' and elastic_map[row-1][col + 1] == 'Z' and elastic_map[row-1][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'r':
            if (elastic_map[row-1][col - 1] == 'Z' and elastic_map[row-1][col + 1] == 'Z' and elastic_map[row-1][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok

def check_left(elastic_map, current_loc, last):
    ok = 0
    row = current_loc[0]
    col = current_loc[1]
    if row != 0 and row != len(elastic_map) - 1:
        if last == 1:
            if (elastic_map[row - 1][col - 1] == 'Z' and elastic_map[row+1][col - 1] == 'Z' and elastic_map[row][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row - 1][col - 1] == 'Z' and elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row][col - 2] == 'Z'
                    and elastic_map[row - 1][col - 2] == 'Z' and elastic_map[row + 1][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    elif row == 0:
        if last == 1:
            if (elastic_map[row][col - 2] == 'Z' and elastic_map[row+1][col - 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row][col - 2] == 'Z' and elastic_map[row+1][col - 1] == 'Z' and elastic_map[row+1][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    elif row == len(elastic_map) - 1:
        if last == 1:
            if (elastic_map[row][col - 2] == 'Z' and elastic_map[row-1][col - 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row][col - 2] == 'Z' and elastic_map[row-1][col - 1] == 'Z' and elastic_map[row-1][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok

def check_down(elastic_map, current_loc, last, direc):
    ok = 0
    row = current_loc[0]
    col = current_loc[1]
    if row != len(elastic_map) - 2:
        if last == 1:
            if (elastic_map[row + 2][col] == 'Z' and elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'l':
            if (elastic_map[row + 2][col] == 'Z' and elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z'
            and elastic_map[row + 2][col - 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'r':
            if (elastic_map[row + 2][col] == 'Z' and elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z'
            and elastic_map[row + 2][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    else:
        if last == 1:
            if (elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'l':
            if (elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z' and elastic_map[row + 1][col - 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        elif direc == 'r':
            if (elastic_map[row + 1][col - 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z' and elastic_map[row + 1][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok

def resolve_order(order):
    increase = []
    for i in range(len(order)):
        increase.append(i)
    for i in increase:
        count = 0
        not_found = []
        found = []
        for j in range(len(order)):
            if order[j] == i:
                count += 1
                found.append(j)
        if count == 0:
            not_found.append(i)
        if count > 1:
            first = i - count + 1
            end = i + count - 1
            if first <= 0:
                for j in range(end + 1):
                    if j not in order or j == i:
                        order[found.pop(-1)] = j
                    if len(found) == 0:
                        break

            elif end >= len(order) - 1:
                for j in range(first, len(order)):
                    if j not in order or j == i:
                        order[found.pop(-1)] = j
                    if len(found) == 0:
                        break
            else:
                for j in range(first, end + 1):
                    if j not in order or j == i:
                        order[found.pop(-1)] = j
                    if len(found) == 0:
                        break
def check_right(elastic_map, current_loc, last):
    ok = 0
    row = current_loc[0]
    col = current_loc[1]
    if row != 0 and row != len(elastic_map) - 1:
        if last == 1:
            if (elastic_map[row - 1][col + 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z' and elastic_map[row][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row - 1][col + 1] == 'Z' and elastic_map[row + 1][col + 1] == 'Z' and elastic_map[row][col + 2] == 'Z'
            and elastic_map[row - 1][col + 2] == 'Z' and elastic_map[row + 1][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    elif row == 0:
        if last == 1:
            if (elastic_map[row][col + 2] == 'Z' and elastic_map[row+1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row][col + 2] == 'Z' and elastic_map[row+1][col + 1] == 'Z' and elastic_map[row+1][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
    elif row == len(elastic_map) - 1:
        if last == 1:
            if (elastic_map[row][col + 2] == 'Z' and elastic_map[row-1][col + 1] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
        else:
            if (elastic_map[row][col + 2] == 'Z' and elastic_map[row-1][col + 1] == 'Z' and elastic_map[row-1][col + 2] == 'Z'):
                ok = 1
                return ok
            else:
                return ok
def clean_map(map):
    z_col = []
    for i in range(len(map[0])):
        all_z = 1
        for row in map:
            if row[i] != 'Z':
                all_z = 0
                break
        if all_z == 1:
            z_col.append(i)
    z_col.sort(reverse=True)
    for col in z_col:
        for i in range(len(map)):
            map[i].pop(col)
    return map

def normal_fill(map):
    max = 0
    for row in map:
        if len(row) > max:
            max = len(row)
    for i in range(len(map)):
        if len(map[i]) != max:
            map[i] = map[i] + ['Z'] * (max - len(map[i]))

def find_front_order(front_loc, rows):
    y_loc = []
    front_or = []
    for loc in front_loc:
        if loc[1] not in y_loc:
            y_loc.append(loc[1])
    y_loc.sort()
    for y in y_loc:
        found = []
        for i in range(len(front_loc)):
            if front_loc[i][1] == y:
                found.append(front_loc[i])
        if len(found) == 1:
            front_or.insert(0, front_loc.index(found[0]))
        else:
            x_loc = []
            for loc in found:
                x_loc.append(loc[0])
            up = min(x_loc)
            down = rows - max(x_loc) - 1
            if up > down:
                x_loc.sort(reverse=True)
                for x in x_loc:
                    for loc in found:
                        if loc[0] == x:
                            front_or.append(front_loc.index(loc))
                            break
            else:
                x_loc.sort()
                for x in x_loc:
                    for loc in found:
                        if loc[0] == x:
                            front_or.insert(0, front_loc.index(loc))
                            break
    return front_or

def find_back_order(back_loc, rows):
    y_loc = []
    front_or = []
    for loc in back_loc:
        if loc[1] not in y_loc:
            y_loc.append(loc[1])
    y_loc.sort(reverse=True)
    for y in y_loc:
        found = []
        for i in range(len(back_loc)):
            if back_loc[i][1] == y:
                found.append(back_loc[i])
        if len(found) == 1:
            front_or.insert(0, back_loc.index(found[0]))
        else:
            x_loc = []
            for loc in found:
                x_loc.append(loc[0])
            up = min(x_loc)
            down = rows - max(x_loc) - 1
            if up > down:
                x_loc.sort(reverse=True)
                for x in x_loc:
                    for loc in found:
                        if loc[0] == x:
                            front_or.append(back_loc.index(loc))
                            break
            else:
                x_loc.sort()
                for x in x_loc:
                    for loc in found:
                        if loc[0] == x:
                            front_or.insert(0, back_loc.index(loc))
                            break
    return front_or

def find_close(index, front_order, locations):
    distance = []
    cur_loc = locations[front_order[index]]
    for i in range(index + 1, len(front_order)):
        distance.append(math.fabs(cur_loc[0] - locations[front_order[i]][0]))
    min_dist = min(distance)
    indx = index + distance.index(min_dist) + 1
    return locations[front_order[indx]]

def dist(loc1, loc2):
    x = math.fabs(loc1[0] - loc2[0])
    y = math.fabs(loc1[1] - loc2[1])
    return math.sqrt(x**2 + y**2)