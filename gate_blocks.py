import copy
import math

H = ['X','Y','Y','Y']
P = ['X','X','P','X']
S = ['X','X','P','X'] #pi/2
Z = ['X','X','P','X'] #pi
T = ['X','X','P','X'] #pi/4
I1 = ['X','X']
I2 = ['X','X','X','X']
I3 = ['X','X','X','X','X','X']
RX = ['X','R']
X = ['X', 'P']
A = ['X','R','R','R']
RZ = ['X','X','R','X']
CNOT = [['X','Y','Y','Y','Y','Y'],['Z','Z','Z','Y','Z','Z'],['X','X','X','Y','X','X']]
SW = [['X','X','S','X'],['Z','S','X','Z'],['X','X','S','X']]
CPS = [['X','X','P','X'],['Z','P','X','Z'],['X','X','P','X']]
CZS = [['X','X','P','X'],['Z','P','X','Z'],['X','X','P','X']]
DCNOT1 = [ ['X','Y','Y','Y'],
['Z','Z','Z','Y'],
['X','X','X','Y'],
['Z','Z','Z','Z'],
['X','Y','Y','Y']]

DCNOT2 = [ ['X','Y','Y','Y'],
['Z','Y','Z','Z'],
['Y','Y','X','X'],
['Y','Z','Z','Z'],
['Y','Y','Y','Y']]

def de_gate(gate):
    X = gate.split()
    match X[0]:
        case 'H':
            return H, int(X[1]), int(X[1]), int(X[1]), 'H'
        case 'P':
            return P, int(X[1]), int(X[1]), int(X[1]), 'P'
        case 'S':
            return S, int(X[1]), int(X[1]), int(X[1]), 'S'
        case 'Z':
            return Z, int(X[1]), int(X[1]), int(X[1]), 'Z'
        case 'T':
            return T, int(X[1]), int(X[1]), int(X[1]), 'T'
        case 'X':
            return X, int(X[1]), int(X[1]), int(X[1]), 'X'
        case 'RX':
            return RX, int(X[1]), int(X[1]), int(X[1]), 'RX'
        case 'RZ':
            return RZ, int(X[1]), int(X[1]), int(X[1]), 'RZ'
        case 'A':
            return A, int(X[1]), int(X[1]), int(X[1]), 'A'
        case 'CNOT':
            return CNOT, int(X[1]), int(X[2]), int(X[2]), 'CNOT'
        case 'CZ':
            return CZS, int(X[1]), int(X[2]), int(X[2]), 'CZ'
        case 'CP':
            return CPS, int(X[1]), int(X[2]), int(X[2]), 'CP'
        case 'DCN1':
            return DCNOT1, int(X[1]), int(X[2]), int(X[3]), 'DCN1'
        case 'DCN2':
            return DCNOT2, int(X[1]), int(X[2]), int(X[3]), 'DCN2'
        case 'SW':
            return SW, int(X[1]), int(X[1]), int(X[2]), 'SW'
        case 'I1':
            return I1, int(X[1]), int(X[1]), int(X[1]), 'I1'
        case 'I2':
            return I2, int(X[1]), int(X[1]), int(X[1]), 'I2'
        case 'I3':
            return I3, int(X[1]), int(X[1]), int(X[1]), 'I3'
def swap(map, t3, t4, tracker, dir, physical_gate):
    qubits = int((len(map) + 1) / 2)
    while tracker[t4] - tracker[t3] > 2:
        physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t3], 't2': tracker[t3] + 1})
        new_swap(map, t3, tracker.index(tracker[t3] + 1), tracker)
        physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t4] - 1, 't2': tracker[t4]})
        new_swap(map, tracker.index(tracker[t4] - 1), t4, tracker)
    if math.fabs(tracker[t4] - tracker[t3]) == 2:
        if dir == 'u':
            t1 = tracker.index(tracker[t3] + 1)
            t2 = t4
        else:
            t2 = tracker.index(tracker[t4] - 1) #need to debug here
            t1 = t3
        p_t1 = tracker[t1]
        p_t2 = tracker[t2]
        while (tracker[t1] != p_t2 and tracker[t2] != p_t1):
            if len(map[(tracker[t1]+1) * 2]) != len(map[(tracker[t1]+1) * 2 - 1]) or len(map[(tracker[t1]+1) * 2 - 1]) != len(map[tracker[t1] * 2]) or len(map[(tracker[t1]+1) * 2]) != len(map[tracker[t1] * 2]):
                fill_map(qubits, map)
            if dir == 'u':
                physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t2] - 1, 't2': tracker[t2]})
                map[(tracker[t2] - 1) * 2].extend(SW[0])
                map[(tracker[t2] - 1) * 2 + 1].extend(SW[1])
                map[tracker[t2] * 2].extend(SW[2])
                index = tracker.index(tracker[t2] - 1)
                tracker[t2] = tracker[t2] - 1
                tracker[index] = tracker[index] + 1
            else:
                physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t1], 't2': tracker[t1] + 1})
                map[(tracker[t1]) * 2].extend(SW[0])
                map[(tracker[t1] + 1) * 2 - 1].extend(SW[1])
                map[(tracker[t1] + 1) * 2].extend(SW[2])
                index = tracker.index(tracker[t1] + 1)
                tracker[t1] = tracker[t1] + 1
                tracker[index] = tracker[index] - 1
    fill_map(qubits, map)

