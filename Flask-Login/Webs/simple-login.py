from flask import Flask, render_template, flash
from flask import redirect, url_for, request

app = Flask(__name__)


@app.route('/home/<name>', methods=["GET", "POST"])
# @app.route('/home/')
def home(name=None):
    if request.method == 'POST':
        print "request.method == 'POST'"
        print request.form
        if request.form['logout'] == 'POST Logout':
            print "request.form['submit'] == 'POST Logout'"
            return redirect(url_for("login"))
    return render_template('home.html', name=name)


# route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    print "in login"
    error = None
    if request.method == 'POST':
        print "in post"
        if request.form['username'] != 'admin' or request.form['password'] != 'pass':
            print "invalid"
            error = 'Invalid Credentials. Please try again.'
        else:
            print "Rendering home"
            return redirect(url_for("home", name=request.form['username']))
    # http://127.0.0.1:5000/login?username=admin&password=admin&get_button=GET+Login
    if request.method == 'GET':
        print "in get"
        if request.args:
            if request.args['username'] != 'admin' or request.args['password'] != 'pass':
                print "invalid"
                error = 'Invalid Credentials. Please try again.'
            else:
                print "Rendering home"
                return redirect(url_for("home", name=request.args['username']))
                # return render_template('home.html', name=request.args['username'])
    print "Rendering login"
    return render_template('login.html', error=error)
