from flask import Flask
from terminal.terminal import terminal

app = Flask(__name__)
app.register_blueprint(terminal)
app.config.from_object('config.ProductionConfig')
# Blueprint can be registered many times
#app.register_blueprint(terminal, url_prefix='/pages') 


if __name__ == '__main__':
    app.run(debug=True)