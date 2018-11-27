from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import app, db


# 6migrate数据库迁移
manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command("db", MigrateCommand)


@app.route("/")
def index():
    return "Hello World!"


if __name__ == '__main__':
    manage.run()
