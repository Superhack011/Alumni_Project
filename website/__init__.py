from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'No_Secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.instance_path, DB_NAME)}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True


    with app.app_context(): ###Insure that path exists
        if not path.exists(app.instance_path): 
            path.makedirs(app.instance_path)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    from .models import User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    from .auth import auth
    from .features import features

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(features, url_prefix='/')

    return app

def create_database(app):
    db_path = path.join(app.instance_path, DB_NAME)
    print(f"Checking for database at: {db_path}")

    if not path.exists(db_path):
        with app.app_context():
            db.create_all()  # Create tables based on the models
        print("DATABASE CREATED SUCCESSFULLY!")
    else:
        print("DATABASE ALREADY EXISTS!")
