from flask import Blueprint

profile_bp = Blueprint("user", __name__, url_prefix="/user")

from .views import *