from core import app, api, get, template
from core.routing import api_help
from models import db

@get(app.config['API_ROOT'], 'API Listing')
@template('api.html')
def api_index():
    """Returns a plain text listing of API methods, parameters, and descriptions."""
    output = ''
    for url in sorted(api_help.iterkeys()):
        output += api_help[url]

    return {'content': output}

@api('/speakers', methods=['GET'])
def speakers(method):
    """Return a list of all speakers, ordered by number of quotes."""
    c = db.cursor()
    c.execute('''SELECT speaker, COUNT(1) AS count
                 FROM utterance
                 GROUP BY speaker
                 ORDER BY count DESC
                 ''')
    result = c.fetchall()

    return [speaker.capitalize() for (speaker, count) in result if len(speaker) > 1]
