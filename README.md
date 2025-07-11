# AI Chess Assistant

## Overview
The **AI Chess Assistant** is a web-based application designed to provide chess players with move suggestions, position evaluations, and strategic insights based on the current board state. Built using **Flask** and **Python**, it features an interactive chessboard interface, supports **FEN** notation input, and integrates an **opening book database**.

The system evaluates positions using piece values, positional factors, king safety, and mobility, while also identifying threatened pieces and legal moves.

---

##  Objective
Provide intelligent move suggestions and strategic analysis based on the chessboard state, leveraging **position evaluation** and **opening book lookup**.

---

##  Features
-  **Interactive Chessboard**: Visual board with piece movement and FEN notation input.
-  **Position Evaluation**: Assesses material, positional advantage, king safety, and mobility.
-  **Opening Book Lookup**: Identifies known openings (ECO codes, common moves, stats).
-  **Move Suggestions**: Top 3 move recommendations with evaluation and reasoning.
-  **Threat Visualization**: Highlights threatened pieces and legal moves.
-  **Game History**: Tracks moves in algebraic notation.
-  **Board Tools**: Flip board, reset, and load positions via FEN.
-  **Responsive UI**: Bootstrap-based UI for a clean experience.

---

##  Computational Techniques

###  Position Evaluation
- **Material**: Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9
- **Positional**: Piece-square tables for key pieces
- **King Safety**: Count of attackers to king's square
- **Mobility**: Number of legal moves

###  Opening Book Lookup
- **SQLite Database** with:
  - FEN keys
  - Opening name & ECO code
  - Common follow-ups and win/draw/loss percentages

---

##  Dataset

### Types:
- Opening theory
- Chess games

### Sources:
- [Chess.com API](https://www.chess.com/news/view/published-data-api)
- [Lichess Database](https://database.lichess.org)
- Stockfish-compatible formats

---

