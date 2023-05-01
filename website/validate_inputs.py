from flask import jsonify, redirect, url_for, flash
from flask_login import  current_user
from .models import GameEntity, GameStatus
import re

def validate_gameid(game_id):
    if not re.match(r'^[0-9]+', str(game_id)):
        return jsonify({"status": "error", "message": "Invalid game ID"}), 400
    game_to_validate = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if game_to_validate == None:
        return jsonify({"status": "error", "message": "Game does not exist"}), 400

def delete_game_check(game_id):
    game_to_delete = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if not game_to_delete:
        flash("Game not found or unauthorized",category="error")
        return redirect(url_for('views.view_archive'))
    if not game_to_delete.status == GameStatus.FINISH:
        flash("Game is still running or broken",category="error")
        return redirect(url_for('views.view_archive'))