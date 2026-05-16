"""
main.py — Pygame GUI for the Chess Game
Extracted and corrected from Chess_Game.docx

Requirements:
    pip install pygame chess-engine  (use the local chess.py in same folder)

Run:
    python main.py

Controls:
    Mouse drag  : Move pieces
    H           : Let AI make a move for you
    U           : Undo last 2 moves (your move + AI's)
    C           : Change board colour scheme
    P / D       : Print move list to console
    E           : Print current evaluation score
    ESC / Q     : Quit
"""

import sys
import os

# Ensure chess.py in same directory is found first
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chess                          # local chess.py engine
import pygame
from random import choice             # BUG FIX: was 'choicea' (typo in original)
from traceback import format_exc
from sys import stderr
from time import strftime
from copy import deepcopy

pygame.init()

# ── Constants ────────────────────────────────────────────────────────────────

SQUARE_SIDE    = 80          # pixels per square (increased from 50 for readability)
AI_SEARCH_DEPTH = 2

RED_CHECK           = (240, 150, 150)
WHITE_COLOR         = (255, 255, 255)
BLUE_LIGHT          = (140, 184, 219)
BLUE_DARK           = (91,  131, 159)
GRAY_LIGHT          = (240, 240, 240)
GRAY_DARK           = (200, 200, 200)
CHESSWEBSITE_LIGHT  = (212, 202, 190)
CHESSWEBSITE_DARK   = (100,  92,  89)
LICHESS_LIGHT       = (240, 217, 181)
LICHESS_DARK        = (181, 136,  99)
LICHESS_GRAY_LIGHT  = (164, 164, 164)
LICHESS_GRAY_DARK   = (136, 136, 136)

BOARD_COLORS = [
    (GRAY_LIGHT,         GRAY_DARK),
    (BLUE_LIGHT,         BLUE_DARK),
    (WHITE_COLOR,        BLUE_LIGHT),
    (CHESSWEBSITE_LIGHT, CHESSWEBSITE_DARK),
    (LICHESS_LIGHT,      LICHESS_DARK),
    (LICHESS_GRAY_LIGHT, LICHESS_GRAY_DARK),
]

BOARD_COLOR = choice(BOARD_COLORS)

CLOCK      = pygame.time.Clock()
CLOCK_TICK = 30
SCREEN     = pygame.display.set_mode((8 * SQUARE_SIDE, 8 * SQUARE_SIDE), pygame.RESIZABLE)
SCREEN_TITLE = 'Chess Game'

# ── Load piece images ─────────────────────────────────────────────────────────
# BUG FIX: Wrapped image loading in try/except so the game still runs
#           even if the images/ folder is missing, falling back to text rendering.

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

def _load(filename):
    path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(path):
        return pygame.image.load(path)
    return None   # will fall back to text rendering

BLACK_KING   = _load('black_king.png')
BLACK_QUEEN  = _load('black_queen.png')
BLACK_ROOK   = _load('black_rook.png')
BLACK_BISHOP = _load('black_bishop.png')
BLACK_KNIGHT = _load('black_knight.png')
BLACK_PAWN   = _load('black_pawn.png')
BLACK_JOKER  = _load('black_joker.png')
WHITE_KING   = _load('white_king.png')
WHITE_QUEEN  = _load('white_queen.png')
WHITE_ROOK   = _load('white_rook.png')
WHITE_BISHOP = _load('white_bishop.png')
WHITE_KNIGHT = _load('white_knight.png')
WHITE_PAWN   = _load('white_pawn.png')
WHITE_JOKER  = _load('white_joker.png')

# Map chess engine piece codes → (image, fallback_text)
PIECE_IMAGE_MAP = {
    chess.BLACK | chess.KING:   (BLACK_KING,   '♚'),
    chess.BLACK | chess.QUEEN:  (BLACK_QUEEN,  '♛'),
    chess.BLACK | chess.ROOK:   (BLACK_ROOK,   '♜'),
    chess.BLACK | chess.BISHOP: (BLACK_BISHOP, '♝'),
    chess.BLACK | chess.KNIGHT: (BLACK_KNIGHT, '♞'),
    chess.BLACK | chess.PAWN:   (BLACK_PAWN,   '♟'),
    chess.BLACK | chess.JOKER:  (BLACK_JOKER,  'J'),
    chess.WHITE | chess.KING:   (WHITE_KING,   '♔'),
    chess.WHITE | chess.QUEEN:  (WHITE_QUEEN,  '♕'),
    chess.WHITE | chess.ROOK:   (WHITE_ROOK,   '♖'),
    chess.WHITE | chess.BISHOP: (WHITE_BISHOP, '♗'),
    chess.WHITE | chess.KNIGHT: (WHITE_KNIGHT, '♘'),
    chess.WHITE | chess.PAWN:   (WHITE_PAWN,   '♙'),
    chess.WHITE | chess.JOKER:  (WHITE_JOKER,  'J'),
}

