# a basic hello world application in WSGI without werkzeung
'''def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ['Hello, World!']
'''
# A WSGI application is something you can call and pass an environ dict and a start_response callable. The environ contains all the incoming information. The start_response is used to determine the start of the response.

# With werkzeung, we do not need to deal directly with responses or requests.
'''def application(environ, start_response):
    request = Request(environ)
    text = 'Hello %s!' % request.args.get('name', 'World')
    response = Response(text, mimetype='text/plain')
    return response(environ, start_response)
'''



import os
import redis
import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader


def is_valid_url(url):
	parts = urlparse.urlparse(url)
	return parts.scheme in ('http', 'https')

def base36_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))

# Now create a structure for out application. The class is an application, as it is structued.
class Shortly(object):

    def __init__(self, config):
    	self.redis = redis.Redis(config['redis_host'], config['redis_port'])
        # step 2: Include Jinja templating and pointing it to the templates directory to fetch templates from
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
    	self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                 autoescape=True)
    	# step 2: For routing -> matching and parsing the url to something we can use
    	self.url_map = Map([
					    Rule('/', endpoint='new_url'),
					    Rule('/<short_id>', endpoint='follow_short_link'),
					    Rule('/<short_id>+', endpoint='short_link_details')
					])
    def on_new_url(self, request):
    	error = None
    	url = ''
    	if request.method == 'POST':
		    url = request.form['url']
		    if not is_valid_url(url):
		        error = 'Please enter a valid URL'
		    else:
		        short_id = self.insert_url(url)
		        return redirect('/%s+' % short_id)
        return self.render_template('new_url.html', error=error, url=url)

    def insert_url(self, url):
		short_id = self.redis.get('reverse-url:' + url)
		if short_id is not None:
			return short_id
		url_num = self.redis.incr('last-url-id')
		short_id = base36_encode(url_num)
		self.redis.set('url-target:' + short_id, url)
		self.redis.set('reverse-url:' + url, short_id)
		return short_id

    def on_follow_short_link(self, request, short_id):
		link_target = self.redis.get('url-target:' + short_id)
		if link_target is None:
			raise NotFound()
		self.redis.incr('click-count:' + short_id)
		return redirect(link_target)


    def on_short_link_details(self, request, short_id):
	    link_target = self.redis.get('url-target:' + short_id)
	    if link_target is None:
	        raise NotFound()
	    click_count = int(self.redis.get('click-count:' + short_id) or 0)
	    return self.render_template('short_link_details.html',
	        link_target=link_target,
	        short_id=short_id,
	        click_count=click_count
	    )
    # step 2 : For rendering pages using given templates
    def render_template(self, template_name, **context):
	    t = self.jinja_env.get_template(template_name)
	    return Response(t.render(context), mimetype='text/html')

    def dispatch_request(self, request):
    	# Step 1: Just print hello world
        # return Response('Hello World!')
        # Step 2: map url to endpoint
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, 'on_' + endpoint)(request, **values)
		except HTTPException, e:
			return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host='localhost', redis_port=6379, with_static=True):
    app = Shortly({
        'redis_host':       redis_host,
        'redis_port':       redis_port
    })
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


# The following will start a local development server with automatic code relode and a debugger
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

# The basic idea here is that our Shortly class is an actual WSGI application. The __call__ method directly dispatches to wsgi_app. This is done so that we can wrap wsgi_app to apply middlewares like we do in the create_app function. The actual wsgi_app method then creates a Request object and calls the dispatch_request method which then has to return a Response object which is then evaluated as WSGI application again. As you can see: turtles all the way down. Both the Shortly class we create, as well as any request object in Werkzeug implements the WSGI interface. As a result of that you could even return another WSGI application from the dispatch_request method.

# Making views
