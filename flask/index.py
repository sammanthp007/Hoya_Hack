from flask import Flask, render_template 	# an instance of Flask will be used as the structure of our whole application
app = Flask(__name__)		# This signifies, in Flask, that wherever this particular module is is the root directory

# Views:
# by default, routes only answer to GET requests. We can change that by providing methods to the decorator.

@app.route('/')
def home():
	return render_template('home.html', title='Home')

@app.route('/profile/user/<username>')
def profile(username):
	return 'Hey, %s' % username

@app.route('/logout')
def logout():
	return 

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		login()
	else:
		pass
		# dont





# to build a url for a particular function, use -> url_for('home') = /
# also works for static -> url_for('static', filename='style.css') = 'static/style.css'
if __name__ == '__main__':
	# app.debug = True or
	app.run(debug=True)		#Don't enable debug in forking environment because it will allow execution of arbitary code.
