# Chess Game — Setup & Run Guide

## Files
```
chess_game/
├── chess.py      ← Chess engine (bitboard AI, all game logic)
├── main.py       ← Pygame GUI (drag-and-drop interface)
├── book.txt      ← (optional) Opening book — one move sequence per line
└── images/       ← (optional) Piece images — PNG files + chess_icon.ico
    ├── white_king.png
    ├── white_queen.png
    ├── white_rook.png
    ├── white_bishop.png
    ├── white_knight.png
    ├── white_pawn.png
    ├── white_joker.png
    ├── black_king.png
    ├── black_queen.png
    ├── black_rook.png
    ├── black_bishop.png
    ├── black_knight.png
    ├── black_pawn.png
    ├── black_joker.png
    └── chess_icon.ico
```

> **No images?** The game still works — it falls back to Unicode chess symbols (♔♛♜ etc.).

---

## Requirements

- Python 3.8 or newer
- pygame

### Install pygame

```bash
pip install pygame
```

---

## Run

```bash
# GUI mode (pygame window)
python main.py

# Console mode (text board, type moves like e2e4)
python chess.py      # (or import chess and call chess.play_as_white())
```

---

## Controls (GUI)

| Key / Action        | Effect                              |
|---------------------|-------------------------------------|
| Drag & drop piece   | Make your move                      |
| **H**               | Let AI make a move for you (hint)   |
| **U**               | Undo last 2 half-moves              |
| **C**               | Cycle board colour theme            |
| **P** / **D**       | Print move history to console       |
| **E**               | Print position evaluation           |
| **ESC** / **Q**     | Quit                                |

---

## Console mode — move notation

Type moves in any of these formats:

| Format   | Example  | Meaning               |
|----------|----------|-----------------------|
| Coordinate | `e2e4` | Pawn from e2 to e4   |
| Short algebraic | `e4` | Pawn to e4         |
| Piece + dest | `Nf3` | Knight to f3        |
| Castling | `O-O`  | King-side castle      |
| Castling | `O-O-O`| Queen-side castle     |

---

## Bugs Fixed (vs. original docx)

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from random import choicea` — typo | Changed to `choice` |
| 2 | `INITIAL_BOARD` referenced directly (mutable list shared) | Wrapped in `list()` copy in `Game.__init__` |
| 3 | `get_attacks()` / `get_moves()` returned implicit `None` for unmatched piece | Added `return 0` fallback |
| 4 | `count_attacks()` didn't guard `None` from `get_attacks()` | Added `if attacks and attacks & target` guard |
| 5 | `random_move()` passed generator to `choice()` (requires a sequence) | Wrapped in `list()` |
| 6 | `evaluated_move()` / `alpha_beta()` could call `choice([])` on empty list | Added empty-list guard |
| 7 | `find_in_book()` crashed with `FileNotFoundError` if `book.txt` absent | Wrapped in try/except |
| 8 | Default mutable argument `game=Game()` evaluated once at import time | Changed to `game=None` + `if game is None: game = Game()` |
| 9 | `pygame.display.flip()` called in `set_title()` (unnecessary) | Removed redundant flip |
| 10 | Image loading crashed whole program if `images/` folder missing | Wrapped in try/exist check with Unicode fallback |
| 11 | Key checks used raw ASCII codes (`113`, `104`, etc.) — fragile | Replaced with `pygame.K_*` constants |
