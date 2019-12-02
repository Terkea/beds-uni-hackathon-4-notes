from flask.views import MethodView

from api import app, db
from flask import request, jsonify
import uuid
from api.models import Category, User
import jwt
from functools import wraps


class CategoryEndPoint(MethodView):

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
            categories = Category.query.filter_by(user_id=current_user.id)
            output = []
            for category in categories:
                category_data = {
                    "id": category.id,
                    "public_id": category.public_id,
                    "name": category.name,
                    "user_id": category.user_id
                }
                output.append(category_data)
            return jsonify({'categories': output}), 200

        else:
            category = Category.query.filter_by(public_id=public_id).first()
            if not category:
                return jsonify({"message": "No category found!"}), 204
            else:
                # check if that category belongs to the user who made the request
                if category.user_id != current_user.id:
                    return jsonify({"message": "No category found!"}), 204
                else:
                    category_data = {
                        "id": category.id,
                        "public_id": category.public_id,
                        "name": category.name,
                        "user_id": category.user_id
                    }

                    return jsonify({"category": category_data}), 200


    @token_required
    def post(self):
        current_user = self.get_user_by_token()
        try:
            data = request.get_json()
            new_category = Category(public_id=str(uuid.uuid4()),
                                    name=data['name'],
                                    user_id=str(current_user.id))
            print(data)
            db.session.add(new_category)
            db.session.commit()
            return jsonify({'message': "New category created!"}), 201
        except:
            return jsonify({'message': "Error while creating new category!"}), 404

    @token_required
    def delete(self, public_id):
        current_user = self.get_user_by_token()
        category = Category.query.filter_by(public_id=public_id).first()
        if not category:
            return jsonify({"message": "No category found!"}), 204
        if category.user_id == current_user.id:
            db.session.delete(category)
            db.session.commit()
            return jsonify({"message": "The category has been deleted!"}), 201
        else:
            return jsonify({"message": "Cannot perform that function!"}), 401

    @token_required
    def put(self, public_id):
        current_user = self.get_user_by_token()
        category = Category.query.filter_by(public_id=public_id).first()
        if not category:
            return jsonify({"message": "No category found!"}), 204

        if category.user_id == current_user.id:
            update_data = request.get_json()
            category.name = update_data['name']
            try:
                db.session.commit()
                return jsonify({"message": "The category has been updated!"}), 201
            except:
                return jsonify({"message": "error while updating"}), 404
        else:
            return jsonify({"message": "Cannot perform that function!"}), 401


category_view = CategoryEndPoint.as_view('category_api')
app.add_url_rule('/api/category/', defaults={'public_id': None},
                 view_func=category_view, methods=['GET',])
app.add_url_rule('/api/category/', view_func=category_view, methods=['POST',])
app.add_url_rule('/api/category/<string:public_id>', view_func=category_view,
                 methods=['GET', 'PUT', 'DELETE'])