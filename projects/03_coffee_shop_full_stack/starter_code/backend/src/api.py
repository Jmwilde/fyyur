import os
from flask import Flask, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def drinks():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        formatted_details = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_details
        })
    except:
        abort(400)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    try:
        body = json.loads(request.data)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        recipe_json = json.dumps(new_recipe) # convert Python object to JSON
        drink = Drink(title=new_title, recipe=recipe_json)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    # Handle requests that break db constraints
    except IntegrityError:
        abort(403)
    except:
        abort(400)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            abort(404)

        body = json.loads(request.data)
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        # Make edits only to the fields found in the request
        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe

        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    # Handle requests that break db constraints
    except IntegrityError:
        abort(403)
    # Rethrow expected http exceptions
    except HTTPException as e:
        abort(e.code)
    except Exception as e:
        print('Error:', e)
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    print('Drink id:', id)
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    # Rethrow expected http exceptions
    except HTTPException as e:
        abort(e.code)
    except:
        abort(500)

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        'succes': False,
        'error': 400,
        'message': 'Request was not formatted correctly.'
    }), 400

@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Request is forbidden.'
    }), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Drink not found.'
    }), 404

@app.errorhandler(422)
def unprocessable(e):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Data within the request body was unprocessable.'
    }), 422

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Ruh roh! Something went wrong on our end!'
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(e):
    return jsonify({
        'success': False,
        'error': e.error['code'],
        'message': e.error['description']
    }), e.status_code
