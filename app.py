#imoprt lib
from flask import Flask, render_template, flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, Validators
from passlib.hash import sha256_crypt

#virtual data
from data import Articles

app = Flask(__name__)

Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)





if __name__ == '__main__':
    app.run(debug=True)
