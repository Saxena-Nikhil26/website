from flask import Flask, render_template, request, redirect, flash
from flask import url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.secret_key='mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer,db.Sequence('seq_reg_id', start=1, increment=1), primary_key=True)
    data_created = db.Column(db.DateTime(timezone=True),default=func.now())
    author = db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer,db.Sequence('seq_reg_id', start=1, increment=1), primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    data_created = db.Column(db.DateTime(timezone=True),default=func.now())
    posts = db.relationship('Post',backref='user',passive_deletes=True)


@app.route('/')
@app.route('/home')
def home():
    if 'username' in session:
        db.create_all()
        posts = Post.query.all()
        return render_template('home.html',posts=posts)
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db.create_all()
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        # print(type(user))
        # print(username,password)
        # print(user.username,user.password)
        # print('hello')
        if user:
            if user.password == password:
                session['username'] = username
                # print(session)
                return redirect(url_for('home'))
            else:
                flash('Password Incorrect',category='error')
        else:
            flash('Username Does not Exist',category='error')
    return render_template('login.html')


@app.route('/sign-up',methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_exist = User.query.filter_by(email=email).first()
        username_exist = User.query.filter_by(username=username).first()
        if email_exist:
            flash('Email exist',category='error')

        elif username_exist:
            flash('Username Exist',category='error')

        elif password1 != password2:
            flash('Password Do not match',category='error')

        elif len(username) < 3:
            flash('Username is too small',category='error')

        elif len(password1) < 5:
            flash('Password is too small',category='error')

        else:
            new_user = User(username=username,email=email,password=password1)
            # print(new_user)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('User Created',category='success')
            return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/create-post',methods=['GET','POST'])
def create_post():
    if 'username' in session:
        if request.method == 'POST':
            text = request.form.get('text')
            if not text:
                flash('Post cannot be empty',category='error')
            else:
                db.create_all()
                post = Post(text=text,author= session['username'])
                db.session.add(post)
                db.session.commit()
                flash('Post Created',category='success')
                return redirect(url_for('home'))
        return render_template('create_post.html')
    else:
        return redirect(url_for('login'))


@app.route('/posts/<username>')
def user_page(username):
    posts = Post.query.filter_by(author=username).all()
    return render_template('userPage.html',posts=posts,username=username)


@app.route('/delete-post/<id>')
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post does not exist',category='error')

    elif session['username'] != post.author:
        flash('You do not have permission to delete this post',category='error')

    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted',category='success')
    return redirect(url_for('home'))


@app.route('/update/<id>',methods=['Get','POST'])
def update_post(id):
    if 'username' in session:
        post = Post.query.filter_by(id=id).first()

        if not post:
            flash('Post does not exist',category='error')

        elif session['username'] != post.author:
            flash('You do not have permission to update this post',category='error')

        if request.method == 'POST':
            text = request.form.get('text')
            post.text = text
            db.session.commit()
            flash('Post Updated',category='success')
            return redirect(url_for('home'))
        return render_template('update_post.html',text=post.text)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
