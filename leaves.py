import copy
from collections import Counter

def place_leaves(table, shapes, first, last, rows, special):
    last_table = table[-1]
    last_shapes = shapes[-1]
    final_shapes = []
    for i in range(len(last_table)):
        starts = last_table[i]['starts']
        ends = last_table[i]['ends']
        shape = last_shapes[i]
        shape, starts, ends = fill_shape(shape, rows, starts, ends)
        final_shape = place_final(shape, starts, ends, first, last, special)
        final_shapes.append(final_shape)
    return final_shapes

def place_final(shape, starts, ends, first, last, special):
    start_indexes, up_s, down_s = rank_starts(starts, shape)
    end_indexes, up_e, down_e = rank_ends(ends, shape)
    new_shape = copy.deepcopy(shape)
    for i in range(len(first)):
        if first[i] < 0:
            first[i] = 1
    for i in range(len(new_shape)):
        new_shape[i] = [0]*max(first) + new_shape[i] + [0]*max(last)
    for i in range(len(starts)):
        starts[i][1] = starts[i][1] + max(first)
        ends[i][1] = ends[i][1] + max(first)
    new_shape = place_front(new_shape, start_indexes, starts, first, up_s, down_s, special)
    new_shape = place_end(new_shape, end_indexes, ends, last, up_e, down_e, special)
    new_shape = remove_useless(new_shape)
    return new_shape

def rank_starts(starts, shape):
    width = len(shape)
    start_indexes = []
    x_locs = []
    up_y = -1 #if y upper than this, go up
    down_y = -1 #if y lower than this, go down
    for start in starts:
        x_locs.append(start[1])
    sort_locs = copy.deepcopy(x_locs)
    sort_locs.sort(reverse=True)
    while(sort_locs) != []:
        loc = sort_locs[0]
        if sort_locs.count(loc) == 1:
            start_indexes.append(x_locs.index(loc))
            sort_locs.pop(0)
        else:
            indexes = find_indices(x_locs, loc)
            y_locs = []
            for i in indexes:
                y_locs.append(starts[i][0])
            up = min(y_locs)
            down = width - max(y_locs) - 1
            if up > down:
                while(indexes) != []:
                    ind = y_locs.index(min(y_locs))
                    start_indexes.append(indexes[ind])
                    if len(sort_locs) <= 2:
                        up_y = y_locs[ind]
                    indexes.pop(ind)
                    y_locs.pop(ind)
                    sort_locs.pop(0)
                    if indexes != []:
                        ind = y_locs.index(max(y_locs))
                        start_indexes.append(indexes[ind])
                        if len(sort_locs) <= 2:
                            down_y = y_locs[ind]
                        indexes.pop(ind)
                        y_locs.pop(ind)
                        sort_locs.pop(0)
            else:
                while(indexes) != []:
                    ind = y_locs.index(max(y_locs))
                    start_indexes.append(indexes[ind])
                    if len(sort_locs) <= 2:
                        down_y = y_locs[ind]
                    indexes.pop(ind)
                    y_locs.pop(ind)
                    sort_locs.pop(0)
                    if indexes != []:
                        ind = y_locs.index(min(y_locs))
                        start_indexes.append(indexes[ind])
                        if len(sort_locs) <= 2:
                            up_y = y_locs[ind]
                        indexes.pop(ind)
                        y_locs.pop(ind)
                        sort_locs.pop(0)
    return start_indexes, up_y, down_y

