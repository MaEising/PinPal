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
            username = sanitize_string(username)
            logger.info("{} requested username:{}".format(current_user.email,username))
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
            flash("User already exists", category='error')
            return True
        elif existing_participant.status == ParticipantStatus.inactive:
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
        logger.error("Key error occured by user {}, it was: {}".format(current_user.id,e))
        flash("Something went wrong", category="error")
  return redirect(url_for('views.user_management'))


###* GAME SECTION 
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
    for id in participant_ids:
        fine_record = TotalFineEntity(game_id=game.id, participant_id=id)
        db.session.add(fine_record)
        for penalty in all_penalties:
            try: 
                participant_record = PenaltyRecordEntity(game_id=game.id, participant_id=id, penalty_id = penalty.id)
                records.append(participant_record)
            except:
                logger.debug("PenaltyRecordEntities for user {} could not be added to database".format(current_user.email))
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
        if request.form.get('is_invert'):
            penalty = PenaltyEntity(pay_amount = pay_amount, title = title, user_id = current_user.id, invert=True)
        else:
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

# The total_fine for the Player that got a penalty is not updated if the penalty is inverted because this means everybody elses total_fine is increased.
# The total_fine increase for everybody else is handled in update_inverted_quantity()
def update_quantity_and_total_fine(target_PenaltyRecordEntity, total_fine, action):
    is_performed = False
    if action == 'add':
        target_PenaltyRecordEntity.quantity += 1
        total_fine.add_value(target_PenaltyRecordEntity.penalty.pay_amount)
        is_performed = True
    elif action == 'subtract' and target_PenaltyRecordEntity.quantity >= 1:
        target_PenaltyRecordEntity.quantity -= 1
        total_fine.subtract_value(target_PenaltyRecordEntity.penalty.pay_amount)
        is_performed = True
    logger.debug("TotalFine for {} updated to {}".format(current_user.id,total_fine.total_pay_amount))
    return is_performed

# Increase the quantity inside target_PenaltyRecordEntity, increase / decrease all_other_total_fines with the target_PenaltyRecordEntity.penalty.pay_amount
def update_inverted_quantity(target_PenaltyRecordEntity, all_other_total_fines ,action):
    if action == 'add':
        target_PenaltyRecordEntity.quantity += 1
    elif action == 'subtract' and target_PenaltyRecordEntity.quantity >= 1:
        target_PenaltyRecordEntity.quantity -= 1
    for total_fine in all_other_total_fines:
        if action == 'add':
            total_fine.add_value(target_PenaltyRecordEntity.penalty.pay_amount)
        elif action == 'subtract' and target_PenaltyRecordEntity.quantity >= 1:
            total_fine.subtract_value(target_PenaltyRecordEntity.penalty.pay_amount)
        db.session.add(total_fine)
        logger.debug("total_fine for participant {} has been updated to {}".format(total_fine.participant_id,total_fine.total_pay_amount))


@configure.route('/update_quantity', methods=['POST'])
@login_required
# Updates the given PenaltyRecord.penalty.quantity for one participant inside a game, writes the changes to the PenaltyRecordEntity database object
# also the total_fine the participant has to pay is updated inside the database
def update_quantity():
    if request.method != 'POST':
        abort(405)
    data = request.json
    penalty_id = data.get("penaltyId")
    participant_id = data.get("participantId")
    action = data.get("action")
    game_id = data.get("game_id")
    # Validate input data
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
    logger.debug("Quantity Update from user {}, retrieved penalty_id: {}, participant_id: {},action: {} and game_id {}".format(current_user.email,penalty_id,participant_id,action,game_id))
    # take the PenaltyRecord from the database belonging to the participant for this exact penalty
    target_PenaltyRecordEntity = PenaltyRecordEntity.query.filter_by(game_id=game_id, penalty_id=penalty_id, participant_id=participant_id).first()
    total_fine = TotalFineEntity.query.filter_by(game_id=game_id, participant_id=participant_id).first()
    # Update the quantity inside the Database depending on the chosen action in the frontend. Make sure the quantity is not negative
    if target_PenaltyRecordEntity.penalty.invert:
        total_fine_entities = TotalFineEntity.query.filter_by(game_id=game_id).all()
        # remove FineEntity of quantity_update issuer, only the other should be updated
        total_fine_entities = [entity for entity in total_fine_entities if entity.participant_id != int(participant_id)]
        update_inverted_quantity(target_PenaltyRecordEntity,total_fine_entities, action)
        db.session.add(target_PenaltyRecordEntity)
        db.session.commit()
        return redirect(url_for('views.view_game', game_id = game_id))
    if update_quantity_and_total_fine(target_PenaltyRecordEntity, total_fine, action):
        logger.debug("Gesamtbetrag fuer {} auf {} geaendert".format(current_user.email,total_fine.get_total_pay_amount()))
        # commit all to database
        db.session.add(target_PenaltyRecordEntity)
        db.session.add(total_fine)
        db.session.commit()
    return redirect(url_for('views.view_game', game_id = game_id))

# Sets the TotalFineEntity payamount of a participant by adding up all quantities * the penalty pay amount of all penalties
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


# Generate some initial penelties on user creation for better experience 
# called on user creation in auth.py
def initial_object_generation(user_id,username):
    db.session.add(PenaltyEntity(pay_amount=0.40,title="Rinne",user_id=user_id))
    db.session.add(PenaltyEntity(pay_amount=1.00,title="Klingel",user_id=user_id))
    db.session.add(PenaltyEntity(pay_amount=1.00,title="Ochsengasse",user_id=user_id))
    db.session.add(ParticipantEntity(username=username,user_id=user_id,status=ParticipantStatus.active))
    db.session.commit()