assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."

    res = []
    for a in A:
        for b in B:
            res.append(a+b)
    return res


rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[r+c for (r, c) in zip(rows, cols)], [r+c for (r, c) in zip(rows, reversed(cols))]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    twins = {}  # a dictionary with key=unit index, values=box name
    twins_values = {}  # a dictionary with key=unit index, values=two values that correspond to the digits in the twin
    for num_unit, unit in enumerate(unitlist):
        # first we search all boxes that contains only two digit
        dplaces = [box for box in unit if (len(values[box]) == 2)]

        # then we look into this boxes in order to find twin values (i.e doublon)
        for b1 in dplaces:
            for b2 in dplaces:
                if b1 == b2:
                    continue
                if values[b1] == values[b2]:
                    # we have a twin
                    twins[num_unit] = (b1, b2)
                    twins_values[num_unit] = values[b1]

    # Eliminate the naked twins as possibilities for their peers
    for unit_num, box_set in twins.items():
        for box in unitlist[unit_num]:
            if box in box_set:
                continue   # it's one of the box of the twin so we want to keep it (i.e no change)
            for digit in twins_values[unit_num]:
                if digit in values[box]:
                    values[box] = values[box].replace(digit, '')  # we remove the digit as a possibility for this box
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    res = {}
    for key, val in zip(cross(rows, cols), grid):
        if val is '.':
            res[key] = '123456789'
        else:
            res[key] = val
    return res


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print


def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.

    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key, digit in values.items():
        if len(digit) == 1:
            for peer in peers[key]:
                new_val = values[peer].replace(digit, '')  # we remove the digit
                assign_value(values, peer, new_val)
    return values


def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dictionary form.

    Returns:
        Sudoku in dictionary form after filling in only choices.
    """
    new_values = values.copy()  # note: do not modify original values
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #new_values[dplaces[0]] = digit
                assign_value(new_values, dplaces[0], digit)
    return new_values


def reduce_puzzle(values):
    """

    Args:
        values:

    Returns:

    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        if stalled:
            break
        if solved_values_after == 81:
            break
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.

    Args:
        values:

    Returns:
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False

    nb_solved = len([box for box in values.keys() if len(values[box]) == 1])
    if nb_solved == 81:
        return values

    # Choose one of the unfilled squares with the fewest possibilities

    nb_possibilities_dict = {box:len(values[box]) for box in boxes if len(values[box])>1}
    to_try_in_order = sorted(nb_possibilities_dict, key=nb_possibilities_dict.__getitem__)
    position = to_try_in_order[0]
    possibilities = values[position]

    for possibility in possibilities:
        new_sudoku = values.copy()
        assign_value(new_sudoku, position, possibility)
        new_sudoku = search(new_sudoku)
        if new_sudoku != False:
            return new_sudoku

    return False


def search_not_working(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    # an hard grid (need to deactivate diagonal constraint in order to get a solution)
    #hard_grid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    res = solve(diag_sudoku_grid)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
