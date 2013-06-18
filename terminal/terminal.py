from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

terminal = Blueprint('terminal', __name__,
                        template_folder='templates')

@terminal.route('/', defaults={'page': 'index'})
@terminal.route('/<page>')
def show(page):
    try:
        return render_template('pages/%s.html' % page)
    except TemplateNotFound:
        abort(404)
