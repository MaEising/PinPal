from . import db
from .models import GameEntity,GameStatus, PenaltyEntity, PenaltyRecordEntity,ParticipantStatus, ParticipantEntity, TotalFineEntity
from .sanitize_inputs import sanitize_pay_amount, sanitize_participant_ids, sanitize_participant_id, sanitize_string
from .validate_inputs import delete_game_check, validate_gameid
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, jsonify
from flask_login import login_required, current_user
from .logger_config import setup_logger
import re



# Custom errors
class InvalidInputError(ValueError):
    pass

class GameCreationError(ValueError):
    pass

class ParticipantCreationError(ValueError):
    pass

class ParticipantDeletionError(ValueError):
    pass

class NotYetImplementedFunctionError(ValueError):
    pass

logger = setup_logger()

configure = Blueprint('configure', __name__) # setup a blueprint for flask, can be named w.e. best practice to name same as file

@configure.route('/new_users', methods=['POST'])
@login_required
def new_users():
    # Get username input and sanitize it
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            logger.info("{} requested username:{}".format(current_user.email,username))
            username = sanitize_string(username)
        except ValueError as e:
            return redirect(url_for("views.user_management", user=current_user))

        # if no existing_participant is found we create a fresh one else we reactivate it by setting status to active. 
        # If User already exists True is also returned but we flash error message
        is_participant_reactivated_or_existing = reactivate_existing_participant(username)
        if is_participant_reactivated_or_existing:
            return redirect(url_for("views.user_management", user=current_user))
        new_participant = ParticipantEntity(username = username, user_id=current_user.id, status=ParticipantStatus.active)
        db.session.add(new_participant)
        db.session.commit()
        flash('Nailed it, fresh participant added',category='success')
        return redirect(url_for("views.user_management", user=current_user))

# Check if the participant was created already. If it has and was set to inactive we just reactivate. If it exists and is still active
# we do not create a participant
def reactivate_existing_participant(username):
    existing_participant = ParticipantEntity.query.filter_by(username=username, user_id=current_user.id).first()
    if existing_participant:
        if existing_participant.status == ParticipantStatus.active:
            print("\n STATUS IS ACTIVE \n")
            flash("User already exists", category='error')
            return True
        elif existing_participant.status == ParticipantStatus.inactive:
            print("\n STATUS IS INACTIVE \n")
            existing_participant.status = ParticipantStatus.active
            flash("User reactivated", category='success')
            db.session.add(existing_participant)
            db.session.commit()
            return True
    return False
@configure.route('/delete_participant/<int:participant_id>', methods=['POST'])
@login_required
def delete_participant(participant_id):
  if request.method == 'POST':
    try:
        sanitize_participant_id(participant_id)
        participant_to_deactivate = ParticipantEntity.query.get(participant_id)
        participant_to_deactivate.status = ParticipantStatus.inactive
        db.session.add(participant_to_deactivate)
        db.session.commit()
        flash('User successfully deleted',category='success')
    except InvalidInputError as e:
        flash("Error deleting Participant, invalid Input",category="error")
    except KeyError as e:
        print(e)
        flash("Something went wrong", category="error")
  return redirect(url_for('views.user_management'))


###* GAME SECTION 
# TODO move this into seperate game configuration file

@configure.route('/new_game', methods=['POST'])
@login_required
def new_game():
    if request.method != 'POST':
        return redirect(url_for('views.create_game'))
    participant_ids = request.form.getlist('players')
    sanitize_participant_ids(participant_ids)
    if not participant_ids:
        flash('Please select at least one player.', 'error')
        return redirect(url_for('views.create_or_load_game'))
    all_penalties = PenaltyEntity.query.filter_by(user_id=current_user.id).all()
    if not all_penalties:
        flash('Please create atleast one penalty',category='error')
        return redirect(url_for('views.penalties'))
    game = GameEntity(user_id = current_user.id,game_participants=participant_ids, status=GameStatus.active)
    db.session.add(game)
    db.session.commit()
    records = []
    if game.id == None:
        flash('Something went wrong when creating the game','error')
    for player_id in participant_ids:
        fine_record = TotalFineEntity(game_id=game.id, participant_id=player_id)
        db.session.add(fine_record)
        for penalty in all_penalties:
            try: 
                participant_record = PenaltyRecordEntity(game_id=game.id, participant_id=player_id, penalty_id = penalty.id)
                records.append(participant_record)
            except:
                print("\n Error adding PenaltyRecordEntities for a participant to database - configure.py\n")
    try:
        db.session.add_all(records)
        db.session.commit()
    except:
        flash("Error creating game", category='error')
        db.session.rollback()
        return redirect(url_for('views.create_game'))
    return redirect(url_for('views.view_game', game_id = game.id)) 



