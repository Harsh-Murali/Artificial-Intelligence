#!/usr/bin/env python3


"""
Progam Overview and Design Decisions:

First we set up an empty board with 9 small 3x3 squares filled with stars (*).
We then track previous moves and a make list to check if there is a winner on a small board.
A memory bank is also set up to remember board setups seens before to save recalcualtion time.
When it is our turn to play, we look at the board and decide the best move using our alpha-beta pruning algorithm.
We use heuristics to score each possible move and decide how to move. 
Higher scores indicate better moves and lower scores indicate worser moves.
We then choose the move with the highest score.
After moving, we check if anyone has won and what the affect it has on the opponent.
The game continues until a player wins or if there is not more space left on the board.

Data Structures:

We use a 2D list (a list of a list) to represent each tic tac toe baord. 
This structure allows us to quickly update cells and display the board state while still evaluating potential moves.
We use transposition tables which is a dictionary that stores previous states of the board keyed by a hash of the board configuration. 
This makes alpha-beta faster as it doesn't recompute known states again.
An array tracks the history of moves and the current state and progression of the boards.

Algorithms:

Our alpha-beta pruning algorithm is an extension of the minmax algorithm and represents the minimum score for the maximising player and the maximising score for the minimising player. 
We then prunce any branches that do not affect the final decision.
This reduces the number of evaluated nodes increasing program efficiency.
We also evaluate alignment of x's and o's in our alpha beta algorithm.
Multipliers are applied to scores based of their position to optimise the agents moves. 
Corners are given higher wiehgts due to their advantage.
Overall our heuristic focuses on the next few moves ahead instead of all potential future states to reduce computational load.

"""

# Imports libraries
import sys
import argparse
import socket
import re
import itertools

MAX_MOVE, MAX_DEPTH = 81, 7 # Constants for the maximum number of moves and search depth


class Point:
    def __init__(self, board_num, pos):
        self.board_num = board_num  # Initialises a board number (0-8)
        self.pos = pos  # Initialises positon (1-9) on board
        
