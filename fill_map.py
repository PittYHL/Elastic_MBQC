from placement import *

def fill_A(shapes, fronts, spaces, locs, same_qubit, starts, ends):
    valid = []  # valid shpae after fill A
    new_shapes = []
    new_Spaces = []
    new_fronts = []
    new_starts = []
    new_ends = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        start = starts[i]
        end = ends[i]
        first_base = front[locs[0]]
        second_base = front[locs[1]]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]:  # rr
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit:  # constraints for rr
                valid.append(i)
                extra_column = 0
                if first_base[1] == len(shape[0]) - 1:
                    extra_column = 1
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0]][first_base[1] + 1] = 1
                shape[first_base[0] + 1][first_base[1] + 1] = 1
                shape[first_base[0] + 2][first_base[1] + 1] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 1])
                front.append([second_base[0], second_base[1] + 1])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]:  # ru
            if shapes[i][first_base[0] + 1][first_base[1]] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0]][first_base[1] + 1] = 1
                shape[first_base[0] + 1][first_base[1] + 1] = 1
                shape[first_base[0] + 2][first_base[1] + 1] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 1])
                front.append([second_base[0] - 1, second_base[1]])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]:  # dr
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                #front[locs[0]][1] = front[locs[0]][1] + 1
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1]])
                front.append([second_base[0], second_base[1] + 1])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]:  # du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1]])
                front.append([second_base[0] - 1, second_base[1]])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
    return new_shapes, new_fronts, new_Spaces, valid, new_starts, new_ends

def fill_B(shapes, fronts, spaces, locs, same_qubit, starts, ends): #may need to add more cases
    valid = [] #valid shpae after fill B
    new_shapes = []
    new_Spaces = []
    new_fronts = []
    new_starts = []
    new_ends = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        start = starts[i]
        end = ends[i]
        first_base = front[locs[0]]
        second_base = front[locs[1]]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]: #rr
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit: #constraints for rr
                valid.append(i)
                extra_column = first_base[1] + 3 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0]*extra_column
                shape[first_base[0]][first_base[1] + 1: first_base[1] + 3] = [1,1]
                shape[first_base[0] + 1][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 2][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 2])
                front.append([second_base[0], second_base[1] + 2])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]: #ru
            if shapes[i][first_base[0] + 1][first_base[1]] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 3 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0]][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 1][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape[first_base[0] + 2][first_base[1] + 1: first_base[1] + 3] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0], first_base[1] + 2])
                front.append([second_base[0] - 1, second_base[1] + 1])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]: #dr
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 2 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0] + 1][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 2][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 3][first_base[1]: first_base[1] + 2] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1] + 1])
                front.append([second_base[0], second_base[1] + 2])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]: #du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0: #constraints for ru
                valid.append(i)
                extra_column = first_base[1] + 2 - len(shape[0])
                for j in range(len(shape)):
                    shape[j] = shape[j] + [0] * extra_column
                shape[first_base[0] + 1][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 2][first_base[1]: first_base[1] + 2] = [1, 1]
                shape[first_base[0] + 3][first_base[1]: first_base[1] + 2] = [1, 1]
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                front.pop(max(locs))
                front.pop(min(locs))
                front.append([first_base[0] + 1, first_base[1] + 1])
                front.append([second_base[0] - 1, second_base[1] + 1])
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
    return new_shapes, new_fronts, new_Spaces, valid, new_starts, new_ends

def fill_A_P(shapes, fronts, wire_targets, locs, same_qubit, starts, ends):
    valid = []  # valid shpae after fill A
    new_shapes = []
    new_Spaces = []
    new_preds = []
    new_fronts = []
    new_starts= []
    new_ends = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        pred = wire_targets[i]
        start = starts[i]
        end = ends[i]
        first_base = pred[locs[0]]
        second_base = pred[locs[1]]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]:  # ll
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit:  # constraints for rr
                valid.append(i)
                if first_base[1] == 0:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0]][first_base[1] - 1] = 1
                    shape[first_base[0] + 1][first_base[1] - 1] = 1
                    shape[first_base[0] + 2][first_base[1] - 1] = 1
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    for element in start:
                        element[1] = element[1] + extra_column
                    for element in end:
                        element[1] = element[1] + extra_column
                    shape[first_base[0]][first_base[1]] = 1
                    shape[first_base[0] + 1][first_base[1]] = 1
                    shape[first_base[0] + 2][first_base[1]] = 1
                    first_base[1] = first_base[1] + extra_column
                    second_base[1] = second_base[1] + extra_column
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0], first_base[1] - 1])
                pred.append([second_base[0], second_base[1] - 1])
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]:  # lu
            if shapes[i][first_base[0] + 1][first_base[1]] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0]][first_base[1] - 1] = 1
                shape[first_base[0] + 1][first_base[1] - 1] = 1
                shape[first_base[0] + 2][first_base[1] - 1] = 1
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0], first_base[1] - 1])
                pred.append([second_base[0] - 1, second_base[1]])
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_preds.append(pred)
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]:  # dl
            if shapes[i][first_base[0] + 2][first_base[1] + 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0] + 1, first_base[1]])
                pred.append([second_base[0], second_base[1] - 1])
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]:  # du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                shape[first_base[0] + 1][first_base[1]] = 1
                shape[first_base[0] + 2][first_base[1]] = 1
                shape[first_base[0] + 3][first_base[1]:] = 1
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0] + 1, first_base[1]])
                pred.append([second_base[0] - 1, second_base[1]])
                pred[locs[0]][0] = pred[locs[0]][0] + 1
                pred[locs[1]][0] = pred[locs[1]][0] - 1
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
    return new_shapes, new_fronts, new_Spaces, valid, new_preds, new_starts, new_ends

