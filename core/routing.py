from functools import wraps
import inspect
import json

from flask import abort, make_response, render_template, request

from core import app, encoder

_context = []
_titles = {}

class context(object):
    """Prefix all routing and template paths with the given base URL for any view methods defined during the scope of this context.
    This can also be nested, and all contexts will be concatenated in the order they were entered.
    Usage example:

        with context('/foo'):
            @get('')
            def index():
                pass

            @get('/bar')
            def bar():
                pass

    This creates two routing endpoints: one that routes /foo to index(), and one that routes /foo/bar to bar()."""
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        _context.insert(0, self.url)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _context.pop(0)

def get(url, title=None, cache=True, cache_time=300):
    """Route the given URL for GET methods."""
    def decorator(f):
        full_url = _fullpath(url)
        if title is not None:
            _titles[full_url] = title

        @app.route(full_url, methods=['GET'])
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for key in request.args:
                if key not in kwargs:
                    kwargs[key] = request.args[key]
            rv = f(*args, **kwargs)

            if isinstance(rv, app.response_class):
                if cache:
                    rv.headers.add('Cache-Control',
                                   'public, max-age={}'.format(cache_time))
                else:
                    rv.headers.add('Cache-Control', 'no-store')

            return rv

        return decorated_function

    return decorator

def post(url):
    """Route the given URL for POST methods."""
    return app.route(_fullpath(url), methods=['POST'])


api_help = {}

def api(api_url, methods=['GET', 'POST', 'PUT'], format='application/json', split_payload=False):
    """Route the given API url over multiple HTTP methods, automatically converting between JSON and objects."""
    full_url = app.config['API_ROOT'] + _fullpath(api_url)
    def decorator(f):
        # Build API listing for any method with a docstring
        str_methods = ', '.join(sorted(methods))
        args, varargs, keywords, defaults = inspect.getargspec(f)
        args = args[1:]
        if defaults is not None:
            defaults = list(defaults)
            m = len(args)
            n = len(defaults)
            args[m-n:m] = ["{0}={1}".format(a,d) for a,d in zip(args[m-n:], defaults)]

        args = ', '.join(args)
        str_methods = ', '.join(methods)

        if f.__doc__ is None:
            docs = '    No documentation exists for this method.'
        else:
            docs = '\n'.join(['    ' + line for line in [line.strip() for line in f.__doc__.split('\n')]])

        api_help[full_url] = "{0} ({1}) {2}\n{3}\n\n".format(full_url, args, str_methods, docs)

        @app.route(full_url, methods=methods)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            objects = kwargs

            for key in request.args:
                try:
                    objects[key] = json.loads(request.args[key])
                except ValueError:
                    objects[key] = request.args[key]

            if request.method == 'GET' or request.method == 'DELETE':
                pass

            elif request.method == 'POST' or request.method == 'PUT':
                if request.content_type == 'application/json':
                    payload = json.loads(request.data)

                elif request.content_type == 'application/x-www-form-urlencoded':
                    payload = {}
                    for key in request.form:
                        payload[key] = request.form[key]

                else:
                    abort(400)

                if split_payload and type(payload) == dict:
                    objects.update(payload)
                else:
                    objects['payload'] = payload

            result = f(request.method, *args, **objects)

            if format == 'application/json':
                output = encoder.dump(result)
            else:
                output = result

            response = make_response(output)
            response.mimetype = format
            return response

        return decorated_function
    return decorator

def _fullpath(url):
    """Generate the full URL path using the currently active path contexts."""
    rv = ''.join(_context[-1::-1]) + url
    return rv

