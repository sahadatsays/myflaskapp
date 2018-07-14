#imoprt lib
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from flaskext.mysql import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#virtual data
from data import Articles

app = Flask(__name__)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'myflaskapp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

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


class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=5, max=25)])
    email = StringField('Email', [validators.length(min=5, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Password do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    
    if request.method == 'POST' and form.validate():
        full_name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(str(form.password.data))

        #create cursor
        cur = conn.cursor()
        
        #write mysql query
        cur.execute("INSERT INTO users(full_name, user_name, email, password) VALUES (%s, %s, %s, %s)", (full_name, username, email, password))
        #cur.callproc('users',(full_name,username,email,password))
        #commit to db
        conn.commit()

        #Close connection
        cur.close()

        flash('You are registerd and can log in', 'success')
        #redirect to tergate page
        return redirect(url_for('login'))

    return render_template('register.html', form = form)
        




if __name__ == '__main__':
    app.secret_key = 'secret123456'
    app.run(debug=True)