def fill_B_P(shapes, fronts, wire_targets, locs, same_qubit, starts, ends):
    valid = []  # valid shpae after fill B
    new_shapes = []
    new_Spaces = []
    new_preds = []
    new_fronts = []
    new_starts = []
    new_ends = []
    for i in range(len(shapes)):
        shape = shapes[i]
        front = fronts[i]
        pred = wire_targets[i]
        first_base = pred[locs[0]]
        second_base = pred[locs[1]]
        start = starts[i]
        end = ends[i]
        if first_base[0] > second_base[0]:
            temp = first_base
            first_base = second_base
            second_base = temp
        if first_base[0] + 2 == second_base[0] and first_base[1] == second_base[1]:  # ll
            if shapes[i][first_base[0] + 1][first_base[1]] == 0 or same_qubit:  # constraints for rr
                valid.append(i)
                if first_base[1] == 0:
                    extra_column = 2
                elif first_base[1] == 1:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0]][first_base[1] - 2: first_base[1]] = [1,1]
                    shape[first_base[0] + 1][first_base[1] - 2: first_base[1]] = [1,1]
                    shape[first_base[0] + 2][first_base[1] - 2: first_base[1]] = [1,1]
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    for element in start:
                        element[1] = element[1] + extra_column
                    for element in end:
                        element[1] = element[1] + extra_column
                    shape[first_base[0]][0:2] = [1,1]
                    shape[first_base[0] + 1][0:2] = [1,1]
                    shape[first_base[0] + 2][0:2] = [1,1]
                    first_base[1] = first_base[1] + extra_column
                    second_base[1] = second_base[1] + extra_column
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0], first_base[1] - 2])
                pred.append([second_base[0], second_base[1] - 2])
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] - 1 == second_base[1]:  # lu
            if shapes[i][first_base[0] + 1][first_base[1]] == 0:  # constraints for ru
                valid.append(i)
                if second_base[1] == 0:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0]][first_base[1] - 2: first_base[1]] = [1,1]
                    shape[first_base[0] + 1][first_base[1] - 2: first_base[1]] = [1,1]
                    shape[first_base[0] + 2][first_base[1] - 2: first_base[1]] = [1,1]
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    for element in start:
                        element[1] = element[1] + extra_column
                    for element in end:
                        element[1] = element[1] + extra_column
                    shape[first_base[0]][0:2] = [1,1]
                    shape[first_base[0] + 1][0:2] = [1,1]
                    shape[first_base[0] + 2][0:2] = [1,1]
                    first_base[1] = first_base[1] + extra_column
                    second_base[1] = second_base[1] + extra_column
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0], first_base[1] - 2])
                pred.append([second_base[0] - 1, second_base[1] - 1])
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                new_preds.append(pred)
                new_fronts.append(front)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 3 == second_base[0] and first_base[1] + 1 == second_base[1]:  # dl
            if shapes[i][first_base[0] + 2][first_base[1] + 1] == 0:  # constraints for ru
                valid.append(i)
                if first_base[1] == 0:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0] + 1][second_base[1] - 2: second_base[1]] = [1,1]
                    shape[first_base[0] + 2][second_base[1] - 2: second_base[1]] = [1,1]
                    shape[first_base[0] + 3][second_base[1] - 2: second_base[1]] = [1,1]
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    for element in start:
                        element[1] = element[1] + extra_column
                    for element in end:
                        element[1] = element[1] + extra_column
                    shape[first_base[0] + 1][0:2] = [1,1]
                    shape[first_base[0] + 2][0:2] = [1,1]
                    shape[first_base[0] + 3][0:2] = [1,1]
                    first_base[1] = first_base[1] + extra_column
                    second_base[1] = second_base[1] + extra_column
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0] + 1, first_base[1] - 1])
                pred.append([second_base[0], second_base[1] - 2])
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
        elif first_base[0] + 4 == second_base[0] and first_base[1] == second_base[1]:  # du
            if shapes[i][first_base[0] + 2][first_base[1] - 1] == 0:  # constraints for ru
                valid.append(i)
                if first_base[1] == 0:
                    extra_column = 1
                else:
                    extra_column = 0
                for j in range(len(shape)):
                    shape[j] = [0] * extra_column + shape[j]
                if extra_column == 0:
                    shape[first_base[0] + 1][second_base[1] - 1: second_base[1] + 1] = [1,1]
                    shape[first_base[0] + 2][second_base[1] - 1: second_base[1] + 1] = [1,1]
                    shape[first_base[0] + 3][second_base[1] - 1: second_base[1] + 1] = [1,1]
                else:
                    for element in pred:
                        element[1] = element[1] + extra_column
                    for element in front:
                        element[1] = element[1] + extra_column
                    for element in start:
                        element[1] = element[1] + extra_column
                    for element in end:
                        element[1] = element[1] + extra_column
                    shape[first_base[0] + 1][0:2] = [1,1]
                    shape[first_base[0] + 2][0:2] = [1,1]
                    shape[first_base[0] + 3][0:2] = [1,1]
                    first_base[1] = first_base[1] + extra_column
                    second_base[1] = second_base[1] + extra_column
                shape, space = fill_shape(shape)
                new_shapes.append(shape)
                new_Spaces.append(space)
                pred.pop(max(locs))
                pred.pop(min(locs))
                pred.append([first_base[0] + 1, first_base[1] - 1])
                pred.append([second_base[0] - 1, second_base[1] - 1])
                pred[locs[0]][0] = pred[locs[0]][0] + 1
                pred[locs[1]][0] = pred[locs[1]][0] - 1
                new_fronts.append(front)
                new_preds.append(pred)
                new_starts.append(start)
                new_ends.append(end)
    return new_shapes, new_fronts, new_Spaces, valid, new_preds, new_starts, new_ends