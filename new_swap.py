import math
from gate_blocks import *

def intel_swap(map, t3, t4, tracker, circuit, physical_gate):
    qubits = int((len(map) + 1) / 2)
    while tracker[t4] - tracker[t3] > 2:
        physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t3], 't2': tracker[t3] + 1})
        new_swap(map, t3, tracker.index(tracker[t3] + 1), tracker)
        physical_gate.append({'gate': 'SW', 'type':'D', 't1': tracker[t4] - 1, 't2': tracker[t4]})
        new_swap(map, tracker.index(tracker[t4] - 1), t4, tracker)
    if math.fabs(tracker[t4] - tracker[t3]) == 2:
        ta1 = -1
        ta2 = -1
        for current in circuit:
            gate, ta1, ta2, _, name = de_gate(current)
            if ta1 != ta2:
                break
        if ta1 == ta2:
            dir = 'u'
        else:
            if tracker[t3] - tracker[t4] == 2:
                temp_t1 = copy.deepcopy(tracker)
                temp_t2 = copy.deepcopy(tracker)
                current_dis = math.fabs(tracker[ta1] - tracker[ta2])
                temp_t1[tracker.index(tracker[t3] - 1)] = temp_t1[tracker.index(tracker[t3] - 1)] + 1
                temp_t1[t3] = temp_t1[t3] - 1
                temp_t2[tracker.index(tracker[t4] + 1)] = temp_t2[tracker.index(tracker[t4] + 1)] - 1
                temp_t2[t4] = temp_t2[t4] + 1
                new_dist1 = math.fabs(temp_t1[ta1] - temp_t1[ta2])
                new_dist2 = math.fabs(temp_t2[ta1] - temp_t2[ta2])
                if new_dist1 < new_dist2:
                    dir = 'u'
                else:
                    dir = 'd'
            elif tracker[t4] - tracker[t3] == 2:
                temp_t1 = copy.deepcopy(tracker)
                temp_t2 = copy.deepcopy(tracker)
                current_dis = math.fabs(tracker[ta1] - tracker[ta2])
                temp_t1[tracker.index(tracker[t4] - 1)] = temp_t1[tracker.index(tracker[t4] - 1)] + 1
                temp_t1[t4] = temp_t1[t4] - 1
                temp_t2[tracker.index(tracker[t3] + 1)] = temp_t2[tracker.index(tracker[t3] + 1)] - 1
                temp_t2[t3] = temp_t2[t3] + 1
                new_dist1 = math.fabs(temp_t1[ta1] - temp_t1[ta2])
                new_dist2 = math.fabs(temp_t2[ta1] - temp_t2[ta2])
                if new_dist1 < new_dist2:
                    dir = 'u'
                else:
                    dir = 'd'
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