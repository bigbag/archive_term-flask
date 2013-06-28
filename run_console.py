from flask.ext.script import Manager
from api import app
from api.console.report import Report
from api.console.mail import Mail

manager = Manager(app)

manager.add_command('report', Report())
manager.add_command('mail', Mail())
manager.run()
