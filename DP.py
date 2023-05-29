import copy

def DP(ori_map, qubits):
    new_map = []
    for rows in ori_map:
        new_map.append([])
        for item in rows:
            if item != 'Z' and item != 'X':
                new_map[-1].append(1)
            elif item == 'X':
                new_map[-1].append(2)
            else:
                new_map[-1].append(0)
    gen_index(new_map)

def gen_index(map):
    cut = []
    s_row = []
    for i in range(1, len(map)-1, 2):
        rowcut = []
        j = 0
        while j < len(map[0]):
            if map[i][j] != 0:
                rowcut.append(j)
                # if j + 1 < len(map[0]):
                #     if map[i][j+1] == 1:
                #         j = j + 1
            j = j + 1
        cut.append(rowcut)

    for i in range(0, len(cut) - 1):
        temp_row = cut[i] + cut[i + 1]
        temp_row.sort()
        s_row.append(copy.deepcopy(temp_row))
    s_row.insert(0, cut[0])
    s_row.append(cut[-1])
    first = []
    last = []
    qubit = 0
    for i in range(0, len(map), 2):
        for j in range(len(map[i])):
            if map[i][j] != 0:
                front = s_row[qubit][0] - j
                break
        for j in reversed(range(len(map[i]))):
            if map[i][j] != 0:
                back = j - s_row[qubit][-1]
                break
        qubit = qubit + 1
        first.append(front)
        last.append(back)
        gen_DAG(map,s_row)
    print('g')

def gen_DAG(map, s_row):
    indexes = []
    for index in s_row:
        indexes = indexes + index
    indexes = [*set(indexes)]
    indexes.sort()
    nodes = []
    for i in range(len(s_row)):
        nodes.append([])
    A = 0
    B = 0
    C = 0
    W = 0
    index = 0
    while index < len(indexes):
        for i in range(1, len(map)-1, 2):
            if map[i][indexes[index]] != 0:
                if map[i][indexes[index] + 1] != 0:
                    node = 'B' + str(B)
                    loc = int((i-1)/2)
                    nodes[loc].append(node)
                    nodes[loc + 1].append(node)
                    B = B + 1
                elif map[i][indexes[index] - 1] == 0:
                    node = 'A' + str(A)
                    loc = int((i - 1) / 2)
                    nodes[loc].append(node)
                    nodes[loc + 1].append(node)
                    A =  A + 1
        index = index + 1
    print('g')

