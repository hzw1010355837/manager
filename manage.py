from flask_script import Manager
from flask_session import Session
from flask_migrate import Migrate, MigrateCommand
from info import app, db

Session(app)
# 6migrate数据库迁移
migrate = Migrate(app, db)
manage = Manager(app)
manage.add_command("db", MigrateCommand)


@app.route("/")
def index():
    return "Hello World!"


if __name__ == '__main__':
    manage.run()