# Load icon separately
_icon_path = os.path.join(IMAGES_DIR, 'chess_icon.ico')
if os.path.exists(_icon_path):
    pygame.display.set_icon(pygame.image.load(_icon_path))
pygame.display.set_caption(SCREEN_TITLE)

FALLBACK_FONT = pygame.font.SysFont('segoeuisymbol', int(SQUARE_SIDE * 0.75))

# ── Helpers ───────────────────────────────────────────────────────────────────

def resize_screen(square_side_len):
    global SQUARE_SIDE, SCREEN, FALLBACK_FONT
    SCREEN = pygame.display.set_mode((8 * square_side_len, 8 * square_side_len), pygame.RESIZABLE)
    SQUARE_SIDE = square_side_len
    FALLBACK_FONT = pygame.font.SysFont('segoeuisymbol', int(SQUARE_SIDE * 0.75))


def print_empty_board():
    SCREEN.fill(BOARD_COLOR[0])
    paint_dark_squares(BOARD_COLOR[1])


def paint_square(square, square_color):
    col = chess.FILES.index(square[0])
    row = 7 - chess.RANKS.index(square[1])
    pygame.draw.rect(SCREEN, square_color,
                     (SQUARE_SIDE * col, SQUARE_SIDE * row, SQUARE_SIDE, SQUARE_SIDE), 0)


def paint_dark_squares(square_color):
    for position in chess.single_gen(chess.DARK_SQUARES):
        paint_square(chess.bb2str(position), square_color)


def get_square_rect(square):
    col = chess.FILES.index(square[0])
    row = 7 - chess.RANKS.index(square[1])
    return pygame.Rect((col * SQUARE_SIDE, row * SQUARE_SIDE), (SQUARE_SIDE, SQUARE_SIDE))


def coord2str(position, color=chess.WHITE):
    if color == chess.WHITE:
        file_index = int(position[0] / SQUARE_SIDE)
        rank_index = 7 - int(position[1] / SQUARE_SIDE)
    else:  # BLACK (flipped board)
        file_index = 7 - int(position[0] / SQUARE_SIDE)
        rank_index = int(position[1] / SQUARE_SIDE)
    file_index = max(0, min(7, file_index))   # BUG FIX: clamp to board
    rank_index = max(0, min(7, rank_index))
    return chess.FILES[file_index] + chess.RANKS[rank_index]


