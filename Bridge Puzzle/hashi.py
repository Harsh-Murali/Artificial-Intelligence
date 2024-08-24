#!/usr/bin/env python3

"""
First the program reads user input and converts it to a numpy array for better modification.
User input is then stored as both a map and an original_map.
Next, potential bridge locations between islands are found.
And islands are scanned both horizontally then vertically starting at the top left cell.
If an island doesn't have water surrounding it, a bridge will not be constructed.
This prevents accidential valid solutions from being formed.
Then we keep checking for possible bridge locations until we reach the end cell.
Our place bridge function tells us whether to add or remove bridges based off the value of the remove flag.
The search function uses a backtracking algorithm to recursively place various bridge combinations.
COmbinations that fail are undone.
The algorithm continues to find a valid solution until all possiblities are exhausted. 
The solve_hashmap function employs our search function to place these potential bridges in our map.
The apply_assignments function updates the original puzzle with bridge placements as determined by our backtracking algorithm.
Our abc_num converts the numbers 10,11,12 to the strings a,b,c.
The is_printable function then strips all non-printable characters from our output.
Finally our, print_solution function iterates through the grid and converts a,b,c to 10,11,12. And prints the final solution.

This program ensures that no bridges are created diagonally by forming rows and columns in a single direction until they reach the end. Then they change.
Dictionaries are used to efficiently modify recursive explorations of each viable solution.

Numpy arrays were used because they were easier to modify compared to lists.
A recursive backtracking algorithm allows for decisions to be undone allowing for a more thorough search.
The pre-calculation step of using potential bridges reduces the search space for the backtracking algorithm, thus reducing time complexity.
Utilising multiple functions increases the clarity and structure of the code.
"""


#import libraries
import numpy as np
import sys

# Define the main function
def main():
    # nrow stores the rows, ncol stores columns
    # map stores the input as a numpy array
    # scanmap then reads this map and gets its dimensions
    nrow, ncol, map = scanmap()
    #original_map makes a copy of the map to use later
    # this will be used to make comparisions and verify whether the map we output matches the original map
    original_map = np.copy(map)
    #potential_bridges displays a pair of tuples indicating the start and end points of possible bridges locations
    potential_bridges = find_potential_bridges(map, nrow, ncol)
    # solve_hashmap attempts to place bridges by observing map, potential_bridges, nrow, ncol, original_map
    if solve_hashmap(map, potential_bridges, nrow, ncol, original_map):
        #If it succeeds then valid solution is printed
        print("Valid Solution.")
    else:
        #If it fails then invalid solution is printed
        print("Invalid Solution.")

#This functions the values contained in map
def scanmap():
    # this empty list stores rows of map
    text = []
    # This iterates through each line of standard input
    for line in sys.stdin:
        # 0-9 are converted from characters to integers
        # a->c are converted from characters to integers, namely 10, 11 and 12
        row = [int(ch) if '0' <= ch <= '9' else ord(ch) - 87 if 'a' <= ch <= 'c' else 0 for ch in line.strip()]
        # Each processed row is appended to the empty text list
        text.append(row)
    # finally the completed text list is converted to an array
    # this array allows us to perform backtracking later on
    map = np.array(text)
    # The number of rows, columns and the map are returned
    return map.shape[0], map.shape[1], map  

# This function finds pair potential bridge locations
def find_potential_bridges(map, nrow, ncol):
    # an empty list called bridges is initialised to store pairs containing potential bridge locations
    bridges = []
    # r iterates through each row
    for r in range(nrow):
        # c iterates through each column
        for c in range(ncol):
            # Ensures that the current cell is an island 0-12 value
            if map[r][c] > 0:
                # checks horizontally and vertically for bridges
                # starting from the current cell
                # checks for bridges in the horizontal and vertical directions
                for dr, dc in [(0, 1), (1, 0)]:
                    # calculates coordinates of neighbouring cells
                    nr, nc = r + dr, c + dc
                    # Ensures that the neighbour cell is within map boundaries
                    while 0 <= nr < nrow and 0 <= nc < ncol:
                        # Checks if another island is found
                        if map[nr][nc] > 0:
                            # Ensures that there is at least 1 unit of water around the island
                            if not (nr == r + dr and nc == c + dc):
                                # As long as this is true then we can add the bridge to the list
                                bridges.append(((r, c), (nr, nc)))
                            # Exit after finding a bridge or island
                            break  # Exit the loop after finding a bridge or an adjacent island
                        # Moves to the next cell
                        nr += dr
                        nc += dc
    # A list of potential bridge pairs are returned
    return bridges

