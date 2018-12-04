from flask import current_app, jsonify, render_template, session, g, request
from info import constants, db
from info.models import News, User, Category, Comment, CommentLike
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
        news_comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
        # comment_obj_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论查询错误")
    # for comment_obj in comment_obj_list:

    # ----------------是否点赞验证 ------------------------
    if user:
        # ----------------6.查询当前登录用户具体对那几条评论点过赞 ------------------------
        # 1. 查询出当前新闻的所有评论，取得所有评论的id —>  list[1,2,3,4,5,6]
        # news_comment_list：评论对象列表
        comment_id_list = [comment.id for comment in news_comment_list]

        # 2. 再通过评论点赞模型(CommentLike)查询当前用户点赞了那几条评论  —>[模型1,模型2...]
        try:
            commentlike_obj_list = CommentLike.query.filter(CommentLike.comment_id.in_(comment_id_list),
                                                            CommentLike.user_id == user.id
                                                            ).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
        # 3. 遍历上一步的评论点赞模型列表，获取所以点赞过的评论id（comment_like.comment_id）
        commentlike_id_list = [commentlike_obj.comment_id for commentlike_obj in commentlike_obj_list]

        # 对象列表转字典列表
    comment_dict_list = []
    for comment_obj in news_comment_list if news_comment_list else []:
        # 评论对象转字典
        comment_dict = comment_obj.to_dict()
        comment_dict["is_like"] = False
        # 遍历每一个评论对象获取其id对比看是否在评论点赞列表中
        # comment_obj1.id == 1 ==> in [1,3,5] ==> is_like=True
        # comment_obj2.id == 2 ==> in [1,3,5] ==> is_like=False
        # comment_obj3.id == 3 ==> in [1,3,5] ==> is_like=True
        if comment_obj.id in commentlike_id_list:
            comment_dict["is_like"] = True
        comment_dict_list.append(comment_dict)

    # 首页数据字典
    data = {
        "user_info": user.to_dict() if user else None,
        "news_rank_list": news_dict_list,
        "news": news_dict,
        "is_collected": is_collected,
        "comments": comment_dict_list
    }
    return render_template("news/detail.html", data=data)
    # if user:
    #     # 1获取评论id
    #     comment_id_list = [comment.id for comment in comment_obj_list]
    #     try:
    #         commentlike_obj_list = CommentLike.query.filter(CommentLike.user_id.in_(comment_id_list),
    #                                                         CommentLike.user_id == user.id).all()
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(errno=RET.DBERR, errmsg="查询错误")
    #     # 评论id列表
    #     commentlike_id_list = [commentlike_obj.comment_id for commentlike_obj in commentlike_obj_list]
    #
    # commentlike_dict_list = []
    # for commentlike_obj in comment_obj_list if comment_obj_list else []:
    #     comment_dict = commentlike_obj.to_dict()
    #     comment_dict["is_like"] = False
    #     if commentlike_obj.id in commentlike_id_list:
    #         comment_dict["is_like"] = True
    #     comment_dict_list.append(comment_dict)
    #
    # data = {
    #     "user_info": user.to_dict() if user else None,
    #     "news_rank_list": news_rank_list,
    #     "news": news_dict,
    #     "is_collected": is_collected,
    #     "comments": comment_dict_list,
    #     # "comment_like_list": commentlike_dict_list
    # }
    # return render_template("news/detail.html", data=data)


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


@news_detail_bp.route("/comment_like", methods=["POST"])
@user_login_data
def set_comment_like():
    # 1,获取参数   comment_id, (news_id, user)分析错误, action(是否点赞了)
    """
    为什么不加user,这样看不到是谁点赞
    :return:
    """
    user = g.user
    if not user:
        current_app.logger.error("用户未登录")
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    param = request.json
    comment_id = param.get("comment_id")
    action = param.get("action")
    # 2,校验参数
    if not all([comment_id, action]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.NODATA, errmsg="参数不足")
    if action not in ["add", "remove"]:
        current_app.logger.error("参数错误")
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3,逻辑处理
    try:
        # comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id).first()
        # comment = Comment.query.filter(comment_id).first()
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    try:
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                CommentLike.user_id == user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if action == "add":
        if not comment_like:
            comment_like_obj = CommentLike()
            comment_like_obj.user_id = user.id
            comment_like_obj.comment_id = comment_id
            comment.like_count += 1
            db.session.add(comment_like_obj)
    else:
        if comment_like:
            db.session.delete(comment_like)
            comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")

    # 4,返回值
    return jsonify(errno=RET.OK, errmsg="点赞功能完成")
