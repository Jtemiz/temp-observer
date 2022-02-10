import os

from flask_script import Manager
from flask_script.commands import Clean, ShowUrls

from app.factory import create_app
# default to dev config because no one should use this in
# production anyway
env = os.environ.get('APPNAME_ENV', 'Base')
app = create_app('app.config.%sConfig' % env.capitalize())

manager = Manager(app)
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())

@manager.shell
def make_shell_context():
    return dict(app=app)


if __name__ == "__main__":
    manager.run()