@configure.route('/new_penalty', methods=['POST'])
@login_required
def new_penalty():
    if request.method == 'POST':
        pay_amount = float(request.form.get('pay_amount'))
        sanitize_pay_amount(pay_amount)
        title = request.form.get('title')
        title = sanitize_string(title)
    penalty = PenaltyEntity(pay_amount = pay_amount, title = title, user_id = current_user.id)
    db.session.add(penalty)
    db.session.commit()
    all_penalties = PenaltyEntity.query.filter_by(user_id=current_user.id).all
    return redirect(url_for("views.penalties", user=current_user, all_penalties = all_penalties))

@configure.route('/delete_penalty/<int:penalty_id>', methods=['POST'])
@login_required
def delete_penalty(penalty_id):
  if request.method == 'POST':
    penalty = PenaltyEntity.query.get(penalty_id)
    db.session.delete(penalty)
    db.session.commit()
    flash('Penalty successfully deleted',category='success')
  return redirect(url_for('views.penalties'))

@configure.route('/update_quantity', methods=['POST'])
@login_required
# Updates the given PenaltyRecord.penalty.quantity for one participant inside a game, writes the changes to the PenaltyRecordEntity database object
# also the total_fine the participant has to pay is updated inside the database
def update_quantity():
    is_performed = False
    if request.method != 'POST':
        abort(405)
    penalty_id = request.json.get("penaltyId")
    participant_id = request.json.get("participantId")
    action = request.json.get("action")
    game_id = request.json.get("game_id")
    print("\nRetrieved penalty_id:", penalty_id, "\n")
    print("\nRetrieved participant_id:", participant_id, "\n")
    print("\nRetrieved Action:", action, "\n")
    print("\nGame id :", game_id, "\n")
    # bunch of validating
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
    # take the PenaltyRecord from the database belonging to the participant for this exact penalty
    target_PenaltyRecordEntity = PenaltyRecordEntity.query.filter_by(game_id = game_id,penalty_id = penalty_id, participant_id = participant_id).first()
    total_fine = TotalFineEntity.query.filter_by(game_id = game_id, participant_id = participant_id).first()
    # Update the quantity inside the Database depending on the chosen action in the frontend. Make sure the quantity is not negative
    if action == 'add':
        target_PenaltyRecordEntity.quantity += 1
        is_performed = True
    elif action == 'subtract' and target_PenaltyRecordEntity.quantity >= 1:
        target_PenaltyRecordEntity.quantity -= 1
        is_performed = True
    # Get total_fine value, set totalFine value to new pay_amount
    if is_performed:
        total_fine_value = total_fine.get_value()
        total_fine_value += target_PenaltyRecordEntity.quantity * target_PenaltyRecordEntity.penalty.pay_amount
        total_fine.set_value(total_fine_value)
        # commit all to database
        db.session.add(target_PenaltyRecordEntity)
        db.session.add(total_fine)
        db.session.commit()
    return redirect(url_for('views.view_game', game_id = game_id))

@configure.route('/delete_game/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    validate_gameid(game_id)
    delete_game_check(game_id)
    game_to_delete = GameEntity.query.get(game_id)
    if not game_to_delete:
        flash("Game unavailable or unauthorized",category="error")
        return redirect(url_for('views.view_archive'))
    db.session.delete(game_to_delete)
    db.session.commit()
    return redirect(url_for('views.view_archive'))

@configure.route('/save_game/<int:game_id>', methods=['POST'])
@login_required
def save_game(game_id):
    if request.method != 'POST':
        abort(405)
    validate_gameid(game_id)
    game_entity = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    game_entity.status = GameStatus.save
    db.session.add(game_entity)
    db.session.commit()
    return redirect(url_for('views.view_game', game_id = game_entity.id))

@configure.route('/load_game/<int:game_id>', methods=['GET'])
@login_required
def load_game(game_id):
    if request.method != 'GET':
        abort(405)
    validate_gameid(game_id)
    game_entity = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    if game_entity.status.value != GameStatus.finish and game_entity.status != GameStatus.save:
        flash("Game has not been saved", category="error")
        return redirect(url_for('views.create_or_load_game'))
    return redirect(url_for('views.view_game', game_id = game_entity.id))

@configure.route('/finish_game/<int:game_id>', methods=['POST'])
@login_required
def finish_game(game_id):
    if request.method != 'POST':
        abort(405)
    validate_gameid(game_id)
    game_entity = GameEntity.query.filter_by(id = game_id, user_id = current_user.id).first()
    game_entity.status = GameStatus.finish
    db.session.add(game_entity)
    db.session.commit()
    # The code=307 argument specifies that the redirect should be sent as a POST request. 
    return redirect(url_for('views.game_summary', game_id = game_entity.id),code = '307')

### GAME SECTION