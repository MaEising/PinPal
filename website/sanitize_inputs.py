from flask import flash
from html import escape
import re
from .logger_config import setup_logger
from flask_login import current_user



logger = setup_logger()

class InvalidInputError(ValueError):
    pass

def sanitize_pay_amount(pay_amount):
    pay_amount2 = str(pay_amount)
    if not re.match(r'^[0-9]+(\.[0-9]{1,2})?$|^[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{1,2})?$', pay_amount2):
        flash("Invalid pay amount. Please enter a valid float like '0.25' or '0,50'.", category='error')
        raise ValueError("Invalid pay amount, the pay amount included was:", pay_amount)

def sanitize_participant_ids(participant_id_list):
    if type(participant_id_list) == list:
        for id in participant_id_list:
            sanitize_participant_id(id)
    else:
        raise InvalidInputError

def sanitize_participant_id(participant_id):
    if not re.match(r'^[0-9]+', str(participant_id)):
        raise InvalidInputError("This input provided is invalid {}".format(id))

def sanitize_string(description) -> str:
    description = escape(description).strip()
    if not description or description.isspace():
        flash("Error: Please enter a valid description.", "error")
        raise ValueError("Invalid description.")    
    if len(description) > 249 or len(description) <= 1:
        flash("Error: The description cannot be more than 250 characters or less than 1 Character.", "error")
        logger.info("Description was invalid and got blocked, Description: {}, by user: {}").format(current_user.email,description)
        raise ValueError("Invalid description.")

    # remove any characters that from these: <=":(');>
    description = re.sub(r'[<=:("\');>-]', '', description)
    
    return description