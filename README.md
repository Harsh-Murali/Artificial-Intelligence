# Artificial-Intelligence

**Nine Board Tic Tac Toe AI Agent – Python**

- **Stored** each 9x9 board as a 2D list-of-lists structure with a 10x10 padding layout to simplify indexing, move validation, and board visualization without extra condition checks.
- **Used** alpha-beta pruning with recursive depth-limited search, manually passing alpha and beta values across calls, and built transposition tables as hash dictionaries to cache and reuse board evaluations.
- **Implemented** a custom heuristic that summed positional multipliers (center, corners, edges) for move scoring, precomputed static small-board scores using itertools, and optimized evaluation speed.
- **Handled** full move history, dynamic max-depth increases after late-game states, direct TCP/IP socket communication with a game server, and regex-based game command parsing for real-time decision-making.

**Hashiwokakero Puzzle Solver – Python**

- Stored the puzzle as a 2D numpy array for fast access and updates, enabling efficient bridge placement during the solving process.
- Used a recursive backtracking algorithm with early-exit conditions and search pruning to reduce time complexity from brute-force exponential to manageable levels.
- Implemented valid bridge-checking, directional scans, and undo logic to explore the solution space while minimizing unnecessary steps.
