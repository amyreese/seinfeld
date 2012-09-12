from flask import abort

from core import app, context, get, template
from core.routing import api_help

from models import Quote, Passage

@get('/', 'Seinfeld Quote')
@template('index.html')
def index():
    return {}

@get('/about', 'About')
@template('about.html')
def about():
    return {}

@get(app.config['API_ROOT'], 'API Listing')
@template('api.html')
def api_index():
    """Returns a plain text listing of API methods, parameters, and descriptions."""
    output = ''
    for url in sorted(api_help.iterkeys()):
        output += api_help[url]

    return {'content': output}

@get('/quote/<int:uid>', 'Passage')
@template('quote.html')
def quote(uid):
    try:
        return {
            'passage': Passage(uid),
        }
    except (KeyError, ValueError) as e:
        abort(404)

@get('/random', 'Random')
@get('/random/<subject>', 'Random')
@template('quote.html')
def random(subject=None):
    try:
        passage = Passage.random(subject)
        if passage is None:
            abort(404)

        return {
            'passage': Passage.random(subject),
        }
    except (KeyError, ValueError) as e:
        abort(404)