def new_swap(map, t1, t2, tracker): #t1 location is lower than t2
    if len(map[(tracker[t1]+1) * 2]) != len(map[(tracker[t1]+1) * 2 - 1]) or len(map[(tracker[t1]+1) * 2 - 1]) != len(map[tracker[t1] * 2]) or len(map[(tracker[t1]+1) * 2]) != len(map[tracker[t1] * 2]):
        fill_map(int((len(map) + 1)/2), map)
    map[(tracker[t1] + 1) * 2].extend(SW[2])
    map[(tracker[t1] + 1) * 2 - 1].extend(SW[1])
    map[tracker[t1] * 2].extend(SW[0])
    tracker[t1] = tracker[t1] + 1
    tracker[t2] = tracker[t2] - 1

def lookahead(gates, t1, t2, tracker, index, map, current): #the look ahead of CP and CNOT are different
    for i in range(index + 1, len(gates)):
        gate, t3, t4, _ = de_gate(gates[i])
        tracker1 = copy.deepcopy(tracker)  # up to down
        tracker2 = copy.deepcopy(tracker)  # down to up
        if gate == CNOT or gate == CZS or gate == CPS:
            tracker1[tracker1.index(tracker1[t1] + 1)] = tracker1[tracker1.index(tracker1[t1] + 1)] - 1
            tracker1[t1] = tracker1[t1] + 1
            tracker2[tracker2.index(tracker1[t2] - 1)] = tracker2[tracker2.index(tracker2[t2] - 1)] + 1
            tracker2[t2] = tracker2[t2] - 1
            if current == CPS or current == CZS:
                tracker1[tracker1.index(tracker1[t1] + 1)] = tracker1[tracker1.index(tracker1[t1] + 1)] - 1
                tracker2[tracker2.index(tracker1[t2] - 1)] = tracker2[tracker2.index(tracker2[t2] - 1)] + 1
                tracker1[t1] = tracker1[t1] + 1
                tracker2[t2] = tracker2[t2] - 1
            new_l1 = math.fabs(tracker1[t3] - tracker1[t4])
            new_l2 = math.fabs(tracker2[t3] - tracker2[t4])
            if (new_l2 - new_l1) > 0:
                new_swap(map, t1, tracker.index(tracker[t1] + 1), tracker)
                fill_map(int((len(map) + 1)/2), map)
                return map, 'd'
            else:
                new_swap(map, tracker.index(tracker[t2] - 1), t2, tracker)
                fill_map(int((len(map) + 1) / 2), map)
                return map, 'u'
    new_swap(map, t1, tracker.index(tracker[t1] + 1), tracker)
    fill_map(int((len(map) + 1) / 2), map)
    return map, 'd'

def fill_map(n,map):
    max = 0
    for i in range(n):
        if len(map[i*2]) > max:
            max = len(map[i*2])
    for i in range(n):
        if len(map[i*2]) < max:
            map[i * 2].extend(['X']* (max - len(map[i*2])))
        if (i < n - 1 and len(map[i*2+1]) < max):
            map[i * 2 + 1].extend(['Z']* (max - len(map[i*2 + 1])))

def eliminate_redundant(map, qubits):
    new_map = copy.deepcopy(map)
    end = 1
    tracker = [0] * (qubits * 2 -1)
    position = [0] * (qubits * 2 -1)
    while (end != len(new_map[0])):
        for i in range(qubits):
            if (new_map[i*2][end - 1] ==  new_map[i*2][end] == 'X'):
                tracker[i*2] = 1
                position[i*2] = end - 1
        for i in range(qubits - 1):
            if (new_map[i*2 + 1][end - 1] ==  new_map[i*2 + 1][end] == 'Z'):
                tracker[i*2 + 1] = 1
                position[i*2 + 1] = end - 1
        if (all(ele == 1 for ele in tracker)):
            valid = 1
            for j in range(len(position) - 1):
                if position[j+1] - position[j] > 1:
                    tracker[j] = 0
                    valid = 0
                elif position[j] - position[j + 1] > 1:
                    tracker[j+1] = 0
                    valid = 0
            if valid:
                tracker = [0] * (qubits * 2 - 1)
                for i in range(qubits * 2 - 1):
                    del new_map[i][position[i]]
                    del new_map[i][position[i]]
                end = end - 2
        end += 1
    return new_map

def cal_utilization(map, qubits):
    redundancy = 0
    for i in range(qubits):
        end = 1
        while(end < len(map[0])):
            if (map[i*2][end-1] == map[i*2][end] == 'X'):
                redundancy = redundancy + 2
                end = end + 2
            else:
                end = end + 1
    for i in range(qubits*2 - 1):
        end = 0
        while(end < len(map[0])):
            if (map[i][end] == 'Z'):
                end = end + 1
                redundancy = redundancy + 1
            else:
                end = end + 1
    return redundancy

def cal_utilization2(map, rows): #also count x measurement
    useful = 0
    for row in map:
        for element in row:
            if element != 'Z':
                useful = useful + 1
    utilization = useful/(rows * len(map[0]))
    return utilization, useful

def num_photons(map):
    num = 0
    for row in map:
        for p in row:
            if p!= 'Z':
                num = num + 1
    return  num



