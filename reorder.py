import numpy as np
import math
from gate_blocks import *
from new_swap import *
import copy
from dense import *
def biuld_DAG(gates):
    DAG_list = gates.copy()
qubits = 4
physical_gate = []
tracker= []
map = []
direc = 'd'
for i in range(qubits*2-1):
    map.append([])
for i in range(qubits):
    tracker.append(i)
with open('Benchmarks/iqp4b.txt') as f:
    lines = f.readlines()
circuit= lines.copy()
layer = []
tracker = [] #track physical location
for i in range(qubits):
    tracker.append(i)
next = 0
for current in circuit:
    gate, t1, t2, _, name = de_gate(current)
    if t1 != t2:
        if next == 1:
            break
        t3 = t1
        t4 = t2
        next = 1

while math.fabs(tracker[t3] - tracker[t4]) != 1:
    if tracker[t3] - tracker[t4] > 2:
        tracker[tracker.index(tracker[t3] - 1)] = tracker[tracker.index(tracker[t3] - 1)] + 1
        tracker[t3] = tracker[t3] - 1
        tracker[tracker.index(tracker[t4] + 1)] = tracker[tracker.index(tracker[t4] + 1)] - 1
        tracker[t4] = tracker[t4] + 1
    elif tracker[t4] - tracker[t3]> 2:
        tracker[tracker.index(tracker[t3] + 1)] = tracker[tracker.index(tracker[t3] + 1)] - 1
        tracker[t3] = tracker[t3] + 1
        tracker[tracker.index(tracker[t4] - 1)] = tracker[tracker.index(tracker[t4] - 1)] + 1
        tracker[t4] = tracker[t4] - 1
    elif tracker[t3] - tracker[t4] == 2:
        temp_t1 = copy.deepcopy(tracker)
        temp_t2 = copy.deepcopy(tracker)
        current_dis = math.fabs(tracker[t1] - tracker[t2])
        temp_t1[tracker.index(tracker[t3] - 1)] = temp_t1[tracker.index(tracker[t3] - 1)] + 1
        temp_t1[t3] = temp_t1[t3] - 1
        temp_t2[tracker.index(tracker[t4] + 1)] = temp_t2[tracker.index(tracker[t4] + 1)] - 1
        temp_t2[t4] = temp_t2[t4] + 1
        new_dist1 = math.fabs(temp_t1[t1] - temp_t1[t2])
        new_dist2 = math.fabs(temp_t2[t1] - temp_t2[t2])
        if new_dist1 < new_dist2:
            tracker = temp_t1
        else:
            tracker = temp_t2
    elif tracker[t4] - tracker[t3] == 2:
        temp_t1 = copy.deepcopy(tracker)
        temp_t2 = copy.deepcopy(tracker)
        current_dis = math.fabs(tracker[t1] - tracker[t2])
        temp_t1[tracker.index(tracker[t4] - 1)] = temp_t1[tracker.index(tracker[t4] - 1)] + 1
        temp_t1[t4] = temp_t1[t4] - 1
        temp_t2[tracker.index(tracker[t3] + 1)] = temp_t2[tracker.index(tracker[t3] + 1)] - 1
        temp_t2[t3] = temp_t2[t3] + 1
        new_dist1 = math.fabs(temp_t1[t1] - temp_t1[t2])
        new_dist2 = math.fabs(temp_t2[t1] - temp_t2[t2])
        if new_dist1 < new_dist2:
            tracker = temp_t1
        else:
            tracker = temp_t2
new_circuit = []
for gate in circuit:
    X = gate.split()
    if X[0] == 'H' or X[0] == 'P' or X[0] == 'S' or X[0] == 'Z' or X[0] == 'RX' or X[0] == 'RZ' or X[0] == 'X' or X[0] == 'T':
        t1 = str(tracker[int(X[1])])
        new_circuit.append(X[0] + ' ' + t1)
    else:
        t1 = str(tracker[int(X[1])])
        t2 = str(tracker[int(X[2])])
        new_circuit.append(X[0] + ' ' + t1 + ' ' + t2)

tracker= []
for i in range(qubits):
    tracker.append(i)
