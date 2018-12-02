from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_bp
# from info import redis_store
from flask import render_template, current_app, session, jsonify, request, g

# import logging

"""
ImportError: cannot import name 'redis_store'出现循环导入
"""


# 2 使用蓝图对象
@index_bp.route("/")
@user_login_data
def index():
    # redis_store.set("name", "zhangsan")
    # current_app.logger.debug("debug")

    # logging.debug(current_app.url_map)
    # 添加模板

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

    data = {
        "user_info": user.to_dict() if user else None,
        "news_rank_list": news_dict_list
    }

    return render_template("news/index.html", data=data)


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_bp.route("/news_list")
def news_list():
    params = request.args
    cid = params.get("cid")
    page = params.get("page", 1)
    per_page = params.get("per_page", 10)
    if not cid:
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.NODATA, errmsg="参数不足")
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    filter_list = []
    if cid != 1:
        filter_list.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(page, per_page, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    # 新闻对象列表转新闻字典列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_dict())
    data = {
        "newsList": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return jsonify(errno=RET.OK, errmsg="新闻查询成功", data=data)
