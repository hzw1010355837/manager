from flask import current_app, jsonify, render_template, session, g

from info import constants
from info.models import News, User, Category
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
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询分类数据异常")

    # 分类对象列表转换成字典列表
    categories_dict_list = []
    for category in categories if categories else []:
        # 分类对象转出成字典
        category_dict = category.to_dict()
        categories_dict_list.append(category_dict)
    data = {
        "user_info": user,
        "news_rank_list": news_rank_list,
        "categories_dict_list": categories_dict_list
    }
    return render_template("news/detail.html", data=data)
