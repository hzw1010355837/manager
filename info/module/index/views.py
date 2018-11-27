from . import index_bp
from info import redis_store

"""
ImportError: cannot import name 'redis_store'出现循环导入
"""


# 2 使用蓝图对象
@index_bp.route("/")
def index():
    redis_store.set("name","zhangsan")
    return "Hello World!"
