# Simple quintris program! v0.2
# D. Crandall, Sept 2021

from copy import deepcopy
from itertools import product
from AnimatedQuintris import *
from SimpleQuintris import *
from kbinput import *
import time, sys
import collections

class HumanPlayer:
    def get_moves(self, quintris):
        print("Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\n  h for horizontal flip\nThen press enter. E.g.: bbbnn\n")
        moves = input()
        return moves

    def control_game(self, quintris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": quintris.left, "h": quintris.hflip, "n": quintris.rotate, "m": quintris.right, " ": quintris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
    def identify_piece(self, id_quintris):
        PIECES = id_quintris.PIECES
        pieces_names = ["A", "B", "C", "D", "E", "F"]
        pieces_dict = dict(zip(pieces_names, PIECES))
        identified_piece = ""

        for piece_name, piece in pieces_dict.items():
            piece_in_quintris = id_quintris.get_piece()[0]
            if(piece == piece_in_quintris):
                identified_piece = piece_name
                del id_quintris
                return identified_piece
            else:
                for _ in range(4):
                    id_quintris.rotate()
                    piece_in_quintris = id_quintris.get_piece()[0]
                    if(piece == piece_in_quintris):
                        identified_piece = piece_name
                        del id_quintris
                        return identified_piece

                id_quintris.hflip()
                piece_in_quintris = id_quintris.get_piece()[0]
                if(piece == piece_in_quintris):
                        identified_piece = piece_name
                        del id_quintris
                        return identified_piece

                for _ in range(4):
                    id_quintris.rotate()
                    piece_in_quintris = id_quintris.get_piece()[0]
                    if(piece == piece_in_quintris):
                        identified_piece = piece_name
                        del id_quintris
                        return identified_piece

    def get_col_of_matrix(self, matrix, i):
        return [row[i] for row in matrix]

    def get_utility(self, quintris):
        # Evaluate the utility of the board!
        # Return the utility of the board. The higher, the better!

        utility = 0
        ROWS = quintris.BOARD_HEIGHT
        COLS = quintris.BOARD_WIDTH
        board = quintris.get_board()

        board_matrix = []
        for i in range(ROWS):
            new_row = []
            for j in range(COLS):
                new_row.append(board[i][j])
            board_matrix.append(new_row)


        # Calculate the number of holes in the board i.e. whitespaces below x
        # Reward boards with less number of holes
        hole_count = 0
        holes = list()  # List to store indices of hole positions
        for j in range(COLS):
            flag = False
            for i in range(ROWS):
                if(flag and board_matrix[i][j] == ' '):
                    hole_count += 1
                    holes.append((i, j))
                if(board_matrix[i][j] == 'x'):
                    flag = True

        utility += 1 if hole_count == 0 else (1 / (2 * hole_count))
        # utility -= (5 * hole_count)

        # Calculate difference in the heights of columns
        # Lesser the difference, smoother the board - Better chances of completing a row
        # Reward smoothness
        heights = dict()
        for j in range(COLS):
            x_found = False
            for i in range(ROWS):
                if board_matrix[i][j] == 'x':
                    x_found = True
                    heights[j] = i
                    break
            if not x_found:
                heights[j] = ROWS

        max_column_height = min(heights.values())
        min_column_height = max(heights.values())
        height_difference = abs(max_column_height - min_column_height)

        multiplier = 5
        if(max_column_height < 16):
            multiplier = 7

        utility += 1 if height_difference == 0 else (1 / (multiplier * height_difference))
        # utility -= (2 * height_difference)

        # Calculate the no. of whitespaces in all the rows with an 'x'
        # Lesser the total number of whitespaces, better the board
        space_count = 0
        rows_with_x = 1
        for i in range(ROWS):
            if 'x' in board_matrix[i]:
                rows_with_x += 1
                for j in range(COLS):
                    if board_matrix[i][j] == ' ':
                        space_count += 1

        utility += 1 if space_count == 0 else (1 / space_count)

        n_pits = 0
        for j in range(COLS):
            x = self.get_col_of_matrix(board_matrix, j)
            if(collections.Counter(x)['x'] == ROWS):
                n_pits += 1
        # utility -= (space_count)
        utility += 1 if n_pits == 0 else (1 / (n_pits))
        # print(f"Holes: {hole_count}, Height Diff.: {height_difference}, Spaces: {space_count}")
        # print(f"Utility: {utility * 100}")
        return utility * 100

    def get_successors(self, quintris, base):
        """
        Get all variations for each of the moves for current piece
        Drop each variation in every column
        Calculate utility
        """
        temp_quintris = deepcopy(quintris)
        ROWS = temp_quintris.BOARD_HEIGHT
        COLS = temp_quintris.BOARD_WIDTH
       
        # base = temp_quintris.get_piece()[0]
        hflip_base = temp_quintris.hflip_piece(base)

        transformations = {
            '-': base,
            'h': hflip_base,
            'n': temp_quintris.rotate_piece(base, 90),
            'nn': temp_quintris.rotate_piece(base, 180),
            'nnn': temp_quintris.rotate_piece(base, 270),
            'hn': temp_quintris.rotate_piece(hflip_base, 90),
            'hnn': temp_quintris.rotate_piece(hflip_base, 180),
            'hnnn': temp_quintris.rotate_piece(hflip_base, 270)
        }

        successors = list()
        for next_move, next_piece in transformations.items():
            max_piece_width = max([len(row) for row in next_piece])
            # print('Max width:', max_piece_width)
            for col in range(COLS - max_piece_width + 1):
                # Create a new copy of the quintris object
                # for every valid column for each successor
                probable_quintris = deepcopy(temp_quintris)

                commands = {
                    'b': probable_quintris.left,
                    'm': probable_quintris.right,
                    'n': probable_quintris.rotate,
                    'h': probable_quintris.hflip
                }

                # Move next_piece to that column
                direction = ''
                if col < probable_quintris.col:
                    diff = probable_quintris.col - col
                    direction += ('b' * diff)
                    for _ in range(diff):
                        commands['b']()

                elif col > probable_quintris.col:
                    diff = col - probable_quintris.col
                    direction += ('m' * diff)
                    for _ in range(diff):
                        commands['m']()

                # Execute the actual moves that gave us the successor
                if '-' not in next_move:
                    for m in next_move:
                        commands[m]()

                # Drop the piece and calculate it's utility
                # If there is a high difference in score between the successor and the current state, reward it well!
                probable_quintris.down()
                moves = direction + next_move if '-' not in next_move else direction
                successors.append([
                    probable_quintris,
                    moves,
                    self.get_utility(probable_quintris) + ( 100 * (probable_quintris.state[1] - temp_quintris.state[1]))
                ])


        return successors

    def get_maximax_move(self, quintris, piece, depth):
        successors = self.get_successors(quintris, piece)

        if depth == 1:
            best_utility = max(successors, key=lambda x: x[-1])[-1]
            return best_utility
        else:
            return max(
                [[succ, self.get_maximax_move(succ[0], quintris.get_next_piece(), depth + 1)]
                for succ in successors],
                key=lambda x: x[1]
            )[0][1]
         

    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. quintris is an object that lets you inspect the board, e.g.:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def get_moves(self, quintris):

        current_piece = quintris.get_piece()[0]
        best_move = self.get_maximax_move(quintris, current_piece, 0)
        # print(best_move)

        # successors = self.get_successors(quintris, current_piece)
        # best_move = max(successors, key=lambda x: x[-1])[1]
        # print(best_move)
        return best_move


        # super simple current algorithm: just randomly move left, right, and rotate a few times
        # return random.choice("mnbh") * random.randint(1, 10)
       
    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "quintris" object to control the movement. In particular:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, quintris):
        # # another super simple algorithm: just move piece to the least-full column
        # while 1:
        #     time.sleep(0.1)

        #     board = quintris.get_board()
        #     column_heights = [ min([ r for r in range(len(board)-1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
        #     index = column_heights.index(max(column_heights))

        #     if(index < quintris.col):
        #         quintris.left()
        #     elif(index > quintris.col):
        #         quintris.right()
        #     else:
        #         quintris.down()
        commands = {
            'b': quintris.left,
            'm': quintris.right,
            'n': quintris.rotate,
            'h': quintris.hflip
        }

        while 1:
            time.sleep(0.1)
            current_piece = quintris.get_piece()[0]
            best_move = self.get_maximax_move(quintris, current_piece, 0)
            # successors = self.get_successors(quintris, current_piece)
            # best_move = max(successors, key=lambda x: x[-1])[1]
            for m in best_move:
                commands[m]()
                
            quintris.down()



###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print("unknown player!")

    if interface_opt == "simple":
        quintris = SimpleQuintris()
    elif interface_opt == "animated":
        quintris = AnimatedQuintris()
    else:
        print("unknown interface!")

    quintris.start_game(player)

except EndOfGame as s:
    print("\n\n\n", s)
