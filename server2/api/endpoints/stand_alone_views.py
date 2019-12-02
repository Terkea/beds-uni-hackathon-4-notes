import datetime

import jwt
from flask import request, make_response, jsonify
from flask.views import View
from werkzeug.security import check_password_hash

from api import app
from api.models import User, Note, Category
from functools import wraps


class Login(View):
    def dispatch_request(self):
        # get the request authorization information
        auth = request.authorization

        # if there's no auth at all or username or password return
        if not auth or not auth.username or not auth.password:
            return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        user = User.query.filter_by(email=auth.username).first()
        if not user:
            return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        if check_password_hash(user.password, auth.password):
            # generate token
            token = jwt.encode(
                # the token lasts 356 days, eventually can be changed later on
                {'public_id': user.public_id, 'user_id': user.id,
                 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                app.config['SECRET_KEY'])

            return jsonify({'token': token.decode('UTF-8')})

        return make_response("Could not verify", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


class Notes_by_Category(View):
    def token_required(self):
        """
        Decorator meant to check if the token exists or not
        If the token exists check if it is valid
        """

        @wraps(self)
        def decorated(*args, **kwargs):
            token = None

            if 'token' in request.headers:
                token = request.headers['token']

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify({'message': 'Token is invalid!'}), 401

            return self(*args, **kwargs)

        return decorated

    def get_user_by_token(self):
        """
        :param token: has to be a jwt token
        :return: the user based on the public_id supplied by the token
        """
        token = request.headers['token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        user = User.query.filter_by(public_id=data['public_id']).first()
        return user

    @token_required
    def dispatch_request(self, category_id):
        current_user = self.get_user_by_token()
        notes = Note.query.join(Category).filter(User.id == current_user.id).filter(Category.public_id == category_id).all()
        output = []

        for note in notes:

            category_name = ""
            try:
                category = Category.query.filter_by(id=note.category_id).first()
                category_name = category.name
            except:
                category_name = None

            note_data = {
                "public_id": note.public_id,
                "title": note.title,
                "content": note.content,
                "category_id": note.category_id,
                "user_id": note.user_id,
                "category_name": category_name
            }
            output.append(note_data)
        return jsonify({'notes': output}), 200


class Notes_with_no_Category(View):
    def token_required(self):
        """
        Decorator meant to check if the token exists or not
        If the token exists check if it is valid
        """

        @wraps(self)
        def decorated(*args, **kwargs):
            token = None

            if 'token' in request.headers:
                token = request.headers['token']

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify({'message': 'Token is invalid!'}), 401

            return self(*args, **kwargs)

        return decorated

    def get_user_by_token(self):
        """
        :param token: has to be a jwt token
        :return: the user based on the public_id supplied by the token
        """
        token = request.headers['token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        user = User.query.filter_by(public_id=data['public_id']).first()
        return user

    @token_required
    def dispatch_request(self):
        current_user = self.get_user_by_token()
        notes = Note.query.filter_by(user_id=current_user.id).filter(Note.category_id == None).order_by(
            Note.created_date.desc()).all()
        output = []

        for note in notes:
            note_data = {
                "public_id": note.public_id,
                "title": note.title,
                "content": note.content,
                "category_id": note.category_id,
                "user_id": note.user_id,
                "created_date": note.created_date
            }
            output.append(note_data)
        return jsonify({'notes': output}), 200


class Search_note(View):
    def token_required(self):
        """
        Decorator meant to check if the token exists or not
        If the token exists check if it is valid
        """

        @wraps(self)
        def decorated(*args, **kwargs):
            token = None

            if 'token' in request.headers:
                token = request.headers['token']

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                User.query.filter_by(public_id=data['public_id']).first()
            except:
                return jsonify({'message': 'Token is invalid!'}), 401

            return self(*args, **kwargs)

        return decorated

    def get_user_by_token(self):
        """
        :param token: has to be a jwt token
        :return: the user based on the public_id supplied by the token
        """
        token = request.headers['token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        user = User.query.filter_by(public_id=data['public_id']).first()
        return user

    @token_required
    def dispatch_request(self, keyword, category_public_id):
        """
        if category_public_id is all the the category doesn't matter else search by keyword in specified category
        :param keyword:
        :param category_public_id:
        :return:
        """
        current_user = self.get_user_by_token()
        if category_public_id == 'all':
            notes = Note.query.join(Category).filter_by(user_id=current_user.id). \
                filter(Note.content.like("%" + keyword + "%"))\
                .order_by(Note.created_date.desc()) \
                .all()
        else:
            notes = Note.query.join(Category).filter_by(user_id=current_user.id). \
                filter(Note.content.like("%" + keyword + "%")). \
                filter(Category.public_id == category_public_id) \
                .order_by(Note.created_date.desc()) \
                .all()
        output = []

        for note in notes:

            category_name = ""
            try:
                category = Category.query.filter_by(id=note.category_id).first()
                category_name = category.name
            except:
                category_name = None

            note_data = {
                "public_id": note.public_id,
                "title": note.title,
                "content": note.content,
                "category_id": note.category_id,
                "user_id": note.user_id,
                "category_name": category_name,
                "created_date": note.created_date
            }
            output.append(note_data)
        return jsonify({'notes': output}), 200


app.add_url_rule('/api/login/', view_func=Login.as_view('login'))

app.add_url_rule('/api/notes_by_category/<string:category_id>',
                 view_func=Notes_by_Category.as_view('notes_by_category'))

app.add_url_rule('/api/notes_with_no_category/',
                 view_func=Notes_with_no_Category.as_view('notes_with_no_category'))

app.add_url_rule('/api/search_note/<string:keyword>/<string:category_public_id>',
                 view_func=Search_note.as_view('search_note'))
