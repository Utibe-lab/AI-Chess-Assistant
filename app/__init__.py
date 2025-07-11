from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes.chess_routes import chess_bp
    app.register_blueprint(chess_bp, url_prefix="/chess")

    return app
