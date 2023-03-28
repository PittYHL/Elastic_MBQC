#method that make physical gates more dense
from gate_blocks import *
import copy

def dense(qubits, physical_gate):
    gates = copy.deepcopy(physical_gate)
    DAG = []
    layer = []
    layer_q = []
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
    DAG.append(layer_q) #generate normal DAG
    front_barrier = [-1]*4
    back_barrier = [-1] * 4
    for i in range(len(DAG)):
        for j in range(len(DAG[i])):
            if DAG[i][j]['type'] == 'D':
                if front_barrier[DAG[i][j]['t1']] == -1:
                    front_barrier[DAG[i][j]['t1']] = i
                if front_barrier[DAG[i][j]['t2']] == -1:
                    front_barrier[DAG[i][j]['t2']] = i
    for i in reversed(range(len(DAG))):
        for j in range(len(DAG[i])):
            if DAG[i][j]['type'] == 'D':
                if back_barrier[DAG[i][j]['t1']] == -1:
                    back_barrier[DAG[i][j]['t1']] = i
                if back_barrier[DAG[i][j]['t2']] == -1:
                    back_barrier[DAG[i][j]['t2']] = i
    return DAG

