from flask import current_app, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models
from info.models import User

# 1 创建app对象

app = create_app("development")
# 6migrate数据库迁移
manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command("db", MigrateCommand)
"""
@option('-n', '--name', dest='name')
@option('-u', '--url', dest='url')
def hello(name, url):
    print "hello", name, url
"""


@manage.option('-n', '--name', dest='name')
@manage.option('-p', '--password', dest='password')
def createsuperuser(name, password):
    if not all([name, password]):
        return "参数不足"
    user = User()
    user.nick_name = name
    user.mobile = name
    user.is_admin = True
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return "保存用户管理员失败"
    return "创建管理员成功"


if __name__ == '__main__':
    manage.run()
