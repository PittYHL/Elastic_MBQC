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
    front_barrier = [-1]*4
    back_barrier = [-1] * 4
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
    if count2 != count1:
        raise Exception('check why the two DAG do not have the same gate number')
    return newDAG

def fill_new_map(n,DAG):
    map = []
    for i in range(n * 2 - 1):
        map.append([])
    for i in range(len(DAG)):
        for gate in DAG[i]:
            pattern, t1, t2, t3, name = de_gate(gate['gate'] + ' 0 0 ')
            if gate['type'] == 'S':
                map[gate['t1']*2] = map[gate['t1']*2] + pattern
            elif gate['type'] == 'D':
                map[gate['t1'] * 2].extend(pattern[0])
                map[gate['t2'] * 2].extend(pattern[2])
                if gate['t1'] - gate['t2'] > 0:
                    map[gate['t1'] * 2 - 1].extend(pattern[1])
                else:
                    map[gate['t2'] * 2 - 1].extend(pattern[1])
        fill_map(n,map)
    return map

