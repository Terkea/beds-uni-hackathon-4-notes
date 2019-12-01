import json

import jwt
import requests
from flask import Flask, render_template, redirect, url_for, flash, request, session

from client.forms import registerForm, loginForm, createCategory, updateCategory, deleteCategory, createNote, searchNote

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER_MEGA_SECURE_KEY'
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


@app.route('/create_note/', methods=['GET', 'POST'])
def create_note():
    form = createNote()
    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']

    if form.validate_on_submit():
        title = str(form.title.data)
        if type(form.category.data) is None:
            category = None
        else:
            category = str(form.category.data)
        content = str(form.content.data)

        post_data = {
            "title": title,
            "category_id": category,
            "content": content,
        }

        print(post_data)

        query = requests.post(f"{API_URL}note/", headers={"token": session['token']}, json=post_data)

        if query.status_code == 201:
            print("[INFO] New note created")
            return redirect(url_for('notes'))
    else:
        print('nooo')

    return render_template('create_note.html', categories=categories, form=form, note=None)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = createCategory()
    form2 = updateCategory()
    form3 = deleteCategory()

    query = requests.get(f"{API_URL}category/", headers={"token": session['token']})

    # get all the categories
    if query.status_code == 200:
        data = query.json()


    no_categories = len(data['categories'])
    no_notes = len(requests.get(f"{API_URL}note/", headers={"token": session['token']}).json()['notes'])
    uncategorized_noted = len(requests.get(f"{API_URL}notes_with_no_category/", headers={"token": session['token']}).json()['notes'])
    average = 0
    try:
        average = no_categories / no_notes
    except:
        pass
    stats = [no_categories, no_notes, average, uncategorized_noted]


    # CREATE NEW CATEGORY
    if "form1-submit" in request.form and form.validate_on_submit():
        name = str(form.category_name.data)

        post_data = {
            "name": name
        }

        create_query = requests.post(f"{API_URL}category/", headers={"token": session['token']}, json=post_data)
        if create_query.status_code == 201:
            print('[INFO] New category created')
            return redirect(url_for('index'))

    # UPDATE CATEGORY
    if "form2-submit" in request.form and form2.validate_on_submit():
        public_id = str(form2.public_id.data)
        name = str(form2.category_name.data)

        post_data = {
            "name": name
        }

        update_query = requests.put(f"{API_URL}category/{public_id}",
                                    headers={"token": session['token']}, json=post_data)

        if update_query.status_code == 201:
            print('[INFO] Category updated')
            return redirect(url_for('index'))

    # DELETE CATEGORY
    if "form3-submit" in request.form and form3.validate_on_submit():
        public_id = str(form3.public_id.data)
        notes_action = str(form3.notes_action.data)

        post_data = {
            "public_id": public_id
        }

        _all_notes = requests.get(f"{API_URL}notes_by_category/{public_id}",
                                  headers={"token": session['token']}, json=post_data)

        if _all_notes.status_code == 200:
            print('[INFO] Notes available in category')
            if notes_action == '0':
                print('[INFO]  Delete all the notes and the category')
                for note in _all_notes.json()['notes']:
                    print(f"DELETING {note['public_id']}")
                    requests.delete(f"{API_URL}note/{note['public_id']}",
                                    headers={"token": session['token']})
                requests.delete(f"{API_URL}category/{public_id}",
                                headers={"token": session['token']})
                return redirect(url_for('index'))

            if notes_action == '1':
                print('[INFO] uncategorize all the notes and delete the category')
                for note in _all_notes.json()['notes']:
                    update_data = {
                        "category_id": None
                    }
                    print(f"UPDATING {note['public_id']}")
                    requests.put(f"{API_URL}note/{note['public_id']}",
                                 headers={"token": session['token']}, json=update_data)

                requests.delete(f"{API_URL}category/{public_id}",
                                headers={"token": session['token']})
                return redirect(url_for('index'))

    return render_template('categories.html', data=data, form=form, form2=form2, form3=form3, stats=stats)


@app.route('/delete_note/<string:public_id>', methods=['GET', 'POST'])
def delete_category(public_id):
    print('[INFO] DELETED note ' + public_id)
    request = requests.delete(f"{API_URL}note/{public_id}", headers={"token": session['token']})
    print(request.status_code)
    return redirect(url_for('notes'))


@app.route('/notes/', methods=['GET', 'POST'])
def notes():
    form = searchNote()

    if form.validate_on_submit():
        keyword = str(form.keyword.data)
        category_id = str(form.category_id.data)
        return redirect(f"/search_notes/{keyword}/{category_id}")

    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']
    notes = requests.get(f"{API_URL}note/", headers={"token": session['token']}).json()['notes']
    return render_template('notes.html', categories=categories, notes=notes, form=form)


@app.route('/search_notes/<string:keyword>/<string:category_public_id>', methods=['GET', 'POST'])
def search_notes(keyword, category_public_id):
    form = searchNote()

    if form.validate_on_submit():
        keyword = str(form.keyword.data)
        category_id = str(form.category_id.data)
        return redirect(f"/search_notes/{keyword}/{category_id}")
    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']
    notes = requests.get(f"{API_URL}search_note/{keyword}/{category_public_id}", headers={"token": session['token']}).json()['notes']
    return render_template('notes.html', categories=categories, notes=notes, form=form)


@app.route('/note/<string:public_id>', methods=['GET', 'POST'])
def note(public_id):
    form = createNote()
    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']
    note = requests.get(f"{API_URL}note/{public_id}", headers={"token": session['token']}).json()['notes']


    if form.validate_on_submit():
        title = str(form.title.data)
        if type(form.category.data) is None:
            category = None
        else:
            category = str(form.category.data)
        content = str(form.content.data)

        post_data = {
            "title": title,
            "category_id": category,
            "content": content,
        }

        query = requests.put(f"{API_URL}note/{note['public_id']}", headers={"token": session['token']}, json=post_data)
        if query.status_code == 201:
            print(f'[INFO] note {public_id} has been updated')
            return redirect(url_for('notes'))
    return render_template('create_note.html', form=form, note=note, categories=categories)


@app.route('/notes/<string:category_public_id>')
def notes_by_category(category_public_id):
    form = searchNote()

    if form.validate_on_submit():
        keyword = str(form.keyword.data)
        category_id = str(form.category_id.data)
        return redirect(f"/search_notes/{keyword}/{category_id}")
    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']
    notes = requests.get(f"{API_URL}notes_by_category/{category_public_id}", headers={"token": session['token']}).json()['notes']
    return render_template('notes.html', categories=categories, notes=notes, form=form)


@app.route('/notes/category=none')
def notes_without_category():
    form = searchNote()

    if form.validate_on_submit():
        keyword = str(form.keyword.data)
        category_id = str(form.category_id.data)
        return redirect(f"/search_notes/{keyword}/{category_id}")

    categories = requests.get(f"{API_URL}category/", headers={"token": session['token']}).json()['categories']
    notes = requests.get(f"{API_URL}notes_with_no_category/", headers={"token": session['token']}).json()['notes']
    return render_template('notes.html', categories=categories, notes=notes, form=form)

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
