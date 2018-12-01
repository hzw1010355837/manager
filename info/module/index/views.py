from info import constants
from info.models import User, News, Category
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
        "user_info": user.to_dict() if user else None,
        "news_rank_list": news_dict_list,
        "categories": categories_dict_list
    }

    return render_template("news/index.html", data=data)


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
