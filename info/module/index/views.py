from . import index_bp
# from info import redis_store
from flask import render_template, current_app

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

    return render_template("news/index.html")


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
