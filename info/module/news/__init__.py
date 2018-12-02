from flask import Blueprint

news_detail_bp = Blueprint("new_detail_bp", __name__, url_prefix="/news")

from .views import *