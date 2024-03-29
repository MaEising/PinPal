from flask import jsonify, redirect, url_for, flash
from flask_login import  current_user
from .models import GameEntity, GameStatus
import re
from .logger_config import setup_logger

logger = setup_logger()

def validate_gameid(game_id):
    if not re.match(r'^[0-9]+', str(game_id)):
        return jsonify({"status": "error", "message": "Invalid game ID"}), 400
    game_to_validate = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if game_to_validate == None:
        logger.info("User {} requested invalid game with id {}".format(current_user.email, game_id))
        return jsonify({"status": "error", "message": "Game does not exist"}), 400

def delete_game_check(game_id):
    game_to_delete = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if not game_to_delete:
        flash("Game not found or unauthorized",category="error")
        return redirect(url_for('views.view_archive'))
    if not game_to_delete.status == GameStatus.finish:
        flash("Game is still running or broken",category="error")
        return redirect(url_for('views.view_archive'))


def validate_quantity_input(data):
    penalty_id = data.get("penaltyId")
    participant_id = data.get("participantId")
    action = data.get("action")
    game_id = data.get("game_id")
    if not re.match(r'^[0-9]+', str(game_id)):
        return jsonify({"status": "error", "message": "Invalid game ID"}), 400
    if not re.match(r'^[0-9]+', str(penalty_id)):
        return jsonify({"status": "error", "message": "Invalid penalty ID"}), 400
    if not re.match(r'^[0-9]+', str(participant_id)):
        return jsonify({"status": "error", "message": "Invalid participant ID"}), 400
    if action != 'add' and action != 'subtract':
        return jsonify({"status": "error", "message": "Invalid action"}), 400
    if not GameEntity.query.filter_by(user_id=current_user.id,id=game_id).first():
        return jsonify({"status": "error", "message": "Invalid Game"}), 400
    return penalty_id, participant_id, action, game_id