from flask import url_for, render_template, flash, redirect, request
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm
from main.models import User, Post
from main import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

tweets = [
    {
        'author': 'Lekshmi',
        'title': 'Post 1',
        'content': 'This content',
        'date_posted': '04/10/2021',
        'pidx': '123'
    },
    {
        'author': 'Jayadev',
        'title': 'Post 2',
        'content': 'This content as well!',
        'date_posted': '04/10/2021',
        'pidx': '124'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=tweets)


@app.route('/aboutus')
def aboutsection():
    return render_template('about.html', title='Flasker!')


@app.route('/user/<username>')
def userprofile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        posts = user.posts
        return render_template('user.html', username=username, posts=posts)  # 'User %s' % escape(username)
    else:
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid ID and password', 'danger')
    return render_template('login.html', title='Log In', form=form)


@app.route('/post/<postidx>')
def post(postidx):
    return render_template('post.html', idx=postidx, post=tweets)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)
