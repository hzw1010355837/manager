from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import config_dict
from flask_session import Session
import logging

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 0日志
    setup_log(config_name)
    # 1创建app对象
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    # 2创建db对象
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 3创建redis_store对象
    global redis_store
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT)
    # 4csrf包含请求体都需要csrf,保护
    CSRFProtect(app)
    # 5Session将数据存放到redis中
    Session(app)

    # 3 注册蓝图
    # 注册蓝图的时候再使用,可以避免循环导入
    from info.module.index import index_bp
    app.register_blueprint(index_bp)

    return app
