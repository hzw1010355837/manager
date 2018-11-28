from flask import Blueprint

# 可以跟上一个前缀
passport_bp = Blueprint("passport", __name__, url_prefix="/passport")

from .views import *
