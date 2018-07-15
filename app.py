#imoprt lib
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from flaskext.mysql import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

#virtual data
from data import Articles

app = Flask(__name__)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'myflaskapp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)

conn = mysql.connect()

Articles = Articles()
#Home 
@app.route('/')
def index():
    return render_template('home.html')
#About
@app.route('/about')
def about():
    return render_template('about.html')
#Articles
@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

#Register form
class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=5, max=25)])
    email = StringField('Email', [validators.length(min=5, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Password do not match')
    ])
    confirm = PasswordField('Confirm Password')
#show Register Form
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

#login form     
@app.route('/login', methods=['GET', 'POST'])
def login():
    #make sure request
    if request.method == 'POST':
        #validate
        if request.form['username'] != '' and request.form['password'] != '':
            username = request.form['username']
            request_password = request.form['password']

            #get cursor 
            cur = conn.cursor()
            #get User by username
            check = cur.execute("SELECT * FROM users WHERE user_name = %s", [username])

            if check > 0:
                data = cur.fetchone()
                #Compare password
                if sha256_crypt.verify(request_password, data[4]):

                    session['logged_in'] = True 
                    session['username'] = username

                    flash('You are now logged in.', 'success')
                    return redirect(url_for('dashboard'))

                else:
                    error = 'Login Invalid !'
                    return render_template('login.html', error=error)
            else:
                error = 'User Not Found !'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Your input is empty.'
            return render_template('login.html', error=error)
        return username
    if session.get('logged_in') is not None:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

#check auth

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login.', 'danger')
            return redirect(url_for('login'))
    return wrap


#Logout 
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now Logged out', 'success')
    return redirect(url_for('login'))


#dashboard function
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Crate cursor
    cur = conn.cursor()
    
    # Query 
    check = cur.execute("SELECT * FROM articles ORDER BY created_at  DESC")

    # Get data
    articles = cur.fetchall()

    # Close DB
    cur.close()

    if check > 0:
        
        return render_template('dashboard.html', articles=articles)
    else:
        msg = "Articles not found."
        return render_template('dashboard.html', msg=msg)

# Add Article
class ArtilceForm(Form):
    title = StringField('Title', [validators.length(min=5, max=200)])
    body = TextAreaField('Body', [validators.length(min=15)])

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArtilceForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = conn.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, body, auth) VALUES (%s, %s, %s)", (title, body, session['username']))

        # Commint to DB
        conn.commit()

        # Connection close
        cur.close()

        # Flash Message set
        flash("Article Created.", "success")

        # Redirect to tergate page
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

#main function
if __name__ == '__main__':
    app.secret_key = 'secret123456'
    app.run(debug=True)
