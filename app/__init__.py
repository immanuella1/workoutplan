from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import openai

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    #loading environment variables from .env file
    load_dotenv()
    
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app

#incorporated flask migrate
        
def run_migrations():
    from flask import current_app
    with current_app.app_context():
        from flask_migrate import upgrade
        upgrade()
        







