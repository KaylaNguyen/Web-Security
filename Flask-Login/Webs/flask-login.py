# http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
# https://github.com/shekhargulati/flask-login-example/blob/master/flask-login-example.py
from flask import Flask, Response, request, redirect, url_for, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'some_secret'


class User(UserMixin):
    # proxy for a database of users
    user_database = {"admin": ("admin", "pass"),
               "someone": ("someone", "pass")}

    def __init__(self, username, password):
        self.id = username
        self.password = password
        # self.is_authenticated = False
        # self.is_active = False

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)

    def is_active(self):
        print "in is active"
        return True

    def is_authenticated(self):
        print "is authenticated"
        return True

    @classmethod
    def get_user_obj(cls, user_id):
        user = cls.user_database.get(user_id)
        if user:
            print user
            return User(user[0], user[1])
        return None


@login_manager.user_loader
def load_user(user_id):
    print "in load user"
    print User.get_user_obj(user_id)
    return User.get_user_obj(user_id)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = token.split(":")
        user_entry = User.get(username)
        if user_entry is not None:
            user = User(user_entry[0], user_entry[1])
            if user.password == password:
                return user
    return None


# anyone can access
@app.route("/", methods=["GET"])
def index():
    return Response(response="Hello World!", status=200)


# http://localhost:5000/protected/?token=someone:pass
@app.route("/protected/<name>", methods=["GET", "POST"])
@login_required
def protected(name):
    if request.method == 'POST':
        print "request.method == 'POST'"
        print request.form
        if request.form['logout'] == 'POST Logout':
            print "request.form['submit'] == 'POST Logout'"
            logout_user()
            return redirect(url_for("login"))
    return render_template('home.html', name=name)


# POST request: form automatically try to split data
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        print "post request"
        user = User.get(request.form['username'])
        if user and request.form['password'] == user[1]:
            print 'Logged in successfully.'
            current_user = User(request.form['username'], request.form['password'])
            login_user(current_user)
            return redirect(url_for("protected", name=current_user.id))
        else:
            return abort(401)
    else:
        print "get request"
        if request.args:
            user = User.get(request.args['username'])
            if user and request.args['password'] == user[1]:
                print('Logged in successfully.')
                current_user = User(request.args['username'], request.args['password'])
                login_user(current_user)
                return redirect(url_for("protected", name=current_user.id))
            else:
                return abort(401)
        return render_template('login.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)