import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from contextlib import closing

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'blog.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"admin": ("admin", "pass"),
                     "Kayla": ("Kayla", "2001"),
                     "Phil": ("Phil", "theawesome")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

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


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    # db = get_db()
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT title, text , author FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    # TODO get logged in user
    db.execute('INSERT INTO entries (title, text, author) VALUES (?, ?, ?)',
               [request.form['title'], request.form['text'], session['current_user'][0]])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.get(request.form['username'])
        if user and request.form['password'] == user[1]:
            print 'Logged in successfully.'
            session['logged_in'] = True
            session['current_user'] = user
            print user
            flash('You were logged in')
            return redirect(url_for('show_entries'))
        else:
            error = 'Invalid user name or password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
