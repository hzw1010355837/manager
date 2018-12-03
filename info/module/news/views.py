from flask import current_app, jsonify, render_template, session, g, request
from info import constants, db
from info.models import News, User, Category, Comment
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_detail_bp


@news_detail_bp.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    # # 1获取参数
    # try:
    #     news = News.query.filter(News.id == news_id).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="查询错误")
    # # 2校验参数
    # if not news:
    #     current_app.logger.error("没有参数")
    #     return jsonify(errno=RET.NODATA, errmsg="没有参数")
    # # 3逻辑处理
    # # 4返回值

    # -----------------查询用户对象------------------
    user = g.user
    # -----------------新闻点击排行对象------------------
    try:
        news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻查询错误")
    # 将新闻对象列表转换成新闻字典列表
    news_dict_list = []
    for news_obj in news_rank_list if news_rank_list else []:
        news_dict = news_obj.to_dict()
        news_dict_list.append(news_dict)
    # ----------------查询新闻分类数据 ------------------------
    # try:
    #     categories = Category.query.all()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="查询分类数据异常")
    #
    # # 分类对象列表转换成字典列表
    # categories_dict_list = []
    # for category in categories if categories else []:
    #     # 分类对象转出成字典
    #     category_dict = category.to_dict()
    #     categories_dict_list.append(category_dict)
    # ----------------新闻内容展示 ------------------------
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    news_dict = None
    if news:
        news_dict = news.to_dict()
    # ----------------查询新闻是否收藏 ------------------------
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True
    # ----------------评论表单实现 ------------------------
    try:
        comment_obj_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论查询错误")
    comment_dict_list = []
    for comment_obj in comment_obj_list:
        comment_dict_list.append(comment_obj.to_dict())

    data = {
        "user_info": user,
        "news_rank_list": news_rank_list,
        "news": news_dict,
        "is_collected": is_collected,
        "comments": comment_dict_list
    }
    return render_template("news/detail.html", data=data)


@news_detail_bp.route("/news_collect", methods=["POST"])
@user_login_data
def get_news_collect():
    # 1,获取参数 ,user, news_id, action 收藏或取消的行为
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    param = request.json
    news_id = param.get("news_id")
    action = param.get("action")
    # 2,校验参数
    if not all([news_id, action]):
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ["collect", "cancel_collect"]:
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3,逻辑处理
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if not news:
        current_app.logger.error("新闻不存在")
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    if action == "collect":
        user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    # 4,返回值
    return jsonify(errno=RET.OK, errmsg="OK")


@news_detail_bp.route("/news_comment", methods=["POST"])
@user_login_data
def set_news_comment():
    # 1,获取参数 user, news_id, comment, parent_id
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    param = request.json
    news_id = param.get("news_id")
    comment_str = param.get("comment")
    parent_id = param.get("parent_id")
    # 2,校验参数
    if not all([news_id, comment_str]):
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3,逻辑处理
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if not news:
        current_app.logger.error("新闻不存在")
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存错误")

    # 4,返回值
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())
