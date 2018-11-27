from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate, MigrateCommand
from config import Config
from redis import StrictRedis

# 1创建app对象
app = Flask(__name__)
app.config.from_object(Config)
# 2创建db对象
db = SQLAlchemy(app)
# 3创建redis_store对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
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
