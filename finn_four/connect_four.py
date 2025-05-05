import pygame
import sys
import numpy as np
import math
import random

# Game settings
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT+1) * SQUARESIZE  # Extra row for UI
SIZE = (WIDTH, HEIGHT)

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

pygame.init()
FONT = pygame.font.SysFont("monospace", 50)

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all([board[r][c+i] == piece for i in range(4)]):
                return True

    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c] == piece for i in range(4)]):
                return True

    # Check positive diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c+i] == piece for i in range(4)]):
                return True

    # Check negative diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all([board[r-i][c+i] == piece for i in range(4)]):
                return True
    return False

def draw_board(board, player_color, ai_color):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, (r+1)*SQUARESIZE, SQUARESIZE, SQUARESIZE))
            color = BLACK
            if board[r][c] == PLAYER_PIECE:
                color = player_color
            elif board[r][c] == AI_PIECE:
                color = ai_color
            pygame.draw.circle(screen, color, (int(c*SQUARESIZE + SQUARESIZE/2), int((r+1)*SQUARESIZE + SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 5

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    return score

def score_position(board, piece):
    score = 0
    # Center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Positive Diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negative Diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)
    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, AI_PIECE):
                return (None, 1000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -1000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# taking user input for colour
player_color = RED if input("Choose your color (red/yellow): ").strip().lower() == "red" else YELLOW
ai_color = YELLOW if player_color == RED else RED

# Init game
board = create_board()
game_over = False
turn = random.randint(PLAYER, AI)

screen = pygame.display.set_mode(SIZE)
draw_board(board, player_color, ai_color)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            x_pos = event.pos[0]
            pygame.draw.circle(screen, player_color, (x_pos, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            col = int(event.pos[0] / SQUARESIZE)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)
                if winning_move(board, PLAYER_PIECE):
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    label = FONT.render("You win!", 1, player_color)
                    screen.blit(label, (40, 10))
                    game_over = True
                turn = AI
                draw_board(board, player_color, ai_color)

    if turn == AI and not game_over:
        col, _ = minimax(board, 4, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if winning_move(board, AI_PIECE):
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                label = FONT.render("AI wins!", 1, ai_color)
                screen.blit(label, (40, 10))
                game_over = True
            draw_board(board, player_color, ai_color)
            turn = PLAYER

    if game_over:
        pygame.display.update()
        pygame.time.wait(3000)
        board = create_board()
        game_over = False
        draw_board(board, player_color, ai_color)
