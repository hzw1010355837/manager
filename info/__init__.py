from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from config import Config
from flask_session import Session

# 1创建app对象
app = Flask(__name__)
app.config.from_object(Config)
# 2创建db对象
db = SQLAlchemy(app)
# 3创建redis_store对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 4csrf包含请求体都需要csrf
CSRFProtect(app)
# 5Session将数据存放到redis中
Session(app)