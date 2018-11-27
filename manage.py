from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate, MigrateCommand
import redis


class Config(object):
    SECRET_KEY = "1238sadfhaksdhf"

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:1234@127.0.0.1:3306/manage_demo"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


# 1创建app对象
app = Flask(__name__)
app.config.from_object(Config)
# 2创建db对象
db = SQLAlchemy(app)
# 3创建redis_store对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
manage = Manager(app)
# 4csrf包含请求体都需要csrf
CSRFProtect(app)
# 5Session将数据存放到redis中
Session(app)
# 6migrate数据库迁移
migrate = Migrate(app, db)

manage.add_command("db", MigrateCommand)


@app.route("/")
def index():
    return "Hello World!"


if __name__ == '__main__':
    manage.run()
