from flask import abort
from jinja2.filters import do_capitalize

from core import app, context, get, template

from models import Quote, Passage

@get('/', 'Seinfeld Quote')
@template('index.html')
def index():
    passage = Passage(uid=37592)
    return {
        'passage': passage,
    }

@get('/about', 'About')
@template('about.html')
def about():
    return {}

@get('/search', 'Search Quotes')
@template('search.html')
def search():
    return {}

@get('/quote/<int:uid>', 'Passage')
@template('quote.html')
def quote(uid):
    try:
        return {
            'passage': Passage(uid),
        }
    except (KeyError, ValueError) as e:
        abort(404)

@get('/random')
@get('/random/<subject>')
@get('/random/subject/<subject>')
@get('/random/speaker/<speaker>')
@get('/random/speaker/<speaker>/<subject>')
@template('quote.html')
def random(subject=None, speaker=None):
    try:
        passage = Passage.random(subject=subject, speaker=speaker)
        if passage is None:
            abort(404)

        return {
            'title': speaker or subject or 'Random',
            'passage': passage,
        }
    except (KeyError, ValueError) as e:
        abort(404)
