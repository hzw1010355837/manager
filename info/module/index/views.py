from info.models import User
from info.utils.response_code import RET
from . import index_bp
# from info import redis_store
from flask import render_template, current_app, session, jsonify

# import logging

"""
ImportError: cannot import name 'redis_store'出现循环导入
"""


# 2 使用蓝图对象
@index_bp.route("/")
def index():
    # redis_store.set("name", "zhangsan")
    # current_app.logger.debug("debug")

    # logging.debug(current_app.url_map)
    # 添加模板

    user_id = session.get("user_id")
    user = None
    # -----------------查询用户对象------------------
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
    data = {
        "user_info": user.to_dict() if user else None,
    }

    return render_template("news/index.html", data=data)


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
