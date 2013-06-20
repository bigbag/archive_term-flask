from flask import Flask
from api import app

app.config.from_object('api.config.ProductionConfig')

app.run()
