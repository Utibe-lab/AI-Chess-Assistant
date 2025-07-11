def lookup_opening(fen):
    # You’ll replace this with a database lookup or PGN parser
    if "rnbqkbnr" in fen:
        return "Likely Opening: King's Pawn Game"
    return "Unknown Opening"
