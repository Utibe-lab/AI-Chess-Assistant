import chess

def evaluate_position(fen):
    board = chess.Board(fen)
    material = sum(piece_value(piece) for piece in board.piece_map().values())
    return {'material_score': material}

def piece_value(piece):
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    return values.get(piece.piece_type, 0)