# Checks where bridges can be placed
def can_place_bridges(map, start, end, bridges):  # Define function to check if bridges can be placed
    # Calculates row direction for bridge
    dr = end[0] - start[0]
    # Calculates column direction for bridge
    dc = end[1] - start[1]
    # Normalises row direction
    # If direction is not zero, it is divided by itself
    # and turned postive
    if dr != 0:
        dr //= abs(dr)
    # Likewise, this normalises column direction
    if dc != 0:
        dc //= abs(dc)
    # r,c represent the starting coordinates to place bridges
    r, c = start
    # Keeps going until r and c have reached the end
    while (r, c) != end:
        # Increments in row direction
        r += dr
        # Increments in column direction
        c += dc
        # Checks that we are not at the end and the current cell is an island
        if (r, c) != end and map[r][c] != 0:
            # Fails since we are still iterating thorugh the array
            # And the current cell is an island
            return False
    # Otherwise, return true since a bridge can be placed
    return True

# This function tells us when to add or remove bridges
def place_bridges(map, start, end, bridges, remove):
    # Calculates direction of rows for bridges
    dr = end[0] - start[0]
    # Calculates direction of columns for bridges
    dc = end[1] - start[1]
    # Normalises row direction
    # If direction is not zero, it is divided by itself
    # and turned postive
    if dr != 0:
        dr //= abs(dr)
    # Similarly, column direction is normalised
    if dc != 0:
        dc //= abs(dc)
    # Value change tells us whether to remove or add bridges
    # If bridges are being removed then value change is increases
    # If bridges are being added then value change decreases
    value_change = -bridges if remove else bridges
    # Subtracting value change tells us the number of bridges connected to each island
    # This updates the start island value
    map[start] -= value_change
    # This updates the end island value
    map[end] -= value_change
    # The value r and c initialse starting coordinates for brige placement
    r, c = start
    # Keep going until the end is not reached
    while (r, c) != end:
        # Increments r in the direction of the row
        r += dr
        # Increments c in the direction of the column
        c += dc  # Move in the column direction

# This is our backtracking search function
# Define the recursive search function
def search(k, potential_bridges, map, assignments):
    # Sets the base case for recursion
    # Checks whether all potential bridges have been considered
    if k == len(potential_bridges):
        # Checks if all islands are connected
        # Iterates through the map and if a cell that contained an island 
        # also has no remaining potential bridge connections
        # Then it returns true
        all_clear = all(map[r, c] == 0 for r in range(map.shape[0]) for c in range(map.shape[1]) if map[r, c] > 0)
        return all_clear
    # Using the index k
    # The start and end points of the current potential bridge are extracted
    start, end = potential_bridges[k]
    # Iterates through the range 1->12 since island numbers go from 1->12
    for bridges in range(1, 13):
        # checks if the bridge can be placed
        if can_place_bridges(map, start, end, bridges):
            # Records number of bridges placed between start and end points
            # This is recorded in the assignments dictionary
            assignments[(start, end)] = bridges
            # Places BRidges on the map
            # False indicates bridges are NOT being removed
            # Therefore, False indicates bridges being added
            place_bridges(map, start, end, bridges, False)
            # Recursively calls the search function to place a bridge on the next index k+1
            if search(k + 1, potential_bridges, map, assignments):
                # True means that a solution was found
                # Now a bridge is placed
                return True
            # Otherwise, the bridge is removed
            # True indicates that yes, we want to remove this bridge
            place_bridges(map, start, end, bridges, True)
    # False indicates that the current path has no solution
    # The algorithm now backtracks and tries another configuration
    return False


# This function finds a solution by placing these potential bridges 
# found by previous function onto the map
def solve_hashmap(map, potential_bridges, nrow, ncol, original_map):
    # an empty dictionary called assignments is initialised
    assignments = {}
    # We call our backtracking function(search) and start 
    # searching with the initial index for potential bridges
    if search(0, potential_bridges, map, assignments):
        # If a valid solution is found, we apply bridge placements stored in the assignments dictionary to the map
        apply_assignments(map, assignments, potential_bridges)
        # Next, this solution is printed
        print_solution(map, assignments, nrow, ncol, original_map)
        # True means a solution was found
        return True
    # False means a solution was not found
    return False


