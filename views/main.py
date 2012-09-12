from core import app, context, get, template
from core.routing import api_help

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
