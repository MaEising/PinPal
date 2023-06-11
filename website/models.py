from . import db
from enum import Enum
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime
import json
import random
import os, os.path
from .logger_config import setup_logger

logger = setup_logger()

# There is a convention in flask sqlalchemy to convert CamelCase tablenames to camel_case
# when creating a foreign key to reference the table name use the camel_case as reference

class UserEntity(db.Model, UserMixin): # User object inherits database (all classes should ) and UserMixin model (only user class)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    games = db.relationship("GameEntity", backref="UserEntity")

class GameStatus(Enum):
    active = "active"
    save = "save"
    finish = "finish"
    error = "error"
    broken = "broken"

# This Class is used to deactivate a participant in case a user wants to delete it
# we can't just drop the participant from the database because games with this participant will not load anymore  
class ParticipantStatus(Enum):
    active = "active"
    inactive = "inactive"

class GameEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user_entity.id'))
    status = db.Column(SQLAlchemyEnum(GameStatus), default=GameStatus.active) # save (after hitting save button, game can be loaded up again. Has not been finished tho), active (when only updates for quantities happen), finish (when game should be finished), error (error occurs)
    game_participants = db.Column(db.String(300))

    def __init__(self, user_id, game_participants, status, date_created=None):
        self.user_id = user_id
        self.game_participants = json.dumps(game_participants)
        self.status = status
        if date_created is None:
            self.date_created = datetime.datetime.utcnow()
        else:
            self.date_created = date_created

    
class PenaltyEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pay_amount = db.Column(db.Float)
    title = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user_entity.id'))
    invert = db.Column(db.Boolean)

    def __init__(self, pay_amount, title, user_id, invert=False):
        self.pay_amount = pay_amount
        self.title = title
        self.user_id = user_id
        self.invert = invert


class ParticipantEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user_entity.id'))
    status = db.Column(SQLAlchemyEnum(ParticipantStatus), default=ParticipantStatus.active)
    avatar_index = db.Column(db.Integer)

    def __init__(self, username, user_id, status):
        self.username = username
        self.user_id = user_id
        self.status = status
        self.update_avatar_index()

    def update_avatar_index(self):
        logger.debug("Set avatar_index to {}".format(self.avatar_index))
        avatar_directory = 'website/static/images/profile_avatars'
        avatar_files = os.listdir(avatar_directory)
        num_files = len(avatar_files)
        self.avatar_index = random.randint(1, num_files)

class PenaltyRecordEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_entity.id'))
    penalty_id = db.Column(db.Integer, db.ForeignKey('penalty_entity.id'))
    penalty = db.relationship("PenaltyEntity", lazy="joined")
    date_created = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, default=0)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant_entity.id'))
    participant = db.relationship("ParticipantEntity", lazy="joined")

    def __init__(self, game_id, penalty_id, participant_id, date_created=None):
        self.game_id = game_id
        self.penalty_id = penalty_id
        self.participant_id = participant_id
        if date_created is None:
            self.date_created = datetime.datetime.utcnow()
        else:
            self.date_created = date_created

class TotalFineEntity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant_entity.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game_entity.id'))
    total_pay_amount = db.Column(db.Float, default=0)

    def __init__(self, participant_id, game_id, total_pay_amount=0):
        self.participant_id = participant_id
        self.game_id = game_id
        self.total_pay_amount = total_pay_amount

    def get_total_pay_amount(self) -> float:
        return self.total_pay_amount

    def add_value(self, penalty_amount: float):
        self.total_pay_amount += penalty_amount

    def subtract_value(self, penalty_amount: float):
        self.total_pay_amount -= penalty_amount

    def reset_total_pay_amount(self):
        self.total_pay_amount = 0