# Copyright 2014 John Reese
# Licensed under the MIT license

from flask import abort
from jinja2.filters import do_capitalize

from core import app, context, get, template

from models import Quote, Passage

@get('/', 'Seinfeld Quote')
@template('index.html')
def index():
    #passage = Passage(uid=37592)
    passage = Passage(34663)
    return {
        'passage': passage,
    }

@get('/about', 'About')
@template('about.html')
def about():
    return {}

@get('/search', 'Search Quotes')
@template('search.html')
def search(subject=None, speaker=None):
    return {
        'speaker': speaker,
        'subject': subject,
    }

@get('/quote/<int:uid>', 'Passage')
@template('quote.html')
def quote(uid):
    try:
        return {
            'passage': Passage(uid),
        }
    except (KeyError, ValueError) as e:
        abort(404)

@get('/random', cache=False)
@get('/random/<subject>', cache=False)
@get('/random/subject/<subject>', cache=False)
@get('/random/speaker/<speaker>', cache=False)
@get('/random/speaker/<speaker>/<subject>', cache=False)
@template('random.html')
def random(subject=None, speaker=None):
    passage = Passage.random(subject=subject, speaker=speaker)

    return {
        'title': speaker or subject or 'Random',
        'passage': passage,
        'speaker': speaker,
        'subject': subject,
    }
