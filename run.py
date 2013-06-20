from flask import Flask
from app import app

app.config.from_object('config.ProductionConfig')

app.run()
