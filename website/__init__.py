from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "schmeisinger.db"


def create_app():
    app = Flask(__name__) # initialize flask
    app.config['SECRET_KEY'] = 'eih7theicieFeipap5heechaethaeT' # remove in production
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)


    from .views import views # register our blueprint
    from .auth import auth
    from .configure import configure
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth, url_prefi='/') # '/auth' > means you need to navigate /auth/<name of page>
    app.register_blueprint(configure, url_prefix='/')

    from .models import UserEntity, GameEntity, PenaltyEntity, PenaltyRecordEntity, ParticipantEntity
    create_database(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(id):
        return UserEntity.query.get(int(id)) # query.get is like query_id but looks for primary key by default so no id=id required
    
    def load_game(id):
        return GameEntity.query.get(int(id))
    return app


def create_database(app):
    # check if db exists if not create
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')