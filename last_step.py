import copy
from itertools import *
from dense import *
maximum = 5
import numpy as np
from dense import convert_new_map2

def combination(final_shapes):
    shortest_shape = []
    shortest_depth = 100000
    indexes = []
    for shape in final_shapes:
        if len(shape[0]) < shortest_depth:
            shortest_depth = len(shape[0])
    for shape in final_shapes:
        if len(shape[0]) == shortest_depth:
            indexes.append(final_shapes.index(shape))
            shortest_shape.append(shape)
    shortest_shape, _ = sort_shape(shortest_shape, indexes)
    shortest_shape = double_shape(shortest_shape)
    arr = []
    for i in range(len(shortest_shape)):
        arr.append(i)
    combina = list(combinations(arr, 2))
    original = original_reduction(shortest_shape)
    comb = comb_reduction(shortest_shape, combina)
    print('g')

def sort_shape(shapes, old_indexes):
    indexes = []
    if len(shapes) <= maximum:
        for i in range(len(shapes)):
            indexes.append(old_indexes[i])
        return shapes, indexes
    else:
        temp_shapes = copy.deepcopy(shapes)
        spaces = []
        shortest_shape = []
        for shape in shapes:
            space = check_space(shape)
            spaces.append(space)
        temp_spaces = copy.deepcopy(spaces)
        temp_spaces.sort(reverse=True)
        while len(shortest_shape) != maximum:
            depth = temp_spaces.pop(0)
            index = spaces.index(depth)
            spaces.pop(index)
            shape = temp_shapes.pop(index)
            indexes.append(old_indexes[shapes.index(shape)])
            shortest_shape.append(shape)
        return shortest_shape, indexes

def check_space(shape):
    space = 0
    for row in shape:
        for j in range(len(row)):
            if row[j] != 0:
                space = space + j
                break
        for j in reversed(range(len(row))):
            if row[j] != 0:
                space = space + len(row) - j - 1
                break
    return space

def double_shape(shortest_shape):
    new_shapes = []
    for shape in shortest_shape:
        new_shape = []
        for row in reversed(shape):
            new_shape.append(row)
        new_shapes.append(new_shape)
    shortest_shape = shortest_shape + new_shapes
    return shortest_shape

