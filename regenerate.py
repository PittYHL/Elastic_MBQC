from dense import *

with open('Benchmarks/hlf27.txt') as f:
    lines = f.readlines()
circuit= lines.copy()
f.close()
def transform_num(t1, t2):
    if 1 <= t1 <= 4:
        t1 = t1 - 1
    elif 7 <= t1 <= 17:
        t1 = t1 - 3
    elif 19 <= t1 <= 26:
        t1 = t1 - 4
    if 1 <= t2 <= 4:
        t2 = t2 - 1
    elif 7 <= t2 <= 17:
        t2 = t2 - 3
    elif 19 <= t2 <= 26:
        t2 = t2 - 4
    if t1 == t2:
        t2 = ''
    return t1, t2

with open('Benchmarks/real_hlf27.txt', 'w') as f:
    for current in circuit:
        gate, t1, t2, _, name = de_gate(current)
        t1, t2 = transform_num(t1, t2)
        f.write(name + ' ' + str(t1) + ' ' + str(t2)+ '\n')
f.close()