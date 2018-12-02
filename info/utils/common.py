from flask import session, current_app, jsonify, g
from info.utils.response_code import RET
import functools


def set_rank_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


def user_login_data(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        # -----------------查询用户对象------------------
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="查询错误")
        g.user = user
        return view_func(*args, **kwargs)

    return wrapper
