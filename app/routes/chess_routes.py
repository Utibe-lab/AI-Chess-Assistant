from flask import Blueprint, request, jsonify
from app.services.evaluations import evaluate_position
from app.services.openings import lookup_opening

chess_bp = Blueprint('chess', __name__)

@chess_bp.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    fen = data.get('fen')
    score = evaluate_position(fen)
    opening = lookup_opening(fen)
    return jsonify({
        'evaluation': score,
        'opening': opening
    })
