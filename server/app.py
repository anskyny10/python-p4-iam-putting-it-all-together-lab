#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
# from flask_bcrypt import Bcrypt

from config import app, db, api
from models import User, Recipe

# bcrypt = Bcrypt(app)

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            new_user.password_hash = data.get('password')
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            return make_response(new_user.to_dict(), 201)
            
        except Exception as e:
            return make_response({'error': str(e)}, 422)
    
# class CheckSession(Resource):
#     def get(self):
#         user_id = session.get('user_id')
        
#         if user_id:
#             user = User.query.filter_by(id=user_id).first()
#             if user:
#                 # user_dict = user.to_dict()
#                 # print(user_dict)
#                 return make_response(user.to_dict(), 200)
        
#         return make_response({'error': 'Not logged in'}, 401)
    
class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return make_response(user.to_dict())
        else:
            return make_response({'message': '401: Not Authorized'}, 401)

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)

        return make_response({'error': 'Invalid username or password'}, 401)

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        
        if user_id:
            session['user_id'] = None
            return make_response({'message': '204: No Content'}, 204)
        
        return make_response({'error': 'Unauthorized'}, 401)
    
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            return make_response([recipe.to_dict() for recipe in recipes], 200)
        else:
            return make_response({'error': 'Unauthorized'}, 401)
        
    def post(self):
        user_id = session.get('user_id')
        
        if user_id:
            try:
                data = request.get_json()
                
                new_recipe = Recipe(
                    title=data.get('title'),
                    instructions=data.get('instructions'),
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=user_id
                )
                db.session.add(new_recipe)
                db.session.commit()
                return make_response(new_recipe.to_dict(), 201)
            except Exception as e:
                return make_response({'error': str(e)}, 422)
        else:
            return make_response({'error': 'Unauthorized'}, 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)