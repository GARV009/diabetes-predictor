from flask import Blueprint

prediction_bp = Blueprint('prediction', __name__)

from app.prediction import routes
