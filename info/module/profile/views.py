from info.utils.response_code import RET
from . import profile_bp
from info.utils.common import user_login_data
from flask import render_template, g, current_app, jsonify


@profile_bp.route("/user_info")
@user_login_data
def user_info():
    # 1,获取参数 user,
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 2,校验参数

    # 3,逻辑处理
    # 4,返回值
    data = {
        "user_info": user.to_dict()
    }
    return render_template("news/user.html", data=data)
