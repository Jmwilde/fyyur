import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from json.decoder import JSONDecodeError

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, data):
  if not data:
    return data
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  return data[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': formatted_categories
            })
        except:
            abort(400)


    @app.route('/questions')
    def get_questions():
        try:
            questions = Question.query.all()
            paginated_qs = paginate(request, questions)

            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'questions': [q.format() for q in paginated_qs],
                'total_questions': len(questions),
                'categories': formatted_categories,
                'current_category': paginated_qs[0].category
            })
        except:
            abort(400)


    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            question = Question.query.get(q_id)
            if not question:
                raise ValueError('Question with id {} does not exist.'.format(q_id))
            question.delete()
            return jsonify({
                'success': True,
                'message': 'Question successfully deleted.'
            })
        except ValueError:
            abort(422)
        except:
            abort(400)


    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = json.loads(request.data)
            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)
            search = body.get('searchTerm', None)

            if search:
                results = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
                questions = paginate(request, results)
                formatted_qs = [q.format() for q in questions]
            
                return jsonify({
                    'success': True,
                    'questions': formatted_qs,
                    'total_questions': len(results),
                    'current_category': questions and questions[0].category
                })
            else:
                if not (new_question and new_answer):
                    raise ValueError('Both question and answer fields must not be None.')
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()
                return jsonify({
                    'success': True,
                    'message': 'Question successfully created.'
                })
        except JSONDecodeError:
            abort(400)
        except Exception as e:
            abort(422)
            print(e)


    @app.route('/categories/<int:category_id>/questions')
    def get_questions_for_category(category_id):
        try:
            results = Question.query.filter(Question.category == category_id).all()
            questions = paginate(request, results)
            formatted_qs = [q.format() for q in questions]
            return jsonify({
                'success': True,
                'questions': formatted_qs,
                'total_questions': len(results),
                'current_category': questions and questions[0].category
            })
        except:
            abort(400)


    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        try:
            body = json.loads(request.data)
            previous = body.get('previous_questions', [])
            category = body.get('quiz_category', None)

            if category:
                category_id = category.get('id', 0)
                questions = Question.query.filter(Question.id.notin_(previous), Question.category == category_id).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous)).all()
            
            question = random.choice(questions).format() if questions else None
            return jsonify({
                'success': True,
                'question': question,
            })
        except JSONDecodeError:
            abort(400)
        except:
            abort(422)


    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'succes': False,
            'error': 400,
            'message': 'Request was not formatted correctly.'
        }), 400


    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
          'success': True,
          'questions': formatted_qs,
          'total_questions': len(results),
          'current_category': questions[0].category
        })
      else:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()
        return jsonify({
          'success': True
        })
    except Exception as e:
      print('Error: ', e)
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_for_category(category_id):
    try:
      results = Question.query.filter(Question.category == category_id).all()
      questions = paginate(request, results)
      formatted_qs = [q.format() for q in questions]
      return jsonify({
        'success': True,
        'questions': formatted_qs,
        'total_questions': len(results),
        'current_category': questions[0].category
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random question within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    body = json.loads(request.data)
    previous = body.get('previous_questions', [])
    category = body.get('quiz_category', None)

    try:
      if category:
        category_id = category.get('id', 0)
        questions = Question.query.filter(Question.id.notin_(previous), Question.category == category_id).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous)).all()
      
      question = random.choice(questions).format() if questions else None
      return jsonify({
          'success': True,
          'question': question,
      })
    except Exception as e:
      print('Error:', e)
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request():
    return jsonify({
      'succes': False,
      'error': 400,
      'message': 'Request was not formatted correctly.'
    }), 400

  @app.errorhandler(404)
  def not_found():
    return jsonify({
      'success': False,
      'error': 404
      'message': 'Question not found.'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable():
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Data within the request body was unable to be processed.'
    }), 422

  return app

    