def original_reduction(shortest_shape):
    reductions = []
    index = -1
    for shape in shortest_shape:
        index = index + 1
        new_shape = []
        for row in shape:
            new_shape.append(row + row)
        back_locs = []
        for row in shape:
            for j in reversed(range(len(row))):
                if row[j] != 0:
                    back_locs.append(j + 1)
                    break
                elif j == 0:
                    back_locs.append(0)
        found_reduc = 1
        for i in range(len(new_shape)):
            if new_shape[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc == 0:
            n_map = np.array(new_shape)
            np.savetxt("example/bv10/new" + str(index) + ".csv", n_map, fmt='%s', delimiter=",")
        if found_reduc:
            reduc = 0
            temp_shape = copy.deepcopy(shape)
            for i in range(len(temp_shape)):
                temp_shape[i].append(0)
            while found_reduc:
                for i in range(len(new_shape)):
                    if i == 0 and (new_shape[i][back_locs[i] + 1] != 0 or (new_shape[i + 1][back_locs[i]] != 0 and
                    shape[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i == len(new_shape) - 1 and (new_shape[i][back_locs[i] + 1] != 0 or
                    (new_shape[i - 1][back_locs[i]] != 0 and temp_shape[i - 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i > 0 and i < len(new_shape) - 1 and (new_shape[i][back_locs[i] + 1] != 0 or
                    (new_shape[i - 1][back_locs[i]] != 0  and temp_shape[i - 1][back_locs[i]] == 0) or
                    (new_shape[i + 1][back_locs[i]] != 0 and temp_shape[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                if found_reduc:
                    for i in range(len(new_shape)):
                        new_shape[i].pop(back_locs[i])
                    reduc = reduc + 1
                else:
                    reductions.append(reduc)
                    n_map = np.array(new_shape)
                    np.savetxt("example/bv10/new" + str(index) + ".csv", n_map, fmt = '%s',delimiter=",")

        else:
            reductions.append(0)
    print('original depth is ' + str(len(shape[0])) + ". The reduction is " + str(max(reductions)))

def comb_reduction(shortest_shape, combina):
    reductions = []
    for comb in combina:
        shape1 = shortest_shape[comb[0]]
        shape2 = shortest_shape[comb[1]]
        #for first shape
        new_shape1 = []
        if len(shape1) != len(shape2):
            print('shape not the same!')
        for i in range(len(shape1)):
            new_shape1.append(shape1[i] + shape2[i])
        back_locs = []
        for row in shape1:
            for j in reversed(range(len(row))):
                if row[j] != 0:
                    back_locs.append(j + 1)
                    break
                elif j == 0:
                    back_locs.append(0)
        found_reduc = 1
        for i in range(len(new_shape1)):
            if new_shape1[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc:
            reduc1 = 0
            temp_shape = copy.deepcopy(shape1)
            for i in range(len(temp_shape)):
                temp_shape[i].append(0)
            while found_reduc:
                for i in range(len(new_shape1)):
                    if i == 0 and (new_shape1[i][back_locs[i] + 1] != 0 or
                    (new_shape1[i + 1][back_locs[i]] != 0 and temp_shape[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i == len(new_shape1) - 1 and (new_shape1[i][back_locs[i] + 1] != 0 or
                    (new_shape1[i - 1][back_locs[i]] != 0 and temp_shape[i - 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i > 0 and i < len(new_shape1) - 1 and (new_shape1[i][back_locs[i] + 1] != 0 or
                    (new_shape1[i - 1][back_locs[i]] != 0 and temp_shape[i - 1][back_locs[i]] == 0) or
                    (new_shape1[i + 1][back_locs[i]] != 0 and temp_shape[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                if found_reduc:
                    for i in range(len(new_shape1)):
                        new_shape1[i].pop(back_locs[i])
                    reduc1 = reduc1 + 1
        else:
            reduc1 = 0
        # for second shape
        new_shape2 = []
        for i in range(len(shape2)):
            new_shape2.append(shape2[i] + shape1[i])
        back_locs = []
        for row in shape2:
            for j in reversed(range(len(row))):
                if row[j] != 0:
                    back_locs.append(j + 1)
                    break
                elif j == 0:
                    back_locs.append(0)
        found_reduc = 1
        for i in range(len(new_shape2)):
            if new_shape2[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc:
            reduc2 = 0
            temp_shape = copy.deepcopy(shape2)
            for i in range(len(temp_shape)):
                temp_shape[i].append(0)
            while found_reduc:
                for i in range(len(new_shape2)):
                    if i == 0 and (new_shape2[i][back_locs[i] + 1] != 0 or
                    (back_locs[i] < len(shape2[i]) and new_shape2[i + 1][back_locs[i]] != 0
                     and shape2[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i == len(new_shape2) - 1 and (new_shape2[i][back_locs[i] + 1] != 0 or
                    (new_shape2[i - 1][back_locs[i]] != 0 and temp_shape[i - 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                    elif i > 0 and i < len(new_shape2) - 1 and (new_shape2[i][back_locs[i] + 1] != 0 or
                    (new_shape2[i - 1][back_locs[i]] != 0 and temp_shape[i - 1][back_locs[i]] == 0) or
                    (new_shape2[i + 1][back_locs[i]] != 0 and temp_shape[i + 1][back_locs[i]] == 0)):
                        found_reduc = 0
                        break
                if found_reduc:
                    for i in range(len(new_shape2)):
                        new_shape2[i].pop(back_locs[i])
                    reduc1 = reduc1 + 1
        else:
            reduc2 = 0
        reductions.append((reduc2 + reduc1) / 2)
    print('combination depth is ' + str(len(shape1[0])) + ". The reduction is " + str(max(reductions)))

def combination2(table, middle_shapes, first, last, rows):
    shortest_shape = []
    shortest_depth = 100000
    indexes = []
    for shape in middle_shapes:
        if len(shape[0]) < shortest_depth:
            shortest_depth = len(shape[0])
    for shape in middle_shapes:
        if len(shape[0]) == shortest_depth:
            indexes.append(middle_shapes.index(shape))
            shortest_shape.append(shape)
    shortest_shape, indexes = sort_shape(shortest_shape, indexes)
    shortest_shape = double_shape(shortest_shape)
    arr = []
    for i in range(len(shortest_shape)):
        arr.append(i)
    combina = list(combinations(arr, 2))
    original_reduction2(shortest_shape, table, indexes, first, last)
    print('g')

def original_reduction2(shortest_shape, table, indexes, first, last):
    for i in range(int(len(shortest_shape)/2)):
        shape = shortest_shape[i]
        shape = fill_ori_shape(shape, table, indexes[i], first, last)
        new_map = convert_new_map2(shape)
        n_map = np.array(new_map)
        w = len(shape)
        np.savetxt("example/bv5/bv5ela" + str(w) + ".csv", n_map, fmt='%s', delimiter=",")
        font_distances = check_distance(shape, table[indexes[i]], 'f')
        back_distances = check_distance(shape, table[indexes[i]], 'b')
        new_shape = []
        for row in shape:
            new_shape.append(row + row)
        back_locs = []
        for row in shape:
            for j in reversed(range(len(row))):
                if row[j] != 0:
                    back_locs.append(j + 1)
                    break
                elif j == 0:
                    back_locs.append(0)
        found_reduc = 1
        for i in range(len(new_shape)):
            if new_shape[i][back_locs[i]] != 0:
                found_reduc = 0
                break
    print('g')

def fill_ori_shape(shape, table, index, first, last):
    new_shape = copy.deepcopy(shape)
    starts = copy.deepcopy(table[index]['starts'])
    ends = copy.deepcopy(table[index]['ends'])
    max_first = max(first)
    max_last = max(last)
    for i in range(len(new_shape)):
        new_shape[i] = [0] * max_first + new_shape[i] + [0] * max_last
    for i in range(len(starts)):
        new_shape[starts[i][0]][starts[i][1] - first[i] + max_first: starts[i][1] + max_first] = [1] * first[i]
        new_shape[ends[i][0]][ends[i][1] + max_first + 1: ends[i][1] + max_first + 1 + last[i]] = [1] * last[i]
    return new_shape

def check_distance(shape, table, loc):
    distances = []
    front_space = []
    back_space = []
    for i in range(len(shape)):
        for j in reversed(range(len(shape[i]))):
            if shape[i][j] != 0:
                back_space.append(len(shape[i]) - j - 1)
                break
        for j in range(len(shape[i])):
            if shape[i][j] != 0:
                front_space.append(j)
                break
    if loc == 'f':
        for i in range(len(front_space)):
            if i == 0:
                distances.append(front_space[i] + min(back_space[i] - 1, back_space[i + 1]))
            elif i == len(front_space) - 1:
                distances.append(front_space[i] + min(back_space[i - 1], back_space[i] - 1))
            else:
                distances.append(front_space[i] + min(back_space[i - 1], back_space[i] - 1, back_space[i + 1]))
        starts = copy.deepcopy(table['starts'])
        front_distances = []
        # for i in range(len(starts)):
        #     front_distances.append(distances[starts[i][0]])
    elif loc == 'b':
        for i in range(len(back_space)):
            if i == 0:
                distances.append(back_space[i] + min(front_space[i] - 1, front_space[i + 1]))
            elif i == len(back_space) - 1:
                distances.append(back_space[i] + min(front_space[i - 1], front_space[i] - 1))
            else:
                distances.append(back_space[i] + min(front_space[i - 1], front_space[i] - 1, front_space[i + 1]))
        starts = copy.deepcopy(table['ends'])
        front_distances = []
        # for i in range(len(starts)):
        #     front_distances.append(distances[starts[i][0]])
    return distances

def check_fb_distances(distances, table):
    front_distances = []
    back_distances = []
    starts = copy.deepcopy(table['starts'])
    ends = copy.deepcopy(table['ends'])
    for i in range(len(starts)):
        front_distances.append(distances[starts[i][0]])
        back_distances.append(distances[ends[i][0]])
    return front_distances, back_distances
