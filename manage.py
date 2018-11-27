from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 1 创建app对象
app = create_app("development")
# 6migrate数据库迁移
manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manage.run()
