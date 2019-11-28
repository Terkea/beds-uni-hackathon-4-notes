import json

import requests
from flask import Flask, render_template, redirect, url_for, flash, request, session

from client.forms import registerForm, loginForm, createCategory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SEX_BOT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_URL = 'http://127.0.0.1:5001/api/'


@app.before_request
def require_login():
    """
    all routes are protected except the ones from  allowed_routes
    if a session is initialized with a valid token the access is granted

    the server side generates the tokens and we store them in sessions to communicate with the api later on
    :rtype: redirect
    """
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'token' not in session:
        return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    """
    delete the session token
    """
    del session['token']
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/categories/', methods=['GET', 'POST'])
def categories():
    form = createCategory()
    request = requests.get(f"{API_URL}category/", headers={"token": session['token']})

    if request.status_code == 200:
        data = request.json()


    if form.validate_on_submit():
        name = str(form.category_name.data)
        post_data = {
            "name": name
        }
        requests.post(f"{API_URL}category/", headers={"token": session['token']}, json=post_data)
        if request.status_code == 200:
            print('[INFO] New category created')
            return redirect(url_for('categories'))
    return render_template('categories.html', data=data, form=form)



# todo: when a category is deleted pop up a model and ask the user what he wants to do with the notes. ex, delete all,
# move them to another category or let them without category
@app.route('/delete_category/<string:public_id>', methods=['GET', 'POST'])
def delete_category(public_id):
    print('deleted ' + public_id)
    request = requests.delete(f"{API_URL}category/{public_id}", headers={"token": session['token']})
    print(request.status_code)
    return redirect(url_for('categories'))


@app.route('/notes/')
def notes():
    return render_template('notes.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = loginForm()

    if form.validate_on_submit():
        email = str(form.email.data)
        password = str(form.password.data)

        request = requests.get(f"{API_URL}login/", auth=(email, password))
        if request.status_code == 200:
            print(f"[INFO] Logged in")
            token = json.loads(request.text)['token']
            session['token'] = token
            return redirect(url_for('index'))
        else:
            print(f"[ERROR] {request.text}")
            flash("Wrong email or password")
    else:
        print("[INFO] Login form not submited")

    return render_template('login.html', form=form)


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
    app.run(debug=True)
