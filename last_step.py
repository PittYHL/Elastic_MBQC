import copy
from itertools import combinations
maximum = 5

def combination(final_shapes):
    shortest_shape = []
    shortest_depth = 100000
    for shape in final_shapes:
        if len(shape[0]) < shortest_depth:
            shortest_depth = len(shape[0])
    for shape in final_shapes:
        if len(shape[0]) == shortest_depth:
            shortest_shape.append(shape)
    shortest_shape = sort_shape(shortest_shape)
    shortest_shape = double_shape(shortest_shape)
    arr = []
    for i in range(len(shortest_shape)):
        arr.append(i)
    combina = list(combinations(arr, 2))
    original = original_reduction(shortest_shape)
    comb = comb_reduction(shortest_shape, combina)
    print('g')

def sort_shape(shapes):
    if len(shapes) <= maximum:
        return shapes
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
            shortest_shape.append(temp_shapes.pop(index))
        return shortest_shape

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
    for shape in shortest_shape:
        new_shape = []
        for row in shape:
            new_shape.append(row + row)
        back_locs = []
        for row in shape:
            for j in reversed(range(len(row))):
                if row[j] != 0:
                    back_locs.append(j + 1)
                    break
        found_reduc = 1
        for i in range(len(new_shape)):
            if new_shape[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc:
            reduc = 0
            while found_reduc:
                for i in range(len(new_shape)):
                    new_shape[i].pop(back_locs[i])
                    if new_shape[i][back_locs[i]] != 0:
                        found_reduc = 0
                        break
                if found_reduc:
                    reduc = reduc + 1
                else:
                    reductions.append(reduc)
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
        found_reduc = 1
        for i in range(len(new_shape1)):
            if new_shape1[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc:
            reduc1 = 0
            while found_reduc:
                for i in range(len(new_shape1)):
                    new_shape1[i].pop(back_locs[i])
                    if new_shape1[i][back_locs[i]] != 0:
                        found_reduc = 0
                        break
                if found_reduc:
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
        found_reduc = 1
        for i in range(len(new_shape1)):
            if new_shape2[i][back_locs[i]] != 0:
                found_reduc = 0
                break
        if found_reduc:
            reduc2 = 0
            while found_reduc:
                for i in range(len(new_shape2)):
                    new_shape2[i].pop(back_locs[i])
                    if new_shape2[i][back_locs[i]] != 0:
                        found_reduc = 0
                        break
                if found_reduc:
                    reduc2 = reduc2 + 1
        else:
            reduc2 = 0
        reductions.append((reduc2 + reduc1) / 2)
    print('combination depth is ' + str(len(shape1[0])) + ". The reduction is " + str(max(reductions)))