def rank_ends(ends, shape):
    width = len(shape)
    start_indexes = []
    x_locs = []
    up_y = -1  # if y upper than this, go up
    down_y = -1  # if y lower than this, go down
    for end in ends:
        x_locs.append(end[1])
    sort_locs = copy.deepcopy(x_locs)
    sort_locs.sort()
    while (sort_locs) != []:
        loc = sort_locs[0]
        if sort_locs.count(loc) == 1:
            start_indexes.append(x_locs.index(loc))
            sort_locs.pop(0)
        else:
            indexes = find_indices(x_locs, loc)
            y_locs = []
            for i in indexes:
                y_locs.append(ends[i][0])
            up = min(y_locs)
            down = width - max(y_locs) - 1
            if up > down:
                while (indexes) != []:
                    ind = y_locs.index(min(y_locs))
                    start_indexes.append(indexes[ind])
                    if len(sort_locs) <= 2:
                        up_y = y_locs[ind]
                    indexes.pop(ind)
                    y_locs.pop(ind)
                    sort_locs.pop(0)
                    if indexes != []:
                        ind = y_locs.index(max(y_locs))
                        start_indexes.append(indexes[ind])
                        if len(sort_locs) <= 2:
                            down_y = y_locs[ind]
                        indexes.pop(ind)
                        y_locs.pop(ind)
                        sort_locs.pop(0)
            else:
                while (indexes) != []:
                    ind = y_locs.index(max(y_locs))
                    start_indexes.append(indexes[ind])
                    if len(sort_locs) <= 2:
                        down_y = y_locs[ind]
                    indexes.pop(ind)
                    y_locs.pop(ind)
                    sort_locs.pop(0)
                    if indexes != []:
                        ind = y_locs.index(min(y_locs))
                        start_indexes.append(indexes[ind])
                        if len(sort_locs) <= 2:
                            up_y = y_locs[ind]
                        indexes.pop(ind)
                        y_locs.pop(ind)
                        sort_locs.pop(0)
    return start_indexes, up_y, down_y

def find_indices(list_to_check, item_to_find):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value == item_to_find:
            indices.append(idx)
    return indices

def place_front(new_shape, start_indexes, starts, first, up_y, down_y, special):
    for i in start_indexes:
        current = starts[i]
        if i == start_indexes[-1] and special:
            if current[0] < len(new_shape)/2:
                new_shape = place_leaf_f(new_shape, first[i], current, 'd', len(new_shape) - 1)
            else:
                new_shape = place_leaf_f(new_shape, first[i], current, 'u', 0)
        elif current[0] <= up_y:
            if i != len(start_indexes) - 1 and i != start_indexes[-1]:
                lower_bound = starts[i + 1][0] - 2
            else:
                lower_bound = len(new_shape) - 1
            new_shape = place_leaf_f(new_shape, first[i], current, 'u', lower_bound)
        elif current[0] >= down_y:
            if i != 0 and i != start_indexes[-1]:
                upper_bound = starts[i - 1][0] + 2
            else:
                upper_bound = 0
            new_shape = place_leaf_f(new_shape, first[i], current, 'd', upper_bound)
    return new_shape

def place_end(new_shape, end_indexes, ends, last, up_y, down_y, special):
    for i in end_indexes:
        current = ends[i]
        if i == end_indexes[-1] and special:
            if current[0] < len(new_shape)/2:
                new_shape = place_leaf_e(new_shape, last[i], current, 'd', len(new_shape) - 1)
            else:
                new_shape = place_leaf_e(new_shape, last[i], current, 'u', 0)
        elif current[0] <= up_y:
            if i != len(end_indexes) - 1 and i != end_indexes[-1]:
                lower_bound = ends[i + 1][0] - 2
            else:
                lower_bound = len(new_shape) - 1
            new_shape = place_leaf_e(new_shape, last[i], current, 'u', lower_bound)
        elif current[0] >= down_y:
            if i != 0 and i != end_indexes[-1]:
                upper_bound = ends[i - 1][0] + 2
            else:
                upper_bound = 0
            new_shape = place_leaf_e(new_shape, last[i], current, 'd', upper_bound)
    return new_shape

