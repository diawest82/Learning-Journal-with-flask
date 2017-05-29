from flask import (Flask, g, render_template, redirect, url_for, flash, abort,
                   request)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, current_user,
                             logout_user, login_required)
import unidecode
import re

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = "l;kjdfa./m1lkjJJK#jk;kj0agm;"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.template_filter()
def slugify(title):
    """Turns a title into the slug of a url."""
    title = unidecode.unidecode(title).lower()
    return re.sub(r'\W+', '-', title)


@app.template_filter()
def split_string(string, delimter=','):
    """Split a string by the comma."""
    return string.strip().split(delimter)


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/')
def index():
    """
    If the user logs in: contains a list of journal entries, which displays
    Title, Date for Entry. Title should be hyperlinked to the detail page for
    each journal entry. Include a link to add an entry. If not: sent to
    welcome page.
    """
    try:
        if current_user in models.User.select():
            user = current_user
            stream = user.get_entry().limit(10)
            return render_template('journal.html', user=user, stream=stream)
    except models.DoesNotExist:
        pass
    else:
        return render_template('welcome.html')


@app.route('/register', methods=('POST', 'GET'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            password=form.password.data
        )
        flash("Yay, you register", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("The username or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in.", "sucess")
                return redirect(url_for('index'))
            else:
                flash("The username or password doesn't match.", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "sucess")
    return redirect(url_for('index'))


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = forms.BlogForm()
    if form.validate_on_submit():
        models.BlogEntry.create_entry(title=form.title.data,
                                      date=form.date.data,
                                      time_spent=form.time_spent.data,
                                      learned=form.learned.data,
                                      resources=form.resources.data,
                                      tags=form.tags.data,
                                      user=g.user._get_current_object(),)
        flash("New entry has been added!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/detail')
@app.route('/detail/<int:blogid>/<string:slug>')
def detail(blogid, slug):
    try:
        entry = models.BlogEntry.select().where(
            models.BlogEntry.pk == blogid).get()
    except models.BlogEntry.DoesNotExist:
        return "That entry does not exist."
    return render_template('detail.html', entry=entry)


@app.route('/tags/<string:tags>')
@login_required
def tags(tags):
    """Shows Journal entry tags"""
    user = current_user
    stream = user.get_tags(tags)
    return render_template("journal.html", stream=stream, user=user, tags=tags)


@app.route('/edit/<int:blogid>', methods=('GET', 'POST'))
@login_required
def edit(blogid=None):
    """
    Allows a uder to edit a journal entry
    """
    try:
        entry = models.BlogEntry.select().where(
            models.BlogEntry.pk == blogid).get()
    except models.DoesNotExist:
        return render_template('edit.html', form=None, entry=None)
    else:
        form = forms.BlogForm(obj=entry)
        if request.method == 'POST':
            if form.validate_on_submit():
                entry.title = form.title.data
                entry.date = form.date.data
                entry.time_spent = form.time_spent.data
                entry.learned = form.learned.data
                entry.resources = form.resources.data
                entry.tags = form.tags.data
                entry.save()
                flash("The Journal has been updataed!", "success")
                return redirect(url_for('index'))
    return render_template('edit.html', form=form, entry=entry)


@app.route('/delete/<int:blogid>')
@login_required
def delete(blogid):
    try:
        entry = models.BlogEntry.select().where(
            models.BlogEntry.pk == blogid).get()
    except models.DoesNotExist:
        abort(404)
    else:
        entry.delete_instance()
        flash("Journal has been deleted!", "success")
        return redirect(url_for('index'))


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='Tester23',
            password='password'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, port=PORT, host=HOST)
