import requests
from flask import Flask, render_template, redirect, url_for, flash

from client.forms import registerForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SEX_BOT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_URL = 'http://127.0.0.1:5001/api/'



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = registerForm()

    if form.validate_on_submit():
        first_name = str(form.first_name.data)
        last_name = str(form.first_name.data)
        email = str(form.email.data)
        password = str(form.password.data)
        password_check = str(form.password_check.data)

        if password == password_check:
            data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
            request = requests.post(f"{API_URL}users/", json=data)
            if request.status_code == 201:
                print("[INFO] Account created")
                return redirect(url_for('login'))
            else:
                print(f"[ERROR] {request.text}")
                flash('Email not unique')
        else:
            flash('Passwords don\'t match')
    else:

        print("NOOO")

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run()
