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
