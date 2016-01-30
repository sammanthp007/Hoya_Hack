# a basic hello world application in WSGI without werkzeung
'''def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ['Hello, World!']
'''
# A WSGI application is something you can call and pass an environ dict and a start_response callable. The environ contains all the incoming information. The start_response is used to determine the start of the response.

# With werkzeung, we do not need to deal directly with responses or requests.
from werkzeug.wrappers import Request, Response

def application(environ, start_response):
    request = Request(environ)
    text = 'Hello %s!' % request.args.get('name', 'World')
    response = Response(text, mimetype='text/plain')
    return response(environ, start_response)


