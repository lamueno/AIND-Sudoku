# from utils import *

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    return [s + t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

diag_units = [[r + c for r, c in zip(rows, cols)], [
    r + c for r, c in zip(rows, cols[::-1])]]
diag_unitlist = unitlist + diag_units
diag_units = dict((s, [u for u in diag_unitlist if s in u]) for s in boxes)
diag_peers = dict((s, set(sum(diag_units[s], [])) - set([s])) for s in boxes)


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
            If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    return dict(zip(boxes, ['123456789' if v == '.' else v for v in grid]))


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any
    # values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values, diag=False):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    if diag:
        unit_list = diag_unitlist
    else:
        unit_list = unitlist

    # Find all instances of naked twins
    twins = []
    for unit in unit_list:
        seen = set()
        two_digits_place = [box for box in unit if len(values[box]) == 2]
        for box in two_digits_place:
            if values[box] not in seen:
                seen.add(values[box])
            else:  # Found the naked twins!
                twins.append((unit, values[box]))

    # Reduce values according to naked twins
    for unit, twins_value in twins:
        for box in unit:
            if len(values[box]) > 1 and values[box] != twins_value:
                for digit in twins_value:
                    values[box] = values[box].replace(digit, '')
    return values


def eliminate(values, diag=False):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    if diag:
        _peers = peers
    else:
        _peers = diag_peers

    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in _peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values, diag=False):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    if diag:
        unit_list = diag_unitlist
    else:
        unit_list = unitlist

    for unit in unit_list:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values, is_diag=False):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values, is_diag)
        values = only_choice(values, is_diag)
        values = naked_twins(values, is_diag)
        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values, is_diag=False):
    # Using depth-first search and propagation, create a search tree and solve the sudoku.
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values, is_diag)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku, is_diag)
        if attempt:
            return attempt


def solve(grid, is_diag=False):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # is_diag = True
    values = grid_values(grid)
    return search(values, is_diag)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print(
            'We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