while(new_circuit!=[]):
    current = new_circuit.pop(0)
    gate, t1, t2, _, name = de_gate(current)
    if (gate == H or gate == P or gate == S or gate == T or gate == Z or gate == RX or gate == A):
        if t1 in layer:
            layer = []
            layer.append(t1)
            fill_map(qubits,map)
        else:
            layer.append(t1)
        map[tracker[t1]*2] = map[tracker[t1]*2] + gate
        #physical_gate.append(name + str(tracker[t1]))
        physical_gate.append({'gate':name, 'type':'S', 't1':tracker[t1]})
    elif(gate==CNOT):
        if t1 in layer or t2 in layer:
            layer = []
            layer.append(t1)
            layer.append(t2)
            fill_map(qubits,map)
        else:
            layer.append(t1)
            layer.append(t2)
        if tracker[t1] - tracker[t2] == 1:
            map[tracker[t1] * 2].extend(CNOT[0])
            map[tracker[t2] * 2 + 1].extend(CNOT[1])
            map[tracker[t2] * 2].extend(CNOT[2])
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] == -1:
            map[tracker[t1] * 2].extend(CNOT[0])
            map[tracker[t1] * 2 + 1].extend(CNOT[1])
            map[tracker[t2] * 2].extend(CNOT[2])
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] > 1:
            #worst case
            intel_swap(map, t2, t1, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CNOT[0])
            map[tracker[t2] * 2 + 1].extend(CNOT[1])
            map[tracker[t2] * 2].extend(CNOT[2])
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            intel_swap(map, t1, t2, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CNOT[0])
            map[tracker[t1] * 2 + 1].extend(CNOT[1])
            map[tracker[t2] * 2].extend(CNOT[2])
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
    elif(gate==CZS):
        if t1 in layer or t2 in layer:
            layer = []
            layer.append(t1)
            layer.append(t2)
            fill_map(qubits,map)
        else:
            layer.append(t1)
            layer.append(t2)
        if tracker[t1] - tracker[t2] == 1:
            map[tracker[t1] * 2].extend(CZS[0])
            map[tracker[t2] * 2 + 1].extend(CZS[1])
            map[tracker[t2] * 2].extend(CZS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] == -1:
            map[tracker[t1] * 2].extend(CZS[0])
            map[tracker[t1] * 2 + 1].extend(CZS[1])
            map[tracker[t2] * 2].extend(CZS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] > 1:
            intel_swap(map, t2, t1, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CZS[0])
            map[tracker[t2] * 2 + 1].extend(CZS[1])
            map[tracker[t2] * 2].extend(CZS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            intel_swap(map, t1, t2, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CZS[0])
            map[tracker[t1] * 2 + 1].extend(CZS[1])
            map[tracker[t2] * 2].extend(CZS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
    elif (gate == CPS):
        if t1 in layer or t2 in layer:
            layer = []
            layer.append(t1)
            layer.append(t2)
            fill_map(qubits, map)
        else:
            layer.append(t1)
            layer.append(t2)
        if tracker[t1] - tracker[t2] == 1:
            map[tracker[t1] * 2].extend(CPS[0])
            map[tracker[t2] * 2 + 1].extend(CPS[1])
            map[tracker[t2] * 2].extend(CPS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] == -1:
            map[tracker[t1] * 2].extend(CPS[0])
            map[tracker[t1] * 2 + 1].extend(CPS[1])
            map[tracker[t2] * 2].extend(CPS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        elif tracker[t1] - tracker[t2] > 1:
            intel_swap(map, t2, t1, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CPS[0])
            map[tracker[t2] * 2 + 1].extend(CPS[1])
            map[tracker[t2] * 2].extend(CPS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            intel_swap(map, t1, t2, tracker, new_circuit, physical_gate)
            map[tracker[t1] * 2].extend(CPS[0])
            map[tracker[t1] * 2 + 1].extend(CPS[1])
            map[tracker[t2] * 2].extend(CPS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
fill_map(qubits,map)
print(physical_gate[0]["gate"])
DAG = dense(qubits, physical_gate)
dense_map = cons_new_map(qubits,DAG)
new_map = eliminate_redundant(map, qubits)
new_map = new_eliminate_redundant(map, qubits)
redun0 = cal_utilization(map, qubits)
redun1 = cal_utilization(dense_map, qubits)
redun2 = cal_utilization(new_map, qubits)
utilization0 = 1 - redun0/(len(map[0])*len(map))
utilization1 = 1 - redun1/(len(dense_map[0])*len(dense_map))
utilization2 = 1 - redun2/(len(new_map[0])*len(new_map))
np_map = np.array(dense_map)
np_new_map = np.array(new_map)
#np.savetxt("result/iqp7_base.csv", np_map, fmt = '%s',delimiter=",")
#np.savetxt("result/iqp7_base_el.csv", np_new_map, fmt = '%s',delimiter=",")
#np_map.tofile('hlf4_base.csv', sep = ',')
print(str(len(map[0])))
print(str(utilization0))
print(num_photons(map))
print(str(len(dense_map[0])))
print(str(utilization1))
print(num_photons(dense_map))
print(str(len(new_map[0])))
print(str(utilization2))
print(num_photons(new_map))