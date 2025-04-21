# Chinese Chess Game

This project is a simple implementation of the traditional Chinese chess game (Xiangqi) using Python and Pygame. The game allows two players to compete against each other by moving their pieces strategically on the board.

## Project Structure

```
chinese-chess-game
├── src
│   ├── main.py          # Entry point of the game
│   ├── game
│   │   ├── board.py     # Board class for managing the chessboard
│   │   ├── pieces.py    # Classes for each type of chess piece
│   │   └── rules.py     # Game rules and move validation
│   ├── view
│   │   └── draw.py      # Rendering the chessboard and pieces
│   └── utils
│       └── helpers.py   # Utility functions for the game
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chinese-chess-game
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   Execute the main script to start the game:
   ```bash
   python src/main.py
   ```

## Gameplay Rules

- The game is played on a 9x10 board.
- Each player has 16 pieces: 1 General, 2 Advisors, 2 Elephants, 2 Horses, 2 Chariots, 2 Cannons, and 5 Soldiers.
- The objective is to checkmate the opponent's General.
- Players take turns moving one piece at a time according to the movement rules defined for each piece.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. Your feedback and contributions are welcome!