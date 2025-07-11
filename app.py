from flask import Flask, request, jsonify
import chess
import chess.pgn
import random
import sqlite3
from collections import defaultdict
import uuid

app = Flask(__name__)

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


PIECE_SQUARE_TABLES = {
    chess.PAWN: [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]
}

# Initialize opening book database
def init_opening_book():
    conn = sqlite3.connect('openings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS openings
                 (fen TEXT PRIMARY KEY, moves TEXT, name TEXT, eco TEXT, stats TEXT)''')
    
    # Sample opening data
    sample_openings = [
        ('rnbqkbnr/pppppppp/5n5/8/8/5N5/PPPPPPPP/RNBQKBNR w KQkq - 1 1',
         'e4,d4', 'Italian Game', 'C50', '{"win": 0.45, "draw": 0.35, "loss": 0.20}'),
        ('rnbqkbnr/pppp1ppp/5n5/4p3/4P3/5N5/PPPP1PPP/RNBQKBNR w KQkq - 0 1',
         'Nf3,d4', 'Ruy Lopez', 'C60', '{"win": 0.50, "draw": 0.30, "loss": 0.20}')
    ]
    
    c.executemany('INSERT OR IGNORE INTO openings VALUES (?, ?, ?, ?, ?)', sample_openings)
    conn.commit()
    conn.close()

# Evaluate board position
def evaluate_position(board):
    material = 0
    position_score = 0
    
    # Material evaluation
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            material += value if piece.color == chess.WHITE else -value
            
            # Positional evaluation
            if piece.piece_type in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece.piece_type]
                square_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                position_score += table[square_index] / 100.0 if piece.color == chess.WHITE else -table[square_index] / 100.0
    
    # King safety (simplified)
    king_safety = 0
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square:
            attackers = len(board.attackers(not color, king_square))
            king_safety += (-attackers * 0.5) if color == chess.WHITE else (attackers * 0.5)
    
    # Mobility
    mobility = len(list(board.legal_moves)) * 0.1 * (1 if board.turn == chess.WHITE else -1)
    
    return {
        'material': material,
        'position': position_score,
        'king_safety': king_safety,
        'mobility': mobility,
        'total': material + position_score + king_safety + mobility
    }

# Get opening information
def get_opening_info(fen):
    conn = sqlite3.connect('openings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM openings WHERE fen = ?', (fen,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'name': result[2],
            'eco': result[3],
            'moves': result[1].split(','),
            'stats': eval(result[4])  
        }
    return None

# Generate move suggestions
def generate_move_suggestions(board):
    suggestions = []
    for move in board.legal_moves:
        board.push(move)
        eval_score = evaluate_position(board)['total']
        board.pop()
        
        suggestions.append({
            'move': board.san(move),
            'score': eval_score,
            'description': f"Score: {eval_score:.2f}",
            'uci': move.uci()
        })
    
    suggestions.sort(key=lambda x: x['score'], reverse=(board.turn == chess.WHITE))
    return suggestions[:3]  

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)
    
    try:
        board = chess.Board(fen)
    except:
        return jsonify({'error': 'Invalid FEN'}), 400
    
    # Get evaluation
    evaluation = evaluate_position(board)
    
    # Get move suggestions
    suggestions = generate_move_suggestions(board)
    
    # Get opening info
    opening = get_opening_info(fen) or {
        'name': 'Unknown Opening',
        'eco': 'N/A',
        'moves': [],
        'stats': {'win': 0.5, 'draw': 0.3, 'loss': 0.2}
    }
    
    # Get threatened pieces
    threatened = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and board.is_attacked_by(not board.turn, square):
            threatened.append({
                'square': chess.square_name(square),
                'piece': piece.symbol()
            })
    
    return jsonify({
        'evaluation': evaluation,
        'suggestions': suggestions,
        'opening': opening,
        'threatened': threatened
    })

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)
    move = data.get('move')
    
    try:
        board = chess.Board(fen)
        board.push_uci(move)
        return jsonify({
            'fen': board.fen(),
            'san': board.san(chess.Move.from_uci(move))
        })
    except:
        return jsonify({'error': 'Invalid move or FEN'}), 400

if __name__ == '__main__':
    init_opening_book()
    app.run(debug=True)
