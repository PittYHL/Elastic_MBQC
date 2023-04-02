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
rows = 9
extra_row = rows - 2 * qubits + 1
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
            if gate['gate'] == 'I':
                middle_DAG[i].append(gate)
            elif gate['type'] == 'S' and i < gate['front'][gate['t1']]:
                front_DAG[i].append(gate)
            elif gate['type'] == 'S' and i > gate['front'][gate['t1']] and i < gate['back'][gate['t1']]:
                middle_DAG[i].append(gate)
            elif gate['type'] == 'S' and i > gate['back'][gate['t1']]:
                back_DAG[i].append(gate)
            elif gate['type'] == 'D':
                middle_DAG[i].append(gate)

    map = []
    for i in range(n * 2 - 1):
        map.append([])
    for i in range(len(DAG)):
        length = 4 #record length iof the DAG layer
        for gate in DAG[i]:
            if gate['gate'] == 'CNOT':
                length = 6
        for gate in DAG[i]:
            pattern, t1, t2, t3, name = de_gate(gate['gate'] + ' 0 0 ')
            if gate['type'] == 'S':
                t1 = gate['t1']
                if length == 6 and (i == 0 or t1 not in DAG[i-1][0]['active']):
                    map[gate['t1'] * 2] = map[gate['t1'] * 2] + ['Z','Z'] + pattern
                elif length == 6 and (i == len(DAG) - 1 or t1 not in DAG[i+1][0]['active']):
                    map[gate['t1'] * 2] = map[gate['t1'] * 2] + pattern + ['Z', 'Z']
                else:
                    map[gate['t1']*2] = map[gate['t1']*2] + pattern
            elif gate['type'] == 'D':
                map[gate['t1'] * 2].extend(pattern[0])
                map[gate['t2'] * 2].extend(pattern[2])
                if gate['t1'] - gate['t2'] > 0:
                    map[gate['t1'] * 2 - 1].extend(pattern[1])
                else:
                    map[gate['t2'] * 2 - 1].extend(pattern[1])
        new_fill_map(n,map, gate['active'])
    return map
