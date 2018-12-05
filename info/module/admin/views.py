from flask import request, render_template, jsonify, current_app, redirect, url_for, session
from info.models import User
from info.utils.response_code import RET
from . import admin_bp


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        user_id = session.get("user_id")
        password = session.get("password")
        if user_id and password:
            return redirect(url_for("user.admin_index"))
        else:
            return render_template("admin/login.html")
    else:
        param = request.form
        name = param.get("username")
        password = param.get("password")
        if not all([name, password]):
            current_app.logger.error("参数错误")
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        try:
            admin_user = User.query.filter(User.mobile == name, User.is_admin == True).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.NODATA, errmsg="查询管理员异常")
        if not admin_user:
            current_app.logger.error("管理员不存在")
            return jsonify(errno=RET.NODATA, errmsg="管理员不存在")
        if not admin_user.check_password(password):
            current_app.logger.error("密码错误")
            return jsonify(errno=RET.PWDERR, errmsg="密码错误")
        # 少了一步,保存管理员登陆信息
        session["user_id"] = admin_user.id
        session["nick_name"] = name
        session["mobile"] = name
        return redirect(url_for("admin.admin_index"))


@admin_bp.route("/index")
def admin_index():
    return render_template("admin/index.html")


