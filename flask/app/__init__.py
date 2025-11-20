from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from app.config import Config

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.auth import auth_bp
    from app.main import main_bp
    from app.prediction import prediction_bp
    from app.history import history_bp
    from app.gamification import gamification_bp
    from app.chatbot import chatbot_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(prediction_bp, url_prefix='/prediction')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(gamification_bp, url_prefix='/gamification')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    
    with app.app_context():
        db.create_all()
    
    return app
