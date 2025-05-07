import pygame
import sys
import numpy as np
from backend import *

pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
font = pygame.font.SysFont("monospace", 75)

def draw_board(board, user_color, ai_color):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, (0, 0, 255), (c*SQUARESIZE, (r+1)*SQUARESIZE, SQUARESIZE, SQUARESIZE))
            color = (0, 0, 0)
            if board[r][c] == PLAYER_PIECE:
                color = user_color
            elif board[r][c] == AI_PIECE:
                color = ai_color
            pygame.draw.circle(screen, color, (int(c*SQUARESIZE+SQUARESIZE/2), int((r+1)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def main():
    user_input = input("Choose your color (red/green/yellow): ").lower()
    color_map = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0)
    }
    user_color = color_map.get(user_input, (255, 0, 0))
    ai_color = (0, 255, 255)

    board = create_board()
    game_over = False
    turn = random.randint(PLAYER, AI)
    draw_board(board, user_color, ai_color)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION and turn == PLAYER:
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, user_color, (posx, int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, SQUARESIZE))
                col = event.pos[0] // SQUARESIZE
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        draw_board(board, user_color, ai_color)
                        label = font.render("You win!", 1, user_color)
                        screen.blit(label, (40, 10))
                        pygame.display.update()
                        pygame.time.wait(3000)
                        game_over = True
                    else:
                        turn = AI
                        draw_board(board, user_color, ai_color)

        if turn == AI and not game_over:
            col, _ = minimax(board, 5, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    draw_board(board, user_color, ai_color)
                    label = font.render("AI wins!", 1, ai_color)
                    screen.blit(label, (40, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True
                else:
                    draw_board(board, user_color, ai_color)
                    turn = PLAYER

if __name__ == "__main__":
    main()
