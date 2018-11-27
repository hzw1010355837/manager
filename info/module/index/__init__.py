from flask import Blueprint
# 1创建蓝图对象
index_bp = Blueprint("index", __name__)

from . import views
