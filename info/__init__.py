from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import config_dict
from flask_session import Session

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def create_app(config_name):
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
