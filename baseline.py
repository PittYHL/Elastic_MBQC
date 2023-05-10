import numpy as np
import math
from gate_blocks import *
from scheduling import *
from dense import *
def biuld_DAG(gates):
    DAG_list = gates.copy()
direc = 'd'
qubits = 4
physical_gate = []
rows = 7
tracker= []
map = []
for i in range(qubits*2-1):
    map.append([])
for i in range(qubits):
    tracker.append(i)
with open('Benchmarks/qft4.txt') as f:
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
schedule = scheduling(qubits,DAG, rows)
np_map = np.array(schedule)
#np.savetxt("qft4_sche.csv", np_map, fmt = '%s',delimiter=",")
new_map = eliminate_redundant(map, qubits)
new_map = new_eliminate_redundant(map, qubits)
redun2 = cal_utilization(map, qubits)
useful2 = len(map) * len(map[0]) - redun2
old_uti2 = useful2/(len(map[0])*rows)
uti0, use0 = cal_utilization2(dense_map, rows)
uti1, use1 = cal_utilization2(schedule, rows)
uti2, use2 = cal_utilization2(map, rows)

#np.savetxt("result/iqp7_base.csv", np_map, fmt = '%s',delimiter=",")
#np.savetxt("result/iqp7_base_el.csv", np_new_map, fmt = '%s',delimiter=",")
#np_map.tofile('hlf4_base.csv', sep = ',')
print(str(len(dense_map[0])))
print(str(uti0))
print(num_photons(dense_map))
print(str(len(schedule[0])))
print(str(uti1))
print(num_photons(schedule))
print(str(len(map[0])))
print(str(old_uti2))
print(str(uti2))
print(num_photons(map))