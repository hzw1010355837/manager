from info import db, constants
from info.models import User, News, Category
from info.utils.pic_storage import pic_storage
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
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else []
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
        if not user:
            current_app.logger.error("用户未登录")
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
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
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("profile/user_pic_info.html", data=data)
    else:
        # 1,获取参数
        file_data = request.files.get("avatar").read()
        # 2,校验参数
        if not all([user, file_data]):
            current_app.logger.error("参数不足")
            return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
        try:
            pic_name = pic_storage(file_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="七牛云错误")
        # 3,逻辑处理
        user.avatar_url = pic_name
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
        data = {
            "user_info": user.to_dict(),
            "avatar_url": constants.QINIU_DOMIN_PREFIX + pic_name
        }
        # 4,返回值
        return jsonify(errno=RET.OK, errmsg="上传头像成功", data=data)


# 密码修改
@profile_bp.route("/pass_info", methods=["GET", "POST"])
@user_login_data
def pass_info():
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("profile/user_pass_info.html", data=data)
    else:
        param = request.json
        old_password = param.get("old_password")
        new_password = param.get("new_password")
        if not all([old_password, new_password, user]):
            current_app.logger.error("参数不足")
            return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
        if not user.check_password(old_password):
            current_app.logger.error("密码错误")
            return jsonify(errno=RET.PWDERR, errmsg="密码错误")
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
        return jsonify(errno=RET.OK, errmsg="修改密码成功")


# 收藏
@profile_bp.route("/user_collection")
@user_login_data
def user_collection():
    user = g.user
    p = request.args.get("p", 1)
    # 后面需要
    news_collect_list = []
    current_page = 1
    total_page = 1
    # 必须先将p转成int类型
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if user:
        try:
            paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
            news_collect_list = paginate.items
            current_page = paginate.page
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
    news_dict_list = []
    for news in news_collect_list if news_collect_list else []:
        news_dict_list.append(news.to_review_dict())
    data = {
        # "user_info": user.to_dict(),
        "collections": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("profile/user_collection.html", data=data)


# 发布新闻
@profile_bp.route("/user_news_release", methods=["GET", "POST"])
@user_login_data
def user_news_release():
    user = g.user
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
        category_dict_list = []
        for category in categories if categories else []:
            category_dict_list.append(category.to_dict())
        category_dict_list.pop(0)

        data = {
            # "user_info": user.to_dict() if user else None,
            "categories": category_dict_list
        }
        return render_template("profile/user_news_release.html", data=data)
    else:
        param = request.form
        index_image = request.files.get("index_image")
        title = param.get("title")
        cid = param.get("category_id")
        digest = param.get("digest")
        content = param.get("content")
        source = "个人发布"
        if not all([user, title, cid, digest, content, index_image]):
            current_app.logger.error("参数错误")
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        index_data = index_image.read()
        try:
            index_name = pic_storage(index_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")

        news = News()
        news.user_id = user.id
        news.title = title
        news.source = source
        news.content = content
        news.digest = digest
        news.category_id = cid
        news.status = 1
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + index_name
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")

        return jsonify(errno=RET.OK, errmsg="发布成功")


# 新闻列表
@profile_bp.route("/user_news_list")
@user_login_data
def user_news_list():
    user = g.user
    p = request.args.get("p", 1)
    # p 必须转整型
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="页数错误")
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    try:
        # 查询当前用户的文章
        paginate = News.query.filter(News.status != 0, News.user_id == user.id).paginate(p,
                                                                                         constants.USER_COLLECTION_MAX_NEWS,
                                                                                         False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    news_obj_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_list = []
    for news in news_obj_list if news_obj_list else []:
        news_dict_list.append(news.to_review_dict())
    data = {
        "user_info": user.to_dict(),
        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("profile/user_news_list.html", data=data)
