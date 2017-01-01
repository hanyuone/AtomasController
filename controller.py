import random
import subprocess

atom_range = [1, 3]
board = []
score = 0
move_number = 0
carry_over = " "
previous_moves = []

specials = ["+", "-", "B", "C"]


def plus_process(user_input):
    global board, score, previous_moves, matches
    previous_moves = []
    matches = 0

    def score_calc(atom):
        global score, matches
        if matches == 0:
            score += int(round((1.5 * atom) + 1.25, 0))
        else:
            if atom < final_atom:
                outer = final_atom - 1
            else:
                outer = atom
            score += ((-final_atom + outer + 3) * matches) - final_atom + (3 * outer) + 3
        matches += 1

    if len(board) < 1 or user_input == "":
        board.append("+")
        return None
    board_start = board[:int(user_input) + 1]
    board_end = board[int(user_input) + 1:]
    final_atom = 0
    while len(board_start) > 0 and len(board_end) > 0:
        if board_start[-1] == board_end[0] and board_end[0] != "+":
            if final_atom == 0:
                final_atom = board_end[0] + 1
            elif board_end[0] >= final_atom:
                final_atom += 2
            else:
                final_atom += 1
            score_calc(board_end[0])
            board_start = board_start[:-1]
            board_end = board_end[1:]
        else:
            break
    if len(board_start) == 0:
        while len(board_end) > 1:
            if board_end[0] == board_end[-1] and board_end[0] != "+":
                if final_atom == 0:
                    final_atom = board_end[0]
                elif board_end[0] >= final_atom:
                    final_atom += 2
                else:
                    final_atom += 1
                score_calc(board_end[0])
                board_end = board_end[1:-1]
            else:
                break
    if len(board_end) == 0:
        while len(board_start) > 1:
            if board_start[0] == board_start[-1] and board_start[0] != "+":
                if board_start[0] >= final_atom:
                    final_atom += 2
                else:
                    final_atom += 1
                score_calc(board_start[0])
                board_start = board_start[1:-1]
            else:
                break
    if matches == 0:
        board = board_start + ["+"] + board_end
    else:
        board = board_start + [final_atom] + board_end
        for a in range(len(board) - 1):
            if board[a] == "+":
                if board[(a + 1) % len(board)] == board[a - 1]:
                    board = board[:a - 1] + board[a:]
                    plus_process(a)
                    break


def minus_process(user_input, minus_check):
    global carry_over, board
    carry_atom = board[int(user_input)]
    if user_input == len(board) - 1:
        board = board[:-1]
    else:
        board = board[:int(user_input)] + board[int(user_input) + 1:]
    if minus_check == "y":
        carry_over = "+"
    elif minus_check == "n":
        carry_over = str(carry_atom)


def black_plus_process(user_input):
    global board
    if board[int(user_input)] == "+":
        if board[int(user_input) + 1] == "+":
            inter_atom = 4
        else:
            inter_atom = board[int(user_input) + 1] + 2
    else:
        if board[int(user_input)] + 1 == "+":
            inter_atom = board[int(user_input)] + 2
        else:
            inter_list = [board[int(user_input)], board[int(user_input) + 1]]
            inter_atom = (inter_list.sort())[1] + 2
    board = board[int(user_input) - 1:] + [inter_atom] * 2 + board[int(user_input) + 1:]
    plus_process(int(user_input) - 1)


def clone_process(user_input):
    global carry_over
    carry_over = str(board[user_input])


def regular_process(user_input):
    global board
    if user_input == "":
        board.append(random.randint(atom_range[0], atom_range[1]))
    else:
        board = board[:int(user_input) + 1] + [random.randint(atom_range[0], atom_range[1])] + \
                board[int(user_input) + 1:]


def gen_specials():
    special = random.randint(1, 240)
    if special <= 48:
        return "+"
    elif special <= 60 and len(board) > 0:
        return "-"
    elif special <= 64 and len(board) > 0 and score >= 750:
        return "B"
    elif special <= 67 and len(board) > 0 and score >= 1500:
        return "C"
    else:
        small_atoms = []
        for atom in board:
            if atom not in specials and atom < atom_range[0]:
                small_atoms.append(atom)
        small_atom_check = random.randint(1, len(board))
        if small_atom_check <= len(small_atoms):
            return str(small_atoms[small_atom_check - 1])
        else:
            return str(random.randint(atom_range[0], atom_range[1]))


def specials_call(atom, user_input):
    specials_dict = {
        "+": plus_process,
        "-": minus_process,
        "B": black_plus_process,
        "C": clone_process
    }
    if atom in specials_dict.keys():
        if atom == "-":
            minus_process(user_input[0], user_input[1])
        else:
            specials_dict[atom](user_input[0])
    else:
        regular_process(user_input[0])


def init():
    global board, score, move_number, carry_over, previous_moves
    board = []
    score = 0

    for _ in range(6):
        board.append(random.randint(1, 3))

    while len(board) <= 18:
        move_number += 1
        if move_number % 40 == 0:
            atom_range[0] += 1
            atom_range[1] += 1
        if carry_over != " ":
            special_atom = carry_over
            carry_over = " "
        elif len(previous_moves) >= 5:
            special_atom = "+"
        else:
            special_atom = gen_specials()
        previous_moves.append(special_atom)
        bot_command = "python derp.py"
        bot = subprocess.Popen(bot_command.split(),
                               stdout = subprocess.PIPE,
                               stdin = subprocess.PIPE)
        bot.stdin.write("/".join([
            str(score),
            str(move_number),
            str(special_atom),
            " ".join([str(x) for x in board])
        ]))
        bot.stdin.close()
        all_user_input = bot.stdout.readline().strip("\n").split(" ")
        specials_call(special_atom, all_user_input)

    print("Game over! Your score is " + str(score))

if __name__ == "__main__":
    for a in range(20):
        init()
