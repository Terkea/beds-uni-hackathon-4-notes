from flask.views import MethodView

from api import app, db
from flask import request, jsonify
import uuid
from api.models import Note, User, Category
import jwt
from functools import wraps


class NoteEndPoint(MethodView):

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
    def get(self, public_id):
        current_user = self.get_user_by_token()
        if public_id is None:
            notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_date.desc())
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
        else:
            note = Note.query.filter_by(public_id=public_id).first()
            category_name = ""

            try:
                category = Category.query.filter_by(id=note.category_id).first()
                category_name = category.name
            except:
                category_name = None

            if not note:
                return jsonify({"message": "No note found!"}), 204
            else:
                # check if that category belongs to the user who made the request
                if note.user_id != current_user.id:
                    return jsonify({"message": "No note found!"}), 204
                else:
                    note_data = {
                        "public_id": note.public_id,
                        "title": note.title,
                        "content": note.content,
                        "category_id": note.category_id,
                        "user_id": note.user_id,
                        "category_name": category_name,
                        "created_date": note.created_date
                    }
                    return jsonify({"notes": note_data}), 200

    @token_required
    def post(self):
        current_user = self.get_user_by_token()
        try:
            data = request.get_json()
            new_note = Note(public_id=str(uuid.uuid4()),
                            title=data['title'],
                            content=data['content'],
                            category_id=data['category_id'],
                            user_id=str(current_user.id))
            print(data)
            db.session.add(new_note)
            db.session.commit()
            return jsonify({'message': "New note created!"}), 201
        except:
            return jsonify({'message': "Error while creating new note!"}), 404

    @token_required
    def delete(self, public_id):
        current_user = self.get_user_by_token()
        note = Note.query.filter_by(public_id=public_id).first()
        if not note:
            return jsonify({"message": "No note found!"}), 204
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            return jsonify({"message": "The note has been deleted!"}), 201
        else:
            return jsonify({"message": "Cannot perform that function!"}), 401

    @token_required
    def put(self, public_id):
        current_user = self.get_user_by_token()
        note = Note.query.filter_by(public_id=public_id).first()
        if not note:
            return jsonify({"message": "No category found!"}), 204

        if note.user_id == current_user.id:
            update_data = request.get_json()

            try:
                note.title = update_data['title']
            except:
                pass

            try:
                note.content = update_data['content']
            except:
                pass

            try:
                note.category_id = update_data['category_id']
            except:
                pass

            try:
                db.session.commit()
                return jsonify({"message": "The note has been updated!"}), 201
            except:
                return jsonify({"message": "error while updating"}), 404
        else:
            return jsonify({"message": "Cannot perform that function!"}), 401


note_view = NoteEndPoint.as_view('note_api')
app.add_url_rule('/api/note/', defaults={'public_id': None},
                 view_func=note_view, methods=['GET', ])
app.add_url_rule('/api/note/', view_func=note_view, methods=['POST', ])
app.add_url_rule('/api/note/<string:public_id>', view_func=note_view,
                 methods=['GET', 'PUT', 'DELETE'])