def blit_piece(piece_code, rect):
    """Draw a piece using its image, or fall back to Unicode text."""
    if piece_code not in PIECE_IMAGE_MAP:
        return
    img, symbol = PIECE_IMAGE_MAP[piece_code]
    if img is not None:
        scaled = pygame.transform.smoothscale(img, (SQUARE_SIDE, SQUARE_SIDE))
        SCREEN.blit(scaled, rect)
    else:
        is_white_piece = (piece_code & chess.COLOR_MASK) == chess.WHITE
        color = (20, 20, 20) if is_white_piece else (240, 240, 240)
        text_surf = FALLBACK_FONT.render(symbol, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        SCREEN.blit(text_surf, text_rect)


def print_board(board, color=chess.WHITE):
    if color == chess.WHITE:
        printed_board = board
    else:
        printed_board = chess.rotate_board(board)

    print_empty_board()

    if chess.is_check(board, chess.WHITE):
        paint_square(chess.bb2str(chess.get_king(printed_board, chess.WHITE)), RED_CHECK)
    if chess.is_check(board, chess.BLACK):
        paint_square(chess.bb2str(chess.get_king(printed_board, chess.BLACK)), RED_CHECK)

    # Draw all pieces
    for piece_code in PIECE_IMAGE_MAP:
        piece_type = piece_code & chess.PIECE_MASK
        piece_color = piece_code & chess.COLOR_MASK
        for position in chess.colored_piece_gen(printed_board, piece_type, piece_color):
            rect = get_square_rect(chess.bb2str(position))
            blit_piece(piece_code, rect)

    pygame.display.flip()


def set_title(title):
    pygame.display.set_caption(title)


def make_ai_move(game, color):
    set_title(SCREEN_TITLE + ' - Calculating move...')
    ai_move = chess.get_AI_move(game, AI_SEARCH_DEPTH)
    if ai_move is None:
        set_title(SCREEN_TITLE)
        return game
    new_game = chess.make_move(game, ai_move)
    set_title(SCREEN_TITLE)
    print_board(new_game.board, color)
    return new_game


def try_move(game, attempted_move):
    for move in chess.legal_moves(game, game.to_move):
        if move == attempted_move:
            game = chess.make_move(game, move)
    return game


# ── Main game loop ─────────────────────────────────────────────────────────────

def play_as(game, color):
    global BOARD_COLOR

    run     = True
    ongoing = True
    joker   = 0

    try:
        while run:
            CLOCK.tick(CLOCK_TICK)
            print_board(game.board, color)

            if chess.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + chess.get_outcome(game))
                ongoing = False

            if ongoing and game.to_move == chess.opposing_color(color):
                game = make_ai_move(game, color)

            if chess.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + chess.get_outcome(game))
                ongoing = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    leaving_square = coord2str(event.pos, color)

                if event.type == pygame.MOUSEBUTTONUP:
                    arriving_square = coord2str(event.pos, color)
                    if ongoing and game.to_move == color:
                        move = (chess.str2bb(leaving_square), chess.str2bb(arriving_square))
                        game = try_move(game, move)
                        print_board(game.board, color)

                if event.type == pygame.KEYDOWN:
                    # ESC or Q → quit
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        run = False
                    # H → AI hint move
                    if event.key == pygame.K_h and ongoing:
                        game = make_ai_move(game, color)
                    # U → undo
                    if event.key == pygame.K_u:
                        game = chess.unmake_move(game)
                        game = chess.unmake_move(game)
                        set_title(SCREEN_TITLE)
                        print_board(game.board, color)
                        ongoing = True
                    # C → cycle colour scheme
                    if event.key == pygame.K_c:
                        new_colors = deepcopy(BOARD_COLORS)
                        new_colors.remove(BOARD_COLOR)
                        BOARD_COLOR = choice(new_colors)
                        print_board(game.board, color)
                    # P or D → print move list
                    if event.key in (pygame.K_p, pygame.K_d):
                        print(game.get_move_list() + '\n')
                        print('\n'.join(game.position_history))
                    # E → evaluation
                    if event.key == pygame.K_e:
                        print('eval = ' + str(chess.evaluate_game(game) / 100))
                    # J → Easter-egg joker transform (press 13 times)
                    if event.key == pygame.K_j:
                        joker += 1
                        if joker == 13 and chess.get_queen(game.board, color):
                            queen_index = chess.bb2index(chess.get_queen(game.board, color))
                            game.board[queen_index] = color | chess.JOKER
                            print_board(game.board, color)

                if event.type == pygame.VIDEORESIZE:
                    if SCREEN.get_height() != event.h:
                        resize_screen(int(event.h / 8.0))
                    elif SCREEN.get_width() != event.w:
                        resize_screen(int(event.w / 8.0))
                    print_board(game.board, color)

    except Exception:
        print(format_exc(), file=stderr)
        with open('bug_report.txt', 'a') as bug_file:
            bug_file.write('----- ' + strftime('%x %X') + ' -----\n')
            bug_file.write(format_exc())
            bug_file.write('\nPlaying as WHITE:\n\t' if color == chess.WHITE else '\nPlaying as BLACK:\n\t')
            bug_file.write(game.get_move_list() + '\n\t')
            bug_file.write('\n\t'.join(game.position_history))
            bug_file.write('\n-----------------------------\n\n')


def play_as_white(game=None):
    if game is None:
        game = chess.Game()
    return play_as(game, chess.WHITE)


def play_as_black(game=None):
    if game is None:
        game = chess.Game()
    return play_as(game, chess.BLACK)


def play_random_color(game=None):
    if game is None:
        game = chess.Game()
    color = choice([chess.WHITE, chess.BLACK])
    play_as(game, color)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    play_random_color()
    pygame.quit()
