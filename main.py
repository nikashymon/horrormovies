from flask import Flask, render_template, request, session, redirect, flash
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask('test website')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

class Film(db.Model):
    name = db.Column(db.String, primary_key=True)
    genre = db.Column(db.String, nullable=False)
    country = db.Column(db.String(), nullable=False)
    year = db.Column(db.DateTime(), nullable=False)
    duration = db.Column(db.String(), nullable=False)
    poster = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    video_path = db.Column(db.String(), nullable=False)

    def __init__(self, name, genre, country, year, duration, poster, description, video_path):
        self.name = name
        self.genre = genre
        self.country = country
        self.year = year
        self.duration = duration
        self.poster = poster
        self.description = description
        self.video_path = video_path

class Register(db.Model):
    username = db.Column(db.String(), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(), nullable=False)
    review = db.Column(db.Text(), nullable=False)
    score = db.Column(db.Integer(), nullable=False)

    def __init__(self, nickname, review, score):
        self.nickname = nickname
        self.review = review
        self.score = score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/films')
def films():
    data = db.session.query(Film).all()
    return render_template('films.html', films=data)

@app.route('/reviews')
def reviews():
    dat = db.session.query(Review).all()
    return render_template('reviews.html', reviews=dat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect('/review')

    if request.method == 'GET':
        return render_template('login.html')

    email_input = request.form.get('email')
    password_input = request.form.get('password')
    user = db.session.query(Register).filter_by(email=email_input).first()

    if user and user.password == password_input:
        session['user_id'] = user.username
        return redirect('/review')
    else:
        return render_template('login.html', message='Такого облікового запису не існує')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = db.session.query(Register).filter(
            (Register.username == username) | (Register.email == email)).first()
        if existing_user:
            flash('Користувач з таким ім\'ям або електронною адресою вже існує.')
            return redirect('/register')
        new_user = Register(username=username, email=email, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Реєстрація пройшла успішно! Тепер ви можете увійти.')
            return redirect('/login')
        except Exception as e:
            flash('Сталася помилка під час реєстрації. Спробуйте ще раз.')
            return redirect('/register')

@app.route('/review', methods=['GET', 'POST'])
def add_review():
    if session.get('user_id'):
        if request.method == 'GET':
            return render_template('review.html')
        else:
            nickname = request.form.get('nickname')
            review = request.form.get('review')
            score = request.form.get('rating')
            if score and score.isdigit():
                new_review = Review(nickname=nickname, review=review, score=int(score))
                db.session.add(new_review)
                db.session.commit()
                return redirect('/films')
            else:
                flash('Оцінка повинна бути числом.')
                return redirect('/review')
    else:
        return redirect('/login')

@app.route('/film/<name>')
def film_detail(name):
    film = db.session.query(Film).filter_by(name=name).first()
    return render_template('film_detail.html', film=film)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()