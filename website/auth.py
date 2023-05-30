from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import UserEntity
from werkzeug.security import generate_password_hash, check_password_hash # store password as hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .logger_config import setup_logger
from .configure import initial_object_generation
auth = Blueprint('auth', __name__)


logger = setup_logger()
@auth.route('/logout')
@login_required
def logout():
    logger.info("User {} logout".format(current_user.email))
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = UserEntity.query.filter_by(email=email).first()
        if user:
            flash('User with this email already exists', category='error')
        elif len(email) < 4:
            flash('E-Mail is invalid', category='error')
        elif len(first_name) < 2:
            flash('firstName needs more than two characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be atleast 7 characters', category='error')
        else:
            # add user to database
            user = UserEntity(email=email,first_name=first_name,password=generate_password_hash(password1, method='sha256'))
            db.session.add(user)
            db.session.commit()
            initial_object_generation(user.id,user.first_name)
            logger.info("Create initial Penalties for User {}".format(email))
            logger.info("User {} registered".format(email))
            flash('Account created', category='success')
            login_user(user, remember=True)
            logger.info("User {} login".format(email))
            return redirect(url_for('views.home'))
    return render_template("signup.html", user=current_user)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = UserEntity.query.filter_by(email=email).first() # return first result with this email
        if user: # if one was found
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                logger.info("User {} login".format(current_user.email))
                return redirect(url_for('views.home'))
            else:
                flash('incorrect password, try again.',category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)