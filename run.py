from app import create_app, db
from app.models import user
from flask_script import Manager, Shell , Server

app = create_app()
app.debug = True

manager = Manager(app)
manager.add_command("runserver", Server('0.0.0.0',port=5000, threaded=True))

def make_shell_context():
	return dict(app = app, db = db, user = user)

manager.add_command("shell",Shell(make_context = make_shell_context))

if __name__ == '__main__':
	manager.run()

