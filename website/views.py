from . import db
from .data_mapper import map_penalty_records, map_to_game_summary
from .models import UserEntity, GameEntity, GameStatus, PenaltyEntity, PenaltyRecordEntity, ParticipantStatus, ParticipantEntity, TotalFineEntity
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
import json


from .logger_config import setup_logger

DEBUG = True

class PlayerListError(ValueError):
    pass

logger = setup_logger()

views = Blueprint('views', __name__) # setup a blueprint for flask, can be named w.e. best practice to name same as file

# Display homepage endpoint
@views.route('/') # decorator
@login_required
def home():
    return render_template("home.html", user=current_user)

# Display user_management site
@views.route('/user_management', methods=['GET'])
@login_required
def user_management():
    participants = ParticipantEntity.query.filter_by(user_id=current_user.id, status = ParticipantStatus.active)
    return render_template("user_management.html", participants=participants, user=current_user)

# Display Game creation and loading site
@views.route('/create_or_load_game/', methods=['GET'])
@login_required
def create_or_load_game():
    participants = ParticipantEntity.query.filter_by(user_id=current_user.id, status = ParticipantStatus.active)
    all_saved_games = GameEntity.query.filter_by(user_id = current_user.id, status = GameStatus.active).all()
    len_all_saved_games = len(all_saved_games)
    logger.debug("Length of all saved_games for user {} is {}".format(current_user.email, len_all_saved_games))
    return render_template("create_or_load_game.html", game_participants=participants, user=current_user, all_saved_games = all_saved_games, len_all_saved_games=len_all_saved_games)

# Display certain game
@views.route('/view_game/<game_id>', methods=['GET'])
@login_required
def view_game(game_id):
    try:
        game = GameEntity.query.filter_by(id = game_id,user_id = current_user.id).one()
    except:
        flash("No game was found", category="error")
        return render_template("create_or_load_game.html",user=current_user)
    # game_participants is a json object storing all the player_ids as a string
    all_penalties = PenaltyEntity.query.filter_by(user_id=current_user.id).all()
    game_participants = game.game_participants
    if game_participants is None or game_participants == "":
        flash("invalid game", category="error")
        return render_template("create_or_load_game.html", user=current_user)
    logger.info("Game Status for user {} is {}".format(current_user.email,game.status))
    all_participant_ids = []
    if game.status == GameStatus.active:
        participants_data = []
        # Iterate through all participant ids
        # Get all their PenaltyRecordEntities from database
        # Get their TotalFine from database
        for player in json.loads(game_participants):
            all_participant_ids.append(int(player))
            participant_record = PenaltyRecordEntity.query.filter_by(game_id=game.id, participant_id=player).first()
            participant_fine_sum = TotalFineEntity.query.filter_by(game_id=game.id, participant_id=player).first()
            # Map the Database Entities to useful data_models, a single object that stores everything needed for the player
            # (name, quantity for each penalty, the total_finesum and more)
            # All stored in a list and given to the template
            participants_data.extend(map_penalty_records(participant_record, game_id,all_penalties, participant_fine_sum))
    if game.status == GameStatus.save:
        participants_data = []
        for player in json.loads(game_participants):
            all_participant_ids.append(player)
            participant_records = PenaltyRecordEntity.query.filter_by(game_id=game.id, participant_id=player).all()
            participant_fine_sum = TotalFineEntity.query.filter_by(game_id=game.id, participant_id=player).first()
            participants_data.append(map_to_game_summary(participant_records, participant_fine_sum))
        logger.debug("All participant_ids going into the game: ", all_participant_ids)
    return render_template("view_game.html",user=current_user, game=game, all_penalties=all_penalties, player_record_list = participants_data, all_participant_ids=all_participant_ids)

# Display finished game summary
@views.route('/game_summary/<game_id>', methods=['POST','GET'])
@login_required
def game_summary(game_id):
    if request.method != 'POST' and request.method !='GET':
        abort(405)
    # Create a game summary object and map everything so far obtained to it in the finish_game endpoint
    all_penalties = PenaltyEntity.query.filter_by(user_id = current_user.id).all()
    target_game = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if target_game and target_game.status == GameStatus.finish:
        game_participants = target_game.game_participants
        game_summary_objects = []
        for player in json.loads(game_participants):
            participant_records = PenaltyRecordEntity.query.filter_by(game_id=target_game.id, participant_id=player).all()
            participant_fine_sum = TotalFineEntity.query.filter_by(game_id=target_game.id, participant_id=player).first()
            game_summary_objects.append(map_to_game_summary(participant_records,participant_fine_sum))
        tier_list = retrieve_tier_list(game_summary_objects)
        penalty_sum = 1 + len(all_penalties)
        return render_template("game_summary.html", user= current_user, game = target_game, all_penalties = all_penalties, game_summary_objects = game_summary_objects, tier_list = tier_list, penalty_sum = penalty_sum)
    else:
        flash("This game has not been finished yet", category="error")

def retrieve_tier_list(PenaltyRecordList):
    max_quantities = {}
    for record in PenaltyRecordList:
        for penalty in record.penalties:
            if penalty.penalty_name not in max_quantities or max_quantities[penalty.penalty_name][1] < penalty.penalty_quantity:
                max_quantities[penalty.penalty_name] = (record.participant_name, penalty.penalty_quantity)
    return max_quantities

@views.route('/penalties', methods=['GET'])
@login_required
def penalties():
    penalties = PenaltyEntity.query.filter_by(user_id=current_user.id)
    return render_template("penalties.html", user=current_user, all_penalties = penalties)

@views.route('/view_archive', methods=['GET'])
@login_required
def view_archive():
    all_finished_games = GameEntity.query.filter_by(user_id = current_user.id, status = 'finish').all()
    return render_template("view_archive.html", user=current_user, all_finished_games = all_finished_games)