# Applies bridge assignments to the map
def apply_assignments(map, assignments, potential_bridges):
    # generates a tuple of indicies for each cell in the map array
    # Accesses these cells using r and c
    # Iterates through all cells in the map
    for r, c in np.ndindex(map.shape):
        # If the current cell is an island
        if map[r, c] > 0:
            # It is converted a negative value
            map[r, c] = -map[r, c]
    # Bridge is a tuple containing the start and end points of a bridge
    # Count is the number of bridges to place between these points  
    for bridge, count in assignments.items():
        # If count is positive
        if count > 0:
            # Then we palce a bridge on the map
            place_bridges(map, bridge[0], bridge[1], count, False)
            


# This converts 10,11,12 to a,b,c respectively
def abc_num(num):
    # If num is 10 then we turn it back into the string a
    if num == 10:  # Check if the number represents 'a'
        return 'a'
    # If num is 11 then we turn it back into the string b
    elif num == 11:
        return 'b'
    # If num is 12 then we turn it back into the string c
    elif num == 12:  # Check if the number represents 'c'
        return 'c'
    # Otherwise all numbers 0->9 are turned into strings
    else:
        return str(num)  # Convert the number to a string

# Removes all non-printable characters from our output
def is_printable(s):
    # We iterate over each character x in the string s
    # Only printable characters are returned
    # They are concatenated and joined without space
    return ''.join(filter(lambda x: x in ' \t\n\r' or 32 <= ord(x) <= 126, s))  # Filter and return printable characters

# This function prints the final hashi map
def print_solution(map, assignments, nrow, ncol, original_map):
    # Initialises an empty grid with spaces with dimensions nrow x ncol
    solution_grid = [[' ' for _ in range(ncol)] for _ in range(nrow)]
    # Iterates over each item in the assignments dictionary
    # each item contains a tuple with start and end points of the bridges
    for ((start_r, start_c), (end_r, end_c)), bridges in assignments.items():
        # if no bridges are placed between the start and end points,
        if bridges == 0:
            # the next item in assignments is checked
            continue
        # If 1 bridge placed between islands
        # and start and end rows/columns are the same we apply the pipe or dash symbol
        # start = end tells us the orientation of the bridge
        symbol = '-' if start_r == end_r else '|'
        # If 2 bridges placed between islands
        # and start and end rows/columns are the same we apply the equals or "" symbol
        if bridges > 1:
            symbol = '=' if start_r == end_r else '"'  
        # and start and end rows/columns are the same we apply the E or hash symbol
        if bridges > 2:
            symbol = 'E' if start_r == end_r else '#'  # Use 'E' or '#' for excessive horizontal or vertical bridges respectively

        # Initialise coordinates for placing bridges
        r, c = start_r, start_c
        # Whilst we haven't reached the end
        while (r, c) != (end_r, end_c):  # Iterate until reaching the end coordinates
            # Place bridge symbol at r,c coordinates on the map
            solution_grid[r][c] = symbol
            # as long as the current row coordinate 
            # isn't the end row coordinate continue
            if r != end_r:
                # Update row coordinate by 1
                # if end > start, move down
                # if end < start, move up
                r += 1 if end_r > start_r else -1
            # check current column coordinate is not end column coordinate
            if c != end_c:
                # Update column coordinate by 1
                # if end > start, move right
                # if end < start, move left
                c += 1 if end_c > start_c else -1

    # Iterate through each row in original map
    for r in range(nrow):
        # Iterate through each column in original map
        for c in range(ncol):
            # Checks if current cell is an island
            if original_map[r, c] > 0:
                # If cell is the letter a, b or c it gets converted to 10, 11 or 12
                solution_grid[r][c] = abc_num(original_map[r, c])  # Place the island symbol on the solution grid
    
    # Iterates through rows in the final solution grid
    for row in solution_grid:
        # Joins all characters into a single string
        # Uses is_printable function to remove all non-printable characters
        printable_row = is_printable(''.join(row))
        # All filtered rows are now printed
        print(printable_row)

if __name__ == '__main__':
    main()
