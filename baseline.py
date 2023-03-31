import numpy as np
import math
from gate_blocks import *
from dense import *
def biuld_DAG(gates):
    DAG_list = gates.copy()
direc = 'u'
qubits = 4
physical_gate = []
tracker= []
map = []
for i in range(qubits*2-1):
    map.append([])
for i in range(qubits):
    tracker.append(i)
with open('Benchmarks/iqp4b.txt') as f:
    lines = f.readlines()
circuit= lines.copy()
layer = []
while(circuit!=[]):
    current = circuit.pop(0)
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
            swap(map, t2, t1, tracker, direc, physical_gate)
            map[tracker[t1] * 2].extend(CNOT[0])
            map[tracker[t2] * 2 + 1].extend(CNOT[1])
            map[tracker[t2] * 2].extend(CNOT[2])
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            swap(map, t1, t2, tracker, direc, physical_gate)
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
            swap(map, t2, t1, tracker, direc, physical_gate)
            map[tracker[t1] * 2].extend(CZS[0])
            map[tracker[t2] * 2 + 1].extend(CZS[1])
            map[tracker[t2] * 2].extend(CZS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            swap(map, t1, t2, tracker, direc, physical_gate)
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
            swap(map, t2, t1, tracker, direc, physical_gate)
            map[tracker[t1] * 2].extend(CPS[0])
            map[tracker[t2] * 2 + 1].extend(CPS[1])
            map[tracker[t2] * 2].extend(CPS[2])
            temp = tracker[t1]
            tracker[t1] = tracker[t2]
            tracker[t2] = temp
            physical_gate.append({'gate':name, 'type':'D', 't1':tracker[t1], 't2':tracker[t2]})
        else:
            swap(map, t1, t2, tracker, direc, physical_gate)
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