class Agent:
    def __init__(self):
            self.board = [['*'] * 10 for _ in range(10)]  # Initialise a 10x10 game board with stars
            self.player, self.index, self.result, self.reason, self.move, self.index = None, None, None, None, [-1] * MAX_MOVE, 0  # Initialise all game variables and move histories
            self.max_depth, self.transposition_table, self.small_str, self.step_count  = MAX_DEPTH, {}, {}, 0  # Initialise max depth (7), transposition table and precomputed states, tracks game moves
            self.corners, self.center = {1, 3, 7, 9}, {5}  # Corners are intialised as (1,3,7,9) and the center is intialised as 5

    def smaller(self):
        # Computes scores for all configurations for each 3 by 3 smaller board
        # Then it creates a configuration starting with an empty string
        # Finally it stores the score
        self.small_str = {''.join(['*'] + list(comb)): self.heuristic(['*'] + list(comb)) for comb in itertools.product('xo.', repeat=9)}

    def moves(self, prev_move):
        # Finds the best move from possible options
        possible_moves = [Point(prev_move, i) for i in range(1, 10) if self.board[prev_move][i] == '*']  # Lists out all possible moves
        if not possible_moves:
            return None  # Returns none if no moves are possible

        opponent = 'o' if self.player == 'x' else 'x'  # Assigns o to the opponent if we are x and x to the opponent if we are o
        best_move = None
        best_move_score = -float('inf')  # Initialise the best score as negative infinity

        for point in possible_moves:
            self.board[point.board_num][point.pos] = self.player  # Simulates placing a hypothetical move in a square
            move_score = self.alpha_beta_algorithm(1, opponent, -float('inf'), float('inf'), point.pos)  # Uses alpha-beta pruning to calculate move score
            self.board[point.board_num][point.pos] = '*'  # Undoes the hypothetical move
            if move_score > best_move_score:  # Update the best move if the current score is higher
                best_move = point.pos
                best_move_score = move_score

        return best_move  # Return best move position

    def winner(self, player):
        # Checks if a particular player has won on any of the 3x3 boards
        winning_positions = [  # Lists of all winning combinations
            (1, 2, 3), (4, 5, 6), (7, 8, 9),  # Represents winning horizontal lines
            (1, 4, 7), (2, 5, 8), (3, 6, 9),  # Represents winning vertical lines
            (1, 5, 9), (3, 5, 7)  # Represents winning diagonal lines
        ]

        for board_num in range(len(self.board)):  # Checks and iterates every board
            b = self.board[board_num]
            if any(b[pos1] == b[pos2] == b[pos3] == player for pos1, pos2, pos3 in winning_positions):  # Check if a winning combination has occured
                return True  # Returns frue if a player has won

        return False  # Otherwise false if there hasn't been a win

    def reset(self):
        # Resets board to inital state ready to start printing again
        self.board = [['*'] * 10 for _ in range(10)]  # Clear the board and fill it with stars again

        # Sets up the sections and indices for displaying the printed board
        sections = [
            (1, 2, 3),
            (4, 5, 6),
            (7, 8, 9)
        ]
        group = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        separator = ' ------+-------+-------\n'  # This is the separator between all 9 boards
        result = ''  # Initialises the result string as empty for now

        def format_board_row(board_indices, indices):
            # Formats one row of the board to start printing
            i, j, k = indices # These are the indicies
            row_format = ' {} {} {} |' * 3 + '\n'  # Sets up the format for a row
            return row_format.format(
                *(self.board[x][y] for x in board_indices for y in (i, j, k))
            )

        for section in sections:  # Iterates over every board section
            for indices in group:  # Iterates over each group of indices within a given section
                result += format_board_row(section, indices)  # Formats and add the current row to the resultant string
            result += separator  # Adds a separator after each section
        return result.strip()  # Returns the formatted board as a string and removed all leading and trailing whitespace



    def heuristic(self, board):
        # We need to ensure that board is a single string since calculation requires that
        # Convert board (a list of lists) into a single string
        board_str = '*' + ''.join(''.join(str(cell) for cell in row) for row in board)
        if board_str in self.small_str:
            return self.small_str[board_str]

        score = sum(self.score(i, i+3, i+6, board_str) for i in range(1, 4))  # Calculates score for rows and columns
        score += sum(self.score(*idx, board_str) for idx in [(1, 5, 9), (3, 5, 7)])  # Calculates score for first diagonal followed by second diagonal
        self.small_str[board_str] = score  # Store the final computed score in a variable called score
        return score

    def score(self, idx1, idx2, idx3, mini_board):
        # Calculate the score for a board alignment based off the number of x's and o's by us and opponent
        vals = [mini_board[idx1], mini_board[idx2], mini_board[idx3]]  # Extracts values from the board  # Dictionary to define scores based on combinations of 'x' and 'o'
        scores = {
                (3, 0): 10000,    # Three x's and no o's, we win
                (0, 3): -10000,   # No x's and three o's, they win
                (2, 0): 100,      # Two x's and no o's, we are one move away from winning
                (0, 2): -100,     # No x's and two o's, they are one move away from winning
                (1, 0): 10,       # One x's and no o's, we've placed an x
                (0, 1): -10       # No x's and one o's, they've placed an o
            }
        multiplier = 10 if idx2 == 5 else 5 if idx1 in self.corners or idx3 in self.corners else 1  # Set multiplier based on strategic position and adjuest score accordingly
        return scores.get((vals.count(self.player), vals.count('o' if self.player == 'x' else 'x')), 0) * multiplier  # Compute and return the score for a specific line


    def hash_key(self, board):
        # Generates a hash key for the current board
        return ''.join(''.join(row) for row in board)  # Joins all rows to form a single string hash key

    def alpha_beta_algorithm(self, depth, player, alpha, beta, prev_move):
        board_key = self.hash_key(self.board)  # Generates a hash key for the current board
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]  # Return the cached valie if computed already

        possible_moves = [Point(prev_move, i) for i in range(1, 10) if self.board[prev_move][i] == '*']  # Lists all possible moves fromm current position
        if not possible_moves:
            return 0  # Returns 0 if no moves are possible

        if depth == self.max_depth or self.winner(player):
            score = self.heuristic(self.board)  # Calculate the heuristic score of the current board
            self.transposition_table[board_key] = score  # Stores this score
            return score  # Return heuristic score

        if player == self.player:  # If it's the current player's turn
            value = -float('inf')  # Initialise the value to negative infinity for maximisation
            for point in possible_moves:
                original_value = self.board[point.board_num][point.pos]  # Saves the original value at the move position
                self.board[point.board_num][point.pos] = player  # Makes a hypothetical move
                score = self.alpha_beta_algorithm(depth + 1, 'o' if player == 'x' else 'x', alpha, beta, point.pos)  # Recurse with the new board state using alpha-beta search
                self.board[point.board_num][point.pos] = original_value  # Undoes the hypothetical move
                value = max(value, score)  # Updates the value if the current score is greater
                alpha = max(alpha, value)  # Updates alpha if the current value is greater
                if alpha >= beta:
                    break  # Prunes the remaining branches
            self.transposition_table[board_key] = value  # Stores computed value
            return value  # Returns computed value
        else:  # If it's the opponent's turn
            value = float('inf')  # Initialise the value to positive infinity for minimisation
            for point in possible_moves:
                original_value = self.board[point.board_num][point.pos]  # Saves the original value at the move position
                self.board[point.board_num][point.pos] = player  # Makes a hypothetical move
                score = self.alpha_beta_algorithm(depth + 1, 'o' if player == 'x' else 'x', alpha, beta, point.pos)  # Recurse with the new board state using alpha-beta search
                self.board[point.board_num][point.pos] = original_value  # Undoes the hypothetical move
                value = min(value, score)  # Updates the value if the current score is less
                beta = min(beta, value)  # Updates beta if the current value is less
                if alpha >= beta:
                    break  # Prunes the remaining branches
            self.transposition_table[board_key] = value  # Stores computed value
            return value  # Returns computed value

    def start(self, player):
        # Initialises and starts a new game for a particular player
        self.reset()  # Resets and prints initial board state
        self.move[0] = 0  # Initialises the first move
        self.player = player  # Sets to the starting player
        self.smaller()  # Computes scores for all smaller 3x3 board configurations

    def second_move(self, board_num, prev_move):
        # Determines second move based off opponents first move
        opponent = 'o' if self.player == 'x' else 'x'  # Determine whether opponent is x or o
        self.move[:2] = [board_num, prev_move]  # Stores both the first and second moves
        self.board[board_num][prev_move] = opponent  # Places the opponent's mark on the board
        this_move = self.moves(prev_move)  # Determines the best move based using the previous move
        self.move[2] = this_move  # Stores the third move
        self.board[prev_move][this_move] = self.player  # Places our mark on the baord
        return this_move  # Return the position of the third move

    def third_move(self, board_num, first_move, prev_move):
        # Calculate and perform the third move based off previous 2 moves
        self.move[:3] = [board_num, first_move, prev_move]  # Stores the first, second and third moves
        opponent = 'o' if self.player == 'x' else 'x'  # Determine whether opponent is x or o
        self.board[board_num][first_move] = self.player  # Places our mark on the first move position
        self.board[first_move][prev_move] = opponent  # Places the opponent's mark on the second move position
        self.index = 3  # Updates move index to 3
        self.step_count += 1  # Increments step count by 1

        this_move = self.moves(prev_move)  # Finds best move based off the previous move
        self.move[3] = this_move  # Stores the 4th move
        self.board[prev_move][this_move] = self.player  # Places our mark
        return this_move  # Return the position of the fourth move

    def next_move(self, prev_move):
        # Determiness and performs the next move
        if self.index is None:
            raise ValueError("Move not initialised")  # Raise an error if the move index is not set

        opponent = 'o' if self.player == 'x' else 'x'  # Determine whether opponent is x or o
        self.index += 1  # Increments the move index by 1
        self.move[self.index] = prev_move  # Stores the previous move at the current index
        self.board[self.move[self.index - 1]][prev_move] = opponent  # And places the opponent's mark at the previous move position

        self.index += 1  # Increment move index by 1 again for the next move
        self.step_count += 1  # Increment the step count by 1 as well

        if self.step_count > 8:
            if ((self.step_count % 3 == 0 and self.step_count < 16) or
                (self.step_count % 2 == 0 and self.step_count >= 17 and self.max_depth < 14)):
                self.max_depth += 1  # Increase the maximum depth based off the step count and game progression

        next_move = self.moves(prev_move)  # Determines the next best move
        self.move[self.index] = next_move  # Stores the next move at the current index
        self.board[prev_move][next_move] = self.player  # Places our mark
        return next_move  # Returns the next move position

    def last_move(self, prev_move):
        # Executes the last move of the game
        self.move[self.index + 1] = prev_move  # Stores the last move at the next index
        self.board[self.move[self.index]][prev_move] = 'o' if self.player == 'x' else 'x'  # Places the last mark
        self.index += 1  # Increments move index by 1

    def final(self, result, reason):
        # Records game result and reason
        self.result = result  # Stores the result as either a win, loss or draw
        self.reason = reason  # Store the reason for result

    def end(self):
        # End the game
        sys.exit()

    def implementation(self, data):
        # Process data from the game server and implements game commands
        command_pattern = re.compile(r'(\w+)\((.*)\)')  # Regex to extract commands
        match = command_pattern.match(data)  # Match the regex against the data
        if match:
            command, args = match.groups()  # Extracts commands and arguments
            if command == 'init':
                self.init()  # Initialises game settings
            elif command == 'start':
                self.start(args)  # Starts a new game with a particular player
            elif command == 'second_move':
                board_num, prev_move = map(int, args.split(','))  # Uses the board number and previous move
                return self.second_move(board_num, prev_move)  # Performs the second move
            elif command == 'third_move':
                board_num, first_move, prev_move = map(int, args.split(','))  # Uses the board number, first move, and previous move
                return self.third_move(board_num, first_move, prev_move)  # Performs the third move
            elif command == 'next_move':
                return self.next_move(int(args))  # Performs the next move
            elif command == 'last_move':
                return self.last_move(int(args))  # Performs the final move
            elif command in {'win', 'loss', 'draw'}:
                self.final(command.upper(), args)  # Sets the game result based off the command
            elif command == 'end':
                self.end()  # Finishes the game
        return None

def main():
    parser = argparse.ArgumentParser(description="Connects to server")  # Create command line argument parser
    parser.add_argument("-p", "--port", type=int, required=True, help="Enter port number")  # Defines the port number
    args = parser.parse_args()  # Parse command line arguments
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates a socket object for TCP/IP communication
    s.connect(('localhost', args.port))  # Connects to the game server using a particular port
    agent = Agent()
    try:
        while True:  # Recieves and processes data from the server
            text = s.recv(1024).decode()  # Receives data from the server and decodes it
            if not text:
                continue  # Continues to the next iteration if no data recieved
            responses = [agent.implementation(line) for line in text.split("\n") if line]  # Processes each line of data
            for response in responses:
                if response is None:
                    continue  # Continues to the next iteration if no response generated
                elif response == -1:
                    s.close()  # Closes the socket
                    return
                elif response > 0:
                    s.sendall(f"{response}\n".encode())  # Sends a response back to the server
    except KeyboardInterrupt:
        s.close()  # Close the socket and exits

if __name__ == "__main__":
    main()  # Execute the main function