def place_leaf_f(new_shape, length, loc, dir, bound):
    t_length = copy.deepcopy(length)
    c_loc = copy.deepcopy(loc)
    if dir == 'u': #bound is lower bound
        while t_length != 0:
            if dir == 'u':
                if c_loc[0] == 0:
                    new_shape[0][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1
                    dir = 'd' #left
                elif c_loc[0] == 1 and new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0:
                    new_shape[0][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1
                    dir = 'd' #up
                elif new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1#up
                else:
                    new_shape[c_loc[0]][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1 #left
                t_length = t_length - 1
            elif dir == 'd':
                if c_loc[0] == bound:
                    new_shape[0][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1
                    dir = 'u' #left
                elif c_loc[0] == bound - 1 and new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1
                    dir = 'u' #d
                elif new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1#d
                else:
                    new_shape[c_loc[0]][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1 #left
                t_length = t_length - 1
    elif dir == 'd': #bound is upper bound
        while t_length != 0:
            if dir == 'u':
                if c_loc[0] == bound:
                    new_shape[c_loc[0]][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1
                    dir = 'd' #left
                elif c_loc[0] == bound + 1 and new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1
                    dir = 'd' #up
                elif new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1#up
                else:
                    new_shape[c_loc[0]][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1 #left
                t_length = t_length - 1
            elif dir == 'd':
                if c_loc[0] == len(new_shape) - 1:
                    new_shape[len(new_shape) - 1][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1
                    dir = 'u' #left
                elif c_loc[0] == len(new_shape) - 2 and new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1
                    dir = 'u' #d
                elif new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1#d
                else:
                    new_shape[c_loc[0]][c_loc[1] - 1] = 1
                    c_loc[1] = c_loc[1] - 1 #left
                t_length = t_length - 1
    return new_shape

def place_leaf_e(new_shape, length, loc, dir, bound):
    t_length = copy.deepcopy(length)
    c_loc = copy.deepcopy(loc)
    if dir == 'u': #bound is lower bound
        while t_length != 0:
            if dir == 'u':
                if c_loc[0] == 0:
                    new_shape[0][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1
                    dir = 'd' #left
                elif c_loc[0] == 1 and new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0:
                    new_shape[0][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1
                    dir = 'd' #up
                elif new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1#up
                else:
                    new_shape[c_loc[0]][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1 #left
                t_length = t_length - 1
            elif dir == 'd':
                if c_loc[0] == bound:
                    new_shape[0][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1
                    dir = 'u' #left
                elif c_loc[0] == bound - 1 and new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1
                    dir = 'u' #d
                elif new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1#d
                else:
                    new_shape[c_loc[0]][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1 #left
                t_length = t_length - 1
    elif dir == 'd': #bound is upper bound
        while t_length != 0:
            if dir == 'u':
                if c_loc[0] == bound:
                    new_shape[c_loc[0]][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1
                    dir = 'd' #left
                elif c_loc[0] == bound + 1 and new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1
                    dir = 'd' #up
                elif new_shape[c_loc[0] - 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] - 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] - 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] - 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] - 1#up
                else:
                    new_shape[c_loc[0]][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] - 1 #left
                t_length = t_length - 1
            elif dir == 'd':
                if c_loc[0] == len(new_shape) - 1:
                    new_shape[len(new_shape) - 1][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1
                    dir = 'u' #left
                elif c_loc[0] == len(new_shape) - 2 and new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and\
                    new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1
                    dir = 'u' #d
                elif new_shape[c_loc[0] + 1][c_loc[1] - 1] == 0 and new_shape[c_loc[0] + 1][c_loc[1] + 1] == 0 \
                    and new_shape[c_loc[0] + 2][c_loc[1]] == 0:
                    new_shape[c_loc[0] + 1][c_loc[1]] = 1
                    c_loc[0] = c_loc[0] + 1#d
                else:
                    new_shape[c_loc[0]][c_loc[1] + 1] = 1
                    c_loc[1] = c_loc[1] + 1 #left
                t_length = t_length - 1
    return new_shape

def remove_useless(new_shape):
    front = []
    end = []
    for i in range(len(new_shape)):
        for j in range(len(new_shape[i])):
            if new_shape[i][j] != 0:
                front.append(j)
                break
        for j in reversed(range(len(new_shape[i]))):
            if new_shape[i][j] != 0:
                end.append(len(new_shape[i]) - j - 1)
                break
    min_front = min(front)
    min_back = min(end)
    for i in range(len(new_shape)):
        for j in range(min_front):
            new_shape[i].pop(0)
        for j in range(min_back):
            new_shape[i].pop(-1)
    return new_shape

def show_min(middle_shapes, final_shapes):
    min_middle = 1000000
    min_final = 1000000
    for shape in middle_shapes:
        if len(shape[0]) < min_middle:
            min_middle = len(shape[0])
    for shape in final_shapes:
        if len(shape[0]) < min_final:
            min_final = len(shape[0])
    print("min middle is " + str(min_middle))
    print("min final is " + str(min_final))

def fill_shape(shape, rows, starts, ends):
    extra_row = rows - len(shape)
    up = int(extra_row/2)
    down = extra_row - up
    row = [0]*len(shape[0])
    for i in range(up):
        shape.insert(0, row)
    for i in range(down):
        shape.append(row)
    for i in range(len(starts)):
        starts[i][0] = starts[i][0] + up
        ends[i][0] = ends[i][0] + up
    return shape, starts, ends