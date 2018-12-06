from datetime import datetime, timedelta
from flask import request, render_template, jsonify, current_app, redirect, url_for, session, abort
import time
from info import constants, db
from info.models import User, News, Category
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import admin_bp


# 登陆
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            return redirect(url_for("admin.admin_index"))
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
        # 保存管理员身份
        session["is_admin"] = True
        return redirect(url_for("admin.admin_index"))


# 首页
@admin_bp.route("/index", methods=['POST', "GET"])
def admin_index():
    return render_template("admin/index.html")


# 用户统计
@admin_bp.route("/user_count")
def user_count():
    """返回用户统计信息"""
    # 查询总人数
    total_count = 0
    try:
        # 统计普通用户总人数
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    try:
        """
        time.struct_time(tm_year=2018, tm_mon=12, tm_mday=4, tm_hour=16, tm_min=30, tm_sec=23, tm_wday=1, tm_yday=338, tm_isdst=0)

        当前月的第一天：2018-12-01
        下一个月第一天：2019-01-01
        下下一个月第一天：2019-02-01

        """
        now = time.localtime()
        # 每一个月的第一天:字符串数据
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        #  strptime:字符串时间转换成时间格式
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        # 本月新增人数：用户的创建时间 >= 本月第一天   01--->04表示本月新增人数
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    try:
        """
        2018-12-04-00:00 ---> 2018-12-04-23:59
        2018-12-05-00:00 ---> 2018-12-05-23:59
        """
        # 一天的开始时间
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        # 本日新增人数：查询条件是：用户创建时间 > 今天的开始时间，表示今天新增人数
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图表信息
    # 获取到当天2018-12-04-00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    """
    开始时间: 2018-12-04-00:00:00 - 0天
    结束时间：2018-12-04-24:00:00 = 开始时间 + 1天

    开始时间: 2018-12-04-00:00:00 - 1天  代表12-03
    结束时间：2018-12-03-24:00:00 = 开始时间 + 1天

    开始时间: 2018-12-04-00:00:00 - 2天  代表12-02
    结束时间：2018-12-02-24:00:00 = 开始时间 + 1天

    """
    # 依次添加数据，再反转
    for i in range(0, 31):  # 0 1 2.... 30
        # 获取一天的开始时间
        begin_date = now_date - timedelta(days=i)
        # 结束时间：2018-12-04-24:00:00 = 开始时间 + 1天
        end_date = begin_date + timedelta(days=1)
        # 添加每一天的时间到列表中
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            # 用户最后一次登录时间 > 一天的开始时间
            # 用户最后一次登录时间 < 一天的结束时间
            # 一天内的活跃量
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        # 将每一天的活跃量添加到列表
        active_count.append(count)

    # [12-04, 12-03.....]  --> [11-04, 11-05.....12-04]
    # 日期和数据反转
    active_date.reverse()
    active_count.reverse()

    data = {"total_count": total_count, "mon_count": mon_count, "day_count": day_count, "active_date": active_date,
            "active_count": active_count}

    return render_template('admin/user_count.html', data=data)


# 用户列表
@admin_bp.route("/user_list")
def user_list():
    # 1,获取参数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 2,校验参数
    user_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(p,
                                                                                                       constants.ADMIN_USER_PAGE_MAX_COUNT,
                                                                                                       False)
        user_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 3,逻辑处理
    user_dict_list = []
    for user in user_list:
        user_dict_list.append(user.to_admin_dict())
    data = {
        "users": user_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    # 4,返回值
    return render_template("admin/user_list.html", data=data)


# 新闻管理
@admin_bp.route("/news_review")
def news_review():
    p = request.args.get("p", 1)
    keywords = request.args.get("keywords")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    news_obj_list = []
    current_page = 1
    total_page = 1
    if keywords:
        try:
            filter_list = [News.title.contains(keywords)]
            paginate = News.query.filter(*filter_list).paginate(p, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
            news_obj_list = paginate.items
            current_page = paginate.page
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
        news_dict_list = []
        for news in news_obj_list:
            news_dict_list.append(news.to_review_dict())
        data = {
            "news_list": news_dict_list,
            "current_page": current_page,
            "total_page": total_page
        }
        return render_template("admin/news_review.html", data=data)
    else:
        try:
            paginate = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(p,
                                                                                                      constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                                      False)

            news_obj_list = paginate.items
            current_page = paginate.page
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
        news_dict_list = []
        for news in news_obj_list:
            news_dict_list.append(news.to_review_dict())
        data = {
            "news_list": news_dict_list,
            "current_page": current_page,
            "total_page": total_page
        }

        return render_template("admin/news_review.html", data=data)


# 新闻详情
@admin_bp.route("/news_review_detail", methods=["POST", "GET"])
def news_review_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        news = None
        try:
            # news = News.query.filter(News.id == news_id).first()
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        news_dict = None
        if news:
            news_dict = news.to_dict()
        data = {
            "news": news_dict
        }
        return render_template("admin/news_review_detail.html", data=data)
    else:
        param = request.json
        action = param.get("action")
        news_id = param.get("news_id")
        news = []
        # 2.1 非空判断
        if not all([news_id, action]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
        # 2.2 action in ["accept", "reject"]
        if action not in ["accept", "reject"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            current_app.logger.error("新闻对象不存在")
            abort(404)
        if action == "reject":
            reason = param.get("reason")
            news.reason = reason
            news.status = -1
        else:
            news.status = 0
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="提交错误")
        return jsonify(errno=RET.OK, errmsg="OK")


# 新闻版式
@admin_bp.route("/news_edit")
def news_edit():
    p = request.args.get("p", 1)
    keywords = request.args.get("keywords")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1
    news_list = None
    filter_list = []
    current_page = 1
    total_page = 1
    if keywords:
        filter_list.append(News.title.contains(keywords))
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p,
                                                                                              constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                              False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not news_list:
        abort(404)
    news_dict = []
    for news in news_list:
        news_dict.append(news.to_basic_dict())
    data = {
        "news_list": news_dict,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("admin/news_edit.html", data=data)


@admin_bp.route("/news_edit_detail", methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        if not news_id:
            current_app.logger.error("参数错误")
            abort(404)
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询错误")
        categories_dict = []
        for category in categories if categories else []:
            categories_dict.append(category.to_dict())
        categories_dict.pop(0)
        data = {
            "news": news.to_dict(),
            "categories": categories_dict
        }

        return render_template("admin/news_edit_detail.html", data=data)

    # 因为前段使用ajaxSubmit所有数据是form表单提交的
    param_dict = request.form
    #  1.1 news_id:新闻id， title：新闻标题，category_id:新闻分类id
    #  digest:新闻摘要，index_image:新闻主图片（非必传），content：新闻内容
    news_id = param_dict.get("news_id")
    title = param_dict.get("title")
    category_id = param_dict.get("category_id")
    digest = param_dict.get("digest")
    content = param_dict.get("content")
    index_image_url = request.files.get("index_image_url")

    if not all([news_id, title, digest, content, category_id]):
        return jsonify(errno=RET.NODATA, errmsg="参数不足")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="查询错误")
    if not news:
        abort(404)
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id
    if index_image_url:
        pic_name = captcha(index_image_url.read())
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + pic_name
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据库异常")
    return jsonify(errno=RET.OK, errmsg="OK")
