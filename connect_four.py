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
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
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
screen = pygame.display.set_mode(SIZE)

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT-1, -1, -1):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all([board[r][c+i] == piece for i in range(4)]):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c] == piece for i in range(4)]):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c+i] == piece for i in range(4)]):
                return True
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
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

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

def get_ai_depth(level):
    if level == "easy":
        return 2
    elif level == "hard":
        return 6

def choose_difficulty():
    font = pygame.font.SysFont("monospace", 40)
    easy_button = pygame.Rect(150, 200, 200, 50)
    hard_button = pygame.Rect(150, 300, 200, 50)

    screen.fill(WHITE)
    label = font.render("Choose Difficulty:", 1, BLACK)
    screen.blit(label, (100, 50))

    pygame.draw.rect(screen, BLUE, easy_button)
    screen.blit(font.render("Easy", 1, WHITE), (easy_button.x + 75, easy_button.y + 10))

    pygame.draw.rect(screen, BLUE, hard_button)
    screen.blit(font.render("Hard", 1, WHITE), (hard_button.x + 75, hard_button.y + 10))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if easy_button.collidepoint(pos):
                    return "easy"
                if hard_button.collidepoint(pos):
                    return "hard"

def choose_color():
    font = pygame.font.SysFont("monospace", 40)
    red_button = pygame.Rect(150, 200, 200, 50)
    yellow_button = pygame.Rect(150, 300, 200, 50)

    screen.fill(WHITE)
    label = font.render("Choose Your Color:", 1, BLACK)
    screen.blit(label, (100, 50))

    pygame.draw.rect(screen, RED, red_button)
    screen.blit(font.render("Red", 1, WHITE), (red_button.x + 75, red_button.y + 10))

    pygame.draw.rect(screen, YELLOW, yellow_button)
    screen.blit(font.render("Yellow", 1, BLACK), (yellow_button.x + 50, yellow_button.y + 10))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if red_button.collidepoint(pos):
                    return RED
                if yellow_button.collidepoint(pos):
                    return YELLOW

# Game Start
difficulty = choose_difficulty()
player_color = choose_color()
ai_color = YELLOW if player_color == RED else RED
ai_depth = get_ai_depth(difficulty)

board = create_board()
game_over = False
turn = random.randint(PLAYER, AI)
draw_board(board, player_color, ai_color)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if not game_over:
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                pygame.draw.circle(screen, player_color, (event.pos[0], int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
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
        col, _ = minimax(board, ai_depth, -math.inf, math.inf, True)
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
