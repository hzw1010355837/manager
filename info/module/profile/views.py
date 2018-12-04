from info import db
from info.models import User
from info.utils.response_code import RET
from . import profile_bp
from info.utils.common import user_login_data
from flask import render_template, g, current_app, jsonify, request, redirect, url_for, session


# 用户中心首页
@profile_bp.route("/user_info")
@user_login_data
def user_info():
    user = g.user
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("profile/user.html", data=data)


# 基本资料
@profile_bp.route("/base_info", methods=["POST", "GET"])
@user_login_data
def base_info():
    # 1,获取参数 user,
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if request.method == "GET":
        data = {
            "user_info": user.to_dict()
        }
        return render_template("profile/user_base_info.html", data=data)
    # 2,校验参数
    else:
        # POST 请求, 接收参数"signature": signature,"nick_name": nick_name,"gender": gender
        param = request.json
        signature = param.get("signature")
        nick_name = param.get("nick_name")
        gender = param.get("gender")
        if not all([signature, nick_name, gender]):
            current_app.logger.error("参数错误")
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        if gender not in ["MAN", "WOMAN"]:
            current_app.logger.error("性别错误")
            return jsonify(errno=RET.PARAMERR, errmsg="性别错误")
        user_list = User.query.filter(User.nick_name == nick_name).all()
        # 3,逻辑处理
        if user_list:
            return jsonify(errno=RET.DATAEXIST, errmsg="用户昵称已经存在")
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        # 由于修改了nick_name,需要重新修改redis中保存的
        session["nick_name"] = nick_name
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
        # 4,返回值
        return jsonify(errno=RET.OK, errmsg="修改成功")


# 头像
@profile_bp.route("/user_pic_info", methods=["GET", "POST"])
@user_login_data
def user_pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("profile/user_pic_info.html")
