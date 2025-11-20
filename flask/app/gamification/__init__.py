from flask import Blueprint

gamification_bp = Blueprint('gamification', __name__)

from app.gamification import routes
